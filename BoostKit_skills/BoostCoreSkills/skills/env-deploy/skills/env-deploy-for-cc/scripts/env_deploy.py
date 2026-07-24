#!/usr/bin/env python3
"""Automated Linux environment deployment helper for env-deploy-for-cc.

The script intentionally keeps destructive decisions outside automation:
driver replacement, ambiguous project/build-tool selection, and unresolved
test failures are reported as blocked/skipped items for the agent/user to
resolve explicitly.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


PROJECT_PRIORITY = ["cpp", "python", "go", "java", "docker"]
TYPE_LABELS = {
    "cpp": "C++",
    "python": "Python",
    "go": "Go",
    "java": "Java",
    "docker": "Docker",
}


@dataclasses.dataclass
class CommandSpec:
    step: str
    command: list[str]
    cwd: Path
    include_in_setup: bool = True
    shell: bool = False
    required_tool: str | None = None


@dataclasses.dataclass
class CommandResult:
    spec: CommandSpec
    exit_code: int | None
    stdout: str
    stderr: str
    status: str
    analysis: str


@dataclasses.dataclass
class DeploymentTarget:
    mode: str
    project: Path
    output_dir: Path
    remote_host: str | None = None
    remote_project: str | None = None
    remote_port: int = 22
    remote_key: Path | None = None
    remote_ssh_options: list[str] = dataclasses.field(default_factory=list)

    @property
    def is_remote(self) -> bool:
        return self.mode == "ssh"

    @property
    def display_project(self) -> str:
        return self.remote_project if self.is_remote and self.remote_project else str(self.project)


@dataclasses.dataclass
class ProjectDetection:
    root: Path
    markers: dict[str, list[str]]
    primary_type: str | None
    all_types: list[str]
    ambiguous: bool
    build_tool: str | None
    java_build_ambiguous: bool
    test_triggers: dict[str, list[str]]
    notes: list[str]

    def to_json(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "markers": self.markers,
            "primary_type": self.primary_type,
            "primary_label": TYPE_LABELS.get(self.primary_type or "", self.primary_type),
            "all_types": self.all_types,
            "ambiguous": self.ambiguous,
            "build_tool": self.build_tool,
            "java_build_ambiguous": self.java_build_ambiguous,
            "test_triggers": self.test_triggers,
            "notes": self.notes,
        }


class DeployContext:
    def __init__(self, target: DeploymentTarget, apply: bool, skip_tests: bool) -> None:
        self.target = target
        self.project = target.project
        self.apply = apply
        self.skip_tests = skip_tests
        self.log_path = target.output_dir / "deploy.log"
        self.setup_path = target.output_dir / "setup.sh"
        self.report_path = target.output_dir / "deploy-report.md"
        self.results: list[CommandResult] = []
        self.success: list[str] = []
        self.failed: list[str] = []
        self.skipped: list[str] = []
        self.warnings: list[str] = []
        self.setup_commands: list[CommandSpec] = []

    def write_log_entry(self, result: CommandResult) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        command_text = format_command(result.spec)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write("=" * 80 + "\n")
            handle.write(f"Timestamp: {dt.datetime.now().astimezone().isoformat()}\n")
            handle.write(f"Deployment mode: {self.target.mode}\n")
            if self.target.is_remote:
                handle.write(f"Remote host: {redact(self.target.remote_host or '')}\n")
                handle.write(f"Remote project: {self.target.remote_project}\n")
            handle.write(f"Step: {result.spec.step}\n")
            handle.write(f"Working directory: {result.spec.cwd}\n")
            handle.write("Command:\n")
            handle.write(f"  {redact(command_text)}\n")
            handle.write(f"Exit code: {result.exit_code if result.exit_code is not None else 'not run'}\n")
            handle.write("Stdout:\n")
            handle.write(indent_block(redact(result.stdout)) + "\n")
            handle.write("Stderr:\n")
            handle.write(indent_block(redact(result.stderr)) + "\n")
            handle.write("Analysis:\n")
            handle.write(indent_block(result.analysis) + "\n")
            handle.write("Decision:\n")
            handle.write(indent_block(result.status) + "\n")


def redact(value: str) -> str:
    patterns = [
        (r"(?i)(token|password|passwd|secret)=([^\s]+)", r"\1=<REDACTED>"),
        (r"https://([^:\s]+):([^@\s]+)@", r"https://<REDACTED_CREDENTIAL>@"),
    ]
    output = value
    for pattern, repl in patterns:
        output = re.sub(pattern, repl, output)
    return output


def indent_block(value: str) -> str:
    if not value:
        return "  "
    return "\n".join(f"  {line}" for line in value.rstrip().splitlines())


def format_command(spec: CommandSpec) -> str:
    if spec.shell:
        return " ".join(spec.command)
    return " ".join(sh_quote(part) for part in spec.command)


def sh_quote(value: str) -> str:
    if re.match(r"^[A-Za-z0-9_./:=@%+-]+$", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def remote_path(value: str) -> Path:
    return Path(value)


def ssh_base_command(target: DeploymentTarget) -> list[str]:
    if not target.remote_host:
        raise ValueError("remote_host is required for SSH mode")
    command = ["ssh", "-p", str(target.remote_port)]
    if target.remote_key:
        command.extend(["-i", str(target.remote_key)])
    for option in target.remote_ssh_options:
        command.extend(["-o", option])
    command.append(target.remote_host)
    return command


def remote_shell_command(target: DeploymentTarget, command_text: str) -> list[str]:
    if not target.remote_project:
        raise ValueError("remote_project is required for SSH mode")
    remote_script = f"cd {sh_quote(target.remote_project)} && {command_text}"
    return [*ssh_base_command(target), remote_script]


def remote_command_preview(target: DeploymentTarget, spec: CommandSpec) -> str:
    return " ".join(sh_quote(part) for part in remote_shell_command(target, format_command(spec)))


def file_exists(root: Path, name: str) -> bool:
    return (root / name).exists()


def find_files(root: Path, patterns: Sequence[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if any(part in {".git", ".venv", "node_modules", "build", "target"} for part in path.parts):
                continue
            if path.is_file() or path.is_dir():
                matches.append(str(path.relative_to(root)))
    return sorted(set(matches))


def read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def detect_project(root: Path) -> ProjectDetection:
    markers = {
        "cpp": [name for name in ["CMakeLists.txt", "Makefile", "BUILD", "WORKSPACE"] if file_exists(root, name)],
        "python": [name for name in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"] if file_exists(root, name)],
        "go": [name for name in ["go.mod", "go.sum"] if file_exists(root, name)],
        "java": [name for name in ["pom.xml", "build.gradle", "build.gradle.kts"] if file_exists(root, name)],
        "docker": [name for name in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"] if file_exists(root, name)],
    }
    if not markers["go"] and ((root / "src").exists() and os.environ.get("GOPATH")):
        markers["go"].append("GOPATH-style src/")

    all_types = [kind for kind in PROJECT_PRIORITY if markers[kind]]
    primary_type = all_types[0] if all_types else None
    ambiguous = len(all_types) > 1

    build_tool = None
    java_build_ambiguous = False
    if primary_type == "cpp":
        if "CMakeLists.txt" in markers["cpp"]:
            build_tool = "cmake"
        elif "Makefile" in markers["cpp"]:
            build_tool = "make"
        elif "BUILD" in markers["cpp"] or "WORKSPACE" in markers["cpp"]:
            build_tool = "bazel"
    elif primary_type == "java":
        has_maven = "pom.xml" in markers["java"]
        has_gradle = "build.gradle" in markers["java"] or "build.gradle.kts" in markers["java"]
        java_build_ambiguous = has_maven and has_gradle
        if has_maven and not has_gradle:
            build_tool = "maven"
        elif has_gradle and not has_maven:
            build_tool = "gradle"
    elif primary_type == "docker":
        build_tool = "compose" if markers["docker"] and any("compose" in item for item in markers["docker"]) else "docker"

    tests = {
        "cpp": find_cpp_tests(root) if markers["cpp"] else [],
        "python": (find_files(root, ["test_*.py", "*_test.py"]) + [name for name in ["test", "tests"] if (root / name).is_dir()]) if markers["python"] else [],
        "go": find_files(root, ["*_test.go"]) if markers["go"] else [],
        "java": find_files(root / "src" / "test", ["*.java", "*.kt", "*.groovy"]) if markers["java"] and (root / "src" / "test").exists() else [],
        "docker": [],
    }
    notes = []
    if ambiguous:
        notes.append("Multiple project type markers found; use --component-type to select the primary automation path.")
    if java_build_ambiguous:
        notes.append("Both Maven and Gradle markers found; use --java-tool to select one.")
    if not primary_type:
        notes.append("No supported project markers found.")

    return ProjectDetection(root, markers, primary_type, all_types, ambiguous, build_tool, java_build_ambiguous, tests, notes)


def detect_remote_project(target: DeploymentTarget) -> ProjectDetection:
    if not target.remote_project:
        raise ValueError("remote_project is required for SSH detection")
    check_names = [
        "CMakeLists.txt",
        "Makefile",
        "BUILD",
        "WORKSPACE",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "Pipfile",
        "go.mod",
        "go.sum",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "mvnw",
        "gradlew",
    ]
    remote_script = " ; ".join(
        f"if [ -e {sh_quote(name)} ]; then printf '%s\\n' {sh_quote(name)}; fi"
        for name in check_names
    )
    proc = subprocess.run(
        remote_shell_command(target, remote_script),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "Remote project detection failed. Confirm SSH access, host key trust, and the remote project path.\n"
            + redact(proc.stderr.strip())
        )

    found = set(proc.stdout.splitlines())
    markers = {
        "cpp": [name for name in ["CMakeLists.txt", "Makefile", "BUILD", "WORKSPACE"] if name in found],
        "python": [name for name in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"] if name in found],
        "go": [name for name in ["go.mod", "go.sum"] if name in found],
        "java": [name for name in ["pom.xml", "build.gradle", "build.gradle.kts"] if name in found],
        "docker": [name for name in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"] if name in found],
    }
    all_types = [kind for kind in PROJECT_PRIORITY if markers[kind]]
    primary_type = all_types[0] if all_types else None
    ambiguous = len(all_types) > 1

    build_tool = None
    java_build_ambiguous = False
    if primary_type == "cpp":
        if "CMakeLists.txt" in markers["cpp"]:
            build_tool = "cmake"
        elif "Makefile" in markers["cpp"]:
            build_tool = "make"
        elif "BUILD" in markers["cpp"] or "WORKSPACE" in markers["cpp"]:
            build_tool = "bazel"
    elif primary_type == "java":
        has_maven = "pom.xml" in markers["java"]
        has_gradle = "build.gradle" in markers["java"] or "build.gradle.kts" in markers["java"]
        java_build_ambiguous = has_maven and has_gradle
        if has_maven and not has_gradle:
            build_tool = "maven"
        elif has_gradle and not has_maven:
            build_tool = "gradle"
    elif primary_type == "docker":
        build_tool = "compose" if any("compose" in item for item in markers["docker"]) else "docker"

    test_triggers = {
        "cpp": ["remote test discovery not expanded"] if markers["cpp"] else [],
        "python": ["remote test discovery not expanded"] if markers["python"] else [],
        "go": ["remote test discovery not expanded"] if markers["go"] else [],
        "java": ["remote test discovery not expanded"] if markers["java"] else [],
        "docker": [],
    }
    notes = ["Remote detection used top-level project markers over SSH."]
    if ambiguous:
        notes.append("Multiple project type markers found; use --component-type to select the primary automation path.")
    if java_build_ambiguous:
        notes.append("Both Maven and Gradle markers found; use --java-tool to select one.")
    if not primary_type:
        notes.append("No supported project markers found.")

    return ProjectDetection(
        remote_path(target.remote_project),
        markers,
        primary_type,
        all_types,
        ambiguous,
        build_tool,
        java_build_ambiguous,
        test_triggers,
        notes,
    )


def remote_dry_run_detection(target: DeploymentTarget, args: argparse.Namespace) -> ProjectDetection:
    kind = args.component_type
    markers = {project_type: [] for project_type in PROJECT_PRIORITY}
    if kind:
        markers[kind] = ["remote dry-run component selection"]
    notes = [
        "SSH dry-run does not connect to the remote host; pass --apply to detect remote markers over SSH.",
        "Provide --component-type to preview deployment commands without remote detection.",
    ]
    return ProjectDetection(
        remote_path(target.remote_project or "."),
        markers,
        kind,
        [kind] if kind else [],
        False,
        args.java_tool if kind == "java" else None,
        False,
        {project_type: (["remote dry-run test preview"] if project_type == kind else []) for project_type in PROJECT_PRIORITY},
        notes,
    )


def find_cpp_tests(root: Path) -> list[str]:
    triggers = [name for name in ["test", "tests"] if (root / name).is_dir()]
    cmake = root / "CMakeLists.txt"
    if cmake.exists() and "enable_testing()" in read_text(cmake):
        triggers.append("CMakeLists.txt:enable_testing()")
    return sorted(set(triggers))


def package_manager() -> str:
    if shutil.which("apt-get"):
        return "apt"
    if shutil.which("dnf"):
        return "dnf"
    if shutil.which("yum"):
        return "yum"
    return "unknown"


def package_manager_for_target(target: DeploymentTarget, apply: bool) -> str:
    if not target.is_remote:
        return package_manager()
    if not apply:
        return "remote"
    proc = subprocess.run(
        remote_shell_command(target, "if command -v apt-get >/dev/null 2>&1; then echo apt; elif command -v dnf >/dev/null 2>&1; then echo dnf; elif command -v yum >/dev/null 2>&1; then echo yum; else echo unknown; fi"),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return "unknown"
    return proc.stdout.strip() or "unknown"


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def command_specs(detection: ProjectDetection, args: argparse.Namespace, pm: str | None = None) -> tuple[list[CommandSpec], list[str]]:
    project = detection.root
    kind = args.component_type or detection.primary_type
    warnings: list[str] = []
    commands: list[CommandSpec] = []

    if not kind:
        return commands, ["No supported project type detected."]

    if detection.ambiguous and not args.component_type:
        warnings.append("Multiple project types detected; defaulting to priority order. Use --component-type to override.")

    if args.install_system_packages:
        commands.extend(system_package_commands(kind, project, pm))

    if kind == "cpp":
        commands.extend(cpp_commands(project, detection.build_tool))
    elif kind == "python":
        commands.extend(python_commands(project, detection))
    elif kind == "go":
        commands.extend(go_commands(project, detection))
    elif kind == "java":
        commands.extend(java_commands(project, args.java_tool, detection))
    elif kind == "docker":
        commands.extend(docker_commands(project, detection.build_tool))

    if args.skip_tests:
        commands = [cmd for cmd in commands if "test" not in cmd.step.lower()]

    return commands, warnings


def system_package_commands(kind: str, project: Path, pm: str | None = None) -> list[CommandSpec]:
    pm = pm or package_manager()
    packages = {
        "cpp": ["build-essential", "cmake", "make", "pkg-config"],
        "python": ["python3", "python3-venv", "python3-pip"],
        "go": ["golang-go"],
        "java": ["default-jdk", "maven", "gradle"],
        "docker": ["docker.io", "docker-compose-plugin"],
    }.get(kind, [])
    if not packages or pm == "unknown":
        return []
    if pm == "apt":
        return [
            CommandSpec("Update apt package index", ["sudo", "apt-get", "update"], project),
            CommandSpec("Install system packages", ["sudo", "apt-get", "install", "-y", *packages], project),
        ]
    if pm in {"dnf", "yum"}:
        return [CommandSpec("Install system packages", ["sudo", pm, "install", "-y", *packages], project)]
    return []


def cpp_commands(project: Path, build_tool: str | None) -> list[CommandSpec]:
    if build_tool == "cmake":
        return [
            CommandSpec("Configure CMake project", ["cmake", "-S", ".", "-B", "build"], project, required_tool="cmake"),
            CommandSpec("Build CMake project", ["cmake", "--build", "build"], project, required_tool="cmake"),
            CommandSpec("Run CMake tests", ["ctest", "--test-dir", "build", "--output-on-failure"], project, required_tool="ctest"),
        ]
    if build_tool == "make":
        return [
            CommandSpec("Build Make project", ["make"], project, required_tool="make"),
            CommandSpec("Run Make tests", ["make", "test"], project, required_tool="make"),
        ]
    if build_tool == "bazel":
        return [
            CommandSpec("Build Bazel project", ["bazel", "build", "//..."], project, required_tool="bazel"),
            CommandSpec("Run Bazel tests", ["bazel", "test", "//..."], project, required_tool="bazel"),
        ]
    return []


def python_commands(project: Path, detection: ProjectDetection) -> list[CommandSpec]:
    python = "python3"
    commands = [
        CommandSpec("Create Python virtual environment", [python, "-m", "venv", ".venv"], project, required_tool=Path(python).name),
    ]
    pip = ".venv/bin/pip"
    py = ".venv/bin/python"
    commands.append(CommandSpec("Upgrade pip", [pip, "install", "--upgrade", "pip"], project))
    python_markers = set(detection.markers.get("python", []))
    if "requirements.txt" in python_markers:
        commands.append(CommandSpec("Install Python requirements", [pip, "install", "-r", "requirements.txt"], project))
    if "pyproject.toml" in python_markers or "setup.py" in python_markers:
        commands.append(CommandSpec("Install Python project", [pip, "install", "-e", "."], project))
    if has_pytest(project):
        commands.append(CommandSpec("Run pytest", [py, "-m", "pytest"], project))
    else:
        commands.append(CommandSpec("Run unittest", [py, "-m", "unittest", "discover"], project))
    return commands


def has_pytest(project: Path) -> bool:
    names = ["requirements.txt", "pyproject.toml", "setup.py"]
    return any("pytest" in read_text(project / name).lower() for name in names if (project / name).exists())


def go_commands(project: Path, detection: ProjectDetection) -> list[CommandSpec]:
    commands: list[CommandSpec] = []
    if "go.mod" in detection.markers.get("go", []):
        commands.append(CommandSpec("Download Go modules", ["go", "mod", "download"], project, required_tool="go"))
    commands.extend([
        CommandSpec("Build Go project", ["go", "build", "./..."], project, required_tool="go"),
        CommandSpec("Run Go tests", ["go", "test", "./..."], project, required_tool="go"),
    ])
    return commands


def java_commands(project: Path, selected_tool: str | None, detection: ProjectDetection) -> list[CommandSpec]:
    tool = selected_tool or detection.build_tool
    if not tool and detection.java_build_ambiguous:
        return []
    if tool == "maven":
        mvn = "./mvnw" if (project / "mvnw").exists() else "mvn"
        return [
            CommandSpec("Resolve Maven dependencies", [mvn, "dependency:resolve"], project, required_tool=None if mvn.startswith("./") else "mvn"),
            CommandSpec("Compile Maven project", [mvn, "compile"], project, required_tool=None if mvn.startswith("./") else "mvn"),
            CommandSpec("Run Maven tests", [mvn, "test"], project, required_tool=None if mvn.startswith("./") else "mvn"),
        ]
    if tool == "gradle":
        gradle = "./gradlew" if (project / "gradlew").exists() else "gradle"
        return [
            CommandSpec("Resolve Gradle dependencies", [gradle, "dependencies"], project, required_tool=None if gradle.startswith("./") else "gradle"),
            CommandSpec("Compile Gradle project", [gradle, "compileJava"], project, required_tool=None if gradle.startswith("./") else "gradle"),
            CommandSpec("Run Gradle tests", [gradle, "test"], project, required_tool=None if gradle.startswith("./") else "gradle"),
        ]
    return []


def docker_commands(project: Path, build_tool: str | None) -> list[CommandSpec]:
    if build_tool == "compose":
        docker = "docker"
        return [
            CommandSpec("Build Docker Compose services", [docker, "compose", "build"], project, required_tool="docker"),
            CommandSpec("Start Docker Compose services", [docker, "compose", "up", "-d"], project, required_tool="docker"),
            CommandSpec("Validate Docker Compose services", [docker, "compose", "ps"], project, include_in_setup=False, required_tool="docker"),
        ]
    return [
        CommandSpec("Build Docker image", ["docker", "build", "-t", project.name.lower().replace("_", "-"), "."], project, required_tool="docker"),
    ]


def should_run_test_command(spec: CommandSpec, detection: ProjectDetection, kind: str | None) -> bool:
    if "test" not in spec.step.lower() and "pytest" not in spec.step.lower() and "unittest" not in spec.step.lower():
        return True
    if not kind:
        return False
    return bool(detection.test_triggers.get(kind))


def run_command(ctx: DeployContext, spec: CommandSpec) -> CommandResult:
    if ctx.target.is_remote:
        return run_remote_command(ctx, spec)
    if not ctx.apply:
        return CommandResult(spec, None, "", "", "planned", "Dry run only; pass --apply to execute.")
    if spec.required_tool and not tool_exists(spec.required_tool):
        return CommandResult(spec, None, "", "", "skipped", f"Required tool `{spec.required_tool}` is not available.")
    proc = subprocess.run(
        spec.command if not spec.shell else " ".join(spec.command),
        cwd=spec.cwd,
        text=True,
        capture_output=True,
        shell=spec.shell,
        check=False,
    )
    status = "success" if proc.returncode == 0 else "failed"
    analysis = "Command completed successfully." if status == "success" else "Command failed; inspect stdout/stderr and apply the Skill failure flow."
    return CommandResult(spec, proc.returncode, proc.stdout, proc.stderr, status, analysis)


def run_remote_command(ctx: DeployContext, spec: CommandSpec) -> CommandResult:
    preview = remote_command_preview(ctx.target, spec)
    preview_spec = dataclasses.replace(spec, command=[preview], shell=True)
    if not ctx.apply:
        return CommandResult(preview_spec, None, "", "", "planned", "SSH dry-run only; pass --apply to execute on the remote host.")
    if not tool_exists("ssh"):
        return CommandResult(preview_spec, None, "", "", "skipped", "Required local tool `ssh` is not available.")
    proc = subprocess.run(
        remote_shell_command(ctx.target, format_command(spec)),
        text=True,
        capture_output=True,
        check=False,
    )
    status = "success" if proc.returncode == 0 else "failed"
    analysis = "Remote command completed successfully." if status == "success" else "Remote command failed; inspect stdout/stderr and apply the Skill failure flow."
    return CommandResult(preview_spec, proc.returncode, proc.stdout, proc.stderr, status, analysis)


def write_setup(ctx: DeployContext) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "# Generated by env-deploy-for-cc. Review before running on the target host.",
        "# In SSH deployments, run this script inside the remote project directory; it does not include ssh commands.",
        "set -euo pipefail",
        "",
        'PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"',
        'cd "$PROJECT_ROOT"',
        "",
    ]
    for spec in ctx.setup_commands:
        lines.append(f"# {spec.step}")
        lines.append(format_command(spec))
        lines.append("")
    ctx.setup_path.write_text("\n".join(lines), encoding="utf-8")
    ctx.setup_path.chmod(0o755)


def write_report(ctx: DeployContext, detection: ProjectDetection, warnings: Sequence[str], pm: str) -> None:
    all_warnings = [*warnings, *ctx.warnings]
    lines = [
        "# Deployment Report",
        "",
        "## Project",
        "",
        f"- Deployment mode: `{ctx.target.mode}`",
        f"- Path: `{ctx.target.display_project}`",
        f"- Remote host: `{ctx.target.remote_host or 'n/a'}`",
        f"- Remote project: `{ctx.target.remote_project or 'n/a'}`",
        f"- Detected type: `{TYPE_LABELS.get(detection.primary_type or '', detection.primary_type or 'unknown')}`",
        f"- Build tool: `{detection.build_tool or 'unknown'}`",
        f"- Linux distribution: `{'remote Linux' if ctx.target.is_remote else platform.platform()}`",
        f"- Package manager: `{pm}`",
        "",
        "## Success",
        "",
        *bullet_lines(ctx.success),
        "",
        "## Failed",
        "",
        *bullet_lines(ctx.failed),
        "",
        "## Skipped",
        "",
        *bullet_lines(ctx.skipped),
        "",
        "## Warnings",
        "",
        *bullet_lines(all_warnings),
        "",
        "## Artifacts",
        "",
        "- `deploy.log`",
        "- `setup.sh`",
    ]
    ctx.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def bullet_lines(items: Sequence[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def resolve_source(source: str | None, clone_dir: Path | None, apply: bool) -> Path:
    if not source:
        return Path.cwd().resolve()
    if re.match(r"^(git@|https?://)", source):
        target_root = (clone_dir or (Path.cwd() / "env-deploy-for-cc-sources")).expanduser().resolve()
        target_root.mkdir(parents=True, exist_ok=True)
        name = re.sub(r"\.git$", "", source.rstrip("/").split("/")[-1].split(":")[-1])
        destination = target_root / name
        if destination.exists():
            return destination.resolve()
        if not apply:
            raise SystemExit(f"Git source would be cloned to {destination}; rerun with --apply to clone.")
        subprocess.run(["git", "clone", source, str(destination)], check=True)
        return destination.resolve()
    return Path(source).expanduser().resolve()


def resolve_target(args: argparse.Namespace) -> DeploymentTarget:
    if bool(args.remote_host) != bool(args.remote_project):
        raise SystemExit("--remote-host and --remote-project must be provided together.")
    if args.remote_host:
        output_dir = (args.output_dir or (Path.cwd() / "env-deploy-remote-artifacts")).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return DeploymentTarget(
            mode="ssh",
            project=remote_path(args.remote_project),
            output_dir=output_dir,
            remote_host=args.remote_host,
            remote_project=args.remote_project,
            remote_port=args.remote_port,
            remote_key=args.remote_key.expanduser().resolve() if args.remote_key else None,
            remote_ssh_options=args.remote_ssh_option,
        )

    source = args.source or args.project
    project = resolve_source(source, args.clone_dir, args.apply)
    if not project.exists():
        raise SystemExit(f"Project path does not exist: {project}")
    output_dir = (args.output_dir.expanduser().resolve() if args.output_dir else project)
    output_dir.mkdir(parents=True, exist_ok=True)
    return DeploymentTarget(mode="local", project=project, output_dir=output_dir)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate env-deploy-for-cc discovery, execution, logging, and artifact generation.")
    parser.add_argument("--project", help="Local project path. Defaults to current directory.")
    parser.add_argument("--source", help="Local path or Git URL. Overrides --project when set.")
    parser.add_argument("--clone-dir", type=Path, help="Directory for cloning Git sources.")
    parser.add_argument("--output-dir", type=Path, help="Local directory for deploy.log, setup.sh, and deploy-report.md. Defaults to the project root, or ./env-deploy-remote-artifacts for SSH mode.")
    parser.add_argument("--remote-host", help="SSH target such as user@host. Requires --remote-project.")
    parser.add_argument("--remote-project", help="Absolute project path that already exists on the remote Linux server.")
    parser.add_argument("--remote-port", type=int, default=22, help="SSH port for --remote-host. Default: 22.")
    parser.add_argument("--remote-key", type=Path, help="SSH private key path passed to ssh -i. The key contents are never logged.")
    parser.add_argument("--remote-ssh-option", action="append", default=[], metavar="KEY=VALUE", help="Additional ssh -o option. Can be repeated.")
    parser.add_argument("--apply", action="store_true", help="Execute planned commands. Default is dry-run planning.")
    parser.add_argument("--install-system-packages", action="store_true", help="Include package-manager system package installation commands.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unit-test commands.")
    parser.add_argument("--component-type", choices=PROJECT_PRIORITY, help="Select a primary component type when detection is ambiguous.")
    parser.add_argument("--java-tool", choices=["maven", "gradle"], help="Select Java build tool when both are present.")
    parser.add_argument("--json", action="store_true", help="Print final machine-readable summary.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target = resolve_target(args)

    if target.is_remote:
        if args.apply:
            if not tool_exists("ssh"):
                raise SystemExit("SSH mode requires the local `ssh` client.")
            detection = detect_remote_project(target)
        else:
            detection = remote_dry_run_detection(target, args)
    else:
        detection = detect_project(target.project)

    ctx = DeployContext(target, args.apply, args.skip_tests)
    ctx.log_path.write_text("", encoding="utf-8")

    pm = package_manager_for_target(target, args.apply)
    commands, warnings = command_specs(detection, args, pm)
    warnings.extend(detection.notes)
    kind = args.component_type or detection.primary_type

    if target.is_remote:
        ctx.warnings.append("SSH mode expects the project to already exist at the remote path; no code upload or remote clone is performed.")
        if not args.apply:
            ctx.warnings.append("SSH dry-run does not connect to the remote host; command previews may require --component-type for useful planning.")

    if detection.java_build_ambiguous and not args.java_tool:
        ctx.skipped.append("Java automation blocked because both Maven and Gradle markers are present; rerun with --java-tool.")
    if detection.ambiguous and not args.component_type:
        ctx.warnings.append("Ambiguous project markers found; automation used priority order for planning.")

    for spec in commands:
        if not should_run_test_command(spec, detection, kind):
            ctx.skipped.append(f"{spec.step}: no unit-test trigger detected.")
            continue
        result = run_command(ctx, spec)
        ctx.results.append(result)
        ctx.write_log_entry(result)
        if result.status == "success":
            ctx.success.append(spec.step)
            if spec.include_in_setup:
                ctx.setup_commands.append(spec)
        elif result.status == "planned":
            ctx.success.append(f"Planned: {spec.step}")
            if spec.include_in_setup:
                ctx.setup_commands.append(spec)
        elif result.status == "skipped":
            ctx.skipped.append(f"{spec.step}: {result.analysis}")
        else:
            ctx.failed.append(f"{spec.step}: exit {result.exit_code}")
            break

    write_setup(ctx)
    write_report(ctx, detection, warnings, pm)

    summary = {
        "project": target.display_project,
        "deployment_mode": target.mode,
        "remote_host": target.remote_host,
        "remote_project": target.remote_project,
        "apply": args.apply,
        "detection": detection.to_json(),
        "success": ctx.success,
        "failed": ctx.failed,
        "skipped": ctx.skipped,
        "warnings": [*warnings, *ctx.warnings],
        "artifacts": {
            "deploy_log": str(ctx.log_path),
            "setup_sh": str(ctx.setup_path),
            "deploy_report": str(ctx.report_path),
        },
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human_summary(summary)
    return 1 if ctx.failed else 0


def print_human_summary(summary: dict[str, object]) -> None:
    print("env-deploy-for-cc summary")
    print(f"Project: {summary['project']}")
    print(f"Deployment mode: {summary.get('deployment_mode', 'local')}")
    if summary.get("remote_host"):
        print(f"Remote host: {summary['remote_host']}")
    print(f"Mode: {'apply' if summary['apply'] else 'dry-run'}")
    detection = summary["detection"]
    if isinstance(detection, dict):
        print(f"Detected: {detection.get('primary_label') or 'unknown'}")
    for key in ["success", "failed", "skipped", "warnings"]:
        print(f"\n{key.title()}:")
        values = summary.get(key) or []
        if isinstance(values, list) and values:
            for value in values:
                print(f"- {value}")
        else:
            print("- None")
    artifacts = summary.get("artifacts")
    if isinstance(artifacts, dict):
        print("\nArtifacts:")
        for path in artifacts.values():
            print(f"- {path}")


if __name__ == "__main__":
    raise SystemExit(main())
