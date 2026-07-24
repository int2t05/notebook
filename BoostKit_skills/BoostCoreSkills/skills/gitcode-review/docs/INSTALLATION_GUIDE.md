# GitCode Review Skill - 完整安装指南

本指南将一步步引导你完成 GitCode Review Skill 的安装和配置。

## 📋 目录

1. [前置要求](#前置要求)
2. [步骤 1：获取 GitCode 访问令牌](#步骤-1获取-gitcode-访问令牌)
3. [步骤 2：安装 GitCode MCP 服务器](#步骤-2安装-gitcode-mcp-服务器)
4. [步骤 3：配置 Claude Code](#步骤-3配置-claude-code)
5. [步骤 4：验证 MCP 服务器](#步骤-4验证-mcp-服务器)
6. [步骤 5：安装 GitCode Review Skill](#步骤-5安装-gitcode-review-skill)
7. [步骤 6：测试 Skill](#步骤-6测试-skill)
8. [其他工具配置](#其他工具配置)
   - [Codex CLI 配置](#codex-cli-配置)
   - [Trae (ByteDance) 配置](#trae-bytedance-配置)
9. [故障排除](#故障排除)
10. [卸载指南](#卸载指南)

---

## 前置要求

在开始之前，请确保你已经具备：

- ✅ **AI编码工具**：确保已安装 Claude Code或Codex cli, Trae, 以claude code为例:
  ```bash
  claude --version
  ```

- ✅ **Python 3.8+**：用于运行 MCP 服务器
  ```bash
  python --version
  # 或
  python3 --version
  ```

- ✅ **GitCode 账号**：有效的 GitCode 账号
  - 访问 https://gitcode.com 注册或登录

- ✅ **网络连接**：能够访问 GitCode API

---

## 步骤 1：获取 GitCode 访问令牌

### 1.1 登录 GitCode

访问 [GitCode](https://gitcode.com) 并登录你的账号。

### 1.2 进入访问令牌页面

有两种方式：

**方式 1：通过设置菜单**
1. 点击右上角的头像
2. 选择 **设置** (Settings)
3. 在左侧菜单中选择 **访问令牌** (Access Tokens)

### 1.3 保存令牌

⚠️ **重要**：令牌只会显示一次！

1. 复制生成的令牌
2. 将令牌保存到安全的地方（例如密码管理器）
3. 不要将令牌分享给他人或提交到版本控制

---

## 步骤 2：安装 GitCode MCP 服务器

### 2.1 安装gitcode_mcp_server

**从源码安装**

```bash
# 克隆仓库
git clone https://gitcode.com/gitcode-ai/gitcode_mcp_server.git

# 安装依赖
pip install -r requirements.txt

# 源码安装
pip install .
```
安装参考：https://gitcode.com/gitcode-ai/gitcode_mcp_server

---

## 步骤 3：配置 Claude Code

### 3.1 添加 MCP 服务器

使用以下命令将 GitCode MCP 服务器添加到 Claude Code：

```bash
claude mcp add gitcode -e GITCODE_TOKEN="你的访问令牌" -- python -m gitcode_mcp
```

**重要提示**：
- 将 `你的访问令牌` 替换为步骤 1 中获取的实际令牌
- 令牌必须用引号包裹
- 服务器名称 `gitcode` 必须在环境变量选项 `-e` 之前

### 3.2 使用代理（可选）

如果你需要通过代理访问 GitCode：

```bash
claude mcp add gitcode \
  -e GITCODE_TOKEN="你的访问令牌" \
  -e HTTP_PROXY="http://localhost:8080" \
  -e HTTPS_PROXY="http://localhost:8080" \
  -- python -m gitcode_mcp
```

### 3.3 使用特定 Python 路径（可选）

如果需要使用特定的 Python 解释器：

```bash
claude mcp add gitcode \
  -e GITCODE_TOKEN="你的访问令牌" \
  -- /path/to/python -m gitcode_mcp
```

例如，使用虚拟环境中的 Python：

**Windows**:
```bash
claude mcp add gitcode \
  -e GITCODE_TOKEN="你的访问令牌" \
  -- C:\path\to\venv\Scripts\python.exe -m gitcode_mcp
```

**macOS/Linux**:
```bash
claude mcp add gitcode \
  -e GITCODE_TOKEN="你的访问令牌" \
  -- /path/to/venv/bin/python -m gitcode_mcp
```

---

## 步骤 4：验证 MCP 服务器

### 4.1 检查服务器列表

```bash
claude mcp list
```

你应该能看到 `gitcode` 服务器已配置（可能显示为空，这是正常的，因为它是项目级配置）。

### 4.2 查看配置文件

检查配置文件以确认服务器已添加：

**Windows**:
```bash
type %USERPROFILE%\.claude.json
```

**macOS/Linux**:
```bash
cat ~/.claude.json
```

在配置文件中，你应该能找到类似以下的内容：

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

### 4.3 测试 MCP 服务器

启动 Claude Code 并尝试以下命令：

```
列出我的 GitCode 仓库
```

如果配置正确，你应该能看到你的 GitCode 仓库列表。

---

## 步骤 5：安装 GitCode Review Skill

### 5.1 下载 Skill 文件

确保你已经有 `gitcode-review.skill` 文件。

### 5.2 安装 Skill

有两种安装方式，推荐使用 Skills CLI。

#### 方式 1：使用 Skills CLI（推荐）

Skills CLI 是官方的 Skill 包管理工具，提供更好的安装和管理体验。

**从远程安装**：
```bash
npx skills add https://gitcode.com/CarbonadoRain/gitcode-review.git -g -y
```

**参数说明**：
- `-g` 或 `--global` - 全局安装（用户级别），所有项目都可使用
- `-y` 或 `--yes` - 跳过确认提示，自动安装

**查看已安装的 Skills**：

```bash
npx skills list
```

**更新 Skill**：

```bash
npx skills update
```

**卸载 Skill**：

```bash
npx skills remove gitcode-review
```

#### 方式 2：手动复制

如果不想使用 Skills CLI，也可以手动复制文件。

**Windows**:
```bash
# 创建 skills 目录（如果不存在）
mkdir %USERPROFILE%\.claude\skills

# 复制 skill 文件
copy gitcode-review.skill %USERPROFILE%\.claude\skills\
```

**macOS/Linux**:
```bash
# 创建 skills 目录（如果不存在）
mkdir -p ~/.claude/skills

# 复制 skill 文件
cp gitcode-review.skill ~/.claude/skills/
```

### 5.3 验证 Skill 安装

#### 使用 Skills CLI 验证

```bash
# 列出所有已安装的 Skills
npx skills list

# 查看 gitcode-review Skill 详情
npx skills info gitcode-review
```

#### 手动验证

检查 skill 文件是否已复制：

**Windows**:
```bash
dir %USERPROFILE%\.claude\skills\gitcode-review.skill
```

**macOS/Linux**:
```bash
ls -lh ~/.claude/skills/gitcode-review.skill
```

### 5.4 重启 Claude Code（可选）

为确保 Skill 被加载，建议重启 Claude Code 会话：

1. 退出当前 Claude Code 会话
2. 重新启动 Claude Code

---

## 步骤 6：测试 Skill

### 6.1 测试基本功能

在 Claude Code 中尝试以下命令：

**测试 1：列出 PR**
```bash
/review
```

如果有打开的 PR，应该会显示 PR 列表。

**测试 2：审查指定 PR**
```bash
/review 2
```

应该会：
1. 获取 PR #2 的详细信息
2. 分析代码变更
3. 生成中文审查报告
4. 询问是否提交评论

### 6.2 测试自然语言触发(claude code之外平台)

尝试使用自然语言：

```
帮我审查 https://gitcode.com/CarbonadoRain/hyperscan 的最近一个 PR
```

应该会自动：
1. 识别仓库信息
2. 获取最近的 PR
3. 进行代码审查
4. 生成报告

### 6.3 验证审查报告

审查报告应该包含：

- ✅ PR 概述
- ✅ 变更详情（文件、行数）
- ✅ 代码质量分析（优点和改进点）
- ✅ 潜在问题和风险
- ✅ 改进建议
- ✅ 总体评价和评分
- ✅ 中文输出

---

## 其他工具配置

除了 Claude Code，GitCode MCP 服务器还可以在其他 AI 编程工具中使用。以下是各工具的配置指南。

### Codex CLI 配置

Codex 是 OpenAI 开发的 AI 编程助手 CLI 工具，使用 TOML 格式配置文件。

#### 安装 Codex CLI

```bash
# 使用 npm 安装
npm install -g @openai/codex-cli

# 或使用 pip 安装
pip install openai-codex
```

#### 配置文件位置

- **Windows**: `%USERPROFILE%\.codex\config.toml`
- **macOS**: `~/.codex/config.toml`
- **Linux**: `~/.config/codex/config.toml`

#### 配置内容

**重要**: Codex 使用 TOML 格式，不是 JSON。

```toml
# Codex CLI 配置文件

[mcp.servers.gitcode]
command = "python"
args = ["-m", "gitcode_mcp"]

[mcp.servers.gitcode.env]
GITCODE_TOKEN = "你的访问令牌"
```

#### 使用命令行添加

```bash
codex mcp add gitcode --env GITCODE_TOKEN="你的访问令牌" -- python -m gitcode_mcp
```

#### 验证配置

```bash

# 列出 MCP 服务器
codex mcp list

#### 在 Codex 中使用

启动 Codex 并使用：

```bash
codex
```

然后输入：

```
列出我的 GitCode 仓库
```

#### 参考资源

- **详细配置指南**: 查看 `CODEX_SETUP.md`
- **官方文档**: https://developers.openai.com/codex/cli/
- **MCP 文档**: https://developers.openai.com/codex/mcp/

---

### Trae (ByteDance) 配置

Trae 是由 ByteDance（字节跳动）开发的 AI 驱动的独立 IDE。

**重要**: Trae 是一个独立的 IDE 产品，不是 VS Code 扩展。

#### 下载和安装

1. 访问 Trae 官网
   - https://traeide.com/
   - https://www.trae.ai/

2. 下载适合你操作系统的版本
   - Windows
   - macOS
   - Linux

3. 安装 Trae IDE

#### 配置内容

```json
{
  "mcpServers": {
    "gitcode": {
      "command": "python",
      "args": ["-m", "gitcode_mcp"],
      "env": {
        "GITCODE_TOKEN": "你的访问令牌"
      },
      "description": "GitCode MCP服务，用于与GitCode代码托管平台交互"
    }
  }
}
```

#### 配置步骤

1. 打开 Trae IDE
2. 进入 Settings
3. 找到MCP-添加
4. 添加上述配置或编辑配置文件
5. 保存并重启 Trae

#### 在 Trae 中使用

配置完成后，可以在 Trae 中使用：

```
列出我的 GitCode 仓库
```

```
审查 PR #2
```

### 通用配置说明

#### 环境变量配置

所有工具都支持以下环境变量：

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `GITCODE_TOKEN` | GitCode 访问令牌 | ✅ 是 |
| `HTTP_PROXY` | HTTP 代理地址 | ❌ 否 |
| `HTTPS_PROXY` | HTTPS 代理地址 | ❌ 否 |

#### 配置文件格式

标准的 MCP 服务器配置格式：

```json
{
  "mcpServers": {
    "服务器名称": {
      "command": "命令",
      "args": ["参数1", "参数2"],
      "env": {
        "环境变量名": "环境变量值"
      }
    }
  }
}
```

#### 验证配置

配置完成后，可以通过以下方式验证：

1. **检查配置文件语法**
   ```bash
   python -m json.tool < 配置文件路径
   ```

2. **测试 MCP 服务器**
   ```bash
   export GITCODE_TOKEN="你的令牌"
   python -m gitcode_mcp
   ```

3. **在工具中测试**
   - 尝试列出仓库
   - 尝试获取 PR 信息
   - 检查是否有错误信息

#### 常见配置问题

**问题：配置文件不生效**
- 检查 JSON 格式是否正确
- 确认文件路径是否正确
- 重启工具使配置生效

**问题：找不到 Python 模块**
- 使用完整的 Python 路径
- 确认 gitcode_mcp 已安装
- 检查虚拟环境是否激活

**问题：令牌无效**
- 确认令牌未过期
- 检查令牌权限范围
- 重新生成令牌

---

## 故障排除

### 问题 1：命令参数顺序错误

**错误信息**：
```
Invalid environment variable format: gitcode
```

**原因**：服务器名称和环境变量选项的顺序错误。

**解决方案**：
```bash
# ❌ 错误
claude mcp add -e GITCODE_TOKEN="..." gitcode -- python -m gitcode_mcp

# ✅ 正确
claude mcp add gitcode -e GITCODE_TOKEN="..." -- python -m gitcode_mcp
```

### 问题 2：MCP 服务器启动失败

**错误信息**：
```
GitCode令牌未提供
```

**解决方案**：
1. 检查 GITCODE_TOKEN 是否正确设置
2. 确认令牌用引号包裹
3. 验证令牌是否有效（未过期）
4. 重新生成令牌并更新配置

### 问题 3：Python 模块未找到

**错误信息**：
```
No module named 'gitcode_mcp'
```

**解决方案**：
1. 确认已安装 gitcode_mcp 包：
   ```bash
   pip list | grep gitcode
   ```

2. 使用完整路径指定 Python：
   ```bash
   claude mcp add gitcode -e GITCODE_TOKEN="..." -- /full/path/to/python -m gitcode_mcp
   ```

3. 检查 Python 环境：
   ```bash
   which python
   python -c "import sys; print(sys.path)"
   ```

### 问题 4：无法访问仓库

**错误信息**：
```
404, token not found
```

**解决方案**：
1. 确认令牌有正确的权限范围（api, read_repository, write_repository）
2. 检查仓库是否存在且有访问权限
3. 验证 owner 和 repo 参数是否正确
4. 尝试在浏览器中访问仓库确认权限

### 问题 5：Skill 未加载

**症状**：使用 `/review` 命令没有反应

**解决方案**：
1. 确认 skill 文件已复制到正确位置：
   ```bash
   # Windows
   dir %USERPROFILE%\.claude\skills\gitcode-review.skill

   # macOS/Linux
   ls ~/.claude/skills/gitcode-review.skill
   ```

2. 检查 skill 文件完整性：
   ```bash
   # 查看 skill 文件内容
   python -c "import zipfile; zf = zipfile.ZipFile('~/.claude/skills/gitcode-review.skill'); print('\n'.join(zf.namelist()))"
   ```

3. 重启 Claude Code 会话

4. 尝试手动解压 skill 文件到 skills 目录

### 问题 6：代理配置问题

**症状**：无法连接到 GitCode API

**解决方案**：
1. 验证代理地址是否正确
2. 测试代理连接：
   ```bash
   curl -x http://localhost:8080 https://gitcode.com
   ```

3. 更新 MCP 服务器配置：
   ```bash
   claude mcp remove gitcode
   claude mcp add gitcode \
     -e GITCODE_TOKEN="..." \
     -e HTTP_PROXY="http://proxy:port" \
     -e HTTPS_PROXY="http://proxy:port" \
     -- python -m gitcode_mcp
   ```

### 问题 7：权限不足

**错误信息**：
```
403 Forbidden
```

**解决方案**：
1. 确认令牌有足够的权限
2. 检查是否对目标仓库有访问权限
3. 如果是私有仓库，确认你是仓库成员
4. 重新生成令牌并确保选择了所有必要的权限范围

---

## 卸载指南

### 卸载 Skill

**Windows**:
```bash
del %USERPROFILE%\.claude\skills\gitcode-review.skill
```

**macOS/Linux**:
```bash
rm ~/.claude/skills/gitcode-review.skill
```

### 移除 MCP 服务器

```bash
claude mcp remove gitcode
```

### 撤销 GitCode 访问令牌

1. 访问 https://gitcode.com/-/profile/personal_access_tokens
2. 找到你创建的令牌
3. 点击 **撤销** (Revoke) 按钮

---

## 常见问题 (FAQ)

### Q1: Skill 支持哪些 GitCode 功能？

A: Skill 支持：
- 列出 Pull Requests
- 获取 PR 详细信息
- 分析代码变更（diff）
- 生成中文审查报告
- 提交评论到 PR

### Q2: 可以审查私有仓库的 PR 吗？

A: 可以，只要你的 GitCode 令牌有访问该私有仓库的权限。

### Q3: 审查报告的语言可以更改吗？

A: 当前版本固定为中文输出。如需其他语言，可以修改 SKILL.md 中的报告模板。

### Q4: 可以自定义审查规则吗？

A: 可以通过编辑 `references/review-guidelines.md` 文件来自定义审查重点和规则。

### Q5: Skill 会自动提交评论吗？

A: 不会。Skill 会先生成审查报告，然后询问你是否需要提交评论。只有在你确认后才会提交。

### Q6: 如何更新 Skill？

A: 下载新版本的 .skill 文件，然后覆盖旧文件：
```bash
# Windows
copy /Y gitcode-review.skill %USERPROFILE%\.claude\skills\

# macOS/Linux
cp -f gitcode-review.skill ~/.claude/skills/
```

### Q7: 可以同时审查多个 PR 吗？

A: 当前版本一次只能审查一个 PR。批量审查功能计划在未来版本中添加。

---

## 获取帮助

如果遇到问题：

1. **查看文档**：
   - [README.md](README.md) - 完整配置指南

2. **检查日志**：
   - MCP 服务器日志：`gitcode_mcp.log`
   - Claude Code 日志：查看终端输出

3. **提交 Issue**：
   - 在 GitCode MCP 服务器仓库提交问题
   - 提供详细的错误信息和复现步骤

4. **社区支持**：
   - 查看 Claude Code 文档：https://code.claude.com/docs
   - 访问 Skills 社区：https://skills.sh

---

## 下一步

安装完成后，你可以：

1. **阅读最佳实践**：查看 `references/review-guidelines.md` 了解代码审查技巧

2. **尝试审查 PR**：在实际项目中使用 Skill 进行代码审查

3. **自定义配置**：根据团队需求调整审查规则和模板

4. **分享反馈**：帮助改进 Skill，提出功能建议

---

**祝你使用愉快！** 🎉

如有任何问题，请参考故障排除部分或查看完整文档。
