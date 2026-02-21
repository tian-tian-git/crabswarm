"""
MainConsciousness - 主意识
协调Agent团队的核心意识
"""

from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MainConsciousness:
    """
    主意识
    - 唯一对外接口
    - 管理Agent团队
    - 做出最终决策
    """

    name: str = "蟹爪主意识"
    awareness_level: int = 1
    emotional_state: str = "curious"
    confidence: float = 0.7

    # 管理的Swarm
    swarms: Dict[str, any] = field(default_factory=dict)

    # 学习记录
    learning_history: List[Dict] = field(default_factory=list)

    def create_swarm(self, name: str) -> "Swarm":
        """创建新的Swarm"""
        from .swarm import Swarm

        swarm = Swarm(name=name)
        self.swarms[swarm.id] = swarm
        return swarm

    def get_swarm(self, swarm_id: str) -> Optional["Swarm"]:
        """获取Swarm"""
        return self.swarms.get(swarm_id)

    def list_swarms(self) -> List[Dict]:
        """列出所有Swarm"""
        return [
            {
                "id": swarm.id,
                "name": swarm.name,
                "agent_count": len(swarm.agents),
            }
            for swarm in self.swarms.values()
        ]

    def reflect(self) -> str:
        """自我反思"""
        reflections = [
            "我在协调Agent团队时，是否充分考虑了每个Agent的专长？",
            "我的决策是否基于足够的信息？",
            "我是否在持续学习和进化？",
        ]
        import random

        return random.choice(reflections)

    def make_decision(self, context: Dict) -> Dict:
        """做出决策"""
        return {
            "decision": "proceed",
            "confidence": self.confidence,
            "reasoning": "基于当前信息，建议继续",
            "timestamp": datetime.now().isoformat(),
        }
