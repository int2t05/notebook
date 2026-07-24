#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "用法: $0 <repo_dir> <patch_file>" >&2
  exit 1
fi

repo_dir="$1"
patch_file="$2"

if [ ! -d "$repo_dir/.git" ]; then
  echo "错误: $repo_dir 不是 git 仓库" >&2
  exit 1
fi

if [ ! -f "$patch_file" ]; then
  echo "错误: patch 不存在: $patch_file" >&2
  exit 1
fi

echo "== 仓库 =="
echo "$repo_dir"
echo

echo "== patch =="
echo "$patch_file"
echo

echo "== 当前分支 =="
git -C "$repo_dir" branch --show-current || true
echo

echo "== 工作树状态 =="
git -C "$repo_dir" status --short || true
echo

echo "== patch 修改概览 =="
git -C "$repo_dir" apply --stat "$patch_file" || true
echo

echo "== patch 新增/删除文件摘要 =="
git -C "$repo_dir" apply --summary "$patch_file" || true
echo

echo "== 非破坏性 apply 检查 =="
if git -C "$repo_dir" apply --check "$patch_file" 2>/tmp/mysql_patch_apply_check.err; then
  echo "apply --check: 通过"
else
  echo "apply --check: 失败"
  cat /tmp/mysql_patch_apply_check.err
fi
