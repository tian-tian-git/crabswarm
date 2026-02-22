# CrabSwarm LLM 集成文档

> 将LLM能力集成到CrabSwarm多智能体框架

## 概述

CrabSwarm LLM模块提供统一的接口调用不同LLM提供商的API，支持多模型路由和成本优化。

## 功能特性

- ✅ **多提供商支持** - SiliconFlow、OpenRouter、Kimi
- ✅ **模型路由** - 根据任务特征自动选择最合适的模型
- ✅ **成本追踪** - 实时监控token使用和成本
- ✅ **增强型Agent** - LLMAgent支持对话历史和思考能力
- ✅ **流式输出** - 支持流式响应
- ✅ **工具调用** - 支持Function Calling

## 快速开始

### 基础使用

```python
from crabswarm.llm import LLMClient, LLMConfig, ModelProvider

# 创建配置
config = LLMConfig(
    provider=ModelProvider.SILICONFLOW,
    api_key="your-api-key"
)

# 创建客户端
client = LLMClient(config)

# 简单对话
response = await client.chat([
    ChatMessage(role="user", content="Hello")
])
print(response.content)
```

### 使用LLMAgent

```python
from crabswarm.llm import LLMAgent

# 创建LLM增强型Agent
agent = LLMAgent(
    name="分析师",
    role="数据分析师",
    llm_client=client,
    model="deepseek-v3"
)

# 思考分析
result = await agent.think("分析市场趋势")
print(result)

# 多轮对话
response = await agent.chat("请详细说明")
print(response)
```

### 模型路由

```python
from crabswarm.llm import ModelRouter

# 创建路由器
router = ModelRouter(client)

# 自动选择模型
response = await router.chat_with_routing([
    ChatMessage(role="user", content="写一个Python函数")
])
# 自动选择 deepseek-v3 (代码任务)
```

## 支持的模型

### DeepSeek系列
- `deepseek-v3` - 通用对话
- `deepseek-r1` - 推理型
- `deepseek-r1-distill-qwen-7b/14b/32b` - 蒸馏模型

### Qwen2.5系列
- `qwen2.5-7b/14b/32b/72b` - 通用对话
- `qwen2.5-coder-7b/32b` - 代码专用

### 模型层级
- `FAST` - 快速响应 (14B)
- `BALANCED` - 平衡 (32B)
- `POWERFUL` - 强力 (DeepSeek-V3)
- `REASONING` - 推理型 (DeepSeek-R1)

## 配置

### 环境变量

```bash
# 必需
export SILICONFLOW_API_KEY="sk-xxx"

# 可选
export LLM_PROVIDER="siliconflow"  # 或 openrouter, kimi
export DEFAULT_MODEL="deepseek-v3"
export LLM_TIMEOUT="60"
export LLM_MAX_RETRIES="3"
```

### YAML配置

```yaml
# config/llm.yaml
provider: siliconflow
api_key: ${SILICONFLOW_API_KEY}
default_model: deepseek-v3
timeout: 60
max_retries: 3
```

## API参考

### LLMClient

```python
class LLMClient:
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
    ) -> ChatResponse
    
    async def chat_stream(...) -> AsyncIterator[str]
    
    def simple_chat(self, prompt: str, **kwargs) -> str
```

### LLMAgent

```python
class LLMAgent(Agent):
    async def think(self, topic: str) -> str
    async def chat(self, message: str, stream: bool = False) -> str
    async def analyze(self, data: str, task: str = "分析") -> str
    async def summarize(self, text: str, max_length: int = 200) -> str
    def clear_history(self)
    def get_stats(self) -> Dict[str, Any]
```

### ModelRouter

```python
class ModelRouter:
    def add_rule(self, rule: RoutingRule)
    def route(self, prompt: str) -> str
    async def chat_with_routing(...) -> ChatResponse
```

## 成本优化

```python
from crabswarm.llm import CostTracker

# 创建成本追踪器
tracker = CostTracker(
    daily_budget_usd=10.0,
    alert_threshold=0.8,
    on_alert=lambda alert: print(f"警告: {alert.message}")
)

# 查看预算状态
status = tracker.get_budget_status()
print(f"今日使用: ${status['current_cost']:.2f}")
```

## 错误处理

```python
from crabswarm.llm.exceptions import (
    RateLimitError,
    TokenLimitError,
    AuthenticationError,
    ProviderError
)

try:
    response = await client.chat(messages)
except RateLimitError as e:
    print(f"限流，请等待 {e.retry_after} 秒")
except TokenLimitError as e:
    print(f"Token超限")
except AuthenticationError as e:
    print(f"认证失败: {e.provider}")
```

## 测试

```bash
# 运行所有测试
pytest tests/test_llm.py -v

# 运行特定测试
pytest tests/test_llm.py::TestLLMConfig -v
```

## 文件结构

```
crabswarm/llm/
├── __init__.py          # 模块入口
├── config.py            # 配置和模型映射
├── client.py            # LLM客户端
├── agent.py             # LLM增强型Agent
├── router.py            # 模型路由
├── cost.py              # 成本追踪
├── exceptions.py        # 异常定义
└── adapters/            # 提供商适配器
    ├── __init__.py
    ├── base.py          # 适配器基类
    ├── siliconflow.py   # SiliconFlow适配器
    └── openrouter.py    # OpenRouter适配器
```

## 许可证

MIT License
