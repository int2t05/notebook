# Dependency And Runtime Guidance

Use this reference when installing system packages, drivers, language runtimes, or Docker.

## Linux Package Managers

Detect the distribution from `/etc/os-release`.

| Distribution | Package Manager |
|--------------|-----------------|
| Ubuntu / Debian | `apt` |
| CentOS / RHEL | `yum` or `dnf` |

Install system packages only when required by build files, README/INSTALL, or compiler errors. Prefer minimal packages and record each package in `deploy.log` and `setup.sh`.

For SSH deployments, detect and install packages on the remote Linux server only when `--apply` is used. Dry-run does not connect to the remote host, and system package installation remains opt-in through `--install-system-packages`.

## Dependency Discovery Priority

1. Parse structured build and dependency files.
2. Read README/INSTALL for missing system packages, drivers, environment variables, and private repository requirements.
3. Use compiler or installer errors to identify one missing dependency at a time.

| Type | Primary Files |
|------|---------------|
| C++ | `CMakeLists.txt`, `Makefile`, `conanfile.txt`, `vcpkg.json` |
| Python | `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` |
| Go | `go.mod`, `go.sum` |
| Java | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| Docker | `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml` |

## Driver Handling

Supported driver categories:

- NVIDIA GPU driver
- CUDA and cuDNN
- Other drivers explicitly required by build files or documentation

For NVIDIA/CUDA/cuDNN, detect current host versions and required versions before installing. If a required version conflicts with an installed version and cannot coexist, stop and ask the user before continuing. Never uninstall or overwrite existing drivers automatically.

## Python

- Detect Python version from `.python-version`, `pyproject.toml` `requires-python`, or README.
- If the required Python version is unavailable, ask the user to install it manually unless a safe package-manager installation is clearly available.
- Create `.venv` in the project root.
- Install dependencies inside `.venv` only.
- Verify key imports when dependencies expose obvious package names.
- Prefer `pytest` when project configuration or dependencies indicate pytest; otherwise use `python -m unittest`.

## Go

- Read the `go` field in `go.mod` for the minimum required version.
- If the host Go version satisfies the requirement, use it.
- If not, prefer an official Go binary installation in an independent path and adjust `PATH` for the deployment session.
- Do not overwrite the system Go installation.
- In module mode, run `go mod download`; run `go mod tidy` only when the user accepts changes to module files or when the project expects it.
- If dependency download fails because of network restrictions, suggest configuring `GOPROXY`, for example `https://goproxy.cn`.

## Java

- Detect JDK version from Maven compiler settings, Gradle compatibility settings, `.java-version`, or README.
- Install missing JDK versions with the system package manager when available.
- Do not delete existing JDKs.
- Use `update-alternatives` during deployment when necessary and restore the original default JDK afterwards.
- Prefer `mvnw` or `gradlew` wrappers over system Maven or Gradle.
- If dependency resolution fails for private repositories, ask the user to check `settings.xml`, `gradle.properties`, or repository credentials.

## Docker

- Check whether Docker Engine is installed and running.
- If missing, install Docker Engine through the distribution-appropriate package manager.
- Install Docker Compose when Compose files are present.
- Pull images before build/start when possible.
- Validate container startup with the project-defined health check, `docker compose ps`, logs, or a documented smoke test.
