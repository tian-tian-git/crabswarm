# crabswarm/llm/adapters/siliconflow.py
"""
SiliconFlow 适配器
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


class SiliconFlowAdapter(BaseAdapter):
    """SiliconFlow API 适配器"""
    
    def __init__(self, config):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("OpenAI SDK is required. Install with: pip install openai")
        
        self.client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://api.siliconflow.cn/v1",
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
        """发送对话请求"""
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
            
            # 处理DeepSeek-R1的思维链
            reasoning_content = getattr(message, 'reasoning_content', None)
            
            return ChatResponse(
                content=message.content or "",
                reasoning_content=reasoning_content,
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
            raise AuthenticationError("siliconflow")
        except openai.APIError as e:
            if "token" in str(e).lower():
                raise TokenLimitError(message=str(e))
            raise ProviderError("siliconflow", str(e), getattr(e, 'status_code', None))
        except Exception as e:
            raise ProviderError("siliconflow", str(e))
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_chunk: Optional[callable] = None,
    ) -> AsyncIterator[str]:
        """流式对话"""
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
            raise ProviderError("siliconflow", f"Stream error: {str(e)}")
