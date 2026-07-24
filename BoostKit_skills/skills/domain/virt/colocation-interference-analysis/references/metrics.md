# 指标参考

## 核心派生指标

如果用户提供了原始计数器，优先计算以下派生指标：

| 指标 | 公式 | 含义 |
|---|---|---|
| IPC | `instructions / cycles` | 每个 CPU cycle 完成的指令数。下降表示执行效率降低，但不能单独说明原因。 |
| CPI | `cycles / instructions` | IPC 的倒数。升高表示每条指令消耗更多 cycle。 |
| MPKI | `cache_misses / instructions * 1000` | 每千条指令的 cache miss 数。适合比较指令总量不同的窗口。 |
| LLC miss rate | `LLC_misses / LLC_references` | 末级缓存访问失败比例。 |
| Branch miss rate | `branch_misses / branches` | 分支预测失败比例。 |
| CPU utilization | busy CPU time / elapsed time | CPU 饱和信号，但不足以单独做微架构诊断。 |
| Instructions per request | `instructions / requests` | 帮助区分干扰和请求类型变化。 |
| Cycles per request | `cycles / requests` | 帮助把 PMU 变化和业务请求成本关联起来。 |

## 指标族

### 执行效率

- `instructions`
- `cycles`
- IPC/CPI
- frontend/backend/topdown slots，如果有

解释：IPC 下降通常说明执行效率下降，但要结合 cache、memory、branch、frequency 和 throttling 判断原因。

### 缓存和内存

- L1/L2/LLC references and misses
- LLC MPKI
- memory bandwidth read/write
- TLB misses
- NUMA local/remote memory access

解释：cache miss、LLC MPKI、memory bandwidth、remote memory 同时上升时，更像缓存或内存层级竞争。

### 分支和前端

- branches
- branch misses
- frontend bound
- i-cache misses
- ITLB misses

解释：branch miss rate 或 frontend bound 上升时，可能是代码路径、请求 mix、指令缓存压力或前端取指瓶颈，不一定是离线任务直接干扰。

### 频率和限流

- CPU frequency
- CPU throttled time
- thermal/power limit events
- cgroup CPU throttling

解释：cycles、latency 上升但 cache/memory 信号不强时，应检查 CPU 频率、功耗限制和 cgroup 限制。

## 归一化建议

优先使用归一化后的指标：

- 按秒归一化：bandwidth、misses/s、instructions/s。
- 按指令归一化：MPKI、branch miss rate。
- 按请求归一化：instructions/request、cycles/request、misses/request。
- 按 CPU 时间归一化：适合比较 CPU 调度时间不同的容器或 cgroup。

避免在窗口时长或 CPU 分配不同的情况下直接比较原始计数器总量。

## 经验阈值

这些阈值用于筛选重点，不是严格统计检验。采样窗口很短、负载不稳定或采集范围不一致时，应提高阈值并降低置信度。

| 判断项 | 经验阈值 | 处理方式 |
|---|---:|---|
| 一级 Top-down 指标变化 | `< 1pp` | 通常不显著，除非趋势数据中持续出现。 |
| 一级 Top-down 指标变化 | `>= 3pp` | 需要解释方向和可能原因。 |
| Top-down 子项变化 | `>= 5pp` | 标为重点变化项。 |
| Memory 子项内部迁移 | `>= 8-10pp` | 标为缓存/内存层级瓶颈迁移线索。 |
| IPC 相对变化 | `>= 5%` | 认为执行效率发生明显变化。 |
| Instructions 相对变化 | `>= 10%` | 必须进入工作量变化分支，不能直接比较 raw cycles。 |
| Cycles 相对变化 | `>= 10%` | 需要结合 Instructions、CPU 时间、QPS 和 IPC 判断。 |

`pp` 表示百分点，例如 `Memory Bound` 从 `40%` 到 `46%` 是 `+6pp`。

## 工作量变化分支

当 `Instructions`、`Cycles`、QPS 或请求数变化明显时，先判断工作量是否变化，再判断微架构瓶颈。

优先规则：

- `Instructions` 明显变化时，不要直接比较 raw `Cycles` 总量。
- `IPC` 基本不变，但 `cycles/s`、`instructions/s` 或请求吞吐下降时，优先检查在线进程是否拿不到 CPU 时间。
- `Cycles` 和 `Instructions` 同向下降，但 `IPC` 不变：更像工作量、CPU 时间或 QPS 变化，不像每条指令变慢。
- `Instructions/request` 上升：可能是请求 mix、代码路径、重试、GC 或业务阶段变化。
- `Cycles/request` 上升且 `Instructions/request` 不变、IPC 下降：更支持微架构效率劣化。

需要检查：

- QPS、请求数、请求类型和 benchmark 阶段是否变化。
- 在线进程 CPU 时间、run queue、上下文切换是否变化。
- cgroup `nr_throttled`、`throttled_usec` 是否上升。
- CPU frequency、CPU 亲和性、NUMA placement 是否变化。

## DevKit Top-down 文本报告分析

当用户提供类似 `devkit tuner top-down -d 5` 的文本报告时，先把报告当作结构化层级数据解析，再做诊断。报告通常包含：

- 元信息：`Version`、`CPU Model`、`Command`。
- 采样时间：`TOP-DOWN Summary Report-ALL Time:...`。
- 总体计数：`Cycles`、`Instructions`、`IPC`。
- Top-down 层级：每行包含指标名、`Bound(%)` 和 `Preferred Sampling Event`。

### 抽取规则

对每个纯在线/混部窗口分别抽取：

| 字段 | 示例 | 用途 |
|---|---|---|
| CPU Model | `Kunpeng 950 ... @ 2.3GHz` | 判断架构和频率背景。 |
| Command | `devkit tuner top-down -d 5` | 判断采样时长和采集方式是否一致。 |
| Time | `2026/06/03 15:23:19` | 对齐业务 SLO、离线任务启动时间和外部事件。 |
| Cycles | `26,408,378,682` | 与 Instructions、IPC 一起判断执行成本。 |
| Instructions | `5,820,173,199` | 与 cycles 计算 IPC，并判断工作量是否变化。 |
| IPC | `0.22` | 核心效率指标。 |
| Bound 指标 | `Backend Bound 94.41` | Top-down 归因入口。 |
| 采样事件 | `inst_retired`、`br_mis_pred` | 指示可进一步采样定位的事件。 |

解析时保留层级关系，例如：

```text
Backend Bound
  Core Bound
    Exe Ports Util
  Memory Bound
    L1 Bound
      Forward hazard
    L2 Bound
    L3 Bound
    Mem Bound
      Latency bound
      Bandwidth bound
```

不要只抽取叶子节点；父节点的变化代表大类瓶颈迁移，叶子节点用于进一步定位。父节点下降不代表所有子项都改善，子项之间可能发生占比迁移。

### 对比方法

对每个同名指标计算：

- 绝对变化：`mixed - baseline`。
- 相对变化：`(mixed - baseline) / baseline`，baseline 为 0 或接近 0 时只报告绝对变化。
- 总瓶颈变化：一级指标是否恶化，例如 `Backend Bound` 是否明显上升、`Retiring` 是否明显下降。
- 瓶颈内部迁移：父节点变化不大时，子项占比是否迁移，例如 `L1 Bound` 下降而 `L3 Bound` 或 `Mem Bound/Latency bound` 上升。
- 排名变化：混部阶段 Bound(%) 最高的几个节点，和纯在线阶段是否不同。

优先关注：

- 一级指标：`Retiring`、`Backend Bound`、`Frontend Bound`、`Bad Speculation`。
- Backend 子项：`Core Bound`、`Memory Bound`。
- Memory 子项：`L1 Bound`、`L2 Bound`、`L3 Bound`、`Mem Bound`、`Latency bound`、`Bandwidth bound`、`Store Bound`。
- Frontend 子项：`Fetch Latency Bound`、`Fetch Bandwidth Bound`、`L1I TLB Miss`、`L1I Cache Miss`、`BPU Q Stall`。
- Bad Speculation 子项：`Branch Mispredicts`、`Machine Clears`。

### 单份报告的解读限制

只有一份 topdown 报告时，可以描述当前瓶颈，但不要判断混部干扰。必须至少有纯在线和混部两类窗口，才能做“干扰导致变化”的分析。

例如单份报告中：

- `IPC = 0.22`
- `Backend Bound = 94.41%`
- `Memory Bound = 64.30%`
- `Mem Bound = 21.95%`
- `Latency bound = 21.95%`
- `Bandwidth bound = 0.00%`

只能说明该采样窗口主要受 Backend/Memory 侧限制，且更偏内存访问延迟而不是带宽上限；不能单独说明这是离线负载造成的。

### 总瓶颈变化与内部迁移

分析时分开回答三个问题：

| 判断项 | 说明 |
|---|---|
| 一级瓶颈是否恶化 | 看 `Retiring`、`Backend Bound`、`Frontend Bound`、`Bad Speculation` 是否超过阈值变化。 |
| Backend 内部是否迁移 | 即使 `Backend Bound` 基本不变，也要看 `Core Bound` 和 `Memory Bound` 是否此消彼长。 |
| Memory 内部是否迁移 | 看 `L1/L2/L3/Mem/Latency/Bandwidth Bound` 是否发生迁移。 |

示例：`Backend Bound` 只变化 `-0.3pp`，但 `L1 Bound` 下降、`L3 Bound` 或 `Mem Bound` 上升 `+10pp`，不应解读为整体 Backend 恶化；更准确的判断是 Backend 总量基本稳定，但内存层级瓶颈向更深层缓存或 DRAM 迁移。

### 反常模式

| 现象 | 解读方式 |
|---|---|
| 父节点下降，某个子项上升 | 父节点总体改善不代表所有子项改善；子项占比迁移仍需解释。 |
| `Memory Bound` 下降，但 `L3/Mem/Latency Bound` 上升 | 可能是 L1/DTLB/近端 stall 缓解，同时深层缓存或 DRAM 延迟占比上升。 |
| `Backend Bound` 基本不变，但 Memory 子项迁移明显 | 不支持“整体 Backend 恶化”，但支持内存层级干扰假设。 |
| IPC 不变但 P99 变差 | 优先检查 CPU 时间、调度、锁、I/O、GC 或尾部请求 mix。 |

### Top-down 指标到干扰模式的映射

| 变化模式 | 倾向解释 | 注意事项 |
|---|---|---|
| `Backend Bound` 上升，`Retiring` 下降，IPC 下降 | 执行效率下降，需继续看 Core/Memory 子项 | Backend 是大类，不是根因。 |
| `Memory Bound` 上升，`Mem Bound/Latency bound` 上升 | 内存层级延迟或远端内存影响 | 需要结合 NUMA、LLC miss、内存延迟指标。 |
| `Memory Bound` 上升，`Bandwidth bound` 上升 | 内存带宽竞争 | 需要确认节点/socket 带宽是否接近上限。 |
| `L3 Bound` 或 LLC 相关项上升 | LLC/cache 容量或共享竞争 | 需要确认在线和离线是否共享 LLC domain。 |
| `L1 Bound`、`Forward hazard`、`Pipeline` 上升 | 可能是在线自身代码路径、数据依赖或负载 mix 变化 | 不应优先归因于混部，除非混部前后变化明显且外部因素排除。 |
| `Frontend Bound` 上升 | 前端取指、指令缓存、BPU 或代码路径问题 | 检查发布、请求 mix、i-cache/ITLB。 |
| `Bad Speculation` 或 `Branch Mispredicts` 上升 | 分支预测或代码路径变化 | 离线干扰通常不是首要解释。 |
| `Core Bound` 上升，Memory 信号不强 | 计算资源、执行端口或调度压力 | 检查 CPU 时间、run queue、频率和 cgroup throttling。 |

### 输出建议

当输入是 topdown 报告时，在最终分析中增加一个层级变化表：

| 层级 | 指标 | 纯在线 Bound(%) | 混部 Bound(%) | 变化 | 解释 |
|---|---|---:|---:|---:|---|

层级字段可使用 `L1`、`L2`、`L3` 或缩进路径，例如 `Backend Bound > Memory Bound > Mem Bound > Latency bound`。

## 两种输入模式的分析策略

### 模式一：两点快照分析

输入形态：

- 一份纯在线 topdown 报告。
- 一份混部后 topdown 报告。
- 通常没有连续监控数据，可能只有一次 `devkit tuner top-down -d 5` 的采样结果。

适用目标：

- 快速判断混部后瓶颈大类是否发生变化。
- 形成 1 到 3 个最可能的干扰假设。
- 给出下一轮低成本验证动作。

处理步骤：

1. 检查两份报告的 `Command`、采样时长、CPU Model、采集范围是否一致。
2. 分别抽取 `Cycles`、`Instructions`、`IPC` 和完整 Top-down 层级。
3. 对比一级指标：`Retiring`、`Backend Bound`、`Frontend Bound`、`Bad Speculation`。
4. 如果 `Backend Bound` 变化明显，继续看 `Core Bound` 与 `Memory Bound` 谁贡献更大。
5. 如果 `Memory Bound` 变化明显，继续看 `L1 Bound`、`L2 Bound`、`L3 Bound`、`Mem Bound`、`Latency bound`、`Bandwidth bound`。
6. 只把变化幅度明显、且方向一致的指标作为主要证据。
7. 明确列出不能排除的混杂因素，例如流量变化、请求 mix、CPU 频率、调度迁移、采集范围不一致。

输出侧重点：

- “混部后相对纯在线的主要变化是什么”。
- “一级瓶颈是否恶化，还是只有内部迁移”。
- “这些变化更像哪类干扰”。
- “由于只有两个采样点，哪些结论只能算假设”。
- “下一步应该补采什么或做什么开关实验”。

置信度边界：

- 两点快照通常最多给到中等置信度。
- 如果两份报告采集范围不一致、采样时长不同、纯在线窗口不稳定，置信度应降为低。
- 如果业务 SLO 同步劣化，且 Top-down 大类变化方向清晰，可以给中等置信度。

### 模式二：时间区间趋势分析

输入形态：

- 一段时间内的 topdown 指标序列。
- 每个时间点包含 `Cycles`、`Instructions`、`IPC` 和 Top-down Bound 指标。
- 最好同时提供在线业务 SLO、QPS、离线任务开始/结束时间和外部事件时间线。

适用目标：

- 识别离线任务介入前后的趋势变化和拐点。
- 判断劣化是否持续、是否随离线任务结束回落。
- 区分偶发采样噪声、在线业务自身变化和混部干扰。
- 给出更高置信度的干扰类型排序。

处理步骤：

1. 按时间排序数据，标记阶段：纯在线、离线启动过渡、混部稳定、离线结束后恢复。
2. 对每个阶段计算核心指标的均值、中位数、P95 或代表性区间，不只看单点。
3. 检查采样间隔是否一致；如果不一致，避免直接比较总量，优先比较比例和归一化指标。
4. 找离线任务启动附近的拐点：IPC、Retiring、Backend Bound、Memory Bound、Core Bound、Frontend Bound 是否同步变化。
5. 找持续性：变化是否在混部阶段持续存在，而不是单个异常点。
6. 找回落性：离线任务结束或暂停后，指标是否向纯在线水平恢复。
7. 与业务 SLO 对齐：P99、平均延迟、吞吐、错误率是否和微架构指标同向变化。
8. 与外部事件对齐：发布、扩缩容、流量变化、CPU 频率变化等是否能解释同一拐点。

输出侧重点：

- 趋势阶段划分。
- 拐点和离线任务时间的对齐关系。
- 混部阶段相对纯在线阶段的统计变化。
- 指标变化是否持续，以及离线结束后是否回落。
- 干扰模式的证据链和反证检查。

趋势判断规则：

| 现象 | 倾向判断 | 置信度影响 |
|---|---|---|
| 离线启动后指标立即劣化，混部阶段持续，离线结束后回落 | 强支持混部干扰 | 提高 |
| 指标劣化早于离线启动 | 更可能是在线业务或外部事件 | 降低 |
| 只有单个采样点异常 | 更可能是噪声或瞬时扰动 | 降低 |
| 微架构指标劣化但 SLO 不变 | 说明资源效率变化，但业务影响未证实 | 降低 |
| SLO 劣化但 topdown 指标无明显变化 | 检查 I/O、锁、GC、网络、调度或采集范围 | 降低 |
| Memory Bound 上升、IPC 下降、SLO 劣化同步发生 | 支持内存层级相关干扰 | 提高 |
| Backend Bound 上升但 Core/Memory 子项不稳定 | 只能说明 Backend 压力变化 | 中性或降低 |

### 模式选择规则

- 用户只给两份报告：使用两点快照分析。
- 用户给按时间排列的多份报告或监控序列：使用时间区间趋势分析。
- 用户给多份报告但没有标注纯在线/混部阶段：先要求用户标注阶段，或只能做无监督异常摘要。
- 用户给趋势数据但没有 SLO：可以分析微架构趋势，但业务影响置信度要降低。
