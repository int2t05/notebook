# perf-topdown 联合瓶颈诊断

`perf-topdown` 结合 devkit top-down 分析和 perf 数据进行 CPU 性能瓶颈交叉验证。回答流水线**为什么**停顿（WHY），与 `perf-hotspot`（回答 WHERE/HOW）形成互补。

`perf-topdown` combines devkit top-down and perf data for CPU bottleneck cross-validation, answering WHY the pipeline stalls.

## 三级诊断中的定位

```
perf-hotspot              perf-topdown（本 Skill）    perf-hotspot
───────────               ─────────────────────      ────────────
函数热点 + 指令/SPE         Top-down 四分类交叉验证      指令级/SPE 深入
WHERE + HOW               WHY                         WHICH/HOW（深入）
```

## 核心能力

- **交叉验证矩阵**：系统地将 perf 数据（采样分布、SPE 数据源、缓存缺失来源）与 top-down 四大分类（Retiring/BadSpec/Frontend/Backend）匹配，含不一致时的排查指南
- **瓶颈决策树**：从 IPC 出发的结构化诊断逻辑，节点处标注应使用 perf-hotspot 的哪个方法深入
- **单核 vs 多核瓶颈迁移分析**：识别核数增加时瓶颈从每核资源迁移到共享资源的规律
- **对比表格模板**：标准化指标表，含 IPC、Retiring、Backend Bound、Memory Bound、L1 StrHaz、L3/DRAM、0-ports-busy、FSU Stall、Load/FMA 采样占比
- **关键阈值参考**：ARM AArch64 健康/警告/严重三级阈值
- **测量开销识别**：识别 devkit/perf 初始化开销过大的场景

## 交叉验证矩阵

| perf-hotspot 方法 | 数据显示 | top-down 应显示 | 不一致排查 |
|------------------|---------|----------------|------------|
| 方法 2（annotate） | Load > 60% | Memory Bound 高 | 注解了错误的函数 |
| 方法 2（annotate） | FMA > 60% | Core Bound / 0-ports-busy 高 | 频率缩放影响 |
| 方法 3（L1D refill） | 集中在某函数 | L1 Structure Hazard 高 | L1 端口竞争 |
| 方法 5（SPE） | 大量 L3 miss | L3/DRAM Bound 高 | 共享带宽墙 |
| 方法 5（SPE） | 大量 TLB miss | DTLB miss 高 | 建议启用大页 |
| 方法 5（SPE） | load 延迟 13 cycles | L2 Bound 高 | L2 命中，L1 容量不足 |
| 方法 3（br_mis_pred） | 集中在某函数 | Bad Speculation 高 | 分支预测器需训练 |

## 瓶颈决策树

```
IPC < 1.0？
├── 是 → Backend Bound %
│   ├── Memory Bound > 15%
│   │   ├── L3/DRAM 高 → 共享带宽墙 → perf-hotspot 方法 6（DDRC）
│   │   └── L1 StrHaz 高 → 缓存端口竞争 → perf-hotspot 方法 3（L1D refill）
│   └── Core Bound > 60%
│       ├── 0-ports-busy > 50% → 计算饱和 → perf-hotspot 方法 2（annotate）
│       └── FSU Stall 高 → 微架构压力 → perf-hotspot 方法 2（annotate）
│
└── 否（IPC > 1.5）→ Retiring %
    ├── Retiring > 40% → 高效执行，微调 → perf-hotspot 方法 5（SPE）
    └── BadSpec / Frontend > 10% → perf-hotspot 方法 3（br_mis_pred）
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
| Load 采样占比 | < 30% | 30–60% | > 60% |
| stall_backend/stall_slot | < 80% | 80–95% | > 95% |

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-topdown -g -y
```

### 数据采集

```bash
# Top-down
devkit tuner top-down -L 0 ./benchmark 2>&1 | tee topdown.log

# Perf 快速体检（交叉验证用）
perf stat -e cycles,instructions,stall_slot_backend,stall_slot_frontend,\
l1d_cache,l1d_cache_refill,l2d_cache,l2d_cache_refill,l3d_cache,l3d_cache_refill,\
br_mis_pred,bus_access,mem_access \
  taskset -c 0 ./benchmark 2>&1
```

## 在 AI Agent 工具中使用

### Claude Code

当你询问联合 top-down + perf 分析、多级瓶颈诊断或程序为何未达到理论峰值性能时，Skill 会自动激活：

```
帮我用 top-down 和 perf stat 交叉验证 dgemm_perf 的瓶颈类型
IPC 只有 0.5，按决策树定位根因
对比 1 核和 8 核的瓶颈迁移
```

### CodeBuddy / Codex / Trae

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill perf-topdown -a <agent-name> -g -y
```

### 常用提示语

| 任务 | 提示语 |
|-----|-------|
| 交叉验证 | "交叉验证 perf 数据和 top-down 分类是否一致" |
| 决策树诊断 | "按瓶颈决策树分析这个 benchmark" |
| 核数扩展对比 | "对比 1 核和 8 核的瓶颈迁移" |
| 阈值检查 | "用阈值表检查这些指标的健康状态" |

## 单核 vs 多核瓶颈迁移

当从 1 核扩展到 N 核时：

| 指标 | 1 核 | N 核 | 迁移方向 |
|------|------|------|---------|
| IPC | 基准值 | ↓↓↓ | 下降 |
| Memory Bound | X% | ↑↑↑ | 共享资源饱和 |
| L1 StrHaz | Y% | ↑↑↑ | L1 端口竞争 |
| L3/DRAM Bound | Z% | ↑↑↑ | 内存带宽墙 |

**关键规则**：Memory Bound 随核数增长超过线性 → 瓶颈已迁移到共享资源。

## 与 perf-hotspot 的分工

| | perf-hotspot | perf-topdown（本 Skill） |
|--|-------------|----------------------|
| 定位 | WHERE 周期去哪了 + HOW 流水线事件 | WHY 流水线为什么停顿 |
| 工具 | perf stat/record/annotate/SPE/PMU/DDRC | devkit tuner top-down |
| 交叉验证 | 提供数据 | 提供验证矩阵和决策树 |
| 阈值参考 | 提供 perf stat 阈值 | 提供完整 ARM AArch64 阈值 |

## 前置条件

- Linux + `devkit` tuner 安装
- `perf` 安装（交叉验证用）
- 二进制建议 `-g` + `taskset -c N` 绑核

## 当前限制

- 仅支持 Linux
- 以 ARM AArch64 为主要目标（x86-64 阈值可能不同）
- 需要同时安装 `devkit` 和 `perf`
- 分析质量取决于采样数量和符号可用性
