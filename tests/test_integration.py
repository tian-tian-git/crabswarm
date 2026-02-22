"""
集成测试
测试完整的工作流和场景
"""

import pytest
from crabswarm import Swarm, Agent, MainConsciousness


class TestFullWorkflow:
    """完整工作流测试"""
    
    def test_create_team_and_discuss(self):
        """测试创建团队并讨论"""
        # 创建主意识
        consciousness = MainConsciousness()
        
        # 创建Swarm
        swarm = consciousness.create_swarm(name="产品开发团队")
        
        # 添加Agent
        product_manager = Agent(
            name="产品经理",
            role="产品规划",
            expertise=["需求分析", "用户研究"],
            personality="用户导向"
        )
        
        developer = Agent(
            name="后端开发",
            role="后端开发",
            expertise=["Python", "数据库", "API设计"],
            personality="严谨"
        )
        
        tester = Agent(
            name="测试工程师",
            role="质量保障",
            expertise=["自动化测试", "性能测试"],
            personality="细致"
        )
        
        swarm.add_agents([product_manager, developer, tester])
        
        # 验证团队创建
        assert len(swarm.agents) == 3
        assert consciousness.get_swarm(swarm.id) is not None
        
        # 进行讨论
        result = swarm.discuss("如何优化产品性能", max_rounds=3)
        
        assert result["topic"] == "如何优化产品性能"
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 3
        assert "consensus" in result
        
        # 验证每个Agent都参与了讨论
        for round_data in result["rounds"]:
            assert len(round_data["thoughts"]) == 3
    
    def test_execute_project_task(self):
        """测试执行项目任务"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="项目执行团队")
        
        # 添加执行Agent
        architect = Agent(
            name="架构师",
            role="系统设计",
            expertise=["架构设计", "技术选型"]
        )
        
        dev = Agent(
            name="开发工程师",
            role="功能开发",
            expertise=["编码实现", "代码审查"]
        )
        
        swarm.add_agents([architect, dev])
        
        # 执行任务
        result = swarm.execute("实现用户认证系统")
        
        assert result["task"] == "实现用户认证系统"
        assert result["status"] == "completed"
        assert len(result["subtasks"]) == 3  # 分析、执行、验证
        assert len(result["results"]) == 3
    
    def test_multi_swarm_management(self):
        """测试多Swarm管理"""
        consciousness = MainConsciousness()
        
        # 创建多个团队
        dev_team = consciousness.create_swarm(name="开发团队")
        qa_team = consciousness.create_swarm(name="测试团队")
        ops_team = consciousness.create_swarm(name="运维团队")
        
        # 为每个团队添加成员
        dev_team.add_agent(Agent(name="后端开发", role="后端"))
        dev_team.add_agent(Agent(name="前端开发", role="前端"))
        
        qa_team.add_agent(Agent(name="测试员", role="测试"))
        
        ops_team.add_agent(Agent(name="运维工程师", role="运维"))
        ops_team.add_agent(Agent(name="DevOps", role="DevOps"))
        
        # 验证所有Swarm
        swarms = consciousness.list_swarms()
        assert len(swarms) == 3
        
        # 验证每个Swarm的Agent数量
        swarm_info = {s["name"]: s["agent_count"] for s in swarms}
        assert swarm_info["开发团队"] == 2
        assert swarm_info["测试团队"] == 1
        assert swarm_info["运维团队"] == 2
    
    def test_agent_skills_workflow(self):
        """测试Agent技能工作流"""
        swarm = Swarm(name="技能测试团队")
        
        # 创建具有不同技能的Agent
        python_dev = Agent(
            name="Python开发者",
            role="后端开发",
            expertise=["Python", "FastAPI"]
        )
        python_dev.install_skill("FastAPI")
        python_dev.install_skill("SQLAlchemy")
        python_dev.install_skill("Docker")
        
        frontend_dev = Agent(
            name="前端开发者",
            role="前端开发",
            expertise=["React", "TypeScript"]
        )
        frontend_dev.install_skill("React")
        frontend_dev.install_skill("TailwindCSS")
        
        swarm.add_agents([python_dev, frontend_dev])
        
        # 验证技能
        agents = swarm.list_agents()
        python_agent = next(a for a in agents if a["name"] == "Python开发者")
        frontend_agent = next(a for a in agents if a["name"] == "前端开发者")
        
        assert len(python_agent["skills"]) == 3
        assert len(frontend_agent["skills"]) == 2
        assert "FastAPI" in python_agent["skills"]
        assert "React" in frontend_agent["skills"]


class TestCollaborationScenarios:
    """协作场景测试"""
    
    def test_code_review_scenario(self):
        """测试代码审查场景"""
        swarm = Swarm(name="代码审查小组")
        
        # 创建审查团队
        author = Agent(
            name="代码作者",
            role="开发者",
            expertise=["功能实现"],
            personality="积极"
        )
        
        reviewer1 = Agent(
            name="审查者A",
            role="代码审查",
            expertise=["代码质量", "最佳实践"],
            personality="严格"
        )
        
        reviewer2 = Agent(
            name="审查者B",
            role="安全审查",
            expertise=["安全审计", "漏洞检测"],
            personality="谨慎"
        )
        
        swarm.add_agents([author, reviewer1, reviewer2])
        
        # 模拟代码审查讨论
        result = swarm.discuss("审查新的API端点实现", max_rounds=2)
        
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 2
        
        # 验证每个审查者都发表了意见
        for round_data in result["rounds"]:
            thoughts = round_data["thoughts"]
            assert len(thoughts) == 3
            
            reviewer_thoughts = [t for t in thoughts if "审查" in t["agent_name"]]
            assert len(reviewer_thoughts) == 2
    
    def test_incident_response_scenario(self):
        """测试故障响应场景"""
        consciousness = MainConsciousness()
        swarm = consciousness.create_swarm(name="故障响应团队")
        
        # 创建响应团队
        incident_lead = Agent(
            name="故障负责人",
            role="协调",
            expertise=["事件管理", "沟通协调"],
            personality="冷静"
        )
        
        backend_engineer = Agent(
            name="后端工程师",
            role="后端排查",
            expertise=["系统诊断", "日志分析"],
            personality="专注"
        )
        
        devops_engineer = Agent(
            name="DevOps工程师",
            role="基础设施",
            expertise=["监控", "部署", "容器"],
            personality="高效"
        )
        
        swarm.add_agents([incident_lead, backend_engineer, devops_engineer])
        
        # 决策
        decision = consciousness.make_decision({
            "type": "incident",
            "severity": "high",
            "service": "payment-api",
            "symptoms": ["500 errors", "high latency"]
        })
        
        assert "decision" in decision
        assert "confidence" in decision
        assert "reasoning" in decision
        
        # 执行响应任务
        result = swarm.execute("处理支付API故障")
        
        assert result["task"] == "处理支付API故障"
        assert result["status"] == "completed"
    
    def test_product_planning_scenario(self):
        """测试产品规划场景"""
        swarm = Swarm(name="产品规划委员会")
        
        # 创建规划团队
        pm = Agent(
            name="产品经理",
            role="产品",
            expertise=["需求分析", "路线图规划"],
            personality="战略思维"
        )
        
        designer = Agent(
            name="设计师",
            role="UX设计",
            expertise=["用户体验", "交互设计"],
            personality="创意"
        )
        
        tech_lead = Agent(
            name="技术负责人",
            role="技术",
            expertise=["技术评估", "可行性分析"],
            personality="务实"
        )
        
        business_analyst = Agent(
            name="业务分析师",
            role="业务",
            expertise=["市场分析", "商业模式"],
            personality="数据驱动"
        )
        
        swarm.add_agents([pm, designer, tech_lead, business_analyst])
        
        # 产品特性讨论
        result = swarm.discuss("下一季度的产品优先级", max_rounds=3)
        
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 3
        
        # 验证所有角色都参与了
        first_round = result["rounds"][0]
        assert len(first_round["thoughts"]) == 4
        
        roles = [t["agent_name"] for t in first_round["thoughts"]]
        assert "产品经理" in roles
        assert "设计师" in roles
        assert "技术负责人" in roles
        assert "业务分析师" in roles


class TestLearningAndEvolution:
    """学习和进化测试"""
    
    def test_consciousness_reflection(self):
        """测试主意识反思"""
        consciousness = MainConsciousness()
        
        # 创建一些Swarm和Agent
        for i in range(3):
            swarm = consciousness.create_swarm(name=f"团队{i}")
            swarm.add_agent(Agent(name=f"成员{i}", role="测试"))
        
        # 反思
        reflection = consciousness.reflect()
        
        assert isinstance(reflection, str)
        assert len(reflection) > 0
    
    def test_discussion_history_accumulation(self):
        """测试讨论历史积累"""
        swarm = Swarm(name="学习团队")
        swarm.add_agent(Agent(name="学习者", role="学习"))
        
        # 进行多次讨论
        topics = [
            "如何提高代码质量",
            "如何优化性能",
            "如何改进团队协作",
            "如何减少技术债务"
        ]
        
        for topic in topics:
            swarm.discuss(topic, max_rounds=2)
        
        # 验证历史记录
        assert len(swarm.discussion_history) == 4
        
        for i, topic in enumerate(topics):
            assert swarm.discussion_history[i]["topic"] == topic
    
    def test_agent_evolution_simulation(self):
        """测试Agent进化模拟"""
        agent = Agent(
            name="初级开发者",
            role="开发",
            expertise=["基础编程"],
            personality="好学"
        )
        
        # 初始技能
        assert len(agent.skills) == 0
        
        # 学习新技能
        skills_to_learn = ["Python", "Git", "Docker", "AWS", "Kubernetes"]
        for skill in skills_to_learn:
            agent.install_skill(skill)
        
        # 验证技能增长
        assert len(agent.skills) == 5
        assert all(skill in agent.skills for skill in skills_to_learn)
        
        # 升级专长
        agent.expertise.extend(["系统设计", "架构模式"])
        assert len(agent.expertise) == 3  # 原有1个 + 新增2个


class TestErrorRecovery:
    """错误恢复测试"""
    
    def test_agent_recovery_after_removal(self):
        """测试Agent移除后恢复"""
        swarm = Swarm(name="弹性团队")
        
        agent1 = Agent(name="成员1", role="开发")
        agent2 = Agent(name="成员2", role="测试")
        
        swarm.add_agents([agent1, agent2])
        assert len(swarm.agents) == 2
        
        # 移除一个Agent
        swarm.remove_agent(agent1.id)
        assert len(swarm.agents) == 1
        assert agent1.id not in swarm.agents
        
        # 添加新Agent替代
        agent3 = Agent(name="新成员", role="开发")
        swarm.add_agent(agent3)
        assert len(swarm.agents) == 2
        
        # 团队仍然可以工作
        result = swarm.discuss("继续工作")
        assert result["status"] == "completed"
    
    def test_swarm_reconstruction(self):
        """测试Swarm重建"""
        consciousness = MainConsciousness()
        
        # 创建原始Swarm
        original = consciousness.create_swarm(name="原始团队")
        original.add_agent(Agent(name="成员1", role="开发"))
        original.add_agent(Agent(name="成员2", role="测试"))
        
        # 保存状态
        original_data = original.to_dict()
        
        # 创建新Swarm并恢复
        new_swarm = consciousness.create_swarm(name="重建团队")
        
        # 根据保存的数据重建Agent
        for agent_data in original_data["agents"]:
            new_agent = Agent(
                name=agent_data["name"],
                role=agent_data["role"],
                expertise=agent_data.get("expertise", [])
            )
            for skill in agent_data.get("skills", []):
                new_agent.install_skill(skill)
            new_swarm.add_agent(new_agent)
        
        # 验证重建成功
        assert len(new_swarm.agents) == 2
        assert new_swarm.name == "重建团队"


class TestPerformanceScenarios:
    """性能场景测试"""
    
    def test_large_team_discussion(self):
        """测试大团队讨论"""
        swarm = Swarm(name="大团队")
        
        # 创建20个Agent
        for i in range(20):
            agent = Agent(
                name=f"成员{i}",
                role=f"角色{i % 5}",
                expertise=[f"专长{i % 3}"]
            )
            swarm.add_agent(agent)
        
        assert len(swarm.agents) == 20
        
        # 进行简短讨论
        result = swarm.discuss("团队建设", max_rounds=2)
        
        assert result["status"] == "completed"
        assert len(result["rounds"]) == 2
        
        # 每轮应该有20个thoughts
        for round_data in result["rounds"]:
            assert len(round_data["thoughts"]) == 20
    
    def test_many_small_tasks(self):
        """测试多个小任务"""
        swarm = Swarm(name="任务工厂")
        swarm.add_agent(Agent(name="执行者", role="通用"))
        
        tasks = [f"任务{i}" for i in range(10)]
        results = []
        
        for task in tasks:
            result = swarm.execute(task)
            results.append(result)
        
        assert len(results) == 10
        assert all(r["status"] == "completed" for r in results)
