# 双归档与推送

## 配置（首次按你自己的环境填，本 skill 不内置任何个人信息）

下面这些占位符是**用户自有信息**，第一次跑前由用户给定（或从本机现有 git 配置/remote 推断），**不要硬编码进 skill 文件**：

| 占位符 | 含义 | 怎么拿 |
|---|---|---|
| `<gitcode-user>` | 你的代码托管账号名 | 从已有 remote 的 URL 里读 |
| `<public-repo>` | 公开分享仓库名 | 用户给定，默认 `tech-daily-brief` |
| `<commit-email>` / `<commit-name>` | 提交身份 | 优先复用本机 `git config user.email/name`；按你环境的提交规范，别用私人邮箱 |
| 私有归档仓库 | 分享之外的私有备份仓（如个人的 `ai-docs`） | 用户给定其本地路径 |

> token 永远从 `git remote -v` 取、绝不写进任何文件——见下「铁律」。

Step 8 用本文件。产物要落到**两个 git 仓库**：
1. **公开仓库**（分享）：gitcode `<gitcode-user>/<public-repo>`，本地克隆在 `repo_root`（默认 `~/workspace/<public-repo>/`）。
2. **私有归档镜像**：你的私有归档仓库下的 `tech-daily-brief/` 子树（如 `~/workspace/<私有归档仓库>/tech-daily-brief/`）。

## 铁律（来自用户全局 CLAUDE.md，违反即 bug）

- **token 只从 `git remote -v` 取**，绝不写进任何文件、commit message、命令回显或产物。你自己账号的 token 已存在于现有 remote（如 ai-docs、BoostCoreSkills 的 `fork` remote）里，可复用。
- **commit message 用英文**，标题 + 正文都英文，与开源风格一致。
- **不含任何 AI 署名**（无 `Co-Authored-By: Claude` 等）。
- **commit 身份用 `<commit-email>`**（严禁私人邮箱）。每个仓库首次提交前 `git config user.email <commit-email>`。
- **只 `git add` 本次明确产出的显式路径**，不要 `git add .` / `-A`，不要把无关 untracked 文件带进来。

## 一、首次：创建并初始化公开仓库

仅当 `repo_root` 下还没有克隆时做一次。

1. **确认远程仓库存在**。若 gitcode 上还没有 `<gitcode-user>/<public-repo>`，用 gitcode API 创建一个**公开**仓库（token 从现有 remote 取，经环境变量传，不写进命令文本里硬编码 token）：
   ```bash
   # TOKEN 从已有 remote 提取后存入 shell 变量（示例，不要回显 token）
   curl -s -X POST "https://api.gitcode.com/api/v5/user/repos" \
     -H "PRIVATE-TOKEN: $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"tech-daily-brief","private":false,"description":"按领域每天汇总 论文/资讯/上游代码 三维度动态的中文简报"}'
   ```
   > 创建公开仓库是对外动作——**首次创建前先跟用户确认仓库名与公开属性**，确认后再建。
2. **克隆 / 初始化** 到 `repo_root`：
   ```bash
   git clone "https://<gitcode-user>:$TOKEN@gitcode.com/<gitcode-user>/<public-repo>.git" <repo_root>
   # 或在已有空目录里 git init + git remote add origin <带 token 的 URL>
   cd <repo_root> && git config user.email <commit-email> && git config user.name <commit-name>
   ```
3. **建骨架 + `.gitignore`**：根 `README.md`、各关注集目录 `<标签>/`；`.gitignore` 写入 `<标签>/state/`（去重账本不进公开仓库，保持干净）：
   ```
   */state/
   .DS_Store
   ```

## 二、每期：写产物（已在 Step 6 完成）

Step 6 已把产物写到 `repo_root` 下。本步只做 add/commit/push。一个关注集每天只有**一份** daily 报告。

## 三、推送公开仓库

只 add 本期实际产出的显式路径（`<标签>` 如 `compiler-mem`，`<YYYY-MM>` 如 `2026-06`）：

```bash
cd <repo_root>
git add README.md \
        <标签>/README.md \
        <标签>/sources.profile.md \
        <标签>/daily/<YYYY-MM>/<YYYY-MM-DD>.md
git commit -m "brief: add <YYYY-MM-DD> daily brief for <标签>"
git push origin HEAD
```

commit message 示例（英文、无署名）：
- `brief: add 2026-06-28 daily brief for compiler-mem`
- 新建关注集那期可加正文一行：`Bootstrap source profile for compiler-mem (GCC/LLVM/Go/Java/AI-compiler/memory-lib).`

## 四、镜像到 ai-docs

把本期产物复制到 `aidocs_root`（`ai-docs/tech-daily-brief/`）下**同样的相对路径**，然后在 ai-docs 仓库提交。ai-docs 镜像可保留 `state/`（私有，便于跨机去重）。

```bash
# 复制本期文件（显式列出，保持同结构）
mkdir -p <aidocs_root>/<标签>/daily/<YYYY-MM>
cp <repo_root>/<标签>/daily/<YYYY-MM>/<YYYY-MM-DD>.md <aidocs_root>/<标签>/daily/<YYYY-MM>/
cp <repo_root>/<标签>/README.md                       <aidocs_root>/<标签>/
cp <repo_root>/<标签>/sources.profile.md              <aidocs_root>/<标签>/
cp <repo_root>/README.md                              <aidocs_root>/
# 在 ai-docs 仓库提交（只 add tech-daily-brief 子树的显式路径）
cd <ai-docs 仓库根>
git add tech-daily-brief/README.md \
        tech-daily-brief/<标签>/README.md \
        tech-daily-brief/<标签>/sources.profile.md \
        tech-daily-brief/<标签>/daily/<YYYY-MM>/<YYYY-MM-DD>.md
git commit -m "tech-daily-brief: archive <YYYY-MM-DD> brief for <标签>"
git push origin main
```

> ai-docs 的 remote/token 已配好（`git remote -v` 可见），直接 `git push origin main`。

## 五、失败与回退

- push 失败（网络/鉴权）→ 报告用户哪边失败、产物已在本地什么路径，**不要**把 token 写进任何重试脚本。
- 两边只成功一边 → 明确告诉用户"公开仓库已推 / ai-docs 未推（原因）"，给出手动补推命令（仍不含明文 token）。
- 公开仓库远程还不存在 → 回到"一、首次创建"，先与用户确认再建。

## 校验清单（push 前自查）

- [ ] commit message 是英文、无 AI 署名
- [ ] `git config user.email` = <commit-email>
- [ ] 只 add 了本期显式路径，`git status` 没有夹带无关文件
- [ ] 产物/命令回显里没有出现明文 token
- [ ] 公开仓库 `.gitignore` 已忽略 `*/state/`
