# Project Detection

Use this reference before installing dependencies or running build commands.

## Project Type Priority

When more than one marker exists, use this priority order unless the user or repository documentation clearly says otherwise:

| Priority | Type | Markers |
|----------|------|---------|
| 1 | C++ | `CMakeLists.txt`, `Makefile`, `BUILD`, `WORKSPACE` |
| 2 | Python | `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` |
| 3 | Go | `go.mod`, `go.sum`, GOPATH-style layout |
| 4 | Java | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| 5 | Docker | `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml` |

If the markers indicate multiple independent deployable components, treat it as a multi-component project and deploy each component in the priority order above. If the correct primary component is unclear, ask the user.

## Build Tool Detection

### C++

| Marker | Build Tool |
|--------|------------|
| `CMakeLists.txt` | CMake |
| `Makefile` | Make |
| `BUILD` or `WORKSPACE` | Bazel |

If no known marker exists, inspect README/INSTALL. If still unclear, ask the user.

### Java

| Marker | Build Tool |
|--------|------------|
| `pom.xml` | Maven |
| `build.gradle` or `build.gradle.kts` | Gradle |

Prefer wrapper scripts when present: `mvnw` for Maven, `gradlew` for Gradle. If Maven and Gradle markers both exist and neither README nor wrapper usage makes the intended tool clear, ask the user.

### Docker

Prefer Compose when `docker-compose.yml` or `docker-compose.yaml` exists. Otherwise build and run from `Dockerfile` according to project documentation.

## Unit Test Triggers

| Type | Trigger |
|------|---------|
| C++ | `test/`, `tests/`, or CMake `enable_testing()` |
| Python | `test/`, `tests/`, `test_*.py`, or `*_test.py` |
| Go | Any `*_test.go` file |
| Java | `src/test/` containing test files |

Do not invent tests if no trigger exists. Record "no UT detected" in the final report.

## Standard Build And Test Commands

Use repository-specific scripts or wrappers before generic commands when documentation clearly identifies them.

| Type | Build | Test |
|------|-------|------|
| CMake C++ | `cmake -S . -B build && cmake --build build` | `ctest --test-dir build --output-on-failure` |
| Make C++ | `make` | `make test` when available |
| Bazel C++ | `bazel build //...` | `bazel test //...` |
| Python | package-specific import/build check | `pytest` or `python -m unittest` |
| Go | `go build ./...` | `go test ./...` |
| Maven Java | `./mvnw compile` or `mvn compile` | `./mvnw test` or `mvn test` |
| Gradle Java | `./gradlew compileJava` or `gradle compileJava` | `./gradlew test` or `gradle test` |
| Docker | `docker compose build` or `docker build .` | container startup validation |
