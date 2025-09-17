# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于AI Agent的软件工程缺陷检测与修复系统，专注于代码质量分析和问题诊断。项目使用Python开发，集成了多种静态分析工具和AI分析功能。

## 常用命令

### 环境设置
```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 测试环境验证
python --version
```

### 运行和分析
```bash
# 运行Debug Agent分析
python -m src.agents.debug_agent

# 分析特定目录
python -c "
from src.agents.debug_agent import DebugAgent
agent = DebugAgent()
report = agent.analyze_directory('./src')
print(report)
"

# 测试API连接
python test_api_key.py  # 如果文件存在
```

### 代码质量检查
```bash
# 静态分析（如果工具已安装）
flake8 src/
pylint src/
bandit -r src/

# 代码复杂度分析
radon cc src/ -a -nb

# 安全检查
safety check
```

### 测试（需要先安装pytest）
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest tests/ -v

# 带覆盖率测试
pytest tests/ --cov=src --cov-report=html
```

## 项目架构

### 核心组件

1. **DebugAgent** (`src/agents/debug_agent.py:23`)
   - 主要的AI驱动的代码分析类
   - 支持静态分析和AI分析
   - 生成质量报告和评分

2. **AnalysisResult** (`src/agents/debug_agent.py:13`)
   - 分析结果数据结构
   - 包含文件路径、行号、问题类型、严重程度等信息

### 分析功能

- **静态分析** (`src/agents/debug_agent.py:80`)
  - 检测硬编码密码
  - 识别TODO/FIXME注释
  - 基于模式匹配的问题检测

- **AI分析** (`src/agents/debug_agent.py:113`)
  - 使用ZhipuAI GLM-4.5模型
  - 智能代码质量评估
  - 深度问题分析

### 报告生成

- **详细报告** (`src/agents/debug_agent.py:164`)
  - 按类型和严重程度分类
  - 包含置信度评分
  - 文件级统计信息

- **质量评分** (`src/agents/debug_agent.py:200`)
  - 0-100分评分系统
  - 基于问题严重程度加权计算

## 开发指南

### 依赖管理
- 使用`requirements.txt`管理依赖
- 主要依赖：`langchain`, `zhipuai`, `pytest`, `代码分析工具`

### 代码结构
- `src/agents/` - Agent实现
- `src/tools/` - 工具集成（待实现）
- `src/workflows/` - 工作流定义（待实现）
- `src/utils/` - 工具函数（待实现）
- `tests/` - 测试用例（待实现）
- `docs/` - 项目文档

### 环境配置
- 需要设置`ZHIPUAI_API_KEY`环境变量
- Python 3.8+ required
- 使用虚拟环境隔离依赖

### 注意事项
- 项目尚在开发阶段，许多功能待实现
- AI分析需要有效的ZhipuAI API密钥
- 测试框架需要先安装pytest
- 代码质量工具需要额外安装配置