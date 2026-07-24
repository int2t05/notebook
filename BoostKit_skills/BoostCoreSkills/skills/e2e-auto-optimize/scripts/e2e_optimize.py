#!/usr/bin/env python3
"""Helpers for the e2e-auto-optimize skill."""

from __future__ import annotations

import argparse
import json
import math
import os
import posixpath
import re
import shlex
import shutil
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_CONFIG = "e2e-auto-optimize.config.json"
VALID_DIRECTIONS = {"lower_is_better", "higher_is_better"}
VALID_OCCURRENCES = {"first", "last", "min", "max", "mean", "median"}


class ConfigError(Exception):
    """Raised when the JSON config is missing or invalid."""


class RemoteError(Exception):
    """Raised when a remote command fails."""


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(
            f"Config file not found: {path}. Create it from templates/config.example.json."
        )
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Config root must be a JSON object.")
    return data


def require_string(cfg: Dict[str, Any], dotted: str, errors: List[str]) -> str:
    cur: Any = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            errors.append(f"Missing required field: {dotted}")
            return ""
        cur = cur[part]
    if not isinstance(cur, str) or not cur.strip():
        errors.append(f"Field must be a non-empty string: {dotted}")
        return ""
    return cur.strip()


def optional_string(cfg: Dict[str, Any], dotted: str, default: str = "") -> str:
    cur: Any = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    if cur is None:
        return default
    return str(cur)


def expand_local_path(raw: str, config_path: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw))
    path = Path(expanded)
    if not path.is_absolute():
        path = (config_path.parent / path).resolve()
    return path


def ensure_section(cfg: Dict[str, Any], name: str) -> Dict[str, Any]:
    section = cfg.setdefault(name, {})
    if not isinstance(section, dict):
        raise ConfigError(f"Config section must be an object: {name}")
    return section


def normalize_config(path: Path) -> Dict[str, Any]:
    cfg = load_json(path)
    errors: List[str] = []

    software = ensure_section(cfg, "software")
    environment = ensure_section(cfg, "environment")
    workspace = ensure_section(cfg, "workspace")
    commands = ensure_section(cfg, "commands")
    git = ensure_section(cfg, "git")
    analysis = ensure_section(cfg, "analysis")
    optimization = ensure_section(cfg, "optimization")
    metric = ensure_section(cfg, "metric")

    repo_path = require_string(cfg, "software.repo_path", errors)
    software.setdefault("baseline_ref", "HEAD")

    if repo_path:
        repo_clean = repo_path.rstrip("/")
        repo_parent = posixpath.dirname(repo_clean) or "."
        software_name = safe_name(str(software.get("name", "software")))
        base = posixpath.join(repo_parent, "e2e-auto-optimize", software_name)
        workspace.setdefault("work_dir", repo_path)
        workspace.setdefault("test_report_dir", posixpath.join(base, "test-reports"))
        workspace.setdefault("summary_report_dir", posixpath.join(base, "summary-reports"))
        workspace.setdefault("data_dir", posixpath.join(base, "data"))
        workspace.setdefault("perf_data_dir", posixpath.join(base, "perf-data"))

    optimization.setdefault("kb_dir", "kb")
    optimization.setdefault("kb_menu", "kb/menu.md")
    optimization.setdefault("candidate_directions", [])
    optimization.setdefault("iterations", 3)
    optimization.setdefault("threshold_percent", 5)

    metric.setdefault("value_group", 1)
    metric.setdefault("occurrence", "last")
    metric.setdefault("repeat", 1)

    environment.setdefault("port", 22)
    environment.setdefault("connect_timeout_seconds", 10)
    git.setdefault("username", "")
    git.setdefault("email", "")

    require_string(cfg, "software.name", errors)
    require_string(cfg, "environment.host", errors)
    require_string(cfg, "environment.user", errors)
    require_string(cfg, "environment.auth_method", errors)
    require_string(cfg, "commands.build", errors)
    require_string(cfg, "commands.ut", errors)
    require_string(cfg, "commands.perftest", errors)
    require_string(cfg, "metric.name", errors)
    require_string(cfg, "metric.direction", errors)
    require_string(cfg, "metric.parse_regex", errors)

    if "password" in environment and environment.get("password"):
        errors.append("Inline environment.password is not allowed. Use password_file_path or private_key_path.")

    for field in ("username", "email"):
        if not isinstance(git.get(field), str):
            errors.append(f"git.{field} must be a string. Use an empty string when unset.")

    auth_method = str(environment.get("auth_method", "")).strip()
    if auth_method not in {"private_key", "password_file"}:
        errors.append("environment.auth_method must be private_key or password_file.")
    elif auth_method == "private_key":
        key = require_string(cfg, "environment.private_key_path", errors)
        if key:
            key_path = expand_local_path(key, path)
            environment["private_key_path"] = str(key_path)
            if not key_path.exists():
                errors.append(f"Private key file does not exist: {key_path}")
    elif auth_method == "password_file":
        password_file = require_string(cfg, "environment.password_file_path", errors)
        if password_file:
            password_path = expand_local_path(password_file, path)
            environment["password_file_path"] = str(password_path)
            if not password_path.exists():
                errors.append(f"Password file does not exist: {password_path}")
        if shutil.which("sshpass") is None:
            errors.append("password_file auth requires sshpass on the local machine.")

    try:
        port = int(environment.get("port", 22))
        if port <= 0:
            errors.append("environment.port must be positive.")
        environment["port"] = port
    except (TypeError, ValueError):
        errors.append("environment.port must be an integer.")

    try:
        timeout = int(environment.get("connect_timeout_seconds", 10))
        if timeout <= 0:
            errors.append("environment.connect_timeout_seconds must be positive.")
        environment["connect_timeout_seconds"] = timeout
    except (TypeError, ValueError):
        errors.append("environment.connect_timeout_seconds must be an integer.")

    try:
        iterations = int(optimization.get("iterations", 3))
        if iterations <= 0:
            errors.append("optimization.iterations must be positive.")
        optimization["iterations"] = iterations
    except (TypeError, ValueError):
        errors.append("optimization.iterations must be an integer.")

    try:
        threshold = float(optimization.get("threshold_percent", 5))
        if threshold < 0:
            errors.append("optimization.threshold_percent must be non-negative.")
        optimization["threshold_percent"] = threshold
    except (TypeError, ValueError):
        errors.append("optimization.threshold_percent must be a number.")

    try:
        repeat = int(metric.get("repeat", 1))
        if repeat <= 0:
            errors.append("metric.repeat must be positive.")
        metric["repeat"] = repeat
    except (TypeError, ValueError):
        errors.append("metric.repeat must be an integer.")

    direction = str(metric.get("direction", "")).strip()
    if direction not in VALID_DIRECTIONS:
        errors.append(f"metric.direction must be one of: {', '.join(sorted(VALID_DIRECTIONS))}.")

    occurrence = str(metric.get("occurrence", "last")).strip()
    if occurrence not in VALID_OCCURRENCES:
        errors.append(f"metric.occurrence must be one of: {', '.join(sorted(VALID_OCCURRENCES))}.")

    regex = str(metric.get("parse_regex", ""))
    if regex:
        try:
            re.compile(regex, re.MULTILINE)
        except re.error as exc:
            errors.append(f"metric.parse_regex is invalid: {exc}")

    for dotted in (
        "workspace.work_dir",
        "workspace.test_report_dir",
        "workspace.summary_report_dir",
        "workspace.data_dir",
        "workspace.perf_data_dir",
    ):
        require_string(cfg, dotted, errors)

    analysis.setdefault("bottleneck_summary", "")
    analysis.setdefault("topdown_file", "")
    analysis.setdefault("perf_file", "")
    cfg.setdefault("notes", "")

    if errors:
        raise ConfigError("\n".join(f"- {err}" for err in errors))
    return cfg


def ssh_target(cfg: Dict[str, Any]) -> str:
    env = cfg["environment"]
    return f"{env['user']}@{env['host']}"


def ssh_base_args(cfg: Dict[str, Any]) -> List[str]:
    env = cfg["environment"]
    args = [
        "ssh",
        "-p",
        str(env["port"]),
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={env['connect_timeout_seconds']}",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    if env["auth_method"] == "private_key":
        args.extend(["-i", env["private_key_path"]])
    elif env["auth_method"] == "password_file":
        args = [
            "sshpass",
            "-f",
            env["password_file_path"],
        ] + args
    args.append(ssh_target(cfg))
    return args


def run_ssh(
    cfg: Dict[str, Any],
    command: str,
    *,
    timeout: Optional[int] = None,
    input_text: Optional[str] = None,
) -> subprocess.CompletedProcess[str]:
    remote = f"bash -lc {shlex.quote(command)}"
    return subprocess.run(
        ssh_base_args(cfg) + [remote],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def remote_quote(value: str) -> str:
    return shlex.quote(value)


def git_cmd(cfg: Dict[str, Any], args: str) -> str:
    repo = cfg["software"]["repo_path"]
    q_repo = remote_quote(repo)
    config_args = [f"-c safe.directory={q_repo}"]
    git_cfg = cfg.get("git", {})
    username = str(git_cfg.get("username", "")).strip()
    email = str(git_cfg.get("email", "")).strip()
    if username:
        config_args.append(f"-c {remote_quote('user.name=' + username)}")
    if email:
        config_args.append(f"-c {remote_quote('user.email=' + email)}")
    return f"git {' '.join(config_args)} -C {q_repo} {args}"


def run_required_ssh(cfg: Dict[str, Any], command: str, *, timeout: Optional[int] = None) -> str:
    result = run_ssh(cfg, command, timeout=timeout)
    if result.returncode != 0:
        raise RemoteError(
            f"Remote command failed with exit code {result.returncode}\n"
            f"COMMAND:\n{command}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def print_config_error(exc: ConfigError) -> int:
    print("Config validation failed:", file=sys.stderr)
    print(str(exc), file=sys.stderr)
    return 2


def cmd_validate_config(args: argparse.Namespace) -> int:
    try:
        cfg = normalize_config(Path(args.config))
    except ConfigError as exc:
        return print_config_error(exc)
    if args.print_normalized:
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
    else:
        print(f"Config OK: {args.config}")
    return 0


def cmd_check_environment(args: argparse.Namespace) -> int:
    try:
        cfg = normalize_config(Path(args.config))
    except ConfigError as exc:
        return print_config_error(exc)

    repo = cfg["software"]["repo_path"]
    q_repo = remote_quote(repo)
    info_cmd = "\n".join(
        [
            "set -e",
            "echo '## connection'",
            "echo user=$(whoami)",
            "echo home=$HOME",
            "echo '## uname'",
            "uname -a",
            "echo '## cpu'",
            "if command -v lscpu >/dev/null 2>&1; then lscpu | head -80; else cat /proc/cpuinfo | head -80; fi",
            "echo '## memory'",
            "if command -v free >/dev/null 2>&1; then free -h; fi",
            "echo '## repo'",
            f"test -d {q_repo}",
            f"{git_cmd(cfg, 'rev-parse --short HEAD')}",
        ]
    )
    result = run_ssh(cfg, info_cmd)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        print("Environment check failed before Git status inspection.", file=sys.stderr)
        return result.returncode or 1

    status_cmd = git_cmd(cfg, "status --porcelain")
    status = run_ssh(cfg, status_cmd)
    if status.returncode != 0:
        if status.stdout:
            print(status.stdout.rstrip())
        if status.stderr:
            print(status.stderr.rstrip(), file=sys.stderr)
        return status.returncode or 1
    dirty = status.stdout.strip()
    if dirty:
        print("Remote repo has uncommitted changes:", file=sys.stderr)
        print(dirty, file=sys.stderr)
        if not args.allow_dirty:
            print("Refusing to continue without --allow-dirty.", file=sys.stderr)
            return 3
    else:
        print("Remote repo clean.")
    return 0


def parse_number(raw: str) -> float:
    return float(raw.replace(",", ""))


def extract_metric_values(text: str, cfg: Dict[str, Any]) -> List[float]:
    metric = cfg["metric"]
    regex = re.compile(metric["parse_regex"], re.MULTILINE)
    group = metric.get("value_group", 1)
    values: List[float] = []
    for match in regex.finditer(text):
        if isinstance(group, int):
            raw = match.group(group)
        else:
            group_text = str(group)
            raw = match.group(group_text if not group_text.isdigit() else int(group_text))
        values.append(parse_number(raw))
    if not values:
        raise ValueError(f"No values matched metric regex for {metric['name']}.")
    return values


def select_metric_value(values: List[float], occurrence: str) -> float:
    if occurrence == "first":
        return values[0]
    if occurrence == "last":
        return values[-1]
    if occurrence == "min":
        return min(values)
    if occurrence == "max":
        return max(values)
    if occurrence == "mean":
        return statistics.fmean(values)
    if occurrence == "median":
        return statistics.median(values)
    raise ValueError(f"Unsupported occurrence policy: {occurrence}")


def selected_metric(text: str, cfg: Dict[str, Any]) -> Tuple[List[float], float]:
    values = extract_metric_values(text, cfg)
    selected = select_metric_value(values, cfg["metric"].get("occurrence", "last"))
    return values, selected


def improvement_percent(base_value: float, opt_value: float, direction: str) -> float:
    if base_value == 0:
        raise ValueError("Cannot compute improvement when baseline metric is zero.")
    denominator = abs(base_value)
    if direction == "lower_is_better":
        return (base_value - opt_value) / denominator * 100.0
    if direction == "higher_is_better":
        return (opt_value - base_value) / denominator * 100.0
    raise ValueError(f"Unsupported metric direction: {direction}")


def cmd_parse_metric(args: argparse.Namespace) -> int:
    try:
        cfg = normalize_config(Path(args.config))
    except ConfigError as exc:
        return print_config_error(exc)

    if args.input == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8", errors="replace")

    try:
        values, selected = selected_metric(text, cfg)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 4

    payload = {
        "metric": cfg["metric"]["name"],
        "direction": cfg["metric"]["direction"],
        "occurrence": cfg["metric"].get("occurrence", "last"),
        "values": values,
        "selected_value": selected,
    }
    print(json.dumps(payload, indent=2))
    return 0


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "software"


def report_names(cfg: Dict[str, Any], iteration: int) -> Dict[str, str]:
    software = safe_name(cfg["software"]["name"])
    prefix = f"{software}-iter{iteration}"
    return {
        "base_test": f"{prefix}-base-test-result.md",
        "opt_test": f"{prefix}-opt-test-result.md",
        "base_summary": f"{prefix}-base-summary-result.md",
        "opt_summary": f"{prefix}-opt-summary-result.md",
    }


def command_summary(cfg: Dict[str, Any]) -> str:
    return (
        f"BUILD: {cfg['commands']['build']} ; "
        f"UT: {cfg['commands']['ut']} ; "
        f"PERF: {cfg['commands']['perftest']}"
    )


def iteration_command(cfg: Dict[str, Any]) -> str:
    return "\n".join(
        [
            "set -e",
            "echo '## build'",
            cfg["commands"]["build"],
            "echo '## ut'",
            cfg["commands"]["ut"],
            "echo '## perftest'",
            cfg["commands"]["perftest"],
        ]
    )


def render_test_report(
    cfg: Dict[str, Any],
    *,
    iteration: int,
    variant: str,
    ref: str,
    command: str,
    exit_code: int,
    output: str,
    metric_value: Optional[float],
) -> str:
    metric_line = "not parsed" if metric_value is None else f"{metric_value:.6g}"
    return "\n".join(
        [
            f"# {cfg['software']['name']} iter{iteration} {variant} test result",
            "",
            f"- ref: `{ref}`",
            f"- command: `{command}`",
            f"- exit_code: `{exit_code}`",
            f"- metric: `{cfg['metric']['name']}`",
            f"- parsed_metric_value: `{metric_line}`",
            "",
            "## Raw output",
            "",
            "```text",
            output.rstrip(),
            "```",
            "",
        ]
    )


def render_summary_report(
    cfg: Dict[str, Any],
    *,
    iteration: int,
    variant: str,
    base_ref: str,
    opt_ref: str,
    base_metric: Optional[float],
    opt_metric: Optional[float],
    improvement: Optional[float],
    decision: str,
    reason: str,
    next_direction: str,
    optimization_overview: str,
) -> str:
    threshold = float(cfg["optimization"]["threshold_percent"])
    improvement_line = "not available" if improvement is None else f"{improvement:.3f}%"
    base_line = "not parsed" if base_metric is None else f"{base_metric:.6g}"
    opt_line = "not parsed" if opt_metric is None else f"{opt_metric:.6g}"
    lines = [
        f"# {cfg['software']['name']} iter{iteration} {variant} summary",
        "",
        f"- base_ref: `{base_ref}`",
        f"- opt_ref: `{opt_ref}`",
        f"- metric: `{cfg['metric']['name']}` ({cfg['metric']['direction']})",
        f"- base_metric: `{base_line}`",
        f"- opt_metric: `{opt_line}`",
        f"- improvement: `{improvement_line}`",
        f"- threshold_percent: `{threshold:g}`",
        f"- decision: `{decision}`",
        f"- reason: {reason}",
        f"- next_direction: {next_direction}",
    ]
    if variant != "base":
        overview = optimization_overview.strip() or "not provided"
        lines.append(f"- optimization_overview: {overview}")
    lines.append("")
    return "\n".join(lines)


def commit_message_from_overview(optimization_overview: str) -> str:
    message = "\n".join(line.rstrip() for line in optimization_overview.strip().splitlines()).strip()
    if not message:
        raise ValueError("optimization_overview is required when committing an accepted iteration.")
    return message


def remote_relative_path(parent: str, child: str) -> Optional[str]:
    parent_clean = parent.rstrip("/")
    child_clean = child.rstrip("/")
    if child_clean == parent_clean:
        return "."
    prefix = parent_clean + "/"
    if child_clean.startswith(prefix):
        return child_clean[len(prefix) :].strip("/")
    return None


def commit_excluded_pathspecs(cfg: Dict[str, Any]) -> List[str]:
    repo = cfg["software"]["repo_path"]
    excludes = {
        ".e2e-auto-optimize",
    }
    for key in ("test_report_dir", "summary_report_dir", "data_dir", "perf_data_dir"):
        rel = remote_relative_path(repo, cfg["workspace"][key])
        if rel and rel != ".":
            excludes.add(rel)
    return sorted(excludes)


def commit_accepted_changes(
    cfg: Dict[str, Any],
    *,
    optimization_overview: str,
) -> Tuple[str, str]:
    message = commit_message_from_overview(optimization_overview)
    pathspecs = ["."] + [f":(exclude){path}" for path in commit_excluded_pathspecs(cfg)]
    q_pathspecs = " ".join(remote_quote(pathspec) for pathspec in pathspecs)
    q_message = remote_quote(message)
    command = "\n".join(
        [
            "set -e",
            f"{git_cmd(cfg, f'add -A -- {q_pathspecs}')}",
            f"if {git_cmd(cfg, 'diff --cached --quiet')}; then",
            "  echo '__E2E_NO_ACCEPTED_CHANGES__'",
            "  exit 7",
            "fi",
            f"{git_cmd(cfg, f'commit -m {q_message}')}",
            f"{git_cmd(cfg, 'rev-parse --short HEAD')}",
        ]
    )
    result = run_ssh(cfg, command)
    if result.returncode != 0:
        raise RemoteError(
            f"Failed to commit accepted iteration with optimization_overview as message.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    commit_hash = ""
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if re.fullmatch(r"[0-9a-fA-F]{7,40}", line):
            commit_hash = line
            break
    return "committed", commit_hash


def write_local(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def cmd_render_reports(args: argparse.Namespace) -> int:
    try:
        cfg = normalize_config(Path(args.config))
    except ConfigError as exc:
        return print_config_error(exc)

    base_output = Path(args.base_output).read_text(encoding="utf-8", errors="replace")
    opt_output = Path(args.opt_output).read_text(encoding="utf-8", errors="replace")
    base_metric = opt_metric = improvement = None
    reason = args.reason
    try:
        _, base_metric = selected_metric(base_output, cfg)
        _, opt_metric = selected_metric(opt_output, cfg)
        improvement = improvement_percent(base_metric, opt_metric, cfg["metric"]["direction"])
    except ValueError as exc:
        reason = f"{reason}; metric parse failed: {exc}" if reason else f"metric parse failed: {exc}"

    names = report_names(cfg, args.iteration)
    output_dir = Path(args.output_dir)
    command = command_summary(cfg)

    files = {
        names["base_test"]: render_test_report(
            cfg,
            iteration=args.iteration,
            variant="base",
            ref=args.base_ref,
            command=command,
            exit_code=args.base_exit_code,
            output=base_output,
            metric_value=base_metric,
        ),
        names["opt_test"]: render_test_report(
            cfg,
            iteration=args.iteration,
            variant="opt",
            ref=args.opt_ref,
            command=command,
            exit_code=args.opt_exit_code,
            output=opt_output,
            metric_value=opt_metric,
        ),
        names["base_summary"]: render_summary_report(
            cfg,
            iteration=args.iteration,
            variant="base",
            base_ref=args.base_ref,
            opt_ref=args.opt_ref,
            base_metric=base_metric,
            opt_metric=opt_metric,
            improvement=improvement,
            decision=args.decision,
            reason=reason,
            next_direction=args.next_direction,
            optimization_overview="",
        ),
        names["opt_summary"]: render_summary_report(
            cfg,
            iteration=args.iteration,
            variant="opt",
            base_ref=args.base_ref,
            opt_ref=args.opt_ref,
            base_metric=base_metric,
            opt_metric=opt_metric,
            improvement=improvement,
            decision=args.decision,
            reason=reason,
            next_direction=args.next_direction,
            optimization_overview=args.optimization_overview,
        ),
    }

    for name, content in files.items():
        write_local(output_dir / name, content)
        print(output_dir / name)
    return 0


def write_remote_file(cfg: Dict[str, Any], remote_path: str, content: str) -> None:
    parent = posixpath.dirname(remote_path)
    command = f"mkdir -p {remote_quote(parent)} && cat > {remote_quote(remote_path)}"
    result = run_ssh(cfg, command, input_text=content)
    if result.returncode != 0:
        raise RemoteError(
            f"Failed to write remote file {remote_path}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def remote_command_output(
    cfg: Dict[str, Any],
    worktree: str,
    command: str,
    *,
    timeout: Optional[int],
) -> Tuple[int, str]:
    wrapped = "\n".join(
        [
            "set -o pipefail",
            f"cd {remote_quote(worktree)}",
            f"({command}) 2>&1",
        ]
    )
    result = run_ssh(cfg, wrapped, timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output


def create_worktree(cfg: Dict[str, Any], path: str, ref: str) -> None:
    parent = posixpath.dirname(path)
    repo = cfg["software"]["repo_path"]
    q_path = remote_quote(path)
    q_repo = remote_quote(repo)
    q_ref = remote_quote(ref)
    command = "\n".join(
        [
            "set -e",
            f"mkdir -p {remote_quote(parent)}",
            f"{git_cmd(cfg, f'worktree remove --force {q_path}')} >/dev/null 2>&1 || true",
            f"rm -rf {q_path}",
            "if "
            f"{git_cmd(cfg, f'worktree add --force {q_path} {q_ref}')}"
            "; then",
            "  :",
            "else",
            "  echo 'git worktree add failed; falling back to archive checkout' >&2",
            f"  rm -rf {q_path}",
            f"  mkdir -p {q_path}",
            f"  {git_cmd(cfg, f'archive {q_ref}')} | tar -x -C {q_path}",
            "fi",
        ]
    )
    run_required_ssh(cfg, command)


def remove_worktree(cfg: Dict[str, Any], path: str) -> None:
    q_path = remote_quote(path)
    command = f"{git_cmd(cfg, f'worktree remove --force {q_path}')} >/dev/null 2>&1 || rm -rf {q_path}"
    run_ssh(cfg, command)


def cmd_run_iteration(args: argparse.Namespace) -> int:
    try:
        cfg = normalize_config(Path(args.config))
    except ConfigError as exc:
        return print_config_error(exc)

    if not args.allow_dirty:
        status = run_ssh(cfg, git_cmd(cfg, "status --porcelain"))
        if status.returncode != 0:
            print(status.stderr or status.stdout, file=sys.stderr)
            return status.returncode or 1
        if status.stdout.strip():
            print("Remote repo has uncommitted changes; refusing to create worktrees.", file=sys.stderr)
            print(status.stdout.strip(), file=sys.stderr)
            return 3

    base_ref = args.base_ref or cfg["software"].get("baseline_ref", "HEAD")
    opt_ref = args.opt_ref or "HEAD"
    data_dir = cfg["workspace"]["data_dir"].rstrip("/")
    base_wt = posixpath.join(data_dir, "worktrees", f"iter{args.iteration}-base")
    opt_wt = posixpath.join(data_dir, "worktrees", f"iter{args.iteration}-opt")

    try:
        create_worktree(cfg, base_wt, base_ref)
        create_worktree(cfg, opt_wt, opt_ref)

        full_command = iteration_command(cfg)
        base_exit, base_output = remote_command_output(
            cfg,
            base_wt,
            full_command,
            timeout=args.timeout_seconds,
        )
        opt_exit, opt_output = remote_command_output(
            cfg,
            opt_wt,
            full_command,
            timeout=args.timeout_seconds,
        )

        base_metric = opt_metric = improvement = None
        decision = "rejected"
        reason = ""
        if base_exit != 0:
            reason = f"baseline command failed with exit code {base_exit}"
        elif opt_exit != 0:
            reason = f"optimized command failed with exit code {opt_exit}"
        else:
            try:
                _, base_metric = selected_metric(base_output, cfg)
                _, opt_metric = selected_metric(opt_output, cfg)
                improvement = improvement_percent(base_metric, opt_metric, cfg["metric"]["direction"])
                threshold = float(cfg["optimization"]["threshold_percent"])
                if improvement >= threshold:
                    decision = "accepted"
                    reason = f"improvement {improvement:.3f}% >= threshold {threshold:g}%"
                else:
                    reason = f"improvement {improvement:.3f}% < threshold {threshold:g}%"
            except ValueError as exc:
                reason = f"metric parse failed: {exc}"

        names = report_names(cfg, args.iteration)
        test_dir = cfg["workspace"]["test_report_dir"]
        summary_dir = cfg["workspace"]["summary_report_dir"]
        command_line = command_summary(cfg)
        report_payloads = {
            posixpath.join(test_dir, names["base_test"]): render_test_report(
                cfg,
                iteration=args.iteration,
                variant="base",
                ref=base_ref,
                command=command_line,
                exit_code=base_exit,
                output=base_output,
                metric_value=base_metric,
            ),
            posixpath.join(test_dir, names["opt_test"]): render_test_report(
                cfg,
                iteration=args.iteration,
                variant="opt",
                ref=opt_ref,
                command=command_line,
                exit_code=opt_exit,
                output=opt_output,
                metric_value=opt_metric,
            ),
            posixpath.join(summary_dir, names["base_summary"]): render_summary_report(
                cfg,
                iteration=args.iteration,
                variant="base",
                base_ref=base_ref,
                opt_ref=opt_ref,
                base_metric=base_metric,
                opt_metric=opt_metric,
                improvement=improvement,
                decision=decision,
                reason=reason,
                next_direction=args.next_direction,
                optimization_overview="",
            ),
            posixpath.join(summary_dir, names["opt_summary"]): render_summary_report(
                cfg,
                iteration=args.iteration,
                variant="opt",
                base_ref=base_ref,
                opt_ref=opt_ref,
                base_metric=base_metric,
                opt_metric=opt_metric,
                improvement=improvement,
                decision=decision,
                reason=reason,
                next_direction=args.next_direction,
                optimization_overview=args.optimization_overview,
            ),
        }
        for remote_path, content in report_payloads.items():
            write_remote_file(cfg, remote_path, content)

        commit_status = "not_requested"
        commit_hash = ""
        commit_message = ""
        if decision == "accepted" and args.commit_accepted:
            commit_message = commit_message_from_overview(args.optimization_overview)
            commit_status, commit_hash = commit_accepted_changes(
                cfg,
                optimization_overview=args.optimization_overview,
            )

        result_payload = {
            "iteration": args.iteration,
            "base_ref": base_ref,
            "opt_ref": opt_ref,
            "decision": decision,
            "reason": reason,
            "base_metric": base_metric,
            "opt_metric": opt_metric,
            "improvement_percent": improvement,
            "reports": sorted(report_payloads),
            "commit_status": commit_status,
            "commit_hash": commit_hash,
            "commit_message": commit_message,
        }
        print(json.dumps(result_payload, indent=2))
        return 0 if decision == "accepted" else 5
    except (RemoteError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        if not args.keep_worktrees:
            remove_worktree(cfg, base_wt)
            remove_worktree(cfg, opt_wt)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="e2e-auto-optimize helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-config", help="validate and normalize a JSON config")
    validate.add_argument("--config", default=DEFAULT_CONFIG)
    validate.add_argument("--print-normalized", action="store_true")
    validate.set_defaults(func=cmd_validate_config)

    check = sub.add_parser("check-environment", help="check remote SSH, hardware, and repo cleanliness")
    check.add_argument("--config", default=DEFAULT_CONFIG)
    check.add_argument("--allow-dirty", action="store_true")
    check.set_defaults(func=cmd_check_environment)

    parse = sub.add_parser("parse-metric", help="extract the configured metric from perftest output")
    parse.add_argument("--config", default=DEFAULT_CONFIG)
    parse.add_argument("--input", required=True, help="input file, or - for stdin")
    parse.set_defaults(func=cmd_parse_metric)

    reports = sub.add_parser("render-reports", help="render local markdown reports from saved outputs")
    reports.add_argument("--config", default=DEFAULT_CONFIG)
    reports.add_argument("--iteration", type=int, required=True)
    reports.add_argument("--base-output", required=True)
    reports.add_argument("--opt-output", required=True)
    reports.add_argument("--output-dir", required=True)
    reports.add_argument("--base-ref", default="BASE")
    reports.add_argument("--opt-ref", default="OPT")
    reports.add_argument("--base-exit-code", type=int, default=0)
    reports.add_argument("--opt-exit-code", type=int, default=0)
    reports.add_argument("--decision", default="unknown")
    reports.add_argument("--reason", default="")
    reports.add_argument("--next-direction", default="")
    reports.add_argument("--optimization-overview", default="")
    reports.add_argument("--environment-snapshot", default="")
    reports.set_defaults(func=cmd_render_reports)

    iteration = sub.add_parser("run-iteration", help="run remote baseline/optimized comparison using worktrees")
    iteration.add_argument("--config", default=DEFAULT_CONFIG)
    iteration.add_argument("--iteration", type=int, required=True)
    iteration.add_argument("--base-ref", default="")
    iteration.add_argument("--opt-ref", default="")
    iteration.add_argument("--allow-dirty", action="store_true")
    iteration.add_argument("--keep-worktrees", action="store_true")
    iteration.add_argument("--timeout-seconds", type=int, default=None)
    iteration.add_argument("--next-direction", default="")
    iteration.add_argument("--optimization-overview", default="")
    iteration.add_argument("--commit-accepted", action="store_true")
    iteration.set_defaults(func=cmd_run_iteration)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
