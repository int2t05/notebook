# Deploy Log Format

Use this format for `deploy.log` entries.

```text
================================================================================
Timestamp: 2026-04-27T00:00:00+08:00
Deployment mode: local|ssh
Remote host: user@host or blank for local
Remote project: /absolute/remote/project or blank for local
Step: short human-readable step name
Working directory: /absolute/project/path
Command:
  command arguments here
Exit code: 0
Stdout:
  command stdout here
Stderr:
  command stderr here
Analysis:
  why this command was run, what changed, and whether it should be included in setup.sh
Decision:
  user decision if this step involved a required pause point; otherwise "not required"
================================================================================
```

## Redaction Rules

- Replace tokens with `<REDACTED_TOKEN>`.
- Replace passwords with `<REDACTED_PASSWORD>`.
- Replace private repository credentials with `<REDACTED_CREDENTIAL>`.
- Never log SSH private key contents, private key passphrases, SSH passwords, or sudo passwords.
- Keep package names, versions, paths, and non-secret URLs when they are useful for reproduction.
