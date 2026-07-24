# omnioperator-status-analysis

OmniOperator 算子生态分析技能 —— 全链路扫描 Spark / Gluten / OmniOperator / Velox 物理算子支持现状，生成覆盖度 Gap 分析报告。

## 功能

对四个代码仓进行静态扫描，必要时补充 E2E 抽样验证，产出报告至 `OmniOperator/docs/operator-status/operator_status_report_<yyyymmdd>.md`，回答：

- 当前 Omni 支持哪些 Spark 物理算子？
- 哪些算子只在 Gluten 侧声明了支持，但 Omni 执行侧还不完整？
- 哪些算子 OmniOperator 后端已有实现，但 Gluten 还没有下推？
- 当前 fallback 主要来自哪些算子或类型限制？
- 与 Velox 相比，Omni 缺哪些算子能力？
- 下一阶段应该优先补哪些算子？

## 前置条件

工作目录根路径下需存在以下代码仓：

```
<workspace-root>/
├── OmniOperator/             ← OmniOperator 仓库（必需）
├── Gluten/                   ← Gluten 仓库（必需）
├── velox/                    ← Velox 仓库（可选，缺失时标注”未验证”）
├── spark/                    ← Spark 仓库（可选，缺失时标注”未验证”）
└── .agents/
    └── skills/
        └── omnioperator-status-analysis/   ← 本技能
            ├── SKILL.md
            ├── README.md
            └── references/
                ├── report-template.md
                └── pitfalls-and-boundaries.md

```

> 缺失的仓库不要阻塞报告，但必须标注”本地缺失，未验证”。目录名可以不同，但需在运行前告知 agent 实际路径。

## 扫描源层次

本 skill 沿完整执行链路逐层采集证据：

```text
Spark physical plan
  -> Gluten backend support / Transformer
  -> Substrait Validator / Converter
  -> Omni PlanNode
  -> local_planner / OperatorFactory
  -> Operator runtime
```

| 层次 | 数据源 | 作用 |
|------|--------|------|
| Spark 物理计划层 | `spark/sql/core/.../execution/*Exec*.scala` | 物理算子全集和触发语义 |
| Gluten 支持声明层 | `OmniBackend.scala` | 是否允许 Omni backend 接管 |
| Gluten Transformer 层 | `OmniSparkPlanExecApi.scala`、`gluten-substrait/.../execution` | 是否能生成 Substrait |
| cpp-omni Validator 层 | `SubstraitToOmniPlanValidator.cpp` | 是否接受 Substrait Rel / 类型 / 模式 |
| cpp-omni Converter 层 | `SubstraitToOmniPlan.cpp` | 是否映射到 Omni PlanNode |
| **Omni 执行层**（主要真相源） | `plannode/`、`local_planner.cpp`、`operator/` | 是否真实执行 |
| Velox 对标层 | `SubstraitToVeloxPlan.cc`、`velox/core`、`velox/exec` | 竞品/上游参考 |

## 关键方法论

**不要用文件数量估算覆盖度。** 只有完整链路都存在，并且没有 fallback / unsupported 证据时，才能判定为完整支持。每个重要结论都要带文件路径和简短证据，说明是哪一层支持或缺失。

**当结论不确定时，报告应标记为”待验证”。** 列出需要补充的 E2E SQL 或源码位置。如果某层源码缺失或未验证，使用”待验证”，不要推测为”支持”。

**表达式缺失不要归类成算子缺失。** 此类问题转交 `omnioperator-expression-analysis` skill。

## 使用方法

和 agent 交互，输入：
帮我分析 OmniOperator 算子生态现状，回溯到 <具体月> 月底的版本。
具体要求：
- OmniOperator：用 2026_330_poc 分支，找到 <具体日期> 最近的 commit checkout 后分析
- Gluten：同样用 2026_330_poc 分支
- Velox、Spark：用各自主分支即可
产出报告到 OmniOperator/docs/operator-status/
