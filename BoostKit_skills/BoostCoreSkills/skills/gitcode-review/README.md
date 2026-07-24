# GitCode Review Skill配置指南

本指南将帮助你在 Claude Code 上配置 GitCode MCP 服务器，以便使用 GitCode Review Skill。如需在其他ai工具上配置，请参阅[INSTALLATION_GUIDE.md](https://gitcode.com/boostkit/skills/tree/master/skills/gitcode-review/docs/INSTALLATION_GUIDE.md)，在trae/trae CN上配置可以参阅图文指导[TRAE_SETUP.md](https://gitcode.com/boostkit/skills/tree/master/skills/gitcode-review/docs/TRAE_SETUP.md)

## ✨ 功能特性

- ✅ 自动获取 PR 列表
- ✅ 分析代码变更（diff）
- ✅ 生成专业的中文审查报告
- ✅ 可选提交评论到 PR
- ✅ 支持多种触发方式
- ✅ 遵循代码审查最佳实践

## 前置要求

1. **AI编码工具**：确保已安装 Claude Code或Codex cli, Trae
2. **Python 环境**：Python 3.8 或更高版本
3. **GitCode 账号**：需要有 GitCode 账号和访问令牌

## 步骤 1：获取 GitCode 访问令牌

1. 登录 [GitCode](https://gitcode.com)
2. 进入 **设置** → **访问令牌** 
3. 点击 **生成新令牌**
4. 设置令牌信息：
   - **名称**：例如 "Claude Code MCP"
   - **过期时间**：根据需要选择
   - **权限范围**：至少选择以下权限
     - `api` - 完整的 API 访问权限
     - `read_repository` - 读取仓库
     - `write_repository` - 写入仓库（如需提交评论）
5. 点击 **创建令牌**
6. **重要**：复制生成的令牌并妥善保存（令牌只显示一次）

## 步骤 2：安装 GitCode MCP 服务器

### 从源码安装gitcode_mcp_server

```bash
# 克隆仓库
git clone https://gitcode.com/gitcode-ai/gitcode_mcp_server.git

# 安装依赖
pip install -r requirements.txt

#源码安装
cd gitcode_mcp_server
pip install .
```
安装参考：https://gitcode.com/gitcode-ai/gitcode_mcp_server

## 步骤 3：配置 Claude Code

使用 Claude Code 的 MCP 配置命令添加 GitCode 服务器：

```bash
claude mcp add gitcode -e GITCODE_TOKEN="你的访问令牌" -- python -m gitcode_mcp
```

**参数说明**：
- `gitcode` - MCP 服务器名称
- `-e GITCODE_TOKEN="..."` - 设置环境变量（替换为你的实际令牌）
- `-- python -m gitcode_mcp` - 启动服务器的命令

### 使用代理（可选）

如果需要通过代理访问 GitCode：

```bash
claude mcp add gitcode \
  -e GITCODE_TOKEN="你的访问令牌" \
  -e HTTP_PROXY="http://localhost:8080" \
  -e HTTPS_PROXY="http://localhost:8080" \
  -- python -m gitcode_mcp
```

## 步骤 4：验证配置

### 4.1 检查服务器列表

```bash
claude mcp list
```

你应该能看到 `gitcode` 服务器已配置。

### 4.2 测试服务器

启动 Claude Code 并尝试以下命令：

```
列出我的 GitCode 仓库
```

或者直接测试 MCP 工具：

```
使用 mcp__gitcode__list_repositories 列出仓库
```

如果配置正确，你应该能看到你的 GitCode 仓库列表。

## 步骤 5：安装 GitCode Review Skill

### 5.1 复制 Skill 文件

将 `gitcode-review.skill` 文件复制到 Claude Code 的 skills 目录：

**Windows**：
```bash
copy gitcode-review.skill %USERPROFILE%\.claude\skills\
```

**macOS/Linux**：
```bash
cp gitcode-review.skill ~/.claude/skills/
```

### 5.2 或使用 Skills CLI 安装

```bash
npx skills add https://gitcode.com/CarbonadoRain/gitcode-review.git -g -y
```

## 使用 GitCode Review Skill

配置完成后，你可以在 Claude Code 中使用以下命令：

### 审查 PR

```bash
/review              # 列出所有打开的 PR
/review 2            # 审查 PR #2
```

### 或使用自然语言

```
帮我审查 https://gitcode.com/owner/repo 的 PR #2
```

```
查看最近的 Pull Request 并进行代码审查
```

## 故障排除

### 问题 1：命令参数顺序错误

**错误信息**：
```
Invalid environment variable format: gitcode
```

**解决方案**：
确保服务器名称在环境变量选项之前：

```bash
# 正确
claude mcp add gitcode -e GITCODE_TOKEN="..." -- python -m gitcode_mcp

# 错误
claude mcp add -e GITCODE_TOKEN="..." gitcode -- python -m gitcode_mcp
```

### 问题 2：服务器启动失败

**错误信息**：
```
GitCode令牌未提供
```

**解决方案**：
1. 检查 GITCODE_TOKEN 是否正确设置
2. 确认令牌用引号包裹
3. 验证令牌是否有效（未过期）

### 问题 3：无法访问仓库

**错误信息**：
```
404, token not found
```

**解决方案**：
1. 确认令牌有正确的权限范围
2. 检查仓库是否存在且有访问权限
3. 验证 owner 和 repo 参数是否正确

### 问题 4：MCP 服务器未加载

**解决方案**：
1. 重启 Claude Code 会话
2. 检查配置文件：`~/.claude.json` 或 `%USERPROFILE%\.claude.json`
3. 确认 `mcpServers` 部分包含 gitcode 配置

### 问题 5：Python 模块未找到

**错误信息**：
```
No module named 'gitcode_mcp'
```

**解决方案**：
1. 确认已安装 gitcode_mcp 包
2. 使用完整路径指定 Python：
   ```bash
   claude mcp add gitcode -e GITCODE_TOKEN="..." -- /path/to/python -m gitcode_mcp
   ```
3. 或使用虚拟环境中的 Python

## 配置文件示例

配置成功后，`~/.claude.json` 中应包含类似以下内容：

```json
{
  "projects": {
    "D:/Code/your-project": {
      "mcpServers": {
        "gitcode": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "gitcode_mcp"],
          "env": {
            "GITCODE_TOKEN": "你的访问令牌"
          }
        }
      }
    }
  }
}
```

## 安全建议

1. **保护令牌**：
   - 不要将令牌提交到版本控制
   - 不要在公共场合分享令牌
   - 定期轮换令牌

2. **最小权限原则**：
   - 只授予必要的权限
   - 为不同用途创建不同的令牌

3. **监控使用**：
   - 定期检查令牌使用情况
   - 发现异常立即撤销令牌

## 更新和维护

### 更新 MCP 服务器

```bash
# 如果从源码安装
cd /path/to/gitcode_mcp_server
git pull
pip install -r requirements.txt

### 更新 Skill

```bash
# 如果使用 Skills CLI
npx skills update

# 或手动替换 .skill 文件
```

### 查看服务器详情

```bash
claude mcp get gitcode
```

### 移除服务器

```bash
claude mcp remove gitcode
```

## 支持的功能

GitCode MCP 服务器提供以下功能：

### 仓库管理
- ✅ 列出仓库
- ✅ 获取仓库详情
- ✅ 创建仓库

### 分支管理
- ✅ 列出分支
- ✅ 获取分支详情
- ✅ 创建分支

### Issue 管理
- ✅ 列出 Issues
- ✅ 获取 Issue 详情
- ✅ 创建 Issue
- ✅ 列出 Issue 评论
- ✅ 创建 Issue 评论

### Pull Request 管理
- ✅ 列出 Pull Requests
- ✅ 获取 PR 详情
- ✅ 创建 Pull Request
- ✅ 更新 Pull Request
- ✅ 合并 Pull Request
- ✅ 列出 PR 评论
- ✅ 创建 PR 评论

### 搜索功能
- ✅ 搜索仓库
- ✅ 搜索 Issues
- ✅ 搜索用户

## 进一步帮助

- **GitCode MCP 服务器文档**：查看项目 README
- **Claude Code 文档**：https://code.claude.com/docs
- **Skills 文档**：https://skills.sh
- **问题反馈**：在相应的 GitHub 仓库提交 Issue

## 快速参考

### 常用命令

```bash
# 添加 MCP 服务器
claude mcp add gitcode -e GITCODE_TOKEN="..." -- python -m gitcode_mcp

# 列出服务器
claude mcp list

# 查看服务器详情
claude mcp get gitcode

# 移除服务器
claude mcp remove gitcode

# 或手动复制 Skill
copy gitcode-review.skill %USERPROFILE%\.claude\skills\  # Windows
cp gitcode-review.skill ~/.claude/skills/  # macOS/Linux

# 使用 Review Skill
/review
/review <PR编号>
```

### 环境变量

- `GITCODE_TOKEN` - GitCode 访问令牌（必需）
- `HTTP_PROXY` - HTTP 代理地址（可选）
- `HTTPS_PROXY` - HTTPS 代理地址（可选）

---

配置完成！现在你可以使用 GitCode Review Skill 进行专业的代码审查了。
