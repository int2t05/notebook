# 关联类算子（HashJoin/SortMergeJoin）速查卡

> 覆盖多表JOIN场景，重点关注Join类型、关联条件、执行模式及key倾斜与NULL处理。

## 算子基础信息

数据流向=读取类 | 功能语义=关联类 | Omni算子=OmniBroadcastHashJoinExecTransformer/OmniShuffledHashJoinExecTransformer/OmniSortMergeJoinExecTransformer | SQL模式=读取类SQL模式 | 开关=spark.omni.sql.columnar.broadcastJoin/spark.omni.sql.columnar.shuffledHashJoin/spark.omni.sql.columnar.sortMergeJoin

## 输入因子

| 因子编号 | 因子分类 | 因子名称 | 全量可选值 | 影响权重 |
| :--- | :--- | :--- | :--- | :--- |
| F001 | 核心功能因子 | Join类型 | INNER / LEFT OUTER / RIGHT OUTER / FULL OUTER / LEFT SEMI / LEFT ANTI / CROSS / EXISTENCE | 极高 |
| F002 | 条件配置因子 | 关联条件类型 | 单字段等值/多字段复合等值/含函数等值/非等值(回退) | 极高 |
| F003 | 条件配置因子 | 开关状态 | 开启(默认) / 关闭 | 极高 |
| F004 | 输入数据特征因子 | 左表数据量级 | 空表/单条/小表(1W行)/中表(100W行)/大表(1亿行) | 高 |
| F005 | 输入数据特征因子 | 右表数据量级 | 空表/单条/小表/中表/大表 | 高 |
| F006 | 输入数据特征因子 | 关联key特征 | 无重复key/全重复key/无匹配key/全NULL key/大key倾斜/均匀分布 | 极高 |
| F007 | 执行配置因子 | Join执行模式 | Broadcast Join / Sort Merge Join / Shuffle Hash Join | 高 |
| F008 | 输入数据特征因子 | 数据类型 | 同写入类F003 | 极高 |

## 测试场景清单

| 场景编号 | 场景分类 | 场景描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| J-001 | 开关测试 | 开关开启/关闭场景 | Level0 |
| J-002 | Join类型 | INNER JOIN | Level0 |
| J-003 | Join类型 | LEFT OUTER JOIN | Level0 |
| J-004 | Join类型 | RIGHT OUTER JOIN | Level0 |
| J-005 | Join类型 | FULL OUTER JOIN | Level0 |
| J-006 | Join类型 | LEFT SEMI JOIN | Level0 |
| J-007 | Join类型 | LEFT ANTI JOIN | Level0 |
| J-008 | Join类型 | CROSS JOIN | Level1 |
| J-009 | 关联条件 | 单字段等值关联 | Level0 |
| J-010 | 关联条件 | 多字段复合等值关联 | Level0 |
| J-011 | 关联条件 | 含函数等值关联 | Level1 |
| J-012 | 关联条件 | 非等值关联（回退场景） | Level1 |
| J-013 | 数据特征 | 空表关联 | Level0 |
| J-014 | 数据特征 | 大key倾斜关联 | Level0 |
| J-015 | 数据特征 | 全NULL key关联 | Level0 |
| J-016 | 数据特征 | 无匹配key关联 | Level1 |
| J-017 | 数据特征 | 全重复key关联 | Level1 |
| J-018 | 执行模式 | Broadcast Join | Level0 |
| J-019 | 执行模式 | Sort Merge Join | Level0 |
| J-020 | 执行模式 | Shuffle Hash Join | Level1 |
| J-021 | 数据类型 | 各数据类型关联 | Level0 |
| J-022 | 边界值 | 边界值关联 | Level0 |
| J-023 | 异常 | 关联条件列不存在 | Level2 |
| J-024 | 异常 | 类型不匹配关联 | Level2 |

