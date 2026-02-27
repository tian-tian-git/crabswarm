#!/usr/bin/env python3
"""
MCP Server - CrabSwarm MCP 服务端实现

支持:
- SSE (Server-Sent Events) 连接
- JSON-RPC 协议
- 工具注册和调用
- 智能体间通信
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Optional[Callable] = None


@dataclass
class MCPAgent:
    """MCP智能体定义"""
    id: str
    name: str
    department: str
    permissions: List[str] = field(default_factory=list)


class MCPServer:
    """
    MCP 服务端
    
    职责:
    1. 管理SSE连接
    2. 处理JSON-RPC请求
    3. 管理工具注册和调用
    4. 智能体间通信
    """
    
    def __init__(self, config_path: str = None, port: int = 3000):
        self.config_path = config_path
        self.port = port
        self.host = "0.0.0.0"
        self.tools: Dict[str, MCPTool] = {}
        self.agents: Dict[str, MCPAgent] = {}
        self.clients: List[web.WebSocketResponse] = []
        self.sse_clients: List[web.Response] = []
        self._request_id = 0
        self._app = None
        
        # 加载配置
        if config_path:
            self._load_config(config_path)
        else:
            self._load_default_config()
    
    def _load_config(self, path: str):
        """加载配置文件"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            
            self.port = config.get('port', self.port)
            self.host = config.get('host', '0.0.0.0')
            
            # 加载工具
            for tool_data in config.get('tools', []):
                tool = MCPTool(
                    name=tool_data['name'],
                    description=tool_data['description'],
                    parameters=tool_data.get('parameters', {})
                )
                self.tools[tool.name] = tool
            
            # 加载智能体
            for agent_data in config.get('agents', []):
                agent = MCPAgent(
                    id=agent_data['id'],
                    name=agent_data['name'],
                    department=agent_data.get('department', 'default'),
                    permissions=agent_data.get('permissions', [])
                )
                self.agents[agent.id] = agent
            
            logger.info(f"✅ Loaded config from {path}")
            logger.info(f"   Tools: {len(self.tools)}")
            logger.info(f"   Agents: {len(self.agents)}")
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        # 默认工具
        self.tools = {
            "file_system": MCPTool(
                name="file_system",
                description="文件系统操作",
                parameters={
                    "action": {"type": "string", "enum": ["read", "write", "list", "delete"]},
                    "path": {"type": "string"},
                    "content": {"type": "string", "optional": True}
                }
            ),
            "web_search": MCPTool(
                name="web_search",
                description="网络搜索",
                parameters={
                    "query": {"type": "string"},
                    "limit": {"type": "number", "default": 10}
                }
            ),
            "agent_communication": MCPTool(
                name="agent_communication",
                description="智能体间通信",
                parameters={
                    "target_agent": {"type": "string"},
                    "message": {"type": "object"},
                    "message_type": {"type": "string", "enum": ["request", "response", "broadcast"]}
                }
            ),
            "context_share": MCPTool(
                name="context_share",
                description="共享上下文",
                parameters={
                    "context_id": {"type": "string"},
                    "data": {"type": "object"},
                    "accessible_by": {"type": "array", "items": {"type": "string"}}
                }
            ),
            "task_collaboration": MCPTool(
                name="task_collaboration",
                description="协作任务",
                parameters={
                    "task_name": {"type": "string"},
                    "participants": {"type": "array", "items": {"type": "string"}},
                    "steps": {"type": "array"}
                }
            )
        }
        
        logger.info("✅ Loaded default config")
    
    def _get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        self._request_id += 1
        return self._request_id
    
    async def _handle_sse(self, request: web.Request) -> web.Response:
        """处理SSE连接"""
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        await response.prepare(request)
        
        # 发送初始连接确认
        await response.write(f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n".encode())
        
        self.sse_clients.append(response)
        logger.info(f"SSE client connected: {request.remote}")
        
        try:
            # 保持连接
            while True:
                await asyncio.sleep(30)
                await response.write(f":heartbeat\n\n".encode())
        except Exception as e:
            logger.info(f"SSE client disconnected: {e}")
        finally:
            if response in self.sse_clients:
                self.sse_clients.remove(response)
        
        return response
    
    async def _handle_message(self, request: web.Request) -> web.Response:
        """处理JSON-RPC消息"""
        try:
            body = await request.json()
            logger.debug(f"Received message: {body}")
            
            method = body.get('method')
            params = body.get('params', {})
            request_id = body.get('id')
            
            result = await self._process_method(method, params)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": body.get('id') if 'body' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })
    
    async def _process_method(self, method: str, params: Dict[str, Any]) -> Any:
        """处理方法调用"""
        if method == "initialize":
            return await self._handle_initialize(params)
        elif method == "tools/list":
            return await self._handle_tools_list(params)
        elif method == "tools/call":
            return await self._handle_tool_call(params)
        elif method == "agents/list":
            return await self._handle_agents_list(params)
        elif method == "agents/communicate":
            return await self._handle_agent_communication(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "CrabSwarm MCP Server",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            }
        }
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools = []
        for tool in self.tools.values():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters
            })
        return {"tools": tools}
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        
        # 模拟工具执行
        if tool_name == "file_system":
            return await self._execute_file_system(arguments)
        elif tool_name == "web_search":
            return await self._execute_web_search(arguments)
        elif tool_name == "agent_communication":
            return await self._execute_agent_communication(arguments)
        elif tool_name == "context_share":
            return await self._execute_context_share(arguments)
        elif tool_name == "task_collaboration":
            return await self._execute_task_collaboration(arguments)
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool {tool_name} executed with args: {json.dumps(arguments)}"
                    }
                ]
            }
    
    async def _execute_file_system(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行文件系统操作"""
        action = args.get('action')
        path = args.get('path', '')
        
        if action == 'read':
            return {
                "content": [{"type": "text", "text": f"Reading file: {path}"}],
                "isError": False
            }
        elif action == 'write':
            content = args.get('content', '')
            return {
                "content": [{"type": "text", "text": f"Writing to file: {path}"}],
                "isError": False
            }
        elif action == 'list':
            return {
                "content": [{"type": "text", "text": f"Listing directory: {path}"}],
                "isError": False
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown action: {action}"}],
                "isError": True
            }
    
    async def _execute_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行网络搜索"""
        query = args.get('query', '')
        limit = args.get('limit', 10)
        
        # 模拟搜索结果
        results = [
            {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i}"}
            for i in range(min(limit, 5))
        ]
        
        return {
            "content": [{"type": "text", "text": json.dumps(results, indent=2)}],
            "isError": False
        }
    
    async def _execute_agent_communication(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体通信"""
        target_agent = args.get('target_agent')
        message = args.get('message', {})
        message_type = args.get('message_type', 'request')
        
        return {
            "content": [{
                "type": "text",
                "text": f"Message sent to {target_agent}: {json.dumps(message)}"
            }],
            "isError": False
        }
    
    async def _execute_context_share(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行上下文共享"""
        context_id = args.get('context_id')
        data = args.get('data', {})
        
        return {
            "content": [{
                "type": "text",
                "text": f"Context '{context_id}' shared successfully"
            }],
            "isError": False
        }
    
    async def _execute_task_collaboration(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行协作任务"""
        task_name = args.get('task_name')
        participants = args.get('participants', [])
        
        return {
            "content": [{
                "type": "text",
                "text": f"Task '{task_name}' created with participants: {', '.join(participants)}"
            }],
            "isError": False
        }
    
    async def _handle_agents_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理智能体列表请求"""
        agents = []
        for agent in self.agents.values():
            agents.append({
                "id": agent.id,
                "name": agent.name,
                "department": agent.department,
                "permissions": agent.permissions
            })
        return {"agents": agents}
    
    async def _handle_agent_communication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理智能体通信"""
        source = params.get('source')
        target = params.get('target')
        message = params.get('message', {})
        
        return {
            "status": "delivered",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "tools": len(self.tools),
            "agents": len(self.agents),
            "sse_clients": len(self.sse_clients)
        })
    
    async def _handle_root(self, request: web.Request) -> web.Response:
        """根路径处理"""
        return web.json_response({
            "name": "CrabSwarm MCP Server",
            "version": "1.0.0",
            "endpoints": {
                "/sse": "SSE connection endpoint",
                "/message": "JSON-RPC message endpoint",
                "/health": "Health check"
            }
        })
    
    def setup_routes(self, app: web.Application):
        """设置路由"""
        app.router.add_get('/', self._handle_root)
        app.router.add_get('/sse', self._handle_sse)
        app.router.add_post('/message', self._handle_message)
        app.router.add_get('/health', self._handle_health)
    
    async def start(self):
        """启动服务器"""
        self._app = web.Application()
        self.setup_routes(self._app)
        
        runner = web.AppRunner(self._app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"✅ MCP Server started on http://{self.host}:{self.port}")
        logger.info(f"   SSE endpoint: http://{self.host}:{self.port}/sse")
        logger.info(f"   Message endpoint: http://{self.host}:{self.port}/message")
        logger.info(f"   Health check: http://{self.host}:{self.port}/health")
        
        # 保持运行
        while True:
            await asyncio.sleep(3600)


async def main():
    """主函数"""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    
    server = MCPServer(config_path=config_path, port=port)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
