# Git版本控制工具使用指导文档

## 目录
1. [Git简介](#git简介)
2. [核心概念](#核心概念)
3. [基础命令](#基础命令)
4. [分支管理](#分支管理)
5. [远程仓库操作](#远程仓库操作)
6. [高级功能](#高级功能)
7. [团队协作工作流](#团队协作工作流)
8. [常见问题解决](#常见问题解决)
9. [最佳实践](#最佳实践)

## Git简介

Git是一个分布式版本控制系统，由Linus Torvalds于2005年创建。它能够：
- 追踪文件变更历史
- 支持多人协作开发
- 提供分支管理功能
- 保证代码安全性

### 主要特点
- **分布式**：每个开发者都有完整的代码仓库副本
- **高效**：大部分操作在本地完成，速度快
- **安全**：使用SHA-1哈希确保数据完整性
- **灵活**：支持多种工作流程

## 核心概念

### 工作区（Working Directory）
当前正在编辑的文件目录

### 暂存区（Staging Area）
临时存放即将提交的修改

### 版本库（Repository）
Git管理的项目仓库，包含所有历史记录

### 分支（Branch）
独立的开发线，可以并行开发不同功能

### 提交（Commit）
项目的一个时间点快照

### 标签（Tag）
给特定提交起的有意义的名字

## 基础命令

### 初始化配置

```bash
# 设置用户名和邮箱
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱"

# 查看配置
git config --list

# 设置默认编辑器
git config --global core.editor "vim"

# 设置默认分支名称
git config --global init.defaultBranch main
```

### 仓库操作

```bash
# 初始化新仓库
git init

# 克隆现有仓库
git clone <repository_url>

# 查看仓库状态
git status

# 查看简化状态
git status -s
```

### 文件操作

```bash
# 添加文件到暂存区
git add <file_name>          # 添加指定文件
git add .                    # 添加当前目录所有文件
git add *.py                 # 添加所有Python文件
git add -A                   # 添加所有文件（包括删除的文件）

# 取消暂存文件
git reset HEAD <file_name>

# 查看文件差异
git diff                    # 工作区与暂存区差异
git diff --cached           # 暂存区与最新提交差异
git diff HEAD               # 工作区与最新提交差异

# 查看文件历史
git log <file_name>
git blame <file_name>       # 查看每行最后修改者

# 删除文件
git rm <file_name>          # 删除文件并暂存
git rm --cached <file_name> # 只从暂存区删除，保留工作区文件

# 重命名文件
git mv <old_name> <new_name>
```

### 提交操作

```bash
# 提交暂存区内容
git commit -m "提交说明"

# 详细提交说明（会打开编辑器）
git commit

# 修改最后一次提交
git commit --amend          # 修改提交说明
git commit --amend --no-edit  # 修改提交内容，保持说明不变

# 查看提交历史
git log
git log --oneline          # 简化显示
git log --graph            # 图形化显示分支
git log --stat             # 显示修改统计
git log -p                 # 显示修改内容

# 比较提交
git show <commit_hash>     # 查看指定提交详情
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- <file_name>    # 恢复文件到最新提交状态
git restore <file_name>        # Git 2.23+ 新命令

# 重置操作
git reset HEAD <file_name>     # 取消暂存
git reset --hard HEAD           # 重置到最新提交（危险！）
git reset --soft HEAD~1         # 软重置，保留修改
git reset --mixed HEAD~1        # 混合重置，取消暂存
```

## 分支管理

### 分支基础操作

```bash
# 查看分支
git branch                    # 查看本地分支
git branch -r                 # 查看远程分支
git branch -a                 # 查看所有分支

# 创建分支
git branch <branch_name>      # 创建新分支
git checkout -b <branch_name> # 创建并切换到新分支

# 切换分支
git checkout <branch_name>
git switch <branch_name>      # Git 2.23+ 新命令

# 删除分支
git branch -d <branch_name>   # 删除已合并分支
git branch -D <branch_name>   # 强制删除分支

# 重命名分支
git branch -m <old_name> <new_name>

# 查看分支合并状态
git branch --merged           # 查看已合并分支
git branch --no-merged        # 查看未合并分支
```

### 分支合并

```bash
# 合并分支
git merge <branch_name>       # 将指定分支合并到当前分支
git merge --no-ff <branch_name> # 总是创建合并提交

# 变基操作
git rebase <base_branch>      # 将当前分支变基到指定分支
git rebase -i <commit_hash>   # 交互式变基

# 解决冲突后的操作
git add <conflicted_file>     # 标记冲突已解决
git rebase --continue         # 继续变基
git rebase --abort            # 取消变基
```

## 远程仓库操作

### 远程仓库配置

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add <name> <url>

# 删除远程仓库
git remote remove <name>

# 重命名远程仓库
git remote rename <old_name> <new_name>

# 修改远程仓库URL
git remote set-url <name> <new_url>
```

### 推送和拉取

```bash
# 推送到远程仓库
git push <remote> <branch>       # 推送指定分支
git push -u <remote> <branch>    # 设置上游并推送
git push --all                   # 推送所有分支
git push --tags                  # 推送所有标签

# 从远程仓库拉取
git pull <remote> <branch>       # 拉取并合并
git pull --rebase <remote> <branch> # 拉取并变基

# 获取远程更新
git fetch <remote>               # 获取所有更新
git fetch <remote> <branch>      # 获取指定分支更新
```

### 远程分支管理

```bash
# 跟踪远程分支
git checkout -b <local_branch> <remote>/<remote_branch>
git checkout --track <remote>/<remote_branch>

# 删除远程分支
git push <remote> --delete <branch_name>

# 查看远程分支状态
git remote show <remote>
```

## 高级功能

### 标签管理

```bash
# 创建标签
git tag <tag_name>                    # 轻量标签
git tag -a <tag_name> -m "说明"       # 注释标签
git tag -a <tag_name> <commit_hash>   # 为指定提交创建标签

# 查看标签
git tag                              # 查看所有标签
git tag -l "pattern"                 # 查看匹配模式的标签
git show <tag_name>                   # 查看标签详情

# 删除标签
git tag -d <tag_name>                # 删除本地标签
git push <remote> --delete <tag_name> # 删除远程标签

# 推送标签
git push <remote> <tag_name>         # 推送指定标签
git push <remote> --tags             # 推送所有标签
```

### 储藏操作

```bash
# 储藏当前修改
git stash                            # 储藏当前修改
git stash save "说明"                # 储藏并添加说明
git stash -u                        # 储藏包括未跟踪文件

# 查看储藏
git stash list                       # 查看所有储藏
git stash show <stash_id>           # 查看指定储藏详情

# 应用储藏
git stash apply <stash_id>          # 应用储藏（保留储藏）
git stash pop <stash_id>            # 应用储藏（删除储藏）

# 删除储藏
git stash drop <stash_id>           # 删除指定储藏
git stash clear                     # 删除所有储藏
```

### 历史操作

```bash
# 查看历史
git log --pretty=format:"%h - %an, %ar : %s"  # 自定义格式
git log --since="2023-01-01"                # 查看指定日期后的提交
git log --until="2023-12-31"                # 查看指定日期前的提交
git log --author="作者名"                   # 查看指定作者的提交

# 搜索历史
git log -S "搜索内容"                       # 搜索内容变更
git log -G "正则表达式"                      # 搜索匹配的行

# 重写历史
git rebase -i <commit_hash>                 # 交互式重写历史
git filter-branch --tree-filter 'command'    # 过滤分支历史
```

## 团队协作工作流

### Git Flow工作流

```bash
# 初始化Git Flow
git flow init

# 功能开发
git flow feature start <feature_name>
git flow feature finish <feature_name>

# 发布版本
git flow release start <version>
git flow release finish <version>

# 修复问题
git flow hotfix start <fix_name>
git flow hotfix finish <fix_name>
```

### GitHub Flow工作流

```bash
# 1. 从main创建功能分支
git checkout main
git pull origin main
git checkout -b feature/<feature_name>

# 2. 开发并提交
git add .
git commit -m "Add feature"

# 3. 推送到远程
git push origin feature/<feature_name>

# 4. 创建Pull Request
# 在GitHub网站上创建PR

# 5. 代码审查和合并
# 审查通过后合并到main

# 6. 删除功能分支
git checkout main
git pull origin main
git branch -d feature/<feature_name>
git push origin --delete feature/<feature_name>
```

### Forking工作流

```bash
# 1. Fork原始仓库
# 在GitHub上Fork仓库

# 2. 克隆自己的Fork
git clone <your_fork_url>

# 3. 添加原始仓库为上游
git remote add upstream <original_url>

# 4. 创建功能分支
git checkout -b feature/<feature_name>

# 5. 开发并提交
git add .
git commit -m "Add feature"

# 6. 推送到自己的Fork
git push origin feature/<feature_name>

# 7. 创建Pull Request
# 在GitHub上创建PR到原始仓库

# 8. 同步上游更新
git fetch upstream
git merge upstream/main
```

## 常见问题解决

### 合并冲突解决

```bash
# 发生合并冲突时的标记
<<<<<<< HEAD
当前分支的代码
=======
要合并分支的代码
>>>>>>> <branch_name>

# 解决步骤：
# 1. 编辑文件，删除冲突标记
# 2. 保留需要的代码
# 3. 添加解决后的文件
git add <conflicted_file>
# 4. 继续合并操作
git merge --continue
```

### 撤销错误操作

```bash
# 撤销错误的合并
git reset --hard HEAD~1          # 撤销最后一次合并
git merge --abort               # 中止当前合并

# 撤销错误的提交
git revert <commit_hash>        # 创建新提交来撤销指定提交
git reset --hard <commit_hash>  # 重置到指定提交（危险！）

# 恢复删除的文件
git checkout <commit_hash> -- <file_name>
```

### 清理工作区

```bash
# 清理未跟踪文件
git clean -n                    # 查看将要删除的文件
git clean -f                    # 删除未跟踪文件
git clean -fd                   # 删除未跟踪文件和目录

# 重置工作区
git reset --hard HEAD           # 重置到最新提交
git clean -fd                   # 清理未跟踪文件
```

## 最佳实践

### 提交规范

```bash
# 提交消息格式
<类型>: <描述>

# 常用类型
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 重构
test: 测试相关
chore: 构建过程或辅助工具的变动

# 示例
feat: 添加用户登录功能
fix: 修复密码验证逻辑错误
docs: 更新README安装说明
```

### 分支命名规范

```bash
# 功能分支
feature/<feature_name>
feature/user-authentication

# 修复分支
bugfix/<bug_description>
bugfix/login-validation-error

# 发布分支
release/<version>
release/v1.0.0

# 热修复分支
hotfix/<fix_name>
hotfix/security-patch
```

### 代码审查清单

- [ ] 代码符合项目编码规范
- [ ] 所有测试用例通过
- [ ] 没有引入新的bug
- [ ] 提交消息清晰明确
- [ ] 分支命名符合规范
- [ ] 功能实现完整
- [ ] 性能影响已考虑
- [ ] 安全问题已检查

### 日常开发流程

```bash
# 1. 开始新功能前
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/<feature_name>

# 3. 开发过程中的提交
git add .
git commit -m "feat: 添加核心功能"
git add .
git commit -m "fix: 修复边界条件"

# 4. 推送分支
git push origin feature/<feature_name>

# 5. 创建Pull Request
# 在GitHub上创建PR

# 6. 根据反馈修改
git add .
git commit -m "refactor: 根据review反馈优化代码"
git push origin feature/<feature_name>

# 7. 合并后清理
git checkout main
git pull origin main
git branch -d feature/<feature_name>
```

### 安全性建议

1. **定期备份**：定期推送到远程仓库
2. **使用强密码**：GitHub账户使用强密码和双因素认证
3. **敏感信息**：不要提交密码、密钥等敏感信息
4. **定期更新**：保持Git客户端更新
5. **权限管理**：合理设置仓库权限

## 总结

Git是现代软件开发的必备工具，掌握Git的使用对于团队协作和项目管理至关重要。通过本指南，您应该能够：

- 理解Git的核心概念和工作原理
- 熟练使用常用命令进行版本控制
- 掌握分支管理和团队协作工作流
- 解决常见的Git问题和冲突
- 遵循最佳实践进行高效开发

建议在实际项目中多练习，结合具体场景加深理解。随着经验的积累，您会发现Git的强大功能能够显著提高开发效率和代码质量。