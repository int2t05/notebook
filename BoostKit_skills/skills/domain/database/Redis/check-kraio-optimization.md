---
name: "check-kraio-optimization"
description: "检查Redis进程是否引用了libkraio.so库，确认Redis是否进行了鲲鹏网络异步优化(KRAIO)。当用户询问 Redis 是否启用了网络异步优化、KRAIO/KBAIO 加速是否生效时调用此 skill。"
---

# Check Redis KRAIO Network Async Optimization

此 skill 用于检查 Redis 进程是否引用了 `libkraio.so` 库，确认 Redis 是否进行了鲲鹏 BoostKit 的网络异步优化 (KRAIO, Kunpeng Redis Async I/O)。

KRAIO 是鲲鹏 BoostKit 数据库使能套件中的 Redis 网络异步优化特性，通过将 Redis 中网络 IO 操作交由 KRAIO 异步批量执行，减少系统调用和上下文交换，实现 Redis 业务无阻塞执行，从而提高 Redis 吞吐量。

> **重要说明**：
> - KRAIO 的实现依赖动态链接库 **`libkraio.so`**，Redis 进程若引用此库则表明启用了网络异步优化
> - 早期版本称为 **KBAIO** (Kunpeng Batch Async I/O)，对应库为 **`libkbaio.so`**，本 skill 同时检查两种库
> - KRAIO 特性支持 Redis 6.0.20 和 Redis 7.0.15 版本
> - KRAIO 为鲲鹏 (aarch64) 专属特性

## 检测方法

按优先级依次尝试以下方法，综合判断 KRAIO 网络异步优化是否使能：

### 方法一：检查 Redis 进程是否加载 libkraio.so / libkbaio.so（核心检测）

```bash
REDIS_PIDS=$(pgrep -d',' redis-server)

if [ -z "$REDIS_PIDS" ]; then
    echo "未找到 Redis 进程"
    exit 1
fi

echo "=== 检查 Redis 进程是否加载 libkraio.so / libkbaio.so ==="

for PID in $(echo "$REDIS_PIDS" | tr ',' ' '); do
    echo ""
    echo "--- Redis 进程 PID: $PID ---"
    echo "进程名: $(cat /proc/$PID/comm 2>/dev/null)"
    echo "命令行: $(cat /proc/$PID/cmdline 2>/dev/null | tr '\0' ' ')"

    KRAIO_MAPS=$(cat /proc/$PID/maps 2>/dev/null | grep -E 'libkraio\.so|libkbaio\.so')
    if [ -n "$KRAIO_MAPS" ]; then
        echo "✓ Redis 进程已加载异步 IO 库:"
        echo "$KRAIO_MAPS"
        if echo "$KRAIO_MAPS" | grep -q 'libkraio\.so'; then
            echo "  -> KRAIO (新版) 网络异步优化已启用"
        fi
        if echo "$KRAIO_MAPS" | grep -q 'libkbaio\.so'; then
            echo "  -> KBAIO (旧版) 网络异步优化已启用"
        fi
    else
        echo "✗ Redis 进程未加载 libkraio.so / libkbaio.so"
    fi
done
```

也可通过 `lsof` 检查：

```bash
REDIS_PIDS=$(pgrep redis-server)

if [ -z "$REDIS_PIDS" ]; then
    echo "未找到 Redis 进程"
    exit 1
fi

for PID in $REDIS_PIDS; do
    echo "--- Redis 进程 PID: $PID ---"
    lsof -p $PID 2>/dev/null | grep -E 'libkraio\.so|libkbaio\.so'
    if [ $? -eq 0 ]; then
        echo "✓ Redis 进程已加载异步 IO 库"
    else
        echo "✗ Redis 进程未加载异步 IO 库"
    fi
done
```

或通过 `pmap` 检查：

```bash
REDIS_PIDS=$(pgrep redis-server)

for PID in $REDIS_PIDS; do
    echo "--- Redis 进程 PID: $PID ---"
    pmap -x $PID 2>/dev/null | grep -E 'libkraio\.so|libkbaio\.so'
    if [ $? -eq 0 ]; then
        echo "✓ Redis 进程已加载异步 IO 库"
    else
        echo "✗ Redis 进程未加载异步 IO 库"
    fi
done
```

### 方法二：检查 Redis 启动方式是否配置了 LD_PRELOAD

KRAIO 库通常通过 `LD_PRELOAD` 方式注入 Redis 进程：

```bash
REDIS_PIDS=$(pgrep redis-server)

for PID in $REDIS_PIDS; do
    echo "--- Redis 进程 PID: $PID ---"

    LD_PRELOAD_VAL=$(cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep '^LD_PRELOAD=')
    if [ -n "$LD_PRELOAD_VAL" ]; then
        echo "LD_PRELOAD 配置: $LD_PRELOAD_VAL"
        if echo "$LD_PRELOAD_VAL" | grep -qE 'libkraio\.so|libkbaio\.so'; then
            echo "✓ LD_PRELOAD 已配置异步 IO 库"
        else
            echo "✗ LD_PRELOAD 未配置异步 IO 库"
        fi
    else
        echo "✗ LD_PRELOAD 未设置"
    fi
done
```

检查 Redis 服务配置文件中是否配置了 LD_PRELOAD：

```bash
REDIS_SERVICE_FILES="/usr/lib/systemd/system/redis-server.service
/usr/lib/systemd/system/redis.service
/etc/systemd/system/redis-server.service
/etc/systemd/system/redis.service"

for svc in $REDIS_SERVICE_FILES; do
    if [ -f "$svc" ]; then
        echo "找到 Redis 服务文件: $svc"
        grep -i 'LD_PRELOAD\|Environment\|kraio\|kbaio' "$svc" 2>/dev/null
    fi
done
```

### 方法三：检查系统中 libkraio.so / libkbaio.so 文件是否存在

```bash
echo "=== 检查系统中是否存在 libkraio.so / libkbaio.so ==="

KRAIO_LIB=$(find /usr/lib64 /lib64 /usr/lib /lib /usr/local/lib64 /usr/local/lib -name "libkraio.so*" -o -name "libkbaio.so*" 2>/dev/null)

if [ -n "$KRAIO_LIB" ]; then
    echo "✓ 找到异步 IO 库文件:"
    echo "$KRAIO_LIB"
    echo ""
    echo "库文件详情:"
    for lib in $KRAIO_LIB; do
        ls -la "$lib"
        file "$lib"
    done
else
    echo "✗ 未找到 libkraio.so / libkbaio.so 文件"
fi
```

也可通过 `ldconfig` 检查：

```bash
echo "=== 通过 ldconfig 检查 ==="
ldconfig -p 2>/dev/null | grep -E 'libkraio\.so|libkbaio\.so'
```

### 方法四：检查 BoostKit Redis 软件包是否安装

KRAIO 作为 BoostKit 数据库使能套件的一部分交付：

```bash
echo "=== 检查 BoostKit Redis 软件包 ==="

BOOSTKIT_PKG=$(rpm -qa 2>/dev/null | grep -iE 'boostkit.*redis|kraio|kbaio')

if [ -z "$BOOSTKIT_PKG" ]; then
    BOOSTKIT_PKG=$(dpkg -l 2>/dev/null | grep -iE 'boostkit.*redis|kraio|kbaio')
fi

if [ -n "$BOOSTKIT_PKG" ]; then
    echo "✓ BoostKit Redis 相关软件包已安装:"
    echo "$BOOSTKIT_PKG"
else
    echo "✗ BoostKit Redis 相关软件包未安装"
fi
```

检查所有 BoostKit 相关软件包：

```bash
rpm -qa 2>/dev/null | grep -i boostkit
```

### 方法五：检查 Redis 版本是否支持 KRAIO

KRAIO 特性支持特定版本的 Redis：

```bash
REDIS_PIDS=$(pgrep redis-server)

for PID in $REDIS_PIDS; do
    echo "--- Redis 进程 PID: $PID ---"
    REDIS_BIN=$(readlink -f /proc/$PID/exe 2>/dev/null)
    if [ -n "$REDIS_BIN" ]; then
        REDIS_VERSION=$($REDIS_BIN --version 2>/dev/null || redis-server --version 2>/dev/null)
        echo "Redis 版本: $REDIS_VERSION"

        if echo "$REDIS_VERSION" | grep -qE 'v=6\.0\.|v=7\.0\.'; then
            echo "✓ Redis 版本可能支持 KRAIO 网络异步优化"
        else
            echo "⚠ KRAIO 网络异步优化支持 Redis 6.0.20 和 Redis 7.0.15 版本"
        fi
    fi
done
```

也可通过 `redis-cli` 查询：

```bash
redis-cli INFO server 2>/dev/null | grep redis_version
```

### 方法六：检查系统架构

KRAIO 为鲲鹏 (aarch64) 专属特性：

```bash
ARCH=$(uname -m)
echo "系统架构: $ARCH"

if [ "$ARCH" = "aarch64" ]; then
    echo "✓ 当前为鲲鹏 (aarch64) 平台，支持 KRAIO 特性"
else
    echo "✗ 当前非鲲鹏平台，KRAIO 特性不可用"
fi
```

### 方法七：检查 Redis 运行时网络 IO 行为（运行时验证）

KRAIO 使能后，Redis 的网络 IO 操作会通过异步批量方式执行，可通过 `strace` 观察系统调用模式：

```bash
REDIS_PID=$(pgrep -o redis-server)

if [ -z "$REDIS_PID" ]; then
    echo "未找到 Redis 进程"
    exit 1
fi

echo "=== 抓取 Redis 进程 ($REDIS_PID) 的系统调用 (5秒) ==="
echo "KRAIO 使能后，应观察到批量化的网络 IO 操作（如 io_submit/io_getevents 或聚合的 writev/sendmsg）"

timeout 5 strace -p $REDIS_PID -e trace=writev,sendmsg,recvmsg,io_submit,io_getevents,read,write -c 2>&1 | head -30
```

## 综合判断脚本

```bash
#!/bin/bash

RESULT=""
REDIS_PIDS=$(pgrep redis-server)

echo "========================================="
echo "KRAIO 网络异步优化使能状态检查"
echo "========================================="

echo ""
echo "[1] 检查系统架构 ..."
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    echo "    ✓ 鲲鹏 (aarch64) 平台"
    RESULT="${RESULT}ARCH_OK,"
else
    echo "    ✗ 非 aarch64 平台 ($ARCH)，KRAIO 不可用"
    RESULT="${RESULT}ARCH_FAIL,"
fi

echo ""
echo "[2] 检查 Redis 进程是否加载异步 IO 库 ..."
if [ -n "$REDIS_PIDS" ]; then
    KRAIO_LOADED=0
    for PID in $REDIS_PIDS; do
        if cat /proc/$PID/maps 2>/dev/null | grep -qE 'libkraio\.so|libkbaio\.so'; then
            KRAIO_LOADED=1
            KRAIO_TYPE=$(cat /proc/$PID/maps 2>/dev/null | grep -oE 'libk(r|b)aio\.so[^ ]*' | head -1)
            echo "    ✓ Redis 进程 ($PID) 已加载 $KRAIO_TYPE"
        fi
    done
    if [ "$KRAIO_LOADED" -eq 1 ]; then
        RESULT="${RESULT}KRAIO_OK,"
    else
        echo "    ✗ Redis 进程未加载 libkraio.so / libkbaio.so"
        RESULT="${RESULT}KRAIO_FAIL,"
    fi
else
    echo "    ✗ 未找到 Redis 进程"
    RESULT="${RESULT}NO_REDIS,"
fi

echo ""
echo "[3] 检查 LD_PRELOAD 配置 ..."
LD_PRELOAD_SET=0
if [ -n "$REDIS_PIDS" ]; then
    for PID in $REDIS_PIDS; do
        LD_VAL=$(cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep '^LD_PRELOAD=')
        if echo "$LD_VAL" | grep -qE 'libkraio\.so|libkbaio\.so'; then
            echo "    ✓ Redis 进程 ($PID) LD_PRELOAD 已配置异步 IO 库"
            LD_PRELOAD_SET=1
        fi
    done
fi
if [ "$LD_PRELOAD_SET" -eq 1 ]; then
    RESULT="${RESULT}PRELOAD_OK,"
else
    echo "    ✗ LD_PRELOAD 未配置异步 IO 库"
    RESULT="${RESULT}PRELOAD_FAIL,"
fi

echo ""
echo "[4] 检查异步 IO 库文件 ..."
KRAIO_LIB=$(find /usr/lib64 /lib64 /usr/lib /lib /usr/local/lib64 /usr/local/lib -name "libkraio.so*" -o -name "libkbaio.so*" 2>/dev/null)
if [ -n "$KRAIO_LIB" ]; then
    echo "    ✓ 异步 IO 库文件存在:"
    echo "$KRAIO_LIB" | sed 's/^/      /'
    RESULT="${RESULT}LIB_OK,"
else
    echo "    ✗ 异步 IO 库文件不存在"
    RESULT="${RESULT}LIB_FAIL,"
fi

echo ""
echo "[5] 检查 BoostKit Redis 软件包 ..."
PKG_INSTALLED=$(rpm -qa 2>/dev/null | grep -cE 'boostkit.*redis|kraio|kbaio')
if [ "$PKG_INSTALLED" -gt 0 ]; then
    echo "    ✓ BoostKit Redis 相关软件包已安装"
    rpm -qa 2>/dev/null | grep -iE 'boostkit.*redis|kraio|kbaio' | sed 's/^/      /'
    RESULT="${RESULT}PKG_OK,"
else
    echo "    ✗ BoostKit Redis 相关软件包未安装"
    RESULT="${RESULT}PKG_FAIL,"
fi

echo ""
echo "========================================="
echo "检查结果汇总: $RESULT"
echo "========================================="

if echo "$RESULT" | grep -q "KRAIO_OK"; then
    echo "结论: Redis 网络异步优化 (KRAIO) 已使能"
    if echo "$RESULT" | grep -q "libkraio"; then
        echo "  使用版本: KRAIO (新版)"
    elif echo "$RESULT" | grep -q "libkbaio"; then
        echo "  使用版本: KBAIO (旧版)"
    fi
elif echo "$RESULT" | grep -q "LIB_OK" && echo "$RESULT" | grep -q "PKG_OK"; then
    echo "结论: KRAIO 库文件和软件包已就绪，但 Redis 进程未加载异步 IO 库"
    echo "建议: 按以下步骤使能 KRAIO 网络异步优化："
    echo "  1. 停止 Redis 服务"
    echo "  2. 配置 LD_PRELOAD 加载 libkraio.so"
    echo "     export LD_PRELOAD=/usr/lib64/libkraio.so"
    echo "  3. 重新启动 Redis"
    echo "     LD_PRELOAD=/usr/lib64/libkraio.so redis-server /path/to/redis.conf"
    echo "  或在 systemd 服务文件中配置 Environment=LD_PRELOAD=/usr/lib64/libkraio.so"
elif echo "$RESULT" | grep -q "PKG_OK"; then
    echo "结论: BoostKit 软件包已安装，但 KRAIO 库文件未找到"
    echo "建议: 检查 BoostKit 软件包是否完整安装，确认 libkraio.so 路径"
elif echo "$RESULT" | grep -q "ARCH_FAIL"; then
    echo "结论: 当前平台不支持 KRAIO 特性（仅鲲鹏 aarch64 平台支持）"
else
    echo "结论: Redis 网络异步优化 (KRAIO) 未使能"
    echo "建议: 按以下步骤使能 KRAIO："
    echo "  1. 确认系统架构为 aarch64（鲲鹏平台）"
    echo "  2. 安装鲲鹏 BoostKit 数据库使能套件"
    echo "  3. 安装 KRAIO 库 (libkraio.so)"
    echo "  4. 配置 Redis 启动时加载 libkraio.so"
    echo "  5. 重启 Redis 服务"
fi
```

## KRAIO 使能步骤

当检测到 KRAIO 未使能时，按以下步骤操作：

```bash
# 1. 确认系统架构为 aarch64（鲲鹏平台）
uname -m

# 2. 确认 Redis 版本
redis-server --version
# KRAIO 支持 Redis 6.0.20 和 Redis 7.0.15 版本

# 3. 安装鲲鹏 BoostKit 数据库使能套件
# 参考 https://www.hikunpeng.com/developer/boostkit/database 获取安装包

# 4. 确认 libkraio.so 已安装
find / -name "libkraio.so*" 2>/dev/null
# 常见路径: /usr/lib64/libkraio.so

# 5. 配置 Redis 启动时加载 libkraio.so

# 方式一：通过环境变量启动
export LD_PRELOAD=/usr/lib64/libkraio.so
redis-server /path/to/redis.conf

# 方式二：在 systemd 服务文件中配置
# 编辑 /usr/lib/systemd/system/redis-server.service
# 在 [Service] 段添加:
#   Environment=LD_PRELOAD=/usr/lib64/libkraio.so
# 然后重新加载并重启:
systemctl daemon-reload
systemctl restart redis-server

# 6. 验证 KRAIO 是否生效
REDIS_PID=$(pgrep -o redis-server)
cat /proc/$REDIS_PID/maps | grep libkraio.so
```

## 执行流程

1. 确认系统架构为 `aarch64`（鲲鹏平台），KRAIO 为鲲鹏专属特性
2. 检查 Redis 进程是否加载 `libkraio.so` / `libkbaio.so`（通过 `/proc/<pid>/maps`、`lsof` 或 `pmap`）
3. 检查 Redis 启动方式是否配置了 `LD_PRELOAD` 加载异步 IO 库
4. 检查系统中 `libkraio.so` / `libkbaio.so` 文件是否存在
5. 检查 BoostKit Redis 软件包是否安装
6. 检查 Redis 版本是否支持 KRAIO（Redis 6.0.20 / Redis 7.0.15）
7. 综合以上结果判断 KRAIO 网络异步优化是否使能

## KRAIO 特性说明

| 项目 | 说明 |
|------|------|
| 特性名称 | 网络异步优化 (KRAIO, Kunpeng Redis Async I/O) |
| 旧版名称 | KBAIO (Kunpeng Batch Async I/O) |
| 所属套件 | 鲲鹏 BoostKit 数据库使能套件 |
| 适用架构 | 鲲鹏 aarch64 |
| 适用系统 | openEuler |
| 核心库 | `libkraio.so`（新版）/ `libkbaio.so`（旧版） |
| 支持 Redis 版本 | Redis 6.0.20、Redis 7.0.15 |
| 核心原理 | 将 Redis 网络IO操作交由 KRAIO 异步批量执行，减少系统调用和上下文交换 |
| 加载方式 | `LD_PRELOAD` 预加载或编译时链接 |
| 性能收益 | 减少 Redis 网络IO阻塞，提升吞吐量 |

## 注意事项

- KRAIO 为鲲鹏 BoostKit 专属特性，仅在鲲鹏 (aarch64) 平台上可用
- KRAIO 库通常通过 `LD_PRELOAD` 方式注入 Redis 进程，也可通过 Patch 方式集成到 Redis 源码中编译
- 早期版本称为 KBAIO，对应库为 `libkbaio.so`，本 skill 同时检查两种库
- KRAIO 特性需要特定版本的 Redis 支持（6.0.20 / 7.0.15），其他版本可能不兼容
- 使用 `LD_PRELOAD` 方式加载时，需确保库文件路径正确且有读取权限
- 在 systemd 管理的 Redis 服务中，应通过 `Environment=` 指令配置 `LD_PRELOAD`，而非在 shell 环境中设置
- 容器环境中，`LD_PRELOAD` 配置需在容器启动参数或 Dockerfile 中指定
- 判断 KRAIO 是否使能的最可靠方法是检查 Redis 进程的内存映射中是否包含 `libkraio.so` / `libkbaio.so`
- KRAIO 与 NMO（网络多路径优化）是不同的特性，可独立使能，也可组合使用以获得更大性能提升
