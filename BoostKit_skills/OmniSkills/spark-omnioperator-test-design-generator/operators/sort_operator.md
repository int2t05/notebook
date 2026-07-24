# 排序类算子（Sort/TopN/Limit）速查卡

> 覆盖ORDER BY排序与LIMIT截断场景，重点关注排序方向、NULL排序规则及重复值处理。

## 算子基础信息

数据流向=读取类 | 功能语义=排序类 | Omni算子=SortExecTransformer/OmniTopNSortTransformer/LimitExecTransformer | SQL模式=读取类SQL模式 | 开关=spark.omni.sql.columnar.sort/spark.omni.sql.columnar.takeOrderedAndProject

## 输入因子

| 因子编号 | 因子分类 | 因子名称 | 全量可选值 | 影响权重 |
| :--- | :--- | :--- | :--- | :--- |
| F001 | 核心功能因子 | 排序方向 | ASC / DESC | 极高 |
| F002 | 核心功能因子 | NULL排序规则 | NULLS FIRST / NULLS LAST | 极高 |
| F003 | 核心功能因子 | 排序字段数 | 单字段排序/多字段排序 | 高 |
| F004 | 条件配置因子 | 开关状态 | 开启(默认) / 关闭 | 极高 |
| F005 | 输入数据特征因子 | 数据类型 | 同写入类F003 | 极高 |
| F006 | 输入数据特征因子 | 数据特征 | 全唯一值/有重复值/全NULL/含NULL/全相同值 | 高 |
| F007 | 核心功能因子 | Limit值 | 0/1/小值(10)/大值(10000)/超过总行数 | 高（仅Limit/TopN） |

## 测试场景清单

| 场景编号 | 场景分类 | 场景描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| S-001 | 开关测试 | 开关开启/关闭场景 | Level0 |
| S-002 | 排序方向 | ASC升序 | Level0 |
| S-003 | 排序方向 | DESC降序 | Level0 |
| S-004 | NULL排序 | NULLS FIRST | Level0 |
| S-005 | NULL排序 | NULLS LAST | Level0 |
| S-006 | 排序字段 | 单字段排序 | Level0 |
| S-007 | 排序字段 | 多字段排序 | Level0 |
| S-008 | 数据特征 | 全唯一值排序 | Level1 |
| S-009 | 数据特征 | 有重复值排序 | Level1 |
| S-010 | 数据特征 | 全NULL排序 | Level1 |
| S-011 | 数据特征 | 含NULL排序 | Level0 |
| S-012 | 数据类型 | 各数据类型排序 | Level0 |
| S-013 | Limit值 | LIMIT 0 / 1 / N / 超总行数（仅Limit/TopN） | Level0 |
| S-014 | 边界值 | 边界值排序 | Level0 |
| S-015 | 空表 | 空表排序 | Level1 |
| S-016 | 异常-字段不存在 | 排序字段不存在 | Level2 |
| S-017 | 异常-类型不匹配 | 类型不匹配排序（如STRING类型数值排序） | Level2 |
| S-018 | 异常-LIMIT负值 | LIMIT负值 | Level2 |
| S-019 | 异常-LIMIT非整数 | LIMIT非整数值 | Level2 |
