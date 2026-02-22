# crabswarm/llm/adapters/openrouter.py
"""
OpenRouter 适配器
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


class OpenRouterAdapter(BaseAdapter):
    """OpenRouter API 适配器"""
    
    def __init__(self, config):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("OpenAI SDK is required. Install with: pip install openai")
        
        self.client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://openrouter.ai/api/v1",
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
            
            # OpenRouter 需要额外的 headers
            extra_headers = {
                "HTTP-Referer": "https://crabswarm.local",
                "X-Title": "CrabSwarm LLM Integration",
            }
            
            response = await self.client.chat.completions.create(
                **params,
                extra_headers=extra_headers
            )
            
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
            raise AuthenticationError("openrouter")
        except openai.APIError as e:
            if "token" in str(e).lower():
                raise TokenLimitError(message=str(e))
            raise ProviderError("openrouter", str(e), getattr(e, 'status_code', None))
        except Exception as e:
            raise ProviderError("openrouter", str(e))
    
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
            
            extra_headers = {
                "HTTP-Referer": "https://crabswarm.local",
                "X-Title": "CrabSwarm LLM Integration",
            }
            
            stream = await self.client.chat.completions.create(
                **params,
                extra_headers=extra_headers
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    content = delta.content or ""
                    if content:
                        if on_chunk:
                            on_chunk(content)
                        yield content
                        
        except Exception as e:
            raise ProviderError("openrouter", f"Stream error: {str(e)}")
