#!/usr/bin/env bash
#
# === Hyperscan 性能测试脚本 (hsbench) ===
#
# 这个脚本用来测试 Hyperscan 在你机器上的匹配性能。
# 它会编译你的规则集，然后用它扫描语料，最后告诉你吞吐量 (Mbit/s)。
#
# ===== 用法 =====
#
#   ./benchmark.sh <规则集> <语料库> [mode] [迭代次数]
#
#   参数说明:
#     <规则集>      规则文件路径, 一行一条正则, 格式: ID:/pattern/flags
#                   例如本项目自带的: ../assets/fdr_100.literals
#     <语料库>      用来测试的文本数据, 什么格式都行, 越大越准
#                   一般是一个 .db 文件, 比如 alexa200.db
#     [mode]        选填, N=Block模式, V=Vectored模式, 不填默认=Streaming
#     [迭代次数]     选填, 默认跑 2 遍, 遍数越多结果越稳定但越慢
#
#   示例:
#     ./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db
#     ./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db N       # block
#     ./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db V 10    # vectored, 10 遍
#
# ===== hsbench 是什么 =====
#
#   hsbench 是 Hyperscan 自带的性能测试工具, 源码在 tools/hsbench/main.cpp。
#   它负责三件事:
#     1. 编译规则集 → 生成 Hyperscan 数据库 (hs_database)
#     2. 用数据库扫描语料 → 统计匹配数
#     3. 计算吞吐量 → 输出 Mean/Max throughput (Mbit/s)
#
#   实际的命令行格式:
#     hsbench -e <规则集> -c <语料库> -n <遍数> [-N | -V]
#       -e  指定规则文件
#       -c  指定语料文件
#       -n  重复扫描次数
#       -N  Block 模式 (默认是 Streaming)
#       -V  Vectored 模式
#
# ===== hsbench 从哪来 =====
#
#   hsbench 是编译 Hyperscan 项目时一起编出来的, 不是系统自带的命令。
#   编译好之后它在这里:  <项目根目录>/build/bin/hsbench
#
#   如果你还没有编译, 用本目录下的 build 脚本先编译:
#     ARM 机器:  ./build_arm.sh
#     x86 机器:  ./build_x86.sh
#
#   编译完后检查 hsbench 是否存在:
#     ls -l ../../../build/bin/hsbench
#
#   如果还是找不到, 说明编译没有开启 BUILD_EXAMPLES (默认是 ON 的),
#   检查 CMakeLists.txt 里 BUILD_EXAMPLES 是否被关掉了。
#
# ===== 本脚本做了什么 =====
#
#   1. 自动找到 hsbench (从脚本所在位置推算项目根目录)
#   2. 校验 hsbench、规则集、语料库 三个文件都在
#   3. 拼接 hsbench 命令并执行
#   4. 从输出里提取 Mean throughput、扫描时间、匹配数等关键指标
#   5. 打印结果
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HSBENCH_BIN="$PROJECT_ROOT/build/bin/hsbench"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---- 参数解析 ----
if [ $# -lt 2 ]; then
    echo "用法: $0 <规则集> <语料库> [mode] [迭代次数]"
    echo ""
    echo "  <规则集>     .literals 规则集文件路径"
    echo "  <语料库>     测试语料文件 (.db)"
    echo "  [mode]       N=Block 模式, V=Vectored 模式, 默认=Streaming"
    echo "  [迭代次数]    默认 2"
    echo ""
    echo "示例:"
    echo "  $0 ../assets/fdr_100.literals /data/corpus.db"
    echo "  $0 ../assets/fdr_100.literals /data/corpus.db N      # block"
    echo "  $0 ../assets/fdr_100.literals /data/corpus.db V 10   # vectored, 10 次"
    exit 1
fi

RULES_FILE="$1"
CORPUS_FILE="$2"
MODE="${3}"
ITERATIONS="${4:-2}"

# ---- 校验 ----
if [ ! -f "$HSBENCH_BIN" ]; then
    log_error "找不到 hsbench !!"
    log_error "期望路径: $HSBENCH_BIN"
    echo ""
    echo "  hsbench 是编译 Hyperscan 时生成的, 不是系统命令。"
    echo "  你需要先编译项目才会产生这个文件。"
    echo ""
    echo "  解决方法:"
    echo "    1. cd $(dirname "$0")"
    echo "    2. ARM 机器执行:  ./build_arm.sh"
    echo "    3. x86 机器执行:  ./build_x86.sh"
    echo "    4. 编译完成后确认文件存在:"
    echo "       ls -l $HSBENCH_BIN"
    echo ""
    exit 1
fi

if [ ! -f "$RULES_FILE" ]; then
    log_error "规则集文件不存在: $RULES_FILE"
    exit 1
fi

if [ ! -f "$CORPUS_FILE" ]; then
    log_error "语料文件不存在: $CORPUS_FILE"
    exit 1
fi

# ---- 构建命令 ----
HSBENCH_CMD="$HSBENCH_BIN -e $RULES_FILE -c $CORPUS_FILE -n $ITERATIONS"

case "$MODE" in
    N|n) HSBENCH_CMD="$HSBENCH_CMD -N"; MODE_NAME="Block" ;;
    V|v) HSBENCH_CMD="$HSBENCH_CMD -V"; MODE_NAME="Vectored" ;;
    *)   MODE_NAME="Streaming (默认)" ;;
esac

echo "============================================"
echo "  Hyperscan 性能测试 (hsbench)"
echo "============================================"
echo "  hsbench:    $HSBENCH_BIN"
echo "  规则集:     $RULES_FILE"
echo "  语料:       $CORPUS_FILE"
echo "  模式:       $MODE_NAME"
echo "  迭代次数:   $ITERATIONS"
echo "  命令:       $HSBENCH_CMD"
echo "============================================"
echo ""

# ---- 运行 ----
OUTPUT_FILE=$(mktemp)
trap 'rm -f "$OUTPUT_FILE"' EXIT

$HSBENCH_CMD 2>&1 | tee "$OUTPUT_FILE"
HSBENCH_EXIT=${PIPESTATUS[0]}

if [ $HSBENCH_EXIT -ne 0 ]; then
    log_error "hsbench 执行失败 (exit code: $HSBENCH_EXIT)"
    exit 1
fi

# ---- 解析结果 ----
echo ""
echo "============================================"
echo "  结果"
echo "============================================"

MEAN_TP=$(grep -i "Mean throughput.*overall" "$OUTPUT_FILE" | grep -oP '[\d,]+\.?\d*' | tail -1)
MATCHES=$(grep -i "Matches per iteration" "$OUTPUT_FILE" | grep -oP '[\d,]+' | head -1)
CORPUS_SIZE=$(grep -i "Corpus size" "$OUTPUT_FILE" | head -1 | sed 's/.*Corpus size: *//')
SCAN_TIME=$(grep -i "Time spent scanning" "$OUTPUT_FILE" | sed 's/.*Time spent scanning: *//')
MAX_TP=$(grep -i "Max throughput.*per core" "$OUTPUT_FILE" | grep -oP '[\d,]+\.?\d*' | tail -1)

echo ""
echo "  扫描耗时:        $SCAN_TIME"
echo "  语料大小:        $CORPUS_SIZE"
echo "  匹配数/迭代:     $MATCHES"
[ -n "$MEAN_TP" ] && echo "  Mean throughput:  ${MEAN_TP} Mbit/s"
[ -n "$MAX_TP" ]  && echo "  Max  throughput:  ${MAX_TP} Mbit/s"

echo ""
log_ok "测试完成"
