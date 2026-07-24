# Installation Methods

Use this reference after collecting the user's goal and environment.

## Method Selection

Recommend container installation when:

- The user wants quick experience or learning.
- Docker or Podman is already available.
- The host OS is not clearly compatible with native openGauss packages.
- The user wants to avoid system dependency setup.
- The user cannot or should not modify system users, services, or kernel parameters.

Recommend simplified package installation when:

- The user wants native openGauss tools and layout.
- The user needs persistent data outside a container runtime.
- OS and CPU architecture match available packages.
- The user can install dependencies and prepare users/directories.
- The user wants to inspect or tune native configuration files directly.

## Version And Source Strategy

Before producing concrete package, image, or script commands, establish:

- Target openGauss version.
- CPU architecture.
- Host OS and version for native packages.
- Container runtime and image registry for container installs.
- Whether the user needs the newest release, a specific project-required version, or a stable version from their organization.

Do not rely on memory for package names, image tags, image environment variables, or installer script flags. Ask the user to confirm the current official source:

- Official openGauss download page for native packages.
- Official openGauss image source or registry page for container images.
- Package-bundled README, help output, or `simpleInstall/` script help for package-specific installation flags.

Use this decision rule:

1. If the exact version/source is known from user-provided output, proceed with that value.
2. If the user only says "latest", ask whether "latest acceptable test version" is fine and still have them verify the current tag/package.
3. If the user cannot verify sources, give a placeholder-based command shape and clearly mark values that must be replaced.
4. If package/image docs conflict with this skill, follow the package/image docs.

Safe prompt to the user:

```text
Please confirm the openGauss version and source you want to use. Paste either the package filename, the image tag, or the official page line that shows the version for your OS/architecture.
```

## Container Installation Guidance

Before giving commands, confirm:

- Target openGauss version or "latest acceptable test version".
- CPU architecture.
- Container runtime: Docker or Podman.
- Host port to expose.
- Initial password requirements.
- Host path for persistent data.

Use placeholders instead of stale image names when the exact image/tag has not been confirmed:

```bash
IMAGE="<official-opengauss-image>:<version-tag>"
CONTAINER_NAME="opengauss"
HOST_PORT="5432"
DATA_DIR="$HOME/opengauss-data"
CONTAINER_DATA_DIR="<data-path-documented-by-the-selected-image>"
PASSWORD_ENV_NAME="<password-env-var-documented-by-the-selected-image>"
```

Tell the user to replace `IMAGE`, `CONTAINER_DATA_DIR`, and `PASSWORD_ENV_NAME` with values from the current official image documentation for their version and architecture.

Typical Docker shape:

```bash
mkdir -p "$DATA_DIR"
docker pull "$IMAGE"
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$HOST_PORT":5432 \
  -v "$DATA_DIR":"$CONTAINER_DATA_DIR" \
  -e "$PASSWORD_ENV_NAME=<strong-password>" \
  "$IMAGE"
docker ps
docker logs --tail 100 "$CONTAINER_NAME"
```

Expected result:

- Container is `Up`.
- Logs show database initialization or startup completed.
- Host data directory receives persistent files.

If it fails:

- Check `docker logs`.
- Check password policy messages.
- Check whether `HOST_PORT` is already used.
- Check whether the host volume path is writable.
- Check whether the image/tag matches the CPU architecture.

## Simplified Package Installation Guidance

Before giving commands, confirm:

- Target openGauss version.
- OS and CPU architecture.
- Whether the user has root/sudo.
- Installation directory.
- Data directory.
- Port.

Use placeholders when package names are version-specific:

```bash
OPEN_GAUSS_PACKAGE="<openGauss-server-package-for-os-and-arch>.tar.bz2"
INSTALL_DIR="<install-dir>"
DATA_DIR="<data-dir>"
LOG_DIR="<log-dir>"
PORT="5432"
```

Guide the user to download the package that exactly matches their openGauss version, OS, and architecture. Ask the user to choose `INSTALL_DIR`, `DATA_DIR`, and `LOG_DIR` based on their filesystem layout instead of assuming standard Linux paths.

Typical staged flow:

1. Verify package and extract it.
2. Install missing dependencies using the OS package manager.
3. Create or choose the runtime user.
4. Prepare directories and permissions.
5. Check whether the extracted package includes a documented simplified install script.
6. Initialize and start the database using the documented script or commands for that package.
7. Connect locally and verify status.

Keep commands specific to the package's documented install flow. Do not invent flags for `gs_initdb`, `gs_ctl`, or installer scripts when the exact package layout is unknown. If needed, ask the user to paste the extracted directory listing:

```bash
tar -tjf "$OPEN_GAUSS_PACKAGE" | head -50
```

If the extracted package contains `simpleInstall/`, inspect that directory before giving install commands:

```bash
find simpleInstall -maxdepth 2 -type f -print
```

Then guide the documented script for that package and version. Ask the user to paste the script help or README if the command line is unclear:

```bash
sh simpleInstall/install.sh --help
```

Verification commands may include:

```bash
ps -ef | grep gaussdb
ss -lntp | grep "$PORT"
gsql --version
```

For package-specific commands, ask the user for the target version and extracted files before proceeding.

## Stage Boundaries

Do not give container and native full command paths at the same time unless the user asks for a comparison. Once a method is chosen, guide one stage at a time.
