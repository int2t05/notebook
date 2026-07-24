#!/usr/bin/env python3
"""
Patch Validator - Validate patch applicability or compare local patches with merged commits.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path
from typing import Optional, Union


try:
    from unidiff import PatchSet
    HAS_UNIDIFF = True
except ImportError:
    HAS_UNIDIFF = False

SUBJECT_FUZZY_MIN_SIMILARITY = 0.9
SUBJECT_FUZZY_MIN_TOKEN_COVERAGE = 0.6
SUBJECT_STOPWORDS = {
    "a",
    "add",
    "and",
    "arm64",
    "change",
    "check",
    "fix",
    "for",
    "if",
    "in",
    "implement",
    "introduce",
    "kvm",
    "of",
    "on",
    "support",
    "the",
    "to",
    "use",
    "using",
}


class ValidationMode(Enum):
    APPLICABILITY = "applicability"
    MERGED_DIFF = "merged-diff"


class HunkStatus(Enum):
    CLEAN = "CLEAN"
    VARIATION = "VARIATION"
    FAILED = "FAILED"


class DiffStatus(Enum):
    IDENTICAL = "IDENTICAL"
    DIFFERENT = "DIFFERENT"
    UNMATCHED = "UNMATCHED"
    AMBIGUOUS = "AMBIGUOUS"


class LocalPatchMatchStatus(Enum):
    MATCHED = "MATCHED"
    UNMATCHED_LOCAL_PATCH = "UNMATCHED_LOCAL_PATCH"
    AMBIGUOUS_LOCAL_PATCH = "AMBIGUOUS_LOCAL_PATCH"
    UNMATCHED_TARGET_COMMIT = "UNMATCHED_TARGET_COMMIT"


class TargetCommitMatchStatus(Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass
class HunkResult:
    hunk_number: int
    original_start_line: int
    original_line_count: int
    actual_start_line: Optional[int]
    status: str
    similarity: float
    message: str
    context_preview: str = ""


@dataclass
class FileResult:
    source_file: str
    target_file: str
    hunks: list = field(default_factory=list)
    status: str = HunkStatus.CLEAN.value
    message: str = ""


@dataclass
class PatchResult:
    patch_file: str
    commit_subject: str
    commit_hash: str
    commit_date: str
    commit_author: str
    files: list = field(default_factory=list)
    overall_status: str = HunkStatus.CLEAN.value
    total_hunks: int = 0
    clean_hunks: int = 0
    variation_hunks: int = 0
    failed_hunks: int = 0
    message: str = ""
    matched_commit: str = ""
    matched_by: str = ""
    local_patch_id: str = ""
    merged_patch_id: str = ""
    diff_status: str = ""
    file_differences: list = field(default_factory=list)
    target_commit: str = ""
    target_subject: str = ""
    local_patch_path: str = ""
    local_patch_match_status: str = ""
    local_patch_match_method: str = ""
    local_patch_candidates: list = field(default_factory=list)
    target_match_status: str = ""
    target_match_method: str = ""
    target_commit_candidates: list = field(default_factory=list)
    unmatched_reason: str = ""


@dataclass
class ValidationResult:
    repository: str
    branch: str
    mode: str
    match_strategy: str
    search_scope: str = ""
    upstream_branch: str = ""
    merge_base: str = ""
    target_commit_count: int = 0
    patches: list = field(default_factory=list)
    total_patches: int = 0
    total_hunks: int = 0
    clean_hunks: int = 0
    variation_hunks: int = 0
    failed_hunks: int = 0
    identical_patches: int = 0
    different_patches: int = 0
    unmatched_patches: int = 0
    ambiguous_patches: int = 0
    local_patches_total: int = 0
    matched_target_commits: int = 0
    unmatched_target_commits: int = 0
    ambiguous_target_commits: int = 0


@dataclass
class LocalPatchIndexEntry:
    filename: str
    full_path: str
    normalized_filename_stem: str
    filename_hash: str
    filename_subject: str
    commit_hash: str
    commit_subject: str
    commit_date: str
    commit_author: str
    subject_norm: str
    filename_subject_norm: str
    patch_id: str
    patch_text: str


@dataclass
class TargetCommit:
    commit: str
    subject: str


@dataclass
class TargetCommitIndex:
    commits: list
    subject_map: dict
    patch_id_cache: dict
    search_scope: str = ""
    upstream_branch: str = ""
    merge_base: str = ""


def run_git_command(
    args: list,
    cwd: str,
    check: bool = False,
    stdin_text: Optional[str] = None,
    stdin_bytes: Optional[bytes] = None,
    text: bool = True,
    errors: str = "strict",
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            errors=errors if text else None,
            input=stdin_text if text else stdin_bytes,
            check=False,
        )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, result.args, result.stdout, result.stderr
            )
        return result
    except FileNotFoundError as exc:
        raise RuntimeError("git command not found. Please ensure git is installed.") from exc


def parse_patch_metadata(patch_content: str) -> dict:
    metadata = {
        "commit_hash": "",
        "commit_subject": "",
        "commit_date": "",
        "commit_author": "",
    }

    current_header = ""
    for line in patch_content.split("\n"):
        if line == "":
            break
        if line.startswith((" ", "\t")) and current_header:
            if current_header == "commit_subject":
                metadata[current_header] = f"{metadata[current_header]} {line.strip()}".strip()
            continue
        current_header = ""
        if line.startswith("From "):
            parts = line.split()
            if len(parts) >= 2:
                metadata["commit_hash"] = parts[1][:12]
        elif line.startswith("From:"):
            metadata["commit_author"] = line[5:].strip()
            current_header = "commit_author"
        elif line.startswith("Date:"):
            metadata["commit_date"] = line[5:].strip()
            current_header = "commit_date"
        elif line.startswith("Subject:"):
            subject = line[8:].strip()
            metadata["commit_subject"] = subject
            current_header = "commit_subject"

    metadata["commit_subject"] = re.sub(r"^\[PATCH[^\]]*\]\s*", "", metadata["commit_subject"]).strip()
    return metadata


def parse_patch_with_unidiff_content(patch_text: str) -> list:
    from io import StringIO

    patch_set = PatchSet(StringIO(patch_text))
    files = []
    for patched_file in patch_set:
        file_info = {
            "source_file": patched_file.source_file,
            "target_file": patched_file.target_file,
            "is_binary": bool(getattr(patched_file, "is_binary_file", False)),
            "hunks": [],
        }
        for index, hunk in enumerate(patched_file, 1):
            hunk_info = {
                "hunk_number": index,
                "source_start": hunk.source_start,
                "source_length": hunk.source_length,
                "target_start": hunk.target_start,
                "target_length": hunk.target_length,
                "section_header": hunk.section_header,
                "lines": [],
            }
            for line in hunk:
                hunk_info["lines"].append(
                    {
                        "line_type": line.line_type,
                        "content": line.value.rstrip("\n"),
                        "source_line_no": line.source_line_no,
                        "target_line_no": line.target_line_no,
                    }
                )
            file_info["hunks"].append(hunk_info)
        files.append(file_info)
    return files


def parse_patch_manually(patch_content: str) -> list:
    files = []
    current_file = None
    current_hunk = None
    hunk_number = 0

    for line in patch_content.split("\n"):
        if line.startswith("diff --git"):
            if current_file:
                if current_hunk:
                    current_file["hunks"].append(current_hunk)
                files.append(current_file)
            match = re.match(r"diff --git a/(.*) b/(.*)", line)
            if match:
                current_file = {
                    "source_file": f"a/{match.group(1)}",
                    "target_file": f"b/{match.group(2)}",
                    "is_binary": False,
                    "hunks": [],
                }
                current_hunk = None
                hunk_number = 0
            continue

        if current_file and (line == "GIT binary patch" or line.startswith("Binary files ")):
            current_file["is_binary"] = True
            current_hunk = None
            continue

        if line.startswith("@@"):
            if current_hunk and current_file:
                current_file["hunks"].append(current_hunk)
            hunk_number += 1
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", line)
            if match and current_file:
                current_hunk = {
                    "hunk_number": hunk_number,
                    "source_start": int(match.group(1)),
                    "source_length": int(match.group(2)) if match.group(2) else 1,
                    "target_start": int(match.group(3)),
                    "target_length": int(match.group(4)) if match.group(4) else 1,
                    "section_header": match.group(5).strip(),
                    "lines": [],
                }
            continue

        if current_hunk is not None and current_file:
            if line.startswith((" ", "-", "+")):
                current_hunk["lines"].append(
                    {
                        "line_type": line[0],
                        "content": line[1:],
                        "source_line_no": None,
                        "target_line_no": None,
                    }
                )
            elif line == "-- ":
                break

    if current_file:
        if current_hunk:
            current_file["hunks"].append(current_hunk)
        files.append(current_file)
    return files


def parse_patch_text(patch_text: str) -> list:
    if HAS_UNIDIFF:
        try:
            return parse_patch_with_unidiff_content(patch_text)
        except Exception:
            return parse_patch_manually(patch_text)
    return parse_patch_manually(patch_text)


def load_patch_text(patch_path: str) -> str:
    with open(patch_path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def extract_diff_body(patch_text: str) -> str:
    lines = patch_text.splitlines()
    start_idx = None
    end_idx = len(lines)
    for index, line in enumerate(lines):
        if line.startswith("diff --git "):
            start_idx = index
            break
    if start_idx is None:
        return ""
    for index in range(start_idx, len(lines)):
        if lines[index] == "-- ":
            end_idx = index
            break
    body = "\n".join(lines[start_idx:end_idx]).strip("\n")
    if body:
        body += "\n"
    return body


def normalize_text_for_match(text: str) -> str:
    text = text or ""
    text = re.sub(r"^\[PATCH[^\]]*\]\s*", "", text)
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def normalize_subject(subject: str) -> str:
    return normalize_text_for_match(subject)


def tokenize_subject(subject_norm: str) -> set:
    return {
        token for token in subject_norm.split()
        if token and token not in SUBJECT_STOPWORDS and len(token) > 1
    }


def is_strict_subject_match(local_subject_norm: str, target_subject_norm: str) -> bool:
    return is_truncated_or_exact_match(local_subject_norm, target_subject_norm)


def has_sufficient_token_overlap(local_tokens: set, target_tokens: set) -> bool:
    if not local_tokens or not target_tokens:
        return False
    overlap = len(local_tokens & target_tokens)
    coverage = overlap / max(len(local_tokens), len(target_tokens))
    return coverage >= SUBJECT_FUZZY_MIN_TOKEN_COVERAGE


def is_fuzzy_subject_match(local_subject_norm: str, target_subject_norm: str) -> bool:
    if not local_subject_norm or not target_subject_norm:
        return False
    similarity = SequenceMatcher(None, local_subject_norm, target_subject_norm).ratio()
    if similarity < SUBJECT_FUZZY_MIN_SIMILARITY:
        return False
    return has_sufficient_token_overlap(
        tokenize_subject(local_subject_norm),
        tokenize_subject(target_subject_norm),
    )


def normalize_line_for_compare(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def clean_file_path(path: str) -> str:
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def split_filename_metadata(filename: str) -> tuple[str, str]:
    stem = Path(filename).stem
    match = re.match(r"^([0-9a-fA-F]{7,40})[_-](.*)$", stem)
    if match:
        return match.group(1).lower(), match.group(2)
    return "", stem


def is_truncated_or_exact_match(left: str, right: str) -> bool:
    return bool(left and right and (left == right or left.startswith(right) or right.startswith(left)))


def read_file_lines(repo_path: str, file_path: str, branch: str) -> Optional[list]:
    clean_path = clean_file_path(file_path)
    full_path = os.path.join(repo_path, clean_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as handle:
                return [line.rstrip() for line in handle.read().splitlines()]
        except Exception:
            pass

    result = run_git_command(["show", f"{branch}:{clean_path}"], repo_path)
    if result.returncode == 0:
        return [line.rstrip() for line in result.stdout.splitlines()]
    return None


def extract_context_lines(hunk_info: dict) -> list:
    context_lines = []
    for line in hunk_info["lines"]:
        if line["line_type"] in (" ", "-"):
            context_lines.append(line["content"].rstrip())
    return context_lines


def calculate_similarity(context_lines: list, file_lines: list, start_pos: int) -> float:
    if start_pos < 0 or start_pos + len(context_lines) > len(file_lines):
        return 0.0
    file_slice = file_lines[start_pos:start_pos + len(context_lines)]
    if not context_lines or not file_slice:
        return 0.0
    return SequenceMatcher(None, "\n".join(context_lines), "\n".join(file_slice)).ratio()


def find_best_match(context_lines: list, file_lines: list, expected_start: int, tolerance: int = 3, threshold: float = 0.9) -> tuple:
    if not file_lines:
        return (HunkStatus.FAILED, None, 0.0)

    expected_idx = expected_start - 1 if expected_start > 0 else 0
    exact_similarity = calculate_similarity(context_lines, file_lines, expected_idx)
    if exact_similarity == 1.0:
        return (HunkStatus.CLEAN, expected_start, 1.0)

    best_similarity = 0.0
    best_position = None
    for offset in range(-tolerance, tolerance + 1):
        pos = expected_idx + offset
        if pos < 0:
            continue
        similarity = calculate_similarity(context_lines, file_lines, pos)
        if similarity > best_similarity:
            best_similarity = similarity
            best_position = pos + 1

    if best_similarity >= threshold:
        return (HunkStatus.VARIATION, best_position, best_similarity)
    return (HunkStatus.FAILED, best_position, best_similarity)


def validate_hunk(hunk_info: dict, repo_path: str, branch: str, tolerance: int = 3, threshold: float = 0.9) -> HunkResult:
    target_file = hunk_info.get("target_file", hunk_info.get("source_file", ""))
    expected_start = hunk_info["source_start"]
    file_lines = read_file_lines(repo_path, target_file, branch)

    if file_lines is None:
        return HunkResult(
            hunk_number=hunk_info["hunk_number"],
            original_start_line=expected_start,
            original_line_count=hunk_info["source_length"],
            actual_start_line=None,
            status=HunkStatus.FAILED.value,
            similarity=0.0,
            message=f"Target file not found: {target_file}",
        )

    context_lines = extract_context_lines(hunk_info)
    if not context_lines:
        if expected_start <= len(file_lines) + 1:
            return HunkResult(
                hunk_number=hunk_info["hunk_number"],
                original_start_line=expected_start,
                original_line_count=hunk_info["source_length"],
                actual_start_line=expected_start,
                status=HunkStatus.CLEAN.value,
                similarity=1.0,
                message="Pure addition hunk (no context)",
            )
        return HunkResult(
            hunk_number=hunk_info["hunk_number"],
            original_start_line=expected_start,
            original_line_count=hunk_info["source_length"],
            actual_start_line=None,
            status=HunkStatus.FAILED.value,
            similarity=0.0,
            message=f"Invalid position for addition: line {expected_start} exceeds file length {len(file_lines)}",
        )

    context_preview = "\n".join(context_lines[:5])
    if len(context_lines) > 5:
        context_preview += f"\n... ({len(context_lines) - 5} more lines)"

    status, actual_pos, similarity = find_best_match(context_lines, file_lines, expected_start, tolerance, threshold)
    if status == HunkStatus.CLEAN:
        message = "Exact match found"
    elif status == HunkStatus.VARIATION:
        offset = actual_pos - expected_start if actual_pos else 0
        message = f"Context offset by {offset} line(s), similarity: {similarity:.2%}"
    else:
        message = f"No suitable match found (best similarity: {similarity:.2%})"

    return HunkResult(
        hunk_number=hunk_info["hunk_number"],
        original_start_line=expected_start,
        original_line_count=hunk_info["source_length"],
        actual_start_line=actual_pos,
        status=status.value,
        similarity=round(similarity, 4),
        message=message,
        context_preview=context_preview,
    )


def validate_file(file_info: dict, repo_path: str, branch: str, tolerance: int, threshold: float) -> FileResult:
    result = FileResult(source_file=file_info["source_file"], target_file=file_info["target_file"])
    hunks = file_info.get("hunks", [])
    if not hunks:
        result.message = "No hunks found in patch"
        return result

    for hunk_info in hunks:
        hunk_with_file = dict(hunk_info)
        hunk_with_file["target_file"] = file_info["target_file"]
        hunk_with_file["source_file"] = file_info["source_file"]
        result.hunks.append(asdict(validate_hunk(hunk_with_file, repo_path, branch, tolerance, threshold)))

    has_failed = any(hunk["status"] == HunkStatus.FAILED.value for hunk in result.hunks)
    has_variation = any(hunk["status"] == HunkStatus.VARIATION.value for hunk in result.hunks)
    if has_failed:
        result.status = HunkStatus.FAILED.value
    elif has_variation:
        result.status = HunkStatus.VARIATION.value
    return result


def try_git_apply_check(patch_path: str, repo_path: str) -> tuple:
    result = run_git_command(["apply", "--check", "--verbose", patch_path], repo_path)
    if result.returncode == 0:
        return (True, "")
    return (False, result.stderr.strip() or result.stdout.strip())


def get_commit_diff_bytes(repo_path: str, commit: str) -> bytes:
    result = run_git_command(
        ["show", "--format=", "--unified=3", commit],
        repo_path,
        check=True,
        text=False,
    )
    return result.stdout


def get_commit_diff(repo_path: str, commit: str) -> str:
    result = run_git_command(
        ["show", "--format=", "--unified=3", commit],
        repo_path,
        check=True,
        errors="replace",
    )
    return result.stdout


def compute_patch_id(repo_path: str, diff_input: Union[str, bytes]) -> str:
    if isinstance(diff_input, str):
        if not diff_input.strip():
            return ""
        stdin_bytes = diff_input.encode("utf-8", errors="replace")
    else:
        if not diff_input.strip():
            return ""
        stdin_bytes = diff_input
    result = run_git_command(
        ["patch-id", "--stable"],
        repo_path,
        stdin_bytes=stdin_bytes,
        text=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return ""
    return result.stdout.decode("utf-8", errors="replace").split()[0]


def list_branch_commits(repo_path: str, branch: str) -> list:
    result = run_git_command(["log", "--no-merges", "--format=%H%x00%s", branch], repo_path, check=True)
    commits = []
    for line in result.stdout.splitlines():
        if "\x00" not in line:
            continue
        commit, subject = line.split("\x00", 1)
        commits.append(TargetCommit(commit=commit, subject=subject))
    return commits


def ref_exists(repo_path: str, ref: str) -> bool:
    result = run_git_command(["rev-parse", "--verify", "--quiet", ref], repo_path)
    return result.returncode == 0


def detect_upstream_branch(repo_path: str, branch: str) -> str:
    result = run_git_command(
        ["for-each-ref", f"refs/heads/{branch}", "--format=%(upstream:short)"],
        repo_path,
        check=True,
    )
    return result.stdout.strip()


def resolve_merge_base(repo_path: str, upstream_branch: str, branch: str) -> str:
    result = run_git_command(["merge-base", upstream_branch, branch], repo_path)
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(
            f"cannot determine merge-base between {upstream_branch} and {branch}; "
            "provide a correct --upstream-branch or retry with --global-search"
        )
    return result.stdout.strip()


def list_branch_commits_in_range(repo_path: str, branch: str, upstream_branch: str) -> tuple[list, str]:
    if not ref_exists(repo_path, upstream_branch):
        raise ValueError(
            f"upstream branch does not exist: {upstream_branch}; "
            "provide a correct --upstream-branch or retry with --global-search"
        )
    merge_base = resolve_merge_base(repo_path, upstream_branch, branch)
    commit_range = f"{merge_base}..{branch}"
    result = run_git_command(["log", "--no-merges", "--format=%H%x00%s", commit_range], repo_path, check=True)
    commits = []
    for line in result.stdout.splitlines():
        if "\x00" not in line:
            continue
        commit, subject = line.split("\x00", 1)
        commits.append(TargetCommit(commit=commit, subject=subject))
    return commits, merge_base


def build_target_commit_index(
    repo_path: str,
    branch: str,
    explicit_commit: str = "",
    upstream_branch: str = "",
    global_search: bool = False,
) -> TargetCommitIndex:
    search_scope = "global"
    resolved_upstream = ""
    merge_base = ""
    if explicit_commit:
        subject = run_git_command(["show", "--no-patch", "--format=%s", explicit_commit], repo_path, check=True).stdout.strip()
        commits = [TargetCommit(commit=explicit_commit, subject=subject)]
        search_scope = "explicit"
    else:
        if global_search:
            commits = list_branch_commits(repo_path, branch)
        else:
            resolved_upstream = upstream_branch or detect_upstream_branch(repo_path, branch)
            if not resolved_upstream:
                raise ValueError(
                    f"cannot auto-detect upstream for branch {branch}; "
                    "provide --upstream-branch or retry with --global-search"
                )
            commits, merge_base = list_branch_commits_in_range(repo_path, branch, resolved_upstream)
            search_scope = "scoped"

    subject_map = {}
    for commit in commits:
        subject_map.setdefault(normalize_subject(commit.subject), []).append(commit)

    return TargetCommitIndex(
        commits=commits,
        subject_map=subject_map,
        patch_id_cache={},
        search_scope=search_scope,
        upstream_branch=resolved_upstream,
        merge_base=merge_base,
    )


def build_local_patch_index(patch_dir: str, repo_path: str) -> list:
    entries = []
    for patch_path in sorted(Path(patch_dir).glob("*.patch")):
        patch_text = load_patch_text(str(patch_path))
        metadata = parse_patch_metadata(patch_text)
        filename_hash, filename_subject = split_filename_metadata(patch_path.name)
        entries.append(
            LocalPatchIndexEntry(
                filename=patch_path.name,
                full_path=str(patch_path),
                normalized_filename_stem=normalize_text_for_match(patch_path.stem),
                filename_hash=filename_hash,
                filename_subject=filename_subject,
                commit_hash=metadata["commit_hash"].lower(),
                commit_subject=metadata["commit_subject"] or patch_path.name,
                commit_date=metadata["commit_date"],
                commit_author=metadata["commit_author"],
                subject_norm=normalize_subject(metadata["commit_subject"] or patch_path.name),
                filename_subject_norm=normalize_text_for_match(filename_subject),
                patch_id=compute_patch_id(repo_path, extract_diff_body(patch_text)),
                patch_text=patch_text,
            )
        )
    return entries


def get_target_patch_id(repo_path: str, target_commit: TargetCommit, target_index: TargetCommitIndex) -> str:
    if target_commit.commit not in target_index.patch_id_cache:
        target_index.patch_id_cache[target_commit.commit] = compute_patch_id(repo_path, get_commit_diff_bytes(repo_path, target_commit.commit))
    return target_index.patch_id_cache[target_commit.commit]


def get_target_subject_candidates(local_entry: LocalPatchIndexEntry, target_index: TargetCommitIndex) -> list:
    candidates = []
    for subject_norm, commits in target_index.subject_map.items():
        if is_strict_subject_match(local_entry.subject_norm, subject_norm):
            candidates.extend(commits)
    if not candidates:
        for subject_norm, commits in target_index.subject_map.items():
            if is_strict_subject_match(local_entry.filename_subject_norm, subject_norm):
                candidates.extend(commits)
    # Keep stable order and deduplicate by commit hash.
    unique = {}
    for commit in candidates:
        unique[commit.commit] = commit
    return list(unique.values())


def get_target_fuzzy_subject_candidates(local_entry: LocalPatchIndexEntry, target_index: TargetCommitIndex) -> list:
    candidates = []
    preferred_subjects = [local_entry.subject_norm]
    if local_entry.filename_subject_norm and local_entry.filename_subject_norm != local_entry.subject_norm:
        preferred_subjects.append(local_entry.filename_subject_norm)

    for local_subject_norm in preferred_subjects:
        for target_subject_norm, commits in target_index.subject_map.items():
            if is_fuzzy_subject_match(local_subject_norm, target_subject_norm):
                candidates.extend(commits)

    unique = {}
    for commit in candidates:
        unique[commit.commit] = commit
    return list(unique.values())


def get_target_diff_candidates(repo_path: str, local_entry: LocalPatchIndexEntry, target_index: TargetCommitIndex) -> tuple[list, str]:
    if not local_entry.patch_id:
        return [], ""
    candidates = []
    for target_commit in target_index.commits:
        if get_target_patch_id(repo_path, target_commit, target_index) == local_entry.patch_id:
            candidates.append(target_commit)
    return candidates, local_entry.patch_id


def map_local_patch_to_target_commit(repo_path: str, local_entry: LocalPatchIndexEntry, target_index: TargetCommitIndex) -> dict:
    subject_candidates = get_target_subject_candidates(local_entry, target_index)
    if len(subject_candidates) == 1:
        return {
            "status": TargetCommitMatchStatus.MATCHED.value,
            "target_commit": subject_candidates[0],
            "method": "subject-strict",
            "candidates": [candidate.commit for candidate in subject_candidates],
            "merged_patch_id": "",
            "unmatched_reason": "",
        }
    if len(subject_candidates) > 1:
        return {
            "status": TargetCommitMatchStatus.AMBIGUOUS.value,
            "target_commit": None,
            "method": "subject-strict",
            "candidates": [candidate.commit for candidate in subject_candidates],
            "merged_patch_id": "",
            "unmatched_reason": "",
        }

    fuzzy_candidates = get_target_fuzzy_subject_candidates(local_entry, target_index)
    if len(fuzzy_candidates) == 1:
        return {
            "status": TargetCommitMatchStatus.MATCHED.value,
            "target_commit": fuzzy_candidates[0],
            "method": "subject-fuzzy",
            "candidates": [candidate.commit for candidate in fuzzy_candidates],
            "merged_patch_id": "",
            "unmatched_reason": "",
        }
    if len(fuzzy_candidates) > 1:
        return {
            "status": TargetCommitMatchStatus.AMBIGUOUS.value,
            "target_commit": None,
            "method": "subject-fuzzy",
            "candidates": [candidate.commit for candidate in fuzzy_candidates],
            "merged_patch_id": "",
            "unmatched_reason": "",
        }

    diff_candidates, merged_patch_id = get_target_diff_candidates(repo_path, local_entry, target_index)
    if len(diff_candidates) == 1:
        return {
            "status": TargetCommitMatchStatus.MATCHED.value,
            "target_commit": diff_candidates[0],
            "method": "diff",
            "candidates": [candidate.commit for candidate in diff_candidates],
            "merged_patch_id": merged_patch_id,
            "unmatched_reason": "",
        }
    if len(diff_candidates) > 1:
        return {
            "status": TargetCommitMatchStatus.AMBIGUOUS.value,
            "target_commit": None,
            "method": "diff",
            "candidates": [candidate.commit for candidate in diff_candidates],
            "merged_patch_id": merged_patch_id,
            "unmatched_reason": "",
        }

    unmatched_reason = "diff_not_found"
    if local_entry.subject_norm:
        unmatched_reason = "subject_candidates_below_threshold"
    else:
        unmatched_reason = "no_subject_candidate"

    return {
        "status": TargetCommitMatchStatus.UNMATCHED.value,
        "target_commit": None,
        "method": "",
        "candidates": [],
        "merged_patch_id": merged_patch_id,
        "unmatched_reason": unmatched_reason,
    }


def file_key(file_info: dict) -> tuple:
    return (clean_file_path(file_info["source_file"]), clean_file_path(file_info["target_file"]))


def normalize_hunk_lines(hunk: dict) -> list:
    return [f"{line['line_type']}:{normalize_line_for_compare(line['content'])}" for line in hunk.get("lines", [])]


def collect_lines(hunk: dict, line_type: str) -> list:
    return [line["content"].rstrip() for line in hunk.get("lines", []) if line["line_type"] == line_type]


def collect_file_lines(file_info: dict, line_type: str) -> list:
    lines = []
    for hunk in file_info.get("hunks", []):
        lines.extend(collect_lines(hunk, line_type))
    return lines


def multiset_difference_by_normalized(left_raw: list, right_raw: list) -> list:
    right_counter = Counter(normalize_line_for_compare(item) for item in right_raw)
    diff = []
    for item in left_raw:
        normalized = normalize_line_for_compare(item)
        if right_counter.get(normalized, 0) > 0:
            right_counter[normalized] -= 1
        else:
            diff.append(item)
    return diff


def align_hunks(local_hunks: list, merged_hunks: list) -> list:
    aligned = []
    used_merged = set()
    for local_hunk in local_hunks:
        best_idx = None
        best_score = -1.0
        local_signature = "\n".join(normalize_hunk_lines(local_hunk))
        for index, merged_hunk in enumerate(merged_hunks):
            if index in used_merged:
                continue
            merged_signature = "\n".join(normalize_hunk_lines(merged_hunk))
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


def compare_hunk_pair(local_hunk: Optional[dict], merged_hunk: Optional[dict]) -> dict:
    if local_hunk is None:
        return {
            "local_hunk_number": None,
            "merged_hunk_number": merged_hunk["hunk_number"],
            "status": "extra-hunk",
            "message": "Merged commit contains an extra hunk not present in local patch",
            "missing_added_lines": [],
            "extra_added_lines": collect_lines(merged_hunk, "+"),
            "removed_line_mismatches": [],
            "similarity": 0.0,
        }
    if merged_hunk is None:
        return {
            "local_hunk_number": local_hunk["hunk_number"],
            "merged_hunk_number": None,
            "status": "missing-hunk",
            "message": "Local patch hunk not found in merged commit",
            "missing_added_lines": collect_lines(local_hunk, "+"),
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "similarity": 0.0,
        }

    local_added = collect_lines(local_hunk, "+")
    merged_added = collect_lines(merged_hunk, "+")
    local_removed = collect_lines(local_hunk, "-")
    merged_removed = collect_lines(merged_hunk, "-")
    missing_added = multiset_difference_by_normalized(local_added, merged_added)
    extra_added = multiset_difference_by_normalized(merged_added, local_added)
    removed_mismatches = multiset_difference_by_normalized(local_removed, merged_removed) + multiset_difference_by_normalized(merged_removed, local_removed)
    local_signature = "\n".join(normalize_hunk_lines(local_hunk))
    merged_signature = "\n".join(normalize_hunk_lines(merged_hunk))
    similarity = SequenceMatcher(None, local_signature, merged_signature).ratio()

    status = "identical"
    message = "Hunk content matches"
    if missing_added or extra_added or removed_mismatches:
        status = "different"
        message = "Hunk content differs"
    elif local_signature != merged_signature:
        message = "Hunk content matches (layout differs)"

    return {
        "local_hunk_number": local_hunk["hunk_number"],
        "merged_hunk_number": merged_hunk["hunk_number"],
        "status": status,
        "message": message,
        "missing_added_lines": missing_added,
        "extra_added_lines": extra_added,
        "removed_line_mismatches": removed_mismatches,
        "similarity": round(similarity, 4),
    }


def compare_file_diffs(local_file: dict, merged_file: Optional[dict]) -> dict:
    source_file = clean_file_path(local_file["source_file"])
    target_file = clean_file_path(local_file["target_file"])
    if merged_file is None:
        return {
            "source_file": source_file,
            "target_file": target_file,
            "status": "missing-file",
            "message": "Merged commit does not contain this file diff",
            "missing_added_lines": [line for hunk in local_file["hunks"] for line in collect_lines(hunk, "+")],
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "hunk_differences": [],
        }
    if local_file.get("is_binary") or merged_file.get("is_binary"):
        return {
            "source_file": source_file,
            "target_file": target_file,
            "status": "skipped",
            "message": "Binary or non-UTF8 diff skipped from content comparison",
            "missing_added_lines": [],
            "extra_added_lines": [],
            "removed_line_mismatches": [],
            "hunk_differences": [],
        }

    local_added_all = collect_file_lines(local_file, "+")
    merged_added_all = collect_file_lines(merged_file, "+")
    local_removed_all = collect_file_lines(local_file, "-")
    merged_removed_all = collect_file_lines(merged_file, "-")

    all_missing = multiset_difference_by_normalized(local_added_all, merged_added_all)
    all_extra = multiset_difference_by_normalized(merged_added_all, local_added_all)
    all_removed_mismatches = (
        multiset_difference_by_normalized(local_removed_all, merged_removed_all) +
        multiset_difference_by_normalized(merged_removed_all, local_removed_all)
    )

    hunk_differences = []
    for local_hunk, merged_hunk in align_hunks(local_file["hunks"], merged_file["hunks"]):
        hunk_diff = compare_hunk_pair(local_hunk, merged_hunk)
        hunk_differences.append(hunk_diff)

    status = "identical"
    message = "File diff matches"
    if all_missing or all_extra or all_removed_mismatches:
        status = "different"
        message = "File diff differs"
    else:
        normalized_hunks = []
        for hunk_diff in hunk_differences:
            normalized = dict(hunk_diff)
            if normalized["status"] != "identical":
                normalized["status"] = "identical"
                normalized["message"] = "Hunk content is covered by another aligned hunk"
            normalized_hunks.append(normalized)
        hunk_differences = normalized_hunks

    return {
        "source_file": source_file,
        "target_file": target_file,
        "status": status,
        "message": message,
        "missing_added_lines": all_missing,
        "extra_added_lines": all_extra,
        "removed_line_mismatches": all_removed_mismatches,
        "hunk_differences": hunk_differences,
    }


def compare_patch_to_commit(local_patch_text: str, merged_patch_text: str) -> list:
    local_files = parse_patch_text(local_patch_text)
    merged_files = parse_patch_text(merged_patch_text)
    merged_by_key = {file_key(file_info): file_info for file_info in merged_files}
    differences = []
    seen_keys = set()

    for local_file in local_files:
        key = file_key(local_file)
        seen_keys.add(key)
        differences.append(compare_file_diffs(local_file, merged_by_key.get(key)))

    for key, merged_file in merged_by_key.items():
        if key in seen_keys:
            continue
        differences.append(
            {
                "source_file": clean_file_path(merged_file["source_file"]),
                "target_file": clean_file_path(merged_file["target_file"]),
                "status": "extra-file",
                "message": "Merged commit contains an extra file diff not present in local patch",
                "missing_added_lines": [],
                "extra_added_lines": [line for hunk in merged_file["hunks"] for line in collect_lines(hunk, "+")],
                "removed_line_mismatches": [],
                "hunk_differences": [],
            }
        )
    return differences


def validate_patch_applicability(patch_path: str, repo_path: str, branch: str, tolerance: int, threshold: float, use_git_apply: bool = True) -> PatchResult:
    patch_content = load_patch_text(patch_path)
    metadata = parse_patch_metadata(patch_content)
    result = PatchResult(
        patch_file=os.path.basename(patch_path),
        commit_subject=metadata["commit_subject"] or os.path.basename(patch_path),
        commit_hash=metadata["commit_hash"],
        commit_date=metadata["commit_date"],
        commit_author=metadata["commit_author"],
    )

    if use_git_apply:
        success, error_msg = try_git_apply_check(patch_path, repo_path)
        if not success:
            result.message = error_msg

    files = parse_patch_text(patch_content)
    if not files:
        result.message = result.message or "No file changes found in patch"
        return result

    for file_info in files:
        file_result = validate_file(file_info, repo_path, branch, tolerance, threshold)
        result.files.append(asdict(file_result))
        for hunk in file_result.hunks:
            result.total_hunks += 1
            if hunk["status"] == HunkStatus.CLEAN.value:
                result.clean_hunks += 1
            elif hunk["status"] == HunkStatus.VARIATION.value:
                result.variation_hunks += 1
            else:
                result.failed_hunks += 1

    if result.failed_hunks > 0:
        result.overall_status = HunkStatus.FAILED.value
    elif result.variation_hunks > 0:
        result.overall_status = HunkStatus.VARIATION.value
    return result


def build_matched_result(local_entry: LocalPatchIndexEntry, mapping: dict) -> PatchResult:
    target_commit = mapping["target_commit"]
    return PatchResult(
        patch_file=local_entry.filename,
        commit_subject=local_entry.commit_subject,
        commit_hash=local_entry.commit_hash,
        commit_date=local_entry.commit_date,
        commit_author=local_entry.commit_author,
        overall_status=DiffStatus.UNMATCHED.value,
        diff_status=DiffStatus.UNMATCHED.value,
        target_commit=target_commit.commit,
        target_subject=target_commit.subject,
        local_patch_path=local_entry.full_path,
        local_patch_match_status=LocalPatchMatchStatus.MATCHED.value,
        local_patch_match_method="indexed",
        local_patch_candidates=[local_entry.full_path],
        local_patch_id=local_entry.patch_id,
        target_match_status=TargetCommitMatchStatus.MATCHED.value,
        target_match_method=mapping["method"],
        target_commit_candidates=mapping["candidates"],
        unmatched_reason="",
    )


def validate_patch_merged_diff(
    patch_dir: str,
    repo_path: str,
    branch: str,
    explicit_commit: str = "",
    upstream_branch: str = "",
    global_search: bool = False,
) -> tuple[list, dict]:
    local_index = build_local_patch_index(patch_dir, repo_path)
    target_index = build_target_commit_index(
        repo_path,
        branch,
        explicit_commit,
        upstream_branch=upstream_branch,
        global_search=global_search,
    )

    results = []
    matched_target_commits = set()

    for local_entry in local_index:
        mapping = map_local_patch_to_target_commit(repo_path, local_entry, target_index)

        if mapping["status"] == TargetCommitMatchStatus.AMBIGUOUS.value:
            results.append(
                PatchResult(
                    patch_file=local_entry.filename,
                    commit_subject=local_entry.commit_subject,
                    commit_hash=local_entry.commit_hash,
                    commit_date=local_entry.commit_date,
                    commit_author=local_entry.commit_author,
                    overall_status=DiffStatus.AMBIGUOUS.value,
                    diff_status=DiffStatus.AMBIGUOUS.value,
                    message="Multiple target commits matched this local patch",
                    local_patch_path=local_entry.full_path,
                    local_patch_match_status=LocalPatchMatchStatus.MATCHED.value,
                    local_patch_match_method="indexed",
                    local_patch_candidates=[local_entry.full_path],
                    local_patch_id=local_entry.patch_id,
                    target_match_status=TargetCommitMatchStatus.AMBIGUOUS.value,
                    target_match_method=mapping["method"],
                    target_commit_candidates=mapping["candidates"],
                    merged_patch_id=mapping["merged_patch_id"],
                    unmatched_reason="",
                )
            )
            continue

        if mapping["status"] == TargetCommitMatchStatus.UNMATCHED.value:
            results.append(
                PatchResult(
                    patch_file=local_entry.filename,
                    commit_subject=local_entry.commit_subject,
                    commit_hash=local_entry.commit_hash,
                    commit_date=local_entry.commit_date,
                    commit_author=local_entry.commit_author,
                    overall_status=DiffStatus.UNMATCHED.value,
                    diff_status=DiffStatus.UNMATCHED.value,
                    message="No target commit matched this local patch",
                    local_patch_path=local_entry.full_path,
                    local_patch_match_status=LocalPatchMatchStatus.MATCHED.value,
                    local_patch_match_method="indexed",
                    local_patch_candidates=[local_entry.full_path],
                    local_patch_id=local_entry.patch_id,
                    target_match_status=TargetCommitMatchStatus.UNMATCHED.value,
                    target_commit_candidates=[],
                    merged_patch_id=mapping["merged_patch_id"],
                    unmatched_reason=mapping["unmatched_reason"],
                )
            )
            continue

        result = build_matched_result(local_entry, mapping)
        target_commit = mapping["target_commit"]
        merged_patch_text = get_commit_diff(repo_path, target_commit.commit)
        result.matched_commit = target_commit.commit
        result.matched_by = mapping["method"]
        result.merged_patch_id = mapping["merged_patch_id"] or compute_patch_id(repo_path, merged_patch_text)
        result.file_differences = compare_patch_to_commit(extract_diff_body(local_entry.patch_text), merged_patch_text)
        has_material_diff = any(file_diff["status"] not in ("identical", "skipped") for file_diff in result.file_differences)
        has_skipped_diff = any(file_diff["status"] == "skipped" for file_diff in result.file_differences)
        if has_material_diff:
            result.overall_status = DiffStatus.DIFFERENT.value
            result.diff_status = DiffStatus.DIFFERENT.value
        else:
            result.overall_status = DiffStatus.IDENTICAL.value
            result.diff_status = DiffStatus.IDENTICAL.value
            if has_skipped_diff:
                result.message = "Binary or non-UTF8 file diffs were skipped during content comparison"
        matched_target_commits.add(target_commit.commit)
        results.append(result)

    metadata = {
        "local_patches_total": len(local_index),
        "matched_target_commits": len(matched_target_commits),
        "search_scope": target_index.search_scope,
        "upstream_branch": target_index.upstream_branch,
        "merge_base": target_index.merge_base,
        "target_commit_count": len(target_index.commits),
    }
    return results, metadata


def validate_patches(
    patch_dir: str,
    repo_path: str,
    branch: str,
    mode: str,
    tolerance: int,
    threshold: float,
    use_git_apply: bool = True,
    explicit_commit: str = "",
    upstream_branch: str = "",
    global_search: bool = False,
) -> ValidationResult:
    result = ValidationResult(repository=repo_path, branch=branch, mode=mode, match_strategy="subject-strict->subject-fuzzy->diff")

    if mode == ValidationMode.APPLICABILITY.value:
        patch_files = sorted(Path(patch_dir).glob("*.patch"))
        if not patch_files:
            print(f"Warning: No .patch files found in {patch_dir}")
            return result
        result.total_patches = len(patch_files)
        for patch_file in patch_files:
            print(f"Validating: {patch_file.name}")
            patch_result = validate_patch_applicability(str(patch_file), repo_path, branch, tolerance, threshold, use_git_apply)
            result.patches.append(asdict(patch_result))
            result.total_hunks += patch_result.total_hunks
            result.clean_hunks += patch_result.clean_hunks
            result.variation_hunks += patch_result.variation_hunks
            result.failed_hunks += patch_result.failed_hunks
        return result

    merged_results, metadata = validate_patch_merged_diff(
        patch_dir,
        repo_path,
        branch,
        explicit_commit,
        upstream_branch=upstream_branch,
        global_search=global_search,
    )
    result.patches = [asdict(item) for item in merged_results]
    result.total_patches = len(merged_results)
    result.local_patches_total = metadata["local_patches_total"]
    result.matched_target_commits = metadata["matched_target_commits"]
    result.search_scope = metadata["search_scope"]
    result.upstream_branch = metadata["upstream_branch"]
    result.merge_base = metadata["merge_base"]
    result.target_commit_count = metadata["target_commit_count"]

    for patch_result in merged_results:
        if patch_result.diff_status == DiffStatus.IDENTICAL.value:
            result.identical_patches += 1
        elif patch_result.diff_status == DiffStatus.DIFFERENT.value:
            result.different_patches += 1
        elif patch_result.diff_status == DiffStatus.AMBIGUOUS.value:
            result.ambiguous_patches += 1
        else:
            result.unmatched_patches += 1

        if patch_result.target_match_status == TargetCommitMatchStatus.MATCHED.value:
            continue
        if patch_result.target_match_status == TargetCommitMatchStatus.AMBIGUOUS.value:
            result.ambiguous_target_commits += 1
        else:
            result.unmatched_target_commits += 1

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate git format-patch files against a repository")
    parser.add_argument("--patches", "-p", required=True, help="Directory containing .patch files")
    parser.add_argument("--repo", "-r", required=True, help="Path to target git repository")
    parser.add_argument("--branch", "-b", default="HEAD", help="Target branch to validate against (default: HEAD)")
    parser.add_argument("--mode", choices=[item.value for item in ValidationMode], default=ValidationMode.APPLICABILITY.value, help="Validation mode")
    parser.add_argument("--tolerance", "-t", type=int, default=3, help="Line offset tolerance for fuzzy matching (default: 3)")
    parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold for variation status (default: 0.9)")
    parser.add_argument("--commit", help="Optional explicit target commit for merged-diff mode")
    parser.add_argument("--upstream-branch", default="", help="Optional upstream branch used to limit merged-diff matching scope.")
    parser.add_argument("--global-search", action="store_true", help="Search the full target branch history instead of limiting to upstream..branch.")
    parser.add_argument("--output", "-o", default="validation_result.json", help="Output JSON file path (default: validation_result.json)")
    parser.add_argument("--no-git-apply", action="store_true", help="Skip git apply --check validation")
    args = parser.parse_args()

    if not os.path.isdir(args.patches):
        print(f"Error: Patch directory not found: {args.patches}")
        sys.exit(1)
    if not os.path.isdir(args.repo):
        print(f"Error: Repository directory not found: {args.repo}")
        sys.exit(1)
    if not os.path.isdir(os.path.join(args.repo, ".git")):
        print(f"Error: Not a git repository: {args.repo}")
        sys.exit(1)

    print(f"Validating patches from: {args.patches}")
    print(f"Target repository: {args.repo}")
    print(f"Target branch: {args.branch}")
    print(f"Mode: {args.mode}")
    if args.mode == ValidationMode.APPLICABILITY.value:
        print(f"Tolerance: {args.tolerance} lines")
        print(f"Threshold: {args.threshold}")
    else:
        print("Match strategy: subject-strict->subject-fuzzy->diff")
        if args.commit:
            print(f"Explicit target commit: {args.commit}")
        elif args.global_search:
            print("Search scope: global branch history")
        elif args.upstream_branch:
            print(f"Search scope: upstream-limited ({args.upstream_branch}..{args.branch})")
        else:
            print("Search scope: upstream-limited (auto-detect upstream)")
    print("-" * 60)

    try:
        result = validate_patches(
            args.patches,
            args.repo,
            args.branch,
            args.mode,
            args.tolerance,
            args.threshold,
            use_git_apply=not args.no_git_apply,
            explicit_commit=args.commit or "",
            upstream_branch=args.upstream_branch,
            global_search=args.global_search,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(asdict(result), handle, indent=2, ensure_ascii=False)

    print("-" * 60)
    print(f"Total patches: {result.total_patches}")
    if args.mode == ValidationMode.APPLICABILITY.value:
        print(f"Total hunks: {result.total_hunks}")
        print(f"  Clean: {result.clean_hunks} ({100 * result.clean_hunks / max(result.total_hunks, 1):.1f}%)")
        print(f"  Variation: {result.variation_hunks} ({100 * result.variation_hunks / max(result.total_hunks, 1):.1f}%)")
        print(f"  Failed: {result.failed_hunks} ({100 * result.failed_hunks / max(result.total_hunks, 1):.1f}%)")
        exit_code = 1 if result.failed_hunks > 0 else 0
    else:
        print(f"  Search scope: {result.search_scope or 'global'}")
        if result.upstream_branch:
            print(f"  Upstream branch: {result.upstream_branch}")
        if result.merge_base:
            print(f"  Merge base: {result.merge_base}")
        print(f"  Indexed target commits: {result.target_commit_count}")
        print(f"  Local patch files: {result.local_patches_total}")
        print(f"  Matched target commits: {result.matched_target_commits}")
        print(f"  Unmatched target commits: {result.unmatched_target_commits}")
        print(f"  Ambiguous target commits: {result.ambiguous_target_commits}")
        print(f"  Identical: {result.identical_patches}")
        print(f"  Different: {result.different_patches}")
        print(f"  Unmatched: {result.unmatched_patches}")
        print(f"  Ambiguous: {result.ambiguous_patches}")
        exit_code = 1 if (result.different_patches or result.unmatched_patches or result.ambiguous_patches) else 0
    print(f"\nResults saved to: {args.output}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
