# crabswarm/llm/config.py
"""
LLM配置模块
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml


class ModelProvider(Enum):
    """LLM提供商"""
    SILICONFLOW = "siliconflow"
    OPENROUTER = "openrouter"
    KIMI = "kimi"


class ModelTier(Enum):
    """模型层级"""
    FAST = "fast"           # 快速响应 (7B-14B)
    BALANCED = "balanced"   # 平衡 (32B)
    POWERFUL = "powerful"   # 强力 (72B+)
    REASONING = "reasoning" # 推理型 (R1)


@dataclass
class ModelInfo:
    """模型信息"""
    id: str
    name: str
    tier: ModelTier
    provider: ModelProvider
    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0
    max_tokens: int = 8192
    supports_streaming: bool = True
    supports_tools: bool = True


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: ModelProvider
    api_key: str
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    
    def __post_init__(self):
        if self.base_url is None:
            self.base_url = self._get_default_base_url()
        if self.default_model is None:
            self.default_model = self._get_default_model()
    
    def _get_default_base_url(self) -> str:
        """获取默认base URL"""
        urls = {
            ModelProvider.SILICONFLOW: "https://api.siliconflow.cn/v1",
            ModelProvider.OPENROUTER: "https://openrouter.ai/api/v1",
            ModelProvider.KIMI: "https://api.moonshot.cn/v1",
        }
        return urls.get(self.provider, urls[ModelProvider.SILICONFLOW])
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        defaults = {
            ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-V3",
            ModelProvider.OPENROUTER: "deepseek/deepseek-chat",
            ModelProvider.KIMI: "moonshot-v1-8k",
        }
        return defaults.get(self.provider, defaults[ModelProvider.SILICONFLOW])


# 模型映射表
MODEL_MAPPING: Dict[str, Dict[ModelProvider, str]] = {
    # DeepSeek系列
    "deepseek-v3": {
        ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-V3",
        ModelProvider.OPENROUTER: "deepseek/deepseek-chat",
    },
    "deepseek-r1": {
        ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-R1",
        ModelProvider.OPENROUTER: "deepseek/deepseek-r1",
    },
    # DeepSeek蒸馏模型
    "deepseek-r1-distill-qwen-7b": {
        ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        ModelProvider.OPENROUTER: "deepseek/deepseek-r1-distill-qwen-7b",
    },
    "deepseek-r1-distill-qwen-14b": {
        ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        ModelProvider.OPENROUTER: "deepseek/deepseek-r1-distill-qwen-14b",
    },
    "deepseek-r1-distill-qwen-32b": {
        ModelProvider.SILICONFLOW: "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        ModelProvider.OPENROUTER: "deepseek/deepseek-r1-distill-qwen-32b",
    },
    # Qwen2.5系列
    "qwen2.5-7b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-7B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-7b-instruct",
    },
    "qwen2.5-14b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-14B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-14b-instruct",
    },
    "qwen2.5-32b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-32B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-32b-instruct",
    },
    "qwen2.5-72b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-72B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-72b-instruct",
    },
    # Qwen2.5代码模型
    "qwen2.5-coder-7b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-Coder-7B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-coder-7b-instruct",
    },
    "qwen2.5-coder-32b": {
        ModelProvider.SILICONFLOW: "Qwen/Qwen2.5-Coder-32B-Instruct",
        ModelProvider.OPENROUTER: "qwen/qwen-2.5-coder-32b-instruct",
    },
}


# 模型价格 (元/1M tokens)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "deepseek-ai/DeepSeek-V3": {"input": 2.0, "output": 8.0},
    "deepseek-ai/DeepSeek-R1": {"input": 4.0, "output": 16.0},
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": {"input": 0.0, "output": 0.0},  # 免费
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B": {"input": 0.5, "output": 1.0},
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": {"input": 1.0, "output": 3.0},
    "Qwen/Qwen2.5-7B-Instruct": {"input": 0.5, "output": 0.5},
    "Qwen/Qwen2.5-14B-Instruct": {"input": 1.0, "output": 1.0},
    "Qwen/Qwen2.5-32B-Instruct": {"input": 2.0, "output": 2.0},
    "Qwen/Qwen2.5-72B-Instruct": {"input": 4.0, "output": 4.0},
    "Qwen/Qwen2.5-Coder-7B-Instruct": {"input": 0.5, "output": 0.5},
    "Qwen/Qwen2.5-Coder-32B-Instruct": {"input": 2.0, "output": 2.0},
}


# 层级到模型的默认映射
TIER_MODEL_MAPPING: Dict[ModelTier, str] = {
    ModelTier.FAST: "qwen2.5-14b",
    ModelTier.BALANCED: "qwen2.5-32b",
    ModelTier.POWERFUL: "deepseek-v3",
    ModelTier.REASONING: "deepseek-r1",
}


def resolve_model(model_key: str, provider: ModelProvider) -> str:
    """解析模型名称到提供商特定ID"""
    if model_key in MODEL_MAPPING:
        mapping = MODEL_MAPPING[model_key]
        return mapping.get(provider, mapping[ModelProvider.SILICONFLOW])
    # 如果不是预定义的key，直接当作模型ID使用
    return model_key


def get_model_price(model_id: str) -> Dict[str, float]:
    """获取模型价格"""
    return MODEL_PRICING.get(model_id, {"input": 0.0, "output": 0.0})


def load_config_from_env() -> LLMConfig:
    """从环境变量加载配置"""
    provider_str = os.getenv("LLM_PROVIDER", "siliconflow").lower()
    provider = ModelProvider(provider_str)
    
    api_keys = {
        ModelProvider.SILICONFLOW: os.getenv("SILICONFLOW_API_KEY", ""),
        ModelProvider.OPENROUTER: os.getenv("OPENROUTER_API_KEY", ""),
        ModelProvider.KIMI: os.getenv("KIMI_API_KEY", ""),
    }
    
    api_key = api_keys.get(provider, "")
    if not api_key:
        raise ValueError(f"Missing API key for provider: {provider.value}")
    
    base_urls = {
        ModelProvider.SILICONFLOW: os.getenv("SILICONFLOW_BASE_URL"),
        ModelProvider.OPENROUTER: os.getenv("OPENROUTER_BASE_URL"),
        ModelProvider.KIMI: os.getenv("KIMI_BASE_URL"),
    }
    
    return LLMConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_urls.get(provider),
        default_model=os.getenv("DEFAULT_MODEL"),
        timeout=int(os.getenv("LLM_TIMEOUT", "60")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
    )


def load_config(config_path: Optional[str] = None) -> LLMConfig:
    """加载配置"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        # TODO: 从YAML解析完整配置
        return load_config_from_env()
    
    return load_config_from_env()
