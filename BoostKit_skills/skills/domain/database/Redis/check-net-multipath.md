---
name: "check-net-multipath"
description: "检查当前是否使能了鲲鹏网络多路径(NMO)特性。当用户询问 Redis/MySQL 是否启用了网络多路径加速、或需要确认 NMO 特性使能状态时调用此 skill。"
---

# Check Network Multi-Path (NMO) Enablement

此 skill 用于检查当前系统是否使能了鲲鹏 BoostKit 的网络多路径 (NMO, Network Multi-path Optimization) 特性。NMO 特性通过识别特定业务进程的流量特征，实现业务进程网络请求与网络中断的亲和性，从而提升数据库（如 Redis、MySQL）的网络性能。

参考文档：https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/nmo/kunpeng_mysql_dlj_zn_64_009.html

> **重要说明**：NMO 网络多路径特性涉及**两个内核模块**：
> - **`hisi_l3t`** — 鲲鹏 L3 cache 拓扑模块，是 NMO 的**依赖模块**，提供 L3 cache 锁和拓扑信息
> - **`oenetcls`** — 网络多路径 (NMO) 的**核心内核模块**，负责网络分类和 IRQ 亲和性调度
>
> 使能顺序：先加载 `hisi_l3t`，再加载 `oenetcls` 并指定网卡参数。

## 检测方法

按优先级依次尝试以下方法，综合判断 NMO 是否使能：

### 方法一：检查 NMO 内核模块是否加载（核心检测）

NMO 依赖两个内核模块：`hisi_l3t`（L3 cache 拓扑，依赖模块）和 `oenetcls`（网络多路径核心模块）。

```bash
echo "=== 检查 hisi_l3t 依赖模块 ==="
L3T_MODULE=$(lsmod | grep hisi_l3t)
if [ -n "$L3T_MODULE" ]; then
    echo "hisi_l3t 模块已加载"
    echo "$L3T_MODULE"
else
    echo "hisi_l3t 模块未加载"
fi

echo ""
echo "=== 检查 oenetcls 核心模块 ==="
NMO_MODULE=$(lsmod | grep oenetcls)
if [ -n "$NMO_MODULE" ]; then
    echo "oenetcls (NMO) 核心模块已加载"
    echo "$NMO_MODULE"
else
    echo "oenetcls (NMO) 核心模块未加载"
fi
```

也可通过 `modinfo` 确认模块是否存在于系统中：

```bash
echo "=== 检查 hisi_l3t 模块文件 ==="
modinfo hisi_l3t 2>/dev/null
if [ $? -eq 0 ]; then
    echo "hisi_l3t 模块存在于系统中"
else
    echo "hisi_l3t 模块不存在于系统中"
fi

echo ""
echo "=== 检查 oenetcls 模块文件 ==="
modinfo oenetcls 2>/dev/null
if [ $? -eq 0 ]; then
    echo "oenetcls 模块存在于系统中"
else
    echo "oenetcls 模块不存在于系统中"
fi
```

在 openEuler 系统中搜索 NMO 相关的 .ko 文件：

```bash
find /lib/modules/$(uname -r) -name 'hisi_l3t.ko*' -o -name 'oenetcls.ko*' 2>/dev/null
```

### 方法二：检查 NMO sysfs 接口

```bash
for mod in hisi_l3t oenetcls; do
    if [ -d "/sys/module/$mod" ]; then
        echo "模块 $mod sysfs 目录存在: /sys/module/$mod"
        ls -la /sys/module/$mod/
        if [ -d "/sys/module/$mod/parameters" ]; then
            echo "模块 $mod 参数:"
            for param in /sys/module/$mod/parameters/*; do
                echo "  $(basename $param) = $(cat $param 2>/dev/null)"
            done
        fi
    else
        echo "模块 $mod sysfs 目录不存在（模块未加载）"
    fi
done
```

### 方法三：检查 BoostKit 数据库软件包是否安装

NMO 作为 `boostkit-mysql` 或 `boostkit-redis` 软件包的一部分交付：

```bash
BOOSTKIT_PKG=$(rpm -qa 2>/dev/null | grep -E 'boostkit-(mysql|redis)')

if [ -z "$BOOSTKIT_PKG" ]; then
    BOOSTKIT_PKG=$(dpkg -l 2>/dev/null | grep -E 'boostkit-(mysql|redis)')
fi

if [ -n "$BOOSTKIT_PKG" ]; then
    echo "BoostKit 数据库软件包已安装"
    echo "$BOOSTKIT_PKG"
else
    echo "BoostKit 数据库软件包未安装"
fi
```

也可检查 BoostKit 相关的所有软件包：

```bash
rpm -qa 2>/dev/null | grep -i boostkit
```

### 方法四：检查 NMO 相关服务是否运行

```bash
NMO_SERVICE=$(systemctl list-units --type=service --all 2>/dev/null | grep -iE 'nmo|boostkit.*(mysql|redis)')

if [ -n "$NMO_SERVICE" ]; then
    echo "NMO 相关服务已注册"
    echo "$NMO_SERVICE"
    for svc in nmo boostkit-nmo boostkit-mysql boostkit-redis; do
        systemctl status "$svc" 2>/dev/null && break
    done
else
    echo "NMO 相关服务未注册"
fi
```

也可通过进程检查：

```bash
NMO_PROCESS=$(ps -ef | grep -iE '[n]mo|[b]oostkit.*(nmo|mysql|redis)')

if [ -n "$NMO_PROCESS" ]; then
    echo "NMO 相关进程正在运行"
    echo "$NMO_PROCESS"
else
    echo "NMO 相关进程未运行"
fi
```

### 方法五：检查进程的网络中断亲和性配置（运行时验证）

NMO 的核心机制是为业务进程建立网络请求与网络中断的亲和性：

```bash
PID=${1:-$(pgrep -o redis-server)}

if [ -z "$PID" ]; then
    echo "未找到 Redis 进程"
    exit 1
fi

echo "=== Redis 进程信息 ==="
echo "PID: $PID"
echo "进程名: $(cat /proc/$PID/comm 2>/dev/null)"
echo "CPU 亲和性: $(cat /proc/$PID/status 2>/dev/null | grep Cpus_allowed_list)"

echo ""
echo "=== 进程所在 NUMA 节点 ==="
NUMA_NODE=$(cat /proc/$PID/status 2>/dev/null | grep -i numa)
echo "$NUMA_NODE"

echo ""
echo "=== 网卡中断分布 ==="
NIC=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $5; exit}')
if [ -n "$NIC" ]; then
    echo "主网卡: $NIC"
    echo "网卡 NUMA 节点: $(cat /sys/class/net/$NIC/device/numa_node 2>/dev/null)"
    echo ""
    echo "网卡中断亲和性:"
    grep "$NIC" /proc/interrupts 2>/dev/null | while read irq rest; do
        irq_num=$(echo "$irq" | tr -d ':')
        affinity=$(cat /proc/irq/$irq_num/smp_affinity_list 2>/dev/null)
        echo "  IRQ $irq_num -> CPU $affinity"
    done
fi
```

### 方法六：检查 NMO 配置文件

```bash
NMO_CONF_FILES="/etc/nmo/nmo.conf /etc/nmo.conf /etc/boostkit/nmo.conf /etc/sysconfig/nmo /etc/boostkit-mysql/nmo.conf /etc/boostkit-redis/nmo.conf"

for conf in $NMO_CONF_FILES; do
    if [ -f "$conf" ]; then
        echo "找到 NMO 配置文件: $conf"
        cat "$conf"
    fi
done
```

### 方法七：检查进程网络连接与中断的亲和性（运行时验证）

验证 Redis 进程的网络连接是否与网络中断处于同一 NUMA 节点，这是 NMO 使能后的核心表现：

```bash
PID=${1:-$(pgrep -o redis-server)}

if [ -z "$PID" ]; then
    echo "未找到 Redis 进程"
    exit 1
fi

echo "=== 进程 NUMA 信息 ==="
PROCESS_NUMA=$(cat /proc/$PID/status 2>/dev/null | grep Cpus_allowed_list | awk '{print $2}')
echo "CPU 亲和性列表: $PROCESS_NUMA"

NIC=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $5; exit}')
if [ -z "$NIC" ]; then
    echo "无法确定主网卡"
    exit 1
fi

NIC_NUMA=$(cat /sys/class/net/$NIC/device/numa_node 2>/dev/null)
echo "主网卡 $NIC 所在 NUMA 节点: $NIC_NUMA"

echo ""
echo "=== 亲和性判断 ==="
if [ "$NIC_NUMA" != "-1" ]; then
    NUMA_CPUS=$(lscpu | grep "NUMA node$NIC_NUMA" | awk -F':' '{print $2}' | tr -d ' ')
    PROCESS_CPUS=$(cat /proc/$PID/status 2>/dev/null | grep Cpus_allowed_list | awk '{print $2}')
    echo "NUMA 节点 $NIC_NUMA 的 CPU 范围: $NUMA_CPUS"
    echo "进程 CPU 亲和性: $PROCESS_CPUS"

    if echo "$PROCESS_CPUS" | grep -q "$NIC_NUMA"; then
        echo "进程与网卡在同一 NUMA 节点，具备亲和性（可能已使能 NMO）"
    else
        echo "进程与网卡不在同一 NUMA 节点，缺乏亲和性（NMO 可能未使能）"
    fi
else
    echo "网卡 NUMA 节点信息不可用，无法判断亲和性"
fi
```

## 综合判断脚本

```bash
#!/bin/bash

PID=${1:-$(pgrep -o redis-server)}
RESULT=""

echo "========================================="
echo "NMO (Network Multi-Path) 使能状态检查"
echo "========================================="

echo ""
echo "[1] 检查 hisi_l3t 依赖模块 ..."
L3T_LOADED=$(lsmod | grep -c hisi_l3t)
if [ "$L3T_LOADED" -gt 0 ]; then
    echo "    ✓ hisi_l3t 依赖模块已加载"
    RESULT="${RESULT}L3T_OK,"
else
    echo "    ✗ hisi_l3t 依赖模块未加载"
    RESULT="${RESULT}L3T_FAIL,"
fi

echo ""
echo "[2] 检查 oenetcls 核心模块 ..."
NMO_LOADED=$(lsmod | grep -c oenetcls)
if [ "$NMO_LOADED" -gt 0 ]; then
    echo "    ✓ oenetcls (NMO) 核心模块已加载"
    RESULT="${RESULT}NMO_OK,"
else
    echo "    ✗ oenetcls (NMO) 核心模块未加载"
    RESULT="${RESULT}NMO_FAIL,"
fi

echo ""
echo "[3] 检查 BoostKit 数据库软件包 ..."
PKG_INSTALLED=$(rpm -qa 2>/dev/null | grep -cE 'boostkit-(mysql|redis)')
if [ "$PKG_INSTALLED" -gt 0 ]; then
    echo "    ✓ BoostKit 数据库软件包已安装"
    rpm -qa 2>/dev/null | grep -E 'boostkit-(mysql|redis)'
    RESULT="${RESULT}PKG_OK,"
else
    echo "    ✗ BoostKit 数据库软件包未安装"
    RESULT="${RESULT}PKG_FAIL,"
fi

echo ""
echo "[4] 检查 NMO 相关服务 ..."
SERVICE_ACTIVE=$(systemctl is-active nmo 2>/dev/null || systemctl is-active boostkit-nmo 2>/dev/null)
if [ "$SERVICE_ACTIVE" = "active" ]; then
    echo "    ✓ NMO 服务运行中"
    RESULT="${RESULT}SERVICE_OK,"
else
    echo "    ✗ NMO 服务未运行"
    RESULT="${RESULT}SERVICE_FAIL,"
fi

echo ""
echo "[5] 检查进程网络中断亲和性 ..."
if [ -n "$PID" ]; then
    NIC=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $5; exit}')
    if [ -n "$NIC" ]; then
        NIC_NUMA=$(cat /sys/class/net/$NIC/device/numa_node 2>/dev/null)
        PROCESS_CPUS=$(cat /proc/$PID/status 2>/dev/null | grep Cpus_allowed_list | awk '{print $2}')
        echo "    进程 PID: $PID, CPU 亲和: $PROCESS_CPUS"
        echo "    主网卡: $NIC, NUMA 节点: $NIC_NUMA"
        if [ "$NIC_NUMA" != "-1" ] && [ -n "$NIC_NUMA" ]; then
            echo "    ✓ 具备网络中断亲和性"
            RESULT="${RESULT}AFFINITY_OK"
        else
            echo "    ✗ 网络中断亲和性未配置或无法判断"
            RESULT="${RESULT}AFFINITY_FAIL"
        fi
    else
        echo "    ✗ 无法确定主网卡"
        RESULT="${RESULT}AFFINITY_UNKNOWN"
    fi
else
    echo "    ✗ 未找到目标进程"
    RESULT="${RESULT}AFFINITY_NO_PROCESS"
fi

echo ""
echo "========================================="
echo "检查结果汇总: $RESULT"
echo "========================================="

if echo "$RESULT" | grep -q "NMO_OK"; then
    echo "结论: NMO 网络多路径特性已使能（oenetcls 核心模块已加载）"
elif echo "$RESULT" | grep -q "L3T_OK" && echo "$RESULT" | grep -q "PKG_OK"; then
    echo "结论: NMO 依赖模块和软件包已就绪，但 oenetcls 核心模块未加载"
    echo "建议: 执行 modprobe oenetcls ifname=\"<网卡名>\" mode=1 启用 NMO"
elif echo "$RESULT" | grep -q "AFFINITY_OK"; then
    echo "结论: 网络中断亲和性已配置（可能是 NMO 使能，也可能是手动配置 IRQ affinity）"
    echo "建议: 结合内核模块和软件包安装情况进一步确认"
else
    echo "结论: NMO 网络多路径特性未使能"
    echo "建议: 按以下步骤使能 NMO："
    echo "  1. 安装鲲鹏 BoostKit 数据库使能套件（boostkit-mysql 或 boostkit-redis）"
    echo "  2. 安装网络多路径内核版本"
    echo "  3. modprobe hisi_l3t"
    echo "  4. modprobe oenetcls ifname=\"<网卡名>\" mode=1"
fi
```

## NMO 使能步骤

当检测到 NMO 未使能时，按以下步骤操作：

```bash
# 1. 确认系统架构为 aarch64（鲲鹏平台）
uname -m

# 2. 安装网络多路径内核版本（参考鲲鹏官方文档获取对应内核 RPM）
rpm -ivh kernel-5.10.0-xxx.oe2203sp4.aarch64.rpm --force

# 3. 重启系统，选择网络多路径内核版本启动

# 4. 环境基线配置
systemctl stop firewalld.service
systemctl disable firewalld.service
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
setenforce 0
systemctl stop irqbalance.service
systemctl disable irqbalance.service
swapoff -a

# 5. 加载 hisi_l3t 依赖模块
modprobe hisi_l3t
lsmod | grep hisi_l3t

# 6. 加载 oenetcls 核心模块并启用网络多路径
#    ifname 替换为实际网卡名，mode=1 表示启用
modprobe oenetcls ifname="<网卡名>" mode=1
lsmod | grep oenetcls
```

## 执行流程

1. 确认系统架构为 `aarch64`（鲲鹏平台），NMO 为鲲鹏专属特性
2. 检查 `hisi_l3t` 依赖模块是否加载（`lsmod | grep hisi_l3t`）
3. 检查 `oenetcls` 核心模块是否加载（`lsmod | grep oenetcls`）
4. 检查 BoostKit 数据库软件包是否安装
5. 检查 NMO 相关服务是否运行
6. 检查目标进程（如 Redis）的网络中断亲和性配置
7. 综合以上结果判断 NMO 是否使能

## NMO 特性说明

| 项目 | 说明 |
|------|------|
| 特性名称 | 网络多路径优化 (NMO, Network Multi-path Optimization) |
| 所属套件 | 鲲鹏 BoostKit 数据库使能套件 |
| 特性版本 | 5.1 |
| 适用架构 | 鲲鹏 aarch64 |
| 适用系统 | openEuler |
| 依赖内核模块 | `hisi_l3t`（L3 cache 拓扑模块） |
| 核心内核模块 | `oenetcls`（网络分类与亲和性调度模块） |
| 核心原理 | 识别业务进程流量特征，实现网络请求与网络中断的亲和性 |
| 适用数据库 | Redis、MySQL |
| 性能收益 | 降低网络延迟，提升数据库网络吞吐 |

## 注意事项

- NMO 为鲲鹏 BoostKit 专属特性，仅在鲲鹏 (aarch64) 平台上可用
- NMO 依赖 openEuler 操作系统内核支持，需要安装网络多路径专用内核版本
- NMO 涉及两个内核模块：`hisi_l3t`（依赖模块）和 `oenetcls`（核心模块），加载顺序为先 `hisi_l3t` 后 `oenetcls`
- `oenetcls` 模块加载时需指定 `ifname`（网卡名）和 `mode`（模式）参数
- NMO 的核心效果是让业务进程的网络请求与网卡中断处于同一 NUMA 节点，减少跨 NUMA 访问延迟
- 即使 NMO 未使能，也可通过手动配置 `irq affinity` 和 `numactl` 实现类似效果，但缺乏自动化的流量识别和动态调整能力
- 容器环境中，NMO 需要在宿主机内核层面使能，容器内仅能观察到亲和性效果
- 判断 NMO 是否使能的最可靠方法是检查 `oenetcls` 模块是否加载以及运行时亲和性效果
