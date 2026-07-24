---
name: "check-arm-crc32"
description: "检查进程的二进制是否使用了 ARM CRC32 指令加速。当用户询问 RocksDB 或其他进程是否启用了 ARM CRC32 硬件加速、或需要确认二进制中是否包含 CRC32 指令时调用此 skill。"
---

# Check ARM CRC32 Instruction Acceleration

此 skill 用于检查进程的二进制文件是否使用了 ARM CRC32 指令进行硬件加速。ARMv8 架构引入了 CRC32 硬件指令，可显著提升校验和计算性能，RocksDB 等数据库可利用该指令加速数据校验。

## 检测方法

按优先级依次尝试以下方法，任一方法成功即可得出结论：

### 方法一：使用 objdump 反汇编搜索 CRC32 指令（推荐）

```bash
BINARY_PATH=$(readlink -f /proc/<PID>/exe)

if [ -z "$BINARY_PATH" ]; then
    echo "无法获取进程的二进制路径，请确认 PID 是否正确"
    exit 1
fi

CRC32_INSTRUCTIONS=$(objdump -d "$BINARY_PATH" 2>/dev/null | grep -E '\b(crc32b|crc32h|crc32w|crc32x|crc32cb|crc32ch|crc32cw|crc32cx)\b')

if [ -n "$CRC32_INSTRUCTIONS" ]; then
    echo "二进制文件使用了 ARM CRC32 指令加速"
    echo "找到的 CRC32 指令:"
    echo "$CRC32_INSTRUCTIONS" | head -20
else
    echo "二进制文件未使用 ARM CRC32 指令加速"
fi
```

### 方法二：检查 ELF 构建属性（Build Attributes）

```bash
BINARY_PATH=$(readlink -f /proc/<PID>/exe)

if [ -z "$BINARY_PATH" ]; then
    echo "无法获取进程的二进制路径，请确认 PID 是否正确"
    exit 1
fi

ARCH=$(file "$BINARY_PATH" | grep -o "ARM aarch64")

if [ -z "$ARCH" ]; then
    echo "二进制文件不是 ARM aarch64 架构，不适用 ARM CRC32 检测"
    exit 1
fi

CRC_ATTR=$(readelf -n "$BINARY_PATH" 2>/dev/null | grep -i crc)

if [ -n "$CRC_ATTR" ]; then
    echo "二进制文件的构建属性中包含 CRC 扩展标记"
    echo "$CRC_ATTR"
else
    echo "二进制文件的构建属性中未找到 CRC 扩展标记（可能未启用或编译器未记录该属性）"
fi
```

### 方法三：检查 .ARM.attributes 段

```bash
BINARY_PATH=$(readlink -f /proc/<PID>/exe)

if [ -z "$BINARY_PATH" ]; then
    echo "无法获取进程的二进制路径，请确认 PID 是否正确"
    exit 1
fi

ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "当前系统不是 ARM aarch64 架构: $ARCH"
    exit 1
fi

ATTRS=$(readelf -A "$BINARY_PATH" 2>/dev/null)

if echo "$ATTRS" | grep -qi "crc"; then
    echo "二进制文件的 .ARM.attributes 段中包含 CRC 扩展标记"
    echo "$ATTRS" | grep -i crc
else
    echo "二进制文件的 .ARM.attributes 段中未找到 CRC 扩展标记"
fi
```

### 方法四：检查共享库中的 CRC32 指令

某些情况下 CRC32 加速可能来自动态链接的共享库（如 RocksDB 的 librocksdb.so），需要同时检查：

```bash
PID=<PID>
BINARY_PATH=$(readlink -f /proc/$PID/exe)

echo "=== 检查主二进制 ==="
CRC32_MAIN=$(objdump -d "$BINARY_PATH" 2>/dev/null | grep -E '\b(crc32b|crc32h|crc32w|crc32x|crc32cb|crc32ch|crc32cw|crc32cx)\b')
if [ -n "$CRC32_MAIN" ]; then
    echo "主二进制中包含 CRC32 指令"
else
    echo "主二进制中未找到 CRC32 指令"
fi

echo ""
echo "=== 检查共享库 ==="
MAPS_FILE="/proc/$PID/maps"
LIBS=$(awk '{print $6}' "$MAPS_FILE" 2>/dev/null | grep '\.so' | sort -u)

for lib in $LIBS; do
    if [ -f "$lib" ]; then
        CRC32_LIB=$(objdump -d "$lib" 2>/dev/null | grep -E '\b(crc32b|crc32h|crc32w|crc32x|crc32cb|crc32ch|crc32cw|crc32cx)\b')
        if [ -n "$CRC32_LIB" ]; then
            echo "共享库 $lib 中包含 CRC32 指令"
        fi
    fi
done
```

### 方法五：运行时检测 CPU 是否支持 CRC32 扩展

确认运行环境是否具备 CRC32 硬件支持：

```bash
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "当前系统不是 ARM aarch64 架构: $ARCH"
    exit 1
fi

if [ -f /proc/cpuinfo ]; then
    CRC_FEATURE=$(grep -i "crc32" /proc/cpuinfo)
    if [ -n "$CRC_FEATURE" ]; then
        echo "CPU 支持 CRC32 扩展"
        echo "$CRC_FEATURE" | head -5
    else
        echo "CPU 不支持 CRC32 扩展（或 /proc/cpuinfo 未暴露该信息）"
    fi
else
    echo "无法读取 /proc/cpuinfo"
fi
```

## 执行流程

1. 首先确认目标架构为 `aarch64`（ARM 64位），非 ARM 架构不适用此检测
2. 通过进程 PID 获取二进制文件路径：`readlink -f /proc/<PID>/exe`
3. 使用 `objdump -d` 反汇编二进制，搜索 CRC32 相关指令（`crc32b/w/h/x`、`crc32cb/cw/ch/cx`）
4. 可选：检查 ELF 构建属性和 `.ARM.attributes` 段中的 CRC 扩展标记
5. 可选：检查进程加载的共享库中是否包含 CRC32 指令
6. 可选：检查 CPU 是否支持 CRC32 扩展（运行环境确认）

## ARM CRC32 指令参考

| 指令 | 功能 | 操作数宽度 |
|------|------|-----------|
| CRC32B | CRC-32 计算 | 字节 (8-bit) |
| CRC32H | CRC-32 计算 | 半字 (16-bit) |
| CRC32W | CRC-32 计算 | 字 (32-bit) |
| CRC32X | CRC-32 计算 | 双字 (64-bit) |
| CRC32CB | CRC-32C (Castagnoli) 计算 | 字节 (8-bit) |
| CRC32CH | CRC-32C (Castagnoli) 计算 | 半字 (16-bit) |
| CRC32CW | CRC-32C (Castagnoli) 计算 | 字 (32-bit) |
| CRC32CX | CRC-32C (Castagnoli) 计算 | 双字 (64-bit) |

## 注意事项

- ARM CRC32 指令是 ARMv8-A 架构的可选扩展（CRC32 Extension），需要编译时通过 `-march=armv8-a+crc` 或更高版本启用
- RocksDB 在编译时如果检测到 CRC32 硬件支持，会自动启用相关加速路径
- `objdump -d` 对大型二进制文件可能耗时较长，可考虑仅反汇编 `.text` 段：`objdump -d -j .text <binary>`
- 方法二和方法三（构建属性检测）依赖编译器是否在 ELF 中记录了 CRC 扩展属性，部分编译器可能不记录
- 容器环境中，CPU 特性由宿主机决定，容器内检测结果与宿主机一致
- 如果二进制是 stripped（符号被剥离），`objdump` 仍可反汇编出指令，只是不会显示函数名
