#!/usr/bin/env python3
"""
Export patches from Git repository commits.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from shared.cli import emit_json
from shared.config import DEFAULT_PATCH_DIR, LOG_LEVEL, LOG_FORMAT
from shared.git_helpers import is_git_repo
from shared.paths import resolve_user_path

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def export_patches(repo_path: str, commit_ids: List[str], output_dir: str) -> str:
    repo_path = resolve_user_path(repo_path)
    output_dir = resolve_user_path(output_dir)
    output_dic = {}
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        if not is_git_repo(repo_path):
            return json.dumps({
                "success": False,
                "error": f"{repo_path} is not a valid Git repository"
            }, ensure_ascii=False, indent=2)

        for commit_id in commit_ids:
            patch_result = {"error": None, "commit_msg": "", "patch_str": ""}
            try:
                commit_msg = subprocess.run(
                    ["git", "show", "--no-patch", "--format=%s", commit_id],
                    cwd=repo_path,
                    check=True,
                    text=True,
                    capture_output=True
                ).stdout.strip()
                safe_msg = "".join(c if c.isalnum() else "_" for c in commit_msg)
                patch_name = f"{commit_id[:7]}_{safe_msg[:50]}.patch"
                patch_path = os.path.join(output_dir, patch_name)

                with open(patch_path, "w", encoding="utf-8") as handle:
                    subprocess.run(
                        ["git", "format-patch", "-1", "--stdout", commit_id],
                        cwd=repo_path,
                        check=True,
                        stdout=handle,
                        text=True
                    )

                patch_result["commit_msg"] = commit_msg
                patch_result["patch_str"] = patch_path
                logger.info("Exported patch: %s", patch_name)
            except subprocess.CalledProcessError as exc:
                patch_result["error"] = str(exc)
                logger.error("Failed to export patch for %s: %s", commit_id, exc)

            output_dic[commit_id] = patch_result
    except Exception as exc:
        return json.dumps({
            "success": False,
            "error": f"Error: {str(exc)}"
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "success": True,
        "repo_path": repo_path,
        "output_dir": output_dir,
        "exported_patches": output_dic
    }, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export patches from a git repository.")
    parser.add_argument("--source-repo", required=True, help="Path to the source git repository.")
    parser.add_argument("--output-dir", default=DEFAULT_PATCH_DIR, help="Patch output directory.")
    parser.add_argument("--commits", nargs="+", required=True, help="Commit ids to export in order.")
    args = parser.parse_args()
    return emit_json(json.loads(export_patches(args.source_repo, args.commits, args.output_dir)))


if __name__ == "__main__":
    raise SystemExit(main())
