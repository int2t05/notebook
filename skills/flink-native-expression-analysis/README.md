# flink-native-expression-analysis

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时替换。

Flink SQL 表达式 native 支持分析技能 —— 扫描 Flink SQL 表达式在 OmniStream native 路径的**三层**支持现状(OmniOperator native 注册 / OmniAdaptor Java 决策 / 离线字典),生成三层一致性 + 缺口分析报告。

## 功能

扫描本项目三仓库(OmniAdaptor / OmniOperator / OmniStream),产出报告至 `OmniOperator/docs/expression-analysis/expression_analysis_report_<yyyymmdd>.md`,回答:

- OmniOperator native 实际注册了哪些表达式(Layer A)?各支持哪些类型?
- OmniAdaptor Java 运行时放行哪些表达式(Layer B,硬编码 Map + 白名单)?
- OmniAdaptor 离线字典声称支持哪些表达式(Layer C,`is_support_func`)?
- 三层一致性如何?哪些"声称支持但 native 未实现"(如 `CHAR_LENGTH`)?优先级?

## 前置条件

工作目录根路径下需存在以下代码仓(本项目三仓库,本地均有):

```
<workspace-root>/
├── OmniAdaptor/              ← OmniAdaptor 仓库(必需,Layer B + Layer C)
│   └── omnistream/omniop-flink-extension/   ← Java 决策层
│   └── omnihelper/                          ← 离线字典 + Python 工具
├── OmniOperator/             ← OmniOperator 仓库(必需,Layer A + 报告输出)
│   └── docs/expression-analysis/            ← 分析报告输出(本技能自动创建)
├── OmniStream/               ← OmniStream 仓库(必需,算子调用点)
│   └── cpp/streaming/api/operators/StreamCalcBatch.{h,cpp}
├── velox/                    ← Velox 仓库(已拉取 shallow main,Step 7 业界基准)
└── Gluten/                   ← Gluten 仓库(已拉取 shallow main,Step 7 Spark→Substrait 映射)
```

> 目录名可不同,运行前告知 agent 实际路径。

## 扫描源层次(三层)

| 层次 | 数据源 | 作用 |
|------|--------|------|
| **Layer A — native 注册层**(主要真相源) | `OmniOperator/core/src/vectorization/registration/*.cpp` + `codegen/func_registry_*.cpp` + `aggregator_factory.cpp` | native 运行时实际可执行的表达式 |
| **Layer B — Java 决策层**(运行时放行) | `OmniAdaptor/.../RexNodeUtil.java`(4 硬编码 Map)+ `OmniGraphOverride.java`(INVALID 回退)+ `ValidateCalcOPStrategy.java`(白名单) | 运行时实际放行集(不读字典) |
| **Layer C — 离线字典层**(声称支持) | `OmniAdaptor/omnihelper/resources/{flink,omni}_function_dictionary.json`(`is_support_func`) | omnihelper Python 离线工具的声称清单,与运行时无耦合 |
| OmniStream 算子调用点 | `OmniStream/cpp/streaming/api/operators/StreamCalcBatch.{h,cpp}` | `JSONParser → ExpressionEvaluator(preferVectorization=true)` → codegen;`collectUnsupportedExprImpl` 兜底 |

> **关键**:运行时支持集 = Layer A ∩ Layer B;Layer C 与运行时无耦合。缺口分析重点 = 三层不一致(如字典声称支持但 native 未注册)。

## 关键方法论

**不要用文件数量估计覆盖度。** `functions/*.h` 文件数远多于实际注册表达式数(一个 `Register*.cpp` 可注册几十个函数,每个多类型重载)。始终以 `registration/` 目录为主要数据源。

**通过 `RegistrationHelpers.h` 判断类型覆盖。** `RegisterUnaryDecimal<T>` 等模板 helper 是否被调用决定 DECIMAL 是否支持。helper → 类型映射见 [`references/source_paths.md`](references/source_paths.md)。

**用全量 grep 确认表达式是否已注册:**
```bash
grep -r '"func_name"' OmniOperator/core/src/vectorization/registration/
```
无匹配 = 确认未注册。

**三层独立扫描再交叉。** Layer A/B/C 是独立数据源,分别扫后做一致性缺口分析。

## 使用方法

和 agent 交互,输入:
```
帮我分析 Flink SQL 表达式在 OmniStream native 的支持现状。
要求:
- 三仓库用 <branch> 分支(OmniStream/OmniAdaptor),OmniOperator 用对应 commit
- 三层扫描:native 注册(Layer A)/ Java 决策(Layer B)/ 离线字典(Layer C)
- 重点排查"字典声称支持但 native 未实现"缺口(如 CHAR_LENGTH)
产出报告到 OmniOperator/docs/expression-analysis/
```

## 边界(不做什么)

| 不做 | 转交 |
|------|------|
| 实现缺失函数 | `omnioperator-expression-dev` |
| 适配 / 编译 / 测试 | `omniadaptor-vectorized-expression` / `omnistream-build-deploy` / `omnistream-expression-test` |

本 skill 只产出分析报告,为"接下来实现/适配哪些函数"提供优先级依据。纯只读分析,不改代码。
