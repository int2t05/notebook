#!/usr/bin/env python3
"""
Analyze whether a patch is likely to drift across commit boundaries.
"""

import argparse
import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from shared.cli import emit_json
from shared.config import LOG_FORMAT, LOG_LEVEL, is_config_mapping_source_path
from shared.git_helpers import branch_exists, is_git_repo
from shared.paths import resolve_user_path

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

FUNCTION_RE = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_\s\*]+?\s+)([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*(?:\{|;)$")
TYPE_RE = re.compile(r"^(?:struct|enum|union)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
DEFINE_RE = re.compile(r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\b")
IGNORED_SYMBOLS = {
    "WFE",
    "WFI",
    "CONFIG",
}


def _run_git(args: List[str], repo_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=repo_path, text=True, capture_output=True)


def _path_scope(path: str) -> Tuple[str, ...]:
    parts = Path(path).parts
    return parts[:2] if len(parts) >= 2 else parts


def _extract_symbol(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("CONFIG_") or stripped.startswith("#include"):
        return ""
    for pattern in (FUNCTION_RE, TYPE_RE, DEFINE_RE):
        match = pattern.match(stripped)
        if match:
            symbol = match.group(1)
            if symbol in IGNORED_SYMBOLS or len(symbol) < 5:
                return ""
            return symbol
    return ""


def _is_added_symbol_line(line: str, current_new_path: str) -> bool:
    if not current_new_path:
        return False
    if not line.startswith("+") or line.startswith("+++"):
        return False
    if is_config_mapping_source_path(current_new_path):
        return False
    return not line[1:2].isspace()


def _collect_symbol_from_line(line: str, current_new_path: str) -> Tuple[str, str]:
    if not _is_added_symbol_line(line, current_new_path):
        return "", ""
    return current_new_path, _extract_symbol(line[1:])


def _parse_patch(patch_file: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    new_files: List[str] = []
    symbols: List[Tuple[str, str]] = []
    current_new = ""

    with open(patch_file, "r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if line.startswith("diff --git "):
                current_new = ""
                continue
            if line.startswith("+++ b/"):
                current_new = line[6:].strip()
                continue
            if line.startswith("--- /dev/null") and current_new:
                new_files.append(current_new)
                continue

            source_path, symbol = _collect_symbol_from_line(line, current_new)
            if symbol:
                symbols.append((source_path, symbol))

    return new_files, symbols


def _collect_existing_file_reasons(
    new_files: List[str], repo_path: str, branch: str
) -> List[Dict[str, object]]:
    reasons: List[Dict[str, object]] = []
    for new_file in new_files:
        exists = _run_git(["git", "cat-file", "-e", f"{branch}:{new_file}"], repo_path)
        if exists.returncode == 0:
            reasons.append({"type": "new-file-already-present", "path": new_file})
    return reasons


def _filter_same_scope_matches(matches_text: str, source_path: str) -> List[str]:
    source_scope = _path_scope(source_path)
    same_scope_matches: List[str] = []
    for grep_match in matches_text.splitlines():
        matched_path = grep_match.split(":", 2)[0].split(":", 1)[-1]
        if _path_scope(matched_path) == source_scope:
            same_scope_matches.append(grep_match)
    return same_scope_matches[:5]


def _collect_symbol_overlap_reasons(
    symbols: List[Tuple[str, str]], repo_path: str, branch: str
) -> Tuple[List[Tuple[str, str]], List[Dict[str, object]]]:
    reasons: List[Dict[str, object]] = []
    seen_symbols = set()
    unique_symbols: List[Tuple[str, str]] = []

    for source_path, symbol in symbols:
        key = (source_path, symbol)
        if key in seen_symbols:
            continue

        seen_symbols.add(key)
        unique_symbols.append(key)
        found = _run_git(["git", "grep", "-n", "-w", symbol, branch, "--"], repo_path)
        if found.returncode != 0 or not found.stdout.strip():
            continue

        same_scope_matches = _filter_same_scope_matches(found.stdout, source_path)
        if same_scope_matches:
            reasons.append(
                {
                    "type": "symbol-already-present",
                    "symbol": symbol,
                    "source_path": source_path,
                    "matches": same_scope_matches,
                }
            )

    return unique_symbols, reasons


def analyze_patch_boundary(patch_file: str, repo_path: str, branch: str) -> str:
    try:
        patch_file = resolve_user_path(patch_file)
        repo_path = resolve_user_path(repo_path)
        if not os.path.isfile(patch_file):
            return json.dumps({"success": False, "error": "补丁文件不存在"}, ensure_ascii=False, indent=2)
        if not is_git_repo(repo_path):
            return json.dumps({"success": False, "error": "目标仓库无效"}, ensure_ascii=False, indent=2)
        if not branch_exists(branch, repo_path):
            return json.dumps({"success": False, "error": f"分支不存在: {branch}"}, ensure_ascii=False, indent=2)

        new_files, symbols = _parse_patch(patch_file)
        unique_symbols, symbol_overlap_reasons = _collect_symbol_overlap_reasons(
            symbols, repo_path, branch
        )
        reasons = _collect_existing_file_reasons(new_files, repo_path, branch)
        reasons.extend(symbol_overlap_reasons)

        if any(item["type"] == "new-file-already-present" for item in reasons):
            status = "already-absorbed"
        elif reasons:
            status = "warning-symbol-overlap"
        else:
            status = "apply-as-is"

        return json.dumps({
            "success": True,
            "status": status,
            "patch_file": patch_file,
            "repo_path": repo_path,
            "branch": branch,
            "new_files": new_files,
            "symbols": [{"path": path, "symbol": symbol} for path, symbol in sorted(unique_symbols)],
            "reasons": reasons,
        }, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("补丁边界分析失败: %s", exc)
        return json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze likely patch boundary drift.")
    parser.add_argument("--patch-file", required=True, help="Patch file path.")
    parser.add_argument("--repo-path", required=True, help="Target repository path.")
    parser.add_argument("--branch", required=True, help="Target branch or test branch.")
    args = parser.parse_args()
    return emit_json(json.loads(analyze_patch_boundary(args.patch_file, args.repo_path, args.branch)))


if __name__ == "__main__":
    raise SystemExit(main())
