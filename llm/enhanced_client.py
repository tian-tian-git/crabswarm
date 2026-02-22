"""
增强型LLM客户端

集成重试、缓存、成本追踪等高级功能
"""

from typing import List, Dict, Optional, Union, AsyncIterator, Any, Callable
import asyncio
import time

from .adapters.base import ChatMessage, ChatResponse
from .adapters import SiliconFlowAdapter, OpenRouterAdapter, KimiAdapter
from .config import LLMConfig, ModelProvider, resolve_model
from .exceptions import LLMError, ModelNotFoundError, CostLimitError
from .retry import RetryConfig, retry_async, DEFAULT_RETRY_CONFIG
from .cache import ResponseCache
from .cost import CostTracker


class EnhancedLLMClient:
    """
    增强型LLM客户端
    
    集成以下功能:
    - 自动重试机制
    - 响应缓存
    - 成本追踪
    - 多提供商fallback
    
    示例:
        >>> config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key="sk-xxx")
        >>> client = EnhancedLLMClient(config)
        >>> response = await client.chat([
        ...     ChatMessage(role="user", content="Hello")
        ... ])
    """
    
    def __init__(
        self,
        config: LLMConfig,
        retry_config: Optional[RetryConfig] = None,
        enable_cache: bool = True,
        cache_size: int = 1000,
        enable_cost_tracking: bool = True,
        daily_budget_usd: float = 10.0,
        fallback_client: Optional['EnhancedLLMClient'] = None,
    ):
        """
        初始化增强型客户端
        
        Args:
            config: LLM配置
            retry_config: 重试配置，None则使用默认
            enable_cache: 是否启用缓存
            cache_size: 缓存大小
            enable_cost_tracking: 是否启用成本追踪
            daily_budget_usd: 每日预算(美元)
            fallback_client: fallback客户端
        """
        self.config = config
        self.adapter = self._create_adapter()
        self.retry_config = retry_config or DEFAULT_RETRY_CONFIG
        self.fallback_client = fallback_client
        
        # 缓存
        self.cache = ResponseCache(max_size=cache_size) if enable_cache else None
        
        # 成本追踪
        self.cost_tracker = None
        if enable_cost_tracking:
            self.cost_tracker = CostTracker(
                daily_budget_usd=daily_budget_usd,
                on_alert=self._on_cost_alert,
            )
        
        # 统计
        self._request_count = 0
        self._total_tokens = 0
        self._cache_hits = 0
        self._fallback_count = 0
    
    def _create_adapter(self):
        """创建适配器"""
        adapters = {
            ModelProvider.SILICONFLOW: SiliconFlowAdapter,
            ModelProvider.OPENROUTER: OpenRouterAdapter,
            ModelProvider.KIMI: KimiAdapter,
        }
        
        adapter_class = adapters.get(self.config.provider)
        if not adapter_class:
            raise ModelNotFoundError(f"Provider {self.config.provider.value} not supported")
        
        return adapter_class(self.config)
    
    def _on_cost_alert(self, alert):
        """成本告警回调"""
        print(f"[Cost Alert] {alert.level}: {alert.message}")
    
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
        use_cache: bool = True,
        check_budget: bool = True,
        **kwargs
    ) -> Union[ChatResponse, AsyncIterator[str]]:
        """
        发送对话请求（带重试和缓存）
        
        Args:
            messages: 消息列表
            model: 模型标识符
            temperature: 温度
            max_tokens: 最大token数
            top_p: Top P
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            stream: 是否流式
            tools: 工具定义
            use_cache: 是否使用缓存
            check_budget: 是否检查预算
            **kwargs: 其他参数
            
        Returns:
            ChatResponse 或 AsyncIterator
        """
        # 检查预算
        if check_budget and self.cost_tracker:
            status = self.cost_tracker.get_budget_status()
            if status["is_over_budget"]:
                raise CostLimitError(status["current_cost"], self.daily_budget_usd)
        
        model_id = self._resolve_model(model)
        
        # 流式请求不缓存
        if stream:
            return await self._chat_with_retry(
                messages=messages,
                model=model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=True,
                tools=tools,
            )
        
        # 检查缓存
        if use_cache and self.cache:
            cached = self.cache.get(messages, model_id, temperature)
            if cached:
                self._cache_hits += 1
                return cached
        
        # 执行请求（带重试）
        try:
            response = await self._chat_with_retry(
                messages=messages,
                model=model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                tools=tools,
            )
        except Exception as e:
            # 尝试fallback
            if self.fallback_client:
                self._fallback_count += 1
                return await self.fallback_client.chat(
                    messages, model, temperature, max_tokens,
                    top_p, frequency_penalty, presence_penalty,
                    False, tools, use_cache, check_budget, **kwargs
                )
            raise
        
        # 更新统计
        self._request_count += 1
        self._total_tokens += response.usage.get("total_tokens", 0)
        
        # 记录成本
        if self.cost_tracker:
            self.cost_tracker.record_usage(
                model=model_id,
                prompt_tokens=response.usage.get("prompt_tokens", 0),
                completion_tokens=response.usage.get("completion_tokens", 0),
                latency_ms=response.latency_ms,
            )
        
        # 缓存响应
        if use_cache and self.cache:
            self.cache.set(messages, model_id, response, temperature)
        
        return response
    
    async def _chat_with_retry(self, **kwargs) -> ChatResponse:
        """带重试的对话请求"""
        is_stream = kwargs.pop('stream', False)
        
        if is_stream:
            return self.adapter.chat_stream(**kwargs)
        
        return await retry_async(
            self.adapter.chat,
            config=self.retry_config,
            **kwargs
        )
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
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
            ChatResponse
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
    
    def _resolve_model(self, model: Optional[str]) -> str:
        """解析模型名称"""
        if model is None:
            return self.config.default_model
        return resolve_model(model, self.config.provider)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
            "cache_hits": self._cache_hits,
            "fallback_count": self._fallback_count,
            "provider": self.config.provider.value,
            "default_model": self.config.default_model,
        }
        
        if self.cache:
            stats["cache"] = self.cache.get_stats()
        
        if self.cost_tracker:
            stats["cost"] = self.cost_tracker.get_budget_status()
        
        return stats
    
    def get_cost_report(self) -> Dict[str, Any]:
        """获取成本报告"""
        if self.cost_tracker:
            return self.cost_tracker.get_report()
        return {"error": "Cost tracking not enabled"}
    
    def clear_cache(self):
        """清除缓存"""
        if self.cache:
            self.cache.invalidate()


class MultiProviderClient:
    """
    多提供商客户端
    
    自动在主提供商失败时切换到备用提供商
    """
    
    def __init__(
        self,
        providers: List[LLMConfig],
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        初始化多提供商客户端
        
        Args:
            providers: 提供商配置列表（按优先级排序）
            retry_config: 重试配置
        """
        if not providers:
            raise ValueError("At least one provider config is required")
        
        self.providers = providers
        self.retry_config = retry_config or DEFAULT_RETRY_CONFIG
        
        # 创建客户端链
        self.primary_client = None
        prev_client = None
        
        for config in reversed(providers):
            client = EnhancedLLMClient(
                config=config,
                retry_config=retry_config,
                enable_cache=(prev_client is None),  # 只在主客户端启用缓存
                fallback_client=prev_client,
            )
            prev_client = client
        
        self.primary_client = prev_client
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送对话请求"""
        return await self.primary_client.chat(messages, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.primary_client.get_stats()
