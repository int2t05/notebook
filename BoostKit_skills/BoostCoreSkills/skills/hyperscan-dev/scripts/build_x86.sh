#!/usr/bin/env bash
#
# Hyperscan x86-64 平台编译脚本
# 用法:
#   ./build_x86.sh              # Release 编译 (默认 -j64)
#   ./build_x86.sh debug        # Debug 编译
#   ./build_x86.sh release 32   # Release, -j32
#
# Debug 模式通过 -D__X86_64__ 宏模拟 x86 编译环境（在 ARM 机器上交叉验证 x86 代码路径）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
MAKE_JOBS="${2:-64}"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

MODE="${1:-release}"
echo "============================================"
echo "  Hyperscan x86-64 编译"
echo "============================================"
echo "  项目路径:   $PROJECT_ROOT"
echo "  并行线程:   $MAKE_JOBS"
echo "============================================"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

case "$MODE" in
    debug|Debug|DEBUG)
        log_info "执行 cmake 配置 (x86-64, DEBUG)..."
        cmake "$PROJECT_ROOT" \
            -DCMAKE_BUILD_TYPE=DEBUG \
            -DCMAKE_C_FLAGS="-D__X86_64__" \
            -DCMAKE_CXX_FLAGS="-D__X86_64__"
        ;;
    release|Release|RELEASE|*)
        log_info "执行 cmake 配置 (x86-64, Release)..."
        cmake "$PROJECT_ROOT"
        ;;
esac

log_ok "cmake 配置成功"

log_info "开始编译 (make -j${MAKE_JOBS})..."
make -j"$MAKE_JOBS"
log_ok "编译成功"

echo ""
log_info "构建产物位于: $BUILD_DIR/bin/"
