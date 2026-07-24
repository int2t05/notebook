#!/usr/bin/env python3
"""
scan_file.py — 扫描 velox/gluten C++ 源文件中的 x86 SIMD intrinsics 与类型，
输出按 unique intrinsic 名汇总的清单，标注高风险类。

用法:
    python scan_file.py <path_to_file>

输出（stdout）:
    - 头文件 #include 列表
    - 待替换类型（__m128i, __m256i 等）按出现次数排序
    - 待替换 intrinsic 按 unique 名汇总：名 + 出现次数 + 行号列表 + 高风险标
    - 推荐建立的 TaskCreate 任务数

退出码:
    0 = 扫描完成（无论是否找到）
    2 = 文件读不到
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

# Windows 终端默认 cp936，强制 stdout/stderr UTF-8 避免中文乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


HEADER_PATTERN = re.compile(
    r'^\s*#include\s+[<"]'
    r'(immintrin|emmintrin|xmmintrin|smmintrin|tmmintrin|pmmintrin|nmmintrin'
    r'|avx2intrin|avxintrin|wmmintrin|f16cintrin|x86intrin|mmintrin)\.h'
    r'[>"]'
)

TYPE_PATTERN = re.compile(r'\b(__m128[id]?|__m256[id]?|__m512[id]?|__mmask\d+)\b')

INTRINSIC_PATTERN = re.compile(r'\b(_mm(?:256|512)?_[A-Za-z0-9_]+)\s*\(')

HIGH_RISK_SUBSTR = (
    "shuffle", "permute", "perm2", "permutex",
    "blend", "blendv",
    "pack", "unpack",
    "movemask",
    "alignr",
    "extract", "insert",
    "gather", "scatter",
    "broadcast",
    "maskload", "maskstore",
    "cvt",
)


def is_high_risk(name: str) -> bool:
    nl = name.lower()
    return any(s in nl for s in HIGH_RISK_SUBSTR)


def scan(path: str) -> int:
    if not os.path.isfile(path):
        print(f"[scan_file] ERROR: file not found: {path}", file=sys.stderr)
        return 2

    headers: list[tuple[int, str]] = []
    types: dict[str, list[int]] = defaultdict(list)
    intrins: dict[str, list[int]] = defaultdict(list)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            if HEADER_PATTERN.search(line):
                headers.append((lineno, line.rstrip()))
            for m in TYPE_PATTERN.finditer(line):
                types[m.group(1)].append(lineno)
            for m in INTRINSIC_PATTERN.finditer(line):
                intrins[m.group(1)].append(lineno)

    try:
        rel = os.path.relpath(path)
    except ValueError:
        # 跨盘符（如 cwd 在 C: 而文件在 D:）— relpath 不可计算
        rel = os.path.abspath(path)
    print(f"# scan_file.py — {rel}")
    print()

    if headers:
        print(f"## x86 头文件（{len(headers)} 处，需删除并加 <arm_sve.h>）")
        for ln, txt in headers:
            print(f"  line {ln}: {txt}")
    else:
        print("## x86 头文件: 无")
    print()

    if types:
        print(f"## x86 向量类型（{sum(len(v) for v in types.values())} 处，需改成 svint*_t / svuint*_t / svfloat*_t）")
        for name in sorted(types.keys()):
            lines = types[name]
            preview = ",".join(str(x) for x in lines[:10])
            if len(lines) > 10:
                preview += f",...+{len(lines) - 10}"
            print(f"  {name:<12} x{len(lines):<4} lines: [{preview}]")
    else:
        print("## x86 向量类型: 无")
    print()

    if not intrins:
        print("## intrinsic 调用: 无（无需翻译）")
        print()
        print("# 总结")
        print("  unique intrinsic: 0")
        print("  call sites: 0")
        print("  推荐 TaskCreate 任务数: 0")
        return 0

    total_calls = sum(len(v) for v in intrins.values())
    unique = len(intrins)
    high_risk_names = sorted([n for n in intrins if is_high_risk(n)])
    normal_names = sorted([n for n in intrins if not is_high_risk(n)])

    print(f"## intrinsic 调用（{unique} unique / {total_calls} call sites）")
    print()
    if high_risk_names:
        print(f"### [HIGH-RISK] 必须先 lookup.py 查表（{len(high_risk_names)} 条）")
        for name in high_risk_names:
            lines = intrins[name]
            preview = ",".join(str(x) for x in lines[:10])
            if len(lines) > 10:
                preview += f",...+{len(lines) - 10}"
            print(f"  {name:<35} x{len(lines):<3} lines: [{preview}]")
        print()
    if normal_names:
        print(f"### [normal] 可先查 SKILL.md 速查表（{len(normal_names)} 条）")
        for name in normal_names:
            lines = intrins[name]
            preview = ",".join(str(x) for x in lines[:10])
            if len(lines) > 10:
                preview += f",...+{len(lines) - 10}"
            tag = ""
            print(f"  {name:<35} x{len(lines):<3} lines: [{preview}]{tag}")
        print()

    print("# 总结")
    print(f"  unique intrinsic: {unique}（HIGH-RISK: {len(high_risk_names)}）")
    print(f"  call sites: {total_calls}")
    print(f"  推荐 TaskCreate 任务数: {unique}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scan_file.py <abs_or_rel_path_to_cpp_or_h_file>", file=sys.stderr)
        return 2
    return scan(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
