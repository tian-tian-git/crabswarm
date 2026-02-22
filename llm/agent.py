# crabswarm/llm/agent.py
"""
LLM增强型Agent

将LLM能力集成到CrabSwarm的Agent中
"""

from typing import List, Dict, Optional, Any
import sys
import os

# 添加父目录到路径以导入core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.swarm import Agent
except ImportError:
    # 如果core模块不可用，使用基类
    class Agent:
        """Agent基类（备用）"""
        def __init__(self, name: str, role: str, **kwargs):
            self.name = name
            self.role = role
            self.personality = kwargs.get("personality", "专业、高效")
            self.expertise = kwargs.get("expertise", [role])
            self.bias = kwargs.get("bias", "可能有盲点")
            self.catchphrase = kwargs.get("catchphrase", "Ready to work")
            self.id = kwargs.get("id", "agent_001")
            self.skills = []
            self.mcp_tools = []
            self.memory = []

from .client import LLMClient
from .adapters.base import ChatMessage


class LLMAgent(Agent):
    """
    支持LLM的增强型Agent
    
    继承自CrabSwarm的Agent，添加LLM对话能力
    
    示例:
        >>> from crabswarm.llm import LLMClient, LLMConfig, ModelProvider
        >>> client = LLMClient(LLMConfig(provider=ModelProvider.SILICONFLOW, api_key="sk-xxx"))
        >>> agent = LLMAgent(
        ...     name="分析师",
        ...     role="数据分析师",
        ...     llm_client=client,
        ...     model="deepseek-v3"
        ... )
        >>> result = await agent.think("分析市场趋势")
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        llm_client: LLMClient,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_history: int = 20,
        enable_reasoning: bool = False,
        **kwargs
    ):
        """
        初始化LLM Agent
        
        Args:
            name: Agent名称
            role: Agent角色
            llm_client: LLM客户端
            system_prompt: 系统提示词
            model: 模型标识符
            max_history: 最大历史记录数
            enable_reasoning: 是否显示思维链
            **kwargs: 其他参数传递给父类
        """
        super().__init__(name=name, role=role, **kwargs)
        
        self.llm_client = llm_client
        self.model = model
        self.max_history = max_history
        self.enable_reasoning = enable_reasoning
        
        # 设置系统提示词
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = f"你是{name}，{role}。{self.personality}"
        
        # 对话历史
        self.conversation_history: List[ChatMessage] = []
        
        # 统计
        self._total_tokens = 0
        self._request_count = 0
    
    async def think(self, topic: str) -> str:
        """
        增强思考能力 - 使用LLM
        
        Args:
            topic: 思考主题
            
        Returns:
            思考结果
        """
        messages = [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=f"请从{self.role}的角度分析：{topic}")
        ]
        
        response = await self.llm_client.chat(
            messages=messages,
            model=self.model
        )
        
        # 更新统计
        self._total_tokens += response.usage.get("total_tokens", 0)
        self._request_count += 1
        
        # 保存到历史
        self._add_to_history(topic, response.content)
        
        # 返回结果
        if self.enable_reasoning and response.reasoning_content:
            return f"[思考过程]\n{response.reasoning_content}\n\n[结论]\n{response.content}"
        
        return response.content
    
    async def chat(self, message: str, stream: bool = False) -> str:
        """
        多轮对话
        
        Args:
            message: 用户消息
            stream: 是否流式输出
            
        Returns:
            回复内容
        """
        # 构建消息列表
        messages = [ChatMessage(role="system", content=self.system_prompt)]
        messages.extend(self.conversation_history)
        messages.append(ChatMessage(role="user", content=message))
        
        if stream:
            # 流式输出
            content_parts = []
            async for chunk in self.llm_client.chat(
                messages=messages,
                model=self.model,
                stream=True
            ):
                content_parts.append(chunk)
                print(chunk, end="", flush=True)
            print()  # 换行
            content = "".join(content_parts)
        else:
            response = await self.llm_client.chat(
                messages=messages,
                model=self.model
            )
            content = response.content
            self._total_tokens += response.usage.get("total_tokens", 0)
        
        self._request_count += 1
        
        # 保存到历史
        self._add_to_history(message, content)
        
        return content
    
    async def analyze(self, data: str, task: str = "分析") -> str:
        """
        分析数据
        
        Args:
            data: 要分析的数据
            task: 分析任务描述
            
        Returns:
            分析结果
        """
        prompt = f"请{task}以下数据：\n\n{data}"
        return await self.think(prompt)
    
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """
        总结文本
        
        Args:
            text: 要总结的文本
            max_length: 最大长度
            
        Returns:
            总结内容
        """
        prompt = f"请总结以下内容，不超过{max_length}字：\n\n{text}"
        return await self.think(prompt)
    
    def _add_to_history(self, user_msg: str, assistant_msg: str):
        """添加到历史记录"""
        self.conversation_history.append(ChatMessage(role="user", content=user_msg))
        self.conversation_history.append(ChatMessage(role="assistant", content=assistant_msg))
        
        # 截断历史
        if len(self.conversation_history) > self.max_history * 2:
            # 保留系统提示之后的最近记录
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
            "history_length": len(self.conversation_history) // 2,
            "max_history": self.max_history,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = {
            "id": getattr(self, 'id', 'unknown'),
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "expertise": self.expertise,
            "bias": self.bias,
            "catchphrase": self.catchphrase,
            "skills": getattr(self, 'skills', []),
            "mcp_tools": getattr(self, 'mcp_tools', []),
        }
        
        # 添加LLM相关字段
        base_dict["llm_enabled"] = True
        base_dict["model"] = self.model
        base_dict["stats"] = self.get_stats()
        
        return base_dict
