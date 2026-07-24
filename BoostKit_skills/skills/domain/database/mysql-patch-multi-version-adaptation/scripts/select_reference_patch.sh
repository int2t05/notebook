#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "用法: $0 <repo_dir> <keyword> [branch-pattern]" >&2
  exit 1
fi

repo_dir="$1"
keyword="$2"
branch_pattern="${3:-origin/}"

if [ ! -d "$repo_dir/.git" ]; then
  echo "错误: $repo_dir 不是 git 仓库" >&2
  exit 1
fi

git -C "$repo_dir" for-each-ref --format='%(refname:short)' refs/remotes |
  grep "$branch_pattern" |
  while read -r branch; do
    echo "== $branch =="
    git -C "$repo_dir" ls-tree -r --name-only "$branch" boostdb-patches 2>/dev/null |
      grep -i "$keyword" || true
    echo
  done
