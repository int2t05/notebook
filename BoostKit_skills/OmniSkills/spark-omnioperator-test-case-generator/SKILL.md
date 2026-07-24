---
name: spark-omnioperator-test-case-generator
description: |
  当用户需要为Spark OMNI优化算子生成测试用例JSON文件时触发。必须首先检查测试设计文档是否存在；如不存在，提示用户指定文档路径或引导用户使用spark-omnioperator-test-design-generator skill生成。
  覆盖内容：用例标题预览确认、批量生成4字段标准JSON用例、名称-实现一致性强制自检、最终交付报告。
  触发关键词：算子测试用例生成、Spark算子用例JSON、测试用例生成、OMNI算子用例、生成xxx算子测试用例、TableWrite/Filter/HashAggregate/Sort/HashJoin/Window算子测试用例。
---

# Spark OmniOperator 优化算子 — 测试用例生成

为指定Spark OMNI优化算子生成标准化JSON测试用例文件（4字段格式）。

**⚠️ 前置条件**：本skill依赖测试设计文档。生成用例前必须存在由`spark-omnioperator-test-design-generator`生成的测试设计文档。如未找到设计文档，将提示用户指定路径或引导生成。

输出文件：`BigData_Spark_Operator_Test_{OperatorName}_Test_Cases.json`
输出目录：当前工作目录下的`{OperatorName}_Test_Design/`

## 参考文件

`references/` 目录提供参考文件，执行过程中按需加载：

| 文件 | 用途 | 加载时机 | 具体用途 |
|:---|:---|:---|:---|
| [case-spec.md](./references/case-spec.md) | JSON字段定义、步骤格式、命名规范、预期结果速查、输出样例 | Phase 2.1 提取算子信息后 | 了解JSON字段定义和格式要求 |
| [data-type-reference.md](./references/data-type-reference.md) | 数据类型矩阵、边界值规范、数据插入强制规则 | Phase 2.2 提取数据类型后 | 了解边界值规范和数据插入规则 |
| [sql-patterns-reference.md](./references/sql-patterns-reference.md) | 写入类/读取类SQL模式、通用SQL规则 | Phase 2.3 确定数据流向后 | 匹配对应的SQL测试模式 |
| [case-checklist.md](./references/case-checklist.md) | 校验规则、排列顺序、强制约束清单 | Phase 3.1 生成用例前 | 了解排列顺序和校验规则 |
| [data-type-checklist.md](./references/data-type-checklist.md) | 数据类型/边界值/数据质量检视清单 | Phase 3.2 自检阶段 | 检查数据类型覆盖情况 |

**加载顺序说明**：
1. **Phase 2.1**：提取算子信息后，立即加载`case-spec.md`，了解JSON格式要求
2. **Phase 2.2**：提取数据类型后，加载`data-type-reference.md`，了解边界值规范
3. **Phase 2.3**：确定数据流向后，加载`sql-patterns-reference.md`，匹配SQL模式
4. **Phase 3.1**：生成用例前，加载`case-checklist.md`，了解排列顺序和校验规则
5. **Phase 3.2**：自检阶段，加载`data-type-checklist.md`，检查数据类型覆盖

---

# 流程

## Phase 1: 设计文档前置检查

### 1.1 检查设计文档是否存在

按以下优先级定位测试设计文档：

```
优先级：
  1. 用户输入中明确指定的文件路径 → 直接使用，跳过搜索
  2. 默认搜索路径（用户未指定路径时）：
     a. {OperatorName}_Test_Design/
     b. test_design/
     c. 当前工作目录
  目标文件名：{OperatorName}_Test_Design_Document.md
```

| 条件 | 操作 |
|:---|:---|
| 用户指定了路径 | 验证文件存在且有效 → ✅ 进入Phase 2；文件无效 → 🚨 提示用户（见1.2） |
| 未指定路径，搜索到文档 | ✅ 进入Phase 2 |
| 未指定路径，搜索不到文档 | 🚨 提示用户（见1.2） |

### 1.2 设计文档缺失时提示用户

当设计文档缺失时，**不可自动调用其他skill**，必须使用 AskUserQuestion 提示用户选择处理方式：

```
📋 未找到 {OperatorName} 的测试设计文档。

请选择处理方式：
  1. 指定文档路径 — 如果您已有设计文档，请提供文件路径
  2. 生成测试设计文档 — 请使用 spark-omnioperator-test-design-generator skill 生成测试设计文档，完成后再回来生成用例
```

**用户选择"指定文档路径"时**：
1. 接收用户提供的路径
2. 验证文件是否存在且为有效的测试设计文档
3. 验证通过后进入Phase 2

**用户选择"生成测试设计文档"时**：
1. 告知用户可使用 `/spark-omnioperator-test-design-generator` 生成测试设计文档
2. 终止当前skill执行，等待用户完成测试设计文档生成后再次调用本skill

---

## Phase 2: 获取算子信息

读取测试设计文档，提取：
- 算子名称、Omni算子名称
- 数据流向（写入类/读取类）
- 开关配置项
- 用例名称列表
- 总用例规划

### ⚠️ 2.1 用例数量校验（强制）

提取完成后必须执行数量校验：

```
校验规则：
  1. 统计实际提取的用例数量（按编号计数）
  2. 读取设计文档声明的总用例数
  3. 对比两者是否一致
```

| 校验结果 | 操作 |
|:---|:---|
| 数量一致 | ✅ 进入Phase 3 |
| 数量不一致 | 🚨 提示用户并列出差异（见2.2） |

### 2.2 数量不一致时提示用户

当数量不一致时，必须向用户展示差异详情：

```
⚠️ 用例数量校验失败

【设计文档声明】总用例数：XX条
【实际提取数量】YY条
【差异】ZZ条

【缺失用例列表】
- T-XXX: 用例名称1
- T-YYY: 用例名称2

请选择处理方式：
  1. 继续生成 — 使用已提取的YY条用例生成JSON
  2. 补充用例 — 请提供缺失用例的详细信息
  3. 重新提取 — 重新解析设计文档
```

---

## Phase 3: 用例生成

> 📖 JSON字段定义、测试步骤格式、用例命名规范、输出样例等完整规范请阅读 [case-spec.md](./references/case-spec.md)

### 3.1 用例排列顺序

> 📖 完整规则请阅读[case-checklist.md](./references/case-checklist.md)「用例排列顺序」章节

```
第一层（基础验证）：开关测试 → 单类型基础操作（13种类型）→ 组合类型 → 不支持类型验证
第二层（功能深化）：按算子速查卡子项差异化排列（写入模式/Join类型/聚合函数/分区类型等）
第三层（质量保障）：边界值 → NULL处理 → 格式验证 → 异常测试（异常始终在最后）
```

### ⚠️ 3.2 标题预览检查点

**在正式生成JSON之前，必须展示所有用例标题并等待用户确认：**

```
📋 用例生成规划，请确认：

【用例数量】
  - 功能测试：XX条 / 性能测试：XX条 / 可靠性测试：XX条 / 兼容性测试：XX条 / 总计：XX条

【功能用例标题】
  001. {OperatorName}_开关开启场景测试
  002. {OperatorName}_INT类型_{操作}_测试
  ...（列出全部）

【性能/可靠性/兼容性用例标题】
  ...（按类别列出）
```

### 3.3 正式生成与批量交付

当用例总数超过30条时：
1. 先生成前10条用例，用户确认格式和质量
2. 用户确认后，继续生成剩余批次
3. 每批次生成后执行自检

### ⚠️ 3.4 生成后强制自检

> 📖 完整校验规则与强制约束清单请阅读 [case-checklist.md](./references/case-checklist.md)
> 📖 数据类型检视请阅读 [data-type-checklist.md](./references/data-type-checklist.md)

每批次用例生成后执行**六项自检**：

| 自检项 | 不通过条件 | 严重程度 |
|:---|:---|:---|
| 格式完整性 | 字段数量≠4、缺少step、缺少description/sql_statement/expected_result | ❌ 必须修复 |
| 异常用例格式 | 异常用例包含step2、异常用例expected_result不含"执行报错" | ❌ 必须修复 |
| 名称-实现一致性 | 去掉类型/模式后，步骤无法区分 | ⚠️ 建议修复 |
| 数据类型 | 名称中标注的类型未使用边界值 | ⚠️ 建议修复 |
| 功能模式 | 步骤未体现该模式的本质特征 | ⚠️ 建议修复 |
| 预期结果 | 与同类用例完全相同 | ⚠️ 建议修复 |

**异常用例格式检查规则**：

```
FOR EACH 用例:
  IF 用例_名称 CONTAINS "异常场景" THEN
    CHECK 用例_测试步骤 NOT HAS step2  // 异常用例只有step1
    CHECK step1.expected_result CONTAINS "执行报错"  // 预期结果必须是报错
    CHECK step1.sql_statement CONTAINS  // SQL必须能触发错误
      "不匹配" → SQL包含列数/类型不匹配的INSERT
      "超长" → SQL包含超长字符串的INSERT
      "溢出" → SQL包含溢出数据的INSERT
      "未开启" → SQL包含未启用配置的操作
  END IF
END FOR
```

### 3.5 最终交付报告

```
📊 {OperatorName} 测试用例生成完成

【用例统计】功能XX条 / 性能XX条 / 可靠性XX条 / 兼容性XX条 / 总计XX条
【自检结果】名称-实现一致性 XX/XX / 数据类型 XX/XX / 功能模式 XX/XX / 预期结果 XX/XX
【输出文件】BigData_Spark_Operator_Test_{OperatorName}_Test_Cases.json
```

---

## 规则

### 四大铁律

| # | 铁律 | 含义 |
|:---|:---|:---|
| 1 | 单变量控制 | 仅控制"是否启用OMNI优化" |
| 2 | 原生基准 | 所有预期以原生Spark算子行为为基准 |
| 3 | 纯黑盒 | 仅通过外部可观察行为测试 |
| 4 | 名称-实现一致性 | 名称中标注的特征必须在步骤中体现 |

### SQL生成规范

**通用约束**：
- 表名：`{operator_name_lowercase}_{operation}_{type_name}`
- 存储格式统一`STORED AS ORC`
- SELECT验证统一添加`ORDER BY id`
- 非异常用例INSERT ≥ 20行

**写入类SQL**：`DROP → CREATE → INSERT(≥20行) → SELECT ORDER BY id → EXPLAIN EXTENDED INSERT`

**读取类SQL**：有固定表 → `SELECT → EXPLAIN`；无固定表 → `DROP → CREATE → INSERT → SELECT → EXPLAIN`
