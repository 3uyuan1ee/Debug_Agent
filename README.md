# AI Agent 软件项目缺陷自主检测与修复系统

基于AI Agent的软件工程缺陷检测与修复系统，能够自主或半自主地进行代码缺陷检测、分析和修复。本项目专注于构建一个智能的代码质量监控和问题诊断系统。

## 📋 项目概述

基于AI Agent的软件工程缺陷检测与修复系统，能够自主或半自主地进行代码缺陷检测、分析和修复。本项目专注于构建一个智能的代码质量监控和问题诊断系统。

### 核心功能

**🔍 智能代码分析**
- 静态代码分析：检测潜在的安全漏洞、代码异味和性能问题
- AI驱动的深度分析：基于ZhipuAI GLM-4.5模型的智能代码理解
- 多维度检测：安全性、性能、逻辑质量、文档完整性

**📊 质量评估与报告**
- 自动化质量评分：0-100分的综合质量评估
- 详细问题报告：按类型、严重程度、置信度分类
- 趋势分析：代码质量变化追踪和预测

**🤖 自主工作流**
- 目录级批量分析：支持整个项目的代码扫描
- 可扩展架构：预留工具集成和自定义工作流接口
- 报告导出：结构化分析结果输出

### 当前状态

**✅ 已实现功能**
- 基础静态分析（安全漏洞检测、TODO识别）
- AI分析接口集成（需要API密钥）
- 质量评分系统
- 详细报告生成

**🚧 待开发功能**
- 完整的测试套件
- 更多代码分析工具集成
- 可视化界面
- GitHub Actions工作流
- 高级错误处理机制

## 🗂️ 项目结构

```
Debug_Agent/
├── src/                        # 源代码
│   ├── agents/                # Agent实现
│   │   └── debug_agent.py     # 核心Agent类
│   ├── tools/                 # 工具集成（待实现）
│   ├── workflows/             # 工作流定义（待实现）
│   └── utils/                 # 工具函数（待实现）
├── tests/                     # 测试用例（待实现）
├── docs/                      # 项目文档
│   ├── DEVELOPMENT_PLAN.md    # 开发计划
│   ├── GIT_VERSION_CONTROL_GUIDE.md  # Git版本控制指南
│   ├── GIT_VERSION_EXPLAINED.md      # Git版本详解
│   ├── PROJECT_STRUCTURE.md         # 项目结构说明
│   └── advise.md              # 项目建议
├── experiments/               # 实验数据（待使用）
├── reports/                  # 分析报告（待使用）
├── .github/                  # GitHub配置（待配置）
├── .idea/                    # PyCharm IDE配置
├── requirements.txt          # Python依赖
├── CLAUDE.md                 # Claude Code开发指南
└── README.md                 # 项目说明文档
```

## 📊 开发环境配置

### 系统要求
- **操作系统**: macOS 10.15+, Windows 10+, Linux Ubuntu 20.04+
- **Python版本**: 3.8+
- **内存**: 最少8GB RAM，推荐16GB+
- **存储**: 最少2GB可用空间

### IDE推荐与配置

#### macOS用户 (推荐PyCharm)
```bash
# 安装PyCharm Professional
brew install --cask pycharm

# 或通过官网下载：https://www.jetbrains.com/pycharm/
```

**PyCharm配置步骤：**
1. **项目设置**
   - File → Open Project → 选择项目根目录
   - Configure → Python Interpreter → New environment
   - 选择Virtualenv环境

2. **代码风格配置**
   - Preferences → Editor → Code Style → Python
   - 设置Line length: 100
   - 启用PEP 8检查

3. **Git集成**
   - Preferences → Version Control → Git
   - 确保Git路径正确
   - 启用GitHub集成

#### Windows用户 (推荐VS Code)
```powershell
# 安装VS Code
winget install Microsoft.VisualStudioCode

# 或通过官网下载：https://code.visualstudio.com/
```

**VS Code配置步骤：**
1. **安装必要扩展**
   ```powershell
   code --install-extension ms-python.python
   code --install-extension ms-python.vscode-pylance
   code --install-extension ms-toolsai.jupyter
   code --install-extension github.vscode-pull-request-github
   ```

2. **Python环境配置**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - 选择或创建虚拟环境

3. **Git配置**
   - 安装Git for Windows：https://git-scm.com/download/win
   - 配置用户名和邮箱

### 环境配置步骤

#### 1. 克隆项目
```bash
# macOS/Linux
git clone git@github.com:3uyuan1ee/Debug_Agent.git
cd Debug_Agent

# Windows
git clone https://github.com/3uyuan1ee/Debug_Agent.git
cd Debug_Agent
```

#### 2. 创建虚拟环境
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

#### 3. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 可选：安装开发工具（代码分析、测试等）
pip install pytest pytest-cov flake8 pylint bandit radon safety
```

## 🔧 必要工具和依赖

### 核心依赖
- **Python 3.8+**: 主要开发语言
- **ZhipuAI**: AI模型接口
- **LangChain**: AI Agent框架
- **Git**: 版本控制

### 开发工具
- **静态代码分析**: bandit, flake8, pylint, safety
- **测试框架**: pytest, pytest-cov
- **代码质量**: radon, mypy
- **文档工具**: sphinx, mkdocs

### 可视化工具
- **matplotlib**: 图表生成
- **seaborn**: 统计图表
- **pandas**: 数据处理
- **numpy**: 数值计算

## 📚 必备知识技能

### 编程技能
- **Python高级编程**: 类、装饰器、上下文管理器
- **异步编程**: asyncio, async/await
- **网络编程**: HTTP API, RESTful设计
- **数据处理**: JSON, YAML, CSV格式

### AI/机器学习基础
- **机器学习基础**: 监督学习、无监督学习
- **自然语言处理**: 文本分析、语义理解
- **API使用**: OpenAI API, LangChain
- **提示工程**: Prompt设计和优化

### 软件工程
- **Git工作流**: 分支管理、合并策略
- **测试驱动开发**: 单元测试、集成测试
- **代码审查**: Code Review流程
- **CI/CD**: GitHub Actions工作流

### 系统设计
- **系统架构**: 微服务、分布式系统
- **数据库设计**: SQL、NoSQL
- **API设计**: RESTful API设计原则
- **安全性**: 身份验证、授权、数据加密

## 📅 开发计划和时间线

### 第一阶段：基础建设 (Week 1-2)
- [x] 项目结构搭建
- [x] Git仓库配置
- [x] 开发环境设置
- [x] 核心依赖安装
- [x] 基础文档编写

### 第二阶段：Agent开发 (Week 3-4)
- [x] Agent架构设计
- [x] 静态分析功能
- [x] AI分析集成（接口预留）
- [x] 基础配置系统
- [ ] 测试框架搭建

### 第三阶段：工具集成 (Week 5-6)
- [ ] 代码质量工具集成
- [ ] 报告生成系统
- [ ] 可视化界面
- [ ] 性能优化
- [ ] 错误处理机制

### 第四阶段：工作流开发 (Week 7-8)
- [ ] GitHub Actions修复
- [ ] 自动化测试流程
- [ ] 质量监控工作流
- [ ] 通知系统
- [ ] 部署流程

### 第五阶段：测试与优化 (Week 9-10)
- [ ] 全面测试
- [ ] 性能测试
- [ ] 用户体验优化
- [ ] 文档完善
- [ ] 项目总结

## 🚀 快速开始

### 1. 环境验证
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list | grep -E "(zhipuai|langchain)"

# 验证虚拟环境激活
which python
```

### 2. API密钥配置
```bash
# 设置ZhipuAI API密钥（可选，用于AI分析功能）
export ZHIPUAI_API_KEY="your_api_key_here"

# 验证API密钥设置
echo $ZHIPUAI_API_KEY
```

### 3. 运行示例
```bash
# 运行Debug Agent基础分析
python -m src.agents.debug_agent

# 或通过Python脚本测试
python -c "
from src.agents.debug_agent import DebugAgent
agent = DebugAgent()
test_code = 'def example(): pass'
results = agent.analyze_code(test_code, 'test.py')
print(f'发现 {len(results)} 个问题')
"

# 分析当前项目
python -c "
from src.agents.debug_agent import DebugAgent
agent = DebugAgent()
report = agent.analyze_directory('./src')
print(f'质量评分: {report.get(\"quality_score\", \"N/A\")}')
print(f'发现问题: {report.get(\"total_issues\", 0)} 个')
"
```

## 🤝 团队协作指南

### 代码贡献流程
1. Fork项目仓库
2. 创建功能分支
3. 开发和测试
4. 提交Pull Request
5. 代码审查
6. 合并到主分支

### 分支管理策略
- **main**: 主分支，保持稳定
- **develop**: 开发分支，集成新功能
- **feature/***: 功能分支，开发新特性
- **hotfix/***: 紧急修复分支

### 提交规范
```bash
# 功能开发
git commit -m "feat: 添加新的代码分析功能"

# Bug修复
git commit -m "fix: 修复AI分析模块的内存泄漏问题"

# 文档更新
git commit -m "docs: 更新开发环境配置文档"

# 测试相关
git commit -m "test: 添加Agent测试用例"
```

## 📈 项目监控和指标

### 质量指标
- 代码覆盖率 > 80%
- 静态分析问题数 < 10
- AI分析准确率 > 85%
- 响应时间 < 5秒

### 进度跟踪
- 使用GitHub Projects管理任务
- 每日站会同步进度
- 每周代码审查
- 每月项目回顾

## 🚨 常见问题和解决方案

### 环境配置问题
1. **Python版本不兼容**
   - 使用pyenv管理Python版本
   - 确保使用Python 3.8+

2. **依赖冲突**
   - 使用虚拟环境隔离
   - 检查requirements.txt版本约束

3. **API密钥问题**
   - 确保环境变量正确设置
   - 检查API密钥权限

### 开发问题
1. **Git冲突**
   - 定期同步主分支
   - 使用git rebase合并更改

2. **测试失败**
   - 检查测试环境配置
   - 查看详细错误日志

3. **性能问题**
   - 使用性能分析工具
   - 优化算法和数据结构

## 📞 支持和联系

### 技术支持
- **GitHub Issues**: https://github.com/3uyuan1ee/Debug_Agent/issues
- **邮件支持**: [your-email@example.com]
- **文档**: 查看 `/docs` 目录下的详细文档

### 社区资源
- **Python官方文档**: https://docs.python.org/
- **ZhipuAI文档**: https://open.bigmodel.cn/
- **LangChain文档**: https://python.langchain.com/
- **GitHub Actions文档**: https://docs.github.com/en/actions

---

## 📝 最后更新

- **版本**: 0.1.0-alpha
- **最后更新**: 2025年9月
- **维护者**: Debug Agent开发团队
- **开发状态**: 积极开发中