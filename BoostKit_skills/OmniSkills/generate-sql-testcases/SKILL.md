---
name: generate-sql-testcases
description: 为Spark表达式生成测试SQL用例。读取包含Spark函数信息的CSV文件，为每个函数生成19种数据类型的测试SQL并输出到新CSV。使用场景：用户需要为Spark函数生成测试SQL、处理CSV中的表达式列表、批量生成SQL测试用例、或涉及OmniOperator/gluten-velox表达式兼容性测试。触发关键词包括但不限于：生成测试SQL、表达式测试、SQL测试用例、Spark函数测试、批量生成SQL、数据类型测试、Spark表达式CSV、OmniOperator测试、gluten-velox测试。即使用户没有明确提到"skill"或"脚本"，只要涉及从CSV中的函数列表生成SQL测试，就应使用此skill。
---

# Spark表达式测试SQL生成

读取包含Spark表达式信息的CSV文件，为每个表达式生成19种数据类型的测试SQL，输出到新的CSV文件。

## 使用方法

运行脚本：
```bash
# 默认模式（白名单过滤）：只为合理的数据类型组合生成SQL
python3 scripts/generate_sql_testcases.py <输入CSV> <输出CSV>

# 全类型模式：对所有19种数据类型都生成SQL（向后兼容）
python3 scripts/generate_sql_testcases.py <输入CSV> <输出CSV> --all
```

**直接运行脚本即可，不要自己写脚本。** 脚本会自动识别函数类型并生成正确的SQL。

默认使用白名单模式——例如 `abs` 只对数值类型生成SQL，`upper` 只对字符串类型生成SQL，不支持的类型列标记为 `ns`。加 `--all` 可对所有类型生成SQL（旧行为）。

## 输入要求

CSV文件必须包含以下列：
- `spark表达式(Spark Functions)` — 函数名
- `Spark类(Spark Expressions)` — Spark类名
- `函数类型` — 标量函数/聚合函数/窗口函数
- `Spark表达式功能简述` — 函数描述

## 输出格式

输出CSV保留原始列，新增：
- `状态`列（标记为"已完成"）
- 19个数据类型列（BOOLEAN ~ STRUCT(ROW)），每列包含对应的测试SQL

已有"已完成"状态的函数会被跳过，不会重复处理。

## SQL生成规则

脚本按以下规则生成SQL：

1. **无参数函数**：`SELECT pi() FROM sve_exp_operator_panoramic;`
2. **单参数函数**：`SELECT abs(c_int) FROM sve_exp_operator_panoramic;`
3. **多参数函数**：根据函数签名自动填充，如 `SELECT add_months(c_date, 1)`
4. **窗口函数**：自动添加 `OVER (ORDER BY c_int)`
5. **运算符**：如 `SELECT c_int + c_int`、`SELECT -c_int`

**禁止**：不使用CAST、不添加WHERE子句、不添加额外函数。

## 脚本内部机制

脚本维护了两个核心配置：

1. **FUNC_SQL_TEMPLATES**：函数签名配置表，覆盖 ~170 个已知函数的SQL模板。新增函数只需在字典中添加一行。

2. **FUNC_SUPPORTED_TYPES**：白名单配置，定义每个函数支持的数据类型。将函数按类别分组：
   - 数值函数（abs, sqrt...）→ BYTE ~ DECIMAL128
   - 字符串函数（upper, trim...）→ STRING, CHAR, VARCHAR
   - 日期函数（day, month...）→ DATE, TIMESTAMP
   - 数组函数（array_sort...）→ ARRAY
   - 无参数函数（pi, rand...）→ 所有类型

不在白名单中的函数默认对所有类型生成SQL。

## 示例文件

- [输入示例](examples/example_input.csv) — 10个代表性函数的CSV输入
- [输出示例](examples/example_output.csv) — 白名单模式下的对应输出

## 参考资料

- [数据类型和表结构参考](references/data_types.md) — 19种数据类型映射、表DDL、测试数据示例
