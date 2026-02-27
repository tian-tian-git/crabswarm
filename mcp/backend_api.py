#!/usr/bin/env python3
"""
MCP Backend API - 前后端联调服务

提供REST API供前端调用，桥接MCP服务端
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
from aiohttp import web

# 添加crabswarm路径
import sys
sys.path.insert(0, '/root/.openclaw/workspace/crabswarm')

from crabswarm.mcp.adapter_sse import MCPAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPBackendAPI:
    """
    MCP后端API服务
    
    提供REST API端点:
    - GET /api/health - 健康检查
    - POST /api/connect - 连接到MCP服务器
    - GET /api/tools - 获取工具列表
    - POST /api/tools/call - 调用工具
    - GET /api/status - 获取连接状态
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000", port: int = 8080):
        self.mcp_server_url = mcp_server_url
        self.port = port
        self.host = "0.0.0.0"
        self.adapter: Optional[MCPAdapter] = None
        self._app = None
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "mcp_connected": self.adapter is not None and self.adapter.is_connected,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def _handle_connect(self, request: web.Request) -> web.Response:
        """连接到MCP服务器"""
        try:
            body = await request.json()
            server_url = body.get('server_url', self.mcp_server_url)
            
            # 关闭现有连接
            if self.adapter:
                await self.adapter.close()
            
            # 创建新连接
            config = {
                "server_url": server_url,
                "timeout": 30,
                "max_retries": 3,
                "_test_mode": True  # 不使用SSE循环，使用HTTP请求
            }
            
            self.adapter = MCPAdapter(config)
            connected = await self.adapter.connect()
            
            if connected:
                return web.json_response({
                    "success": True,
                    "message": "Connected to MCP server",
                    "server_info": self.adapter.state.server_info
                })
            else:
                return web.json_response({
                    "success": False,
                    "message": "Failed to connect to MCP server"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return web.json_response({
                "success": False,
                "message": str(e)
            }, status=500)
    
    async def _handle_disconnect(self, request: web.Request) -> web.Response:
        """断开连接"""
        try:
            if self.adapter:
                await self.adapter.close()
                self.adapter = None
            
            return web.json_response({
                "success": True,
                "message": "Disconnected from MCP server"
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "message": str(e)
            }, status=500)
    
    async def _handle_tools_list(self, request: web.Request) -> web.Response:
        """获取工具列表"""
        try:
            if not self.adapter or not self.adapter.is_connected:
                # 尝试自动连接
                if not self.adapter:
                    config = {
                        "server_url": self.mcp_server_url,
                        "timeout": 30,
                        "max_retries": 2,
                        "_test_mode": True
                    }
                    self.adapter = MCPAdapter(config)
                
                connected = await self.adapter.connect()
                if not connected:
                    return web.json_response({
                        "success": False,
                        "message": "Not connected to MCP server"
                    }, status=503)
            
            tools = await self.adapter.list_tools()
            
            return web.json_response({
                "success": True,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    }
                    for tool in tools
                ]
            })
            
        except Exception as e:
            logger.error(f"Tools list error: {e}")
            return web.json_response({
                "success": False,
                "message": str(e)
            }, status=500)
    
    async def _handle_tool_call(self, request: web.Request) -> web.Response:
        """调用工具"""
        try:
            body = await request.json()
            tool_name = body.get('tool_name')
            params = body.get('params', {})
            
            if not tool_name:
                return web.json_response({
                    "success": False,
                    "message": "tool_name is required"
                }, status=400)
            
            if not self.adapter or not self.adapter.is_connected:
                return web.json_response({
                    "success": False,
                    "message": "Not connected to MCP server"
                }, status=503)
            
            result = await self.adapter.call_tool(tool_name, params)
            
            return web.json_response({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Tool call error: {e}")
            return web.json_response({
                "success": False,
                "message": str(e)
            }, status=500)
    
    async def _handle_status(self, request: web.Request) -> web.Response:
        """获取连接状态"""
        return web.json_response({
            "connected": self.adapter is not None and self.adapter.is_connected,
            "server_url": self.mcp_server_url,
            "server_info": self.adapter.state.server_info if self.adapter else None
        })
    
    async def _handle_root(self, request: web.Request) -> web.Response:
        """根路径"""
        return web.json_response({
            "name": "MCP Backend API",
            "version": "1.0.0",
            "endpoints": {
                "/api/health": "Health check",
                "/api/connect": "Connect to MCP server (POST)",
                "/api/disconnect": "Disconnect from MCP server (POST)",
                "/api/tools": "Get tools list (GET)",
                "/api/tools/call": "Call a tool (POST)",
                "/api/status": "Get connection status (GET)"
            }
        })
    
    def setup_routes(self, app: web.Application):
        """设置路由"""
        # CORS中间件
        async def cors_middleware(app, handler):
            async def middleware_handler(request):
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            return middleware_handler
        
        app.middlewares.append(cors_middleware)
        
        app.router.add_get('/', self._handle_root)
        app.router.add_get('/api/health', self._handle_health)
        app.router.add_post('/api/connect', self._handle_connect)
        app.router.add_post('/api/disconnect', self._handle_disconnect)
        app.router.add_get('/api/tools', self._handle_tools_list)
        app.router.add_post('/api/tools/call', self._handle_tool_call)
        app.router.add_get('/api/status', self._handle_status)
        
        # OPTIONS处理
        async def handle_options(request):
            return web.Response(headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            })
        
        app.router.add_options('/{path:.*}', handle_options)
    
    async def start(self):
        """启动API服务"""
        self._app = web.Application()
        self.setup_routes(self._app)
        
        runner = web.AppRunner(self._app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"✅ MCP Backend API started on http://{self.host}:{self.port}")
        logger.info(f"   API documentation: http://{self.host}:{self.port}/")
        
        # 保持运行
        while True:
            await asyncio.sleep(3600)


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Backend API')
    parser.add_argument('--mcp-server', default='http://localhost:3000', help='MCP server URL')
    parser.add_argument('--port', type=int, default=8080, help='API server port')
    args = parser.parse_args()
    
    api = MCPBackendAPI(mcp_server_url=args.mcp_server, port=args.port)
    await api.start()


if __name__ == "__main__":
    asyncio.run(main())
