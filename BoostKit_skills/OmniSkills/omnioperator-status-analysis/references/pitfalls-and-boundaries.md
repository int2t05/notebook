# 常见误判与 Skill 边界

## 常见误判

- 只看到 `ExecTransformer` 类存在，就判定支持。必须继续检查 backend support 开关、Substrait Validator、Converter 和 Omni 执行侧。
- 只看到 `supportXxxExec = true`，就判定支持。可能 `genXxxExecTransformer` 返回 `null`，或 cpp-omni Validator 拒绝。
- 只看到 OmniOperator 有 Operator，就判定 Spark 能下推。Gluten 侧可能没有生成该 PlanNode。
- 用 SQL 结果正确判定算子支持。Spark 可能已经 fallback 到 JVM 路径，需要看物理计划和 fallback warning。
- 把 `Project` / `Filter` 中的表达式缺失归类为算子缺失。表达式 gap 应转交 `omnioperator-expression-analysis`。
- 把文件名或类名数量当成覆盖率。覆盖率必须以完整执行链路为准。
- 把 Spark 语义等价 SQL 当成同一物理算子验证 SQL。E2E 抽样必须确认物理计划出现目标 `XxxExec` 或 `XxxExecTransformer`。

## 与其他 skill 的边界

- 需要表达式覆盖度、函数类型矩阵、Omni 注册表达式清单时，使用 `omnioperator-expression-analysis`。
- 要实现或补齐具体算子时，切换到对应的算子开发 skill。
- 只需要某个算子的实现前设计文档时，切换到对应的算子设计 skill。
- 算子已实现但性能不达标时，切换到对应的性能优化 skill。

## 交付前自检

- 报告中每个“完整支持”结论都能追溯到完整链路证据。
- “部分支持”明确写出限制维度，例如类型、join type、aggregate mode、window frame、sort ordering。
- 未扫描到的仓库或远端验证缺口已在扫描范围中说明。
- Top gaps 均给出严重度、修复复杂度和建议后续 skill。
