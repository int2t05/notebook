# Automation Reference

The bundled scripts automate the repeatable parts of environment deployment while preserving explicit user confirmation for risky decisions.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/detect_project.py` | Inspect markers and print project detection JSON. |
| `scripts/env_deploy.py` | Detect, plan, optionally execute commands, and generate artifacts. |

## Execution Modes

Default mode is dry-run:

```bash
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project
```

Dry-run mode:

- Detects project type and build tool.
- Plans build, dependency, and test commands.
- Writes `deploy.log`, `setup.sh`, and `deploy-report.md`.
- Does not execute project commands.
- In SSH mode, does not connect to the remote host; provide `--component-type` to preview useful commands.

Apply mode:

```bash
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply
```

Apply mode executes planned project-level commands until the first failure. It records command output in `deploy.log`, includes successful repeatable commands in `setup.sh`, and writes a structured report.

System package installation is opt-in:

```bash
python3 "$SKILL_DIR/scripts/env_deploy.py" --project /path/to/project --apply --install-system-packages
```

Use this only after reviewing planned package-manager commands.

## SSH Remote Mode

SSH mode targets a project path that already exists on a remote Linux server. It does not upload files, clone repositories remotely, or overwrite the remote directory.

```bash
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python
python3 "$SKILL_DIR/scripts/env_deploy.py" --remote-host user@host --remote-project /srv/app --component-type python --apply
```

Remote options:

- `--remote-host user@host`: SSH target.
- `--remote-project /absolute/path`: existing project directory on the remote server.
- `--remote-port 22`: SSH port.
- `--remote-key ~/.ssh/id_ed25519`: private key path passed to `ssh -i`; key contents are never logged.
- `--remote-ssh-option KEY=VALUE`: additional OpenSSH `-o` option; repeat as needed.
- `--output-dir ./artifacts`: local artifact directory. SSH mode defaults to `./env-deploy-remote-artifacts`.

In `--apply`, commands execute as `ssh ... 'cd /remote/project && <command>'`. The generated `setup.sh` intentionally omits SSH wrapping so it can be run directly inside the remote project directory.

## Ambiguity Controls

Use explicit flags when detection finds multiple plausible paths:

```bash
--component-type cpp|python|go|java|docker
--java-tool maven|gradle
```

If these flags are omitted, the script follows the documented project-type priority for planning and records a warning. Java Maven/Gradle ambiguity blocks Java automation until `--java-tool` is supplied.

## Generated Artifacts

The script writes artifacts to the target project root for local deployments. SSH mode writes artifacts to the local output directory:

- `deploy.log`
- `setup.sh`
- `deploy-report.md`

Generated `setup.sh` includes only planned or successful repeatable commands. Failed exploratory commands and secrets are excluded.

## Safety Boundaries

The automation does not perform automatic driver replacement, destructive package-manager cleanup, credential entry, SSH host key acceptance, remote code upload, remote clone, or code fixes. When a required tool is missing or a command fails, it records the issue and stops or skips as appropriate so the agent can apply the Skill's interaction rules.

## Trae Path Resolution

Set `SKILL_DIR` before invoking scripts:

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

For workspace-local Trae Skills, copy this folder to `.trae/skills/env-deploy-for-trae/`. This repository also mirrors the same content under `.trae/skill/env-deploy-for-trae/` for platform-specific packaging.

## Trae Context Guidance

Use Trae's context references before applying deployment commands:

- Add `#Workspace` when first inspecting an unfamiliar project.
- Add `#Folder` for the target project root or relevant component.
- Add `#File` for build files, dependency manifests, README/INSTALL files, and deployment logs.
- Ensure the code index has completed before relying on `#Folder` or `#Workspace`.
