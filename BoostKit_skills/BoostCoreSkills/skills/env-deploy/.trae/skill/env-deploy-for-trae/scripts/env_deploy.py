#!/usr/bin/env python3
"""Automated Linux environment deployment helper for env-deploy-for-trae.

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
    def __init__(self, project: Path, apply: bool, skip_tests: bool) -> None:
        self.project = project
        self.apply = apply
        self.skip_tests = skip_tests
        self.log_path = project / "deploy.log"
        self.setup_path = project / "setup.sh"
        self.report_path = project / "deploy-report.md"
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


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def command_specs(detection: ProjectDetection, args: argparse.Namespace) -> tuple[list[CommandSpec], list[str]]:
    project = detection.root
    kind = args.component_type or detection.primary_type
    warnings: list[str] = []
    commands: list[CommandSpec] = []

    if not kind:
        return commands, ["No supported project type detected."]

    if detection.ambiguous and not args.component_type:
        warnings.append("Multiple project types detected; defaulting to priority order. Use --component-type to override.")

    if args.install_system_packages:
        commands.extend(system_package_commands(kind, project))

    if kind == "cpp":
        commands.extend(cpp_commands(project, detection.build_tool))
    elif kind == "python":
        commands.extend(python_commands(project))
    elif kind == "go":
        commands.extend(go_commands(project))
    elif kind == "java":
        commands.extend(java_commands(project, args.java_tool, detection))
    elif kind == "docker":
        commands.extend(docker_commands(project, detection.build_tool))

    if args.skip_tests:
        commands = [cmd for cmd in commands if "test" not in cmd.step.lower()]

    return commands, warnings


def system_package_commands(kind: str, project: Path) -> list[CommandSpec]:
    pm = package_manager()
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


def python_commands(project: Path) -> list[CommandSpec]:
    python = sys.executable or "python3"
    commands = [
        CommandSpec("Create Python virtual environment", [python, "-m", "venv", ".venv"], project, required_tool=Path(python).name),
    ]
    pip = ".venv/bin/pip"
    py = ".venv/bin/python"
    commands.append(CommandSpec("Upgrade pip", [pip, "install", "--upgrade", "pip"], project))
    if (project / "requirements.txt").exists():
        commands.append(CommandSpec("Install Python requirements", [pip, "install", "-r", "requirements.txt"], project))
    if (project / "pyproject.toml").exists() or (project / "setup.py").exists():
        commands.append(CommandSpec("Install Python project", [pip, "install", "-e", "."], project))
    if has_pytest(project):
        commands.append(CommandSpec("Run pytest", [py, "-m", "pytest"], project))
    else:
        commands.append(CommandSpec("Run unittest", [py, "-m", "unittest", "discover"], project))
    return commands


def has_pytest(project: Path) -> bool:
    names = ["requirements.txt", "pyproject.toml", "setup.py"]
    return any("pytest" in read_text(project / name).lower() for name in names if (project / name).exists())


def go_commands(project: Path) -> list[CommandSpec]:
    commands: list[CommandSpec] = []
    if (project / "go.mod").exists():
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


def write_setup(ctx: DeployContext) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "# Generated by env-deploy-for-trae. Review before running on another host.",
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


def write_report(ctx: DeployContext, detection: ProjectDetection, warnings: Sequence[str]) -> None:
    all_warnings = [*warnings, *ctx.warnings]
    lines = [
        "# Deployment Report",
        "",
        "## Project",
        "",
        f"- Path: `{ctx.project}`",
        f"- Detected type: `{TYPE_LABELS.get(detection.primary_type or '', detection.primary_type or 'unknown')}`",
        f"- Build tool: `{detection.build_tool or 'unknown'}`",
        f"- Linux distribution: `{platform.platform()}`",
        f"- Package manager: `{package_manager()}`",
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
        target_root = (clone_dir or (Path.cwd() / "env-deploy-for-trae-sources")).expanduser().resolve()
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


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate env-deploy-for-trae discovery, execution, logging, and artifact generation.")
    parser.add_argument("--project", help="Local project path. Defaults to current directory.")
    parser.add_argument("--source", help="Local path or Git URL. Overrides --project when set.")
    parser.add_argument("--clone-dir", type=Path, help="Directory for cloning Git sources.")
    parser.add_argument("--apply", action="store_true", help="Execute planned commands. Default is dry-run planning.")
    parser.add_argument("--install-system-packages", action="store_true", help="Include package-manager system package installation commands.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unit-test commands.")
    parser.add_argument("--component-type", choices=PROJECT_PRIORITY, help="Select a primary component type when detection is ambiguous.")
    parser.add_argument("--java-tool", choices=["maven", "gradle"], help="Select Java build tool when both are present.")
    parser.add_argument("--json", action="store_true", help="Print final machine-readable summary.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    source = args.source or args.project
    project = resolve_source(source, args.clone_dir, args.apply)
    if not project.exists():
        raise SystemExit(f"Project path does not exist: {project}")

    detection = detect_project(project)
    ctx = DeployContext(project, args.apply, args.skip_tests)
    ctx.log_path.write_text("", encoding="utf-8")

    commands, warnings = command_specs(detection, args)
    warnings.extend(detection.notes)
    kind = args.component_type or detection.primary_type

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
    write_report(ctx, detection, warnings)

    summary = {
        "project": str(project),
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
    print("env-deploy-for-trae summary")
    print(f"Project: {summary['project']}")
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
