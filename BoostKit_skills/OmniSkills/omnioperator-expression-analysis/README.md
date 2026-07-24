# omnioperator-expression-analysis

OmniOperator 表达式生态分析技能 —— 系统扫描 OmniOperator / Velox / Spark SQL 三方表达式支持现状，生成覆盖度 Gap 分析报告。

## 功能

对三个代码仓进行静态扫描，产出报告至 `OmniOperator/docs/expression-analysis/expression_analysis_report_<yyyymmdd>.md`，回答：

- OmniOperator 向量化框架已注册哪些表达式？各支持哪些类型？
- Velox（Meta 开源向量化引擎）覆盖了哪些 Spark SQL 表达式？
- Omni 与 Velox / Spark SQL 标准之间的差距是什么？优先级如何？

## 前置条件

工作目录根路径下需存在以下代码仓：

```
<workspace-root>/
├── OmniOperator/             ← OmniOperator 仓库（必需）
│   └── docs/
│       ├── expression-analysis/   ← 分析报告输出（本技能自动创建）
│       │   └── expression_analysis_report_<yyyymmdd>.md
│       └── ...
├── Gluten/                   ← Gluten 仓库（必需）
├── velox/                    ← Velox 仓库（必需）
├── spark/                    ← Spark 仓库（可选，缺失时用内置分类表估算，精度有限）
└── .agents/
    └── skills/
        └── omnioperator-expression-analysis/   ← 本技能
            ├── SKILL.md
            └── README.md
```

> 目录名可以不同，但需在运行前告知 agent 实际路径。

## 扫描源层次

| 层次 | 数据源 | 作用 |
|------|--------|------|
| Gluten 意图层 | `Gluten/gluten-substrait/.../ExpressionMappings.scala` | Gluten 尝试下推的表达式权威全集 |
| **Omni 注册层**（主要真相源） | `OmniOperator/core/src/vectorization/registration/*.cpp` | 向量化框架运行时实际可调用的表达式 |
| Omni 运行时限制层 | `Gluten/backends-omni/.../OmniExpressionAdaptor.scala` | Scala 层类型检查，已注册表达式在此也可能回退 |
| Velox 参考层 | `velox/velox/functions/sparksql/registration/Register*.cpp` | 业界对标基准 |
| Omni 聚合层 | `OmniOperator/.../aggregator_factory.cpp` | 聚合表达式 dispatch 工厂 |

## 关键方法论

**不要用文件数量估计覆盖度。** `functions/*.h` 有 107 个文件，但实际注册表达式 ~210+，类型签名 ~1,100+。始终以 `registration/` 目录为主要数据源。

**通过 `RegistrationHelpers.h` 判断类型覆盖。** `RegisterUnaryDecimal<T>` 等模板辅助函数决定 DECIMAL 是否被支持。`abs`/`round`/`ceil`/`floor` 调用了整数/浮点辅助函数但遗漏了 DECIMAL 辅助函数——已确认的 DECIMAL 缺口，修复成本低。

**用全量 grep 确认表达式是否已注册：**

```bash
grep -r '"func_name"' OmniOperator/core/src/vectorization/registration/
```

无匹配 = 确认未注册。

## 使用方法

和agent交互，输入：
帮我分析 OmniOperator 表达式生态现状，回溯到 <具体月> 月底的版本。
具体要求：
- OmniOperator：用 2026_330_poc 分支，找到 <具体日期> 最近的 commit checkout 后分析
- Gluten：同样用 2026_330_poc 分支
- Velox、Spark：用各自主分支即可
产出报告到 OmniOperator/docs/expression-analysis/