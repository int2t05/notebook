# env-deploy Skill Collection

`env-deploy` is a multi-platform Skill collection for automating Linux project environment deployment. It helps an AI coding agent inspect a project, plan setup commands, optionally execute safe deployment steps, run applicable tests, and produce reproducible deployment artifacts.

`env-deploy` 是一组多平台适配的 Skill，用于自动化部署 Linux 代码项目运行环境。它可以帮助 AI 编程助手识别项目类型、规划环境部署命令、按需执行安全步骤、运行适用测试，并生成可复现的部署产物。

## Which Version / 版本选择

| Version | Target platform | Directory | Metadata style | Use when |
|---------|-----------------|-----------|----------------|----------|
| Universal | Any Agent Skills-compatible framework | `skills/env-deploy/` | Minimal `SKILL.md` only | You want lightweight framework-neutral deployment guidance. |
| Codex | OpenAI Codex / Codex-style Skills | `skills/env-deploy-for-codex/` | `SKILL.md` + `agents/openai.yaml` | You want OpenAI/Codex UI metadata, default prompt support, and bundled automation scripts. |
| Claude Code | Claude Code | `skills/env-deploy-for-cc/` | `SKILL.md` with Claude Code fields | You want Claude Code-oriented tool guidance and local Skill loading. |
| Trae | Trae | `skills/env-deploy-for-trae/` | `SKILL.md` with Trae compatibility metadata | You want Trae context usage such as `#File`, `#Folder`, and `#Workspace`. |

`skills/env-deploy/` is the minimal universal version. Prefer one of the platform-specific directories when you want bundled automation scripts or agent-specific metadata.

`skills/env-deploy/` 是最小通用版本。需要自动化脚本或平台专属元数据时，建议选择上表中的平台专用目录。

## Capabilities / 核心能力

- Detect C++, Python, Go, Java, and Docker project markers.
- Plan build, dependency, runtime, and unit-test commands.
- Plan or apply deployment commands on an SSH-accessible Linux server when the project already exists remotely.
- Default to dry-run mode so commands can be reviewed before execution.
- Execute project-level automation only when `--apply` is provided.
- Keep system package installation opt-in through `--install-system-packages`.
- Generate `deploy.log`, `setup.sh`, and `deploy-report.md` in the target project root.
- Preserve manual confirmation gates for risky or ambiguous operations.

能力概览：

- 自动识别 C++、Python、Go、Java、Docker 项目标识。
- 规划构建、依赖、运行时和单元测试命令。
- 当项目已存在于远程服务器时，可通过 SSH 规划或执行部署命令。
- 默认 dry-run，先生成计划再由用户决定是否执行。
- 只有显式传入 `--apply` 才会执行项目级自动化。
- 系统包安装必须额外传入 `--install-system-packages`。
- 在目标项目根目录生成 `deploy.log`、`setup.sh`、`deploy-report.md`。
- 对高风险或歧义场景保留人工确认门。

## Safety Gates / 安全边界

The automation must pause and ask for an explicit user decision before continuing when:

- Driver, CUDA, or cuDNN versions conflict and cannot safely coexist.
- Unit tests fail and cannot be fixed with a narrow environment-only repair.
- Project type detection is ambiguous.
- A Java project has both Maven and Gradle markers without a clear preference.
- Credentials, private repository settings, or manual runtime installation are required.
- SSH host key trust, private key passphrase, SSH password, sudo password, or remote project permissions require manual handling.

以下情况必须暂停并等待用户明确确认：

- 驱动、CUDA 或 cuDNN 版本存在不可安全共存的冲突。
- 单元测试失败，且无法通过狭窄的环境修复自动解决。
- 项目类型识别存在歧义。
- Java 项目同时存在 Maven 和 Gradle 标识且缺少明确偏好。
- 需要凭据、私有仓库配置或手动安装运行时。
- 需要处理 SSH 主机信任、私钥口令、SSH 密码、sudo 密码或远程项目权限。

The scripts do not automatically replace drivers, perform destructive package-manager cleanup, enter credentials, or fix application code.

脚本不会自动替换驱动、执行破坏性包管理器清理、输入凭据或修复业务代码。

## Quick Start / 快速开始

### Install with npx / 使用 npx 安装

Install interactively from the GitCode git source:

从 GitCode git 源交互式安装：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth
```

Install all three Skill variants globally without prompts:

非交互式全局安装全部三个 Skill 版本：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill '*' --agent '*' -g -y
```

Install for a specific agent:

安装到指定 Agent：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill env-deploy -g -y
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill env-deploy-for-codex -a codex -g -y
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill env-deploy-for-cc -a claude-code -g -y
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill env-deploy-for-trae -a trae -g -y
```

List available Skills without installing:

只查看可安装 Skill，不执行安装：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --list
```

The repository uses the standard `skills/<skill-name>/` layout under `env-deploy/`. Use the `.git` source and `--full-depth` so `npx skills add` clones the GitCode repository and discovers each variant.

本仓库在 `env-deploy/` 下使用标准 `skills/<skill-name>/` 布局。使用 `.git` 源和 `--full-depth` 可让 `npx skills add` 克隆 GitCode 仓库并发现各平台版本。

### Run from this repository / 在本仓库中运行

Choose the directory that matches your agent platform, then resolve `SKILL_DIR` to that directory.

先选择与你的 Agent 平台匹配的目录，然后把 `SKILL_DIR` 指向该目录。

### Codex

```bash
SKILL_DIR="$PWD/skills/env-deploy-for-codex"
if [ -f ".codex/skill/env-deploy-for-codex/SKILL.md" ]; then
  SKILL_DIR="$PWD/.codex/skill/env-deploy-for-codex"
fi

python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply
```

Codex version includes `agents/openai.yaml` for UI metadata and default prompt behavior.

Codex 版本包含 `agents/openai.yaml`，用于 UI 元数据和默认 prompt。

### Claude Code

```bash
if [ -n "${CLAUDE_SKILL_ROOT:-}" ]; then
  SKILL_DIR="$CLAUDE_SKILL_ROOT"
elif [ -f "skills/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$PWD/skills/env-deploy-for-cc"
elif [ -f ".claude-plugin/skill/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$PWD/.claude-plugin/skill/env-deploy-for-cc"
elif [ -f "$HOME/.claude/skills/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$HOME/.claude/skills/env-deploy-for-cc"
fi

python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
```

Claude Code version includes Claude Code-oriented `SKILL.md` fields and workflow guidance.

Claude Code 版本在 `SKILL.md` 中包含面向 Claude Code 的字段和工作流说明。

### Trae

```bash
if [ -n "${TRAE_SKILL_ROOT:-}" ]; then
  SKILL_DIR="$TRAE_SKILL_ROOT"
elif [ -f "skills/env-deploy-for-trae/SKILL.md" ]; then
  SKILL_DIR="$PWD/skills/env-deploy-for-trae"
elif [ -f ".trae/skill/env-deploy-for-trae/SKILL.md" ]; then
  SKILL_DIR="$PWD/.trae/skill/env-deploy-for-trae"
elif [ -f ".trae/skills/env-deploy-for-trae/SKILL.md" ]; then
  SKILL_DIR="$PWD/.trae/skills/env-deploy-for-trae"
elif [ -f "$HOME/.trae/skills/env-deploy-for-trae/SKILL.md" ]; then
  SKILL_DIR="$HOME/.trae/skills/env-deploy-for-trae"
fi

python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
```

Trae version can be installed with `npx skills add` or copied to `.trae/skills/env-deploy-for-trae/`. Use Trae context references such as `#File`, `#Folder`, and `#Workspace` after the project index is ready.

Trae 版本可通过 `npx skills add` 安装，也可复制到 `.trae/skills/env-deploy-for-trae/`。在项目索引完成后，可使用 `#File`、`#Folder`、`#Workspace` 补充上下文。

## Common Commands / 通用命令

```bash
# Detection only / 仅检测
python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty

# Dry-run planning / dry-run 规划
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project

# Apply project-level automation / 执行项目级自动化
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply

# Include package-manager installation after review / 审核后包含系统包安装
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply --install-system-packages

# SSH dry-run for an existing remote project path / 对已有远程项目路径执行 SSH dry-run
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python

# SSH apply on the remote Linux server / 在远程 Linux 服务器上通过 SSH 执行
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python --apply

# SSH with port, key, and OpenSSH options / 使用端口、私钥和 OpenSSH 选项
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --remote-port 2222 --remote-key ~/.ssh/id_ed25519 --remote-ssh-option ServerAliveInterval=30 --component-type python

# Resolve ambiguity / 显式解决歧义
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type python --apply
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type java --java-tool maven --apply
```

## Repository Layout / 仓库结构

Each adapted Skill has the same core resource layout:

各适配版 Skill 都使用相同的核心资源结构：

```text
skills/
├── env-deploy/
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   └── assets/
├── env-deploy-for-codex/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── scripts/
│   ├── templates/
│   └── assets/
├── env-deploy-for-cc/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   ├── templates/
│   └── assets/
└── env-deploy-for-trae/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    ├── templates/
    └── assets/
```

Platform compatibility mirrors are also kept in sync:

平台兼容镜像目录也会保持同步：

```text
.codex/skill/env-deploy-for-codex/
.claude-plugin/skill/env-deploy-for-cc/
.trae/skill/env-deploy-for-trae/
```

- `SKILL.md`: platform-specific agent instructions and activation metadata.
- `references/`: detailed guidance for detection, dependencies, safety, automation, and outputs.
- `scripts/`: executable automation helpers.
- `templates/`: reusable output templates such as `setup.sh` and report formats.
- `assets/`: reserved for future assets.

说明：

- `SKILL.md`：平台专属的 Agent 指令和激活元数据。
- `references/`：项目识别、依赖、风险控制、自动化和输出产物的详细说明。
- `scripts/`：可执行自动化辅助脚本。
- `templates/`：`setup.sh`、报告格式等可复用模板。
- `assets/`：预留给未来资产。

## Generated Artifacts / 输出产物

The deployment helper writes artifacts to the target project root:

部署辅助脚本会把产物写入目标项目根目录：

- `deploy.log`: full command log, timestamps, outputs, exit codes, and decisions.
- `setup.sh`: repeatable setup script generated from planned or successful commands.
- `deploy-report.md`: structured summary of success, failure, skipped steps, and warnings.
- SSH mode writes artifacts locally, defaulting to `./env-deploy-remote-artifacts`, while `setup.sh` remains a script intended to run inside the remote project directory.

- `deploy.log`：完整命令日志、时间戳、输出、退出码和决策记录。
- `setup.sh`：由规划或成功命令生成的可重复执行安装脚本。
- `deploy-report.md`：成功、失败、跳过和警告项的结构化汇总。
- SSH 模式会把产物写到本地，默认目录为 `./env-deploy-remote-artifacts`；其中 `setup.sh` 仍是供远程项目目录内直接执行的脚本。

## Current Limitations / 当前限制

- Linux only.
- No Windows or macOS support.
- SSH mode requires an existing remote project path; it does not upload code, clone remotely, or auto-accept host keys.
- No conda environment management.
- No automatic driver replacement.
- No automatic code fixes.

- 仅支持 Linux。
- 不支持 Windows 或 macOS。
- SSH 模式要求远程项目路径已存在；不会上传代码、远程 clone 或自动接受主机密钥。
- 不支持 conda 环境管理。
- 不自动替换驱动。
- 不自动修复业务代码。

## TODO / 后续计划

- Validate each adapted Skill in its real target platform.
- Improve dependency inference from `README.md` and `INSTALL.md`.
- Add optional CUDA/cuDNN detection helpers that never install drivers without confirmation.
- Improve failure classification in `deploy-report.md`.
- Add optional platform-specific companion docs or rules only when needed.

- 在真实目标平台中验证每个适配版 Skill。
- 增强从 `README.md` 和 `INSTALL.md` 推断依赖的能力。
- 增加可选 CUDA/cuDNN 检测辅助脚本，但仍不在未确认时安装驱动。
- 改进 `deploy-report.md` 的失败分类。
- 仅在确有需要时添加平台专属 companion 文档或规则。
