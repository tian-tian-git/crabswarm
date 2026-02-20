#!/usr/bin/env python3
"""
示例：股票分析Agent团队
"""

from crabswarm import Swarm, Agent


def main():
    print("="*70)
    print("🦀 CrabSwarm 示例：股票分析Agent团队")
    print("="*70)
    
    # 创建股票分析团队
    stock_team = Swarm(name="股票分析团队")
    
    # 创建专业Agent
    analyst = Agent(
        name="分析师",
        role="数据分析",
        personality="理性、严谨、数据驱动",
        expertise=["财务分析", "技术指标", "数据挖掘"],
        bias="过度依赖历史数据",
        catchphrase="数据不会撒谎，但解读可能有偏差"
    )
    
    trader = Agent(
        name="交易员",
        role="实盘交易",
        personality="果断、直觉敏锐、执行力强",
        expertise=["市场情绪", "资金流向", "盘口语言"],
        bias="容易受情绪影响",
        catchphrase="市场总是对的，错的是我的判断"
    )
    
    philosopher = Agent(
        name="哲学家",
        role="策略思考",
        personality="深度思考、质疑一切、追求本质",
        expertise=["行为金融", "系统思维", "认知偏差"],
        bias="过度思考导致行动迟缓",
        catchphrase="为什么？还有更深层的为什么？"
    )
    
    # 添加Agent到团队
    stock_team.add_agents([analyst, trader, philosopher])
    
    print(f"\n✅ 创建团队: {stock_team.name}")
    print(f"   团队成员:")
    for agent_info in stock_team.list_agents():
        print(f"   • {agent_info['name']} ({agent_info['role']})")
    
    # 安装技能
    analyst.install_skill("财务建模")
    analyst.install_skill("Python数据分析")
    trader.install_skill("情绪分析")
    philosopher.install_skill("逻辑推理")
    
    print(f"\n📚 已安装技能:")
    for agent_info in stock_team.list_agents():
        print(f"   • {agent_info['name']}: {', '.join(agent_info['skills'])}")
    
    # 执行讨论
    topic = "分析贵州茅台的投资价值"
    print(f"\n🔍 讨论主题: {topic}")
    print(f"   开始讨论...")
    
    result = stock_team.discuss(topic, max_rounds=3)
    
    print(f"\n📊 讨论结果:")
    print(f"   讨论轮数: {len(result['rounds'])}")
    print(f"   共识: {result['consensus']}")
    
    print("\n" + "="*70)
    print("示例完成！")
    print("="*70)


if __name__ == "__main__":
    main()
