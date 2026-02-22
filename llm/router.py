# crabswarm/llm/router.py
"""
模型路由模块

根据任务特征自动选择最合适的模型
"""

import re
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass

from .client import LLMClient
from .adapters.base import ChatMessage, ChatResponse
from .config import ModelTier, TIER_MODEL_MAPPING, resolve_model


@dataclass
class RoutingRule:
    """路由规则"""
    name: str
    condition: Callable[[str], bool]
    model: str
    priority: int = 0
    description: str = ""


class ModelRouter:
    """
    智能模型路由器
    
    根据提示词特征自动选择最合适的模型，平衡成本和质量
    
    示例:
        >>> router = ModelRouter(client)
        >>> router.add_rule(RoutingRule(
        ...     name="code_task",
        ...     condition=lambda p: "代码" in p or "code" in p.lower(),
        ...     model="deepseek-v3",
        ...     priority=10
        ... ))
        >>> response = await router.chat_with_routing(messages)
    """
    
    def __init__(self, client: LLMClient):
        """
        初始化路由器
        
        Args:
            client: LLM客户端实例
        """
        self.client = client
        self.rules: List[RoutingRule] = []
        self.tier_mapping = TIER_MODEL_MAPPING.copy()
        self.default_tier = ModelTier.BALANCED
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认路由规则"""
        default_rules = [
            RoutingRule(
                name="code_generation",
                condition=lambda p: any(kw in p.lower() for kw in ["代码", "code", "编程", "programming", "函数", "function"]),
                model="deepseek-v3",
                priority=10,
                description="代码生成任务使用高质量模型"
            ),
            RoutingRule(
                name="complex_analysis",
                condition=lambda p: any(kw in p for kw in ["分析", "分析", "推理", "reasoning", "解释", "explain"]),
                model="deepseek-r1",
                priority=9,
                description="复杂分析使用推理模型"
            ),
            RoutingRule(
                name="simple_greeting",
                condition=lambda p: len(p) < 30 and any(kw in p.lower() for kw in ["你好", "hello", "hi", "hey"]),
                model="qwen2.5-14b",
                priority=5,
                description="简单问候使用轻量模型"
            ),
            RoutingRule(
                name="short_query",
                condition=lambda p: len(p) < 50,
                model="qwen2.5-14b",
                priority=3,
                description="短查询使用轻量模型"
            ),
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: RoutingRule):
        """
        添加路由规则
        
        Args:
            rule: 路由规则
        """
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, name: str) -> bool:
        """
        移除路由规则
        
        Args:
            name: 规则名称
            
        Returns:
            是否成功移除
        """
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                self.rules.pop(i)
                return True
        return False
    
    def route(self, prompt: str, preferred_tier: Optional[ModelTier] = None) -> str:
        """
        根据提示词选择模型
        
        Args:
            prompt: 提示词
            preferred_tier: 偏好的模型层级
            
        Returns:
            模型标识符
        """
        # 1. 检查自定义规则
        for rule in self.rules:
            try:
                if rule.condition(prompt):
                    return rule.model
            except Exception:
                continue
        
        # 2. 根据层级选择
        if preferred_tier:
            return self.tier_mapping.get(preferred_tier, self.tier_mapping[self.default_tier])
        
        # 3. 默认模型
        return self.tier_mapping[self.default_tier]
    
    async def chat_with_routing(
        self,
        messages: List[ChatMessage],
        preferred_tier: Optional[ModelTier] = None,
        prompt_analysis: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        自动路由的对话
        
        Args:
            messages: 消息列表
            preferred_tier: 偏好的模型层级
            prompt_analysis: 用于路由分析的提示词（默认使用最后一条消息）
            **kwargs: 其他参数
            
        Returns:
            ChatResponse
        """
        # 获取用于分析的提示词
        if prompt_analysis is None and messages:
            prompt_analysis = messages[-1].content
        
        # 路由选择模型
        model = self.route(prompt_analysis or "", preferred_tier)
        
        # 执行对话
        return await self.client.chat(messages, model=model, **kwargs)
    
    def set_tier_model(self, tier: ModelTier, model: str):
        """
        设置层级对应的模型
        
        Args:
            tier: 模型层级
            model: 模型标识符
        """
        self.tier_mapping[tier] = model
    
    def set_default_tier(self, tier: ModelTier):
        """
        设置默认层级
        
        Args:
            tier: 模型层级
        """
        self.default_tier = tier
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """列出所有规则"""
        return [
            {
                "name": rule.name,
                "model": rule.model,
                "priority": rule.priority,
                "description": rule.description,
            }
            for rule in self.rules
        ]
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        分析提示词特征
        
        Args:
            prompt: 提示词
            
        Returns:
            特征分析结果
        """
        features = {
            "length": len(prompt),
            "has_chinese": bool(re.search(r'[\u4e00-\u9fff]', prompt)),
            "has_code_keywords": any(kw in prompt.lower() for kw in ["代码", "code", "函数", "function"]),
            "has_analysis_keywords": any(kw in prompt for kw in ["分析", "分析", "推理"]),
            "is_short": len(prompt) < 50,
            "is_long": len(prompt) > 500,
        }
        
        # 预测路由结果
        predicted_model = self.route(prompt)
        
        return {
            "features": features,
            "predicted_model": predicted_model,
            "rules_checked": len(self.rules),
        }
