#!/usr/bin/env python3
"""
MCP智能体配置验证工具

验证智能体的mcp.yaml配置是否正确，确保与adapter兼容
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
import asyncio

# 添加crabswarm路径
sys.path.insert(0, '/root/.openclaw/workspace/crabswarm')

from crabswarm.mcp.adapter_sse import MCPAdapter


class MCPConfigValidator:
    """MCP配置验证器"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        self.mcp_server_url = mcp_server_url
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_agent_config(self, config_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        验证单个智能体的MCP配置
        
        Args:
            config_path: mcp.yaml文件路径
            
        Returns:
            (是否有效, 配置字典)
        """
        self.errors = []
        self.warnings = []
        
        print(f"\n{'='*60}")
        print(f"🔍 验证配置: {config_path}")
        print('='*60)
        
        # 1. 检查文件是否存在
        if not os.path.exists(config_path):
            self.errors.append(f"配置文件不存在: {config_path}")
            return False, {}
        
        # 2. 解析YAML
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML解析错误: {e}")
            return False, {}
        except Exception as e:
            self.errors.append(f"读取文件错误: {e}")
            return False, {}
        
        # 3. 检查mcp根节点
        if 'mcp' not in config:
            self.errors.append("缺少 'mcp' 根节点")
            return False, config
        
        mcp_config = config['mcp']
        
        # 4. 验证必需字段
        required_fields = ['enabled', 'server_url', 'agent_id']
        for field in required_fields:
            if field not in mcp_config:
                self.errors.append(f"缺少必需字段: mcp.{field}")
        
        # 5. 验证enabled字段
        if mcp_config.get('enabled') not in [True, False]:
            self.warnings.append("mcp.enabled 应该是布尔值")
        
        # 6. 验证server_url格式
        server_url = mcp_config.get('server_url', '')
        if not server_url.startswith(('http://', 'https://', 'ws://', 'wss://')):
            self.warnings.append(f"server_url格式可能不正确: {server_url}")
        
        # 7. 验证tools字段
        tools = mcp_config.get('tools', [])
        if not isinstance(tools, list):
            self.errors.append("mcp.tools 应该是列表")
        elif len(tools) == 0:
            self.warnings.append("mcp.tools 为空列表")
        
        # 8. 验证peers字段
        peers = mcp_config.get('peers', [])
        if not isinstance(peers, list):
            self.errors.append("mcp.peers 应该是列表")
        
        # 9. 验证permissions字段
        permissions = mcp_config.get('permissions', {})
        if not isinstance(permissions, dict):
            self.errors.append("mcp.permissions 应该是字典")
        
        # 10. 打印验证结果
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 配置验证通过!")
        elif not self.errors:
            print("\n✅ 配置有效，但有警告")
        
        # 打印配置摘要
        print(f"\n📋 配置摘要:")
        print(f"   Agent ID: {mcp_config.get('agent_id', 'N/A')}")
        print(f"   Enabled: {mcp_config.get('enabled', 'N/A')}")
        print(f"   Server URL: {mcp_config.get('server_url', 'N/A')}")
        print(f"   Tools: {len(tools)} 个")
        print(f"   Peers: {len(peers)} 个")
        
        return len(self.errors) == 0, config
    
    async def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试智能体配置是否可以连接到MCP服务器
        
        Args:
            config: MCP配置字典
            
        Returns:
            连接是否成功
        """
        mcp_config = config.get('mcp', {})
        server_url = mcp_config.get('server_url', self.mcp_server_url)
        agent_id = mcp_config.get('agent_id', 'unknown')
        
        print(f"\n🔄 测试连接 (Agent: {agent_id})...")
        
        try:
            adapter_config = {
                "server_url": server_url,
                "timeout": 30,
                "max_retries": 2,
                "_test_mode": True
            }
            
            adapter = MCPAdapter(adapter_config)
            connected = await adapter.connect()
            
            if connected:
                print(f"   ✅ 连接成功")
                
                # 测试获取工具列表
                tools = await adapter.list_tools()
                print(f"   ✅ 获取工具列表成功 ({len(tools)} 个工具)")
                
                # 测试调用一个简单工具
                try:
                    result = await adapter.call_tool("web_search", {"query": "test", "limit": 1})
                    print(f"   ✅ 工具调用成功")
                except Exception as e:
                    print(f"   ⚠️ 工具调用警告: {e}")
                
                await adapter.close()
                return True
            else:
                print(f"   ❌ 连接失败")
                return False
                
        except Exception as e:
            print(f"   ❌ 连接错误: {e}")
            return False
    
    def validate_all_agents(self, agents_dir: str) -> Dict[str, Any]:
        """
        验证所有智能体的配置
        
        Args:
            agents_dir: 智能体根目录
            
        Returns:
            验证结果统计
        """
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'agents': []
        }
        
        agents_path = Path(agents_dir)
        
        # 查找所有mcp.yaml文件
        for mcp_file in agents_path.rglob('mcp.yaml'):
            results['total'] += 1
            
            valid, config = self.validate_agent_config(str(mcp_file))
            
            agent_info = {
                'path': str(mcp_file),
                'valid': valid,
                'config': config
            }
            
            if valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
            
            results['agents'].append(agent_info)
        
        return results


async def main():
    """主函数"""
    validator = MCPConfigValidator()
    
    # 验证特定智能体
    test_agents = [
        '/root/.openclaw/workspace/agents/learning/active/github-learner/mcp.yaml',
        '/root/.openclaw/workspace/agents/news/active/news-collector/mcp.yaml',
        '/root/.openclaw/workspace/agents/report/active/report-master/mcp.yaml',
        '/root/.openclaw/workspace/agents/engineering/active/architect-agent/mcp.yaml',
        '/root/.openclaw/workspace/agents/engineering/active/backend-agent/mcp.yaml',
    ]
    
    print("="*60)
    print("🦀 CrabSwarm MCP 智能体配置验证")
    print("="*60)
    
    all_valid = True
    for agent_path in test_agents:
        if os.path.exists(agent_path):
            valid, config = validator.validate_agent_config(agent_path)
            if valid:
                # 测试连接
                connected = await validator.test_connection(config)
                if not connected:
                    all_valid = False
            else:
                all_valid = False
        else:
            print(f"\n⚠️ 文件不存在: {agent_path}")
            all_valid = False
    
    # 验证所有智能体
    print("\n" + "="*60)
    print("📊 验证所有智能体配置")
    print("="*60)
    
    results = validator.validate_all_agents('/root/.openclaw/workspace/agents')
    
    print(f"\n总计: {results['total']} 个智能体")
    print(f"✅ 有效: {results['valid']} 个")
    print(f"❌ 无效: {results['invalid']} 个")
    
    # 打印所有智能体列表
    print("\n📋 智能体列表:")
    for agent in results['agents']:
        status = "✅" if agent['valid'] else "❌"
        agent_id = agent['config'].get('mcp', {}).get('agent_id', 'unknown')
        print(f"   {status} {agent_id} ({agent['path']})")
    
    print("\n" + "="*60)
    if all_valid and results['invalid'] == 0:
        print("🎉 所有配置验证通过!")
        return 0
    else:
        print("⚠️ 部分配置存在问题，请检查")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
