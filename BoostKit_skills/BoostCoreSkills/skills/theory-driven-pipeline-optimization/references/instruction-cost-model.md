# 指令成本建模

本文件定义如何从核心指令微基准推导算法理论 cycles 下界。

## 1. 选择核心指令

从算法 hot path 中提取：

- 占主要计算量的指令，例如 FMA、CRC、bitmanip、integer multiply、shuffle。
- 在关键依赖链上的指令，例如 reduction、carry chain、round chain。
- 高成本数据移动，例如 TBL、REV、shuffle、pack/unpack、transpose。
- 必需 load/store，包括 table load、stream load、scatter/gather、store。

不要把全部静态指令都放进第一版模型。先覆盖决定上限的核心指令，剩余部分放入 `residual`。

## 2. 微基准类型

### Latency benchmark

目的：测量依赖链时延。

形态：

```text
x0 = op(x0)
x0 = op(x0)
x0 = op(x0)
...
latency = cycles / op_count
```

要求：后一次操作必须依赖前一次结果。

### Throughput benchmark

目的：测量独立指令吞吐。

形态：

```text
x0 = op(x0)
x1 = op(x1)
x2 = op(x2)
x3 = op(x3)
...
throughput = cycles / op_count
```

要求：独立寄存器数量足够多，能覆盖单条指令 latency。

### Mix benchmark

目的：测量真实算法中核心指令组合是否能 overlap。

形态：

```text
repeat:
  op_a independent/dependent pattern
  op_b independent/dependent pattern
  optional load/store/layout
```

判断：

```text
if C_mix ~= C_a + C_b:
  op_a 和 op_b 近似相加，竞争同一瓶颈资源或不能 overlap
if C_mix ~= max(C_a, C_b):
  op_a 和 op_b 可以较好 overlap
if C_mix > C_a + C_b:
  可能有寄存器压力、调度压力、前端压力或 memory 副作用
```

## 3. 指令成本表

推荐格式：

```text
instruction/group | latency | throughput | mixed marginal | benchmark | assumption
op_a              | ...     | ...        | ...            | ...       | ...
op_b              | ...     | ...        | ...            | ...       | ...
load/store        | ...     | ...        | ...            | ...       | L1/L2/stream
layout            | ...     | ...        | ...            | ...       | ...
```

## 4. 算法理论 cycles 下界

至少计算三类约束：

```text
throughput_bound = combine(N_i * throughput_cost_i)
dependency_bound = sum(latency_on_critical_path)
memory_bound = load_store_cost + cache_or_tlb_penalty

theoretical_cycles_per_unit =
  max(throughput_bound, dependency_bound, memory_bound, frontend_bound)
```

`combine` 由 mix benchmark 决定：

- 如果指令组不能 overlap，用加和。
- 如果可以 overlap，按资源池取 max。
- 如果不确定，给出 optimistic 和 conservative 两个边界。

## 5. 理论吞吐上限

换算：

```text
units_per_sec = frequency_hz / theoretical_cycles_per_unit
bytes_per_sec = units_per_sec * bytes_per_unit
GB_per_sec = bytes_per_sec / 1e9
```

报告里必须注明：

- 是否包含 load/store。
- 数据假设在 L1、L2、L3 还是 DRAM。
- 是否包含 tail、fallback、函数调用和调度开销。
- 是否使用 optimistic 或 conservative overlap 假设。

## 6. 实测效率

```text
efficiency = theoretical_cycles_per_unit / measured_cycles_per_unit
headroom_cycles = measured_cycles_per_unit - theoretical_cycles_per_unit
```

解释：

- `efficiency` 接近 1：实现接近模型上限。
- `efficiency` 很低：存在调度、依赖、内存、前端、tail 或模型遗漏。
- `efficiency > 1`：理论模型比实测更慢，说明模型过保守或微基准不代表真实路径。
