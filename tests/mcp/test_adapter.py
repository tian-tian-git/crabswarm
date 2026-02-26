"""
MCP Adapter 测试套件

测试目标: 验证adapter.py所有功能
测试框架: pytest + pytest-asyncio
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from crabswarm.mcp.adapter import MCPAdapter, MCPTool, MCPConnectionState


# ============== Fixtures ==============

@pytest.fixture
def adapter_config():
    """标准测试配置"""
    return {
        "server_url": "ws://localhost:8080/mcp",
        "timeout": 30,
        "max_retries": 3,
        "headers": {"Authorization": "Bearer test-token"},
        "_test_mode": True  # 启用测试模式，跳过后台消息循环
    }


@pytest.fixture
def mock_ws_connection():
    """Mock WebSocket连接"""
    mock = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock()
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_session(mock_ws_connection):
    """Mock aiohttp session"""
    mock = AsyncMock()
    mock.ws_connect = AsyncMock(return_value=mock_ws_connection)
    mock.close = AsyncMock()
    return mock


# ============== Test TODO 1: initialize ==============

class TestInitialize:
    """测试初始化功能"""
    
    def test_initialization_with_config(self, adapter_config):
        """测试带配置的初始化"""
        adapter = MCPAdapter(adapter_config)
        
        assert adapter.server_url == "ws://localhost:8080/mcp"
        assert adapter.timeout == 30
        assert adapter.max_retries == 3
        assert adapter.headers == {"Authorization": "Bearer test-token"}
        assert adapter._initialized is True
    
    def test_initialization_default_values(self):
        """测试默认配置初始化"""
        config = {"server_url": "ws://test:8080/mcp"}
        adapter = MCPAdapter(config)
        
        assert adapter.timeout == MCPAdapter.DEFAULT_TIMEOUT
        assert adapter.max_retries == MCPAdapter.DEFAULT_RETRIES
        assert adapter.headers == {}
        assert adapter._initialized is True
    
    def test_initialization_state(self, adapter_config):
        """测试初始化后状态"""
        adapter = MCPAdapter(adapter_config)
        
        assert adapter._state.connected is False
        assert adapter._state.session_id is None
        assert adapter.tools == []
        assert adapter._request_id == 0


# ============== Test TODO 2: connect ==============

class TestConnect:
    """测试连接功能"""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, adapter_config, mock_session, mock_ws_connection):
        """测试成功连接"""
        adapter = MCPAdapter(adapter_config)
        
        # Mock初始化响应
        mock_ws_connection.receive_json = AsyncMock(return_value={
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "TestServer", "version": "1.0.0"},
                "sessionId": "test-session-123"
            }
        })
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await adapter.connect()
        
        assert result is True
        assert adapter.is_connected is True
        assert adapter.state.session_id == "test-session-123"
    
    @pytest.mark.asyncio
    async def test_connect_already_connected(self, adapter_config, mock_session, mock_ws_connection):
        """测试重复连接"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        
        result = await adapter.connect()
        assert result is True  # 应该直接返回True
    
    @pytest.mark.asyncio
    async def test_connect_not_initialized(self):
        """测试未初始化就连接"""
        adapter = MCPAdapter({"server_url": "ws://test:8080/mcp"})
        adapter._initialized = False
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await adapter.connect()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, adapter_config, mock_session):
        """测试连接失败"""
        adapter = MCPAdapter(adapter_config)
        mock_session.ws_connect = AsyncMock(side_effect=Exception("Connection refused"))
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await adapter.connect()
        
        assert result is False
        assert adapter.is_connected is False


# ============== Test TODO 3: send_request ==============

class TestSendRequest:
    """测试请求发送功能"""
    
    @pytest.mark.asyncio
    async def test_send_request_success(self, adapter_config, mock_ws_connection):
        """测试成功发送请求"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        adapter.ws_connection = mock_ws_connection
        adapter._pending_requests = {}
        
        # Mock响应
        response_future = asyncio.Future()
        response_future.set_result({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"data": "test"}
        })
        
        # 模拟消息循环处理响应
        async def mock_receive():
            return response_future.result()
        
        mock_ws_connection.receive_json = mock_receive
        
        # 手动触发响应处理
        asyncio.create_task(adapter._handle_message(await mock_receive()))
        
        result = await adapter.send_request("test/method", {"param": "value"})
        
        assert result == {"data": "test"}
        mock_ws_connection.send_json.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_request_not_connected(self, adapter_config):
        """测试未连接时发送请求"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = False
        
        with pytest.raises(RuntimeError, match="Not connected"):
            await adapter.send_request("test/method", {})
    
    @pytest.mark.asyncio
    async def test_send_request_error_response(self, adapter_config, mock_ws_connection):
        """测试错误响应"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        adapter.ws_connection = mock_ws_connection
        adapter._pending_requests = {}
        
        # 模拟错误响应
        async def mock_receive():
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {"code": -32600, "message": "Invalid Request"}
            }
        
        mock_ws_connection.receive_json = mock_receive
        asyncio.create_task(adapter._handle_message(await mock_receive()))
        
        with pytest.raises(Exception, match="MCP Error"):
            await adapter.send_request("test/method", {})


# ============== Test TODO 4: handle_response ==============

class TestHandleResponse:
    """测试响应处理功能"""
    
    @pytest.mark.asyncio
    async def test_handle_response_success(self, adapter_config):
        """测试成功响应"""
        adapter = MCPAdapter(adapter_config)
        
        response = '{"jsonrpc": "2.0", "id": 1, "result": {"data": "test"}}'
        result = await adapter.handle_response(response)
        
        assert result == {"data": "test"}
    
    @pytest.mark.asyncio
    async def test_handle_response_error(self, adapter_config):
        """测试错误响应"""
        adapter = MCPAdapter(adapter_config)
        
        response = '{"jsonrpc": "2.0", "id": 1, "error": {"code": -32600, "message": "Invalid Request"}}'
        
        with pytest.raises(Exception, match="MCP Error -32600"):
            await adapter.handle_response(response)
    
    @pytest.mark.asyncio
    async def test_handle_response_invalid_json(self, adapter_config):
        """测试无效JSON"""
        adapter = MCPAdapter(adapter_config)
        
        response = "invalid json"
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            await adapter.handle_response(response)


# ============== Test TODO 5: list_tools ==============

class TestListTools:
    """测试工具列表功能"""
    
    @pytest.mark.asyncio
    async def test_list_tools_success(self, adapter_config):
        """测试成功获取工具列表"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        
        # Mock send_request
        adapter.send_request = AsyncMock(return_value={
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "inputSchema": {"type": "object"}
                }
            ]
        })
        
        tools = await adapter.list_tools()
        
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        assert tools[0].description == "A test tool"
        adapter.send_request.assert_called_once_with("tools/list", {})
    
    @pytest.mark.asyncio
    async def test_list_tools_empty(self, adapter_config):
        """测试空工具列表"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        adapter.send_request = AsyncMock(return_value={"tools": []})
        
        tools = await adapter.list_tools()
        
        assert len(tools) == 0


# ============== Test TODO 6: call_tool ==============

class TestCallTool:
    """测试工具调用功能"""
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, adapter_config):
        """测试成功调用工具"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        adapter.tools = [
            MCPTool(name="test_tool", description="Test", parameters={})
        ]
        
        adapter.send_request = AsyncMock(return_value={
            "content": [{"type": "text", "text": "Result"}]
        })
        
        result = await adapter.call_tool("test_tool", {"param": "value"})
        
        assert result["content"][0]["text"] == "Result"
        adapter.send_request.assert_called_once_with(
            "tools/call",
            {"name": "test_tool", "arguments": {"param": "value"}}
        )
    
    @pytest.mark.asyncio
    async def test_call_tool_not_found(self, adapter_config):
        """测试调用不存在的工具"""
        adapter = MCPAdapter(adapter_config)
        adapter._state.connected = True
        adapter.tools = []
        
        with pytest.raises(ValueError, match="Tool not found"):
            await adapter.call_tool("nonexistent_tool", {})


# ============== Integration Tests ==============

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, adapter_config, mock_session, mock_ws_connection):
        """测试完整工作流程"""
        adapter = MCPAdapter(adapter_config)
        
        # Mock连接响应
        mock_ws_connection.receive_json = AsyncMock(return_value={
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "TestServer"},
                "sessionId": "session-123"
            }
        })
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            # 1. 连接
            connected = await adapter.connect()
            assert connected is True
            
            # 2. 获取工具列表
            adapter.send_request = AsyncMock(return_value={
                "tools": [{"name": "echo", "description": "Echo tool", "inputSchema": {}}]
            })
            tools = await adapter.list_tools()
            assert len(tools) == 1
            
            # 3. 调用工具
            adapter.send_request = AsyncMock(return_value={"result": "echo"})
            result = await adapter.call_tool("echo", {"text": "hello"})
            assert result["result"] == "echo"
            
            # 4. 关闭连接
            await adapter.close()
            assert adapter.is_connected is False
