# crabswarm/llm/__init__.py
"""
CrabSwarm LLM Integration Module

提供LLM调用能力，支持多模型路由和成本优化。

示例:
    >>> from crabswarm.llm import LLMClient, LLMConfig, ModelProvider
    >>> config = LLMConfig(
    ...     provider=ModelProvider.SILICONFLOW,
    ...     api_key="sk-xxx"
    ... )
    >>> client = LLMClient(config)
    >>> response = await client.chat([
    ...     ChatMessage(role="user", content="Hello")
    ... ])
"""

from .config import LLMConfig, ModelProvider, ModelTier, load_config
from .client import LLMClient, ChatMessage, ChatResponse
from .router import ModelRouter, RoutingRule
from .agent import LLMAgent
from .cost import CostTracker, TokenTracker
from .exceptions import (
    LLMError, 
    RateLimitError, 
    TokenLimitError,
    ProviderError,
    CostLimitError,
    TimeoutError,
    AuthenticationError,
    ModelNotFoundError,
)
from .retry import (
    RetryConfig,
    retry_async,
    with_retry,
    RetryHandler,
    DEFAULT_RETRY_CONFIG,
    RATE_LIMIT_RETRY_CONFIG,
    NETWORK_RETRY_CONFIG,
    FAST_FAIL_CONFIG,
    retry_with_fallback,
)
from .cache import ResponseCache, CachingClient

__version__ = "1.0.0"
__all__ = [
    # 配置
    "LLMConfig",
    "ModelProvider", 
    "ModelTier",
    "load_config",
    # 客户端
    "LLMClient",
    "ChatMessage",
    "ChatResponse",
    # 路由
    "ModelRouter",
    "RoutingRule",
    # 智能体
    "LLMAgent",
    # 成本
    "CostTracker",
    "TokenTracker",
    # 异常
    "LLMError",
    "RateLimitError",
    "TokenLimitError",
    "ProviderError",
    "CostLimitError",
    "TimeoutError",
    "AuthenticationError",
    "ModelNotFoundError",
    # 重试
    "RetryConfig",
    "retry_async",
    "with_retry",
    "RetryHandler",
    "DEFAULT_RETRY_CONFIG",
    "RATE_LIMIT_RETRY_CONFIG",
    "NETWORK_RETRY_CONFIG",
    "FAST_FAIL_CONFIG",
    "retry_with_fallback",
    # 缓存
    "ResponseCache",
    "CachingClient",
]
