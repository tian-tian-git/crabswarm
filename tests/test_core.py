"""
CrabSwarm 测试套件
"""

import pytest
from crabswarm import Swarm, Agent, MainConsciousness


class TestAgent:
    """Agent类测试"""

    def test_agent_creation(self):
        """测试Agent创建"""
        agent = Agent(
            name="测试Agent",
            role="测试员",
            personality="严谨",
            expertise=["测试", "QA"],
        )
        assert agent.name == "测试Agent"
        assert agent.role == "测试员"
        assert agent.personality == "严谨"
        assert "测试" in agent.expertise
        assert len(agent.id) == 8

    def test_agent_default_values(self):
        """测试Agent默认值"""
        agent = Agent(name="简单Agent", role="通用")
        assert agent.personality == "专业、高效"
        assert agent.expertise == ["通用"]
        assert agent.catchphrase == "Ready to work"

    def test_agent_skills(self):
        """测试Agent技能管理"""
        agent = Agent(name="技能Agent", role="开发")

        # 安装技能
        assert agent.install_skill("Python") is True
        assert "Python" in agent.skills

        # 重复安装
        assert agent.install_skill("Python") is False

        # 卸载技能
        assert agent.uninstall_skill("Python") is True
        assert "Python" not in agent.skills

        # 卸载不存在的技能
        assert agent.uninstall_skill("Java") is False

    def test_agent_mcp_tools(self):
        """测试Agent MCP工具管理"""
        agent = Agent(name="MCPAgent", role="工具使用者")

        assert agent.assign_mcp("search") is True
        assert "search" in agent.mcp_tools

        # 重复分配
        assert agent.assign_mcp("search") is False

    def test_agent_think(self):
        """测试Agent思考功能"""
        agent = Agent(
            name="思考Agent", role="分析师", expertise=["数据分析", "机器学习"]
        )
        thought = agent.think("如何提高性能")
        assert isinstance(thought, str)
        assert len(thought) > 0

    def test_agent_to_dict(self):
        """测试Agent序列化"""
        agent = Agent(name="DictAgent", role="序列化")
        data = agent.to_dict()

        assert "id" in data
        assert "name" in data
        assert data["name"] == "DictAgent"
        assert "role" in data
        assert "expertise" in data


class TestSwarm:
    """Swarm类测试"""

    def test_swarm_creation(self):
        """测试Swarm创建"""
        swarm = Swarm(name="测试团队")
        assert swarm.name == "测试团队"
        assert len(swarm.id) == 8
        assert len(swarm.agents) == 0

    def test_swarm_add_agent(self):
        """测试添加Agent"""
        swarm = Swarm(name="测试团队")
        agent = Agent(name="成员1", role="开发")

        assert swarm.add_agent(agent) is True
        assert agent.id in swarm.agents
        assert len(swarm.agents) == 1

    def test_swarm_add_agents(self):
        """测试批量添加Agent"""
        swarm = Swarm(name="测试团队")
        agents = [
            Agent(name="成员1", role="开发"),
            Agent(name="成员2", role="测试"),
        ]

        assert swarm.add_agents(agents) is True
        assert len(swarm.agents) == 2

    def test_swarm_remove_agent(self):
        """测试移除Agent"""
        swarm = Swarm(name="测试团队")
        agent = Agent(name="成员1", role="开发")
        swarm.add_agent(agent)

        assert swarm.remove_agent(agent.id) is True
        assert len(swarm.agents) == 0

        # 移除不存在的Agent
        assert swarm.remove_agent("nonexistent") is False

    def test_swarm_get_agent(self):
        """测试获取Agent"""
        swarm = Swarm(name="测试团队")
        agent = Agent(name="成员1", role="开发")
        swarm.add_agent(agent)

        found = swarm.get_agent(agent.id)
        assert found is not None
        assert found.name == "成员1"

        # 获取不存在的Agent
        assert swarm.get_agent("nonexistent") is None

    def test_swarm_list_agents(self):
        """测试列出所有Agent"""
        swarm = Swarm(name="测试团队")
        swarm.add_agent(Agent(name="成员1", role="开发"))
        swarm.add_agent(Agent(name="成员2", role="测试"))

        agents = swarm.list_agents()
        assert len(agents) == 2
        assert all("id" in a for a in agents)
        assert all("name" in a for a in agents)

    def test_swarm_discuss(self):
        """测试讨论功能"""
        swarm = Swarm(name="讨论团队")
        swarm.add_agent(Agent(name="分析师", role="分析"))
        swarm.add_agent(Agent(name="工程师", role="开发"))

        result = swarm.discuss("如何提高代码质量", max_rounds=3)

        assert result["topic"] == "如何提高代码质量"
        assert result["status"] == "completed"
        assert len(result["rounds"]) <= 3
        assert "consensus" in result

    def test_swarm_execute(self):
        """测试任务执行"""
        swarm = Swarm(name="执行团队")
        swarm.add_agent(Agent(name="执行者", role="开发"))

        result = swarm.execute("实现新功能")

        assert result["task"] == "实现新功能"
        assert "subtasks" in result
        assert "results" in result
        assert result["status"] == "completed"

    def test_swarm_to_dict(self):
        """测试Swarm序列化"""
        swarm = Swarm(name="序列化团队")
        swarm.add_agent(Agent(name="成员1", role="开发"))

        data = swarm.to_dict()

        assert "id" in data
        assert data["name"] == "序列化团队"
        assert "agents" in data
        assert "created_at" in data


class TestMainConsciousness:
    """MainConsciousness类测试"""

    def test_consciousness_creation(self):
        """测试主意识创建"""
        consciousness = MainConsciousness()
        assert consciousness.name == "蟹爪主意识"
        assert consciousness.awareness_level == 1
        assert consciousness.emotional_state == "curious"
        assert 0 <= consciousness.confidence <= 1

    def test_consciousness_custom_values(self):
        """测试自定义主意识属性"""
        consciousness = MainConsciousness(
            name="自定义意识",
            awareness_level=5,
            emotional_state="focused",
            confidence=0.9,
        )
        assert consciousness.name == "自定义意识"
        assert consciousness.awareness_level == 5
        assert consciousness.emotional_state == "focused"
        assert consciousness.confidence == 0.9

    def test_create_swarm(self):
        """测试创建Swarm"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="新团队")

        assert swarm.name == "新团队"
        assert swarm.id in consciousness.swarms

    def test_get_swarm(self):
        """测试获取Swarm"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="测试团队")

        found = consciousness.get_swarm(swarm.id)
        assert found is not None
        assert found.name == "测试团队"

        # 获取不存在的Swarm
        assert consciousness.get_swarm("nonexistent") is None

    def test_list_swarms(self):
        """测试列出所有Swarm"""
        consciousness = MainConsciousness()
        consciousness.create_swarm(name="团队1")
        consciousness.create_swarm(name="团队2")

        swarms = consciousness.list_swarms()
        assert len(swarms) == 2
        assert all("id" in s for s in swarms)
        assert all("name" in s for s in swarms)
        assert all("agent_count" in s for s in swarms)

    def test_reflect(self):
        """测试自我反思"""
        consciousness = MainConsciousness()
        reflection = consciousness.reflect()

        assert isinstance(reflection, str)
        assert len(reflection) > 0

    def test_make_decision(self):
        """测试决策功能"""
        consciousness = MainConsciousness()
        decision = consciousness.make_decision({"task": "测试任务"})

        assert "decision" in decision
        assert "confidence" in decision
        assert "reasoning" in decision
        assert "timestamp" in decision
