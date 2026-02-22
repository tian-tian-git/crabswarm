# CrabSwarm CI/CD 配置文档

**配置时间**: 2026-02-22 19:15  
**配置者**: devops-agent (项目工程部)  
**任务ID**: TASK-006-CI/CD  

---

## 概述

本 CI/CD 配置为 CrabSwarm 多智能体协作框架提供完整的自动化测试、代码质量检查和发布流程。

## 工作流清单

### 1. CI 工作流 (`ci.yml`)

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 分支

**任务**:

| 任务 | 说明 | 依赖 |
|------|------|------|
| test | 多版本Python测试 (3.10/3.11/3.12) | - |
| build | 构建包并验证 | test |
| examples | 运行示例代码验证 | test |
| test-summary | 生成测试摘要报告 | test |

**测试覆盖**:
- ✅ 核心功能测试 (`test_core.py`)
- ✅ 边界条件测试 (`test_edge_cases.py`)
- ✅ 集成测试 (`test_integration.py`)
- ✅ LLM模块测试 (`test_llm.py`)

### 2. PR 检查工作流 (`pr-check.yml`)

**触发条件**:
- Pull Request 创建、更新、重新打开

**检查项**:
- 代码格式化 (Black)
- 代码质量检查 (flake8)
- 快速测试运行
- PR 大小检查
- 测试覆盖提醒

### 3. 安全扫描工作流 (`security.yml`)

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 分支
- 每周一 9:00 AM (定时)

**扫描项**:
- 依赖安全扫描 (Safety)
- 代码安全扫描 (Bandit)

### 4. 测试报告工作流 (`test-report.yml`)

**触发条件**:
- CI 工作流完成后

**功能**:
- 生成 HTML 测试报告
- 生成 JSON 测试报告
- PR 评论自动发布测试结果

### 5. 发布工作流 (`release.yml`)

**触发条件**:
- 推送标签 `v*`

**功能**:
- 构建并发布到 PyPI
- 创建 GitHub Release
- 自动生成发布说明

---

## 测试统计

| 测试文件 | 测试数量 | 类型 |
|----------|----------|------|
| `test_core.py` | 55 | 单元测试 |
| `test_edge_cases.py` | 47 | 边界测试 |
| `test_integration.py` | 14 | 集成测试 |
| `test_llm.py` | 19 | LLM模块测试 |
| `test_client.py` | 20 | 客户端测试 |
| **总计** | **155** | - |

---

## 使用方法

### 本地运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_core.py -v
pytest tests/test_edge_cases.py -v
pytest tests/test_integration.py -v

# 生成覆盖率报告
pytest tests/ --cov=crabswarm --cov-report=html

# 生成测试报告
pytest tests/ --html=report.html --self-contained-html
```

### 本地代码检查

```bash
# 格式化代码
black crabswarm/ tests/

# 代码质量检查
flake8 crabswarm/ --count --select=E9,F63,F7,F82 --show-source --statistics

# 安全扫描
bandit -r crabswarm/
safety check
```

---

## 配置详情

### 环境要求

- Python 3.10+
- GitHub Actions Runner (Ubuntu Latest)

### Secrets 配置

需要在 GitHub 仓库设置以下 Secrets:

| Secret | 用途 | 必需 |
|--------|------|------|
| `PYPI_API_TOKEN` | 发布到 PyPI | 仅发布时 |
| `CODECOV_TOKEN` | 覆盖率上传 | 可选 |

### 依赖管理

**生产依赖** (setup.py):
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

**开发依赖**:
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-html >= 3.2.0
- pytest-json-report >= 1.5.0
- black >= 23.0.0
- flake8 >= 6.0.0
- safety >= 2.3.0
- bandit >= 1.7.0

**LLM依赖** (可选):
- openai >= 1.0.0
- anthropic >= 0.8.0

---

## 状态徽章

将以下代码添加到 README.md 以显示 CI 状态:

```markdown
[![CI](https://github.com/yourusername/crabswarm/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/crabswarm/actions/workflows/ci.yml)
[![Security Scan](https://github.com/yourusername/crabswarm/actions/workflows/security.yml/badge.svg)](https://github.com/yourusername/crabswarm/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yourusername/crabswarm/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/crabswarm)
```

---

## 故障排除

### 常见问题

1. **测试失败**: 检查 Python 版本是否兼容
2. **覆盖率下降**: 确保新增代码有对应的测试
3. **安全扫描警告**: 及时更新依赖包
4. **构建失败**: 检查 setup.py 配置是否正确

### 联系支持

如有 CI/CD 相关问题，请联系:
- **部门**: 项目工程部
- **负责人**: devops-agent
- **任务**: TASK-006-CI/CD

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-02-22 | v1.0 | 初始配置，支持多版本Python测试、代码质量检查、安全扫描 |

---

*文档版本: v1.0*  
*最后更新: 2026-02-22*
