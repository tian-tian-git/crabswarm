# CrabSwarm API 文档

## 核心类

### Swarm

Agent 团队的管理类。

```python
from crabswarm import Swarm

swarm = Swarm(name="我的团队")
```

#### 方法

##### `add_agent(agent: Agent) -> bool`
添加单个 Agent 到团队。

```python
from crabswarm import Agent

agent = Agent(name="分析师", role="数据分析")
swarm.add_agent(agent)
```

##### `add_agents(agents: List[Agent]) -> bool`
批量添加 Agent。

```python
analyst = Agent(name="分析师", role="数据分析")
trader = Agent(name="交易员", role="市场判断")
swarm.add_agents([analyst, trader])
```

##### `remove_agent(agent_id: str) -> bool`
从团队中移除 Agent。

##### `get_agent(agent_id: str) -> Optional[Agent]`
获取指定 ID 的 Agent。

##### `list_agents() -> List[Dict]`
列出团队中所有 Agent 的信息。

```python
agents = swarm.list_agents()
for agent in agents:
    print(f"{agent['name']}: {agent['role']}")
```

##### `discuss(topic: str, max_rounds: int = 10) -> Dict`
让团队中的 Agent 就某个主题进行讨论。

```python
result = swarm.discuss(
    topic="分析贵州茅台的投资价值",
    max_rounds=5
)
print(result['consensus'])
```

**返回值：**
- `topic`: 讨论主题
- `max_rounds`: 最大讨论轮数
- `rounds`: 每轮讨论详情
- `consensus`: 形成的共识
- `status`: 讨论状态

##### `execute(task: str) -> Dict`
执行任务，自动分解并分配给合适的 Agent。

```python
result = swarm.execute("分析今天的大盘走势")
```

---

### Agent

专业 Agent 类，每个 Agent 有自己的专长和人格。

```python
from crabswarm import Agent

agent = Agent(
    name="分析师",
    role="数据分析",
    personality="理性、严谨",
    expertise=["财务分析", "技术指标"],
    bias="过度依赖历史数据",
    catchphrase="数据不会撒谎"
)
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | str | ✅ | Agent 名称 |
| `role` | str | ✅ | Agent 角色 |
| `personality` | str | ❌ | 人格特征描述 |
| `expertise` | List[str] | ❌ | 专长列表 |
| `bias` | str | ❌ | 可能的盲点 |
| `catchphrase` | str | ❌ | 标志性语句 |

#### 方法

##### `install_skill(skill_name: str) -> bool`
为 Agent 安装技能。

```python
agent.install_skill("财务建模")
agent.install_skill("Python数据分析")
```

##### `uninstall_skill(skill_name: str) -> bool`
卸载 Agent 的技能。

##### `assign_mcp(tool_name: str) -> bool`
为 Agent 分配 MCP 工具。

```python
agent.assign_mcp("web_search")
agent.assign_mcp("code_execution")
```

##### `think(topic: str) -> str`
让 Agent 就某个主题进行思考。

```python
thought = agent.think("分析市场趋势")
print(thought)
```

##### `to_dict() -> Dict`
将 Agent 信息转换为字典。

---

### MainConsciousness

主意识类，协调多个 Swarm。

```python
from crabswarm import MainConsciousness

consciousness = MainConsciousness(name="蟹爪主意识")
```

#### 方法

##### `create_swarm(name: str) -> Swarm`
创建新的 Swarm。

```python
swarm = consciousness.create_swarm(name="股票分析团队")
```

##### `get_swarm(swarm_id: str) -> Optional[Swarm]`
获取指定 ID 的 Swarm。

##### `list_swarms() -> List[Dict]`
列出所有 Swarm。

```python
swarms = consciousness.list_swarms()
for swarm in swarms:
    print(f"{swarm['name']}: {swarm['agent_count']} 个 Agent")
```

##### `reflect() -> str`
主意识进行自我反思。

```python
reflection = consciousness.reflect()
print(reflection)
```

##### `make_decision(context: Dict) -> Dict`
基于上下文做出决策。

```python
decision = consciousness.make_decision({
    "task": "是否执行交易",
    "risk_level": "medium"
})
```

---

## 完整示例

```python
from crabswarm import Swarm, Agent, MainConsciousness

# 创建主意识
consciousness = MainConsciousness()

# 创建 Swarm
swarm = consciousness.create_swarm(name="投资分析团队")

# 创建 Agent
analyst = Agent(
    name="分析师",
    role="数据分析",
    personality="理性、严谨",
    expertise=["财务分析", "技术指标"],
    catchphrase="数据不会撒谎"
)

trader = Agent(
    name="交易员",
    role="实盘交易",
    personality="果断、敏锐",
    expertise=["市场情绪", "资金流向"],
    catchphrase="市场总是对的"
)

# 添加 Agent
swarm.add_agents([analyst, trader])

# 安装技能
analyst.install_skill("财务建模")
trader.install_skill("情绪分析")

# 执行讨论
result = swarm.discuss("分析贵州茅台的投资价值", max_rounds=5)
print(result['consensus'])

# 查看所有 Swarm
print(consciousness.list_swarms())
```

---

## 类型注解

```python
from typing import Dict, List, Optional
from crabswarm import Swarm, Agent

# 函数参数类型
def create_team(name: str) -> Swarm:
    return Swarm(name=name)

# 返回值类型
def get_expert_agents(swarm: Swarm) -> List[Agent]:
    return [
        agent for agent in swarm.agents.values()
        if "专家" in agent.role
    ]
```
