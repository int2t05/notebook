# 窗口类算子（Window）速查卡

> 覆盖窗口函数场景，重点关注窗口函数类型、帧定义（ROWS/RANGE）、帧边界及分区排序组合。

## 算子基础信息

数据流向=读取类 | 功能语义=窗口类 | Omni算子=WindowExecTransformer | SQL模式=读取类SQL模式 | 开关=spark.omni.sql.columnar.window

## 输入因子

| 因子编号 | 因子分类 | 因子名称 | 全量可选值 | 影响权重 |
| :--- | :--- | :--- | :--- | :--- |
| F001 | 核心功能因子 | 窗口函数类型 | ROW_NUMBER/RANK/DENSE_RANK/LEAD/LAG/FIRST_VALUE/LAST_VALUE/NTILE/PERCENT_RANK/CUME_DIST | 极高 |
| F002 | 核心功能因子 | 窗口帧类型 | ROWS BETWEEN / RANGE BETWEEN | 极高 |
| F003 | 核心功能因子 | 窗口帧边界 | UNBOUNDED PRECEDING / N PRECEDING / CURRENT ROW / N FOLLOWING / UNBOUNDED FOLLOWING | 高 |
| F004 | 核心功能因子 | 分区与排序 | PARTITION BY + ORDER BY 组合 | 极高 |
| F005 | 条件配置因子 | 开关状态 | 开启(默认) / 关闭 | 极高 |
| F006 | 输入数据特征因子 | 数据类型 | 同写入类F003 | 极高 |
| F007 | 输入数据特征因子 | 分区内数据量 | 小分区/大分区/空分区/单行分区 | 高 |

## 测试场景清单

| 场景编号 | 场景分类 | 场景描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| WD-001 | 开关测试 | 开关开启/关闭场景 | Level0 |
| WD-002 | 窗口函数 | ROW_NUMBER / RANK / DENSE_RANK | Level0 |
| WD-003 | 窗口函数 | LEAD / LAG | Level0 |
| WD-004 | 窗口函数 | FIRST_VALUE / LAST_VALUE | Level1 |
| WD-005 | 窗口函数 | NTILE / PERCENT_RANK / CUME_DIST | Level1 |
| WD-006 | 窗口帧 | ROWS BETWEEN | Level0 |
| WD-007 | 窗口帧 | RANGE BETWEEN | Level0 |
| WD-008 | 窗口帧边界 | UNBOUNDED / N PRECEDING / CURRENT ROW / N FOLLOWING | Level0 |
| WD-009 | 分区排序 | PARTITION BY + ORDER BY 组合 | Level0 |
| WD-010 | 数据特征 | 小分区/大分区/空分区/单行分区 | Level1 |
| WD-011 | 数据类型 | 各数据类型窗口函数 | Level0 |
| WD-012 | 边界值 | 边界值窗口函数 | Level0 |
| WD-013 | 异常-函数参数错误 | 窗口函数参数错误（如LEAD/LAG的offset为负值） | Level2 |
| WD-014 | 异常-帧定义错误 | 帧定义错误（如ROWS BETWEEN的边界无效） | Level2 |
| WD-015 | 异常-分区字段不存在 | PARTITION BY字段不存在 | Level2 |
| WD-016 | 异常-排序字段不存在 | ORDER BY字段不存在 | Level2 |
| WD-017 | 异常-类型不匹配 | 类型不匹配（如对非数值类型使用SUM窗口函数） | Level2 |
