---
name: opengauss-install-config-advisor
description: Guide ordinary users through openGauss single-node or lightweight installation and configuration. Use when an agent needs to help check a user's Linux/container environment, choose between container installation and simplified package installation, provide staged install commands, configure local or remote access safely, troubleshoot startup or connection failures, or generate conservative resource-aware openGauss tuning suggestions based on CPU, memory, disk, storage, and runtime limits.
---

# openGauss Install Config Advisor

Use this skill to guide ordinary users through installing and configuring openGauss in single-node or lightweight scenarios. Keep the workflow platform-neutral: do not assume a specific agent runtime, plugin format, skill marketplace, or local installation directory.

## Scope

Handle:

- Container installation for quick experience, learning, and low-friction local setup.
- Simplified package installation for users who want native commands, directories, and configuration files.
- Environment checks before installation.
- Basic configuration for local use, persistence, and safe remote access.
- Conservative resource-aware tuning after installation.
- Troubleshooting for common installation, startup, and connection failures.

Do not attempt to fully design production primary-standby, CM, HA, distributed deployment, or deep workload-specific performance tuning. If the user asks for those, state the boundary and point them to the relevant openGauss installation, OM, or performance tuning documentation.

## Source Notes

When local openGauss documentation is available, prefer it over memory. Useful source areas include installation preparation, container image installation, openGauss installation, `gs_check`, `gs_checkos`, `gs_perfconfig`, connection settings, memory parameters, authentication, and performance tuning guides.

## Core Workflow

1. **Clarify the goal.** Ask whether the user wants quick experience, local single-node use, application connection testing, small persistent use, or production/HA preparation.
2. **Check the environment.** Ask for command output or approximate values for OS, CPU architecture, CPU count, memory, disk, privileges, and Docker/Podman availability. Load `references/environment-checks.md`. Load `references/opengauss-doc-facts.md` when you need openGauss documented requirements or tool behavior.
3. **Choose an install method.** Recommend container or simplified package installation using the environment and user goal. Load `references/install-methods.md`, and follow its version/source confirmation strategy before giving concrete package or image commands.
4. **Guide installation in stages.** Give only the next install block, expected result, and minimal recovery hint. Avoid dumping every path at once.
5. **Configure basics.** After installation, guide port, data directory, password, local connection, persistence, and optional remote access. Load `references/basic-config.md`.
6. **Optimize from confirmed resources.** After the server is running, summarize visible resources and generate conservative configuration suggestions. Load `references/resource-tuning.md` and, when citing openGauss tools or documented baselines, `references/opengauss-doc-facts.md`.
7. **Troubleshoot by smallest useful output.** When errors occur, ask for the next smallest useful command output or log excerpt. Load `references/troubleshooting.md`.

## Decision Rules

Recommend **container installation** when the user wants quick experience, already has Docker/Podman, has an unclear or unsupported host OS for native packages, wants to avoid system dependency setup, or should not modify system users/services/kernel parameters.

Recommend **simplified package installation** when the user wants native openGauss commands and layout, needs persistent local data outside a container runtime, has a matching OS and architecture, has enough privileges to install dependencies and prepare directories, or wants to inspect and tune native configuration files.

If both methods are viable, lead with the recommended method and briefly mention the alternative.

## Interaction Rules

- Ask only the next necessary question.
- Prefer copyable commands and short expected-output notes.
- Mark assumptions explicitly.
- Separate "required", "recommended", and "risky" settings.
- Never silently recommend public remote access. Treat `listen_addresses='*'`, broad `pg_hba.conf` CIDRs, and open firewalls as risky unless the user explicitly asks and understands exposure.
- Do not hardcode version-specific package names or image tags as timeless truth. Ask for the target openGauss version or tell the user to verify the current official download or image source.
- When the user asks for "latest", clarify whether they mean the latest acceptable test version or a specific project-required version; still require source/tag/package confirmation before concrete commands.
- Reuse openGauss tools such as `gs_check`, `gs_checkos`, and `gs_perfconfig` when available.

## Output Template

For installation guidance, prefer this shape:

```text
Assumption: ...

Step: ...
Command:
...

Expected result: ...
If it fails: ...
Next: paste the output of ...
```

For optimization guidance, prefer this shape:

```text
Resource summary:
- CPU:
- Memory:
- Disk/storage:
- Runtime:

Recommended changes:
- Setting:
  Why:
  How:
  Reload/restart:
  Verify:
```
