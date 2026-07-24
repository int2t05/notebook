"""
Path helpers for kernel_patch scripts.
"""

from pathlib import Path
from typing import Iterable, List


def resolve_user_path(path: str, cwd: str | None = None) -> str:
    base = Path(cwd).resolve() if cwd else Path.cwd().resolve()
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return str(candidate.resolve())


def to_repo_relative(path: str, repo_path: str) -> str:
    repo = Path(repo_path).resolve()
    candidate = Path(path)
    if not candidate.is_absolute():
        return str(candidate)
    candidate = candidate.resolve()
    try:
        return str(candidate.relative_to(repo))
    except ValueError as exc:
        raise ValueError(f"path {candidate} is outside repo {repo}") from exc


def normalize_repo_paths(paths: Iterable[str], repo_path: str) -> List[str]:
    return [to_repo_relative(path, repo_path) for path in paths]
