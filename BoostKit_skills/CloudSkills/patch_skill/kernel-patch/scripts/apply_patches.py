#!/usr/bin/env python3
"""
Apply patches to a test branch with conflict detection.
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from typing import List, Optional

# 添加父目录到路径以导入共享模块
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from shared.cli import emit_json
from shared.config import DEFAULT_REJECT_DIR, DEFAULT_TEST_BRANCH_PREFIX, LOG_LEVEL, LOG_FORMAT
from shared.git_helpers import branch_exists, is_git_repo
from shared.paths import resolve_user_path, to_repo_relative

# 配置日志
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def parse_git_am_missing_files(stderr: str) -> List[str]:
    """
    从 git am --reject 的 stderr 中解析出不存在的文件

    匹配模式：
    - 中文: error: <filename>：不存在于索引中
    - 英文: error: <filename>: does not exist in index

    Args:
        stderr: git am 的标准错误输出

    Returns:
        不存在的文件路径列表
    """
    missing_files = []
    # 匹配中文和英文的错误信息
    patterns = [
        r'error:\s+(.+?)\s*：不存在于索引中',
        r'error:\s+(.+?)\s*:\s*does not exist in index',
    ]

    for line in stderr.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                filepath = match.group(1).strip()
                if filepath:
                    missing_files.append(filepath)
                    break

    return missing_files


def generate_rej_from_patch(
    patch_content: str,
    target_file: str,
    reject_dir: str
) -> Optional[str]:
    """
    从 patch 内容中提取指定文件的 hunks 并生成 .rej 文件

    Args:
        patch_content: 完整的 patch 文件内容
        target_file: 目标文件路径（如 arch/arm64/configs/openeuler_defconfig）
        reject_dir: .rej 文件输出目录

    Returns:
        生成的 .rej 文件绝对路径，失败返回 None
    """
    lines = patch_content.split('\n')
    i = 0
    hunks = []
    in_target_file = False

    logger.debug(f"尝试为不存在的文件生成 .rej: {target_file}")

    while i < len(lines):
        line = lines[i]

        # 检测是否进入目标文件 (+++ b/xxx 或 +++ a/xxx)
        if line.startswith('+++ b/') or line.startswith('+++ a/'):
            # 修复：直接去掉前缀，保留完整路径
            if line.startswith('+++ b/'):
                current_file = line[6:]  # 去掉 "+++ b/"
            elif line.startswith('+++ a/'):
                current_file = line[6:]  # 去掉 "+++ a/"
            else:
                current_file = ''

            if current_file == target_file:
                in_target_file = True
                hunks = []
                logger.debug(f"找到目标文件: {current_file}")
            else:
                in_target_file = False

        # 如果在目标文件中，收集 hunk
        if in_target_file:
            # 收集从 @@ 开始的所有行
            if line.startswith('@@') or len(hunks) > 0:
                hunks.append(line)

            # 检测下一个 diff 块开始（只有在收集了实际 hunk 内容后才退出）
            # 使用 diff --git 检测更可靠，避免误判 +++ 行
            if line.startswith('diff --git') and len(hunks) > 1:
                break

        i += 1

    if not hunks:
        logger.warning(f"未能从补丁中提取文件 {target_file} 的 hunk 内容")
        return None

    # 生成 .rej 文件
    safe_filename = target_file.replace('/', '--') + ".rej"
    rej_path = os.path.join(reject_dir, safe_filename)

    try:
        with open(rej_path, 'w', encoding='utf-8') as f:
            f.write(f"diff --git a/{target_file} b/{target_file}\n")
            f.write(f"--- a/{target_file}\n")
            f.write(f"+++ b/{target_file}\n")
            f.write('\n'.join(hunks))
        logger.info(f"成功生成 .rej 文件: {rej_path}")
        return os.path.abspath(rej_path)
    except Exception as e:
        logger.warning(f"生成 .rej 文件失败: {e}")
        return None


def apply_single_patch(
    patch_file: str,
    target_repo_path: str,
    target_branch: str,
    reject_dir: str = "rejects",
    test_branch_prefix: str = "auto-patch-",
    test_branch: str = None
) -> str:
    """
    应用单个补丁到测试分支

    Args:
        patch_file: 补丁文件的绝对路径
        target_repo_path: 目标仓库的绝对路径
        target_branch: 目标分支名称（如 "main"）
        reject_dir: .rej 文件输出目录（默认 "rejects"）
        test_branch_prefix: 测试分支前缀（默认 "auto-patch-"）
        test_branch: 指定测试分支名（None 表示创建新分支）

    Returns:
        JSON 格式的应用结果
    """
    # 转换为绝对路径
    patch_file = resolve_user_path(patch_file)
    target_repo_path = resolve_user_path(target_repo_path)

    if os.path.isabs(reject_dir):
        reject_dir = resolve_user_path(reject_dir)
    else:
        reject_dir = os.path.join(target_repo_path, reject_dir)

    os.makedirs(reject_dir, exist_ok=True)

    try:
        # 步骤 1: 验证输入
        # 检查补丁文件是否存在
        if not os.path.isfile(patch_file):
            return json.dumps({
                "success": False,
                "patch_file": patch_file,
                "error": "补丁文件不存在",
                "git_am_status": "failed"
            }, ensure_ascii=False, indent=2)

        # 检查是否是 Git 仓库
        if not is_git_repo(target_repo_path):
            return json.dumps({
                "success": False,
                "patch_file": patch_file,
                "error": f"{target_repo_path} 不是有效的 Git 仓库",
                "git_am_status": "failed"
            }, ensure_ascii=False, indent=2)

        # 检查目标分支是否存在
        if not branch_exists(target_branch, target_repo_path):
            return json.dumps({
                "success": False,
                "patch_file": patch_file,
                "error": f"目标分支 {target_branch} 不存在",
                "git_am_status": "failed"
            }, ensure_ascii=False, indent=2)

        # 步骤 2: 分支管理（首次创建，后续复用）
        if test_branch is None:
            # 首次调用：创建新测试分支
            test_branch = f"{test_branch_prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 先切换到目标分支
            subprocess.run(
                ["git", "checkout", "-q", target_branch],
                cwd=target_repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 创建测试分支
            subprocess.run(
                ["git", "checkout", "-q", "-b", test_branch],
                cwd=target_repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"创建测试分支: {test_branch}")
        else:
            # 后续调用：复用现有测试分支
            if not branch_exists(test_branch, target_repo_path):
                return json.dumps({
                    "success": False,
                    "patch_file": patch_file,
                    "error": f"测试分支 {test_branch} 不存在",
                    "git_am_status": "failed"
                }, ensure_ascii=False, indent=2)

            # 切换到测试分支
            subprocess.run(
                ["git", "checkout", "-q", test_branch],
                cwd=target_repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"复用测试分支: {test_branch}")

        # 步骤 43: 执行 git am --reject
        process = subprocess.run(
            ["git", "am", "--reject", patch_file],
            cwd=target_repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 步骤 4: 读取补丁文件内容（用于后续提取 hunk）
        patch_content = ""
        try:
            with open(patch_file, 'r', encoding='utf-8', errors='ignore') as f:
                patch_content = f.read()
        except Exception:
            pass

        # 步骤 5: 收集/生成 .rej 文件
        rej_files = []

        # 5.1 收集 git 生成的 .rej 文件（冲突文件）
        for root, _, files in os.walk(target_repo_path):
            for file in files:
                if file.endswith(".rej"):
                    rej_path = os.path.join(root, file)
                    target_path = os.path.join(reject_dir, file)
                    try:
                        shutil.move(os.path.abspath(rej_path), target_path)
                        rej_files.append(os.path.abspath(target_path))
                    except Exception:
                        rej_files.append(os.path.abspath(rej_path))

        # 5.2 从 git am stderr 解析不存在的文件，并生成 .rej
        missing_files = parse_git_am_missing_files(process.stderr)

        if missing_files:
            logger.info(f"检测到 {len(missing_files)} 个文件不存在: {missing_files}")
            for missing_file in missing_files:
                rej_path = generate_rej_from_patch(patch_content, missing_file, reject_dir)
                if rej_path:
                    rej_files.append(rej_path)
                    logger.info(f"生成 .rej 文件: {os.path.basename(rej_path)}")

        # 步骤 6: 判断结果并返回
        applied_commit = None
        if process.returncode == 0:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=target_repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if head.returncode == 0:
                applied_commit = head.stdout.strip()

        # 如果 git am 成功且没有 .rej 文件
        if process.returncode == 0 and not rej_files:
            logger.info(f"补丁应用成功")
            return json.dumps({
                "success": True,
                "patch_file": patch_file,
                "test_branch": test_branch,
                "applied_commit": applied_commit,
                "has_conflicts": False,
                "conflict_files": [],
                "git_am_status": "completed",
                "reject_dir": reject_dir,
                "next_action": "continue",
            }, ensure_ascii=False, indent=2)

        # 如果有 .rej 文件（冲突）
        if rej_files:
            repo_relative_conflict_files = []
            for path in rej_files:
                try:
                    repo_relative_conflict_files.append(to_repo_relative(path, target_repo_path))
                except ValueError:
                    continue
            logger.info(f"检测到 {len(rej_files)} 个冲突，git am 处于暂停状态")
            return json.dumps({
                "success": False,
                "patch_file": patch_file,
                "test_branch": test_branch,
                "applied_commit": None,
                "has_conflicts": True,
                "conflict_files": rej_files,
                "repo_relative_conflict_files": repo_relative_conflict_files,
                "git_am_status": "paused",
                "reject_dir": reject_dir,
                "reject_dir_outside_repo": not os.path.abspath(reject_dir).startswith(os.path.abspath(target_repo_path)),
                "next_action": "resolve_conflicts",
            }, ensure_ascii=False, indent=2)

        # 如果 git am 失败且没有 .rej 文件（其他错误）
        error_msg = process.stderr.strip() or process.stdout.strip()
        logger.error(f"补丁应用失败: {error_msg}")
        return json.dumps({
            "success": False,
            "patch_file": patch_file,
            "error": error_msg,
            "has_conflicts": False,
            "git_am_status": "failed",
            "reject_dir": reject_dir,
            "next_action": "stop_invalid_input",
        }, ensure_ascii=False, indent=2)

    except subprocess.CalledProcessError as e:
        error_msg = str(e)
        logger.error(f"Git 命令执行失败: {error_msg}")
        return json.dumps({
            "success": False,
            "patch_file": patch_file,
            "error": error_msg,
            "git_am_status": "failed",
            "next_action": "stop_invalid_input",
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"应用补丁时发生异常: {error_msg}")
        return json.dumps({
            "success": False,
            "patch_file": patch_file,
            "error": error_msg,
            "git_am_status": "failed",
            "next_action": "stop_invalid_input",
        }, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a single patch to a test branch.")
    parser.add_argument("--repo-path", required=True, help="Target repository path.")
    parser.add_argument("--target-branch", required=True, help="Target branch.")
    parser.add_argument("--patch-file", required=True, help="Single patch file path.")
    parser.add_argument("--reject-dir", default=DEFAULT_REJECT_DIR, help="Directory used to store copied .rej files.")
    parser.add_argument("--test-branch", default=None, help="Existing test branch to reuse.")
    parser.add_argument("--test-branch-prefix", default=DEFAULT_TEST_BRANCH_PREFIX, help="Prefix for new test branches.")
    args = parser.parse_args()
    payload = json.loads(apply_single_patch(
        patch_file=args.patch_file,
        target_repo_path=args.repo_path,
        target_branch=args.target_branch,
        reject_dir=args.reject_dir,
        test_branch_prefix=args.test_branch_prefix,
        test_branch=args.test_branch,
    ))
    return emit_json(payload)


if __name__ == "__main__":
    raise SystemExit(main())
