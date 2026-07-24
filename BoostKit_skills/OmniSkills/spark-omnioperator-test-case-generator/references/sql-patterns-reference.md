# SQL测试模式规范

---

## 写入类算子SQL模式

**SQL流程**：`DROP TABLE → CREATE TABLE → INSERT 数据 → SELECT 验证写入结果 → EXPLAIN EXTENDED`

**步骤模板**：

```
S1.原生和Omni执行SQL语句
DROP TABLE IF EXISTS {算子英文名小写}_{操作}_{类型名};
CREATE TABLE IF NOT EXISTS {算子英文名小写}_{操作}_{类型名} ({列定义}) [PARTITIONED BY (...)] STORED AS ORC;
INSERT INTO TABLE {表名} VALUES (...), (...), ...;
SELECT * FROM {表名} ORDER BY id;

S2.查看Omni执行计划
EXPLAIN EXTENDED INSERT INTO TABLE {表名} VALUES (...);
```

**预期结果**：

```
E1.执行未报错, 结果正确且与原生一致
E2.执行计划可以查看到{Omni算子名称}
```

---

## 读取类算子SQL模式（固定表，优先模式）

读取类算子**优先使用固定表模式**。当用户提供了固定测试表时，必须使用固定表模式。

**SQL流程**：`SELECT 查询验证 → EXPLAIN EXTENDED`

**步骤模板**：

```
S1.原生和Omni执行SQL语句
SELECT ... FROM {固定表名} [WHERE ...] [GROUP BY ...] [ORDER BY ...];

S2.查看Omni执行计划
EXPLAIN EXTENDED SELECT ... FROM {固定表名} [WHERE ...];
```

**固定表模式规则**：
- 测试步骤中**禁止出现** DROP TABLE、CREATE TABLE、INSERT 语句
- 固定表的数据准备统一写在预置条件中，或作为独立的初始化用例
- SELECT 直接查询固定表，表名使用用户提供的固定表名
- 预置条件中需增加P3：`P3.固定测试表{表名}已创建并包含全类型测试数据`

---

## 读取类算子SQL模式（自建表，回退模式）

当用户**未提供**固定测试表时，回退使用自建表模式。

**SQL流程**：`DROP TABLE → CREATE TABLE → INSERT 准备数据 → SELECT 查询验证 → EXPLAIN EXTENDED`

**步骤模板**：

```
S1.原生和Omni执行SQL语句
DROP TABLE IF EXISTS {算子英文名小写}_{操作}_{类型名};
CREATE TABLE IF NOT EXISTS {算子英文名小写}_{操作}_{类型名} ({列定义}) [PARTITIONED BY (...)] STORED AS ORC;
INSERT INTO TABLE {表名} VALUES (...), (...), ...;
SELECT ... FROM {表名} [WHERE ...] [GROUP BY ...] [ORDER BY ...] [HAVING ...];

S2.查看Omni执行计划
EXPLAIN EXTENDED SELECT ... FROM {表名} [WHERE ...];
```

---

## 读取类SQL模式选择决策

| 判定条件 | 使用模式 | SQL步骤 | 预置条件 |
| :--- | :--- | :--- | :--- |
| 用户提供了固定测试表名或DDL | 固定表模式（优先） | SELECT → EXPLAIN | P1 + P2 + P3(固定表已创建) |
| 用户未提供固定测试表 | 自建表模式（回退） | DROP → CREATE → INSERT → SELECT → EXPLAIN | P1 + P2 |

**固定表模式额外约束**：测试步骤中**禁止出现** DROP TABLE / CREATE TABLE / INSERT

---

## 通用SQL规则

| 规则项 | 强制要求 |
| :--- | :--- |
| DROP/CREATE | 只写一次，禁止重复出现 |
| 表名格式 | `{算子英文名小写}_{操作}_{类型名}`，**禁止**带 "\_native"、"\_omni" 后缀 |
| 存储格式 | 统一 **STORED AS ORC** |
| SELECT验证 | **SELECT \* FROM 表名 ORDER BY id**（分区表按分区键+id排序） |
| SQL注释 | **禁止**在JSON中混入SQL注释（如 `-- 注释`） |
| 开关设置 | **仅开关专项测试用例**需写SET命令，其他正常功能测试用例一律不写 |
| 动态分区 | 需在S1步骤开头写 `SET hive.exec.dynamic.partition=true; SET hive.exec.dynamic.partition.mode=nonstrict;` |
| 分区表 | PARTITIONED BY字段为该测试的数据类型；非分区表**禁止**使用PARTITIONED BY子句 |

---

## 各功能语义类算子的SELECT查询模式

| 算子语义 | 典型SELECT模式 | 示例 |
| :--- | :--- | :--- |
| 扫描类 | SELECT \* / SELECT 指定列 | `SELECT * FROM t ORDER BY id` / `SELECT c_int, c_string FROM t ORDER BY id` |
| 过滤投影类 | SELECT ... WHERE 条件 | `SELECT * FROM t WHERE c_int > 0 ORDER BY id` |
| 聚合类 | SELECT 聚合函数 GROUP BY | `SELECT c_int, COUNT(*), SUM(c_long) FROM t GROUP BY c_int ORDER BY c_int` |
| 排序类 | SELECT ... ORDER BY | `SELECT * FROM t ORDER BY c_int ASC NULLS FIRST` |
| 关联类 | SELECT ... FROM t1 JOIN t2 ON | `SELECT * FROM t1 INNER JOIN t2 ON t1.id = t2.id ORDER BY t1.id` |
| 窗口类 | SELECT 窗口函数 OVER | `SELECT id, ROW_NUMBER() OVER (PARTITION BY c_int ORDER BY id) FROM t` |

---

## 读取类查询注意事项

| 注意项 | 说明 |
| :--- | :--- |
| ORDER BY稳定性 | SELECT验证必须加ORDER BY确保结果顺序确定，否则双路径对比可能因行序不同而误判 |
| NULL排序位置 | 不同算子对NULL排序位置不同（NULLS FIRST/NULLS LAST），验证时需明确指定 |
| 空表查询 | 必须包含空表查询场景，验证算子对零行输入的处理 |
| 单行查询 | 必须包含单行结果场景，验证边界情况 |
| 大结果集 | 需包含返回大量行的场景，验证算子在大数据量下的正确性 |
| 谓词下推 | WHERE条件可能被优化器下推到Scan层，需确认过滤是在Omni算子层执行而非Scan层 |
| 分区裁剪 | 分区表查询时需验证分区裁剪是否正确，裁剪后Omni算子仍需正常触发 |
| 数据倾斜 | 关联/聚合类算子需设计倾斜数据场景（如某分组值占比>80%），验证算子对倾斜的处理 |
| 隐式类型转换 | WHERE条件中不同类型比较可能触发隐式转换（如INT与STRING比较），需注意是否影响Omni触发 |
| 子查询 | 部分算子在子查询中的行为可能与主查询不同，需单独验证 |
| 多表关联顺序 | 关联类算子需注意表的大小和关联顺序对执行计划的影响，不同顺序可能触发不同Join策略 |
