# crabswarm/llm/exceptions.py
"""
LLM模块异常定义
"""


class LLMError(Exception):
    """LLM基础错误"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RateLimitError(LLMError):
    """限流错误"""
    
    def __init__(self, retry_after: int = 60, message: str = None):
        self.retry_after = retry_after
        msg = message or f"Rate limit exceeded. Retry after {retry_after}s"
        super().__init__(msg)


class TokenLimitError(LLMError):
    """Token超限错误"""
    
    def __init__(self, max_tokens: int = None, requested: int = None):
        self.max_tokens = max_tokens
        self.requested = requested
        msg = f"Token limit exceeded"
        if max_tokens and requested:
            msg = f"Token limit exceeded: {requested} > {max_tokens}"
        super().__init__(msg)


class ProviderError(LLMError):
    """提供商错误"""
    
    def __init__(self, provider: str, message: str, status_code: int = None):
        self.provider = provider
        self.status_code = status_code
        msg = f"Provider {provider} error: {message}"
        super().__init__(msg)


class CostLimitError(LLMError):
    """成本超限错误"""
    
    def __init__(self, current_cost: float, budget: float):
        self.current_cost = current_cost
        self.budget = budget
        msg = f"Cost limit exceeded: ${current_cost:.2f} > ${budget:.2f}"
        super().__init__(msg)


class ModelNotFoundError(LLMError):
    """模型未找到错误"""
    
    def __init__(self, model: str, provider: str = None):
        self.model = model
        self.provider = provider
        msg = f"Model not found: {model}"
        if provider:
            msg += f" for provider {provider}"
        super().__init__(msg)


class TimeoutError(LLMError):
    """超时错误"""
    
    def __init__(self, timeout: float):
        self.timeout = timeout
        msg = f"Request timeout after {timeout}s"
        super().__init__(msg)


class AuthenticationError(LLMError):
    """认证错误"""
    
    def __init__(self, provider: str):
        self.provider = provider
        msg = f"Authentication failed for {provider}. Please check your API key."
        super().__init__(msg)
