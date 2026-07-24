# 报告模板

```md
## 目标与基线

- **目标 workload**: {workload}
- **处理单位**: {byte/item/block}
- **目标性能**: {target}
- **当前基线**: {baseline}
- **实测 cycles/unit**: {measured_cycles_per_unit}
- **运行环境**: {cpu/frequency/compiler/commit/command}

## 核心指令与依赖图

- **核心指令集合**: {instructions}
- **每单位指令计数**:
  - {op_a}: {count}
  - {op_b}: {count}
  - load/store: {count}
  - layout/shuffle: {count}
- **关键依赖链**:
  - chain_0: {instruction chain}
  - chain_1: {instruction chain}

## 指令微基准结果

| 指令/组合 | benchmark | latency cycles | throughput cycles/op | mixed marginal cost | 结论 |
|-----------|-----------|----------------|----------------------|---------------------|------|
| {op_a} | dependent | | | | |
| {op_a} | independent | | | | |
| {op_a + op_b} | mix | | | | |

## 指令成本表

```text
cost(op_a) = ...
cost(op_b) = ...
cost(load/store) = ...
cost(layout) = ...
```

## 理论 cycles 推导

```text
throughput_bound = ...
dependency_bound = ...
memory_bound = ...
frontend_bound = ...
theoretical_cycles_per_unit = max(...) = ...
theoretical_throughput = ...
```

## 实测对比与 Headroom

- **理论 cycles/unit**: {theoretical}
- **实测 cycles/unit**: {measured}
- **效率**: {theoretical / measured}
- **headroom**: {measured - theoretical}
- **差距来源**: {scheduling/dependency/memory/frontend/tail/model-error}

## 下一步实验

| 优先级 | 实验 | 预期收益 | 风险 | 验收指标 |
|--------|------|----------|------|----------|
| P0 | | | | |
| P1 | | | | |

## 结论

{short conclusion}
```
