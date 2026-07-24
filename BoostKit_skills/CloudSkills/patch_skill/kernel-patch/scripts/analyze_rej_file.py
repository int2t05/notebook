#!/usr/bin/env python3
"""
Analyze .rej conflict files.
"""

import argparse
import json
import logging
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from shared.cli import emit_json
from shared.config import LOG_FORMAT, LOG_LEVEL, is_config_mapping_source_path
from shared.paths import resolve_user_path

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# Limit compact output to three non-empty lines so the summary stays easy to scan.
PREVIEW_LINE_LIMIT = 3
# Cap each preview line to avoid oversized JSON payloads in conflict analysis output.
PREVIEW_CHAR_LIMIT = 120


def _preview_lines(lines: List[str]) -> List[str]:
    preview: List[str] = []
    for line in lines:
        if not line.strip():
            continue
        preview.append(line[:PREVIEW_CHAR_LIMIT])
        if len(preview) >= PREVIEW_LINE_LIMIT:
            break
    return preview


def _build_statistics(hunks: List[Dict[str, object]]) -> Dict[str, int]:
    return {
        "hunk_count": len(hunks),
        "total_added_lines": sum(len(h["added_lines"]) for h in hunks),
        "total_removed_lines": sum(len(h["removed_lines"]) for h in hunks),
        "total_context_lines": sum(len(h["context_lines"]) for h in hunks),
    }


def _build_hunk_summaries(hunks: List[Dict[str, object]]) -> List[Dict[str, object]]:
    summaries: List[Dict[str, object]] = []
    for index, hunk in enumerate(hunks):
        added_lines = list(hunk["added_lines"])
        removed_lines = list(hunk["removed_lines"])
        context_lines = list(hunk["context_lines"])
        summaries.append({
            "hunk_index": index,
            "old_start": hunk["old_start"],
            "old_count": hunk["old_count"],
            "new_start": hunk["new_start"],
            "new_count": hunk["new_count"],
            "added_line_count": len(added_lines),
            "removed_line_count": len(removed_lines),
            "context_line_count": len(context_lines),
            "added_preview": _preview_lines(added_lines),
            "removed_preview": _preview_lines(removed_lines),
            "context_preview": _preview_lines(context_lines),
        })
    return summaries


def _suggested_next_step(conflict_class: str) -> str:
    if conflict_class == "config-sync":
        return "只同步到映射后的 config_files，不要修改原 defconfig 路径。"
    return "只按当前 hunk 在目标文件局部对齐，不要扩展到别的文件。"


def _json_error(message: str) -> str:
    return json.dumps({"success": False, "error": message}, ensure_ascii=False, indent=2)


def _build_hunk(hunk_match: re.Match[str]) -> Dict[str, object]:
    return {
        "old_start": int(hunk_match.group(1)),
        "old_count": int(hunk_match.group(2) or "1"),
        "new_start": int(hunk_match.group(3)),
        "new_count": int(hunk_match.group(4) or "1"),
        "context_lines": [],
        "removed_lines": [],
        "added_lines": [],
    }


def _append_hunk_line(current_hunk: Optional[Dict[str, object]], line: str) -> None:
    if current_hunk is None:
        return
    if line.startswith(" "):
        current_hunk["context_lines"].append(line[1:])
    elif line.startswith("-"):
        current_hunk["removed_lines"].append(line[1:])
    elif line.startswith("+"):
        current_hunk["added_lines"].append(line[1:])


def _parse_rej_content(content: str) -> Tuple[Optional[str], List[Dict[str, object]]]:
    target_file: Optional[str] = None
    hunks: List[Dict[str, object]] = []
    current_hunk: Optional[Dict[str, object]] = None

    for line in content.splitlines():
        if line.startswith("diff --git ") or line.startswith("--- "):
            continue
        if line.startswith("+++ "):
            target_file = line[6:] if line.startswith("+++ b/") else line[4:]
            continue

        hunk_match = HUNK_RE.match(line)
        if hunk_match:
            if current_hunk:
                hunks.append(current_hunk)
            current_hunk = _build_hunk(hunk_match)
            continue

        _append_hunk_line(current_hunk, line)

    if current_hunk:
        hunks.append(current_hunk)

    return target_file, hunks


def _detect_patch_type(hunks: List[Dict[str, object]]) -> str:
    has_added = any(hunk["added_lines"] for hunk in hunks)
    has_removed = any(hunk["removed_lines"] for hunk in hunks)
    if has_added and not has_removed:
        return "append_only"
    if has_added and has_removed:
        return "modify"
    if has_removed and not has_added:
        return "remove_only"
    return "unknown"


def _build_payload(
    rej_abs_path: str,
    repo_abs_path: str,
    target_file: str,
    hunks: List[Dict[str, object]],
    output_level: str,
) -> Dict[str, object]:
    is_mapping_source = is_config_mapping_source_path(target_file)
    conflict_class = "config-sync" if is_mapping_source else "manual-edit-risk"
    payload: Dict[str, object] = {
        "success": True,
        "repo_path": repo_abs_path,
        "rej_file": os.path.basename(rej_abs_path),
        "rej_abs_path": rej_abs_path,
        "target_file": target_file,
        "is_config_file": is_mapping_source,
        "conflict_class": conflict_class,
        "patch_type": _detect_patch_type(hunks),
        "statistics": _build_statistics(hunks),
        "suggested_next_step": _suggested_next_step(conflict_class),
    }
    if output_level == "full":
        payload["hunks"] = hunks
    else:
        payload["hunk_summaries"] = _build_hunk_summaries(hunks)
    return payload


def analyze_rej_file(rej_file_path: str, repo_path: str, output_level: str = "compact") -> str:
    try:
        if output_level not in {"compact", "full"}:
            return _json_error(f"invalid output_level: {output_level}")

        rej_abs_path = resolve_user_path(rej_file_path)
        repo_abs_path = resolve_user_path(repo_path)
        if not os.path.isfile(rej_abs_path):
            return _json_error(f".rej 文件不存在: {rej_file_path}")

        with open(rej_abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            rej_content = handle.read()

        target_file, hunks = _parse_rej_content(rej_content)
        resolved_target_file = target_file or os.path.basename(rej_abs_path).replace(".rej", "")
        payload = _build_payload(
            rej_abs_path, repo_abs_path, resolved_target_file, hunks, output_level
        )
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("分析 .rej 文件失败: %s", exc)
        return _json_error(str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a .rej conflict file.")
    parser.add_argument("--rej-file-path", required=True, help="Path to the .rej file.")
    parser.add_argument("--repo-path", required=True, help="Target repository path.")
    parser.add_argument("--output-level", choices=["compact", "full"], default="compact", help="Output detail level.")
    args = parser.parse_args()
    return emit_json(json.loads(analyze_rej_file(args.rej_file_path, args.repo_path, output_level=args.output_level)))


if __name__ == "__main__":
    raise SystemExit(main())
