"""
CrabSwarm - A "soulful" multi-agent collaboration framework
"""

__version__ = "0.1.0"
__author__ = "CrabSwarm Team"

from .core.swarm import Swarm, Agent
from .core.consciousness import MainConsciousness

__all__ = ["Swarm", "Agent", "MainConsciousness"]