"""
重试机制模块

提供LLM请求的重试策略，包括指数退避和特定错误处理
"""

import asyncio
import time
import random
from typing import TypeVar, Callable, Any, Optional, List, Type
from functools import wraps

from .exceptions import (
    LLMError, 
    RateLimitError, 
    TokenLimitError, 
    ProviderError,
    TimeoutError,
    AuthenticationError
)


T = TypeVar('T')


class RetryConfig:
    """
    重试配置
    
    Attributes:
        max_retries: 最大重试次数
        base_delay: 基础延迟(秒)
        max_delay: 最大延迟(秒)
        exponential_base: 指数基数
        retryable_exceptions: 可重试的异常类型
        on_retry: 重试回调函数
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        on_retry: Optional[Callable[[Exception, int, float], None]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions or [
            RateLimitError,
            ProviderError,
            TimeoutError,
        ]
        self.on_retry = on_retry
    
    def calculate_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """
        计算重试延迟
        
        Args:
            attempt: 当前尝试次数 (从1开始)
            retry_after: 服务器建议的重试时间
            
        Returns:
            延迟秒数
        """
        if retry_after is not None:
            return retry_after
        
        # 指数退避 + 抖动
        delay = min(
            self.base_delay * (self.exponential_base ** (attempt - 1)),
            self.max_delay
        )
        # 添加随机抖动 (±20%)
        jitter = delay * 0.2 * (2 * random.random() - 1)
        return delay + jitter


# 默认重试配置
DEFAULT_RETRY_CONFIG = RetryConfig()


async def retry_async(
    func: Callable[..., Any],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    异步函数重试包装器
    
    Args:
        func: 要重试的异步函数
        *args: 函数参数
        config: 重试配置
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值
        
    Raises:
        最后一次重试的异常
    """
    config = config or DEFAULT_RETRY_CONFIG
    last_exception = None
    
    for attempt in range(1, config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except tuple(config.retryable_exceptions) as e:
            last_exception = e
            
            # 如果是最后一次尝试，抛出异常
            if attempt == config.max_retries:
                raise
            
            # 获取建议的重试时间
            retry_after = None
            if isinstance(e, RateLimitError) and hasattr(e, 'retry_after'):
                retry_after = e.retry_after
            
            # 计算延迟
            delay = config.calculate_delay(attempt, retry_after)
            
            # 调用回调
            if config.on_retry:
                config.on_retry(e, attempt, delay)
            
            # 等待后重试
            await asyncio.sleep(delay)
    
    # 理论上不会到达这里
    raise last_exception


def with_retry(config: Optional[RetryConfig] = None):
    """
    重试装饰器
    
    Args:
        config: 重试配置
        
    Returns:
        装饰器函数
        
    Example:
        @with_retry(RetryConfig(max_retries=5))
        async def my_async_function():
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(func, *args, config=config, **kwargs)
        return wrapper
    return decorator


class RetryHandler:
    """
    重试处理器
    
    提供更精细的重试控制
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or DEFAULT_RETRY_CONFIG
        self._retry_count = 0
        self._total_delay = 0.0
    
    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        执行带重试的函数
        
        Args:
            func: 异步函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
        """
        self._retry_count = 0
        self._total_delay = 0.0
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except tuple(self.config.retryable_exceptions) as e:
                self._retry_count += 1
                
                if attempt == self.config.max_retries:
                    raise
                
                # 计算延迟
                retry_after = getattr(e, 'retry_after', None)
                delay = self.config.calculate_delay(attempt, retry_after)
                self._total_delay += delay
                
                if self.config.on_retry:
                    self.config.on_retry(e, attempt, delay)
                
                await asyncio.sleep(delay)
    
    def get_stats(self) -> dict:
        """获取重试统计"""
        return {
            "retry_count": self._retry_count,
            "total_delay": self._total_delay,
        }


# 特定场景的重试配置

# 用于限流场景 - 更长的延迟
RATE_LIMIT_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=2.0,
    max_delay=120.0,
    exponential_base=2.0,
)

# 用于网络不稳定场景 - 更多重试
NETWORK_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=0.5,
    max_delay=30.0,
    exponential_base=1.5,
)

# 用于快速失败场景 - 较少重试
FAST_FAIL_CONFIG = RetryConfig(
    max_retries=1,
    base_delay=0.1,
    max_delay=1.0,
)


async def retry_with_fallback(
    primary_func: Callable[..., T],
    fallback_func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """
    带fallback的重试
    
    主函数重试失败后，执行fallback函数
    
    Args:
        primary_func: 主函数
        fallback_func: fallback函数
        *args: 函数参数
        config: 重试配置
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值
    """
    try:
        return await retry_async(primary_func, *args, config=config, **kwargs)
    except Exception as e:
        # 主函数失败，执行fallback
        return await fallback_func(*args, **kwargs)
