#!/usr/bin/env python3
"""
CrabSwarm Agent团队配置
由蟹爪主意识统一管理
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ProjectAgent:
    """项目Agent配置"""
    id: str
    name: str
    role: str
    responsibilities: List[str]
    skills: List[str]
    tools: List[str] = field(default_factory=list)
    status: str = "idle"  # idle/working/review/done
    current_task: str = ""
    
    def assign_task(self, task: str, tools: List[str] = None):
        """分配任务"""
        self.current_task = task
        self.status = "working"
        if tools:
            self.tools = tools
        return f"✅ {self.name} 已接受任务: {task}"
    
    def complete_task(self, result: str):
        """完成任务"""
        self.status = "done"
        return f"✅ {self.name} 完成任务: {self.current_task}"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "current_task": self.current_task,
            "skills": self.skills,
        }


# Agent团队定义
AGENT_TEAM = {
    "architect": ProjectAgent(
        id="arch-001",
        name="架构师Agent",
        role="系统架构",
        responsibilities=[
            "设计系统架构",
            "定义接口规范", 
            "技术选型",
            "代码审查",
        ],
        skills=[
            "系统设计",
            "模式识别",
            "技术评估",
            "架构文档",
        ],
    ),
    
    "frontend": ProjectAgent(
        id="fe-001",
        name="前端Agent",
        role="前端开发",
        responsibilities=[
            "UI/UX设计",
            "前端代码实现",
            "交互逻辑",
            "响应式适配",
        ],
        skills=[
            "React/Vue",
            "HTML/CSS/JS",
            "UI设计",
            "前端工程化",
        ],
    ),
    
    "backend": ProjectAgent(
        id="be-001",
        name="后端Agent",
        role="后端开发",
        responsibilities=[
            "API设计",
            "业务逻辑实现",
            "数据库设计",
            "性能优化",
        ],
        skills=[
            "Python/Go",
            "数据库设计",
            "API开发",
            "微服务",
        ],
    ),
    
    "router": ProjectAgent(
        id="rt-001",
        name="路由Agent",
        role="网关/路由",
        responsibilities=[
            "URL路由设计",
            "请求分发",
            "负载均衡",
            "API网关",
        ],
        skills=[
            "Nginx",
            "API Gateway",
            "微服务架构",
            "流量控制",
        ],
    ),
    
    "devops": ProjectAgent(
        id="ops-001",
        name="部署Agent",
        role="DevOps",
        responsibilities=[
            "CI/CD流水线",
            "容器化部署",
            "云服务配置",
            "监控告警",
        ],
        skills=[
            "Docker/K8s",
            "GitHub Actions",
            "AWS/阿里云",
            "Terraform",
        ],
    ),
    
    "qa": ProjectAgent(
        id="qa-001",
        name="测试Agent",
        role="质量保证",
        responsibilities=[
            "测试用例设计",
            "自动化测试",
            "性能测试",
            "质量报告",
        ],
        skills=[
            "单元测试",
            "集成测试",
            "性能测试",
            "测试框架",
        ],
    ),
    
    "docs": ProjectAgent(
        id="doc-001",
        name="文档Agent",
        role="技术写作",
        responsibilities=[
            "技术文档编写",
            "API文档",
            "用户手册",
            "示例代码",
        ],
        skills=[
            "技术写作",
            "Markdown",
            "文档生成",
            "教程设计",
        ],
    ),
}


class AgentManager:
    """Agent管理者 - 蟹爪主意识"""
    
    def __init__(self):
        self.agents = AGENT_TEAM
        self.projects = {}
    
    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def get_agent(self, agent_id: str) -> ProjectAgent:
        """获取Agent"""
        return self.agents.get(agent_id)
    
    def assign_task(self, agent_id: str, task: str, tools: List[str] = None) -> str:
        """分配任务给Agent"""
        agent = self.get_agent(agent_id)
        if agent:
            return agent.assign_task(task, tools)
        return f"❌ Agent {agent_id} 不存在"
    
    def check_status(self) -> List[Dict]:
        """检查所有Agent状态"""
        return [
            {
                "name": agent.name,
                "status": agent.status,
                "task": agent.current_task,
            }
            for agent in self.agents.values()
        ]
    
    def create_project_plan(self, project_name: str, tasks: List[Dict]) -> Dict:
        """创建项目计划"""
        plan = {
            "project": project_name,
            "tasks": tasks,
            "created_at": "2026-02-21",
            "status": "planning",
        }
        self.projects[project_name] = plan
        return plan


# 全局管理者实例
manager = AgentManager()

if __name__ == "__main__":
    print("="*70)
    print("🦀 CrabSwarm Agent团队")
    print("="*70)
    
    print("\n📋 Agent列表:")
    for agent_info in manager.list_agents():
        print(f"\n  🎭 {agent_info['name']}")
        print(f"     角色: {agent_info['role']}")
        print(f"     技能: {', '.join(agent_info['skills'][:3])}...")
        print(f"     状态: {agent_info['status']}")
    
    print("\n" + "="*70)
    print(f"总计: {len(manager.agents)} 个Agent")
    print("="*70)
