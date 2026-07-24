# Environment Checks

Use this reference when collecting environment information before recommending an openGauss installation method.

## Minimum Information

Collect these before choosing an install path:

- User goal: quick experience, learning, app connection testing, local persistent use, or production/HA preparation.
- OS and version.
- CPU architecture.
- CPU cores.
- Memory.
- Disk capacity and free space.
- Whether Docker or Podman is available.
- Whether the user has root or sudo privileges.
- Whether remote access is required.

If the user cannot run commands, ask for approximate values instead of blocking.

## Linux Commands

Ask the user to run only the commands needed for the current decision:

```bash
cat /etc/os-release
uname -m
lscpu
free -h
df -h
id
sudo -v
docker --version
podman --version
```

Use `sudo -v` only when the native package path or system-level changes may be needed.

## How To Interpret Results

Architecture:

- `x86_64` means x86_64 packages/images are needed.
- `aarch64` means ARM packages/images are needed.
- Other architectures are not a normal first-path target. Prefer container only if an official matching image exists.

Memory:

- Around 2C4G: learning and light testing only.
- Around 4C8G: ordinary local use and application connection testing.
- 8C16G or higher: comfortable local use, still not automatically production.

Disk:

- Require enough free space for binaries, data, WAL, and logs.
- Warn if the target data filesystem is close to full.
- Prefer faster storage for the data directory when available.
- For containers, confirm the host volume path has enough free space.

Privileges:

- Container installation may not need root if Docker/Podman is already usable by the current user.
- Simplified package installation usually needs privilege for dependencies, users, directories, or service setup.
- If the user lacks privileges and has Docker/Podman, prefer container installation.

OS:

- If OS support is unclear or mismatched for the native package, prefer container installation.
- If the user wants native installation, ask them to confirm the target openGauss version and supported OS list from the matching documentation or official download page.

## Missing Information Handling

When output is incomplete, do not guess silently. Say what is missing and why it matters:

- OS/version determines package compatibility.
- Architecture determines package/image choice.
- Memory and CPU determine post-install configuration.
- Disk determines data/log placement and safety.
- Runtime availability determines whether container installation is low-friction.

Ask for the single most important missing item next.
