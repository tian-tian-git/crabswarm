"""
缓存模块

提供LLM响应缓存，减少重复请求
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from collections import OrderedDict

from .adapters.base import ChatMessage, ChatResponse


@dataclass
class CacheEntry:
    """缓存条目"""
    response: ChatResponse
    timestamp: float
    access_count: int = 0


class ResponseCache:
    """
    LLM响应缓存
    
    缓存LLM响应以减少重复请求，支持TTL和LRU淘汰
    
    Example:
        >>> cache = ResponseCache(max_size=1000, ttl_seconds=3600)
        >>> cached = cache.get(messages, model)
        >>> if cached is None:
        ...     response = await client.chat(messages, model)
        ...     cache.set(messages, model, response)
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        key_func: Optional[Callable[[List[ChatMessage], str], str]] = None,
    ):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间(秒)
            key_func: 自定义缓存键生成函数
        """
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._key_func = key_func or self._default_key_func
        self._hits = 0
        self._misses = 0
    
    def _default_key_func(self, messages: List[ChatMessage], model: str) -> str:
        """默认缓存键生成"""
        content = json.dumps([
            {"role": m.role, "content": m.content}
            for m in messages
        ], sort_keys=True) + model
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: Optional[float] = None,
    ) -> Optional[ChatResponse]:
        """
        获取缓存响应
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数(影响缓存键)
            
        Returns:
            缓存的响应或None
        """
        key = self._make_key(messages, model, temperature)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # 检查是否过期
            if time.time() - entry.timestamp < self.ttl:
                # 更新访问统计
                entry.access_count += 1
                self._cache.move_to_end(key)
                self._hits += 1
                return entry.response
            else:
                # 过期删除
                del self._cache[key]
        
        self._misses += 1
        return None
    
    def set(
        self,
        messages: List[ChatMessage],
        model: str,
        response: ChatResponse,
        temperature: Optional[float] = None,
    ):
        """
        设置缓存
        
        Args:
            messages: 消息列表
            model: 模型名称
            response: 响应对象
            temperature: 温度参数
        """
        key = self._make_key(messages, model, temperature)
        
        # LRU淘汰
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        self._cache[key] = CacheEntry(
            response=response,
            timestamp=time.time(),
        )
    
    def _make_key(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: Optional[float] = None,
    ) -> str:
        """生成缓存键"""
        base_key = self._key_func(messages, model)
        if temperature is not None:
            base_key += f":{temperature}"
        return base_key
    
    def invalidate(self, model: Optional[str] = None):
        """
        使缓存失效
        
        Args:
            model: 指定模型，None则清除所有
        """
        if model is None:
            self._cache.clear()
        else:
            keys_to_remove = [
                k for k in self._cache.keys()
                if self._cache[k].response.model == model
            ]
            for k in keys_to_remove:
                del self._cache[k]
    
    def clear_expired(self):
        """清除过期条目"""
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items()
            if now - v.timestamp >= self.ttl
        ]
        for k in expired_keys:
            del self._cache[k]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl,
        }


class CachingClient:
    """
    带缓存的客户端包装器
    
    自动缓存响应，对相同请求直接返回缓存结果
    """
    
    def __init__(self, client, cache: Optional[ResponseCache] = None):
        """
        初始化
        
        Args:
            client: LLMClient实例
            cache: 缓存实例，None则创建默认缓存
        """
        self.client = client
        self.cache = cache or ResponseCache()
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """
        带缓存的对话
        
        如果缓存命中，直接返回缓存结果；否则调用客户端并缓存响应
        """
        model = kwargs.get('model', self.client.config.default_model)
        temperature = kwargs.get('temperature', 0.7)
        stream = kwargs.get('stream', False)
        
        # 流式请求不缓存
        if stream:
            return await self.client.chat(messages, **kwargs)
        
        # 检查缓存
        cached = self.cache.get(messages, model, temperature)
        if cached is not None:
            return cached
        
        # 调用客户端
        response = await self.client.chat(messages, **kwargs)
        
        # 缓存响应
        self.cache.set(messages, model, response, temperature)
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "client_stats": self.client.get_stats(),
            "cache_stats": self.cache.get_stats(),
        }
