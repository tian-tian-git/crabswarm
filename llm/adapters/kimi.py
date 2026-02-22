"""
Kimi (Moonshot) 适配器

支持Moonshot AI API的适配器实现
"""

from typing import List, Dict, Optional, AsyncIterator
import time

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from .base import BaseAdapter, ChatMessage, ChatResponse
from ..exceptions import RateLimitError, TokenLimitError, ProviderError, AuthenticationError


class KimiAdapter(BaseAdapter):
    """
    Kimi (Moonshot) API 适配器
    
    支持Moonshot AI的API调用，包括流式输出
    """
    
    def __init__(self, config):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("OpenAI SDK is required. Install with: pip install openai")
        
        self.client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://api.moonshot.cn/v1",
            timeout=config.timeout,
        )
    
    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        tools: Optional[List[Dict]] = None,
    ) -> ChatResponse:
        """
        发送对话请求
        
        Args:
            messages: 消息列表
            model: 模型名称 (如 moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
            temperature: 温度 (0-2)
            max_tokens: 最大token数
            top_p: Top P采样
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            tools: 工具定义
            
        Returns:
            ChatResponse
        """
        start_time = time.time()
        
        try:
            params = {
                "model": model,
                "messages": self._prepare_messages(messages),
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            if top_p is not None:
                params["top_p"] = top_p
            if frequency_penalty is not None:
                params["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                params["presence_penalty"] = presence_penalty
            if tools:
                params["tools"] = tools
            
            response = await self.client.chat.completions.create(**params)
            
            choice = response.choices[0]
            message = choice.message
            
            return ChatResponse(
                content=message.content or "",
                tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
                usage=self._parse_usage(response.usage),
                model=response.model,
                finish_reason=choice.finish_reason or "stop",
                latency_ms=self._measure_latency(start_time),
            )
            
        except openai.RateLimitError as e:
            retry_after = int(e.headers.get('retry-after', 60)) if hasattr(e, 'headers') else 60
            raise RateLimitError(retry_after=retry_after)
        except openai.AuthenticationError as e:
            raise AuthenticationError("kimi")
        except openai.APIError as e:
            if "token" in str(e).lower():
                raise TokenLimitError(message=str(e))
            raise ProviderError("kimi", str(e), getattr(e, 'status_code', None))
        except Exception as e:
            raise ProviderError("kimi", str(e))
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_chunk: Optional[callable] = None,
    ) -> AsyncIterator[str]:
        """
        流式对话
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度
            max_tokens: 最大token数
            on_chunk: 流式回调函数
            
        Yields:
            文本块
        """
        try:
            params = {
                "model": model,
                "messages": self._prepare_messages(messages),
                "temperature": temperature,
                "stream": True,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    content = delta.content or ""
                    if content:
                        if on_chunk:
                            on_chunk(content)
                        yield content
                        
        except Exception as e:
            raise ProviderError("kimi", f"Stream error: {str(e)}")
