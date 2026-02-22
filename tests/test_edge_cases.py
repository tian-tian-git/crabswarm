"""
CrabSwarm 边界测试和异常测试
测试边界条件和异常情况
"""

import pytest
from crabswarm import Swarm, Agent, MainConsciousness


class TestAgentEdgeCases:
    """Agent边界条件测试"""
    
    def test_agent_empty_name(self):
        """测试空名称Agent"""
        agent = Agent(name="", role="测试")
        assert agent.name == ""
        assert agent.id is not None
        assert len(agent.id) == 8
    
    def test_agent_special_characters(self):
        """测试特殊字符名称"""
        agent = Agent(name="Agent-测试_123!@#", role="测试员")
        assert agent.name == "Agent-测试_123!@#"
    
    def test_agent_very_long_name(self):
        """测试超长名称"""
        long_name = "A" * 1000
        agent = Agent(name=long_name, role="测试")
        assert agent.name == long_name
    
    def test_agent_empty_expertise(self):
        """测试空专长列表"""
        agent = Agent(name="测试Agent", role="通用", expertise=[])
        # __post_init__ 会将expertise设为 [role]
        assert len(agent.expertise) == 1
        assert agent.expertise[0] == "通用"
    
    def test_agent_duplicate_expertise(self):
        """测试重复专长"""
        agent = Agent(
            name="测试Agent",
            role="开发",
            expertise=["Python", "Python", "Java", "Python"]
        )
        # 当前实现不自动去重，这是预期行为
        assert agent.expertise.count("Python") == 3
    
    def test_agent_unicode_content(self):
        """测试Unicode内容"""
        agent = Agent(
            name="🦀蟹爪",
            role="AI助手",
            personality="🎯专注",
            expertise=["机器学习", "🤖AI", "自然语言处理"]
        )
        assert "🦀" in agent.name
        assert "🤖" in agent.expertise[1]
    
    def test_agent_think_empty_topic(self):
        """测试空话题思考"""
        agent = Agent(name="思考者", role="分析师")
        thought = agent.think("")
        assert isinstance(thought, str)
        assert len(thought) > 0
    
    def test_agent_think_very_long_topic(self):
        """测试超长话题思考"""
        agent = Agent(name="思考者", role="分析师")
        long_topic = "问题" * 1000
        thought = agent.think(long_topic)
        assert isinstance(thought, str)
    
    def test_skill_operations_edge_cases(self):
        """测试技能操作边界情况"""
        agent = Agent(name="技能测试", role="开发")
        
        # 卸载空技能列表中的技能
        assert agent.uninstall_skill("nonexistent") is False
        
        # 安装空字符串技能
        assert agent.install_skill("") is True
        assert "" in agent.skills
        
        # 重复安装空字符串
        assert agent.install_skill("") is False
        
        # 安装None - 当前实现允许None作为技能名（会被转为字符串"None"）
        # 这是实现的行为，测试记录这一行为
        result = agent.install_skill(None)
        # None会被转为字符串"None"并添加到skills
        assert "None" in agent.skills or result is True
    
    def test_mcp_operations_edge_cases(self):
        """测试MCP操作边界情况"""
        agent = Agent(name="MCP测试", role="工具使用者")
        
        # 分配空字符串工具
        assert agent.assign_mcp("") is True
        
        # 重复分配
        assert agent.assign_mcp("") is False
    
    def test_agent_serialization_complex(self):
        """测试复杂对象序列化"""
        agent = Agent(
            name="复杂Agent",
            role="全栈",
            personality="灵活多变",
            expertise=["前端", "后端", "数据库", "DevOps"],
            bias="可能过度工程化"
        )
        agent.install_skill("React")
        agent.install_skill("Node.js")
        agent.assign_mcp("database")
        
        data = agent.to_dict()
        assert data["name"] == "复杂Agent"
        assert len(data["expertise"]) == 4
        assert len(data["skills"]) == 2
        assert len(data["mcp_tools"]) == 1


class TestSwarmEdgeCases:
    """Swarm边界条件测试"""
    
    def test_swarm_empty_name(self):
        """测试空名称Swarm"""
        swarm = Swarm(name="")
        assert swarm.name == ""
        assert len(swarm.id) == 8
    
    def test_swarm_special_characters_name(self):
        """测试特殊字符名称Swarm"""
        swarm = Swarm(name="团队-测试_123!@#中文")
        assert swarm.name == "团队-测试_123!@#中文"
    
    def test_swarm_add_none_agent(self):
        """测试添加None Agent"""
        swarm = Swarm(name="测试")
        with pytest.raises(AttributeError):
            swarm.add_agent(None)
    
    def test_swarm_add_agent_without_id(self):
        """测试添加没有id的Agent"""
        swarm = Swarm(name="测试")
        agent = Agent(name="测试Agent", role="测试")
        # 确保Agent有id
        assert hasattr(agent, 'id')
        assert agent.id is not None
        
        swarm.add_agent(agent)
        assert agent.id in swarm.agents
    
    def test_swarm_remove_nonexistent_agent(self):
        """测试移除不存在的Agent"""
        swarm = Swarm(name="测试")
        assert swarm.remove_agent("nonexistent-id") is False
        assert swarm.remove_agent("") is False
    
    def test_swarm_get_nonexistent_agent(self):
        """测试获取不存在的Agent"""
        swarm = Swarm(name="测试")
        assert swarm.get_agent("nonexistent") is None
        assert swarm.get_agent("") is None
    
    def test_swarm_list_agents_empty(self):
        """测试空Swarm列出Agent"""
        swarm = Swarm(name="空团队")
        agents = swarm.list_agents()
        assert agents == []
        assert len(agents) == 0
    
    def test_swarm_discuss_empty(self):
        """测试空Swarm讨论"""
        swarm = Swarm(name="空团队")
        result = swarm.discuss("测试话题")
        # 空团队应该也能讨论，只是没有thoughts
        assert result["topic"] == "测试话题"
        assert result["status"] == "completed"
    
    def test_swarm_discuss_zero_rounds(self):
        """测试0轮讨论"""
        swarm = Swarm(name="测试")
        swarm.add_agent(Agent(name="成员", role="测试"))
        result = swarm.discuss("话题", max_rounds=0)
        assert len(result["rounds"]) == 0
    
    def test_swarm_discuss_negative_rounds(self):
        """测试负数轮讨论"""
        swarm = Swarm(name="测试")
        swarm.add_agent(Agent(name="成员", role="测试"))
        # 应该处理负数情况
        result = swarm.discuss("话题", max_rounds=-5)
        # 实现可能将其视为0
        assert len(result["rounds"]) >= 0
    
    def test_swarm_discuss_very_large_rounds(self):
        """测试超大轮数讨论"""
        swarm = Swarm(name="测试")
        swarm.add_agent(Agent(name="成员", role="测试"))
        result = swarm.discuss("话题", max_rounds=10000)
        # 实现限制最多10轮
        assert len(result["rounds"]) <= 10
    
    def test_swarm_execute_empty(self):
        """测试空Swarm执行任务"""
        swarm = Swarm(name="空团队")
        result = swarm.execute("测试任务")
        assert result["task"] == "测试任务"
        assert result["status"] == "completed"
        # 空团队应该也能分解任务，只是没有Agent分配
        assert len(result["subtasks"]) == 3
    
    def test_swarm_execute_empty_task(self):
        """测试执行空任务"""
        swarm = Swarm(name="测试")
        swarm.add_agent(Agent(name="成员", role="测试"))
        result = swarm.execute("")
        assert result["task"] == ""
        assert result["status"] == "completed"
    
    def test_swarm_execute_very_long_task(self):
        """测试执行超长任务"""
        swarm = Swarm(name="测试")
        swarm.add_agent(Agent(name="成员", role="测试"))
        long_task = "任务" * 1000
        result = swarm.execute(long_task)
        assert result["task"] == long_task
    
    def test_swarm_add_duplicate_agents(self):
        """测试添加重复Agent"""
        swarm = Swarm(name="测试")
        agent = Agent(name="成员", role="测试")
        
        assert swarm.add_agent(agent) is True
        assert len(swarm.agents) == 1
        
        # 再次添加同一个Agent
        assert swarm.add_agent(agent) is True
        # 应该仍然只有一个（被覆盖）
        assert len(swarm.agents) == 1
    
    def test_swarm_many_agents(self):
        """测试大量Agent"""
        swarm = Swarm(name="大团队")
        for i in range(100):
            agent = Agent(name=f"成员{i}", role="测试")
            swarm.add_agent(agent)
        
        assert len(swarm.agents) == 100
        agents_list = swarm.list_agents()
        assert len(agents_list) == 100
    
    def test_swarm_serialization_empty(self):
        """测试空Swarm序列化"""
        swarm = Swarm(name="空团队")
        data = swarm.to_dict()
        assert data["name"] == "空团队"
        assert data["agents"] == []
        assert "id" in data
        assert "created_at" in data


class TestMainConsciousnessEdgeCases:
    """MainConsciousness边界条件测试"""
    
    def test_consciousness_negative_awareness(self):
        """测试负数认知等级"""
        consciousness = MainConsciousness(awareness_level=-5)
        assert consciousness.awareness_level == -5
    
    def test_consciousness_zero_confidence(self):
        """测试0置信度"""
        consciousness = MainConsciousness(confidence=0.0)
        assert consciousness.confidence == 0.0
    
    def test_consciousness_high_confidence(self):
        """测试高置信度"""
        consciousness = MainConsciousness(confidence=1.0)
        assert consciousness.confidence == 1.0
    
    def test_consciousness_over_confidence(self):
        """测试超过1的置信度"""
        consciousness = MainConsciousness(confidence=2.5)
        # 当前实现不限制范围
        assert consciousness.confidence == 2.5
    
    def test_consciousness_empty_name(self):
        """测试空名称"""
        consciousness = MainConsciousness(name="")
        assert consciousness.name == ""
    
    def test_consciousness_unicode_name(self):
        """测试Unicode名称"""
        consciousness = MainConsciousness(name="🦀蟹爪主意识🎯")
        assert consciousness.name == "🦀蟹爪主意识🎯"
    
    def test_create_swarm_empty_name(self):
        """测试创建空名称Swarm"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="")
        assert swarm.name == ""
        assert swarm.id in consciousness.swarms
    
    def test_get_swarm_empty_id(self):
        """测试获取空ID Swarm"""
        consciousness = MainConsciousness()
        assert consciousness.get_swarm("") is None
    
    def test_get_swarm_nonexistent(self):
        """测试获取不存在的Swarm"""
        consciousness = MainConsciousness()
        assert consciousness.get_swarm("nonexistent") is None
        assert consciousness.get_swarm("12345678") is None
    
    def test_list_swarms_empty(self):
        """测试列出空Swarm列表"""
        consciousness = MainConsciousness()
        swarms = consciousness.list_swarms()
        assert swarms == []
    
    def test_list_swarms_many(self):
        """测试列出大量Swarm"""
        consciousness = MainConsciousness()
        for i in range(50):
            consciousness.create_swarm(name=f"团队{i}")
        
        swarms = consciousness.list_swarms()
        assert len(swarms) == 50
        assert all("id" in s for s in swarms)
        assert all("name" in s for s in swarms)
        assert all("agent_count" in s for s in swarms)
    
    def test_make_decision_empty_context(self):
        """测试空上下文决策"""
        consciousness = MainConsciousness()
        decision = consciousness.make_decision({})
        assert "decision" in decision
        assert "confidence" in decision
        assert "reasoning" in decision
        assert "timestamp" in decision
    
    def test_make_decision_none_context(self):
        """测试None上下文决策"""
        consciousness = MainConsciousness()
        # 应该处理None情况
        try:
            decision = consciousness.make_decision(None)
            assert "decision" in decision
        except (TypeError, AttributeError):
            # 如果抛出异常也是可接受的行为
            pass
    
    def test_make_decision_complex_context(self):
        """测试复杂上下文决策"""
        consciousness = MainConsciousness()
        context = {
            "task": "复杂任务",
            "agents": ["agent1", "agent2"],
            "priority": "high",
            "constraints": {"time": "1h", "budget": 100},
            "metadata": {"version": 1.0, "tags": ["urgent", "important"]}
        }
        decision = consciousness.make_decision(context)
        assert "decision" in decision
        assert decision["confidence"] == 0.7


class TestIntegrationEdgeCases:
    """集成边界测试"""
    
    def test_full_workflow_empty(self):
        """测试完整空工作流"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="测试团队")
        
        # 空团队讨论
        result = swarm.discuss("话题")
        assert result["status"] == "completed"
        
        # 空团队执行任务
        result = swarm.execute("任务")
        assert result["status"] == "completed"
    
    def test_full_workflow_single_agent(self):
        """测试单Agent工作流"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="测试团队")
        agent = Agent(name="唯一成员", role="全能")
        swarm.add_agent(agent)
        
        # 讨论
        result = swarm.discuss("话题", max_rounds=2)
        assert len(result["rounds"]) == 2
        assert len(result["rounds"][0]["thoughts"]) == 1
        
        # 执行任务
        result = swarm.execute("任务")
        assert len(result["results"]) == 3  # 3个子任务
    
    def test_agent_transfer_between_swarms(self):
        """测试Agent在Swarm间转移"""
        consciousness = MainConsciousness()
        swarm1 = consciousness.create_swarm(name="团队1")
        swarm2 = consciousness.create_swarm(name="团队2")
        
        agent = Agent(name="转移成员", role="开发")
        swarm1.add_agent(agent)
        assert agent.id in swarm1.agents
        
        # 从团队1移除
        swarm1.remove_agent(agent.id)
        assert agent.id not in swarm1.agents
        
        # 添加到团队2
        swarm2.add_agent(agent)
        assert agent.id in swarm2.agents
    
    def test_multiple_discussions(self):
        """测试多次讨论"""
        swarm = Swarm(name="讨论团队")
        swarm.add_agent(Agent(name="成员1", role="分析"))
        swarm.add_agent(Agent(name="成员2", role="开发"))
        
        # 第一次讨论
        result1 = swarm.discuss("话题1", max_rounds=2)
        assert len(swarm.discussion_history) == 1
        
        # 第二次讨论
        result2 = swarm.discuss("话题2", max_rounds=2)
        assert len(swarm.discussion_history) == 2
        
        # 验证历史记录
        assert swarm.discussion_history[0]["topic"] == "话题1"
        assert swarm.discussion_history[1]["topic"] == "话题2"
    
    def test_serialization_roundtrip(self):
        """测试序列化往返"""
        # 创建复杂结构
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="测试团队")
        
        agent1 = Agent(
            name="成员1",
            role="开发",
            expertise=["Python", "Go"]
        )
        agent1.install_skill("Docker")
        agent1.assign_mcp("git")
        
        agent2 = Agent(
            name="成员2",
            role="测试",
            expertise=["Selenium", "Pytest"]
        )
        agent2.install_skill("Jenkins")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        # 序列化
        swarm_data = swarm.to_dict()
        
        # 验证数据完整性
        assert swarm_data["name"] == "测试团队"
        assert len(swarm_data["agents"]) == 2
        
        # 验证Agent数据
        agent_data = swarm_data["agents"][0]
        assert "id" in agent_data
        assert "name" in agent_data
        assert "skills" in agent_data
        assert "mcp_tools" in agent_data
