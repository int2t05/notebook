# spark-omnioperator-test-case-generator

为 Spark OMNI 优化算子生成标准化 JSON 测试用例文件（4字段格式）。

## 功能

- 自动检查测试设计文档是否存在，缺失时引导用户选择处理方式
- 基于设计文档批量生成 4 字段标准 JSON 测试用例
- 生成前展示用例标题预览，等待用户确认
- 生成后执行六项强制自检（格式完整性、异常用例格式、名称-实现一致性、数据类型、功能模式、预期结果）
- 输出最终交付报告

## 前置依赖

本 skill 依赖测试设计文档（由 `spark-omnioperator-test-design-generator` skill 生成）。生成用例前必须存在对应算子的测试设计文档，如未找到将提示用户指定路径或引导生成。

## 使用方式

向 AI 提供算子名称及测试设计文档路径即可触发，例如：

- "请生成tablewrite的测试用例，测试设计文档见 `/path/to/TableWrite_Test_Design_Document.md`"
- "帮我生成 HashJoin 算子的测试用例"
- "生成 Sort 算子的 OMNI 用例 JSON"

## 目录结构

```
spark-omnioperator-test-case-generator/
├── SKILL.md                       # 核心指令文件
├── README.md                      # 本文件
└── references/                    # 参考文档
    ├── case-spec.md               # 用例生成规范与AI工作流
    ├── data-type-reference.md     # 数据类型矩阵与边界值规范
    ├── sql-patterns-reference.md  # SQL测试模式规范
    ├── case-checklist.md          # 用例生成校验清单与排列顺序
    └── data-type-checklist.md     # 数据类型检视清单
```

## 核心规范

### JSON 用例格式（4字段）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| 用例_编号 | string | `Spark_OmniRuntime_{算子英文名}_XXX`，XXX为3位数字编号 |
| 用例_名称 | string | 必须以算子名称开头；异常用例必须包含"异常场景" |
| 用例_级别 | string | `"Level1"` 固定值 |
| 用例_测试步骤 | object | 嵌套对象，键为 `step1`/`step2`/…，每个step包含 `description`、`sql_statement`、`expected_result` |

### 测试步骤格式

**正常功能测试用例（两步）**：
- step1: `S1.原生和Omni执行SQL语句` → SQL语句 → `E1.执行未报错, 结果正确且与原生一致`
- step2: `S2.查看Omni执行计划` → `EXPLAIN EXTENDED ...` → `E2.执行计划可以查看到{Omni算子名称}`

**异常测试用例（一步）**：
- step1: `S1.原生和Omni执行SQL语句` → 触发错误的SQL → `E1.执行报错，提示{具体错误信息}`

### 用例排列顺序（三层结构）

1. **基础验证层**：开关测试 → 单类型基础操作（13种类型）→ 组合类型 → 不支持类型验证
2. **功能深化层**：按算子速查卡子项差异化排列（写入模式/Join类型/聚合函数/分区类型等）
3. **质量保障层**：边界值 → NULL处理 → 格式验证 → 异常测试（异常始终在最后）

### SQL生成规范

- **写入类模式**：`DROP → CREATE → INSERT(≥20行) → SELECT ORDER BY id → EXPLAIN EXTENDED`
- **读取类模式**：固定表 `SELECT → EXPLAIN` / 自建表 `DROP → CREATE → INSERT → SELECT → EXPLAIN`
- **存储格式**：统一 `STORED AS ORC`
- **开关设置**：仅开关专项测试用例需写SET命令，其他正常功能测试用例一律不写

### 强制自检（六项）

| 自检项 | 不通过条件 | 严重程度 |
|:---|:---|:---|
| 格式完整性 | 字段数量≠4、缺少step、缺少description/sql_statement/expected_result | ❌ 必须修复 |
| 异常用例格式 | 异常用例包含step2、异常用例expected_result不含"执行报错" | ❌ 必须修复 |
| 名称-实现一致性 | 去掉类型/模式后，步骤无法区分 | ⚠️ 建议修复 |
| 数据类型 | 名称中标注的类型未使用边界值 | ⚠️ 建议修复 |
| 功能模式 | 步骤未体现该模式的本质特征 | ⚠️ 建议修复 |
| 预期结果 | 与同类用例完全相同 | ⚠️ 建议修复 |

## 输出

| 文件/产出 | 格式 | 描述 |
|:---|:---|:---|
| BigData_Spark_Operator_Test_{OperatorName}_Test_Cases.json | JSON | 完整测试用例（4字段标准格式），存放于 `{OperatorName}_Test_Design/` 目录 |
| 最终交付报告 | 对话输出 | 用例统计、自检结果、输出文件路径等汇总信息 |
