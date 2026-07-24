#!/usr/bin/env python3
"""
lookup.py — 查询单条 x86 intrinsic 在 references/avx2_to_sve.md 中的迁移条目。

用法:
    python lookup.py _mm256_shuffle_epi8
    python lookup.py _mm256_add_epi32

输出:
    若命中：该 intrinsic 的完整 markdown 章节（约 10-40 行）
    若未命中：相似名候选 + 提示去查 sve_intrinsics.md / 问用户

退出码:
    0 = 命中输出条目
    1 = 未命中但给出候选
    2 = 参数错误或参考表缺失
"""

from __future__ import annotations

import os
import re
import sys

# Windows 终端默认 cp936，强制 stdout/stderr UTF-8 避免中文乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "references", "avx2_to_sve.md"))


def load_entries(ref_path: str) -> dict[str, str]:
    """
    把 avx2_to_sve.md 按 '### `_mm...`' 标题切分成 dict[name] = section_text。
    """
    if not os.path.isfile(ref_path):
        print(f"[lookup] ERROR: reference table not found: {ref_path}", file=sys.stderr)
        sys.exit(2)

    with open(ref_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    entries: dict[str, str] = {}
    # 章节分隔：### `_mm... `\n  ...内容...  \n---
    pattern = re.compile(
        r"### `(_mm[A-Za-z0-9_]+)`\s*\n(.+?)(?=\n### `_mm|\n## |\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        body = m.group(2).rstrip()
        entries[name] = f"### `{name}`\n{body}"
    return entries


def fuzzy_candidates(query: str, names: list[str], limit: int = 8) -> list[str]:
    """简单子串/前缀候选。"""
    ql = query.lower()
    exact_prefix = [n for n in names if n.lower().startswith(ql)]
    substring   = [n for n in names if ql in n.lower() and n not in exact_prefix]
    # 去掉 _mm 前缀后再 substring 匹配（处理 _mm256_add vs _mm_add）
    stripped = ql.replace("_mm256_", "").replace("_mm512_", "").replace("_mm_", "")
    stripped_match = [n for n in names if stripped and stripped in n.lower()
                       and n not in exact_prefix and n not in substring]
    return (exact_prefix + substring + stripped_match)[:limit]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python lookup.py <intrinsic_name>", file=sys.stderr)
        print("Example: python lookup.py _mm256_shuffle_epi8", file=sys.stderr)
        return 2

    query = argv[1].strip()
    entries = load_entries(REF_PATH)

    if query in entries:
        print(entries[query])
        print()
        print("---")
        print(f"[lookup] 命中。如对应 SVE 候选仍不够清晰，可读 references/sve_intrinsics.md 全文搜对应 svname。")
        return 0

    candidates = fuzzy_candidates(query, list(entries.keys()))
    print(f"[lookup] 未找到 `{query}` 的条目。", file=sys.stderr)
    if candidates:
        print("候选（你是否想查这些？）：", file=sys.stderr)
        for c in candidates:
            print(f"  {c}", file=sys.stderr)
    else:
        print("没有相似名。", file=sys.stderr)
    print("", file=sys.stderr)
    print("建议：", file=sys.stderr)
    print("  1. 检查拼写", file=sys.stderr)
    print("  2. 如确实是冷门 intrinsic，按以下顺序处理：", file=sys.stderr)
    print("     a. 在 Intel Intrinsics Guide (intel.com) 查该 intrinsic 的 pseudo-code", file=sys.stderr)
    print("     b. 在 references/sve_intrinsics.md 按操作语义搜对应 sv 函数", file=sys.stderr)
    print("     c. 仍找不到 → 停下来问用户", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
