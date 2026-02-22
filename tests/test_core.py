"""
CrabSwarm 测试套件 - 扩展版
包含单元测试、集成测试和边缘情况测试
"""

import pytest
from crabswarm import Swarm, Agent, MainConsciousness


class TestAgent:
    """Agent类单元测试"""

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

    def test_agent_think_without_expertise(self):
        """测试无专长Agent的思考"""
        agent = Agent(name="新手Agent", role="实习生", expertise=[])
        thought = agent.think("如何开始")
        assert isinstance(thought, str)
        assert "更多信息" in thought or "需要" in thought

    def test_agent_to_dict(self):
        """测试Agent序列化"""
        agent = Agent(name="DictAgent", role="序列化")
        data = agent.to_dict()

        assert "id" in data
        assert "name" in data
        assert data["name"] == "DictAgent"
        assert "role" in data
        assert "expertise" in data
        assert "skills" in data
        assert "mcp_tools" in data

    def test_agent_memory(self):
        """测试Agent记忆功能"""
        agent = Agent(name="记忆Agent", role="学习者")
        assert isinstance(agent.memory, list)
        assert len(agent.memory) == 0

    def test_agent_multiple_skills(self):
        """测试Agent多技能管理"""
        agent = Agent(name="全栈Agent", role="开发")
        
        skills = ["Python", "JavaScript", "Docker", "Kubernetes"]
        for skill in skills:
            assert agent.install_skill(skill) is True
        
        assert len(agent.skills) == 4
        for skill in skills:
            assert skill in agent.skills

    def test_agent_multiple_mcp_tools(self):
        """测试Agent多MCP工具管理"""
        agent = Agent(name="工具Agent", role="集成")
        
        tools = ["search", "calculator", "translator", "code_runner"]
        for tool in tools:
            assert agent.assign_mcp(tool) is True
        
        assert len(agent.mcp_tools) == 4


class TestSwarm:
    """Swarm类单元测试"""

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

    def test_swarm_discuss_max_rounds_limit(self):
        """测试讨论轮数上限"""
        swarm = Swarm(name="讨论团队")
        swarm.add_agent(Agent(name="分析师", role="分析"))

        # 请求超过10轮，应该被限制
        result = swarm.discuss("测试话题", max_rounds=20)
        assert len(result["rounds"]) <= 10

    def test_swarm_discuss_empty_swarm(self):
        """测试空Swarm讨论"""
        swarm = Swarm(name="空团队")
        result = swarm.discuss("测试话题", max_rounds=3)
        
        assert result["topic"] == "测试话题"
        assert result["status"] == "completed"
        # 空团队应该没有讨论轮次
        assert len(result["rounds"]) == 0 or all(len(r["thoughts"]) == 0 for r in result["rounds"])

    def test_swarm_execute(self):
        """测试任务执行"""
        swarm = Swarm(name="执行团队")
        swarm.add_agent(Agent(name="执行者", role="开发"))

        result = swarm.execute("实现新功能")

        assert result["task"] == "实现新功能"
        assert "subtasks" in result
        assert "results" in result
        assert result["status"] == "completed"

    def test_swarm_execute_empty_swarm(self):
        """测试空Swarm执行任务"""
        swarm = Swarm(name="空团队")
        result = swarm.execute("测试任务")
        
        assert result["task"] == "测试任务"
        assert result["status"] == "completed"
        # 空团队应该无法分配任务
        assert len(result["results"]) == 0 or all(r["agent"] is None for r in result["results"])

    def test_swarm_to_dict(self):
        """测试Swarm序列化"""
        swarm = Swarm(name="序列化团队")
        swarm.add_agent(Agent(name="成员1", role="开发"))

        data = swarm.to_dict()

        assert "id" in data
        assert data["name"] == "序列化团队"
        assert "agents" in data
        assert "created_at" in data

    def test_swarm_discussion_history(self):
        """测试讨论历史记录"""
        swarm = Swarm(name="历史团队")
        swarm.add_agent(Agent(name="成员", role="讨论"))
        
        # 进行多次讨论
        swarm.discuss("话题1", max_rounds=1)
        swarm.discuss("话题2", max_rounds=1)
        
        assert len(swarm.discussion_history) == 2
        assert swarm.discussion_history[0]["topic"] == "话题1"
        assert swarm.discussion_history[1]["topic"] == "话题2"


class TestMainConsciousness:
    """MainConsciousness类单元测试"""

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

    def test_make_decision_with_context(self):
        """测试带上下文的决策"""
        consciousness = MainConsciousness()
        context = {
            "task": "复杂任务",
            "priority": "high",
            "deadline": "2024-12-31"
        }
        decision = consciousness.make_decision(context)

        assert decision["decision"] == "proceed"
        assert "timestamp" in decision

    def test_multiple_swarms_management(self):
        """测试多Swarm管理"""
        consciousness = MainConsciousness()
        
        swarms = []
        for i in range(5):
            swarm = consciousness.create_swarm(name=f"团队{i}")
            swarms.append(swarm)
        
        assert len(consciousness.swarms) == 5
        
        # 验证每个swarm都可以被获取
        for swarm in swarms:
            found = consciousness.get_swarm(swarm.id)
            assert found is not None
            assert found.name == swarm.name

    def test_learning_history(self):
        """测试学习历史"""
        consciousness = MainConsciousness()
        assert isinstance(consciousness.learning_history, list)
        assert len(consciousness.learning_history) == 0


class TestIntegration:
    """集成测试 - 测试组件间交互"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 创建主意识
        consciousness = MainConsciousness()
        
        # 2. 创建Swarm
        swarm = consciousness.create_swarm(name="产品开发团队")
        
        # 3. 创建多个Agent
        developer = Agent(
            name="开发专家",
            role="后端开发",
            expertise=["Python", "API设计", "数据库"]
        )
        tester = Agent(
            name="测试专家",
            role="QA工程师",
            expertise=["自动化测试", "性能测试"]
        )
        designer = Agent(
            name="设计专家",
            role="UI/UX设计师",
            expertise=["用户体验", "交互设计"]
        )
        
        # 4. 添加Agent到Swarm
        swarm.add_agents([developer, tester, designer])
        
        # 5. 验证团队组建
        assert len(swarm.agents) == 3
        assert consciousness.get_swarm(swarm.id) is not None
        
        # 6. 安装技能
        developer.install_skill("FastAPI")
        developer.install_skill("SQLAlchemy")
        tester.install_skill("Pytest")
        tester.install_skill("Selenium")
        
        # 7. 分配MCP工具
        developer.assign_mcp("code_runner")
        tester.assign_mcp("test_runner")
        designer.assign_mcp("design_tools")
        
        # 8. 进行讨论
        discussion = swarm.discuss("如何设计用户认证系统", max_rounds=2)
        assert discussion["status"] == "completed"
        assert len(discussion["rounds"]) == 2
        
        # 9. 执行任务
        result = swarm.execute("实现JWT认证功能")
        assert result["status"] == "completed"
        assert len(result["subtasks"]) > 0
        
        # 10. 验证主意识可以获取所有信息
        swarm_info = consciousness.list_swarms()
        assert len(swarm_info) == 1
        assert swarm_info[0]["agent_count"] == 3

    def test_multi_swarm_coordination(self):
        """测试多Swarm协调"""
        consciousness = MainConsciousness()
        
        # 创建多个专业Swarm
        dev_swarm = consciousness.create_swarm(name="开发团队")
        ops_swarm = consciousness.create_swarm(name="运维团队")
        product_swarm = consciousness.create_swarm(name="产品团队")
        
        # 为每个Swarm添加Agent
        dev_swarm.add_agent(Agent(name="后端开发", role="开发"))
        dev_swarm.add_agent(Agent(name="前端开发", role="开发"))
        
        ops_swarm.add_agent(Agent(name="DevOps", role="运维"))
        ops_swarm.add_agent(Agent(name="SRE", role="可靠性工程"))
        
        product_swarm.add_agent(Agent(name="产品经理", role="产品"))
        product_swarm.add_agent(Agent(name="UX设计师", role="设计"))
        
        # 验证所有Swarm都被管理
        all_swarms = consciousness.list_swarms()
        assert len(all_swarms) == 3
        
        # 每个Swarm独立讨论
        dev_result = dev_swarm.discuss("技术选型", max_rounds=1)
        ops_result = ops_swarm.discuss("部署策略", max_rounds=1)
        product_result = product_swarm.discuss("功能优先级", max_rounds=1)
        
        assert all(r["status"] == "completed" for r in [dev_result, ops_result, product_result])

    def test_agent_transfer_between_swarms(self):
        """测试Agent在Swarm间转移"""
        consciousness = MainConsciousness()
        
        swarm_a = consciousness.create_swarm(name="团队A")
        swarm_b = consciousness.create_swarm(name="团队B")
        
        # 在团队A创建Agent
        agent = Agent(name="多面手", role="全栈")
        swarm_a.add_agent(agent)
        
        assert agent.id in swarm_a.agents
        assert len(swarm_a.agents) == 1
        
        # 模拟转移到团队B
        agent_data = agent.to_dict()
        new_agent = Agent(
            name=agent_data["name"],
            role=agent_data["role"],
            personality=agent_data["personality"],
            expertise=agent_data["expertise"]
        )
        new_agent.skills = agent_data["skills"].copy()
        new_agent.mcp_tools = agent_data["mcp_tools"].copy()
        
        swarm_b.add_agent(new_agent)
        
        assert len(swarm_b.agents) == 1
        assert swarm_b.list_agents()[0]["name"] == "多面手"

    def test_complex_discussion_scenario(self):
        """测试复杂讨论场景"""
        swarm = Swarm(name="架构评审团")
        
        # 添加不同专长的Agent
        experts = [
            Agent(name="架构师", role="系统架构", expertise=["微服务", "分布式系统"]),
            Agent(name="安全专家", role="安全工程师", expertise=["网络安全", "加密"]),
            Agent(name="性能专家", role="性能工程师", expertise=["性能优化", "缓存"]),
            Agent(name="成本专家", role="财务分析师", expertise=["成本控制", "云资源"]),
        ]
        swarm.add_agents(experts)
        
        # 进行多轮讨论
        result = swarm.discuss("是否采用微服务架构", max_rounds=3)
        
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 3
        
        # 验证每轮都有所有Agent参与
        for round_data in result["rounds"]:
            assert len(round_data["thoughts"]) == 4
            agent_names = [t["agent_name"] for t in round_data["thoughts"]]
            assert "架构师" in agent_names
            assert "安全专家" in agent_names

    def test_error_recovery_scenario(self):
        """测试错误恢复场景"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="弹性团队")
        
        # 添加Agent
        agent1 = Agent(name="主开发", role="开发")
        agent2 = Agent(name="备份开发", role="开发")
        swarm.add_agents([agent1, agent2])
        
        # 模拟主开发"故障"（移除）
        swarm.remove_agent(agent1.id)
        
        # 验证备份开发仍在
        assert len(swarm.agents) == 1
        assert swarm.get_agent(agent2.id) is not None
        
        # 任务仍然可以执行
        result = swarm.execute("继续开发任务")
        assert result["status"] == "completed"


class TestEdgeCases:
    """边缘情况测试"""

    def test_empty_name_agent(self):
        """测试空名称Agent"""
        agent = Agent(name="", role="测试")
        assert agent.name == ""
        data = agent.to_dict()
        assert data["name"] == ""

    def test_very_long_name(self):
        """测试超长名称"""
        long_name = "A" * 1000
        agent = Agent(name=long_name, role="测试")
        assert agent.name == long_name

    def test_special_characters_in_name(self):
        """测试特殊字符名称"""
        special_names = [
            "Agent <script>alert('xss')</script>",
            "Agent 🦀",
            "Agent \n\t\r",
            "Agent 中文测试",
            "Agent αβγδ",
        ]
        for name in special_names:
            agent = Agent(name=name, role="测试")
            assert agent.name == name

    def test_unicode_expertise(self):
        """测试Unicode专长"""
        expertise = ["机器学习 🤖", "自然语言处理", "计算机视觉 👁️", "日本語テスト"]
        agent = Agent(name="国际化Agent", role="测试", expertise=expertise)
        assert all(e in agent.expertise for e in expertise)

    def test_large_swarm(self):
        """测试大型Swarm"""
        swarm = Swarm(name="大规模团队")
        
        # 添加100个Agent
        for i in range(100):
            agent = Agent(name=f"Agent{i}", role="成员")
            swarm.add_agent(agent)
        
        assert len(swarm.agents) == 100
        
        # 验证可以列出所有Agent
        agents_list = swarm.list_agents()
        assert len(agents_list) == 100

    def test_nested_skills(self):
        """测试技能依赖关系"""
        agent = Agent(name="技能树Agent", role="开发")
        
        # 安装基础技能
        agent.install_skill("Python基础")
        agent.install_skill("Python进阶")
        agent.install_skill("Web框架")
        agent.install_skill("Django")
        agent.install_skill("Django REST")
        
        assert len(agent.skills) == 5
        
        # 卸载中间技能
        agent.uninstall_skill("Web框架")
        assert "Web框架" not in agent.skills
        assert "Django" in agent.skills  # 其他技能应该保留

    def test_zero_rounds_discussion(self):
        """测试零轮讨论"""
        swarm = Swarm(name="静默团队")
        swarm.add_agent(Agent(name="成员", role="测试"))
        
        result = swarm.discuss("测试话题", max_rounds=0)
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 0

    def test_negative_confidence(self):
        """测试负信心值"""
        # 虽然不应该，但测试系统如何处理
        consciousness = MainConsciousness(confidence=-0.5)
        assert consciousness.confidence == -0.5

    def test_very_high_awareness(self):
        """测试超高意识等级"""
        consciousness = MainConsciousness(awareness_level=999999)
        assert consciousness.awareness_level == 999999

    def test_circular_reference_protection(self):
        """测试循环引用保护"""
        # 确保to_dict不会导致无限递归
        agent = Agent(name="测试", role="测试")
        data = agent.to_dict()
        
        # 验证返回的是简单数据结构
        assert isinstance(data, dict)
        assert isinstance(data["expertise"], list)
        assert isinstance(data["skills"], list)


class TestPerformance:
    """性能相关测试"""

    def test_concurrent_agent_creation(self):
        """测试并发Agent创建性能"""
        import time
        
        start = time.time()
        agents = []
        for i in range(100):
            agent = Agent(name=f"Agent{i}", role="测试")
            agents.append(agent)
        end = time.time()
        
        # 100个Agent应该在1秒内创建
        assert end - start < 1.0
        assert len(agents) == 100

    def test_discussion_performance(self):
        """测试讨论性能"""
        import time
        
        swarm = Swarm(name="性能测试团队")
        for i in range(10):
            swarm.add_agent(Agent(name=f"Agent{i}", role="测试"))
        
        start = time.time()
        result = swarm.discuss("性能测试话题", max_rounds=5)
        end = time.time()
        
        # 10个Agent 5轮讨论应该在1秒内完成
        assert end - start < 1.0
        assert result["status"] == "completed"


class TestCLI:
    """CLI相关测试"""

    def test_import_cli(self):
        """测试CLI模块可导入"""
        from crabswarm.cli import main
        assert callable(main)

    def test_cli_functions_exist(self):
        """测试CLI功能存在"""
        from crabswarm import Swarm, Agent, MainConsciousness
        
        # 验证所有核心类都可导入
        assert Swarm is not None
        assert Agent is not None
        assert MainConsciousness is not None


class TestPackage:
    """包级别测试"""

    def test_version(self):
        """测试版本号"""
        from crabswarm import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_author(self):
        """测试作者信息"""
        from crabswarm import __author__
        assert isinstance(__author__, str)

    def test_all_exports(self):
        """测试__all__导出"""
        from crabswarm import __all__
        assert "Swarm" in __all__
        assert "Agent" in __all__
        assert "MainConsciousness" in __all__
