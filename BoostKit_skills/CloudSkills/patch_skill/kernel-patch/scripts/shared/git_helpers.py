"""
Git utility functions
Git 辅助函数
"""

import subprocess
import os
import logging

logger = logging.getLogger(__name__)


def branch_exists(branch_name: str, repo_path: str) -> bool:
    """
    检查分支是否存在

    Args:
        branch_name: 分支名称
        repo_path: 仓库路径

    Returns:
        分支是否存在
    """
    try:
        subprocess.run(
            ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=repo_path
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_git_repo(repo_path: str) -> bool:
    """
    验证是否是 Git 仓库

    Args:
        repo_path: 仓库路径

    Returns:
        是否是有效的 Git 仓库
    """
    try:
        subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=repo_path
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_commit_message(commit_id: str, repo_path: str) -> str:
    """
    获取 commit 消息

    Args:
        commit_id: Commit ID
        repo_path: 仓库路径

    Returns:
        Commit 消息
    """
    try:
        result = subprocess.run(
            ['git', 'show', '--no-patch', '--format=%s', commit_id],
            check=True,
            text=True,
            capture_output=True,
            cwd=repo_path
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def safe_git_command(cmd: list, cwd: str, **kwargs) -> subprocess.CompletedProcess:
    """
    执行 git 命令并处理错误

    Args:
        cmd: 命令列表
        cwd: 工作目录
        **kwargs: 其他 subprocess.run 参数

    Returns:
        subprocess.CompletedProcess 对象
    """
    try:
        return subprocess.run(
            cmd,
            check=True,
            cwd=cwd,
            **kwargs
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Git 命令执行失败: {' '.join(cmd)}, 错误: {e}")
        raise
