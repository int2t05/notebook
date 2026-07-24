---
name: env-deploy-for-cc
description: Use in Claude Code when asked to automatically deploy a local or cloned Linux code project's runtime environment, including project detection, dependency planning, optional command execution, build, unit-test verification, reproducible setup script generation, deployment logging, and final reporting. Supports C++, Python, Go, Java, and Docker projects. Must pause for driver conflicts, unresolved test failures, credentials, and ambiguous project or build-tool choices.
allowed-tools: "Read Write Edit Bash Glob Grep"
metadata:
  version: "1.0.0"
  short-description: "Automate Linux project environment deployment"
---

# env-deploy-for-cc

Use this Skill in Claude Code to deploy a project's Linux runtime environment and produce reproducible artifacts. Prefer the bundled scripts for repeatable work, and use Claude Code's file tools for inspection, planning files, and targeted follow-up fixes.

## Claude Code Ground Rules

- Use `task_plan.md`, `findings.md`, and `progress.md` in the active workspace for long-running deployment work. Update them after discovery, after each phase, and after any error.
- Use `Read`, `Glob`, and `Grep` before executing install/build commands.
- Use `Bash` for the bundled automation scripts and project commands.
- Use `Write` or `Edit` only for planning files, generated deployment artifacts, or targeted project changes explicitly needed to unblock deployment.
- Never hide failed commands. Record failures in `deploy.log`, `progress.md`, and the final summary.

## Scope

Use this Skill for Linux projects that are C++, Python, Go, Java, Docker, or a clear combination of those types. Do not use it for Windows, macOS, remote SSH deployment, conda-based environment management, unsupported project types, or running C++/Python/Go/Java deployment inside Docker unless the user explicitly changes scope.

## Resolve Skill Directory

Before running scripts, resolve the Skill directory:

```bash
if [ -n "${CLAUDE_SKILL_ROOT:-}" ]; then
  SKILL_DIR="$CLAUDE_SKILL_ROOT"
elif [ -f "skills/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$PWD/skills/env-deploy-for-cc"
elif [ -f ".claude-plugin/skill/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$PWD/.claude-plugin/skill/env-deploy-for-cc"
elif [ -f "$HOME/.claude/skills/env-deploy-for-cc/SKILL.md" ]; then
  SKILL_DIR="$HOME/.claude/skills/env-deploy-for-cc"
elif [ -f "$HOME/.claude/skills/env_deploy_for_cc/SKILL.md" ]; then
  SKILL_DIR="$HOME/.claude/skills/env_deploy_for_cc"
else
  echo "Cannot find env-deploy-for-cc skill directory" >&2
  exit 1
fi
```

Use `"$SKILL_DIR/scripts/env_deploy.py"` and `"$SKILL_DIR/scripts/detect_project.py"` after this.

## Core Workflow

1. **Initialize planning files**
   - If the task is more than a quick detection, create or update `task_plan.md`, `findings.md`, and `progress.md`.
   - Capture the target project path, source type, deployment mode, confirmation gates, and known constraints.

2. **Confirm project source**
   - For a local absolute path, work in that project directly.
   - For a Git URL, let the automation clone only when `--apply` is provided.
   - If source location is missing or inaccessible, ask the user for the project path or repository URL.

3. **Run automated detection**
   ```bash
   python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
   ```
   If the output reports ambiguous project type or Java build tool ambiguity, ask the user unless the prompt already gives the choice.

4. **Plan deployment**
   ```bash
   python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
   ```
   Dry-run is the default. It plans commands and writes `deploy.log`, `setup.sh`, and `deploy-report.md` to the target project root.

5. **Apply deployment when appropriate**
   ```bash
   python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply
   ```
   Add `--install-system-packages` only after reviewing the planned package-manager commands. Use `--component-type` and `--java-tool` to resolve ambiguity explicitly.

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

When pausing, show the current state, requested state, risk or impact, and available choices. Continue only after an explicit user decision.

## Reference Loading

- Read `references/automation.md` before using or extending bundled scripts.
- Read `references/project-detection.md` when interpreting project type, build tool, or unit-test triggers.
- Read `references/dependency-and-runtime.md` before installing dependencies, drivers, language runtimes, or Docker.
- Read `references/safety-and-interaction.md` before high-risk changes or unresolved failures.
- Read `references/outputs.md` before reviewing `deploy.log`, `setup.sh`, or the final report.

## Output Discipline

Generated deployment artifacts go in the target project root, not in the Skill directory. The generated `setup.sh` must contain only repeatable commands. Redact credentials from logs, reports, planning files, and final answers.
