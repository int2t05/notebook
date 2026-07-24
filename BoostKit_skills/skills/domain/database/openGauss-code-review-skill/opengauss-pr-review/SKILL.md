---
name: opengauss-pr-review
description: "Use when the user gives an openGauss gitcode PR number/URL and asks to review and post findings to the PR."
---

# openGauss PR 自动代码检视

对 openGauss 仓库（`gitcode.com/opengauss/openGauss-server`）的指定 PR，调用 superpowers 代码检视方法（`requesting-code-review` 技能的 [code-reviewer.md](../requesting-code-review/code-reviewer.md) 模板）做只读检视，按指定三段式格式整理意见，并提交评论到该 PR 下。

## 触发条件

当用户给出一个 PR 编号或 gitcode PR URL，并要求"检视 PR 并把意见发到/提交到 PR"时调用。典型表述：
- "检视 PR #123 并把意见发到 PR 下"
- "对 https://gitcode.com/opengauss/openGauss-server/pull/123 做代码检视并提交评论"

## 关键事实（实测所得，勿改）

- **API 基础地址**：`https://api.gitcode.com/api/v5`（**必须是 `api.gitcode.com` 子域名**）。`gitcode.com/api/v1`、`gitcode.com/api/v4` 会被 CloudWAF 拦截返回 418，**不可用**。
- **认证方式**：`access_token` **查询参数**，即 `?access_token=${GITCODE_TOKEN}`。`Authorization: Bearer`/`token` 头**不被接受**（返回 401 "token not found"）。
- **提交整体评论端点**：`POST /repos/{owner}/{repo}/pulls/{number}/comments?access_token={token}`，请求体 `{"body":"<Markdown>"}`（不带 `path`/`position` 即整体评论），成功返回 **201**。
- **PR 的 git ref**：`refs/merge-requests/{number}/head`（GitLab 风格，非 Gitea 的 `refs/pull/{n}/head`）。少数旧 PR 可能在 `refs/pull/{n}/head`，fetch 失败时回退尝试。
- **获取 PR 变更用 git，不用 API**：公开仓库 `git fetch` 上述 ref 即可拿到 head，无需 API、无需 token、不经 WAF。openGauss 仓库数 GB，**禁止 clone 整个 fork**。

## 前置要求

- 当前工作目录必须是 `openGauss-server` 仓库（`git remote -v` 应含 `gitcode.com/opengauss/openGauss-server`）。
- 环境变量 `GITCODE_TOKEN`：gitcode **个人访问令牌**（API 专用）。在 gitcode 个人设置 → 访问令牌 创建，需 `repo`/评论写权限。
  - **重要**：git push 用的账号密码 ≠ API personal access token。git credential 里存的密码 API 不接受（实测 401）。必须在 gitcode 生成专用 API token 并设到 `GITCODE_TOKEN`。
  - **仅 Step 4 提交评论需要 token**；Step 1~3 检视本身不需要 token（公开仓库 git 匿名可读）。
  - **禁止将 token 写入任何文件、日志、提交信息或评论正文**。
  - **禁止用 `git credential fill` 提取密码当 token**（会明文输出密码，且 API 不接受）。
  - **读 token 的可靠方式**：`$tok = [Environment]::GetEnvironmentVariable("GITCODE_TOKEN","User")`（直接读用户级注册表，**无需重启终端进程**）。`$env:GITCODE_TOKEN` 只在设置它的那个 shell 窗口有效；通过 Windows 系统属性设置的变量，已运行的 TRAE 终端进程用 `$env:` 读不到，必须用 `[Environment]::GetEnvironmentVariable(...,"User")` 或重启 TRAE。
- 可选环境变量（未设置用默认）：
  - `GITCODE_API_BASE`，默认 `https://api.gitcode.com/api/v5`。
  - `GITCODE_OWNER`，默认 `opengauss`。
  - `GITCODE_REPO`，默认 `openGauss-server`。
  - `GITCODE_BASE_REF`，默认 `master`（PR 目标分支，用于 merge-base；若 PR 目标非 master 则覆盖）。

## 执行步骤

按 Step 0 ~ Step 5 顺序执行，用 TodoWrite 跟踪。

### Step 0 · 前置检查与参数解析

1. 确认在 openGauss-server 仓库：`git remote -v` 含 `gitcode.com/opengauss/openGauss-server`。
2. 解析入参为 `{owner}/{repo}/{pr_number}`：
   - 入参为数字（如 `123`）→ owner=`$env:GITCODE_OWNER`（默认 `opengauss`），repo=`$env:GITCODE_REPO`（默认 `openGauss-server`），pr_number=123。
   - 入参为 URL → 正则提取。**URL 路径可能是 `/pull/123`（单数，gitcode 现行）或 `/pulls/123`（旧/兼容）**，两种都要兼容。
3. 记录 `${OWNER}`、`${REPO}`、`${PR}`。
4. 检查 `GITCODE_TOKEN`：若已设置，记 `HAS_TOKEN=true`；若未设置，记 `HAS_TOKEN=false`，**不停止**——继续 Step 1~3 完成检视，仅在 Step 4 提交时提示用户设置 token 或手动提交。

### Step 1 · 用 git 获取 PR 变更（不依赖 API、不需要 token）

1. Fetch PR head 到本地只读引用（不碰工作树）：
   ```
   git fetch origin refs/merge-requests/${PR}/head:refs/review/pr-${PR}
   ```
   若报错"无此 ref"，回退：
   ```
   git fetch origin refs/pull/${PR}/head:refs/review/pr-${PR}
   ```
   仍失败则按"故障排查"处理。
2. 确定 HEAD 与 BASE：
   ```
   $HEAD_SHA = git rev-parse refs/review/pr-${PR}
   git fetch origin ${GITCODE_BASE_REF:-master}
   $BASE_SHA = git merge-base origin/${GITCODE_BASE_REF:-master} refs/review/pr-${PR}
   ```
   `BASE_SHA` 即 PR 与目标分支的分叉点，作为 diff 基线（比 PR 元数据里的 base.sha 更稳健，能正确反映"相对目标分支的实际改动"）。
3. 概览变更（供子代理与 DESCRIPTION 用）：
   ```
   git diff --stat --merge-base $BASE_SHA refs/review/pr-${PR}
   git diff --name-status --merge-base $BASE_SHA refs/review/pr-${PR}
   git log --oneline $BASE_SHA..refs/review/pr-${PR}
   ```
   注意：PowerShell 下 `..` 语法会被吞，**必须用 `--merge-base $BASE_SHA refs/review/pr-${PR}` 双参数形式**，不要写 `$BASE_SHA..ref`。
4. （可选，丰富 DESCRIPTION）若有 `GITCODE_TOKEN`：`GET ${GITCODE_API_BASE}/repos/${OWNER}/${REPO}/pulls/${PR}?access_token=${GITCODE_TOKEN}` 取 `title`/`body`。失败不影响检视，用 commit message 代替。

### Step 2 · 派发 superpowers 代码检视子代理（只读，基于本地引用）

按 [code-reviewer.md](../requesting-code-review/code-reviewer.md) 模板派发 `general-purpose` 子代理，**在当前仓库用 `refs/review/pr-${PR}` 引用做只读检视**（无需 checkout、无需 tmp 目录、不碰工作树）。

占位符填充：
- `{DESCRIPTION}` = PR 标题+描述（Step 1.4 取得）或 commit message + `git diff --stat` 概览。
- `{PLAN_OR_REQUIREMENTS}` = PR 描述；为空则"检视 PR #${PR} 变更是否符合 openGauss 编码与质量要求"。
- `{BASE_SHA}` = Step 1 的 `BASE_SHA`。
- `{HEAD_SHA}` = Step 1 的 `HEAD_SHA`。

子代理约束（写入子代理 prompt）：
- **只读检视**，禁止 checkout、修改工作树/索引/HEAD/分支，禁止 commit/push。
- 查 diff：`git diff --merge-base <BASE_SHA> refs/review/pr-${PR}`
- 查 PR 版本某文件完整内容：`git show refs/review/pr-${PR}:<文件路径>`（**不要** checkout）
- 查 base 版本文件：`git show <BASE_SHA>:<文件路径>`
- 查 commit：`git show <HEAD_SHA>` / `git log --oneline <BASE_SHA>..refs/review/pr-${PR}`
- **PowerShell 下用 `--merge-base A B` 双参数，不要用 `A..B`**（`..` 会被 PowerShell 吞掉导致 usage 错误）。
- 返回结构：优点 / 问题（Critical/Important/Minor，每条含 `file:line`+问题+为何重要+修法）/ 建议 / 结论（是否可合并）。

### Step 3 · 整理检视意见（指定三段式格式）

将子代理返回的"问题"逐条映射为三段式，**严格按此格式**：

- `[问题N]` 内含 `file:line` + 问题描述，单独一行。
- `[原因]` 对应 "Why it matters"，**换行另起**（前面不要逗号）。
- `[检视意见]` 对应 "How to fix"，**换行另起**（前面不要逗号）。
- 严重程度标签前缀在 `[问题N]` 内：`【严重】`/`【重要】`/`【轻微】` ↔ Critical/Important/Minor。
- 条目之间用中文分号 `；` 分隔，`；` 单独成行以提升可读性。

### Step 4 · 提交评论到 PR

**前置**：需要 `GITCODE_TOKEN`（API personal access token）。若 `HAS_TOKEN=false`：将评论正文（见模板）呈现给用户，提示"检视已完成，但未设置 GITCODE_TOKEN 无法自动提交。请：①在 gitcode 个人设置生成 API 访问令牌并设为环境变量 GITCODE_TOKEN 后重试；或②手动将上述正文贴到 PR 评论。" 然后**停止**，不进入 4.A。

**4.A 提交（主路径）：**

```
POST ${GITCODE_API_BASE}/repos/${OWNER}/${REPO}/pulls/${PR}/comments?access_token=${GITCODE_TOKEN}
```
- 请求头：`Content-Type: application/json`、`User-Agent: openGauss-pr-review/1.0`。（**不要**用 `Authorization` 头，gitcode API 不认。）
- 请求体：`{"body": "<评论正文 Markdown>"}`
- 成功：HTTP 201，从响应取评论 `id` 与 `url`/`html_url`。

PowerShell 示例（**必须用 curl.exe + --data-binary @file，不要用 Invoke-RestMethod/ConvertTo-Json**——实测 PowerShell 的 ConvertTo-Json 对中文/转义处理后 gitcode API 返回 400 "body parsing error"，而 curl.exe 从文件发送原始字节成功）：
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tok = [Environment]::GetEnvironmentVariable("GITCODE_TOKEN","User")
$commentBody = [IO.File]::ReadAllText("pr_comment.md")
$json = @{ body = $commentBody } | ConvertTo-Json -Depth 5 -Compress
$jsonPath = "payload.json"
[IO.File]::WriteAllText($jsonPath, $json, (New-Object Text.UTF8Encoding($false)))
$uri = "https://api.gitcode.com/api/v5/repos/$OWNER/$REPO/pulls/$PR/comments?access_token=$tok"
curl.exe -s -w "`nHTTP_CODE=%{http_code}" -X POST $uri `
  -H "Content-Type: application/json" -H "Accept: application/json" -H "User-Agent: openGauss-pr-review/1.0" `
  --data-binary "@$jsonPath" --max-time 60
Remove-Item $jsonPath -Force
```
成功返回 HTTP 201 + JSON（含 `id`/`note_id`/`body`）。注意：`payload.json` 用无 BOM 的 UTF-8 写入（`UTF8Encoding($false)`）；token 只在 URL 查询串里，不打印。

**4.B 验证 token 有效性**（提交前可先验，避免盲提交）：
```
GET ${GITCODE_API_BASE}/user?access_token=${GITCODE_TOKEN}
```
返回 200+用户信息则 token 有效；401 "token not found" 则 token 无效或不是 API token，按"故障排查"提示用户。

**4.C 兜底**：若 4.A 持续失败且用户配了 `GITCODE_COMMENT_CMD`（自定义提交命令，约定从环境变量 `OGR_COMMENT_BODY` 读正文、`OGR_PR` 读 PR 号，stdout 返回评论链接），则调用它。否则停止并报告。

### Step 5 · 回报结果与清理

向用户展示：
- 提交结果：评论链接（`html_url`/`url`）或"未提交（缺 token）"。
- 检视结论摘要：优点条数、严重/重要/轻微各几条、是否可合并结论。
- 任何降级/回退（如 ref 从 merge-requests 回退到 pull、DESCRIPTION 用 commit message 代替 API）一并说明。

清理：删除本地只读引用 `git update-ref -d refs/review/pr-${PR}`（可选，引用不影响工作树）。无需删目录（未创建 tmp）。

## 评论正文模板

提交到 PR 的 Markdown 正文严格如下（`<...>` 为占位，替换为实际内容）：

```markdown
## 自动代码检视结果（PR #<PR>）

> 由 superpowers 代码检视方法自动生成，仅作参考，最终以人工判断为准。

### 优点
- <优点1，可选 1~3 条，无则写"暂无">

### 检视意见
[问题1]【<严重程度>】<file:line 问题描述>
[原因] <影响/为何是问题>
[检视意见] <建议修法>
；
[问题2]【<严重程度>】<file:line 问题描述>
[原因] <影响>
[检视意见] <建议>
；
<...更多条目>

### 结论
可合并性：<是 / 否 / 需修复>
理由：<1~2 句技术性总结>
```

说明：
- "检视意见"段每条意见的三段 `[问题N]`/`[原因]`/`[检视意见]` 各占一行（换行分隔，不用逗号）；条目之间用单独成行的 `；` 分隔。
- `<严重程度>` 取值：`严重`/`重要`/`轻微`。
- 无问题时"检视意见"段写"未发现需要修改的问题。"，结论为"是"。

## 故障排查

| 现象 | 处理 |
|---|---|
| 401 `token not found` | token 无效或用的是账号密码/git push 凭据而非 API personal access token。提示用户在 gitcode 个人设置生成 API 访问令牌，设为 `GITCODE_TOKEN`。**不要用 `git credential fill` 取的密码**。 |
| 400 `body parsing error` | 提交评论时 JSON body 解析失败。改用 `curl.exe --data-binary @file` 从无 BOM UTF-8 文件发送原始字节，**不要用** PowerShell `Invoke-RestMethod`+`ConvertTo-Json`（对中文/转义处理后触发 400）。 |
| 418 响应体含 "CloudWAF"/"访问被拦截" | 打到了被废弃的 `gitcode.com/api/v1` 或 `/api/v4`。改用 `api.gitcode.com/api/v5`（`GITCODE_API_BASE` 默认值已修正）。确保请求带 `User-Agent`。 |
| 404 | 端点路径或 owner/repo/pr 不对。确认 URL 解析（`/pull/` 与 `/pulls/` 都可能）。 |
| `git fetch refs/merge-requests/{n}/head` 报无此 ref | 回退试 `refs/pull/{n}/head`；仍失败则该 PR 可能未走标准 ref 流程，改用 `GET .../pulls/{n}`（需 token）取 `head.sha` 后 `git fetch origin` 该 commit。 |
| `git diff A..B` 报 usage 错误 | PowerShell 吞了 `..`。改用 `git diff --merge-base A B` 双参数形式。 |
| 子代理读不到 commit | 确认 `refs/review/pr-${PR}` 已 fetch、`BASE_SHA`/`HEAD_SHA` 可达（`git rev-parse --verify`），必要时重新 fetch。 |

## 关键规则

- **只读检视**：全程不修改工作树/索引/HEAD/分支，不 commit/push。检视基于 `refs/review/pr-${PR}` 引用 + `git show`/`git diff`，天然只读。
- **不泄露 token**：`GITCODE_TOKEN` 只放 URL 查询串，禁止打印、写文件、入日志/评论正文。**禁止 `git credential fill`**（明文泄露密码且 API 不认）。
- **不提交代码**：只发评论，不做 git commit/push。
- **格式不可变**：检视意见必须用 `[问题N]/[原因]/[检视意见]` 三段式 + `；` 分隔 + `【严重程度】` 标签。
- **客观校准**：严重程度按子代理实际判定映射，不夸大。
- **API 地址不可错**：必须 `api.gitcode.com/api/v5` + `access_token` 查询参数，勿用 `gitcode.com/api/v1` 或 Authorization 头。
