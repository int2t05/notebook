---
name: perf-topdown
description: Combine devkit top-down and perf annotate data to diagnose CPU performance bottlenecks. Cross-validate "where" (perf annotate, which instructions stall) with "why" (top-down, which pipeline stage is blocked). Use this skill whenever the user wants to understand why a program doesn't reach theoretical peak performance, needs combined top-down + perf hotspot analysis, or asks about multi-level bottleneck diagnosis. All perf-level analysis methods (record, annotate, SPE, PMU events, DDRC bandwidth) are covered by the perf-hotspot skill.
---

# 联合 Top-Down + Perf 瓶颈诊断

结合 devkit top-down 分析（回答流水线**为什么**停顿）和 perf 数据（回答周期去了**哪里**），进行交叉验证和根因定位。

本 Skill 聚焦于 top-down 方法学和交叉验证逻辑。具体的 perf 采集方法（record/annotate/SPE/PMU 事件/DDRC 带宽等）请参见 `perf-hotspot` Skill。

## 数据采集

```bash
# 1. Top-down（完整级别 0）
devkit tuner top-down -L 0 ./benchmark 2>&1 | tee topdown.log

# 2. Perf 数据（具体方法选型见 perf-hotspot Skill）
# 快速体检查看 IPC + stall 构成：
perf stat -e cycles,instructions,stall_slot_backend,stall_slot_frontend,l1d_cache_refill,l2d_cache_refill,l3d_cache_refill,br_mis_pred taskset -c 0 ./benchmark 2>&1
```

## 三级诊断框架

```
Level 1: 宏观           Level 2: 流水线分类        Level 3: 指令级
(perf-hotspot)          (devkit top-down)          (perf-hotspot)
───────────             ────────────────           ────────────
函数热点                  Top-down 四分类           汇编指令 / SPE
perf report              Retiring/BadSpec/         perf annotate /
                         Frontend/Backend          perf SPE
                         
WHERE 周期去哪了          WHY 流水线为什么停顿        WHICH/HOW 哪条指令+什么事件
```

## 交叉验证矩阵

perf 数据和 top-down 分类必须互相印证：

| perf 数据显示 | top-down 应显示 | 不一致时排查 |
|-------------|----------------|------------|
| Load > 60% 采样 | Memory Bound 高，L1/L2/L3 Bound 上升 | 注解了错误的函数；内核态才是真正瓶颈 |
| FMA > 60% 采样 | Core Bound 高，0-ports-busy 高 | 频率缩放影响；测量开销干扰 |
| Store > 10% 采样 | FSU Stall 上升，Store Bound 上升 | 写合并缓冲区满 |
| Branch > 10% 采样 | Bad Speculation 上升，br_mis_pred 高 | 分支预测器需要训练 |
| 采样分散，无 >2% 单指令 | Frontend Bound 上升 | 大代码段导致 ICache 压力 |
| SPE L1D refill 集中在某函数 | L1 Structure Hazard 高 | L1 端口竞争（load vs compute） |
| SPE 大量 L3 miss | L3/DRAM Bound 高 | 共享带宽墙（多核场景） |
| SPE 大量 TLB miss | DTLB miss 高 | 建议启用大页 |
| SPE load 延迟 13 cycles（L2 hit） | L2 Bound 高 | L1 miss 后数据主要来自 L2 |

## 瓶颈决策树

```
IPC < 1.0？
├── 是 → 检查 Backend Bound %
│   ├── Memory Bound > 15%
│   │   ├── L3/DRAM Bound 高 → 共享带宽墙（多核）
│   │   │   → 用 perf-hotspot 方法 6（DDRC）测实际带宽
│   │   │   → 用 perf-hotspot 方法 5（SPE）看 load 数据源比例
│   │   └── L1 Structure Hazard 高 → 每核缓存端口竞争
│   │       → 用 perf-hotspot 方法 3（L1D refill 采样）定位来源函数
│   └── Core Bound > 60%
│       ├── 0-ports-busy > 50% → 计算已饱和（好现象）
│       │   → 用 perf-hotspot 方法 2（perf annotate）确认 FMA 占比
│       └── FSU Stall / Ptag stall 高 → 微架构资源压力
│           → 用 perf-hotspot 方法 2（perf annotate）看指令排布
│
└── 否（IPC > 1.5）→ 检查 Retiring %
    ├── Retiring > 40% → 执行效率良好，用 perf annotate 微调
    └── Bad Spec / Frontend > 10% → 代码布局或分支问题
        → 用 perf-hotspot 方法 3（br_mis_pred 采样）定位分支问题
```

## Instrumentation Overhead 识别标准

如果出现以下情况，说明测量开销过大，结果不可信：

```
Retiring < 1%
Backend Bound < 1%  
Frontend Bound < 1%
Bad Speculation < 1%
(四项合计 << 100%)
```

根本原因：devkit/perf 初始化开销在总运行时间中占比过高（benchmark < 10ms）。解决：增大负载规模或迭代次数。

## 对比表格模板

```bash
# 用 perf-hotspot 方法 0（perf stat）和 devkit top-down 填充
```

```
指标              配置A         配置B        变化      诊断
──                ─────        ─────        ────      ────
IPC               X            Y            ±Δ
Retiring          X%           Y%
Backend Bound     X%           Y%
Memory Bound      X%           Y%           ←关键差异
L1 StrHaz         X%           Y%
L3/DRAM           X%           Y%
0-ports-busy      X%           Y%           ←计算饱和度
FSU Stall         X%           Y%
Load samples      X%           Y%           ←perf annotate
FMA samples       X%           Y%           ←perf annotate
```

## 关键阈值（ARM AArch64）

| 指标 | 健康 | 警告 | 严重 |
|------|------|------|------|
| IPC | > 1.5 | 1.0–1.5 | < 1.0 |
| Retiring | > 35% | 20–35% | < 20% |
| Backend Bound | < 50% | 50–70% | > 80% |
| Memory Bound | < 5% | 5–15% | > 15% |
| L3/DRAM Bound | < 2% | 2–8% | > 8% |
| 0-ports-busy（计算） | > 40% | 20–40% | < 20% |
| Frontend Bound | < 5% | 5–15% | > 15% |
| Load 采样占比（perf） | < 30% | 30–60% | > 60% |
| stall_slot_backend / stall_slot | < 80% | 80–95% | > 95% |

## 单核 vs 多核瓶颈迁移

从 1 核扩展到 N 核时，瓶颈会**迁移**：

| 指标 | 1 核 | N 核 | 原因 |
|------|------|------|------|
| IPC | 基准值 | ↓↓↓ | 共享资源饱和 |
| Load/FMA 混合 | Load=N%, FMA=M% | Load ↑ | 缓存竞争加剧 |
| Memory Bound | X% | ↑↑↑ | 共享 L3/DRAM 饱和 |
| L1 StrHaz | Y% | ↑↑↑ | L1 端口被多核竞争 |
| L3/DRAM Bound | Z% | ↑↑↑ | 内存带宽墙 |

**关键规则**：如果 Memory Bound 随核数增长超过线性比例，瓶颈已从每核资源迁移到共享资源（L3、DRAM 带宽）。用 `perf-hotspot` 方法 6（DDRC 带宽监控）验证。

## 与 perf-hotspot 的分工

| 职责 | perf-hotspot | perf-topdown（本 Skill） |
|------|-------------|----------------------|
| perf 数据采集 | 所有（方法 0–6） | 引用 |
| 指令级分析 | annotate / SPE / PMU | 不覆盖 |
| 流水线分类 | 引用 stall_slot 指标 | devkit top-down 完整分解 |
| 交叉验证 | 引用本 Skill | 核心逻辑 |
| 决策树 | 引用 | 核心逻辑 |
| 阈值参考 | 引用 | 核心逻辑 |
