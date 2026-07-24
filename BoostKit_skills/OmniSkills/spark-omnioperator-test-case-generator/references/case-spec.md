# 用例生成规范（生成阶段参考）

> 用途：用例生成阶段的核心参考文档，提供JSON字段定义、步骤格式、命名规范、输出样例。

---

## 一、JSON字段定义

每条测试用例必须输出为标准JSON对象，包含以下4个字段，字段名称、值类型、值格式均不可变更。

| 序号 | 字段名 | 值类型 | 填写规则 |
| :- | :--- | :--- | :--- |
| 1 | 用例\_编号 | string | `"Spark_OmniRuntime_{算子英文名}_XXX"`，XXX为3位数字编号，从001递增；算子英文名首字母大写驼峰 |
| 2 | 用例\_名称 | string | 必须以算子名称开头；异常用例必须包含"异常场景"标识 |
| 3 | 用例\_级别 | string | `"Level1"` 固定值 |
| 4 | 用例\_测试步骤 | object | 嵌套对象，键为`step1`/`step2`/…，每个step包含`description`、`sql_statement`、`expected_result`三个子字段 |

---

## 二、测试步骤与预期结果格式

**步骤-预期对应规则**：步骤编号step1/step2…与预期编号E1/E2…一一对应，不混用、不省略。`用例_测试步骤`必须是嵌套对象，每个step包含`description`、`sql_statement`、`expected_result`三个子字段。

**正常功能测试用例（固定两步）**：

| 步骤键 | description | sql_statement | expected_result |
| :- | :--- | :--- | :--- |
| step1 | `S1.原生和Omni执行SQL语句` | 合并原生和Omni执行的完整SQL语句，多条SQL用`\n`分隔 | `E1.执行未报错, 结果正确且与原生一致` |
| step2 | `S2.查看Omni执行计划` | `EXPLAIN EXTENDED {被测SQL}` | `E2.执行计划可以查看到{Omni算子名称}` |

**异常测试用例（固定一步）**：

| 步骤键 | description | sql_statement | expected_result |
| :- | :--- | :--- | :--- |
| step1 | `S1.原生和Omni执行SQL语句` | 触发异常的SQL语句 | `E1.执行报错，提示{具体错误信息}` |

### 各场景预期结果速查

| 场景 | E1预期 | E2预期 |
| :--- | :--- | :--- |
| 支持的数据类型 | `E1.执行未报错, 结果正确且与原生一致` | `E2.执行计划可以查看到{Omni算子名称}` |
| 不支持的数据类型 | `E1.原生和Omni执行结果一致` | `E2.执行计划无法查看到{Omni算子名称}` |
| 开关开启 | `E1.执行未报错, 结果正确且与原生一致` | `E2.执行计划可以查看到{Omni算子名称}` |
| 开关关闭 | `E1.执行未报错, 结果正确且与原生一致` | `E2.执行计划中无{Omni算子名称}` |
| INSERT OVERWRITE | `E1.执行未报错, 结果正确且与原生一致` | `E2.执行计划可以查看到{Omni算子名称}` |
| 异常场景 | `E1.执行报错，提示{具体错误信息}` | 无E2 |

### 双路径对比校验规则

| 输出/行为类型 | 校验维度 | 标准化校验规则 |
| :--- | :--- | :--- |
| 结果数据集 | 数据内容、行数、列数、字段类型、精度、NULL位置、排序 | 双路径执行结果排序后逐行逐列100%完全匹配 |
| 执行状态 | 作业成功/失败状态、执行完成度、重试次数 | 双路径执行状态完全一致 |
| 异常行为 | 异常类型、核心错误信息、抛出时机、处理逻辑 | 双路径异常场景下完全一致 |
| 元数据变化 | 表结构、分区信息、文件统计信息（写入类专属） | 双路径执行后元数据变化完全一致 |
| 可观测指标 | 执行耗时、吞吐量、资源占用、shuffle数据量 | 按对应测试模块规则校验 |

---

## 三、用例名称强制规则

所有用例名称**必须以** `{算子名称}_` **开头**：

| 用例类型 | 命名模板 | 示例 |
| :--- | :--- | :--- |
| 开关测试 | `{算子名称}_开关开启场景测试` / `{算子名称}_开关关闭场景测试` | TableWrite算子\_开关开启场景测试 |
| 单类型基本操作 | `{算子名称}_{类型名}类型{操作}测试` | TableWrite算子\_INT类型写入测试 |
| 组合类型操作 | `{算子名称}_组合类型{操作}测试` | TableWrite算子\_组合类型写入测试 |
| 不支持类型验证 | `{算子名称}_不支持类型{操作}验证` | TableWrite算子\_不支持类型写入验证 |
| 功能语义变体 | `{算子名称}_{语义变体描述}测试` | HashAggregate算子\_COUNT聚合测试 |
| 分区表操作 | `{算子名称}_分区表_{类型名}类型{操作}测试` | TableWrite算子\_分区表\_INT类型写入测试 |
| 动态分区 | `{算子名称}_动态分区_{覆盖范围}{操作}测试` | TableWrite算子\_动态分区\_支持类型全覆盖写入测试 |
| 边界值 | `{算子名称}_边界值_{类型名}类型{操作}测试` | TableWrite算子\_边界值\_INT类型写入测试 |
| 异常场景 | `{算子名称}_异常场景_{异常描述}测试` | TableWrite算子\_异常场景\_列数不匹配写入测试 |

---

## 四、JSON格式要求

- 严格的JSON数组格式，无多余逗号、无缺少逗号
- 禁止SQL注释混入JSON中
- 确保所有字符串正确转义（`\n`表示换行）
- 确保JSON可直接被解析，无格式错误
- `用例_测试步骤`必须是嵌套对象，键为`step1`/`step2`/…，每个step包含`description`、`sql_statement`、`expected_result`
- `sql_statement`中多条SQL语句用`\n`分隔，禁止使用`-- 注释`

---

## 五、JSON输出样例

**样例1：写入类算子正常功能测试（TableWrite）**：

```json
{
  "用例_编号": "Spark_OmniRuntime_Tablewrite_003",
  "用例_名称": "TableWrite算子_BOOLEAN类型写入测试",
  "用例_级别": "Level1",
  "用例_测试步骤": {
    "step1": {
      "description": "S1.原生和Omni执行SQL语句",
      "sql_statement": "DROP TABLE IF EXISTS tablewrite_insert_boolean;\nCREATE TABLE IF NOT EXISTS tablewrite_insert_boolean (id int, c_bool boolean) STORED AS ORC;\nINSERT INTO TABLE tablewrite_insert_boolean VALUES (1, true), (2, false), ...;\nSELECT * FROM tablewrite_insert_boolean ORDER BY id;",
      "expected_result": "E1.执行未报错, 结果正确且与原生一致"
    },
    "step2": {
      "description": "S2.查看Omni执行计划",
      "sql_statement": "EXPLAIN EXTENDED INSERT INTO TABLE tablewrite_insert_boolean VALUES (1, true);",
      "expected_result": "E2.执行计划可以查看到OmniInsertIntoHadoopFsRelationCommand"
    }
  }
}
```

**样例2：读取类-过滤投影算子正常功能测试（Filter）**：

```json
{
  "用例_编号": "Spark_OmniRuntime_Filter_005",
  "用例_名称": "Filter算子_INT类型等值条件过滤测试",
  "用例_级别": "Level1",
  "用例_测试步骤": {
    "step1": {
      "description": "S1.原生和Omni执行SQL语句",
      "sql_statement": "DROP TABLE IF EXISTS filter_eq_int;\nCREATE TABLE IF NOT EXISTS filter_eq_int (id int, c_int int) STORED AS ORC;\nINSERT INTO TABLE filter_eq_int VALUES (1, 100), (2, -100), (3, 0), (4, NULL), ...;\nSELECT * FROM filter_eq_int WHERE c_int = 100 ORDER BY id;",
      "expected_result": "E1.执行未报错, 结果正确且与原生一致"
    },
    "step2": {
      "description": "S2.查看Omni执行计划",
      "sql_statement": "EXPLAIN EXTENDED SELECT * FROM filter_eq_int WHERE c_int = 100;",
      "expected_result": "E2.执行计划可以查看到FilterExecTransformer"
    }
  }
}
```

**样例3：通用异常测试用例**：

```json
{
  "用例_编号": "Spark_OmniRuntime_Filter_050",
  "用例_名称": "Filter算子_异常场景_列不存在查询测试",
  "用例_级别": "Level1",
  "用例_测试步骤": {
    "step1": {
      "description": "S1.原生和Omni执行SQL语句",
      "sql_statement": "DROP TABLE IF EXISTS filter_err_col;\nCREATE TABLE IF NOT EXISTS filter_err_col (id int, c_int int) STORED AS ORC;\nSELECT * FROM filter_err_col WHERE c_not_exist > 0;",
      "expected_result": "E1.执行报错，提示列不存在相关错误信息"
    }
  }
}
```

---

## 六、AI用例生成标准工作流

```
步骤1: 从已加载的测试设计文档（第2章算子签名）获取算子名称、数据流向、功能语义、Omni算子名称、开关配置
步骤2: 从已加载的测试设计文档（第4章输入因子、第5章测试设计方法、第6章测试类型）获取输入因子、测试场景、功能用例规划
步骤3: 查阅 data-type-reference.md → 确定数据类型支持范围、边界值、数据插入规范
步骤4: 查阅 sql-patterns-reference.md → 匹配对应数据流向的SQL测试模式
步骤5: 按设计文档中的覆盖准则(EC/BV/SC/DT/OA/EG)生成用例
步骤6: 查阅本文件「各场景预期结果速查」章节 → 填写预期结果
步骤7: 查阅 case-checklist.md「用例排列顺序」章节 → 按三层结构整理
步骤8: 按本文件JSON格式要求 → 输出标准JSON
```
