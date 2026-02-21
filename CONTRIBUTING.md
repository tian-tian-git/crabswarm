# 贡献指南

感谢你对 CrabSwarm 项目的兴趣！我们欢迎各种形式的贡献。

## 🚀 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议，请通过 GitHub Issues 提交：

1. 检查是否已有类似 issue
2. 使用对应的 issue 模板
3. 提供详细的复现步骤（对于 bug）
4. 说明期望的行为

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/yourusername/crabswarm.git
   cd crabswarm
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/issue-description
   ```

3. **安装开发依赖**
   ```bash
   pip install -e ".[dev]"
   ```

4. **编写代码**
   - 遵循 PEP 8 规范
   - 添加类型注解
   - 编写测试用例

5. **运行测试**
   ```bash
   pytest tests/ -v
   ```

6. **格式化代码**
   ```bash
   black crabswarm/ tests/
   flake8 crabswarm/ tests/
   ```

7. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**
   - 描述清楚更改内容
   - 关联相关 issue
   - 等待代码审查

## 📝 代码规范

### Python 代码风格

- 使用 [Black](https://github.com/psf/black) 格式化代码
- 最大行长度：88 字符
- 使用双引号字符串
- 添加类型注解

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加 MCP 工具支持

- 实现 MCP 客户端
- 支持工具发现和调用
- 添加单元测试
```

### 文档规范

- 使用中文或英文（保持一致）
- 代码示例必须可运行
- API 文档包含参数说明

## 🧪 测试要求

- 新功能必须包含测试
- 测试覆盖率不低于 80%
- 使用 pytest 框架

```python
# 示例测试
def test_agent_creation():
    agent = Agent(name="测试", role="测试角色")
    assert agent.name == "测试"
    assert agent.id is not None
```

## 📋 开发流程

1. 在 issue 中讨论大的改动
2. 保持 PR 小而专注
3. 一个 PR 解决一个问题
4. 及时响应审查意见

## 🏆 贡献者

感谢所有为 CrabSwarm 做出贡献的人！

## 📄 许可

通过提交代码，你同意你的贡献将在 MIT 许可证下发布。

---

如有问题，欢迎联系：crabswarm@example.com
