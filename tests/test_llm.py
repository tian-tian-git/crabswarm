"""
LLM模块测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.config import (
    LLMConfig, 
    ModelProvider, 
    ModelTier,
    MODEL_MAPPING,
    TIER_MODEL_MAPPING,
    resolve_model,
    get_model_price
)
from llm.adapters.base import ChatMessage, ChatResponse
from llm.exceptions import LLMError, RateLimitError, TokenLimitError


class TestLLMConfig:
    """测试LLM配置"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        assert config.provider == ModelProvider.SILICONFLOW
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.siliconflow.cn/v1"
        assert config.default_model == "deepseek-ai/DeepSeek-V3"
    
    def test_config_openrouter(self):
        """测试OpenRouter配置"""
        config = LLMConfig(
            provider=ModelProvider.OPENROUTER,
            api_key="test-key"
        )
        assert config.provider == ModelProvider.OPENROUTER
        assert config.base_url == "https://openrouter.ai/api/v1"
    
    def test_config_custom_values(self):
        """测试自定义配置值"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key",
            base_url="https://custom.api.com",
            default_model="custom-model",
            timeout=120,
            max_retries=5
        )
        assert config.base_url == "https://custom.api.com"
        assert config.default_model == "custom-model"
        assert config.timeout == 120
        assert config.max_retries == 5


class TestModelMapping:
    """测试模型映射"""
    
    def test_resolve_model_deepseek_v3(self):
        """测试DeepSeek-V3解析"""
        result = resolve_model("deepseek-v3", ModelProvider.SILICONFLOW)
        assert result == "deepseek-ai/DeepSeek-V3"
        
        result = resolve_model("deepseek-v3", ModelProvider.OPENROUTER)
        assert result == "deepseek/deepseek-chat"
    
    def test_resolve_model_deepseek_r1(self):
        """测试DeepSeek-R1解析"""
        result = resolve_model("deepseek-r1", ModelProvider.SILICONFLOW)
        assert result == "deepseek-ai/DeepSeek-R1"
    
    def test_resolve_model_custom(self):
        """测试自定义模型解析"""
        result = resolve_model("custom-model", ModelProvider.SILICONFLOW)
        assert result == "custom-model"
    
    def test_get_model_price(self):
        """测试获取模型价格"""
        price = get_model_price("deepseek-ai/DeepSeek-V3")
        assert price["input"] == 2.0
        assert price["output"] == 8.0
    
    def test_get_model_price_unknown(self):
        """测试未知模型价格"""
        price = get_model_price("unknown-model")
        assert price["input"] == 0.0
        assert price["output"] == 0.0
    
    def test_tier_mapping(self):
        """测试层级映射"""
        assert TIER_MODEL_MAPPING[ModelTier.FAST] == "qwen2.5-14b"
        assert TIER_MODEL_MAPPING[ModelTier.BALANCED] == "qwen2.5-32b"
        assert TIER_MODEL_MAPPING[ModelTier.POWERFUL] == "deepseek-v3"
        assert TIER_MODEL_MAPPING[ModelTier.REASONING] == "deepseek-r1"


class TestChatMessage:
    """测试聊天消息"""
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
    
    def test_message_to_dict(self):
        """测试消息转字典"""
        msg = ChatMessage(role="user", content="Hello")
        result = msg.to_dict()
        assert result == {"role": "user", "content": "Hello"}
    
    def test_message_with_name(self):
        """测试带名称的消息"""
        msg = ChatMessage(role="assistant", content="Hi", name="Agent1")
        result = msg.to_dict()
        assert result == {"role": "assistant", "content": "Hi", "name": "Agent1"}


class TestChatResponse:
    """测试聊天响应"""
    
    def test_response_creation(self):
        """测试响应创建"""
        response = ChatResponse(content="Hello")
        assert response.content == "Hello"
        assert response.usage == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    def test_response_with_usage(self):
        """测试带用量的响应"""
        response = ChatResponse(
            content="Hello",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        )
        assert response.usage["total_tokens"] == 15


class TestExceptions:
    """测试异常类"""
    
    def test_llm_error(self):
        """测试基础错误"""
        error = LLMError("Test error", {"detail": "info"})
        assert error.message == "Test error"
        assert error.details == {"detail": "info"}
    
    def test_rate_limit_error(self):
        """测试限流错误"""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "60s" in error.message
    
    def test_token_limit_error(self):
        """测试Token限制错误"""
        error = TokenLimitError(max_tokens=1000, requested=1500)
        assert error.max_tokens == 1000
        assert error.requested == 1500
        assert "1500 > 1000" in error.message


class TestModelProvider:
    """测试模型提供商枚举"""
    
    def test_provider_values(self):
        """测试提供商值"""
        assert ModelProvider.SILICONFLOW.value == "siliconflow"
        assert ModelProvider.OPENROUTER.value == "openrouter"
        assert ModelProvider.KIMI.value == "kimi"


class TestModelTier:
    """测试模型层级枚举"""
    
    def test_tier_values(self):
        """测试层级值"""
        assert ModelTier.FAST.value == "fast"
        assert ModelTier.BALANCED.value == "balanced"
        assert ModelTier.POWERFUL.value == "powerful"
        assert ModelTier.REASONING.value == "reasoning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
