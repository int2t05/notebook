# Q45 ExistenceJoin Case

## 问题现象

- SQL：`q45_1.sql`
- 数据库：`tpcds_bin_partitioned_varchar_orc_5`
- Native Spark：返回 `100` 行
- Original Omni：返回 `93` 行
- 关闭 `spark.gluten.sql.columnar.broadcastJoin=false` 后，Omni 与 Native 重新一致

## 版本信息

- OmniOperator repo：`https://gitcode.com/helloxteen_/OmniOperator.git`
- OmniOperator branch：`issue/q45_1`
- OmniOperator commit：
  - 加检查定位：`ab3e58da`
  - 修复版本：`c1987928`
- Gluten repo：`https://gitcode.com/helloxteen_/Gluten.git`
- Gluten branch：`issue/q45_1`
- Gluten commit：`deff6c39`

## skill 执行步骤

本案例的主路径为：结果对比 -> columnar toggle 定位 -> 物理计划确认 -> native 链路加检查 -> 修复验证。

1. 使用 `run_e2e_sql_native` 获取 Spark 基线
2. 使用 `run_e2e_sql` 复现 Omni 结果不一致
3. 使用 `debug_e2e_sql_columnar` 逐个关闭列式算子
4. 观察到 `broadcastJoin=false` 后结果恢复一致
5. 使用 `EXPLAIN EXTENDED` 确认物理计划为 `BroadcastHashJoin + ExistenceJoin`
6. 在 `LookupJoin` 的 ExistenceJoin 链路增加状态检查
7. 重新编译并回归 `q45_1.sql`

## 关键证据

- `debug_e2e_sql_columnar` 显示：
  - `Original Omni`：`match_exact = no`
  - `spark.gluten.sql.columnar.broadcastJoin=false`：`match_exact = yes`
- `EXPLAIN EXTENDED` 显示：

```text
BroadcastHashJoin [i_item_id], [i_item_id], ExistenceJoin(exists#...), BuildRight
```

- native 调试输出显示 ExistenceJoin 为分批输出：

```text
BuildOutput rowCount=1745 probeRowOffset=1745 probeRowCount=1745 existIndexSize=3490
BuildOutput rowCount=606  probeRowOffset=3490 probeRowCount=606  existIndexSize=4096
```

这说明 `existJoinBuildIndex` 是累计缓存，而当前输出只消费其中一个窗口。

## 根因

`LookupJoinOutputBuilder::ConstructExistenceColumn()` 在构造 existence 输出列时，
直接从 `existJoinBuildIndex.begin()` 整段拷贝累计缓存，没有按当前输出窗口
`[probeRowOffset, probeRowOffset + numRows)` 切片。

## 修复

- 在 `ConstructExistenceColumn()` 中：
  - 将 `numRows` 改为当前批次输出行数 `min(probeRowCount, maxRowCount)`
  - 从 `existJoinBuildIndex.begin() + probeRowOffset` 开始拷贝
  - 增加窗口越界检查

## 验证结果

- 修复后，`run_e2e_sql(q45_1.sql)` 返回 `100` 行
- `run_e2e_sql_native(q45_1.sql)` 返回 `100` 行
- `debug_e2e_sql_columnar(q45_1.sql)` 中 `Original Omni` 已经：
  - `match_exact = yes`
  - `match_sorted = yes`

## 对应经验

- 参见 `omnioperator-debugger-workflow.md` 中的 `BroadcastHashJoin + ExistenceJoin 专项经验`
- 这个案例适合作为：
  - `BroadcastHashJoin + ExistenceJoin` 路径的代表性样例
  - “如何用 skill 从 SQL 结果差异定位到 output window 问题”的模板

## 后续可抽象的 knowledge 点

- `BroadcastHashJoin + ExistenceJoin` 不应直接套普通 join 的输出路径分析
- 当 `debug_e2e_sql_columnar` 显示 `broadcastJoin=false` 后结果恢复一致时，应优先检查 ExistenceJoin 专用链路
- `existJoinBuildIndex` 如果是累计缓存，`BuildOutput / ConstructExistenceColumn` 必须按当前输出窗口切片
- `probeRowOffset`、`probeRowCount`、`existJoinBuildIndex.size()` 是 ExistenceJoin 分批输出问题的核心观察变量
