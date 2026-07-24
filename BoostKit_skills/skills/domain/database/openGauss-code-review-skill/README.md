# openGauss PR 自动代码检视技能包

自包含的 TRAE 技能包：对 openGauss 仓库（`gitcode.com/opengauss/openGauss-server`）的指定 PR 调用 superpowers 代码检视方法做只读检视，按三段式格式整理意见，并自动提交评论到该 PR 下。拷贝到任意 TRAE 环境即可直接使用。

## 包含内容

```
code-review-skill/
├── opengauss-pr-review/        # 主技能：PR 检视 + 提交评论
│   └── SKILL.md
├── requesting-code-review/     # 依赖技能：superpowers 代码检视方法论 + 子代理模板
│   ├── SKILL.md
│   └── code-reviewer.md
└── README.md                   # 本说明
```

`opengauss-pr-review/SKILL.md` 通过相对路径 `../requesting-code-review/code-reviewer.md` 引用依赖模板，两个技能需作为同级目录安装。

## 前置要求

- TRAE（CN 版）已安装，支持 `.trae/skills/` 自定义技能。
- 本地有 `openGauss-server` 仓库的 git 工作副本（`git remote -v` 含 `gitcode.com/opengauss/openGauss-server`），用于 `git fetch` PR 变更。
- 操作系统：Windows + PowerShell（技能内命令为 PowerShell 语法，且 `curl.exe`/`[Environment]::GetEnvironmentVariable` 等 Windows 专用）。Linux/macOS 需自行替换为等价 shell 命令。
- gitcode **个人访问令牌**（仅提交评论需要，检视本身不需要）。

## 安装

### 1. 拷贝技能目录

把 `opengauss-pr-review/` 和 `requesting-code-review/` 两个目录整体拷贝到 TRAE 的 skills 目录（二选一，两个技能都要拷）：

- **项目级**（仅当前 openGauss-server 仓库可用）：拷到 `<仓库根>/.trae/skills/`
- **用户级**（所有项目可用，推荐）：拷到 `c:\Users\<你的用户名>\.trae-cn\skills\`

PowerShell 示例（用户级安装）：

```powershell
$dst = "$env:USERPROFILE\.trae-cn\skills"
$src = "<本仓库根>/Tools/code-review-skill"
Copy-Item "$src\opengauss-pr-review"       "$dst\opengauss-pr-review"       -Recurse -Force
Copy-Item "$src\requesting-code-review"    "$dst\requesting-code-review"    -Recurse -Force
```

安装后若 TRAE 正在运行，重启一次 TRAE 以扫描新技能。

### 2. 配置 gitcode 访问令牌

1. 登录 gitcode → 个人设置 → 访问令牌，新建一个令牌，勾选 `repo` / 评论写权限。
2. 把令牌设为用户级环境变量 `GITCODE_TOKEN`：

```powershell
[Environment]::SetEnvironmentVariable("GITCODE_TOKEN", "<你的令牌>", "User")
```

3. **重要提醒**（实测所得）：
   - git push 用的账号密码 **不等于** API personal access token，API 不接受凭据密码（返回 401）。必须用上面生成的专用 token。
   - 通过系统属性设置环境变量后，**已运行的 TRAE 终端进程用 `$env:GITCODE_TOKEN` 读不到**，必须重启 TRAE，或技能内用 `[Environment]::GetEnvironmentVariable("GITCODE_TOKEN","User")` 直接读注册表（技能已采用此方式，无需重启）。
   - 禁止把 token 写入任何文件、日志、提交信息或评论正文。

## 使用

在任意 openGauss-server 工作目录下对 TRAE 说：

- `检视 PR #9343 并把意见发到 PR 下`
- `对 https://gitcode.com/opengauss/openGauss-server/pull/9343 做代码检视并提交评论`

技能会自动执行：

1. `git fetch` PR head 到本地只读引用（不碰工作树）。
2. 派发 `general-purpose` 子代理，按 `code-reviewer.md` 模板做只读检视。
3. 把检视问题映射为三段式格式（见下）。
4. 用 `curl.exe` 提交评论到 PR，成功返回 HTTP 201。

## 输出格式

每条检视意见严格按三段式，`[原因]`/`[检视意见]` 各独占一行，条目间用单独成行的 `；` 分隔：

```
[问题1]【严重】src/backend/optimizer/path/indxpath.cpp:4320 问题描述
[原因] 影响与为何是问题
[检视意见] 建议修法
；
[问题2]【重要】...
```

严重程度标签：`【严重】`/`【重要】`/`【轻微】` ↔ Critical/Important/Minor。

## 关键技术事实（勿改，实测所得）

- API 基础地址：`https://api.gitcode.com/api/v5`（必须是 `api.gitcode.com` 子域名；`gitcode.com/api/v1`、`/api/v4` 会被 CloudWAF 拦截返回 418）。
- 认证方式：`?access_token=<token>` 查询参数（`Authorization` 头不被接受，返回 401）。
- 提交评论端点：`POST /repos/{owner}/{repo}/pulls/{number}/comments?access_token={token}`，请求体 `{"body":"<Markdown>"}`，成功返回 201。
- PR 的 git ref：`refs/merge-requests/{number}/head`（GitLab 风格，非 Gitea 的 `refs/pull/{n}/head`）。
- 提交评论必须用 `curl.exe --data-binary @file` 从无 BOM UTF-8 文件发送原始字节；PowerShell `Invoke-RestMethod`+`ConvertTo-Json` 对中文正文处理后会被 gitcode API 判为 400 `body parsing error`。
- PowerShell 下 `git diff A..B` 的 `..` 会被吞，须用 `git diff --merge-base A B` 双参数形式。

## 故障排查

| 现象 | 处理 |
|---|---|
| 401 `token not found` | token 无效或用了账号密码而非 API personal access token。重新生成 API 令牌设为 `GITCODE_TOKEN`。 |
| 400 `body parsing error` | 改用 `curl.exe --data-binary @file`（无 BOM UTF-8），不要用 `Invoke-RestMethod`+`ConvertTo-Json`。 |
| 418 含 "CloudWAF" | 打到废弃的 `gitcode.com/api/v1`。改用 `api.gitcode.com/api/v5`，请求带 `User-Agent`。 |
| 404 | 端点路径或 owner/repo/pr 不对；URL 路径 `/pull/` 与 `/pulls/` 都要兼容。 |
| `git fetch refs/merge-requests/{n}/head` 报无此 ref | 回退试 `refs/pull/{n}/head`；仍失败用 API 取 `head.sha` 后 `git fetch` 该 commit。 |
| `git diff A..B` 报 usage 错误 | PowerShell 吞了 `..`，改用 `git diff --merge-base A B`。 |

## 限制

- 仅 Windows + PowerShell 环境验证通过；其他平台需适配 shell 命令。
- 仅对 `gitcode.com/opengauss/openGauss-server` 仓库验证；用于其他 gitcode 仓库需调整 `GITCODE_OWNER`/`GITCODE_REPO` 环境变量或 URL 解析。
- 检视为只读，不修改工作树/索引/HEAD/分支，不做 git commit/push，只发评论。
