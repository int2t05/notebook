# theory-driven-pipeline-optimization 理论性能上限分析

`theory-driven-pipeline-optimization` 是面向计算密集型 kernel 的理论性能建模 Skill。它的核心方法是：先为算法 hot path 中的核心指令编写微基准，测量指令时延、吞吐和组合执行成本，再根据算法的指令计数、关键依赖链和数据移动推导每个处理单位需要的理论 cycles，得到理论性能上限。

这个 Skill 适用于 C/C++、汇编、SIMD、加密、压缩、字符串处理、数学库等底层热点实现，尤其适合回答“这个算法理论上最快能到多少”“当前实现离理论上限还有多少”“下一步优化该改哪里”。

## 核心能力

- **核心指令识别**：从源码、汇编或算法伪代码中抽取决定性能上限的计算指令、数据移动、依赖链和控制开销。
- **指令微基准设计**：为核心指令生成 latency、throughput、mix overlap、density、memory/layout 等类型的测试脚本或测试方案。
- **指令成本表**：用 `perf stat`、PMU、SPE、devkit top-down 等数据校准每类指令或指令组合的 cycles 成本。
- **理论 cycles 推导**：根据每单位指令计数、依赖图和资源 overlap 假设，计算 `theoretical_cycles_per_unit`。
- **理论吞吐上限**：将 cycles 下界换算成 `items/s`、`bytes/s` 或 `GB/s`。
- **实测差距分析**：对比 benchmark 实测结果，计算 efficiency 和 headroom，判断差距来自排布、依赖、内存、前端、tail/fallback 还是模型遗漏。
- **优化实验排序**：根据理论模型选择下一步实验，优先处理真正限制上限的指令组、依赖链或数据移动。

## 分析流程

```text
算法热路径
  -> 核心指令集合
  -> 指令 latency / throughput / mix 微基准
  -> 指令成本表
  -> 算法指令计数与依赖图
  -> theoretical_cycles_per_unit
  -> 理论吞吐上限
  -> 实测对比与 headroom 判断
  -> 优化实验
```

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill theory-driven-pipeline-optimization -g -y
```

安装到指定 Agent：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill theory-driven-pipeline-optimization -a codex -g -y
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill theory-driven-pipeline-optimization -a trae -g -y
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill theory-driven-pipeline-optimization -a claude-code -g -y
```

### 典型使用方式

可以这样向 Agent 提问：

```text
帮我分析这个 SIMD kernel 的理论性能上限，先测核心指令时延和吞吐，再推导 cycles/byte。

这个 SIMD 字符串匹配算法每 64B 理论上需要多少 cycle？请先识别核心指令和依赖链。

根据这段汇编写微基准，分别测核心指令 latency、throughput 和 mix overlap，然后算理论 GB/s。

当前实现是 8.5 cycles/item，帮我推导理论下界并判断还有多少 headroom。
```

## 输出示例

最终报告通常包含：

```text
目标与基线:
  workload = ...
  measured = ... cycles/unit

核心指令:
  op_a = ... / unit
  op_b = ... / unit
  load/store = ... / unit
  critical chain = ...

指令成本:
  op_a latency = ... cycles
  op_a throughput = ... cycles/op
  op_a + op_b mix = ...

理论推导:
  throughput_bound = ...
  dependency_bound = ...
  memory_bound = ...
  theoretical_cycles_per_unit = max(...) = ...
  theoretical_throughput = ...

实测对比:
  efficiency = theoretical / measured = ...
  headroom = measured - theoretical = ...

下一步实验:
  P0 = ...
  P1 = ...
```

完整模板见 `references/report-template.md`。

## 与其他性能 Skill 的关系

| Skill | 职责 | 与本 Skill 的关系 |
|-------|------|------------------|
| `perf-hotspot` | perf stat、record、annotate、SPE、PMU、带宽采集 | 提供指令级和事件级原始数据 |
| `devkit-perf` | devkit top-down 基本使用和指标初诊 | 判断宏观瓶颈类别 |
| `perf-topdown` | top-down 与 perf 数据交叉验证 | 验证瓶颈解释是否一致 |
| `theory-driven-pipeline-optimization` | 指令成本建模，推导理论 cycles 下界和性能上限 | 把采集数据转成理论上限、headroom 和优化决策 |

## 目录结构

```text
theory-driven-pipeline-optimization/
├── SKILL.md
├── README.md
└── references/
    ├── instruction-cost-model.md
    ├── microbenchmark-checklist.md
    └── report-template.md
```

## 参考文档

- `references/instruction-cost-model.md`：核心指令选择、latency/throughput/mix 微基准、理论 cycles 推导。
- `references/microbenchmark-checklist.md`：微基准设计和可信度检查清单。
- `references/report-template.md`：理论性能上限分析报告模板。

## 当前限制

- 需要用户提供可运行的 benchmark、源码、汇编或算法伪代码之一。
- 理论上限依赖目标 CPU 和频率；不同微架构必须重新测核心指令成本。
- 如果 workload 受 I/O、锁、系统调用或跨进程通信主导，本 Skill 只能分析其中已定位出的 CPU hot kernel。
- 模型结论必须用真实 benchmark 复核，不能只凭静态指令数定论。
