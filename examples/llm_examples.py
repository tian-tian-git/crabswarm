"""
LLM集成使用示例

展示如何使用CrabSwarm LLM模块的各种功能
"""

import asyncio
import os
from typing import List

# 确保在正确的路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crabswarm.llm import (
    LLMClient,
    LLMConfig,
    ModelProvider,
    ModelTier,
    ChatMessage,
    ModelRouter,
    RoutingRule,
    LLMAgent,
    CostTracker,
    RetryConfig,
    ResponseCache,
    EnhancedLLMClient,
    MultiProviderClient,
)


# ============ 示例1: 基础使用 ============

async def example_basic():
    """基础使用示例"""
    print("\n=== 示例1: 基础使用 ===\n")
    
    # 从环境变量获取API Key
    api_key = os.getenv("SILICONFLOW_API_KEY", "your-api-key")
    
    # 创建配置
    config = LLMConfig(
        provider=ModelProvider.SILICONFLOW,
        api_key=api_key,
    )
    
    # 创建客户端
    client = LLMClient(config)
    
    # 发送消息
    messages = [
        ChatMessage(role="system", content="你是一个 helpful 助手。"),
        ChatMessage(role="user", content="你好，请介绍一下自己"),
    ]
    
    try:
        response = await client.chat(messages)
        print(f"响应: {response.content}")
        print(f"模型: {response.model}")
        print(f"Token使用: {response.usage}")
    except Exception as e:
        print(f"错误: {e}")


# ============ 示例2: 流式输出 ============

async def example_streaming():
    """流式输出示例"""
    print("\n=== 示例2: 流式输出 ===\n")
    
    api_key = os.getenv("SILICONFLOW_API_KEY", "your-api-key")
    config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key=api_key)
    client = LLMClient(config)
    
    messages = [
        ChatMessage(role="user", content="写一首关于AI的短诗"),
    ]
    
    print("流式响应: ", end="", flush=True)
    try:
        async for chunk in client.chat(messages, stream=True):
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"\n错误: {e}")


# ============ 示例3: 模型路由 ============

async def example_routing():
    """模型路由示例"""
    print("\n=== 示例3: 模型路由 ===\n")
    
    api_key = os.getenv("SILICONFLOW_API_KEY", "your-api-key")
    config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key=api_key)
    client = LLMClient(config)
    
    # 创建路由器
    router = ModelRouter(client)
    
    # 添加自定义规则
    router.add_rule(RoutingRule(
        name="coding_task",
        condition=lambda p: "代码" in p or "code" in p.lower(),
        model="deepseek-v3",
        priority=10,
    ))
    
    # 测试路由
    prompts = [
        "你好",
        "写一个Python函数计算斐波那契数列",
        "分析市场趋势",
    ]
    
    for prompt in prompts:
        model = router.route(prompt)
        analysis = router.analyze_prompt(prompt)
        print(f"提示: {prompt[:30]}...")
        print(f"  路由模型: {model}")
        print(f"  特征: {analysis['features']}")
        print()


# ============ 示例4: LLM Agent ============

async def example_agent():
    """LLM Agent示例"""
    print("\n=== 示例4: LLM Agent ===\n")
    
    api_key = os.getenv("SILICONFLOW_API_KEY", "your-api-key")
    config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key=api_key)
    client = LLMClient(config)
    
    # 创建Agent
    agent = LLMAgent(
        name="数据分析师",
        role="专业数据分析师，擅长从数据中发现洞察",
        llm_client=client,
        model="deepseek-v3",
        system_prompt="你是资深数据分析师，回答简洁专业。",
    )
    
    # 思考
    result = await agent.think("如何分析用户留存率下降的问题？")
    print(f"思考结果:\n{result}\n")
    
    # 对话
    reply = await agent.chat("有什么具体的分析方法？")
    print(f"对话回复:\n{reply}\n")
    
    # 查看统计
    stats = agent.get_stats()
    print(f"Agent统计: {stats}")


# ============ 示例5: 成本追踪 ============

async def example_cost_tracking():
    """成本追踪示例"""
    print("\n=== 示例5: 成本追踪 ===\n")
    
    # 创建成本追踪器
    def on_alert(alert):
        print(f"[告警] {alert.level}: {alert.message}")
    
    tracker = CostTracker(
        daily_budget_usd=1.0,  # 设置低预算以便测试告警
        alert_threshold=0.5,
        on_alert=on_alert,
    )
    
    # 模拟使用记录
    tracker.record_usage("deepseek-ai/DeepSeek-V3", 1000, 500)
    tracker.record_usage("Qwen/Qwen2.5-14B-Instruct", 500, 200)
    
    # 查看状态
    status = tracker.get_budget_status()
    print(f"预算状态: {status}")
    
    # 查看报告
    report = tracker.get_report()
    print(f"\n完整报告:")
    print(f"  Token统计: {report['tokens']}")


# ============ 示例6: 增强型客户端 ============

async def example_enhanced_client():
    """增强型客户端示例"""
    print("\n=== 示例6: 增强型客户端 ===\n")
    
    api_key = os.getenv("SILICONFLOW_API_KEY", "your-api-key")
    config = LLMConfig(provider=ModelProvider.SILICONFLOW, api_key=api_key)
    
    # 创建增强型客户端（带缓存和重试）
    client = EnhancedLLMClient(
        config=config,
        enable_cache=True,
        cache_size=100,
        enable_cost_tracking=True,
        daily_budget_usd=10.0,
    )
    
    messages = [
        ChatMessage(role="user", content="什么是机器学习？"),
    ]
    
    try:
        # 第一次请求
        response1 = await client.chat(messages)
        print(f"第一次响应: {response1.content[:50]}...")
        
        # 第二次相同请求（应该命中缓存）
        response2 = await client.chat(messages)
        print(f"第二次响应(缓存): {response2.content[:50]}...")
        
        # 查看统计
        stats = client.get_stats()
        print(f"\n统计: {stats}")
        
    except Exception as e:
        print(f"错误: {e}")


# ============ 示例7: 多提供商 ============

async def example_multi_provider():
    """多提供商示例"""
    print("\n=== 示例7: 多提供商配置 ===\n")
    
    # 配置多个提供商
    providers = [
        LLMConfig(
            provider=ModelProvider.SILICONFLOW,
            api_key=os.getenv("SILICONFLOW_API_KEY", "key1"),
        ),
        LLMConfig(
            provider=ModelProvider.OPENROUTER,
            api_key=os.getenv("OPENROUTER_API_KEY", "key2"),
        ),
    ]
    
    # 创建多提供商客户端
    # 注意：实际使用时需要有效的API Key
    print("多提供商配置示例:")
    print(f"  主提供商: {providers[0].provider.value}")
    print(f"  备用提供商: {providers[1].provider.value}")
    print("  当主提供商失败时，自动切换到备用提供商")


# ============ 运行所有示例 ============

async def main():
    """运行所有示例"""
    print("=" * 50)
    print("CrabSwarm LLM 集成示例")
    print("=" * 50)
    
    # 运行示例（带错误处理）
    examples = [
        ("基础使用", example_basic),
        ("流式输出", example_streaming),
        ("模型路由", example_routing),
        ("LLM Agent", example_agent),
        ("成本追踪", example_cost_tracking),
        ("增强型客户端", example_enhanced_client),
        ("多提供商", example_multi_provider),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n[{name}] 示例出错: {e}")
    
    print("\n" + "=" * 50)
    print("示例运行完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
