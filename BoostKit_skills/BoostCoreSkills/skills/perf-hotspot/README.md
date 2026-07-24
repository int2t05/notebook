# perf-hotspot CPU 性能分析

`perf-hotspot` 是一个综合性的 CPU 性能分析 Skill，覆盖从**快速体检**到**指令级流水线排布**的完整分析方法。集成了 Linux perf、ARM SPE、PMU 事件采样、DDRC 带宽监控等能力。

`perf-hotspot` is a comprehensive CPU performance analysis skill covering quick health checks, function/instruction hotspots, targeted PMU event sampling, multi-level cache profiling, ARM SPE instruction-level pipeline analysis, and HiSilicon DDRC/L3C bandwidth monitoring.

## 分析方法总览

| 层级 | 方法 | 工具 | 回答的问题 | 数据量 | 耗时 |
|------|------|------|-----------|--------|------|
| 0 | 快速流水线体检 | `perf stat` | IPC、stall 构成、缓存命中率 | 零 | < 2s |
| 1 | 函数热点 | `perf report` | 哪个函数最热 | MB | 秒~分 |
| 2 | 指令热点 | `perf annotate` | 哪条汇编指令最热 | MB | 秒~分 |
| 3 | 定向 PMU 采样 | `perf record -e <event>` | 谁产生最多 cache miss/分支失败 | MB | 秒~分 |
| 4 | 三级缓存联合 | L1+L2+L3 同时采样 | 缓存瓶颈在哪个层级 | MB | 秒~分 |
| 5 | SPE 指令流水排布 | `perf record -e arm_spe` | 每条指令的延迟、数据源、TLB | MB~GB | 秒~分 |
| 6 | 内存带宽监控 | `perf stat -e hisi_ddrc` | DRAM 读写带宽 | 零 | < 2s |

## 核心能力

- **零开销快速体检**：`perf stat` 一次命令，2 秒内诊断 IPC + stall 分解 + 三级缓存命中率
- **函数/指令级热点**：`perf record/report/annotate` 标准工作流 + 指令混合分类（Load/FMA/Store/ALU/Control）
- **定向 PMU 事件采样**：直接采样 L1D refill、branch mispredict、stall 等微架构事件，精准回答"谁产生了最多 X"
- **三级缓存联合分析**：一次运行同时对 L1/L2/L3 采样，定位缓存瓶颈层级
- **ARM SPE 指令流水排布**：逐指令延迟 + 数据源缓存层级 + TLB 状态，还原指令流水线具体排布
- **HiSilicon DDRC/L3C 带宽监控**：直接读取硬件 DDR 控制器和 L3 缓存 PMU 的物理带宽数据
- **与 top-down 交叉验证**：所有方法与 devkit top-down 的 Memory/Core/Frontend/BadSpec 分类互相印证

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-hotspot -g -y
```

### 零开销体检（方法 0）

```bash
perf stat -e cycles,instructions,\
stall_slot_backend,stall_slot_frontend,stall_slot,\
l1d_cache,l1d_cache_refill,\
l2d_cache,l2d_cache_refill,\
l3d_cache,l3d_cache_refill,\
br_mis_pred,bus_access,mem_access \
  taskset -c 0 ./benchmark
```

| 指标 | 健康 | 警告 | 严重 |
|------|------|------|------|
| IPC | > 1.5 | 1.0–1.5 | < 1.0 |
| stall_backend / stall_slot | < 80% | 80–95% | > 95% |
| l1d_refill / l1d_cache | < 3% | 3–10% | > 10% |
| br_mis_pred / instructions | < 0.1% | 0.1–1% | > 1% |

### 定向 PMU 采样（方法 3）

```bash
# L1D 缺失来源
perf record -e l1d_cache_refill -c 1000 -o data ./benchmark
perf report -i data --stdio --no-children -n -g none | head -20

# 分支预测失败来源
perf record -e br_mis_pred -c 500 -o data ./benchmark
```

### ARM SPE 指令流水排布（方法 5）

```bash
# 采集
perf record -e arm_spe_0/load_filter=1,store_filter=1,jitter=1/ \
  -c 2000 -o spe.data taskset -c 0 ./benchmark

# 分析缓存命中率
perf report -i spe.data --stdio --mem-mode | head -60

# 逐指令延迟 + 数据源
perf script -i spe.data | head -50
```

### DDRC 带宽监控（方法 6）

```bash
perf stat -e hisi_sccl11_ddrc0_0/flux_rd/,\
hisi_sccl11_ddrc0_0/flux_wr/ \
  ./benchmark
```

## 在 AI Agent 工具中使用

### Claude Code

当你提到 perf、热点分析、指令分析、SPE、PMU 事件、缓存分析或 CPU 性能诊断时，Skill 会自动激活：

```
帮我用 perf stat 快速体检 dgemm_perf
用 perf annotate 分析热点函数的指令混合
用 L1D refill 采样定位谁产生了最多 cache miss
用 SPE 分析 dgemm_kernel 的 load 延迟分布和数据源
交叉验证 Memory Bound 和 SPE 的 L3 miss 是否一致
```

### CodeBuddy / 通用 Agent 框架

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-hotspot -a <agent-name> -g -y
```

### OpenAI Codex / Trae

```bash
# Codex
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-hotspot -a codex -g -y

# Trae
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-hotspot -a trae -g -y
```

### 常用提示语

| 任务 | 提示语 |
|-----|-------|
| 快速体检 | "用 perf stat 快速检查 benchmark 的 IPC 和 stall 构成" |
| 函数热点 | "用 perf 找出 benchmark 的热点函数" |
| 指令热点 | "对 hot_function 做指令级注解和指令混合分类" |
| L1D 缺失来源 | "用 L1D refill 采样定位哪个函数产生最多 cache miss" |
| 三级缓存分析 | "同时采样 L1/L2/L3 refill，定位缓存瓶颈层级" |
| SPE 延迟分布 | "用 SPE 分析 dgemm_kernel 的 load 延迟和数据源" |
| DDRC 带宽 | "读取 DDRC 带宽计数器，确认是否达到内存带宽墙" |
| 交叉验证 | "交叉验证 SPE/Top-down 结果是否一致" |

## 完整分析流程

```
perf stat (方法 0) → 热点函数 (方法 1) → 按需选择：
  ├── 计算密集 → perf annotate (方法 2) → 指令混合分类
  ├── 内存密集 → PMU 采样 (方法 3) → 三级缓存 (方法 4) → SPE (方法 5)
  └── 带宽敏感 → DDRC 监控 (方法 6)
→ 交叉验证 (devkit top-down)
```

## 前置条件

- Linux + `perf` 安装
- 方法 5（SPE）：ARMv8.2+ + `perf_event_paranoid` ≤ 1
- 方法 6（DDRC）：Kunpeng 920 或自带 HiSilicon PMU 的处理器
- 建议 `taskset -c N` 绑核 + `-g` 编译

## 与其他 Skill 的关系

| Skill | 职责 | 与本 Skill 关系 |
|-------|------|---------------|
| `perf-hotspot`（本 Skill） | 所有 perf 级别分析 | — |
| `perf-topdown` | devkit top-down 方法学 + 交叉验证 | 本 Skill 提供 perf 数据，perf-topdown 进行 WHY 层面的交叉验证 |
| `devkit-perf` | devkit tuner 基本使用 | 纯 top-down 工具使用指南 |

## 当前限制

- 仅支持 Linux
- 方法 5（SPE）仅支持 ARM AArch64
- 方法 6（DDRC）仅支持 Kunpeng 920 / HiSilicon 平台
- SPE 只采样 load/store/branch，无法采样纯计算指令（此时用 perf annotate）
- 内存密集型负载的 SPE 数据可能达 10GB+
