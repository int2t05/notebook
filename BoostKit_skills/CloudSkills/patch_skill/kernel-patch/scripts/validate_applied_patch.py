#!/usr/bin/env python3
"""
Validate whether an applied commit still matches the source patch.
"""

import argparse
from collections import Counter
from difflib import SequenceMatcher
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from shared.cli import emit_json, load_json_arg
from shared.config import LOG_FORMAT, LOG_LEVEL, is_config_mapping_source_path
from shared.git_helpers import is_git_repo
from shared.paths import resolve_user_path, to_repo_relative

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
CONFIG_VALUE_RE = re.compile(r"^(CONFIG_[A-Za-z0-9_]+)=(.+)$")
CONFIG_UNSET_RE = re.compile(r"^# (CONFIG_[A-Za-z0-9_]+) is not set$")
FUNC_SIGNATURE_RE = re.compile(
    r"^\s*(?:[A-Za-z_][\w\s\*]*\s+)?[A-Za-z_]\w*\s*\([^;]*\)\s*[;{]\s*$"
)


@dataclass
class Hunk:
    source_start: int = 0
    target_start: int = 0
    lines: List[tuple[str, str]] = field(default_factory=list)
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)


@dataclass
class FileDiff:
    path: str
    old_path: Optional[str] = None
    new_path: Optional[str] = None
    hunks: List[Hunk] = field(default_factory=list)

    @property
    def added_lines(self) -> List[str]:
        lines: List[str] = []
        for hunk in self.hunks:
            lines.extend(hunk.added_lines)
        return lines

    @property
    def removed_lines(self) -> List[str]:
        lines: List[str] = []
        for hunk in self.hunks:
            lines.extend(hunk.removed_lines)
        return lines


def _run_git(args: List[str], repo_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=repo_path, text=True, capture_output=True)


def _normalize_line(line: str) -> str:
    return line.rstrip()


def _normalize_line_for_compare(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _clean_file_path(path: str | None) -> str:
    if path is None:
        return "/dev/null"
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def _parse_patch_text(text: str) -> Dict[str, FileDiff]:
    files: Dict[str, FileDiff] = {}
    current: Optional[FileDiff] = None
    current_hunk: Optional[Hunk] = None

    for raw in text.splitlines():
        if raw.startswith("diff --git "):
            if current and current_hunk:
                current.hunks.append(current_hunk)
            current_hunk = None
            parts = raw.split()
            old_path = parts[2][2:] if len(parts) > 2 and parts[2].startswith("a/") else None
            new_path = parts[3][2:] if len(parts) > 3 and parts[3].startswith("b/") else None
            path = new_path or old_path or "/dev/null"
            current = FileDiff(path=path, old_path=old_path, new_path=new_path)
            files[path] = current
            continue
        if current is None:
            continue
        if raw.startswith("--- "):
            if raw == "--- /dev/null":
                current.old_path = "/dev/null"
            elif raw.startswith("--- a/"):
                current.old_path = raw[6:]
            continue
        if raw.startswith("+++ "):
            if raw == "+++ /dev/null":
                current.new_path = "/dev/null"
            elif raw.startswith("+++ b/"):
                current.new_path = raw[6:]
                current.path = current.new_path
                files[current.path] = current
            continue
        hunk_match = HUNK_RE.match(raw)
        if hunk_match:
            if current_hunk:
                current.hunks.append(current_hunk)
            current_hunk = Hunk(
                source_start=int(hunk_match.group(1)),
                target_start=int(hunk_match.group(3)),
            )
            continue
        if current_hunk is None:
            continue
        if raw.startswith("\\"):
            continue
        if raw == "-- " or raw.startswith("-- \n"):
            current.hunks.append(current_hunk)
            current_hunk = None
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            content = _normalize_line(raw[1:])
            current_hunk.lines.append(("+", content))
            current_hunk.added_lines.append(content)
        elif raw.startswith("-") and not raw.startswith("---"):
            content = _normalize_line(raw[1:])
            current_hunk.lines.append(("-", content))
            current_hunk.removed_lines.append(content)
        elif raw.startswith(" "):
            current_hunk.lines.append((" ", _normalize_line(raw[1:])))
            continue
        else:
            current.hunks.append(current_hunk)
            current_hunk = None

    if current and current_hunk:
        current.hunks.append(current_hunk)
    return files


def parse_patch_text(text: str) -> Dict[str, FileDiff]:
    return _parse_patch_text(text)


def _read_commit_patch(repo_path: str, commit_ref: str) -> str:
    result = _run_git(["git", "show", "--format=", "--no-ext-diff", commit_ref], repo_path)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"无法读取提交 {commit_ref}")
    return result.stdout


def _read_blob_lines(repo_path: str, commit_ref: str, path: str) -> Optional[List[str]]:
    blob = _run_git(["git", "show", f"{commit_ref}:{path}"], repo_path)
    if blob.returncode != 0:
        return None
    return blob.stdout.splitlines()


def _counter_diff(expected: Counter[str], actual: Counter[str]) -> List[Dict[str, object]]:
    diffs: List[Dict[str, object]] = []
    for line in sorted(expected):
        expected_count = expected[line]
        actual_count = actual.get(line, 0)
        if expected_count > actual_count:
            diffs.append({
                "line": line,
                "expected_count": expected_count,
                "actual_count": actual_count,
                "missing_count": expected_count - actual_count,
            })
    return diffs


def _counter_extras(expected: Counter[str], actual: Counter[str]) -> List[Dict[str, object]]:
    extras: List[Dict[str, object]] = []
    for line in sorted(actual):
        actual_count = actual[line]
        expected_count = expected.get(line, 0)
        if actual_count > expected_count:
            extras.append({
                "line": line,
                "expected_count": expected_count,
                "actual_count": actual_count,
                "extra_count": actual_count - expected_count,
            })
    return extras


def _file_key(file_diff: FileDiff) -> tuple[str, str]:
    return (_clean_file_path(file_diff.old_path), _clean_file_path(file_diff.new_path))


def _normalize_hunk_lines(hunk: Hunk) -> List[str]:
    return [f"{line_type}:{_normalize_line_for_compare(content)}" for line_type, content in hunk.lines]


def _collect_lines(hunk: Hunk, line_type: str) -> List[str]:
    return [content for current_type, content in hunk.lines if current_type == line_type]


def _collect_file_lines(file_diff: FileDiff, line_type: str) -> List[str]:
    lines: List[str] = []
    for hunk in file_diff.hunks:
        lines.extend(_collect_lines(hunk, line_type))
    return lines


def _multiset_difference_by_normalized(left_raw: List[str], right_raw: List[str]) -> List[str]:
    right_counter = Counter(_normalize_line_for_compare(item) for item in right_raw)
    diff: List[str] = []
    for item in left_raw:
        normalized = _normalize_line_for_compare(item)
        if right_counter.get(normalized, 0) > 0:
            right_counter[normalized] -= 1
        else:
            diff.append(item)
    return diff


def _align_hunks(local_hunks: List[Hunk], merged_hunks: List[Hunk]) -> List[tuple[Optional[Hunk], Optional[Hunk]]]:
    aligned: List[tuple[Optional[Hunk], Optional[Hunk]]] = []
    used_merged = set()
    for local_hunk in local_hunks:
        best_idx = None
        best_score = -1.0
        local_signature = "\n".join(_normalize_hunk_lines(local_hunk))
        for index, merged_hunk in enumerate(merged_hunks):
            if index in used_merged:
                continue
            merged_signature = "\n".join(_normalize_hunk_lines(merged_hunk))
            score = SequenceMatcher(None, local_signature, merged_signature).ratio()
            if score > best_score:
                best_idx = index
                best_score = score
        if best_idx is not None:
            aligned.append((local_hunk, merged_hunks[best_idx]))
            used_merged.add(best_idx)
        else:
            aligned.append((local_hunk, None))
    for index, merged_hunk in enumerate(merged_hunks):
        if index not in used_merged:
            aligned.append((None, merged_hunk))
    return aligned


def _compare_hunk_pair(local_hunk: Optional[Hunk], merged_hunk: Optional[Hunk]) -> Dict[str, object]:
    if local_hunk is None and merged_hunk is not None:
        return {
            "local_hunk_number": None,
            "merged_hunk_number": merged_hunk.target_start,
            "status": "extra-hunk",
            "missing_added_lines": [],
            "extra_added_lines": _collect_lines(merged_hunk, "+"),
            "removed_line_mismatches": [],
            "similarity": 0.0,
        }
    if local_hunk is not None and merged_hunk is None:
        return {
            "local_hunk_number": local_hunk.target_start,
            "merged_hunk_number": None,
            "status": "missing-hunk",
            "missing_added_lines": _collect_lines(local_hunk, "+"),
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "similarity": 0.0,
        }
    if local_hunk is None or merged_hunk is None:
        return {
            "local_hunk_number": None,
            "merged_hunk_number": None,
            "status": "different",
            "missing_added_lines": [],
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "similarity": 0.0,
        }

    local_added = _collect_lines(local_hunk, "+")
    merged_added = _collect_lines(merged_hunk, "+")
    local_removed = _collect_lines(local_hunk, "-")
    merged_removed = _collect_lines(merged_hunk, "-")
    missing_added = _multiset_difference_by_normalized(local_added, merged_added)
    extra_added = _multiset_difference_by_normalized(merged_added, local_added)
    removed_mismatches = (
        _multiset_difference_by_normalized(local_removed, merged_removed)
        + _multiset_difference_by_normalized(merged_removed, local_removed)
    )
    similarity = SequenceMatcher(
        None,
        "\n".join(_normalize_hunk_lines(local_hunk)),
        "\n".join(_normalize_hunk_lines(merged_hunk)),
    ).ratio()
    status = "identical"
    if missing_added or extra_added or removed_mismatches:
        status = "different"
    return {
        "local_hunk_number": local_hunk.target_start,
        "merged_hunk_number": merged_hunk.target_start,
        "status": status,
        "missing_added_lines": missing_added,
        "extra_added_lines": extra_added,
        "removed_line_mismatches": removed_mismatches,
        "similarity": round(similarity, 4),
    }


def _compare_file_diffs(local_file: FileDiff, merged_file: Optional[FileDiff]) -> Dict[str, object]:
    source_file = _clean_file_path(local_file.old_path)
    target_file = _clean_file_path(local_file.new_path or local_file.path)
    if merged_file is None:
        return {
            "path": target_file,
            "source_file": source_file,
            "target_file": target_file,
            "status": "missing-file",
            "missing_added_lines": _collect_file_lines(local_file, "+"),
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "hunk_differences": [],
        }

    local_added_all = _collect_file_lines(local_file, "+")
    merged_added_all = _collect_file_lines(merged_file, "+")
    local_removed_all = _collect_file_lines(local_file, "-")
    merged_removed_all = _collect_file_lines(merged_file, "-")
    all_missing = _multiset_difference_by_normalized(local_added_all, merged_added_all)
    all_extra = _multiset_difference_by_normalized(merged_added_all, local_added_all)
    all_removed_mismatches = (
        _multiset_difference_by_normalized(local_removed_all, merged_removed_all)
        + _multiset_difference_by_normalized(merged_removed_all, local_removed_all)
    )
    hunk_differences = [
        _compare_hunk_pair(local_hunk, merged_hunk)
        for local_hunk, merged_hunk in _align_hunks(local_file.hunks, merged_file.hunks)
    ]

    status = "identical"
    if all_missing or all_extra or all_removed_mismatches:
        has_missing_hunk = any(item["status"] == "missing-hunk" for item in hunk_differences)
        if has_missing_hunk and not all_extra and not all_removed_mismatches:
            status = "missing-hunk"
        elif all_missing and (all_extra or all_removed_mismatches):
            status = "semantic-substitution-suspected"
        else:
            status = "different"

    return {
        "path": target_file,
        "source_file": source_file,
        "target_file": target_file,
        "status": status,
        "missing_added_lines": all_missing,
        "extra_added_lines": all_extra,
        "removed_line_mismatches": all_removed_mismatches,
        "hunk_differences": hunk_differences,
    }


def _symbol_name(line: str) -> Optional[str]:
    value_match = CONFIG_VALUE_RE.match(line)
    if value_match:
        return value_match.group(1)
    unset_match = CONFIG_UNSET_RE.match(line)
    if unset_match:
        return unset_match.group(1)
    return None


def _extract_missing_symbols(
    missing_added: List[Dict[str, object]],
    lingering_removed: List[Dict[str, object]],
) -> List[str]:
    symbols: List[str] = []
    seen = set()
    for item in missing_added + lingering_removed:
        symbol = _symbol_name(str(item["line"]))
        if symbol and symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)
    return symbols


def _normalize_config_targets(config_targets: Dict[str, List[str]], repo_path: str) -> Dict[str, List[str]]:
    normalized: Dict[str, List[str]] = {}
    for source_path, targets in config_targets.items():
        converted = []
        for target in targets:
            if os.path.isabs(target):
                converted.append(to_repo_relative(target, repo_path))
            else:
                converted.append(os.path.normpath(target))
        normalized[source_path] = converted
    return normalized


def _is_config_boundary_issue(issue: Dict[str, object], config_targets: Dict[str, List[str]]) -> bool:
    path = issue.get("path")
    if not isinstance(path, str):
        return False
    if path in config_targets:
        return True
    mapped_targets = {target for targets in config_targets.values() for target in targets}
    return path in mapped_targets


def _count_by_status(items: List[Dict[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        status = item.get("status")
        if not isinstance(status, str):
            continue
        counts[status] = counts.get(status, 0) + 1
    return counts


def _iter_issue_lines(issue: Dict[str, object]) -> List[str]:
    lines: List[str] = []
    for key in ("missing_added_lines", "extra_added_lines", "removed_line_mismatches"):
        values = issue.get(key, [])
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str):
                lines.append(value)
            elif isinstance(value, dict) and isinstance(value.get("line"), str):
                lines.append(str(value["line"]))
    return lines


def _build_file_signals(issue: Dict[str, object]) -> List[str]:
    lines = _iter_issue_lines(issue)
    signals: List[str] = []
    if any(line.strip().startswith(("#ifdef", "#ifndef", "#endif", "#include")) for line in lines):
        signals.append("macro-boundary-shift")
    if any(FUNC_SIGNATURE_RE.match(line.strip()) for line in lines):
        signals.append("function-signature-shift")
    if any("list_add(" in line or "list_del(" in line for line in lines):
        signals.append("critical-list-operation-shift")
    if any(line.strip().startswith("return ") for line in lines):
        signals.append("return-semantics-shift")
    return signals


def _build_evidence_signals(
    *,
    status: str,
    issues: List[Dict[str, object]],
    config_results: List[Dict[str, object]],
    source_analysis: Optional[Dict[str, object]],
    saw_config_mapping: bool,
    saw_config_problem: bool,
) -> List[Dict[str, object]]:
    signals: List[Dict[str, object]] = []

    def add_signal(code: str, severity: str, scope: str, details: Dict[str, object]) -> None:
        signals.append({
            "code": code,
            "severity": severity,
            "scope": scope,
            "details": details,
        })

    issue_counts = _count_by_status(issues)
    for issue_status, count in issue_counts.items():
        add_signal(
            code=f"issue-{issue_status}",
            severity="high" if issue_status in {"missing-hunk", "missing-file"} else "medium",
            scope="patch",
            details={"count": count},
        )

    for issue in issues:
        path = issue.get("path")
        if not isinstance(path, str):
            continue
        for file_signal in _build_file_signals(issue):
            add_signal(
                code=file_signal,
                severity="medium",
                scope="file",
                details={"path": path, "status": issue.get("status")},
            )

    config_counts = _count_by_status(config_results)
    for config_status, count in config_counts.items():
        if config_status in {"config-mapped-equivalent"}:
            continue
        add_signal(
            code=f"config-{config_status}",
            severity="high" if config_status in {"config-unmapped", "config-target-missing"} else "medium",
            scope="config",
            details={"count": count},
        )

    if saw_config_mapping:
        add_signal(
            code="config-mapping-enabled",
            severity="info",
            scope="config",
            details={"has_problem": saw_config_problem},
        )

    if status == "missing-hunk" and isinstance(source_analysis, dict):
        add_signal(
            code="missing-hunk-source-analysis",
            severity="info",
            scope="patch",
            details={
                "source_type": source_analysis.get("source_type", "unknown"),
                "confidence": source_analysis.get("confidence", "low"),
                "auto_continue_eligible": bool(source_analysis.get("auto_continue_eligible")),
            },
        )

    return signals


def _build_validation_evidence(
    *,
    status: str,
    issues: List[Dict[str, object]],
    config_results: List[Dict[str, object]],
    source_analysis: Optional[Dict[str, object]],
    saw_config_mapping: bool,
    saw_config_problem: bool,
) -> Dict[str, object]:
    line_stats = {
        "missing_added": 0,
        "extra_added": 0,
        "removed_mismatches": 0,
    }
    file_items: List[Dict[str, object]] = []
    for index, issue in enumerate(issues):
        missing_added = issue.get("missing_added_lines", [])
        extra_added = issue.get("extra_added_lines", [])
        removed_mismatches = issue.get("removed_line_mismatches", [])
        hunk_differences = issue.get("hunk_differences", [])

        line_stats["missing_added"] += len(missing_added) if isinstance(missing_added, list) else 0
        line_stats["extra_added"] += len(extra_added) if isinstance(extra_added, list) else 0
        line_stats["removed_mismatches"] += len(removed_mismatches) if isinstance(removed_mismatches, list) else 0

        file_items.append({
            "path": issue.get("path"),
            "status": issue.get("status"),
            "line_stats": {
                "missing_added": len(missing_added) if isinstance(missing_added, list) else 0,
                "extra_added": len(extra_added) if isinstance(extra_added, list) else 0,
                "removed_mismatches": len(removed_mismatches) if isinstance(removed_mismatches, list) else 0,
            },
            "hunk_stats": {
                "hunk_differences": len(hunk_differences) if isinstance(hunk_differences, list) else 0,
            },
            "signals": _build_file_signals(issue),
            "raw_issue_ref": index,
        })

    return {
        "schema_version": 1,
        "status": status,
        "summary": {
            "issue_count": len(issues),
            "config_result_count": len(config_results),
            "issue_status_counts": _count_by_status(issues),
            "config_status_counts": _count_by_status(config_results),
            "line_stats": line_stats,
        },
        "files": file_items,
        "signals": _build_evidence_signals(
            status=status,
            issues=issues,
            config_results=config_results,
            source_analysis=source_analysis,
            saw_config_mapping=saw_config_mapping,
            saw_config_problem=saw_config_problem,
        ),
        "source_analysis": source_analysis or {},
    }


def _analyze_missing_hunk_prereq(
    issues: List[Dict[str, object]],
    prior_patch_files: List[str],
) -> Dict[str, object] | None:
    if not prior_patch_files:
        return None

    missing_by_path: Dict[str, Dict[str, Counter[str]]] = {}
    total_missing = 0
    for issue in issues:
        if issue.get("status") != "missing-hunk":
            continue
        path = issue.get("path")
        if not isinstance(path, str):
            continue
        path_missing = missing_by_path.setdefault(path, {
            "added": Counter(),
            "removed": Counter(),
        })
        for line in issue.get("missing_added_lines", []):
            if isinstance(line, str):
                path_missing["added"][line] += 1
                total_missing += 1
        for line in issue.get("removed_line_mismatches", []):
            if isinstance(line, str):
                path_missing["removed"][line] += 1
                total_missing += 1

    if total_missing == 0:
        return {
            "performed": True,
            "classification": "unknown",
            "reason": "no-missing-lines",
            "total_missing_lines": 0,
            "overlap_missing_lines": 0,
            "overlap_ratio": 0.0,
            "matched_prior_patches": [],
            "checked_prior_patch_count": len(prior_patch_files),
        }

    overlap_missing = 0
    matched_prior_patches: List[Dict[str, object]] = []
    checked_count = 0
    for patch_file in prior_patch_files:
        patch_file = resolve_user_path(patch_file)
        if not os.path.isfile(patch_file):
            continue
        checked_count += 1
        with open(patch_file, "r", encoding="utf-8", errors="ignore") as handle:
            prior_files = _parse_patch_text(handle.read())
        patch_overlap = 0
        for path, missing in missing_by_path.items():
            prior_diff = prior_files.get(path)
            if prior_diff is None:
                continue
            added_counter = Counter(prior_diff.added_lines)
            removed_counter = Counter(prior_diff.removed_lines)
            for line, count in missing["added"].items():
                patch_overlap += min(count, added_counter.get(line, 0))
            for line, count in missing["removed"].items():
                patch_overlap += min(count, removed_counter.get(line, 0))
        overlap_missing += patch_overlap
        if patch_overlap:
            matched_prior_patches.append({
                "patch_file": patch_file,
                "overlap_missing_lines": patch_overlap,
            })

    overlap_ratio = (float(overlap_missing) / float(total_missing)) if total_missing else 0.0
    if overlap_missing >= 3 and overlap_ratio >= 0.5:
        classification = "likely-missing-prerequisite"
        reason = "high-overlap-with-prior-patches"
    elif overlap_missing > 0:
        classification = "unknown"
        reason = "partial-overlap-with-prior-patches"
    else:
        classification = "likely-context-drift"
        reason = "no-overlap-with-prior-patches"

    return {
        "performed": True,
        "classification": classification,
        "reason": reason,
        "total_missing_lines": total_missing,
        "overlap_missing_lines": overlap_missing,
        "overlap_ratio": round(overlap_ratio, 4),
        "matched_prior_patches": matched_prior_patches,
        "checked_prior_patch_count": checked_count,
    }


def _collect_missing_hunk_lines(issues: List[Dict[str, object]]) -> Dict[str, List[str]]:
    lines_by_path: Dict[str, List[str]] = {}
    for issue in issues:
        if issue.get("status") != "missing-hunk":
            continue
        path = issue.get("path")
        if not isinstance(path, str):
            continue
        bucket = lines_by_path.setdefault(path, [])
        for line in issue.get("missing_added_lines", []):
            if isinstance(line, str) and line not in bucket:
                bucket.append(line)
    return lines_by_path


def _resolve_commit_sha(repo_path: str, commit_ref: str) -> Optional[str]:
    result = _run_git(["git", "rev-parse", commit_ref], repo_path)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _analyze_missing_hunk_external_source(
    repo_path: str,
    commit_ref: str,
    issues: List[Dict[str, object]],
) -> Dict[str, object]:
    missing_by_path = _collect_missing_hunk_lines(issues)
    total_missing = sum(len(lines) for lines in missing_by_path.values())
    if total_missing == 0:
        return {
            "performed": False,
            "source_type": "unknown",
            "confidence": "low",
            "auto_continue_level": "none",
            "auto_continue_eligible": False,
            "reason": "no-missing-lines",
            "matched_commits": [],
            "checked_commit_count": 0,
            "total_missing_lines": 0,
            "matched_missing_lines": 0,
            "match_ratio": 0.0,
            "auto_continue": False,
        }

    commit_sha = _resolve_commit_sha(repo_path, commit_ref)
    matched_lines = 0
    checked_commit_count = 0
    matched_commits: List[Dict[str, object]] = []

    for path, missing_lines in missing_by_path.items():
        history = _run_git(["git", "log", "--format=%H", "-n", "80", "--", path], repo_path)
        if history.returncode != 0:
            continue
        commit_refs = [line.strip() for line in history.stdout.splitlines() if line.strip()]
        for hist_commit in commit_refs:
            if commit_sha and hist_commit == commit_sha:
                continue
            blob_lines = _read_blob_lines(repo_path, hist_commit, path)
            if blob_lines is None:
                continue
            checked_commit_count += 1
            normalized_blob = {_normalize_line(line) for line in blob_lines}
            current_match = [line for line in missing_lines if _normalize_line(line) in normalized_blob]
            if not current_match:
                continue
            matched_lines += len(current_match)
            matched_commits.append({
                "commit": hist_commit,
                "path": path,
                "matched_line_count": len(current_match),
                "matched_lines_sample": current_match[:5],
            })
            # 命中后停止该路径继续搜索，避免放大统计
            break

    ratio = float(matched_lines) / float(total_missing) if total_missing else 0.0
    if matched_lines >= 3 and ratio >= 0.6:
        confidence = "high"
        auto_continue_level = "high"
        auto_continue = True
        reason = "strong-history-overlap"
    elif matched_lines > 0:
        confidence = "medium"
        auto_continue_level = "medium"
        auto_continue = True
        reason = "partial-history-overlap"
    else:
        confidence = "low"
        auto_continue_level = "low"
        auto_continue = False
        reason = "no-history-overlap"

    return {
        "performed": True,
        "source_type": "external-history" if matched_lines > 0 else "unknown",
        "confidence": confidence,
        "auto_continue_level": auto_continue_level,
        "auto_continue_eligible": False,
        "reason": reason,
        "matched_commits": matched_commits,
        "checked_commit_count": checked_commit_count,
        "total_missing_lines": total_missing,
        "matched_missing_lines": matched_lines,
        "match_ratio": round(ratio, 4),
        "auto_continue": auto_continue,
    }


def _analyze_missing_hunk_source(
    repo_path: str,
    commit_ref: str,
    issues: List[Dict[str, object]],
    prior_patch_files: List[str],
) -> Dict[str, object]:
    prereq = _analyze_missing_hunk_prereq(issues, prior_patch_files)
    if prereq and prereq.get("classification") == "likely-missing-prerequisite":
        return {
            "performed": True,
            "source_type": "prior-task",
            "confidence": "high",
            "auto_continue_level": "high",
            "auto_continue_eligible": True,
            "reason": prereq.get("reason"),
            "matched_prior_patches": prereq.get("matched_prior_patches", []),
            "total_missing_lines": prereq.get("total_missing_lines", 0),
            "matched_missing_lines": prereq.get("overlap_missing_lines", 0),
            "match_ratio": prereq.get("overlap_ratio", 0.0),
            "auto_continue": True,
        }
    external = _analyze_missing_hunk_external_source(repo_path, commit_ref, issues)
    external["prereq_analysis"] = prereq
    return external


def validate_applied_patch(
    patch_file: str,
    repo_path: str,
    commit_ref: str = "HEAD",
    config_targets: Optional[Dict[str, List[str]]] = None,
    prior_patch_files: Optional[List[str]] = None,
) -> str:
    try:
        patch_file = resolve_user_path(patch_file)
        repo_path = resolve_user_path(repo_path)
        config_targets = _normalize_config_targets(config_targets or {}, repo_path)

        if not os.path.isfile(patch_file):
            return json.dumps({"success": False, "error": "补丁文件不存在"}, ensure_ascii=False, indent=2)
        if not is_git_repo(repo_path):
            return json.dumps({"success": False, "error": "目标仓库无效"}, ensure_ascii=False, indent=2)

        with open(patch_file, "r", encoding="utf-8", errors="ignore") as handle:
            local_patch_text = handle.read()
        merged_patch_text = _read_commit_patch(repo_path, commit_ref)

        local_files = _parse_patch_text(local_patch_text)
        merged_files = _parse_patch_text(merged_patch_text)

        issues: List[Dict[str, object]] = []
        config_results: List[Dict[str, object]] = []
        saw_config_mapping = False
        saw_config_problem = False
        merged_by_key = {_file_key(diff): diff for diff in merged_files.values()}

        for path, local_diff in local_files.items():
            if is_config_mapping_source_path(path):
                if path not in config_targets:
                    config_results.append({
                        "source": path,
                        "status": "config-unmapped",
                    })
                    saw_config_problem = True
                    continue

                targets = config_targets[path]
                saw_config_mapping = True
                for target in targets:
                    blob_lines = _read_blob_lines(repo_path, commit_ref, target)
                    if blob_lines is None:
                        config_results.append({
                            "source": path,
                            "target": target,
                            "status": "config-target-missing",
                        })
                        saw_config_problem = True
                        continue

                    target_counter = Counter(_normalize_line(line) for line in blob_lines)
                    added_counter = Counter(local_diff.added_lines)
                    removed_counter = Counter(local_diff.removed_lines)
                    missing_added = _counter_diff(added_counter, target_counter)
                    lingering_removed = []
                    for line in sorted(removed_counter):
                        lingering_count = target_counter.get(line, 0)
                        if lingering_count:
                            lingering_removed.append({
                                "line": line,
                                "expected_removed_count": removed_counter[line],
                                "actual_count": lingering_count,
                            })
                    missing_symbols = _extract_missing_symbols(missing_added, lingering_removed)

                    config_results.append({
                        "source": path,
                        "target": target,
                        "status": "config-mapped-equivalent" if not missing_added and not lingering_removed else "config-mapped-incomplete",
                        "missing_symbols": missing_symbols,
                        "missing_added_lines": missing_added,
                        "lingering_removed_lines": lingering_removed,
                    })
                    if missing_added or lingering_removed:
                        saw_config_problem = True
                continue

            diff = _compare_file_diffs(local_diff, merged_by_key.get(_file_key(local_diff)))
            if diff["status"] != "identical":
                issues.append(diff)

        local_non_config = {path for path in local_files if not is_config_mapping_source_path(path)}
        local_keys = {_file_key(local_files[path]) for path in local_non_config}
        for key, merged_diff in merged_by_key.items():
            target_file = _clean_file_path(merged_diff.new_path or merged_diff.path)
            if is_config_mapping_source_path(target_file) or key in local_keys:
                continue
            issues.append({
                "path": target_file,
                "source_file": _clean_file_path(merged_diff.old_path),
                "target_file": target_file,
                "status": "extra-file",
                "missing_added_lines": [],
                "extra_added_lines": _collect_file_lines(merged_diff, "+"),
                "removed_line_mismatches": [],
                "hunk_differences": [],
            })

        effective_issues = issues
        if saw_config_mapping and not saw_config_problem:
            effective_issues = [
                issue for issue in issues
                if not _is_config_boundary_issue(issue, config_targets)
            ]

        if effective_issues:
            priority = [
                "missing-file",
                "extra-file",
                "different",
                "semantic-substitution-suspected",
                "missing-hunk",
            ]
            statuses = [issue["status"] for issue in effective_issues]
            status = next((item for item in priority if item in statuses), "different")
        elif saw_config_problem:
            statuses = [item["status"] for item in config_results]
            if "config-unmapped" in statuses:
                status = "config-unmapped"
            elif "config-target-missing" in statuses:
                status = "config-target-missing"
            else:
                status = "config-mapped-incomplete"
        elif saw_config_mapping:
            status = "config-mapped-equivalent"
        else:
            status = "identical"

        prereq_analysis = None
        source_analysis = None
        if status == "missing-hunk":
            prereq_analysis = _analyze_missing_hunk_prereq(issues, prior_patch_files or [])
            source_analysis = _analyze_missing_hunk_source(
                repo_path=repo_path,
                commit_ref=commit_ref,
                issues=issues,
                prior_patch_files=prior_patch_files or [],
            )
        evidence = _build_validation_evidence(
            status=status,
            issues=issues,
            config_results=config_results,
            source_analysis=source_analysis,
            saw_config_mapping=saw_config_mapping,
            saw_config_problem=saw_config_problem,
        )

        return json.dumps({
            "success": True,
            "status": status,
            "issues": issues,
            "config_results": config_results,
            "evidence": evidence,
            "prereq_analysis": prereq_analysis,
            "source_analysis": source_analysis,
            "commit_ref": commit_ref,
            "repo_path": repo_path,
            "patch_file": patch_file,
        }, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("补丁验证失败: %s", exc)
        return json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an applied commit against a patch file.")
    parser.add_argument("--patch-file", required=True, help="Patch file path.")
    parser.add_argument("--repo-path", required=True, help="Target repository path.")
    parser.add_argument("--commit-ref", default="HEAD", help="Commit ref to validate.")
    parser.add_argument("--config-targets", default="{}", help="JSON object mapping source config paths to target config files.")
    parser.add_argument("--prior-patch-files", default="[]", help="JSON array of prior patch file paths used for prerequisite analysis.")
    args = parser.parse_args()
    payload = json.loads(validate_applied_patch(
        patch_file=args.patch_file,
        repo_path=args.repo_path,
        commit_ref=args.commit_ref,
        config_targets=load_json_arg(args.config_targets),
        prior_patch_files=load_json_arg(args.prior_patch_files),
    ))
    return emit_json(payload)


if __name__ == "__main__":
    raise SystemExit(main())
