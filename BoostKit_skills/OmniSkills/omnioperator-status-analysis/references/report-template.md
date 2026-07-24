# 算子现状报告模板

## 状态分级

| 状态 | 判定标准 |
|------|----------|
| 完整支持 | Spark/Gluten 开关、Transformer、Substrait Validator、Substrait 转 Omni、Omni PlanNode、OperatorFactory/Operator 均存在；如有条件，E2E 计划出现 `XxxExecTransformer` 且无 fallback |
| 部分支持 | 链路中部分层存在，但存在类型、模式、配置、JoinType、Aggregate mode、Sort ordering、Window frame 等限制 |
| 仅前端 | Gluten 支持开关或 Transformer 存在，但 cpp-omni / OmniOperator 执行侧缺失或 Validator 会拒绝 |
| 仅后端 | OmniOperator 已有 PlanNode/Operator，但 Gluten 未生成或未下推该算子 |
| 不支持 | 关键入口不存在，或显式 fallback / unsupported |
| 待验证 | 静态信号不足，需 E2E 或源码补充确认 |

## 报告结构

```markdown
# OmniOperator 算子支持现状分析报告

## 1. 执行摘要
- 总体结论
- 完整支持 / 部分支持 / 不支持 / 待验证数量
- Top gaps
- 建议优先级

## 2. 扫描范围与数据源
- 仓库路径和分支/commit
- 已扫描文件
- 未覆盖的数据源
- 是否执行 E2E 抽样

## 3. 算子支持总览矩阵
| Spark 物理算子 | Gluten 支持声明 | Transformer | Substrait Rel | Validator | Omni PlanNode | OperatorFactory/Operator | Velox 对标 | 状态 | 置信度 | 备注 |

## 4. 分层发现
### 4.1 Spark 物理算子全集
### 4.2 Gluten Omni backend 下推入口
### 4.3 Substrait Validator / Converter
### 4.4 OmniOperator 执行侧
### 4.5 Velox 对标

## 5. 重点 Gap 清单
| Gap | 影响算子 | 证据 | 严重度 | 修复复杂度 | 建议 |

## 6. 类型与模式限制
| 算子 | 类型/模式维度 | 当前行为 | 风险 | 证据 |

## 7. E2E 抽样结果
| SQL | Native 物理节点 | Omni 节点 | Fallback | 结论 |

## 8. 优先级建议
| 优先级 | 算子/Gap | 原因 | 建议后续 skill |

## 9. 附录：关键 grep 证据
```

## 证据格式

每个重要结论都要给出文件路径和简短证据，例如：

```text
Gluten/backends-omni/.../OmniBackend.scala: supportSortExec = true
Gluten/cpp-omni/src/substrait/SubstraitToOmniPlan.cpp: ToOmniPlan(SortRel) -> SortNode
OmniOperator/core/src/...: SortNode -> SortOperatorFactory
```

不要只写“代码里支持”。要说明是哪一层支持、哪一层缺失。
