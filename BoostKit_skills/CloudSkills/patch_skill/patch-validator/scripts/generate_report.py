#!/usr/bin/env python3
"""
Report Generator - Generate Markdown reports from patch validation results.

Reads JSON validation results and produces a detailed Markdown report.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def load_validation_result(json_path: str) -> dict:
    """Load validation result from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_status_emoji(status: str) -> str:
    """Get emoji for status."""
    emojis = {
        "CLEAN": "✅",
        "VARIATION": "⚠️",
        "FAILED": "❌",
        "IDENTICAL": "✅",
        "DIFFERENT": "❌",
        "UNMATCHED": "❓",
        "AMBIGUOUS": "⚠️",
    }
    return emojis.get(status, "❓")


def get_status_text(status: str) -> str:
    """Get Chinese text for status."""
    texts = {
        "CLEAN": "无误差",
        "VARIATION": "存在误差",
        "FAILED": "错误",
        "IDENTICAL": "完全一致",
        "DIFFERENT": "存在差异",
        "UNMATCHED": "未匹配",
        "AMBIGUOUS": "匹配歧义",
    }
    return texts.get(status, status)


def get_local_match_text(status: str) -> str:
    texts = {
        "MATCHED": "已匹配本地补丁",
        "UNMATCHED_LOCAL_PATCH": "未找到对应本地补丁",
        "AMBIGUOUS_LOCAL_PATCH": "匹配到多个本地补丁候选",
        "UNMATCHED_TARGET_COMMIT": "未找到对应目标提交",
    }
    return texts.get(status, status)


def get_target_match_text(status: str) -> str:
    texts = {
        "MATCHED": "已匹配目标提交",
        "UNMATCHED": "未找到目标提交",
        "AMBIGUOUS": "匹配到多个目标提交候选",
    }
    return texts.get(status, status)


def get_unmatched_reason_text(reason: str) -> str:
    texts = {
        "no_subject_candidate": "标题未形成可用候选",
        "subject_candidates_below_threshold": "标题未达到近似匹配阈值",
        "diff_not_found": "标题和 patch-id 均未命中",
    }
    return texts.get(reason, reason)


def generate_summary_section(result: dict) -> str:
    """Generate executive summary section."""
    mode = result.get("mode", "applicability")
    if mode == "merged-diff":
        identical = result.get("identical_patches", 0)
        different = result.get("different_patches", 0)
        unmatched = result.get("unmatched_patches", 0)
        ambiguous = result.get("ambiguous_patches", 0)
        total_patches = result.get("total_patches", 0)
        local_total = result.get("local_patches_total", 0)
        matched_target = result.get("matched_target_commits", 0)
        unmatched_target = result.get("unmatched_target_commits", 0)
        ambiguous_target = result.get("ambiguous_target_commits", 0)
        summary = """## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | {total_patches} |
| 本地补丁文件数 | {local_total} |
| 已匹配目标提交 | {matched_target} |
| 未匹配目标提交 | {unmatched_target} |
| 歧义目标提交 | {ambiguous_target} |
| 完全一致 | {identical} |
| 存在差异 | {different} |
| 未匹配 | {unmatched} |
| 匹配歧义 | {ambiguous} |

""".format(
            total_patches=total_patches,
            local_total=local_total,
            matched_target=matched_target,
            unmatched_target=unmatched_target,
            ambiguous_target=ambiguous_target,
            identical=identical,
            different=different,
            unmatched=unmatched,
            ambiguous=ambiguous,
        )
        if different > 0:
            summary += "> **整体状态**: ❌ 已发现本地补丁与目标仓库已合入补丁存在差异\n\n"
        elif unmatched > 0 or ambiguous > 0:
            summary += "> **整体状态**: ⚠️ 存在未定位或定位歧义的补丁\n\n"
        else:
            summary += "> **整体状态**: ✅ 本地补丁与已合入补丁完全一致\n\n"
        return summary

    total_hunks = result.get("total_hunks", 0)
    clean_hunks = result.get("clean_hunks", 0)
    variation_hunks = result.get("variation_hunks", 0)
    failed_hunks = result.get("failed_hunks", 0)

    if total_hunks > 0:
        clean_pct = 100 * clean_hunks / total_hunks
        variation_pct = 100 * variation_hunks / total_hunks
        failed_pct = 100 * failed_hunks / total_hunks
    else:
        clean_pct = variation_pct = failed_pct = 0

    summary = """## 执行摘要

| 指标 | 数量 | 百分比 |
|------|------|--------|
| 总补丁数 | {total_patches} | - |
| 总 Hunks 数 | {total_hunks} | - |
| 无误差 Hunks | {clean_hunks} | {clean_pct:.1f}% |
| 存在误差 Hunks | {variation_hunks} | {variation_pct:.1f}% |
| 错误 Hunks | {failed_hunks} | {failed_pct:.1f}% |

""".format(
        total_patches=result.get("total_patches", 0),
        total_hunks=total_hunks,
        clean_hunks=clean_hunks,
        variation_hunks=variation_hunks,
        failed_hunks=failed_hunks,
        clean_pct=clean_pct,
        variation_pct=variation_pct,
        failed_pct=failed_pct
    )

    # Add status indicator
    if failed_hunks > 0:
        summary += "> **整体状态**: ❌ 存在错误，需要修复\n\n"
    elif variation_hunks > 0:
        summary += "> **整体状态**: ⚠️ 存在轻微偏差，建议检查\n\n"
    else:
        summary += "> **整体状态**: ✅ 全部通过\n\n"

    return summary


def generate_hunk_table(hunks: list) -> str:
    """Generate a table for hunk results."""
    if not hunks:
        return "*此文件无 hunks*\n"

    table = "| Hunk # | 行号 | 状态 | 相似度 | 说明 |\n"
    table += "|--------|------|------|--------|------|\n"

    for hunk in hunks:
        emoji = get_status_emoji(hunk.get("status", ""))
        status_text = get_status_text(hunk.get("status", ""))
        line_range = f"{hunk.get('original_start_line', '?')}"

        if hunk.get("original_line_count", 0) > 1:
            end_line = hunk.get("original_start_line", 0) + hunk.get("original_line_count", 0) - 1
            line_range = f"{hunk.get('original_start_line', '?')}-{end_line}"

        similarity = hunk.get("similarity", 0)
        similarity_str = f"{similarity:.0%}" if similarity < 1.0 else "100%"

        message = hunk.get("message", "")

        # Truncate long messages
        if len(message) > 50:
            message = message[:47] + "..."

        table += f"| {hunk.get('hunk_number', '?')} | {line_range} | {emoji} {status_text} | {similarity_str} | {message} |\n"

    return table


def generate_file_section(file_result: dict, file_index: int) -> str:
    """Generate section for a single file."""
    source = file_result.get("source_file", "unknown")
    target = file_result.get("target_file", "unknown")

    # Clean up file paths
    if source.startswith("a/"):
        source = source[2:]
    if target.startswith("b/"):
        target = target[2:]

    status = file_result.get("status", "UNKNOWN")
    emoji = get_status_emoji(status)
    status_text = get_status_text(status)

    section = f"### 文件 {file_index}: `{target}`\n\n"
    section += f"**状态**: {emoji} {status_text}\n\n"

    if source != target:
        section += f"*源文件*: `{source}`\n\n"

    if file_result.get("message"):
        section += f"*备注*: {file_result['message']}\n\n"

    section += "#### Hunks 详情\n\n"
    section += generate_hunk_table(file_result.get("hunks", []))

    return section


def generate_patch_section(patch: dict, patch_index: int) -> str:
    """Generate section for a single patch."""
    if patch.get("diff_status"):
        return generate_merged_diff_patch_section(patch, patch_index)

    patch_file = patch.get("patch_file", "unknown")
    subject = patch.get("commit_subject", "No subject")
    commit_hash = patch.get("commit_hash", "")
    commit_date = patch.get("commit_date", "")
    commit_author = patch.get("commit_author", "")

    status = patch.get("overall_status", "UNKNOWN")
    emoji = get_status_emoji(status)
    status_text = get_status_text(status)

    # Statistics
    total = patch.get("total_hunks", 0)
    clean = patch.get("clean_hunks", 0)
    variation = patch.get("variation_hunks", 0)
    failed = patch.get("failed_hunks", 0)

    section = f"## 补丁 {patch_index}: {subject}\n\n"
    section += f"| 属性 | 值 |\n|------|-----|\n"
    section += f"| 文件 | `{patch_file}` |\n"

    if commit_hash:
        section += f"| 提交 | `{commit_hash}` |\n"
    if commit_author:
        section += f"| 作者 | {commit_author} |\n"
    if commit_date:
        section += f"| 日期 | {commit_date} |\n"

    section += f"| 状态 | {emoji} {status_text} |\n"
    section += f"| Hunks | {clean}/{total} 无误差, {variation} 误差, {failed} 错误 |\n\n"

    # File sections
    files = patch.get("files", [])
    for i, file_result in enumerate(files, 1):
        section += generate_file_section(file_result, i)
        section += "\n"

    return section


def generate_line_list(title: str, lines: list) -> str:
    if not lines:
        return ""
    section = f"**{title}**:\n"
    for line in lines:
        section += f"- `{line}`\n"
    section += "\n"
    return section


def generate_file_diff_section(file_diff: dict, file_index: int) -> str:
    target_file = file_diff.get("target_file", "unknown")
    raw_status = file_diff.get("status", "unknown")
    normalized_status = raw_status.lower()
    emoji = get_status_emoji("DIFFERENT" if any(token in normalized_status for token in ("different", "missing", "extra")) else "IDENTICAL")
    status_text = raw_status

    section = f"### 文件 {file_index}: `{target_file}`\n\n"
    section += f"**状态**: {emoji} `{status_text}`\n\n"
    if file_diff.get("message"):
        section += f"*备注*: {file_diff['message']}\n\n"

    section += generate_line_list("本地补丁有、目标已合入补丁缺失的新增行", file_diff.get("missing_added_lines", []))
    section += generate_line_list("目标已合入补丁额外包含的新增行", file_diff.get("extra_added_lines", []))
    section += generate_line_list("删除行不一致", file_diff.get("removed_line_mismatches", []))

    hunk_differences = file_diff.get("hunk_differences", [])
    if hunk_differences:
        section += "| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |\n"
        section += "|------------|-------------|------|--------|------|\n"
        for hunk in hunk_differences:
            similarity = hunk.get("similarity", 0)
            section += (
                f"| {hunk.get('local_hunk_number', '-')} | {hunk.get('merged_hunk_number', '-')} | "
                f"`{hunk.get('status', '')}` | {similarity:.1%} | {hunk.get('message', '')} |\n"
            )
        section += "\n"

    return section


def generate_merged_diff_patch_section(patch: dict, patch_index: int) -> str:
    patch_file = patch.get("patch_file", "unknown")
    subject = patch.get("commit_subject") or patch.get("target_subject") or "No subject"
    commit_hash = patch.get("commit_hash", "")
    status = patch.get("diff_status", "UNKNOWN")
    emoji = get_status_emoji(status)
    status_text = get_status_text(status)

    section = f"## 补丁 {patch_index}: {subject}\n\n"
    section += "| 属性 | 值 |\n|------|-----|\n"
    if patch_file:
        section += f"| 本地补丁文件 | `{patch_file}` |\n"
    if patch.get("local_patch_path"):
        section += f"| 本地补丁路径 | `{patch['local_patch_path']}` |\n"
    if commit_hash:
        section += f"| 本地提交 | `{commit_hash}` |\n"
    section += f"| 状态 | {emoji} {status_text} |\n"
    if patch.get("target_commit"):
        section += f"| 目标提交 | `{patch['target_commit']}` |\n"
    if patch.get("target_subject"):
        section += f"| 目标标题 | {patch['target_subject']} |\n"
    if patch.get("target_match_status"):
        section += f"| 目标提交匹配状态 | {get_target_match_text(patch['target_match_status'])} |\n"
    if patch.get("target_match_method"):
        section += f"| 目标提交匹配方式 | `{patch['target_match_method']}` |\n"
    if patch.get("unmatched_reason"):
        section += f"| 未匹配原因 | {get_unmatched_reason_text(patch['unmatched_reason'])} |\n"
    if patch.get("local_patch_match_status"):
        section += f"| 本地补丁匹配状态 | {get_local_match_text(patch['local_patch_match_status'])} |\n"
    if patch.get("local_patch_match_method"):
        section += f"| 本地补丁匹配方式 | `{patch['local_patch_match_method']}` |\n"
    if patch.get("matched_by"):
        section += f"| Diff 比较匹配方式 | `{patch['matched_by']}` |\n"
    if patch.get("local_patch_id"):
        section += f"| 本地 patch-id | `{patch['local_patch_id']}` |\n"
    if patch.get("merged_patch_id"):
        section += f"| 目标 patch-id | `{patch['merged_patch_id']}` |\n"
    section += "\n"

    if patch.get("message"):
        section += f"*备注*: {patch['message']}\n\n"

    if patch.get("local_patch_candidates"):
        section += "**本地补丁候选**:\n"
        for candidate in patch["local_patch_candidates"]:
            section += f"- `{candidate}`\n"
        section += "\n"

    if patch.get("target_commit_candidates"):
        section += "**目标提交候选**:\n"
        for candidate in patch["target_commit_candidates"]:
            section += f"- `{candidate}`\n"
        section += "\n"

    if status in ("UNMATCHED", "AMBIGUOUS"):
        return section

    for i, file_diff in enumerate(patch.get("file_differences", []), 1):
        section += generate_file_diff_section(file_diff, i)
        section += "\n"

    return section


def generate_failed_hunks_detail(result: dict) -> str:
    """Generate detailed section for failed hunks with fix suggestions."""
    failed_hunks = []

    for patch in result.get("patches", []):
        for file_result in patch.get("files", []):
            for hunk in file_result.get("hunks", []):
                if hunk.get("status") == "FAILED":
                    failed_hunks.append({
                        "patch_file": patch.get("patch_file", ""),
                        "patch_subject": patch.get("commit_subject", ""),
                        "target_file": file_result.get("target_file", ""),
                        "hunk_number": hunk.get("hunk_number", 0),
                        "line_range": f"{hunk.get('original_start_line', '?')}",
                        "message": hunk.get("message", ""),
                        "similarity": hunk.get("similarity", 0),
                        "context_preview": hunk.get("context_preview", "")
                    })

    if not failed_hunks:
        return ""

    section = "## 错误 Hunks 详情\n\n"
    section += "> 以下 hunks 无法成功匹配，需要手动检查和修复。\n\n"

    for i, hunk in enumerate(failed_hunks, 1):
        target_file = hunk["target_file"]
        if target_file.startswith("b/"):
            target_file = target_file[2:]

        section += f"### 错误 {i}: `{target_file}` Hunk #{hunk['hunk_number']}\n\n"
        section += f"- **补丁文件**: `{hunk['patch_file']}`\n"
        section += f"- **补丁主题**: {hunk['patch_subject']}\n"
        section += f"- **行号**: {hunk['line_range']}\n"
        section += f"- **错误信息**: {hunk['message']}\n"
        section += f"- **最佳相似度**: {hunk['similarity']:.1%}\n\n"

        if hunk.get("context_preview"):
            section += "**上下文预览**:\n```\n" + hunk["context_preview"] + "\n```\n\n"

        section += "**修复建议**:\n"
        section += "1. 检查目标文件是否存在\n"
        section += "2. 确认目标分支是否正确\n"
        section += "3. 手动检查代码冲突\n"
        section += "4. 考虑使用 `git apply --3way` 进行三方合并\n\n"

    return section


def generate_variation_hunks_detail(result: dict) -> str:
    """Generate detailed section for variation hunks."""
    variation_hunks = []

    for patch in result.get("patches", []):
        for file_result in patch.get("files", []):
            for hunk in file_result.get("hunks", []):
                if hunk.get("status") == "VARIATION":
                    variation_hunks.append({
                        "patch_file": patch.get("patch_file", ""),
                        "patch_subject": patch.get("commit_subject", ""),
                        "target_file": file_result.get("target_file", ""),
                        "hunk_number": hunk.get("hunk_number", 0),
                        "original_line": hunk.get("original_start_line", 0),
                        "actual_line": hunk.get("actual_start_line", 0),
                        "similarity": hunk.get("similarity", 0),
                        "message": hunk.get("message", "")
                    })

    if not variation_hunks:
        return ""

    section = "## 误差 Hunks 详情\n\n"
    section += "> 以下 hunks 存在轻微偏差，通常可以正常应用，但建议检查。\n\n"

    section += "| # | 文件 | Hunk | 原始行 | 实际行 | 偏移 | 相似度 |\n"
    section += "|---|------|------|--------|--------|------|--------|\n"

    for i, hunk in enumerate(variation_hunks, 1):
        target_file = hunk["target_file"]
        if target_file.startswith("b/"):
            target_file = target_file[2:]

        offset = 0
        if hunk.get("actual_line") and hunk.get("original_line"):
            offset = hunk["actual_line"] - hunk["original_line"]

        section += f"| {i} | `{target_file}` | {hunk['hunk_number']} | {hunk['original_line']} | {hunk['actual_line']} | {offset:+d} | {hunk['similarity']:.1%} |\n"

    section += "\n"
    return section


def generate_report(result: dict, template_path: Optional[str] = None) -> str:
    """Generate complete Markdown report."""
    mode = result.get("mode", "applicability")
    title = "补丁已合入差异报告" if mode == "merged-diff" else "补丁校验报告"

    # Header
    report = f"""# {title}

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **目标仓库**: `{result.get('repository', 'unknown')}`
> **目标分支**: `{result.get('branch', 'unknown')}`
> **模式**: `{mode}`

---

"""

    # Executive Summary
    report += generate_summary_section(result)
    report += "---\n\n"

    if mode == "applicability":
        variation_section = generate_variation_hunks_detail(result)
        if variation_section:
            report += variation_section
            report += "---\n\n"

        failed_section = generate_failed_hunks_detail(result)
        if failed_section:
            report += failed_section
            report += "---\n\n"

    # Detailed Results
    report += "## 详细结果\n\n"

    patches = result.get("patches", [])
    for i, patch in enumerate(patches, 1):
        report += generate_patch_section(patch, i)
        report += "---\n\n"

    # Footer
    if mode == "merged-diff":
        report += """## 术语说明

| 状态 | 含义 |
|------|------|
| ✅ 完全一致 (IDENTICAL) | 本地补丁与目标仓库已合入提交的 diff 完全一致 |
| ❌ 存在差异 (DIFFERENT) | 已找到对应提交，但 diff 内容存在缺失行、额外行或删除侧不一致 |
| ❓ 未匹配 (UNMATCHED) | 未找到对应本地补丁，或本地补丁未找到对应目标提交 |
| ⚠️ 匹配歧义 (AMBIGUOUS) | 本地补丁映射存在多个候选，无法安全自动判断 |

---

*报告由 patch-validator 自动生成*
"""
    else:
        report += """## 术语说明

| 状态 | 含义 |
|------|------|
| ✅ 无误差 (CLEAN) | Patch hunk 可以精确应用到目标代码，无需任何调整 |
| ⚠️ 存在误差 (VARIATION) | Patch hunk 可以应用，但上下文行有轻微偏移或空白变化 |
| ❌ 错误 (FAILED) | Patch hunk 无法应用，存在代码冲突或文件不存在等问题 |

---

*报告由 patch-validator 自动生成*
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown report from patch validation results"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input JSON file from validate_patches.py"
    )
    parser.add_argument(
        "--output", "-o",
        default="patch_validation_report.md",
        help="Output Markdown file (default: patch_validation_report.md)"
    )
    parser.add_argument(
        "--template",
        help="Optional template file for report customization"
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Load results
    print(f"Loading validation results from: {args.input}")
    result = load_validation_result(args.input)

    # Generate report
    print("Generating report...")
    report = generate_report(result, args.template)

    # Save report
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total patches: {result.get('total_patches', 0)}")
    if result.get("mode") == "merged-diff":
        print(f"  Local patch files: {result.get('local_patches_total', 0)}")
        print(f"  Matched target commits: {result.get('matched_target_commits', 0)}")
        print(f"  Unmatched target commits: {result.get('unmatched_target_commits', 0)}")
        print(f"  Ambiguous target commits: {result.get('ambiguous_target_commits', 0)}")
        print(f"  Identical: {result.get('identical_patches', 0)}")
        print(f"  Different: {result.get('different_patches', 0)}")
        print(f"  Unmatched: {result.get('unmatched_patches', 0)}")
        print(f"  Ambiguous: {result.get('ambiguous_patches', 0)}")
    else:
        print(f"  Total hunks: {result.get('total_hunks', 0)}")
        print(f"  Clean: {result.get('clean_hunks', 0)}")
        print(f"  Variation: {result.get('variation_hunks', 0)}")
        print(f"  Failed: {result.get('failed_hunks', 0)}")


if __name__ == "__main__":
    main()
