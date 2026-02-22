# crabswarm/llm/adapters/base.py
"""
LLM适配器基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, AsyncIterator
from dataclasses import dataclass
import time


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    usage: Dict[str, int] = None
    model: str = ""
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


class BaseAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: Any):
        self.config = config
        self._client = None
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_chunk: Optional[callable] = None,
    ) -> AsyncIterator[str]:
        """流式对话"""
        pass
    
    def _prepare_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """准备消息格式"""
        return [msg.to_dict() for msg in messages]
    
    def _parse_usage(self, usage: Any) -> Dict[str, int]:
        """解析用量信息"""
        if hasattr(usage, 'prompt_tokens'):
            return {
                "prompt_tokens": usage.prompt_tokens or 0,
                "completion_tokens": usage.completion_tokens or 0,
                "total_tokens": usage.total_tokens or 0,
            }
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    def _measure_latency(self, start_time: float) -> float:
        """测量延迟"""
        return (time.time() - start_time) * 1000
