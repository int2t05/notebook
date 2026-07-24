#!/usr/bin/env bash
#
# Hyperscan ARM (AArch64) 平台编译脚本
# 用法:
#   ./build_arm.sh              # Release 编译 (默认 -j64)
#   ./build_arm.sh debug        # Debug 编译
#   ./build_arm.sh release 32   # Release, -j32
#

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
echo "  Hyperscan ARM (AArch64) 编译"
echo "============================================"
echo "  项目路径:   $PROJECT_ROOT"
echo "  并行线程:   $MAKE_JOBS"
echo "============================================"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

case "$MODE" in
    debug|Debug|DEBUG)
        log_info "执行 cmake 配置 (ARM, DEBUG)..."
        cmake "$PROJECT_ROOT" -DCMAKE_BUILD_TYPE=DEBUG
        ;;
    release|Release|RELEASE|*)
        log_info "执行 cmake 配置 (ARM, Release)..."
        cmake "$PROJECT_ROOT"
        ;;
esac

log_ok "cmake 配置成功"

log_info "开始编译 (make -j${MAKE_JOBS})..."
make -j"$MAKE_JOBS"
log_ok "编译成功"

echo ""
log_info "构建产物位于: $BUILD_DIR/bin/"
