#!/usr/bin/env python3
"""
MCP Adapter 连接测试

验证adapter可以成功连接到MCP服务端
"""

import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/crabswarm')

from crabswarm.mcp.adapter_sse import MCPAdapter


async def test_adapter_connection():
    """测试adapter连接"""
    print("🧪 Testing MCP Adapter Connection (SSE)")
    print("=" * 50)
    
    # 配置adapter - 使用SSE端点
    config = {
        "server_url": "http://localhost:3000",
        "timeout": 30,
        "max_retries": 3,
        "_test_mode": True  # 测试模式，不启动SSE循环
    }
    
    adapter = MCPAdapter(config)
    
    # 测试1: 初始化
    print("\n1️⃣ Testing initialization...")
    assert adapter._initialized == True
    print("   ✅ Adapter initialized successfully")
    
    # 测试2: 连接服务端
    print("\n2️⃣ Testing connection...")
    connected = await adapter.connect()
    if connected:
        print("   ✅ Connected to MCP server")
        print(f"   Server info: {adapter.state.server_info}")
        print(f"   Protocol version: {adapter.state.protocol_version}")
    else:
        print("   ❌ Failed to connect")
        return False
    
    # 测试3: 获取工具列表
    print("\n3️⃣ Testing list_tools...")
    try:
        tools = await adapter.list_tools()
        print(f"   ✅ Loaded {len(tools)} tools")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"   ❌ Failed to list tools: {e}")
        return False
    
    # 测试4: 调用工具
    print("\n4️⃣ Testing call_tool...")
    try:
        result = await adapter.call_tool("web_search", {"query": "Python", "limit": 3})
        print("   ✅ Tool call successful")
        print(f"   Result preview: {str(result)[:100]}...")
    except Exception as e:
        print(f"   ❌ Failed to call tool: {e}")
        return False
    
    # 测试5: 调用另一个工具
    print("\n5️⃣ Testing agent_communication tool...")
    try:
        result = await adapter.call_tool("agent_communication", {
            "target_agent": "news-collector",
            "message": {"type": "test", "content": "Hello"},
            "message_type": "request"
        })
        print("   ✅ Agent communication tool call successful")
    except Exception as e:
        print(f"   ❌ Failed to call agent_communication: {e}")
        return False
    
    # 测试6: 关闭连接
    print("\n6️⃣ Testing close...")
    await adapter.close()
    print("   ✅ Connection closed")
    
    print("\n" + "=" * 50)
    print("✅ All adapter tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_adapter_connection())
    sys.exit(0 if success else 1)
