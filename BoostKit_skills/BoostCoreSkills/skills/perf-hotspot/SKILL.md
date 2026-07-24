---
name: perf-hotspot
description: Comprehensive CPU performance analysis using Linux perf and ARM SPE. Covers, quick pipeline health check (perf stat), function/instruction hotspot (perf record/report/annotate), targeted PMU event sampling (L1D refill, branch mispredict, etc.), multi-level cache profiling, ARM SPE instruction-level pipeline analysis (per-instruction latency, cache source, TLB, load-to-use stall), HiSilicon DDRC/L3C bandwidth monitoring, and cross-validation with devkit top-down. Use this skill whenever the user mentions perf, hotspot analysis, instruction profiling, SPE, PMU events, cache profiling, or CPU performance diagnosis.
---

# CPU 性能分析（Perf / SPE / PMU）

本 Skill 涵盖从**快速体检**到**指令级流水线排布**的完整 CPU 性能分析方法。

## 方法全景

| 层级 | 方法 | 工具 | 回答 | 数据量 | 耗时 |
|------|------|------|------|--------|------|
| 0 | 快速体检 | `perf stat` | IPC、stall 构成、缓存命中率 | 零 | < 2s |
| 1 | 函数热点 | `perf record` + `perf report` | 哪个函数最热 | MB 级 | 秒~分 |
| 2 | 指令热点 | `perf annotate` | 哪条汇编指令最热 | MB 级 | 秒~分 |
| 3 | 定向 PMU 采样 | `perf record -e <pmu_event>` | 哪个函数产生最多 cache miss/分支失败 | MB 级 | 秒~分 |
| 4 | 三级缓存联合 | `perf record -e l1d,l2d,l3d` | 缓存瓶颈在哪个层级 | MB 级 | 秒~分 |
| 5 | SPE 指令流水排布 | `perf record -e arm_spe` | 每条指令的延迟、数据源、TLB | MB~GB | 秒~分 |
| 6 | 内存带宽监控 | `perf stat -e hisi_ddrc` | DRAM 读写带宽（硬件计数器） | 零 | < 2s |

---

## 方法 0：快速流水线体检（perf stat）

最轻量的分析，不需要写数据文件，**< 2 秒**完成。

```bash
perf stat -e cycles,instructions,\
stall_slot_backend,stall_slot_frontend,stall_slot,\
l1d_cache,l1d_cache_refill,\
l2d_cache,l2d_cache_refill,\
l3d_cache,l3d_cache_refill,\
br_mis_pred,bus_access,mem_access \
  taskset -c 0 ./benchmark
```

**输出解读（dgemm on Kunpeng 920 实战）**：

```
cycles              4,893,509,599
instructions        8,442,109,264    IPC = 1.73 (>1.5 健康)
stall_slot_backend  17,301,927,133   后端停顿 96.9%
stall_slot_frontend    557,467,884   前端停顿  3.1%
l1d_cache_refill      152,825,653   L1D 缺失率 5.18%
l2d_cache_refill       51,304,399   L2D 缺失率 5.58%
br_mis_pred              422,318   分支预测失败率 0.005%
```

**判断逻辑**：

| 指标 | 健康 | 警告 | 严重 |
|------|------|------|------|
| IPC | > 1.5 | 1.0–1.5 | < 1.0 |
| stall_slot_backend / stall_slot | < 80% | 80–95% | > 95% |
| l1d_cache_refill / l1d_cache | < 3% | 3–10% | > 10% |
| br_mis_pred / instructions | < 0.1% | 0.1–1% | > 1% |

`stall_slot_backend` 占主导 → 检查 Memory Bound vs Core Bound（用 devkit top-down）。
`stall_slot_frontend` 占主导 → ICache/ITLB/复杂指令译码问题。

---

## 方法 1–2：函数/指令热点（perf record + report + annotate）

### 采集

```bash
# 基本：cycle 采样 + callgraph
perf record -e cycles:u --call-graph dwarf -o perf.data taskset -c 0 ./benchmark

# 短 benchmark（< 100ms）提高采样频率
perf record -e cycles:u -F 999 -o perf.data taskset -c 0 ./benchmark
```

关键选项：
- `-e cycles:u` — 仅用户态 cycles（排除内核）
- `--call-graph dwarf` — DWARF 栈回溯（汇编密集代码必备）
- `-o <file>` — 输出文件名（多版本对比时有用）
- `-F N` — 采样频率 Hz（短 benchmark 提高至 999）

### 函数级热点

```bash
perf report -i perf.data --stdio --no-children -n -g none | head -30
```

关注：Overhead 最高的函数、调用链深度、库 vs. 应用代码占比。

### 指令级热点

```bash
perf annotate -i perf.data --stdio --no-demangle <function_name>
```

**关键区分**：
- **高采样占比**的指令 = 瓶颈（流水线停顿在此）
- **低/零采样占比**的指令 = 快速执行后正常退休，无停顿

### 指令混合分类

```bash
perf annotate -i perf.data --stdio --no-demangle <function> | awk '
/^[[:space:]]*[0-9]+\.[0-9]+/{
    pct=$1; line=$0
    if (line ~ /ld1|ldr/)        load+=pct
    else if (line ~ /fmla|fadd/) fma+=pct
    else if (line ~ /st1|str/)   store+=pct
    else if (line ~ /subs|cmp/)  cmp+=pct
    else if (line ~ /b\.|bne|beq|blt|bgt|ble|bge|ret/) br+=pct
    else if (line ~ /add|sub|mov|lsl|asr|mul|nop/) alu+=pct
    else                         other+=pct
} END {
    printf "Load:    %6.1f%%\nFMA:     %6.1f%%\nStore:   %6.1f%%\nALU:     %6.1f%%\nControl: %6.1f%%\nOther:   %6.1f%%\n",
           load, fma, store, alu, cmp+br, other
}'
```

**指令混合解读**：

| 分布 | 诊断 |
|------|------|
| Load > 50% | 内存/缓存瓶颈，执行单元缺数据 |
| FMA > 50% | 计算饱和，浮点流水线充分利用 |
| Control > 20% | 分支密集，控制流难以预测 |
| Store > 10% | 写回压力大，store 端口竞争 |

### 对比工作流

```bash
perf record -e cycles:u --call-graph dwarf -o perf_A.data taskset -c 0 ./bench_A
perf record -e cycles:u --call-graph dwarf -o perf_B.data taskset -c 0 ./bench_B

perf report -i perf_A.data --stdio -n -g none | head -20
perf report -i perf_B.data --stdio -n -g none | head -20

perf annotate -i perf_A.data --stdio <hot_func> | awk '...'
perf annotate -i perf_B.data --stdio <hot_func> | awk '...'
```

对比五个维度：IPC、函数集中度、指令混合迁移、分支预测失败率、前端停顿比例。

---

## 方法 3：定向 PMU 事件采样

不用 `cycles` 采样，直接采样**你关心的微架构事件**，精准回答"谁产生了最多 X"。

### L1D 缺失来源

```bash
perf record -e l1d_cache_refill -c 1000 -o perf_l1d.data taskset -c 0 ./benchmark
perf report -i perf_l1d.data --stdio --no-children -n -g none | head -20
```

**实战（dgemm on Kunpeng 920）**：
```
80.93%  dgemm_kernel    ← 计算内核产生最多 L1D miss
16.12%  dgemm_itcopy    ← 数据打包次之
 2.69%  dgemm_oncopy    ← 数据拷贝
```

### 分支预测失败来源

```bash
perf record -e br_mis_pred -c 500 -o perf_br.data taskset -c 0 ./benchmark
perf report -i perf_br.data --stdio --no-children -n -g none | head -20
```

**实战（dgemm on Kunpeng 920）**：
```
54.19%  dgemm_kernel    ← 主循环分支
31.13%  libc random()   ← 初始化（不在热路径）
```

### 其他常用 PMU 事件

```bash
# 后端停顿
perf record -e stall_slot_backend -c 4000 ...

# 前端停顿
perf record -e stall_slot_frontend -c 4000 ...

# L2D 缺失
perf record -e l2d_cache_refill -c 500 ...

# TLB 缺失
perf record -e l1d_tlb_refill -c 200 ...
```

### 可用 PMU 事件速查

```
l1d_cache, l1d_cache_refill, l1d_tlb, l1d_tlb_refill
l2d_cache, l2d_cache_refill, l2d_tlb, l2d_tlb_refill
l3d_cache, l3d_cache_refill, l3d_cache_allocate
ll_cache, ll_cache_miss, ll_cache_miss_rd
stall, stall_slot, stall_slot_backend, stall_slot_frontend
br_mis_pred, br_mis_pred_retired, br_retired
bus_access, mem_access, memory_error
```

---

## 方法 4：三级缓存联合采样

一次运行同时采样 L1/L2/L3 三级缓存，快速定位缓存瓶颈层级。

```bash
perf record -e l1d_cache_refill,l2d_cache_refill,l3d_cache_refill \
  -c 1000 -o perf_cache.data taskset -c 0 ./benchmark

# 分别查看各层级热点
for lvl in l1d l2d l3d; do
  echo "=== $lvl ==="
  perf report -i perf_cache.data --stdio --no-children -n -g none 2>/dev/null | head -10
done
```

**判断**：
- L1D miss 集中在计算内核 → 正常的计算访存
- L2D miss 集中在计算内核 → 缓存块大小不够，需增大分块
- L3D/LLC miss 占比高 → 内存带宽墙，需减少工作集或软件预取

---

## 方法 5：ARM SPE 指令流水排布

ARM SPE（Statistical Profiling Extension）在**指令级别**捕获流水线事件：每条采样指令的延迟周期、数据来源缓存层级、TLB 状态。可还原指令流水线的具体排布。

**前置条件**：
- ARMv8.2+（Kunpeng 920 / Neoverse N1/N2/V1）
- `perf_event_paranoid` ≤ 1
- 二进制建议带 `-g`

### 5.1 采集

```bash
# 通用：load + store，随机采样
perf record -e arm_spe_0/load_filter=1,store_filter=1,branch_filter=0,jitter=1/ \
  -c 2000 -o spe.data taskset -c 0 ./benchmark

# 仅采 load（分析数据读取延迟）
perf record -e arm_spe_0/load_filter=1,store_filter=0,jitter=1/ \
  -c 1000 -o spe.data taskset -c 0 ./benchmark

# 包含分支预测失败
perf record -e arm_spe_0/load_filter=1,branch_filter=1,jitter=1/ \
  -c 2000 -o spe.data taskset -c 0 ./benchmark
```

关键选项：
- `load_filter=1`：采样 load 操作（最重要）
- `store_filter=1`：采样 store 操作
- `branch_filter=1`：采样分支指令
- `jitter=1`：随机抖动，避免采样与程序节奏同步
- `-c N`：每 N 个事件采一次（N=1000~4000）

**采集策略**：

| 负载类型 | 推荐配置 | 原因 |
|---------|---------|------|
| 纯计算（fmla） | 不用 SPE，用 perf stat + annotate | SPE load filter 采不到计算指令 |
| 混合型（dgemm） | `load_filter=1,store_filter=1,-c 2000` | 关注数据流缓存命中率 |
| 内存密集型（SVD） | `load_filter=1,-c 500` | 大量访存，密集采样 |

### 5.2 内存访问模式分析

```bash
perf report -i spe.data --stdio --mem-mode 2>/dev/null | head -60
```

输出列解读：
- `Memory access`：L1 hit/miss、L2 hit、L3 hit/miss、DRAM miss
- `Local Weight`：该记录的延迟权重总和
- `Local INSTR Latency`：单条指令的延迟周期数
- `Symbol`：产生该记录的指令所在函数
- `Data Symbol`：被访问的数据地址所在符号
- `TLB access`：TLB Walker hit/miss

### 5.3 查看逐条指令的 SPE 事件

```bash
perf script -i spe.data 2>/dev/null | head -50
```

每条记录的 data_src 格式：
```
|OP LOAD|LVL L1 miss|SNP N/A|TLB Walker hit|LCK No|BLK N/A
```

SPE 可见字段：

| 字段 | 含义 | 诊断用途 |
|------|------|---------|
| `l1d-access` | L1D 缓存命中 | 正常访存，延迟最低 |
| `l1d-miss` | L1D 缺失 | 需查 L2，延迟中等 |
| `LVL L1/L2/L3 hit/miss` | 数据源缓存层级 | 精确归因数据从哪里来 |
| `TLB Walker hit/miss` | TLB 命中状态 | miss 建议启用大页 |
| `Local INSTR Latency` | 指令延迟周期 | 定位高延迟指令 |
| `SNP` | Snoop 状态 | 多核缓存一致性 |

### 5.4 延迟分布统计

```bash
# 按函数统计缓存命中率
perf script -i spe.data 2>/dev/null | awk '
  /<target_function>/{
    if ($0 ~ /L1 hit/) l1_hit++
    else if ($0 ~ /L1 miss/) l1_miss++
    else if ($0 ~ /L3 miss/) l3_miss++
    total++
  } END {
    printf "L1 hit: %d (%.1f%%)\nL1 miss: %d (%.1f%%)\nL3 miss: %d (%.1f%%)\nTotal: %d\n",
           l1_hit, 100*l1_hit/total, l1_miss, 100*l1_miss/total, l3_miss, 100*l3_miss/total, total
  }'
```

### 5.5 逐偏移量延迟分析（定位内核中哪些 load 延迟最高）

```bash
perf script -i spe.data 2>/dev/null | awk '
  /<kernel_function>/{
    for(i=1;i<=NF;i++) if($i ~ /\+0x/) {offset=$i; sub(/.*\+0x/,"",offset); break}
    if ($0 ~ /L1 hit/) hits[offset]++
    else if ($0 ~ /L1 miss/) {misses[offset]++; if($0 ~ /L3 miss/) l3[offset]++}
    total[offset]++
  } END {
    for(o in total) printf "offset=+0x%-6s total=%d  L1_hit=%d  L1_miss=%d  L3_miss=%d\n", o, total[o], hits[o], misses[o], l3[o]
  }' | sort -t= -k2 -rn
```

### 5.6 SPE 实战案例

**fmla_thru（纯计算，2 FMLA/cycle）**：
- SPE load filter 采样：56 条记录，全部内核态
- 结论：计算循环零访存，确认 compute-bound。此类负载不用 SPE。

**dgemm_perf（混合型，OpenBLAS SVE）**：
- SPE 132K 条采样
- `dgemm_itcopy`：大量 L3 miss（weight 8789）→ 数据打包首次访问矩阵
- `dgemm_kernel`：13-cycle L1 miss → L2 缓存命中（Kunpeng 920）
- 结论：计算内核 load 延迟可控，瓶颈在数据打包阶段

**svd_bench（内存密集型，DGESVD）**：
- SPE 9.4GB 数据 → 超密集 memory traffic
- `dgemv_t`：13-18 cycle L1 miss（Level-2 BLAS，低计算强度）
- `dgemm_itcopy`：L1 miss + TLB Walker miss → 数据跨页分散
- 结论：DBE 不在纯带宽，还在于 Level-2 BLAS 低计算强度 + TLB miss

### 5.7 SPE 与 perf annotate 互补关系

| 维度 | perf annotate | ARM SPE |
|------|--------------|---------|
| 可见信息 | 指令采样计数 | 指令延迟 + 数据源 + TLB |
| 可见计算指令 | 是（FMA/ADD） | 否（仅 load/store/branch） |
| 可见延迟 | 否 | 是（Local INSTR Latency） |
| 可见数据源 | 否 | 是（L1/L2/L3/DRAM） |

**互补使用**：perf annotate 看计算指令热点（FMA→计算瓶颈），SPE 看访存指令延迟（load→内存瓶颈）。

---

## 方法 6：HiSilicon DDRC/L3C 带宽监控

Kunpeng 920 有专属的 DDR 控制器和 L3 缓存 PMU，可直接读取硬件级别的带宽数据。

```bash
# DRAM 读/写带宽
perf stat -e hisi_sccl11_ddrc0_0/flux_rd/,\
hisi_sccl11_ddrc0_0/flux_wr/,\
hisi_sccl11_ddrc0_1/flux_rd/,\
hisi_sccl11_ddrc0_1/flux_wr/ \
  taskset -c 0 ./benchmark 2>&1

# L3 缓存命中率
perf stat -e hisi_sccl11_l3c0/dat_access/,\
hisi_sccl11_l3c0/l3c_hit/ \
  taskset -c 0 ./benchmark 2>&1
```

先 `perf list | grep hisi` 查看当前系统可用的 HiSilicon PMU 事件。

---

## 与 devkit top-down 的交叉验证

本 Skill 的所有方法可以与 `devkit-perf`（top-down 分析）交叉验证：

| 本 Skill 显示 | top-down 应显示 | 不一致时排查 |
|-------------|----------------|------------|
| Load > 60% 采样 | Memory Bound 高 | 注解了错误的函数 |
| FMA > 60% 采样 | Core Bound / 0-ports-busy 高 | 频率缩放影响 |
| L1D refill 集中在某函数 | L1 Structure Hazard 高 | L1 端口竞争 |
| L3/LLC miss 占比高 | L3/DRAM Bound 高 | 共享带宽墙 |
| branch mispredict 集中 | Bad Speculation 高 | 分支预测器需训练 |
| SPE 大量 TLB miss | DTLB miss 高 | 建议启用大页 |
| SPE 13-cycle L1 miss | L2 Bound 高 | 数据主要来自 L2 |

---

## 完整分析流程推荐

```
1. perf stat (方法 0)             → 2 秒快速 IPC + stall 分解决定方向
2. perf record + report (方法 1)  → 定位热点函数
3. 按需选择：
   ├── 计算密集 → perf annotate (方法 2) → 指令混合分类
   ├── 内存密集 → 定向 PMU 采样 (方法 3) → L1D/L2D refill 来源
   │             → 三级缓存联合 (方法 4) → 定位缓存瓶颈层级
   │             → SPE (方法 5) → 逐指令延迟 + 数据源
   └── 带宽敏感 → DDRC 监控 (方法 6)
4. 交叉验证 (devkit top-down)     → 确认 perf 发现与 top-down 分类一致
```

---

## 前置条件

- Linux，`perf` 已安装
- 方法 0–4：基本 perf，不要求特殊硬件
- 方法 5（SPE）：ARMv8.2+ 处理器 + `perf_event_paranoid` ≤ 1
- 方法 6（DDRC）：Kunpeng 920 或自带 HiSilicon PMU 的处理器
- 建议 `taskset -c N` 绑核 + `-g` 编译
