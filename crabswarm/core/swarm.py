"""
CrabSwarm Core - Agent and Swarm implementation
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Agent:
    """
    Agent - 专业Agent
    每个Agent有自己的专长、人格和盲点
    """
    
    name: str
    role: str
    personality: str = "专业、高效"
    expertise: List[str] = field(default_factory=list)
    bias: str = "可能有盲点"
    catchphrase: str = "Ready to work"
    
    # 内部状态
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    skills: List[str] = field(default_factory=list)
    mcp_tools: List[str] = field(default_factory=list)
    memory: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.expertise:
            self.expertise = [self.role]
    
    def install_skill(self, skill_name: str) -> bool:
        """安装技能"""
        if skill_name not in self.skills:
            self.skills.append(skill_name)
            return True
        return False
    
    def uninstall_skill(self, skill_name: str) -> bool:
        """卸载技能"""
        if skill_name in self.skills:
            self.skills.remove(skill_name)
            return True
        return False
    
    def assign_mcp(self, tool_name: str) -> bool:
        """分配MCP工具"""
        if tool_name not in self.mcp_tools:
            self.mcp_tools.append(tool_name)
            return True
        return False
    
    def think(self, topic: str) -> str:
        """Agent思考"""
        # 基于专长生成思考
        if self.expertise:
            expertise_str = ", ".join(self.expertise[:2])
            return f"从{expertise_str}角度，我认为{topic}需要..."
        return f"关于{topic}，我需要更多信息..."
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "expertise": self.expertise,
            "bias": self.bias,
            "catchphrase": self.catchphrase,
            "skills": self.skills,
            "mcp_tools": self.mcp_tools,
        }


class Swarm:
    """
    Swarm - Agent团队
    由主意识协调的Agent集合
    """
    
    def __init__(self, name: str):
        self.name = name
        self.id = str(uuid.uuid4())[:8]
        self.agents: Dict[str, Agent] = {}
        self.discussion_history: List[Dict] = []
        self.created_at = datetime.now()
    
    def add_agent(self, agent: Agent) -> bool:
        """添加Agent"""
        self.agents[agent.id] = agent
        return True
    
    def add_agents(self, agents: List[Agent]) -> bool:
        """批量添加Agent"""
        for agent in agents:
            self.add_agent(agent)
        return True
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取Agent"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def discuss(self, topic: str, max_rounds: int = 10) -> Dict:
        """
        Agent讨论
        模拟多轮讨论，形成共识
        """
        discussion = {
            "topic": topic,
            "max_rounds": max_rounds,
            "rounds": [],
            "consensus": "",
            "status": "completed",
        }
        
        agent_list = list(self.agents.values())
        
        for round_num in range(1, min(max_rounds + 1, 11)):  # 最多10轮
            round_data = {
                "round": round_num,
                "thoughts": [],
            }
            
            # 每个Agent发表观点
            for agent in agent_list:
                thought = agent.think(topic)
                round_data["thoughts"].append({
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "thought": thought,
                })
            
            discussion["rounds"].append(round_data)
        
        # 形成共识（简化版）
        if discussion["rounds"]:
            last_round = discussion["rounds"][-1]
            thoughts = [t["thought"] for t in last_round["thoughts"]]
            discussion["consensus"] = f"基于{len(thoughts)}个Agent的讨论，建议进一步分析..."
        
        self.discussion_history.append(discussion)
        return discussion
    
    def execute(self, task: str) -> Dict:
        """
        执行任务
        主入口，协调Agent完成任务
        """
        # 分解任务
        subtasks = self._decompose_task(task)
        
        # 分配任务
        results = []
        for subtask in subtasks:
            # 找到最适合的Agent
            agent = self._select_best_agent(subtask)
            if agent:
                result = {
                    "subtask": subtask,
                    "agent": agent.name,
                    "status": "assigned",
                }
                results.append(result)
        
        return {
            "task": task,
            "subtasks": subtasks,
            "results": results,
            "status": "completed",
        }
    
    def _decompose_task(self, task: str) -> List[str]:
        """分解任务"""
        # 简化版：将任务拆分为分析、执行、验证
        return [
            f"分析: {task}",
            f"执行: {task}",
            f"验证: {task}",
        ]
    
    def _select_best_agent(self, subtask: str) -> Optional[Agent]:
        """选择最适合的Agent"""
        # 简化版：随机选择
        if self.agents:
            return list(self.agents.values())[0]
        return None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "agents": self.list_agents(),
            "created_at": self.created_at.isoformat(),
        }
