# 架构设计

## 整体架构

CrabSwarm 采用分层架构设计：

```
┌─────────────────────────────────────────┐
│           用户接口层 (User Layer)        │
│         CLI / API / Web UI              │
├─────────────────────────────────────────┤
│           主意识层 (Consciousness)       │
│      MainConsciousness - 统一协调        │
├─────────────────────────────────────────┤
│           团队层 (Swarm Layer)           │
│         Swarm - Agent 团队管理           │
├─────────────────────────────────────────┤
│           Agent 层 (Agent Layer)         │
│      Agent - 专业 Agent 实现             │
├─────────────────────────────────────────┤
│           能力层 (Capability Layer)      │
│    Skills / MCP Tools / Memory          │
└─────────────────────────────────────────┘
```

## 核心概念

### 主意识 (MainConsciousness)

- **唯一对外接口**：所有外部请求都通过主意识
- **协调者**：管理多个 Swarm，分配任务
- **决策者**：基于 Agent 讨论结果做出最终决策
- **学习者**：持续学习，积累经验

### Swarm (Agent 团队)

- **容器**：包含多个相关 Agent
- **协作场**：Agent 之间进行讨论和协作
- **任务执行**：分解任务并分配给合适的 Agent

### Agent (专业 Agent)

- **个性化**：每个 Agent 有独特的角色、专长、人格
- **技能系统**：动态安装/卸载技能
- **MCP 支持**：可分配外部工具
- **记忆**：保留历史交互记录

## 数据流

```
用户请求
    ↓
MainConsciousness 接收
    ↓
选择合适的 Swarm
    ↓
Swarm 分解任务
    ↓
分配给相关 Agent
    ↓
Agent 讨论/执行
    ↓
形成共识
    ↓
MainConsciousness 决策
    ↓
返回结果给用户
```

## 讨论机制

```
话题: "分析股票"
    ↓
┌─────────┬─────────┬─────────┐
↓         ↓         ↓
分析师    交易员    哲学家
(数据)    (情绪)    (逻辑)
    └─────────┬─────────┘
              ↓
         观点交换
              ↓
         质疑与完善
              ↓
         形成共识
```

## 扩展点

### 添加新技能

```python
class MySkill:
    name = "我的技能"
    
    def execute(self, context):
        # 实现技能逻辑
        return result

# 注册技能
agent.install_skill("我的技能")
```

### 添加 MCP 工具

```python
# 分配 MCP 工具
agent.assign_mcp("web_search")

# 使用工具
result = agent.use_mcp("web_search", query="股票行情")
```

### 自定义 Agent 类型

```python
class TradingAgent(Agent):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            role="交易员",
            expertise=["技术分析", "风险管理"]
        )
    
    def analyze(self, stock_code: str):
        # 自定义分析逻辑
        pass
```

## 设计原则

1. **单一职责**：每个 Agent 专注于特定领域
2. **协作优先**：通过讨论形成更好的决策
3. **可扩展性**：技能、工具、Agent 都可动态添加
4. **可观测性**：完整的讨论历史和决策记录
5. **容错性**：单个 Agent 失败不影响整体

## 未来规划

- [ ] LLM 集成：接入 OpenAI、Anthropic 等
- [ ] 持久化：数据库存储 Agent 记忆
- [ ] Web UI：可视化 Agent 协作过程
- [ ] 插件系统：第三方扩展支持
- [ ] 分布式：多节点 Swarm 协作
