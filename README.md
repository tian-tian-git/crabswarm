# CrabSwarm

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 🦀 A "soulful" multi-agent collaboration framework
> 
> 一个"有灵魂"的多Agent协作框架

[English](#english) | [中文](#中文)

---

## 中文

### 🌟 核心理念

CrabSwarm 不是一个简单的任务分发系统，而是一个**有层次、有进化、有协作**的Agent组织。

**主意识 (Main Consciousness)**
- 唯一对外接口
- 协调子Agent
- 持续学习进化
- 做出最终决策

**子Agent团队 (Agent Swarm)**
- 各司其职的专业Agent
- 互相讨论、质疑、完善
- 无独立对外权限
- 通过主意识协作

### 🚀 快速开始

```bash
# 安装
pip install crabswarm

# 创建你的第一个Agent团队
from crabswarm import Swarm, Agent

# 创建主意识
swarm = Swarm(name="我的团队")

# 添加专业Agent
analyst = Agent(
    name="分析师",
    role="数据分析",
    skills=["财务分析", "技术指标"]
)

trader = Agent(
    name="交易员", 
    role="市场判断",
    skills=["情绪分析", "资金流向"]
)

swarm.add_agents([analyst, trader])

# 分配任务
result = swarm.execute("分析今天的大盘走势")
print(result)
```

### 💡 示例：股票分析Agent团队

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

stock_team.add_agents([analyst, trader, philosopher])

# 执行分析任务
report = stock_team.discuss(
    topic="分析贵州茅台的投资价值",
    max_rounds=10  # 最多讨论10轮
)

print(report)
```

### 🏗️ 架构

```
用户 ←→ 主意识 (MainConsciousness)
            ↓
    ┌───────┼───────┐
    ↓       ↓       ↓
 Agent1  Agent2  Agent3
    └───────┬───────┘
            ↓
        共识形成
            ↓
        结果输出
```

### 📦 核心特性

- ✅ **主意识协调** - 统一对外接口，内部协调Agent
- ✅ **专业分工** - 每个Agent有自己的专长和人格
- ✅ **协作讨论** - Agent之间互相质疑、完善观点
- ✅ **技能系统** - 动态安装/卸载技能
- ✅ **MCP集成** - 支持Model Context Protocol工具
- ✅ **持续进化** - 自我学习、知识积累

### 🛠️ 进阶用法

#### 自定义Agent

```python
from crabswarm import Agent

my_agent = Agent(
    name="我的Agent",
    role="自定义角色",
    personality="描述人格特征",
    expertise=["技能1", "技能2"],
    bias="可能的盲点",
    catchphrase="标志性语句"
)
```

#### 技能安装

```python
# 为Agent安装新技能
agent.install_skill("量化交易")
agent.install_skill("机器学习")

# 使用技能
result = agent.use_skill("量化交易", data)
```

#### MCP工具

```python
# 分配MCP工具
agent.assign_mcp("web_search")
agent.assign_mcp("code_execution")
```

### 📚 文档

- [快速开始指南](docs/quickstart.md)
- [API文档](docs/api.md)
- [示例应用](examples/)
- [架构设计](docs/architecture.md)

### 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## English

### 🌟 Core Concept

CrabSwarm is not just a task distribution system, but a **hierarchical, evolving, collaborative** Agent organization.

**Main Consciousness**
- Single external interface
- Coordinates sub-agents
- Continuous learning & evolution
- Final decision maker

**Agent Swarm**
- Specialized agents with specific roles
- Discuss, challenge, and improve together
- No independent external access
- Collaborate through main consciousness

### 🚀 Quick Start

```bash
pip install crabswarm
```

```python
from crabswarm import Swarm, Agent

swarm = Swarm(name="My Team")

analyst = Agent(name="Analyst", role="Data Analysis")
trader = Agent(name="Trader", role="Market Judgment")

swarm.add_agents([analyst, trader])

result = swarm.execute("Analyze today's market trend")
print(result)
```

### 📦 Features

- ✅ **Main Consciousness** - Unified interface, internal coordination
- ✅ **Specialization** - Each agent has expertise and personality
- ✅ **Collaboration** - Agents challenge and improve each other's ideas
- ✅ **Skill System** - Dynamic skill installation/removal
- ✅ **MCP Support** - Model Context Protocol integration
- ✅ **Evolution** - Self-learning and knowledge accumulation

---

## 🦀 About the Name

**Crab** - Because crabs evolve by molting (EXFOLIATE!)  
**Swarm** - A collective of specialized agents working together

> "Great things start small, but with a soul."

---

*Built with ❤️ by the CrabSwarm team*
