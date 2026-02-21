# 快速开始指南

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install crabswarm
```

### 从源码安装

```bash
git clone https://github.com/yourusername/crabswarm.git
cd crabswarm
pip install -e .
```

### 开发安装

```bash
git clone https://github.com/yourusername/crabswarm.git
cd crabswarm
pip install -e ".[dev]"
```

## 最小示例

创建一个最简单的 Agent 团队：

```python
from crabswarm import Swarm, Agent

# 创建团队
swarm = Swarm(name="我的第一个团队")

# 创建 Agent
agent = Agent(
    name="助手",
    role="通用助手",
    personality="友好、乐于助人"
)

# 添加 Agent
swarm.add_agent(agent)

# 查看团队成员
print(swarm.list_agents())
```

## 股票分析示例

一个更完整的示例，创建专业的股票分析团队：

```python
from crabswarm import Swarm, Agent

# 创建股票分析团队
stock_team = Swarm(name="股票分析团队")

# 分析师 - 负责数据处理
analyst = Agent(
    name="分析师",
    personality="理性、严谨",
    expertise=["财务分析", "技术指标", "数据挖掘"],
    catchphrase="数据不会撒谎"
)

# 交易员 - 负责市场判断
trader = Agent(
    name="交易员",
    personality="果断、敏锐",
    expertise=["市场情绪", "资金流向", "盘口语言"],
    catchphrase="市场总是对的"
)

# 哲学家 - 负责深度思考
philosopher = Agent(
    name="哲学家",
    personality="深度思考、质疑一切",
    expertise=["行为金融", "认知偏差", "系统思维"],
    catchphrase="为什么？还有更深层的为什么？"
)

# 添加 Agent 到团队
stock_team.add_agents([analyst, trader, philosopher])

# 安装技能
analyst.install_skill("财务建模")
analyst.install_skill("Python数据分析")
trader.install_skill("情绪分析")
philosopher.install_skill("逻辑推理")

# 执行讨论
result = stock_team.discuss(
    topic="分析贵州茅台的投资价值",
    max_rounds=5
)

print(f"讨论共识: {result['consensus']}")
```

运行示例：

```bash
python examples/stock_analysis_team.py
```

## 下一步

- 查看 [API 文档](api.md) 了解所有功能
- 阅读 [架构设计](architecture.md) 深入理解原理
- 参考更多 [示例](../examples/)
