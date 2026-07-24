---
name: env-deploy-for-codex
description: Use when asked to automatically deploy a local or cloned code project's runtime environment on Linux, including project detection, dependency planning, optional command execution, build, unit-test verification, reproducible setup script generation, and deployment reporting. Supports C++, Python, Go, Java, and Docker projects, with required user confirmation for destructive driver changes, unresolved test failures, and ambiguous project or build-tool detection.
---

# env-deploy-for-codex

Deploy a code project's runtime environment on Linux in Codex and leave behind reproducible deployment artifacts. Prefer the bundled automation scripts for detection, planning, execution, logging, report generation, and `setup.sh` generation.

## Scope

Use this Skill for Linux projects that are C++, Python, Go, Java, Docker, or a clear combination of those types. Do not use it for Windows, macOS, remote SSH deployment, conda-based environment management, unsupported project types, or running C++/Python/Go/Java deployment inside Docker unless the user explicitly changes scope.

## Core Workflow

1. **Confirm project source**
   - If the user provides a local absolute path, work in that project directly.
   - If the user provides a Git URL, clone it locally. Use SSH for `git@...` URLs and HTTPS/token credentials for `https://...` URLs.
   - If source location is missing or inaccessible, ask the user for the project path or repository URL.

2. **Run automated detection**
   - Resolve the Skill directory, then run detection:
     ```bash
     if [ -n "${SKILL_DIR:-}" ]; then
       :
     elif [ -f "skills/env-deploy-for-codex/SKILL.md" ]; then
       SKILL_DIR="$PWD/skills/env-deploy-for-codex"
     elif [ -f ".codex/skill/env-deploy-for-codex/SKILL.md" ]; then
       SKILL_DIR="$PWD/.codex/skill/env-deploy-for-codex"
     elif [ -f "$HOME/.codex/skills/env-deploy-for-codex/SKILL.md" ]; then
       SKILL_DIR="$HOME/.codex/skills/env-deploy-for-codex"
     else
       echo "Cannot find env-deploy-for-codex skill directory" >&2
       exit 1
     fi

     python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty
     ```
   - For full automation planning, run:
     ```bash
     python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
     ```
   - Add `--apply` only when the user wants commands executed on the host.

3. **Detect project type**
   - Inspect project markers and README/INSTALL files before executing installation commands.
   - Use the priority and ambiguity rules in `references/project-detection.md`.
   - If multiple plausible project types or Java build tools are present and the expected path is unclear, pause and ask the user to choose.

4. **Identify dependencies and runtime requirements**
   - Prefer structured build files and lock files.
   - Supplement with `README.md` and `INSTALL.md` when build files do not expose system packages, drivers, or setup steps.
   - Use `references/dependency-and-runtime.md` for language-specific and system dependency guidance.

5. **Deploy with isolation and minimal host impact**
   - Detect the Linux distribution and package manager.
   - Preserve the existing host environment as much as possible.
   - Use Python virtual environments, independent Go installations, and Java alternatives instead of deleting or overwriting existing runtimes.
   - Never uninstall or replace drivers without explicit user confirmation.

6. **Build and run unit tests**
   - Build with the detected project toolchain.
   - Run unit tests only when trigger conditions are met.
   - If failures appear environment-related, try one targeted repair and rerun.
   - If failures cannot be safely resolved, follow `references/safety-and-interaction.md`.

7. **Create output artifacts**
   - Write deployment artifacts to the target project root, not to the Skill directory.
   - Produce `deploy.log`, `setup.sh`, and a structured terminal summary.
   - Use `references/outputs.md` and the files in `templates/` for expected formats.

## Automation Commands

Use these scripts from the repository or installed Skill directory:

```bash
# Detection only
python3 "$SKILL_DIR/scripts/detect_project.py" /path/to/project --pretty

# Dry-run: plan commands and generate deploy.log/setup.sh/deploy-report.md
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project

# Apply safe project-level automation
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply

# Include package-manager system package installation
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply --install-system-packages

# Resolve ambiguity explicitly
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type python --apply
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --component-type java --java-tool maven --apply
```

The automation writes artifacts into the target project root. Default mode is dry-run so the agent can inspect planned commands before applying.

## Required Pause Points

Pause and ask the user before proceeding when:

- Driver or system-level component versions conflict and cannot safely coexist.
- Unit tests fail and the failure cannot be automatically repaired with a narrow environment fix.
- Project type detection is ambiguous.
- A Java project contains both Maven and Gradle markers and no clear preference.
- A necessary credential, token, private package repository setting, or manual runtime installation is missing.

When pausing, show the current state, the requested state, risk or impact, and the available choices. Continue only after the user gives an explicit decision.

## Reference Loading

- Read `references/project-detection.md` when identifying project type, build tool, or unit-test triggers.
- Read `references/dependency-and-runtime.md` when installing dependencies, drivers, language runtimes, or Docker.
- Read `references/safety-and-interaction.md` before any high-risk change or unresolved failure decision.
- Read `references/outputs.md` before creating `deploy.log`, `setup.sh`, or the final deployment summary.
- Read `references/automation.md` when using or extending the bundled scripts.

## Output Discipline

Record every effective command and result. The final `setup.sh` must be idempotent, commented, and limited to commands that are safe to repeat. The final summary must separate successful, failed, skipped, and warning items.
