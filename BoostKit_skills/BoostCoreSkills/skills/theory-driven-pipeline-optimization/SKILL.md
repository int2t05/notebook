---
name: theory-driven-pipeline-optimization
description: 当需要为计算密集型算法建立理论性能上限时使用：先识别核心指令和依赖链，编写微基准脚本测量这些指令的时延、吞吐和混合执行成本，再根据算法的指令计数、依赖图和数据移动推算每个处理单位需要多少 cycles，得到理论 cycles 下界和吞吐上限。适用于 C/C++、汇编、SIMD、加密、压缩、字符串处理、数学库等 kernel 的理论性能建模、headroom 判断和优化方向选择。
metadata:
  version: "0.2.0"
  category: "task-software-dev"
  tags: ["domain-lib", "task-performance", "utility-analysis"]
  short-description: "指令成本建模推导理论性能上限"
---

# 指令成本建模驱动的理论性能分析

本 Skill 的核心目标是计算一个算法在目标 CPU 上的理论性能上限。方法是先测核心指令的实际成本，再用这些成本推算算法每个处理单位需要多少 cycles，最后得到理论 cycles 下界和吞吐上限。

它适合计算密集型 hot kernel：汇编循环、SIMD/向量化实现、加密和压缩 primitives、字符串/内存操作、数学库内核、序列化/解析热路径等。

核心闭环：

```text
算法热路径 -> 核心指令集合 -> 指令时延/吞吐微基准 -> 指令成本表
-> 算法指令计数/依赖图 -> cycles/unit 理论下界 -> 理论吞吐上限
-> 实测对比 -> headroom 判断 -> 优化实验
```

## 与其他性能 Skill 的分工

- 使用 `perf-hotspot` 采集 perf stat、perf record、perf annotate、SPE、PMU 事件、带宽数据。
- 使用 `devkit-perf` 或 `perf-topdown` 判断宏观瓶颈属于 Frontend/Core/Memory/Bad Speculation。
- 使用本 Skill 设计核心指令微基准、建立指令成本表、推导算法理论 cycles 下界，并据此判断 headroom 和下一步优化实验。

如果用户只问“热点在哪”，优先用 `perf-hotspot`。如果用户问“这个算法理论上需要多少 cycle、上限是多少、离上限差多少、下一步该怎么改”，使用本 Skill。

## 适用场景

- 需要先计算理论性能上限，再判断实现是否接近上限。
- 已有 benchmark，但不知道离理论上限还有多少。
- 优化方向存在多个候选，需要用模型排序。
- 端口图、issue width、指令手册结论与实测不一致。
- 需要写微基准验证单条指令、依赖链、小指令组、load/store 形态或 mixed pipeline。
- 需要判断某个副路径能否塞进主循环流水线。
- 需要把“更少指令”与“更快执行”区分开。

不适合只做应用级架构优化、数据库查询调参、网络 I/O 调优，除非已经定位到明确的 CPU hot kernel。

## 工作流

### 1. 明确算法、单位和目标

记录：

- 算法名称、hot kernel、输入规模、数据分布、线程数。
- 目标 CPU、频率、向量长度、编译器、commit、运行命令。
- 处理单位：`byte`、`item`、`block`、`round`、`tile` 或 `packet`。
- 当前实测基线：吞吐、延迟、cycles、instructions、IPC。

把目标吞吐换算成周期预算：

```text
cycles_per_unit = frequency_hz * units_per_operation / target_units_per_sec
```

不要混用组件基线和端到端基线；两者都要记录，但分别建模。

### 2. 抽取核心指令和依赖图

先读源码、汇编或算法伪代码，列出每个处理单位必须执行的核心工作：

- 计算指令：FMA、integer ALU、crypto、bitmanip、permute、PMULL 等。
- 数据移动：load、store、shuffle、transpose、pack/unpack、broadcast。
- 依赖链：accumulator、reduction、carry/borrow、hash chain、round chain。
- 控制开销：loop branch、mask、tail、fallback。

输出一个算法成本草图：

```text
per unit:
  instruction counts:
    op_a = ...
    op_b = ...
    load/store = ...
    shuffle/layout = ...
  dependency chains:
    chain_0 = op_a -> op_b -> ...
    chain_1 = ...
  independent lanes / accumulators = ...
```

不要只数静态指令。必须标记哪些指令在关键依赖链上，哪些可以并行展开。

### 3. 编写核心指令微基准脚本

为核心指令集合写可重复运行的微基准，至少覆盖：

- `latency`：单条核心指令或短依赖链的时延。
- `throughput`：多独立寄存器版本的稳定吞吐。
- `mix`：核心指令组合能否 overlap，例如 compute + shuffle、compute + load。
- `density`：固定主指令，扫描副指令数量，观察边际成本。
- `memory/layout`：真实 load/store、shuffle、pack/unpack 形态。

基本规则：

- 同时测 dependent 和 independent 版本，区分 latency 与 throughput。
- 一次只改变一个主变量。
- 让 benchmark 足够长，避免计时和 PMU 开销主导。
- 固定 CPU、频率、亲和性和输入大小。
- 可被 C 调用的汇编必须遵守 ABI。

更细的微基准检查项见 [references/microbenchmark-checklist.md](references/microbenchmark-checklist.md)，指令成本表格式见 [references/instruction-cost-model.md](references/instruction-cost-model.md)。

### 4. 生成指令成本表

至少采集：

```bash
perf stat -r 5 -e cycles,instructions ./benchmark
```

根据问题加采：

- `perf annotate`：确认周期集中在哪些指令。
- PMU stall/cache/branch event：确认资源压力。
- SPE：确认 load latency、data source、TLB、指令级延迟。
- devkit top-down：确认 Core/Memory/Frontend 类别。

把微基准结果整理成成本表：

```text
instruction/group | latency cycles | throughput cycles/op | mixed marginal cost | notes
```

不要只看吞吐；必须同步记录 cycles、instructions、IPC、方差。若结果波动大，先怀疑 benchmark 设计或运行环境。

### 5. 推导算法理论 cycles

用指令成本表和算法指令计数推导理论 cycles 下界。至少计算两类约束：

1. 吞吐约束：所有必需操作按资源池吞吐累加或取最大值。
2. 依赖约束：关键依赖链的最小时延。

常用换算：

```text
throughput_bound = sum_or_max(N_op_i * throughput_cost_i)
dependency_bound = critical_path_latency
memory_bound = load_store_cycles + cache_or_tlb_penalty
theoretical_cycles_per_unit = max(throughput_bound, dependency_bound, memory_bound, frontend_bound)
```

判断 overlap：

```text
if C_mix ~= C_a + C_b:
  两组操作基本不能 overlap，或竞争同一资源池
if C_mix ~= max(C_a, C_b):
  overlap 有效，下一步看依赖和 frontend
if C_mix > C_a + C_b:
  可能有寄存器压力、调度压力、cache/TLB 或前端副作用
```

如果资源池未知，先用实测 mix/density 微基准校准“相加”还是“取最大值”。理论上限必须写清楚假设：数据在 L1/L2/内存、是否忽略 tail、是否包含 load/store、是否包含函数调用/调度开销。

### 6. 对比理论上限和实测

计算：

```text
efficiency = theoretical_cycles_per_unit / measured_cycles_per_unit
headroom = measured_cycles_per_unit - theoretical_cycles_per_unit
```

判断：

- 如果实测接近理论下界，继续优化收益有限，除非算法或数据布局改变。
- 如果差距大，按差距来源分类：指令排布、依赖链、内存层级、frontend、tail/fallback、测量误差。
- 如果模型比实测更慢，说明模型假设过保守或 microbenchmark 不代表真实混合场景。

### 7. 用模型选择下一步优化实验

根据 headroom 和瓶颈来源选择：

优先级：

1. 消除模型确认的高成本指令组或数据移动。
2. 缩短循环携带依赖链。
3. 减少 load/store 或改善对齐、预取、缓存层级命中。
4. 调整指令排布，验证 overlap。
5. 扩大 unroll 或 pipeline 宽度。
6. 评估混合 ISA 或 fallback/tail 分工。

每次真实 kernel 修改后，重新跑同一组核心指令微基准和端到端基线，更新理论上限和效率。

## 输出要求

最终报告应包含：

- 目标与基线。
- 核心指令集合和依赖图。
- 指令时延/吞吐微基准结果。
- 指令成本表。
- 算法理论 cycles 下界和吞吐上限。
- 实测与理论上限的差距。
- 下一步实验列表，按预期收益和风险排序。

使用 [references/report-template.md](references/report-template.md) 组织报告。
