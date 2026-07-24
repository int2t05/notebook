---
name: env-deploy-for-trae
description: Use in Trae when asked to automatically deploy a local, cloned, or SSH-remote Linux code project's runtime environment, including project detection, dependency planning, optional command execution, build, unit-test verification, reproducible setup script generation, deployment logging, and final reporting. Supports C++, Python, Go, Java, and Docker projects. Must pause for driver conflicts, unresolved test failures, credentials, and ambiguous project or build-tool choices.
metadata:
  version: "1.0.0"
  category: "devops"
  tags:
    - "trae"
    - "environment"
    - "deployment"
    - "automation"
  compatibility:
    - "trae"
---

# env-deploy-for-trae

Use this Skill in Trae to deploy a project's Linux runtime environment and produce reproducible artifacts. Prefer the bundled scripts for repeatable detection, dry-run planning, optional execution, logging, `setup.sh` generation, and deployment reporting.

## Trae Usage

- Install or copy this directory to `.trae/skills/env-deploy-for-trae/` when using workspace-local Trae Skills.
- You can also reference this repository-local folder directly as context while iterating on the Skill.
- Before deployment, let Trae finish building the project index so `#Workspace` and `#Folder` references are reliable.
- Use Trae context tools intentionally:
  - `#File` for build files such as `pyproject.toml`, `go.mod`, `pom.xml`, `Dockerfile`, or `CMakeLists.txt`.
  - `#Folder` for project roots, `tests/`, deployment docs, or component directories.
  - `#Workspace` when identifying a new repository's structure.

## Scope

Use this Skill for local Linux projects or SSH-accessible remote Linux servers that are C++, Python, Go, Java, Docker, or a clear combination of those types. Do not use it for Windows, macOS, conda-based environment management, unsupported project types, remote code upload, remote clone, or running C++/Python/Go/Java deployment inside Docker unless the user explicitly changes scope.

## Resolve Skill Directory

Before running scripts, resolve the Skill directory:

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
elif [ -f "$HOME/.trae/skills/env_deploy_for_trae/SKILL.md" ]; then
  SKILL_DIR="$HOME/.trae/skills/env_deploy_for_trae"
else
  echo "Cannot find env-deploy-for-trae skill directory" >&2
  exit 1
fi
```

Use `"$SKILL_DIR/scripts/env_deploy.py"` and `"$SKILL_DIR/scripts/detect_project.py"` after this.

## Core Workflow

1. **Initialize planning files**
   - For multi-step deployment, create or update `task_plan.md`, `findings.md`, and `progress.md` in the active workspace.
   - Capture the target project path, source type, dry-run/apply mode, confirmation gates, and known constraints.

2. **Confirm project source**
   - For a local absolute path, work in that project directly.
   - For a Git URL, let automation clone only when `--apply` is provided.
   - For SSH mode, require both `--remote-host` and `--remote-project`. Treat the remote project path as already present on that Linux server; do not upload code, clone remotely, or overwrite the remote directory.
   - If source location is missing or inaccessible, ask the user for the project path or repository URL.

3. **Run automated detection**
   ```bash
   python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
   ```
   If output reports ambiguous project type or Java build tool ambiguity, ask the user unless the prompt already gives the choice.

4. **Plan deployment**
   ```bash
   python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
   ```
   Dry-run is the default. It plans commands and writes `deploy.log`, `setup.sh`, and `deploy-report.md` to the target project root.
   For SSH dry-run, include `--remote-host`, `--remote-project`, and usually `--component-type`; dry-run does not connect to the remote host.

5. **Apply deployment when appropriate**
   ```bash
   python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply
   ```
   Add `--install-system-packages` only after reviewing package-manager commands. Use `--component-type` and `--java-tool` to resolve ambiguity explicitly.
   For SSH apply, add `--apply` to execute the planned commands on the remote Linux server over SSH.

6. **Handle failures and pause points**
   - For missing tools, dependency failures, or test failures, inspect `deploy.log` and use `references/safety-and-interaction.md`.
   - Try one narrow environment fix when safe.
   - Pause for user confirmation when the rule says to pause.

7. **Deliver artifacts**
   - Confirm the target project contains `deploy.log`, `setup.sh`, and `deploy-report.md`.
   - Summarize success, failure, skipped steps, warnings, user decisions, and remaining TODOs.

## Automation Commands

```bash
# Detection only
python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty

# Dry-run planning and artifact generation
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project

# Apply project-level automation
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply

# Include package-manager installation after review
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply --install-system-packages

# SSH dry-run for an existing remote project path
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python

# SSH apply on the remote Linux server
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python --apply

# SSH with non-default port, key, and OpenSSH option
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --remote-port 2222 --remote-key ~/.ssh/id_ed25519 --remote-ssh-option ServerAliveInterval=30 --component-type python

# Resolve ambiguity explicitly
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type python --apply
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type java --java-tool maven --apply
```

## Required Pause Points

Pause and ask the user before proceeding when:

- Driver or system-level component versions conflict and cannot safely coexist.
- Unit tests fail and the failure cannot be automatically repaired with a narrow environment fix.
- Project type detection is ambiguous.
- A Java project contains both Maven and Gradle markers and no clear preference.
- A credential, token, private package repository setting, or manual runtime installation is missing.
- SSH connection, host key trust, private key passphrase, sudo password, or remote project permissions require manual action.

When pausing, show the current state, requested state, risk or impact, and available choices. Continue only after an explicit user decision.

## Reference Loading

- Read `references/automation.md` before using or extending bundled scripts.
- Read `references/project-detection.md` when interpreting project type, build tool, or unit-test triggers.
- Read `references/dependency-and-runtime.md` before installing dependencies, drivers, language runtimes, or Docker.
- Read `references/safety-and-interaction.md` before high-risk changes or unresolved failures.
- Read `references/outputs.md` before reviewing `deploy.log`, `setup.sh`, or the final report.

## Output Discipline

Generated deployment artifacts go in the target project root, not in the Skill directory. The generated `setup.sh` must contain only repeatable commands. Redact credentials from logs, reports, planning files, and final answers.
