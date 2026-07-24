# 写入类算子（TableWrite）速查卡

> 覆盖INSERT INTO/OVERWRITE写入场景，重点关注写入模式、分区策略、存储格式及异常处理。

## 算子基础信息

数据流向=写入类 | 功能语义=写入类 | Omni算子=OmniInsertIntoHadoopFsRelationCommand | SQL模式=写入类SQL模式 | 开关=spark.omni.sql.columnar.dataWritingCommand

## 输入因子

| 因子编号 | 因子分类 | 因子名称 | 全量可选值 | 影响权重 |
| :--- | :--- | :--- | :--- | :--- |
| F001 | 核心功能因子 | 写入模式 | INSERT INTO / INSERT OVERWRITE | 极高 |
| F002 | 条件配置因子 | 开关状态 | 开启(默认) / 关闭 | 极高 |
| F003 | 输入数据特征因子 | 数据类型 | BOOLEAN/BYTE/SHORT/INT/LONG/FLOAT/DOUBLE/STRING/DATE/DECIMAL64/DECIMAL128/CHAR/VARCHAR/TIMESTAMP/BINARY/ARRAY/MAP/STRUCT | 极高 |
| F004 | 输入数据特征因子 | 数据量级 | 空表/单条数据/小表(20行)/中表(1W行)/大表(100W行) | 高 |
| F005 | 执行配置因子 | 存储格式 | ORC / Parquet | 高 |
| F006 | 条件配置因子 | 分区类型 | 非分区表/静态分区/动态分区/多级分区 | 高 |
| F007 | 输入数据特征因子 | NULL值占比 | 无NULL/少量NULL/大量NULL/全NULL | 中 |
| F008 | 输入数据特征因子 | 边界值 | 最大值/最小值/零值/接近边界值 | 中 |
| F009 | 条件配置因子 | 列匹配方式 | 按位置匹配/按名称匹配 | 中 |
| F010 | 异常配置因子 | 列数/类型异常 | 列数不匹配/列名不匹配/类型不匹配/char超长/decimal溢出 | 中 |

## 测试场景清单

| 场景编号 | 场景分类 | 场景描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| W-001 | 开关测试 | 开关开启场景 | Level0 |
| W-002 | 开关测试 | 开关关闭场景 | Level0 |
| W-003 | 单类型写入 | 每种支持的数据类型单独写入测试 | Level0 |
| W-004 | 组合类型写入 | 所有支持类型组合写入测试 | Level1 |
| W-005 | 不支持类型验证 | 不支持类型写入验证（回退原生） | Level1 |
| W-006 | 写入模式 | INSERT INTO 写入 | Level0 |
| W-007 | 写入模式 | INSERT OVERWRITE 写入 | Level0 |
| W-008 | 分区表 | 静态分区写入（各数据类型分区列） | Level0 |
| W-009 | 分区表 | 动态分区写入（支持类型全覆盖） | Level0 |
| W-010 | 分区表 | 动态分区写入（不支持类型全覆盖） | Level1 |
| W-011 | 分区表 | 多级分区写入 | Level1 |
| W-012 | 边界值 | 各数据类型边界值写入 | Level0 |
| W-013 | NULL处理 | 含NULL值写入 | Level0 |
| W-014 | ORC格式 | ORC格式写入验证 | Level0 |
| W-015 | 多行多列 | 多行多列写入 | Level1 |
| W-016 | 异常-列数不匹配 | 列数不匹配写入 | Level1 |
| W-017 | 异常-列名不匹配 | 列名不匹配写入 | Level1 |
| W-018 | 异常-类型不匹配 | 类型不匹配写入 | Level1 |
| W-019 | 异常-char超长 | CHAR/VARCHAR超长写入 | Level1 |
| W-020 | 异常-decimal溢出 | DECIMAL精度溢出写入 | Level1 |
| W-021 | 异常-动态分区未开启 | 动态分区未开启场景 | Level1 |
| W-022 | 异常-分区列不存在 | 分区列不存在场景 | Level2 |
| W-023 | 异常-表不存在 | 写入不存在的表 | Level2 |
| W-024 | 异常-复杂类型 | ARRAY/MAP/STRUCT操作 | Level2 |
