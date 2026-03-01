# CI/CD 配置说明

## 概述

本文档描述了 CrabSwarm 项目的 CI/CD 流水线配置。

## 工作流列表

### 1. ci.yml - 主 CI/CD 流水线

**触发条件:**
- Push 到 main/master/develop 分支
- Pull Request 到 main/master/develop 分支

**阶段:**

| 阶段 | 任务 | 说明 |
|------|------|------|
| lint | 代码质量检查 | flake8, black, isort |
| test | 通用测试 | Python 3.10/3.11/3.12 |
| test-crabswarm | CrabSwarm 专项测试 | 单元测试 + 示例运行 |
| build | 构建包 | 构建并检查包 |
| security | 安全扫描 | Bandit 安全检测 |
| deploy | 部署 | 仅 main/master 分支 |

### 2. release.yml - 发布工作流

**触发条件:**
- Push 标签 v*

**功能:**
- 创建 GitHub Release
- 构建并发布到 PyPI
- 上传发布资源

### 3. dependency-update.yml - 依赖更新检查

**触发条件:**
- 每周一早上8点 (定时任务)
- 手动触发

**功能:**
- 检查依赖更新
- 生成依赖报告

## 环境要求

- Python 3.10+
- Ubuntu Latest

## 密钥配置

需要在 GitHub Secrets 中配置:

| 密钥名 | 用途 |
|--------|------|
| PYPI_API_TOKEN | 发布到 PyPI |
| GITHUB_TOKEN | 自动提供 |

## 本地测试

```bash
# 安装依赖
cd crabswarm
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码检查
flake8 crabswarm/
black --check crabswarm/

# 构建包
python -m build
twine check dist/*
```

## 状态徽章

```markdown
[![CI/CD](https://github.com/tian-tian-git/crabswarm/actions/workflows/ci.yml/badge.svg)](https://github.com/tian-tian-git/crabswarm/actions/workflows/ci.yml)
[![Release](https://github.com/tian-tian-git/crabswarm/actions/workflows/release.yml/badge.svg)](https://github.com/tian-tian-git/crabswarm/actions/workflows/release.yml)
```
