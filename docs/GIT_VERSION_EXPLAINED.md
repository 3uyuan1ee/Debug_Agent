# Git版本控制详解

## 📋 Git提交记录

### 查看提交历史

```bash
# 查看详细提交历史
git log

# 查看简洁的提交历史（单行显示）
git log --oneline

# 查看最近N次提交
git log --oneline -5

# 查看图形化的提交历史（包含分支）
git log --graph --oneline --decorate --all

# 查看某个文件的修改历史
git log --follow README.md

# 查看每次提交的统计信息
git log --stat
```

### 实际例子
```bash
$ git log --oneline
f10e445 docs: 添加项目结构说明文档
99b1a87 refactor: 清理项目结构，删除测试脚本，添加开发计划文档
45ece29 禁用workflow以避免YAML语法错误
da9f7b9 修复workflow YAML语法错误
b282324 添加Agent质量测试和工作流状态检查
d50027b 添加Debug Agent核心实现和API测试
5770404 重新设计检测系统 - 移除自动修复，专注检测和分析
cd97df2 Add GitHub Actions workflows for AI Agent system
ae6d0b9 Add Git version control guide
d786fc5 Initial project setup: Create repository structure and basic configuration
```

每个提交都有一个唯一的哈希值（如 `f10e445`），这是版本的唯一标识。

## 🕰️ 版本回退

### 查看版本差异
```bash
# 查看两个版本之间的差异
git diff f10e445 99b1a87

# 查看当前版本与某个版本的差异
git diff f10e445

# 查看某个版本的文件内容
git show f10e445:README.md

# 查看某个提交的详细信息
git show f10e445
```

### 回退到历史版本

#### 1. 硬回退（删除后续提交）
```bash
# 回退到指定版本（后续提交会被删除）
git reset --hard f10e445

# 回退到上一个版本
git reset --hard HEAD~1

# 回退到上上个版本
git reset --hard HEAD~2
```

#### 2. 软回退（保留修改）
```bash
# 回退到指定版本，但保留修改
git reset --soft f10e445

# 回退到指定版本，保留修改但不暂存
git reset --mixed f10e445
```

#### 3. 撤销某个提交
```bash
# 撤销某个提交（但会创建新的提交）
git revert f10e445
```

### 查看被删除的提交
```bash
# 查看所有操作历史（包括被删除的提交）
git reflog

# 示例输出：
f10e445 (HEAD -> main) HEAD@{0}: commit: docs: 添加项目结构说明文档
99b1a87 HEAD@{1}: commit: refactor: 清理项目结构，删除测试脚本，添加开发计划文档
45ece29 HEAD@{2}: commit: 禁用workflow以避免YAML语法错误
```

## 🌿 分支的概念和用途

### 什么是分支？
分支是Git的核心功能，允许你在独立的线上开发，不影响主代码。

### 分支的实际应用场景

#### 场景1：开发新功能
```bash
# 创建新分支开发功能
git checkout -b feature/new-analysis

# 在新分支上开发...
git add .
git commit -m "feat: 添加新的代码分析功能"

# 完成后合并回主分支
git checkout main
git merge feature/new-analysis

# 删除分支
git branch -d feature/new-analysis
```

#### 场景2：修复紧急bug
```bash
# 从稳定版本创建hotfix分支
git checkout -b hotfix/fix-security d786fc5

# 修复bug...
git add .
git commit -m "fix: 修复安全漏洞"

# 合并到主分支
git checkout main
git merge hotfix/fix-security
```

#### 场景3：实验性开发
```bash
# 创建实验分支
git checkout -b experiment/ai-model

# 进行实验性开发...
# 如果实验失败，直接删除分支
git checkout main
git branch -D experiment/ai-model
```

### 分支管理最佳实践

#### 1. 主分支策略
```bash
main          # 主分支，始终保持可发布状态
develop       # 开发分支，集成最新功能
feature/*     # 功能分支
hotfix/*      # 紧急修复分支
release/*     # 发布准备分支
```

#### 2. 分支操作命令
```bash
# 查看所有分支
git branch -a

# 创建新分支
git branch feature/new-feature

# 切换到分支
git checkout feature/new-feature

# 创建并切换到新分支
git checkout -b feature/new-feature

# 删除本地分支
git branch -d feature/new-feature

# 删除远程分支
git push origin --delete feature/new-feature

# 查看分支合并情况
git branch --merged
git branch --no-merged
```

## 🔄 实际工作流程示例

### 1. 日常开发流程
```bash
# 1. 同步最新代码
git pull origin main

# 2. 创建功能分支
git checkout -b feature/user-authentication

# 3. 开发功能
# ... 编写代码 ...

# 4. 提交更改
git add .
git commit -m "feat: 实现用户认证功能"

# 5. 推送到远程
git push origin feature/user-authentication

# 6. 创建Pull Request
# 在GitHub上创建PR，请求合并到main

# 7. 代码审查和合并
# 等待团队成员审查，通过后合并

# 8. 删除分支
git checkout main
git branch -d feature/user-authentication
```

### 2. 团队协作流程
```bash
# 开发者A的工作
git checkout -b feature/payment-gateway
# ... 开发支付网关功能 ...
git push origin feature/payment-gateway

# 开发者B的工作
git checkout -b feature/user-profile
# ... 开发用户资料功能 ...
git push origin feature/user-profile

# 同时进行，互不干扰
```

### 3. 版本发布流程
```bash
# 1. 创建发布分支
git checkout -b release/v1.0.0

# 2. 测试和修复
# ... 测试，修复bug ...

# 3. 合并到主分支
git checkout main
git merge release/v1.0.0

# 4. 创建标签
git tag -a v1.0.0 -m "Version 1.0.0"

# 5. 推送标签
git push origin v1.0.0
```

## 🏷️ 标签管理

### 创建标签
```bash
# 创建轻量标签
git tag v1.0.0

# 创建带注释的标签
git tag -a v1.0.0 -m "Version 1.0.0 Release"

# 查看所有标签
git tag

# 查看标签详情
git show v1.0.0

# 推送标签到远程
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

## 🎯 实际应用建议

### 1. 提交规范
```bash
# 功能开发
git commit -m "feat: 添加用户认证功能"

# Bug修复
git commit -m "fix: 修复登录页面的样式问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 重构
git commit -m "refactor: 重构用户管理模块"

# 测试
git commit -m "test: 添加用户认证测试用例"
```

### 2. 分支命名规范
```bash
feature/user-authentication    # 功能分支
bugfix/login-issue            # Bug修复
hotfix/security-patch         # 紧急修复
release/v1.0.0               # 发布分支
experiment/ai-integration    # 实验分支
```

### 3. 定期清理
```bash
# 查看已合并的分支
git branch --merged

# 删除已合并的分支
git branch -d merged-feature

# 清理远程分支
git remote prune origin
```

## 📊 分支策略对比

| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Git Flow** | 结构清晰，发布管理规范 | 复杂，分支较多 | 大型项目，严格版本控制 |
| **GitHub Flow** | 简单，易于理解 | 发布管理较简单 | 中小型项目，快速迭代 |
| **GitLab Flow** | 兼顾简单和规范 | 需要环境管理 | 有环境区分的项目 |
| **Trunk Based** | 快速，减少合并冲突 | 需要自动化测试支持 | 高频发布项目 |

## 🚨 常见问题解决

### 1. 合并冲突
```bash
# 解决冲突步骤
git merge feature/branch
# 出现冲突后，手动编辑冲突文件
# 标记冲突已解决
git add conflicted-file.py
git commit
```

### 2. 误删提交恢复
```bash
# 使用reflog找回
git reflog
# 找到误删的提交哈希
git reset --hard f10e445
```

### 3. 分支丢失
```bash
# 找回丢失的分支
git reflog
# 创建新分支指向丢失的提交
git branch lost-branch f10e445
```

---

**总结**：Git的版本控制和分支系统是现代软件开发的基石。通过合理使用提交历史、版本回退和分支管理，可以实现高效的团队协作和版本控制。