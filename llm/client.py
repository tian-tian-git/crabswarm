# crabswarm/llm/client.py
"""
LLM客户端核心实现
"""

from typing import List, Dict, Optional, Union, AsyncIterator, Any
import asyncio
import time

from .adapters.base import ChatMessage, ChatResponse
from .adapters import SiliconFlowAdapter, OpenRouterAdapter
from .config import LLMConfig, ModelProvider, resolve_model
from .exceptions import LLMError, ModelNotFoundError


class LLMClient:
    """
    LLM客户端
    
    统一接口调用不同LLM提供商的API
    
    示例:
        >>> config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key="sk-xxx")
        >>> client = LLMClient(config)
        >>> response = await client.chat([
        ...     ChatMessage(role="user", content="Hello")
        ... ])
    """
    
    def __init__(self, config: LLMConfig):
        """
        初始化LLM客户端
        
        Args:
            config: LLM配置
        """
        self.config = config
        self.adapter = self._create_adapter()
        self._request_count = 0
        self._total_tokens = 0
    
    def _create_adapter(self):
        """创建适配器"""
        adapters = {
            ModelProvider.SILICONFLOW: SiliconFlowAdapter,
            ModelProvider.OPENROUTER: OpenRouterAdapter,
        }
        
        adapter_class = adapters.get(self.config.provider)
        if not adapter_class:
            raise ModelNotFoundError(f"Provider {self.config.provider.value} not supported")
        
        return adapter_class(self.config)
    
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        on_chunk: Optional[callable] = None,
    ) -> Union[ChatResponse, AsyncIterator[str]]:
        """
        发送对话请求
        
        Args:
            messages: 消息列表
            model: 模型标识符或完整模型名
            temperature: 温度 (0-2)
            max_tokens: 最大token数
            top_p: Top P采样
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            stream: 是否流式输出
            tools: 工具定义
            on_chunk: 流式回调函数
            
        Returns:
            ChatResponse 或 AsyncIterator[str] (流式)
        """
        # 解析模型名称
        model_id = self._resolve_model(model)
        
        if stream:
            return self.adapter.chat_stream(
                messages=messages,
                model=model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                on_chunk=on_chunk,
            )
        
        response = await self.adapter.chat(
            messages=messages,
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            tools=tools,
        )
        
        # 更新统计
        self._request_count += 1
        self._total_tokens += response.usage.get("total_tokens", 0)
        
        return response
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_chunk: Optional[callable] = None,
    ) -> ChatResponse:
        """
        流式对话（收集完整响应）
        
        Args:
            messages: 消息列表
            model: 模型标识符
            temperature: 温度
            max_tokens: 最大token数
            on_chunk: 流式回调
            
        Returns:
            ChatResponse (包含完整内容)
        """
        model_id = self._resolve_model(model)
        
        content_parts = []
        async for chunk in self.adapter.chat_stream(
            messages=messages,
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            on_chunk=on_chunk,
        ):
            content_parts.append(chunk)
        
        full_content = "".join(content_parts)
        
        self._request_count += 1
        
        return ChatResponse(
            content=full_content,
            model=model_id,
            finish_reason="stop",
        )
    
    def simple_chat(self, prompt: str, **kwargs) -> str:
        """
        简单对话（同步接口）
        
        Args:
            prompt: 用户输入
            **kwargs: 其他参数
            
        Returns:
            响应文本
        """
        messages = [ChatMessage(role="user", content=prompt)]
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(self.chat(messages, **kwargs))
        return response.content
    
    async def chat_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> ChatResponse:
        """
        带系统提示的对话
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            **kwargs: 其他参数
            
        Returns:
            ChatResponse
        """
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]
        return await self.chat(messages, **kwargs)
    
    async def call_tools(
        self,
        messages: List[ChatMessage],
        tools: List[Dict],
        **kwargs
    ) -> ChatResponse:
        """
        函数调用（Tool Use）
        
        Args:
            messages: 消息列表
            tools: 工具定义
            **kwargs: 其他参数
            
        Returns:
            ChatResponse (包含tool_calls)
        """
        return await self.chat(messages, tools=tools, **kwargs)
    
    def _resolve_model(self, model: Optional[str]) -> str:
        """解析模型名称"""
        if model is None:
            return self.config.default_model
        
        # 检查是否是预定义的模型key
        resolved = resolve_model(model, self.config.provider)
        return resolved
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
            "provider": self.config.provider.value,
            "default_model": self.config.default_model,
        }
    
    def get_config(self) -> LLMConfig:
        """获取配置"""
        return self.config
