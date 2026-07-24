#!/usr/bin/env python
#
# === Hyperscan 语料生成器 ===
#
# 包装 Hyperscan 自带的 CorpusBuilder.py, 生成匹配比例可控的测试语料。
#
# "匹配比例" 是指: 整个语料中, 有多少比例的数据块包含至少一条规则能命中的内容。
# 比如 --match-ratio 30 表示 30% 的数据块会命中规则, 70% 是纯噪音。
#
# ===== 用法 =====
#
#   python gen_corpus.py -r <规则集> -o <输出.db> [-s 大小] [-m 匹配比例%] [-c 块大小] [--seed 随机种子]
#
#   参数:
#     -r, --rules       规则集文件 (.literals), 必填
#     -o, --output      输出语料文件 (.db), 必填
#     -s, --size        语料总大小, 支持单位 K/M/G, 如 100M (默认: 10M)
#     -m, --match-ratio 匹配数据块的百分比 0-100 (默认: 50)
#     -c, --chunk-size  每块字节数 (默认: 4096)
#     --seed            随机种子, 保证可复现 (默认: 42)
#
#   示例:
#     # 生成 100MB 语料, 50% 命中率
#     python gen_corpus.py -r fdr_100.literals -o test.db -s 100M -m 50
#
#     # 生成 10MB 语料, 10% 命中率 (稀疏匹配场景)
#     python gen_corpus.py -r fdr_100.literals -o sparse.db -m 10
#
#     # 生成 1GB 语料, 90% 命中率 (密集匹配压力测试)
#     python gen_corpus.py -r full_rose_mixed.literals -o dense.db -s 1G -m 90
#
# ===== 数据库结构 =====
#
# 生成的 .db 文件是一个 SQLite 数据库, 表结构如下:
#
#   CREATE TABLE chunk (
#       id        integer primary key,   -- 块唯一 ID, 从 0 递增
#       stream_id integer not null,      -- 流 ID, 本脚本固定为 0 (单流)
#       data      blob                   -- 块数据, 二进制字节串
#   );
#   CREATE INDEX chunk_stream_id_idx on chunk(stream_id);


import sys
import os
import re
import random
import argparse

# ---- 把 CorpusBuilder 加入 sys.path ----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# assets → hyperscan-dev → skills → .claude → 项目根 → tools/hsbench/scripts
CORPUSBUILDER_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "..", "..", "tools", "hsbench", "scripts")
)
sys.path.insert(0, CORPUSBUILDER_DIR)

try:
    from CorpusBuilder import CorpusBuilder
except ImportError:
    print("ERROR: 找不到 CorpusBuilder.py !")
    print("期望路径: %s" % CORPUSBUILDER_DIR)
    print("")
    print("CorpusBuilder 是 Hyperscan 自带的语料生成模块, 位于:")
    print("  <项目根>/tools/hsbench/scripts/CorpusBuilder.py")
    print("请确认该文件存在。")
    sys.exit(1)


def parse_size(s):
    """把 100M / 1G / 500K 转成字节数"""
    s = s.strip().upper()
    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3}
    m = re.match(r"^(\d+)([KMG]?)$", s)
    if not m:
        raise ValueError("无法解析大小: %s (如 100M, 1G, 500K)" % s)
    num = int(m.group(1))
    unit = m.group(2)
    return num * multipliers.get(unit, 1)


def parse_rules(filepath):
    """从 .literals 文件中提取所有字面量模式字符串"""
    patterns = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 格式: ID:/pattern/flags
            m = re.match(r"^\d+:(/.+/)(.*)$", line)
            if not m:
                continue
            raw = m.group(1)  # "/pattern/"
            # 去掉首尾的 /
            pattern = raw[1:-1]
            if pattern:
                patterns.append(pattern)
    return patterns


def generate_match_chunk(patterns, chunk_size, rng):
    """
    生成一个包含规则匹配内容的数据块。
    策略: 随机选一条规则, 把它的字面量字符串嵌在块中某个位置, 其余填充随机可见字符。
    """
    buf = bytearray(chunk_size)
    # 先填充随机可打印字符 (0x20 ~ 0x7e)
    for i in range(chunk_size):
        buf[i] = rng.randint(0x20, 0x7E)

    pattern = rng.choice(patterns)
    plen = len(pattern)
    if plen <= chunk_size:
        # 随机选一个位置嵌入匹配字符串
        offset = rng.randint(0, chunk_size - plen)
        for i, ch in enumerate(pattern):
            buf[offset + i] = ord(ch)
    return bytes(buf)


def generate_noise_chunk(chunk_size, rng):
    """
    生成纯噪音数据块。使用可见字符, 不包含任何规则内容。
    注意: 这只能保证不包含我们已知的规则字面量, 但不排除随机产生的巧合匹配。
    """
    buf = bytearray(chunk_size)
    for i in range(chunk_size):
        buf[i] = rng.randint(0x20, 0x7E)
    return bytes(buf)


def main():
    parser = argparse.ArgumentParser(
        description="Hyperscan 语料生成器 — 生成匹配比例可控的测试语料 (.db)",
    )
    parser.add_argument("-r", "--rules", required=True,
                        help="规则集文件路径 (.literals)")
    parser.add_argument("-o", "--output", required=True,
                        help="输出语料文件路径 (.db)")
    parser.add_argument("-s", "--size", default="10M",
                        help="语料总大小, 如 100M / 1G / 500K (默认: 10M)")
    parser.add_argument("-m", "--match-ratio", type=float, default=50,
                        help="匹配数据块的百分比 0-100 (默认: 50)")
    parser.add_argument("-c", "--chunk-size", type=int, default=4096,
                        help="每块字节数 (默认: 4096)")
    parser.add_argument("--seed", type=int, default=42,
                        help="随机种子 (默认: 42)")

    args = parser.parse_args()

    # ---- 校验参数 ----
    if args.match_ratio < 0 or args.match_ratio > 100:
        print("ERROR: --match-ratio 必须在 0 到 100 之间")
        sys.exit(1)

    if not os.path.isfile(args.rules):
        print("ERROR: 规则集文件不存在: %s" % args.rules)
        sys.exit(1)

    if os.path.exists(args.output):
        print("ERROR: 输出文件已存在: %s (请手动删除或换个名字)")
        sys.exit(1)

    total_bytes = parse_size(args.size)
    chunk_size = args.chunk_size
    match_ratio = args.match_ratio / 100.0

    total_chunks = total_bytes // chunk_size
    if total_chunks == 0:
        print("ERROR: 语料总大小 (%d bytes) 小于块大小 (%d bytes)" % (total_bytes, chunk_size))
        sys.exit(1)

    match_chunks = int(total_chunks * match_ratio)
    noise_chunks = total_chunks - match_chunks

    # ---- 解析规则 ----
    patterns = parse_rules(args.rules)
    if not patterns:
        print("ERROR: 规则集中没有可用的字面量模式")
        sys.exit(1)

    print("============================================")
    print("  Hyperscan 语料生成器")
    print("============================================")
    print("  规则集:       %s" % args.rules)
    print("  提取规则数:   %d 条" % len(patterns))
    print("  输出文件:     %s" % args.output)
    print("  目标大小:     %s (%s bytes)" % (args.size, f"{total_bytes:,}"))
    print("  块大小:       %d bytes" % chunk_size)
    print("  总块数:       %d" % total_chunks)
    print("  匹配块:       %d (%.1f%%)" % (match_chunks, args.match_ratio))
    print("  噪音块:       %d (%.1f%%)" % (noise_chunks, 100 - args.match_ratio))
    print("  随机种子:     %d" % args.seed)
    print("============================================")
    print("")

    rng = random.Random(args.seed)

    # ---- 生成块索引: 打乱匹配块和噪音块的顺序 ----
    chunk_types = [True] * match_chunks + [False] * noise_chunks
    rng.shuffle(chunk_types)

    # ---- 构建语料 ----
    print("正在生成语料...")
    builder = CorpusBuilder(args.output)
    stream_id = 0  # 所有块属于同一个 stream

    for i, is_match in enumerate(chunk_types):
        if is_match:
            data = generate_match_chunk(patterns, chunk_size, rng)
        else:
            data = generate_noise_chunk(chunk_size, rng)
        builder.add_chunk(stream_id, data)

        if (i + 1) % max(1, total_chunks // 10) == 0:
            pct = (i + 1) * 100 // total_chunks
            print("  进度: %d/%d 块 (%d%%)" % (i + 1, total_chunks, pct))

    builder.finish()

    actual_size = os.path.getsize(args.output)
    print("")
    print("============================================")
    print("  语料生成完成!")
    print("  文件:   %s" % args.output)
    print("  大小:   %s bytes" % f"{actual_size:,}")
    print("  匹配率: %.1f%% (约 %d 个匹配块)" % (args.match_ratio, match_chunks))
    print("")
    print("  hsbench 使用方式:")
    print("    hsbench -e %s -c %s -n 10 [-N|-V]" % (args.rules, args.output))
    print("============================================")


if __name__ == "__main__":
    main()
