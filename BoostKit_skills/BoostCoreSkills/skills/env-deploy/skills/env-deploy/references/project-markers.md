# Project Markers

Use these markers to classify the project before proposing setup commands.

| Type | Common markers | Typical first checks |
| --- | --- | --- |
| Python | `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile` | Python version, virtual environment, package manager, tests |
| Go | `go.mod`, `go.sum` | Go version, module path, `go test ./...` |
| Java | `pom.xml`, `build.gradle`, `build.gradle.kts` | Maven vs Gradle, JDK version, wrapper scripts |
| C/C++ | `CMakeLists.txt`, `Makefile`, `meson.build`, `BUILD` | compiler, build directory, system libraries |
| Docker | `Dockerfile`, `docker-compose.yml`, `compose.yaml` | daemon availability, build context, exposed services |

If markers point to multiple project types, explain the candidates and ask the user which component should drive the environment setup.
