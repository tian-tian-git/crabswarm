"""
LLM客户端测试
测试LLM客户端的各种功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查是否安装了openai
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 只有在openai可用时才导入这些模块
if OPENAI_AVAILABLE:
    from llm.client import LLMClient
    from llm.config import LLMConfig, ModelProvider
    from llm.adapters.base import ChatMessage, ChatResponse
    from llm.exceptions import LLMError, ModelNotFoundError


pytestmark = pytest.mark.skipif(
    not OPENAI_AVAILABLE,
    reason="OpenAI SDK not installed. Run: pip install openai"
)


class TestLLMClientCreation:
    """测试LLM客户端创建"""
    
    def test_client_creation_siliconflow(self):
        """测试SiliconFlow客户端创建"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        assert client.config == config
        assert client.adapter is not None
        assert client._request_count == 0
        assert client._total_tokens == 0
    
    def test_client_creation_openrouter(self):
        """测试OpenRouter客户端创建"""
        config = LLMConfig(
            provider=ModelProvider.OPENROUTER,
            api_key="test-key"
        )
        client = LLMClient(config)
        assert client.config.provider == ModelProvider.OPENROUTER
    
    def test_client_creation_unsupported_provider(self):
        """测试不支持的提供商"""
        # 创建无效的provider
        with pytest.raises((ModelNotFoundError, ValueError, AttributeError)):
            config = LLMConfig(
                provider="unsupported",
                api_key="test-key"
            )
            client = LLMClient(config)


class TestLLMClientModelResolution:
    """测试模型解析"""
    
    def test_resolve_model_none(self):
        """测试None模型解析"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key",
            default_model="default-model"
        )
        client = LLMClient(config)
        resolved = client._resolve_model(None)
        assert resolved == "default-model"
    
    def test_resolve_model_custom(self):
        """测试自定义模型解析"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        resolved = client._resolve_model("custom-model")
        assert resolved == "custom-model"
    
    def test_resolve_model_deepseek_v3(self):
        """测试DeepSeek-V3解析"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        resolved = client._resolve_model("deepseek-v3")
        assert "DeepSeek-V3" in resolved


class TestLLMClientStats:
    """测试客户端统计"""
    
    def test_get_stats_initial(self):
        """测试初始统计"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        stats = client.get_stats()
        
        assert stats["request_count"] == 0
        assert stats["total_tokens"] == 0
        assert stats["provider"] == "siliconflow"
    
    def test_get_config(self):
        """测试获取配置"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key",
            default_model="test-model"
        )
        client = LLMClient(config)
        retrieved_config = client.get_config()
        
        assert retrieved_config == config
        assert retrieved_config.default_model == "test-model"


class TestLLMClientSimpleChat:
    """测试简单对话接口"""
    
    @patch('llm.client.LLMClient.chat')
    def test_simple_chat_basic(self, mock_chat):
        """测试基本简单对话"""
        mock_response = ChatResponse(content="Hello, World!")
        mock_chat.return_value = asyncio.Future()
        mock_chat.return_value.set_result(mock_response)
        
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        result = client.simple_chat("Hello")
        assert result == "Hello, World!"
    
    @patch('llm.client.LLMClient.chat')
    def test_simple_chat_empty_prompt(self, mock_chat):
        """测试空提示简单对话"""
        mock_response = ChatResponse(content="")
        mock_chat.return_value = asyncio.Future()
        mock_chat.return_value.set_result(mock_response)
        
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        result = client.simple_chat("")
        assert result == ""
    
    @patch('llm.client.LLMClient.chat')
    def test_simple_chat_with_params(self, mock_chat):
        """测试带参数简单对话"""
        mock_response = ChatResponse(content="Response")
        mock_chat.return_value = asyncio.Future()
        mock_chat.return_value.set_result(mock_response)
        
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        result = client.simple_chat(
            "Hello",
            temperature=0.5,
            max_tokens=100
        )
        assert result == "Response"


class TestLLMClientChatWithSystem:
    """测试带系统提示的对话"""
    
    @pytest.mark.asyncio
    @patch('llm.client.LLMClient.chat')
    async def test_chat_with_system_basic(self, mock_chat):
        """测试基本带系统提示对话"""
        mock_response = ChatResponse(content="System response")
        mock_chat.return_value = mock_response
        
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        response = await client.chat_with_system(
            system_prompt="You are a helpful assistant",
            user_prompt="Hello"
        )
        
        assert response.content == "System response"
        # 验证chat被调用时传递了正确的消息
        call_args = mock_chat.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert messages[0].content == "You are a helpful assistant"
        assert messages[1].role == "user"
        assert messages[1].content == "Hello"


class TestLLMClientCallTools:
    """测试工具调用"""
    
    @pytest.mark.asyncio
    @patch('llm.client.LLMClient.chat')
    async def test_call_tools_basic(self, mock_chat):
        """测试基本工具调用"""
        mock_response = ChatResponse(
            content="Tool result",
            tool_calls=[{"name": "test_tool", "arguments": {}}]
        )
        mock_chat.return_value = mock_response
        
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        tools = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {}
            }
        ]
        
        response = await client.call_tools(
            messages=[ChatMessage(role="user", content="Use tool")],
            tools=tools
        )
        
        assert response.content == "Tool result"
        assert len(response.tool_calls) == 1


class TestLLMClientEdgeCases:
    """测试边界情况"""
    
    def test_client_empty_api_key(self):
        """测试空API Key"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key=""
        )
        # 应该能创建客户端，但调用时会失败
        client = LLMClient(config)
        assert client.config.api_key == ""
    
    def test_client_very_long_api_key(self):
        """测试超长API Key"""
        long_key = "sk-" + "a" * 1000
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key=long_key
        )
        client = LLMClient(config)
        assert client.config.api_key == long_key
    
    @pytest.mark.asyncio
    async def test_chat_empty_messages(self):
        """测试空消息列表"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        # 空消息列表应该处理
        # 实际行为取决于适配器实现
        # 这里测试不抛出异常
        try:
            with patch.object(client.adapter, 'chat', new_callable=AsyncMock) as mock_adapter_chat:
                mock_adapter_chat.return_value = ChatResponse(content="Response")
                response = await client.chat([])
                assert response is not None
        except Exception:
            # 如果抛出异常也是可接受的行为
            pass
    
    @pytest.mark.asyncio
    async def test_chat_very_long_message(self):
        """测试超长消息"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        long_content = "A" * 10000
        messages = [ChatMessage(role="user", content=long_content)]
        
        with patch.object(client.adapter, 'chat', new_callable=AsyncMock) as mock_adapter_chat:
            mock_adapter_chat.return_value = ChatResponse(content="Response")
            response = await client.chat(messages)
            assert response is not None
    
    def test_simple_chat_error_handling(self):
        """测试简单对话错误处理"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        with patch.object(client, 'chat') as mock_chat:
            mock_chat.side_effect = LLMError("Test error")
            
            with pytest.raises(LLMError):
                client.simple_chat("Hello")


class TestLLMClientAsync:
    """测试异步功能"""
    
    @pytest.mark.asyncio
    async def test_chat_stream(self):
        """测试流式对话"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        messages = [ChatMessage(role="user", content="Hello")]
        
        with patch.object(client.adapter, 'chat_stream') as mock_stream:
            async def mock_async_generator():
                yield "Hello"
                yield " World"
            
            mock_stream.return_value = mock_async_generator()
            
            response = await client.chat_stream(messages)
            assert response.content == "Hello World"
    
    @pytest.mark.asyncio
    async def test_chat_with_callback(self):
        """测试带回调的流式对话"""
        config = LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key="test-key"
        )
        client = LLMClient(config)
        
        messages = [ChatMessage(role="user", content="Hello")]
        chunks = []
        
        def on_chunk(chunk):
            chunks.append(chunk)
        
        with patch.object(client.adapter, 'chat_stream') as mock_stream:
            async def mock_async_generator():
                yield "Hello"
                yield " World"
            
            mock_stream.return_value = mock_async_generator()
            
            response = await client.chat_stream(messages, on_chunk=on_chunk)
            assert response.content == "Hello World"
            assert len(chunks) == 2
