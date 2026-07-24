# 聚合类算子（HashAggregate/SortAggregate）速查卡

> 覆盖分组聚合场景，重点关注聚合函数类型、分组方式、分组key特征及数据倾斜。

## 算子基础信息

数据流向=读取类 | 功能语义=聚合类 | Omni算子=OmniHashAggregateExecTransformer | SQL模式=读取类SQL模式 | 开关=spark.omni.sql.columnar.hashagg

## 输入因子

| 因子编号 | 因子分类 | 因子名称 | 全量可选值 | 影响权重 |
| :--- | :--- | :--- | :--- | :--- |
| F001 | 核心功能因子 | 聚合函数类型 | COUNT/SUM/AVG/MIN/MAX/COUNT DISTINCT/VARIANCE/STDDEV/COLLECT_LIST/COLLECT_SET/FIRST/LAST | 极高 |
| F002 | 核心功能因子 | 分组类型 | 无分组(全局聚合)/单字段GROUP BY/多字段GROUP BY/ROLLUP/CUBE/GROUPING SETS | 极高 |
| F003 | 条件配置因子 | 开关状态 | 开启(默认) / 关闭 | 极高 |
| F004 | 输入数据特征因子 | 数据类型 | 同写入类F003 | 极高 |
| F005 | 输入数据特征因子 | 分组key特征 | 无重复key/全重复key/高基数(大量不同key)/低基数(少量不同key)/大key倾斜/全NULL key | 极高 |
| F006 | 输入数据特征因子 | 聚合字段特征 | 全正数/含零值/含负数/含NULL/含极大值/含极小值 | 高 |
| F007 | 输入数据特征因子 | 数据量级 | 空表/小表/中表/大表/超大表 | 高 |
| F008 | 条件配置因子 | HAVING子句 | 无HAVING/有HAVING简单条件/有HAVING复杂条件 | 中 |

## 测试场景清单

| 场景编号 | 场景分类 | 场景描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| A-001 | 开关测试 | 开关开启/关闭场景 | Level0 |
| A-002 | 聚合函数 | COUNT / SUM / AVG / MIN / MAX | Level0 |
| A-003 | 聚合函数 | COUNT DISTINCT | Level0 |
| A-004 | 聚合函数 | VARIANCE / STDDEV | Level1 |
| A-005 | 聚合函数 | COLLECT_LIST / COLLECT_SET | Level1 |
| A-006 | 聚合函数 | FIRST / LAST | Level2 |
| A-007 | 分组类型 | 全局聚合（无GROUP BY） | Level0 |
| A-008 | 分组类型 | 单字段GROUP BY | Level0 |
| A-009 | 分组类型 | 多字段GROUP BY | Level0 |
| A-010 | 分组类型 | ROLLUP / CUBE / GROUPING SETS | Level1 |
| A-011 | HAVING子句 | HAVING条件过滤 | Level1 |
| A-012 | 数据特征 | 高基数分组 | Level0 |
| A-013 | 数据特征 | 低基数分组 | Level0 |
| A-014 | 数据特征 | 数据倾斜分组 | Level0 |
| A-015 | 数据特征 | 全NULL聚合字段 | Level1 |
| A-016 | 数据特征 | 空表聚合 | Level1 |
| A-017 | 数据类型 | 各数据类型聚合 | Level0 |
| A-018 | 边界值 | 边界值聚合 | Level0 |
| A-019 | 异常-类型不匹配 | 类型不匹配聚合 | Level2 |
| A-020 | 异常-分组字段不存在 | GROUP BY字段不存在 | Level2 |
| A-021 | 异常-聚合函数参数错误 | 聚合函数参数错误（如SUM(*)使用参数） | Level2 |
| A-022 | 异常-HAVING列不存在 | HAVING条件列不存在 | Level2 |
| A-023 | 异常-HAVING类型不匹配 | HAVING条件类型不匹配 | Level2 |
