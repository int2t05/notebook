"""Execute bounded automatic repairs for a single applied patch."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from typing import List, Sequence

from validate_applied_patch import FileDiff, Hunk, parse_patch_text


def _normalize(line: str) -> str:
    return " ".join(line.strip().split())


def _find_subsequence(lines: Sequence[str], pattern: Sequence[str]) -> int | None:
    if not pattern:
        return 0
    normalized_pattern = [_normalize(line) for line in pattern]
    limit = len(lines) - len(pattern) + 1
    for index in range(max(limit, 0)):
        candidate = [_normalize(line) for line in lines[index:index + len(pattern)]]
        if candidate == normalized_pattern:
            return index
    return None


def _target_lines(hunk: Hunk) -> List[str]:
    return [content for line_type, content in hunk.lines if line_type in {" ", "+"}]


def _source_lines(hunk: Hunk) -> List[str]:
    return [content for line_type, content in hunk.lines if line_type in {" ", "-"}]


def _read_worktree_lines(repo_path: str, rel_path: str) -> List[str] | None:
    full_path = os.path.join(repo_path, rel_path)
    if not os.path.isfile(full_path):
        return None
    with open(full_path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read().splitlines()


def _write_worktree_lines(repo_path: str, rel_path: str, lines: Sequence[str]) -> None:
    full_path = os.path.join(repo_path, rel_path)
    parent = os.path.dirname(full_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    text = "\n".join(lines)
    if lines:
        text += "\n"
    with open(full_path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _apply_hunk_sequence(lines: List[str], hunk: Hunk) -> tuple[List[str], bool]:
    target = _target_lines(hunk)
    if target and _find_subsequence(lines, target) is not None:
        return lines, False

    source = _source_lines(hunk)
    source_idx = _find_subsequence(lines, source)
    if source_idx is not None:
        updated = list(lines[:source_idx]) + target + list(lines[source_idx + len(source):])
        return updated, updated != lines

    # Pure-addition hunks can still be inserted using the target position as a hint.
    if not source:
        insert_at = max(hunk.target_start - 1, 0)
        insert_at = min(insert_at, len(lines))
        updated = list(lines[:insert_at]) + target + list(lines[insert_at:])
        return updated, updated != lines

    return lines, False


def _apply_file_diff(repo_path: str, file_diff: FileDiff) -> tuple[bool, str]:
    rel_path = file_diff.path
    lines = _read_worktree_lines(repo_path, rel_path)
    if lines is None:
        return False, f"target file missing in worktree: {rel_path}"

    changed = False
    for hunk in file_diff.hunks:
        lines, hunk_changed = _apply_hunk_sequence(lines, hunk)
        changed = changed or hunk_changed

    if changed:
        _write_worktree_lines(repo_path, rel_path, lines)
    return changed, ""


def _run_git(args: List[str], repo_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=repo_path, text=True, capture_output=True)


def _artifact_path(patches_dir: str, commit_id: str, iteration: int) -> str:
    artifacts_dir = os.path.join(patches_dir, ".kernel_patch_artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    safe_commit = commit_id.replace("/", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(artifacts_dir, f"{safe_commit}.iter{iteration}.{ts}.repair.json")


def apply_repair_plan(
    *,
    repo_path: str,
    patch_file: str,
    patches_dir: str,
    commit_id: str,
    iteration: int,
    target_files: Sequence[str],
) -> dict:
    with open(patch_file, "r", encoding="utf-8", errors="ignore") as handle:
        patch_map = parse_patch_text(handle.read())

    attempted_files: List[str] = []
    changed_files: List[str] = []
    errors: List[str] = []
    for target_file in target_files:
        file_diff = patch_map.get(target_file)
        if file_diff is None:
            errors.append(f"patch file does not contain diff for {target_file}")
            continue
        attempted_files.append(target_file)
        changed, error = _apply_file_diff(repo_path, file_diff)
        if error:
            errors.append(error)
            continue
        if changed:
            changed_files.append(target_file)

    payload = {
        "success": False,
        "strategy": "reapply-patch-hunks",
        "commit_id": commit_id,
        "iteration": iteration,
        "patch_file": patch_file,
        "attempted_files": attempted_files,
        "changed_files": changed_files,
        "errors": errors,
        "amended_commit": None,
    }

    if errors or not changed_files:
        payload["reason"] = "repair-noop" if not errors else "repair-apply-failed"
    else:
        add_result = _run_git(["add", "--"] + changed_files, repo_path)
        if add_result.returncode != 0:
            payload["reason"] = "git-add-failed"
            payload["errors"].append(add_result.stderr.strip() or add_result.stdout.strip())
        else:
            amend_result = _run_git(["commit", "--amend", "--no-edit"], repo_path)
            if amend_result.returncode != 0:
                payload["reason"] = "git-amend-failed"
                payload["errors"].append(amend_result.stderr.strip() or amend_result.stdout.strip())
            else:
                head_result = _run_git(["rev-parse", "HEAD"], repo_path)
                payload["success"] = True
                payload["reason"] = "repair-applied"
                payload["amended_commit"] = head_result.stdout.strip() if head_result.returncode == 0 else None

    artifact = _artifact_path(patches_dir, commit_id=commit_id, iteration=iteration)
    with open(artifact, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    payload["artifact_path"] = artifact
    return payload
