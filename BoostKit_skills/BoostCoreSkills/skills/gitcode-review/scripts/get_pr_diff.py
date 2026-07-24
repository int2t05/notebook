#!/usr/bin/env python3
"""
GitCode PR Diff 获取脚本

用于获取 GitCode Pull Request 的代码变更详情
"""

import json
import os
import sys
from typing import Optional
import urllib.request
import urllib.error


def get_pr_diff(owner: str, repo: str, pr_number: int, token: Optional[str] = None) -> dict:
    """
    获取 PR 的 diff 信息

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        token: GitCode 访问令牌（可选，从环境变量读取）

    Returns:
        包含 PR diff 信息的字典
    """
    if token is None:
        token = os.environ.get('GITCODE_TOKEN')

    if not token:
        raise ValueError("需要提供 GITCODE_TOKEN")

    # 首先获取 PR 详情以获取 base 和 head SHA
    pr_url = f"https://gitcode.com/api/v5/repos/{owner}/{repo}/pulls/{pr_number}"
    pr_params = f"?access_token={token}"

    try:
        with urllib.request.urlopen(pr_url + pr_params) as response:
            pr_data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise Exception(f"获取 PR 信息失败: {e.code} {e.reason}")

    # 提取 base 和 head SHA
    base_sha = pr_data['base']['sha']
    head_sha = pr_data['head']['sha']

    # 获取 compare 信息（包含 diff）
    compare_url = f"https://gitcode.com/api/v5/repos/{owner}/{repo}/compare/{base_sha}...{head_sha}"
    compare_params = f"?access_token={token}"

    try:
        with urllib.request.urlopen(compare_url + compare_params) as response:
            compare_data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise Exception(f"获取 diff 信息失败: {e.code} {e.reason}")

    return {
        'pr_info': {
            'number': pr_data['number'],
            'title': pr_data['title'],
            'body': pr_data['body'],
            'state': pr_data['state'],
            'user': pr_data['user']['login'],
            'created_at': pr_data['created_at'],
            'updated_at': pr_data['updated_at'],
        },
        'files': compare_data.get('files', []),
        'commits': compare_data.get('commits', []),
    }


def format_diff_output(diff_data: dict) -> str:
    """
    格式化 diff 输出为易读的文本

    Args:
        diff_data: get_pr_diff 返回的数据

    Returns:
        格式化的文本输出
    """
    output = []

    # PR 基本信息
    pr_info = diff_data['pr_info']
    output.append(f"PR #{pr_info['number']}: {pr_info['title']}")
    output.append(f"作者: {pr_info['user']}")
    output.append(f"状态: {pr_info['state']}")
    output.append(f"创建时间: {pr_info['created_at']}")
    output.append("")

    if pr_info['body']:
        output.append("描述:")
        output.append(pr_info['body'])
        output.append("")

    # 文件变更
    files = diff_data['files']
    output.append(f"变更文件数: {len(files)}")
    output.append("")

    for file in files:
        output.append(f"文件: {file['filename']}")
        output.append(f"状态: {file['status']}")
        output.append(f"变更: +{file['additions']} -{file['deletions']}")

        if 'patch' in file:
            output.append("")
            output.append("Diff:")
            output.append(file['patch'])

        output.append("")
        output.append("-" * 80)
        output.append("")

    return "\n".join(output)


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("用法: python get_pr_diff.py <owner> <repo> <pr_number>")
        print("示例: python get_pr_diff.py CarbonadoRain hyperscan 2")
        print("")
        print("需要设置环境变量 GITCODE_TOKEN")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    pr_number = int(sys.argv[3])

    try:
        diff_data = get_pr_diff(owner, repo, pr_number)

        # 输出 JSON 格式（用于程序化处理）
        if '--json' in sys.argv:
            print(json.dumps(diff_data, ensure_ascii=False, indent=2))
        else:
            # 输出易读格式
            print(format_diff_output(diff_data))

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
