# Output Artifacts

Deployment artifacts are written to the target project root, not to the Skill directory.

## `deploy.log`

Record the complete deployment process:

- Timestamp
- Step name
- Working directory
- Command
- Exit code
- Standard output and error
- Error analysis and retry notes
- User decisions for conflicts, skips, or termination

Redact secrets before writing logs.

## `setup.sh`

Create a reproducible shell script from effective deployment commands.

Rules:

- Include `#!/usr/bin/env bash` and `set -euo pipefail`.
- Add comments explaining each install/configuration step.
- Make commands idempotent with version checks, file existence checks, or package-query guards.
- Do not include failed commands, exploratory diagnostics, secrets, or one-time local paths unrelated to the project.
- Preserve environment isolation such as Python `.venv`, independent Go paths, and Java alternatives restoration.

Use `templates/setup.sh` as the starter shape.

When `scripts/env_deploy.py` is used, it generates `setup.sh` automatically from planned or successful repeatable commands. Review generated commands before reusing the script on another host.

## Terminal Summary

At the end of deployment, print a structured summary with these sections:

| Category | Content |
|----------|---------|
| Success | Installed dependencies, configured runtimes, build result, passed UT |
| Failed | Failed items and root-cause analysis |
| Skipped | User-confirmed skipped steps or tests |
| Warnings | Version fallback, potential conflicts, network issues, missing optional components |

Use `templates/deploy-report.md` as a report shape when a file report is useful.

When `scripts/env_deploy.py` is used, it writes `deploy-report.md` in addition to printing the terminal summary.

## Output Review Checklist

- `deploy.log` contains every command and exit result.
- `setup.sh` contains only repeatable effective commands.
- Final summary separates success, failed, skipped, and warning items.
- Any user confirmation is recorded with enough context to understand the decision.
- Secrets are not present in artifacts.
