---
name: "check-arm-64k"
description: "判断当前进程是否运行在 ARM 64K 页大小的 Linux 内核上。当用户询问 ARM 64K 内核检测、页大小检查、或需要确认运行环境是否为 ARM 64K 时调用此 skill。"
---

# Check ARM 64K Kernel

此 skill 用于判断当前进程是否运行在 ARM 架构且内核页大小为 64K 的 Linux 系统上。

## 检测方法

按优先级依次尝试以下方法，任一方法成功即可得出结论：

### 方法一：使用 getconf 命令（推荐）

```bash
ARCH=$(uname -m)
PAGE_SIZE=$(getconf PAGE_SIZE)

if [ "$ARCH" = "aarch64" ] && [ "$PAGE_SIZE" = "65536" ]; then
    echo "当前环境是 ARM 64K 内核"
else
    echo "当前环境不是 ARM 64K 内核 (arch=$ARCH, pagesize=$PAGE_SIZE)"
fi
```

### 方法二：读取 /proc/self/smaps

```bash
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "非 ARM 架构: $ARCH"
    exit 1
fi

KERNEL_PAGESIZE=$(grep -m1 "KernelPageSize" /proc/self/smaps 2>/dev/null | awk '{print $2}')
if [ "$KERNEL_PAGESIZE" = "64" ]; then
    echo "当前环境是 ARM 64K 内核"
else
    echo "当前环境不是 ARM 64K 内核 (KernelPageSize=$KERNEL_PAGESIZE kB)"
fi
```

### 方法三：使用 Python 检测

```python
import os
import platform

def is_arm_64k():
    if platform.machine() != "aarch64":
        return False
    page_size = os.sysconf("SC_PAGE_SIZE")
    return page_size == 65536

if is_arm_64k():
    print("当前环境是 ARM 64K 内核")
else:
    print("当前环境不是 ARM 64K 内核")
```

### 方法四：使用 C 代码检测

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    long page_size = sysconf(_SC_PAGE_SIZE);
    printf("页大小: %ld 字节\n", page_size);
    if (page_size == 65536) {
        printf("当前环境是 64K 页内核\n");
    } else {
        printf("当前环境不是 64K 页内核\n");
    }
    return 0;
}
```

## 执行流程

1. 首先通过 `uname -m` 确认 CPU 架构为 `aarch64`
2. 然后通过 `getconf PAGE_SIZE` 或读取 `/proc/self/smaps` 中的 `KernelPageSize` 确认页大小为 65536 字节（64 KB）
3. 两个条件同时满足时，判定为 ARM 64K 内核环境

## 常见页大小参考

| 页大小 | 字节数 | 常见架构 |
|--------|--------|----------|
| 4K     | 4096   | x86_64, ARM（标准） |
| 16K    | 16384  | ARM（可选） |
| 64K    | 65536  | ARM（可选）, ppc64le |

## 注意事项

- `getconf PAGE_SIZE` 返回的是字节数，而 `/proc/self/smaps` 中的 `KernelPageSize` 单位是 kB
- ARM 64K 内核通常用于特定场景（如数据库、大数据处理），需要硬件和内核同时支持
- 容器环境中，页大小由宿主机内核决定，容器内检测结果与宿主机一致
