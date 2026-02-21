"""
CrabSwarm CLI
命令行工具
"""

import argparse
import json
from .core.swarm import Swarm
from .core.swarm import Agent
from .core.consciousness import MainConsciousness


def main():
    parser = argparse.ArgumentParser(description="CrabSwarm - Multi-Agent Framework")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 创建swarm
    create_parser = subparsers.add_parser("create", help="Create a new swarm")
    create_parser.add_argument("name", help="Swarm name")

    # 添加agent
    add_parser = subparsers.add_parser("add-agent", help="Add agent to swarm")
    add_parser.add_argument("swarm_id", help="Swarm ID")
    add_parser.add_argument("name", help="Agent name")
    add_parser.add_argument("role", help="Agent role")

    # 列出agents
    list_parser = subparsers.add_parser("list", help="List agents in swarm")
    list_parser.add_argument("swarm_id", help="Swarm ID")

    # 执行任务
    exec_parser = subparsers.add_parser("execute", help="Execute task")
    exec_parser.add_argument("swarm_id", help="Swarm ID")
    exec_parser.add_argument("task", help="Task description")

    args = parser.parse_args()

    if args.command == "create":
        swarm = Swarm(name=args.name)
        print(f"Created swarm: {swarm.name} (ID: {swarm.id})")

    elif args.command == "add-agent":
        # 简化版：实际应该先从存储中加载swarm
        agent = Agent(name=args.name, role=args.role)
        print(f"Created agent: {agent.name} (ID: {agent.id})")
        print(f"Add this agent to swarm {args.swarm_id}")

    elif args.command == "list":
        print(f"Listing agents in swarm {args.swarm_id}")
        print("(In real implementation, this would load from storage)")

    elif args.command == "execute":
        print(f"Executing task in swarm {args.swarm_id}: {args.task}")
        print("(In real implementation, this would coordinate agents)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
