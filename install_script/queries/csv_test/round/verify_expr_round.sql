-- =============================================================================
-- ROUND 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       ROUND(NUMERIC, INT): 把 NUMERIC 舍入到 INT 小数位。
--       Flink 运行时还支持单参 ROUND(NUMERIC) (等价 ROUND(NUMERIC, 0))。
--       舍入模式: HALF_UP (四舍五入, 远离 0 方向, 非银行家舍入)。
--       例: ROUND(2.5, 0)=3; ROUND(-2.5, 0)=-3; ROUND(123.45, -1)=120。
--
-- !! 实现说明 (重要) !!
--   OmniOperator 已有向量化实现 (functions/MathFunctions.h, RoundFunction), 注册名 "round"
--   (registration/RegisterMath.cpp:73-75), 12 个重载:
--     一元 (scale 默认 0): {BYTE/SHORT/INT/LONG/FLOAT/DOUBLE} -> 同类型
--     二元 (带 scale):     {BYTE/SHORT/INT/LONG/FLOAT/DOUBLE, INT} -> 同类型
--   注意: native round 【不支持 DECIMAL】 (源码注释 "byte/short/int/long/float/double only"),
--   整数类型 round 实质是恒等函数 (result=a, scale 被忽略)。
--
--   native 舍入实现 (RoundFunction::call, MathFunctions.h:521-532):
--     * 整数类型: 直接返回原值 (scale 被忽略)
--     * 浮点类型: result = std::round(a * pow(10, scale)) / pow(10, scale)
--     * std::round 语义 = "round halfway away from zero", 与 Flink 的 RoundingMode.HALF_UP
--       在数学上等价 (对 .5 都远离 0 进位)
--     * 无 callNullable, NULL 由框架传播
--
--   !! 类型匹配注意 !!
--   flink_function_dictionary.json 中 ROUND 的 is_supported_type 声明为
--   ["DOUBLE", "DECIMAL64", "DECIMAL128"], 但 native 实际【不】支持 DECIMAL。
--   故本测试仅用 DOUBLE 类型列 (字典与 native 的唯一交集), 确保能真正走 native。
--   DECIMAL 类型的 ROUND 会因 native 无注册重载而 dispatch 失败、回退, 不纳入本测试。
--
--   !! 潜在精度差异 !!
--   native 用浮点 std::round(a*pow(10,s))/pow(10,s), Flink 用 BigDecimal 精确计算。
--   对大多数值两者一致, 但某些 double 无法精确表示的十进制小数 (如 2.675 在 double 中
--   实为 2.67499999...) 可能在两引擎产生不同结果。本测试刻意纳入此类边界值以探测差异;
--   若发现 DIFF, 说明 native 浮点实现与 Flink BigDecimal 语义不完全等价, 需评估是否
--   改用 DECIMAL 精确路径 (但需先在 native 侧增加 DECIMAL 支持)。
--
-- 注意 CSV 以逗号分隔; null 字面量表示 NULL。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/round/verify_expr_round.csv
--   -> /opt/buildtools/install_script/queries/csv_test/round/verify_expr_round.csv
--
-- 对比流程 (见 skills/omniadaptor-vectorized-expression SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_round.sql
--   # 确认走 native:
--   tail -n 50 $FLINK_HOME/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
--   # 原生 Flink 基准:
--   cp $FLINK_HOME/bin/config.sh.orig $FLINK_HOME/bin/config.sh   # 切回原生
--   stop-cluster.sh; start-cluster.sh
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_round.sql
--   grep -E '^\+I' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
--   # 归一化 diff:
--   bash install_script/queries/csv_test/compare_native_vanilla.sh
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  v      DOUBLE,
  s      INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/round/verify_expr_round.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r1     DOUBLE,   -- ROUND(v)            单参, 等价 ROUND(v, 0)
  r2     DOUBLE    -- ROUND(v, s)         双参, scale 取自列 s
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  ROUND(v),
  ROUND(v, s)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r1, r2], 按 row_id 对照):
--   r1 = ROUND(v)     (scale 默认 0)
--   r2 = ROUND(v, s)  (scale = 列 s)
--
-- row_id | v        | s  | r1      | r2        | 说明
-- -------|---------|----|---------|-----------|-------------------------------
-- d01    | 2.5     | 0  | 3.0     | 3.0       | 正数 .5 进位 (HALF_UP)
-- d02    | 2.4     | 0  | 2.0     | 2.0       | 正数 .4 舍去
-- d03    | 2.6     | 0  | 3.0     | 3.0       | 正数 .6 进位
-- d04    | -2.5    | 0  | -3.0    | -3.0      | 负数 .5 远离 0 (HALF_UP, 非 -2)
-- d05    | -2.4    | 0  | -2.0    | -2.0      | 负数 .4 舍去
-- d06    | -2.6    | 0  | -3.0    | -3.0      | 负数 .6 进位 (更负)
-- d07    | 0.5     | 0  | 1.0     | 1.0       | 0.5 进位 (非银行家舍入 0)
-- d08    | -0.5    | 0  | -1.0    | -1.0      | -0.5 进位
-- d09    | 0.0     | 0  | 0.0     | 0.0       | 零
-- d10    | 3.14159 | 2  | 3.0     | 3.14      | scale=2 保留两位
-- d11    | 3.14159 | 1  | 3.0     | 3.1       | scale=1 保留一位
-- d12    | 1.45    | 1  | 1.0     | ?         | 浮点精度边界: 1.45 在 double 中实为
--        |         |    |         |           |   1.44999999..., native round(14.5)=14
--        |         |    |         |           |   -> 1.4; Flink BigDecimal -> 1.5
--        |         |    |         |           |   【可能 DIFF】探测浮点 vs 精确差异
-- d13    | 123.45  | -1 | 123.0   | 120.0     | scale=-1 十位舍入 (123.45->120)
-- d14    | 125.0   | -1 | 125.0   | 130.0     | scale=-1, 125->130 (12.5->13)
-- d15    | 149.9   | -2 | 150.0   | 100.0     | scale=-2 百位 (1.499->1->100)
-- d16    | 150.0   | -2 | 150.0   | 200.0     | scale=-2, 150->200 (1.5->2)
-- d17    | 11111.0 | -1 | 11111.0 | 11110.0   | scale=-1 (native 单元测试用例)
-- d18    | 2.675   | 2  | 3.0     | ?         | 浮点精度边界: 2.675 在 double 中实为
--        |         |    |         |           |   2.67499999..., native round(267.5)=267
--        |         |    |         |           |   -> 2.67; Flink BigDecimal -> 2.68
--        |         |    |         |           |   【可能 DIFF】探测浮点 vs 精确差异
-- d19    | NULL    | 0  | NULL    | NULL      | v 为 NULL -> NULL
-- d20    | 3.7     | NULL| 4.0    | NULL      | s 为 NULL -> r2 为 NULL
-- d21    | 1000000.999 | 2 | 1000001.0 | 1000001.0 | 大数 + 小数 scale=2
--
-- 场景覆盖:
--   HALF_UP .5 进位 (正/负/零) | .4 舍 | .6 进 | scale 正/0/负 | 负 scale 十位/百位 |
--   浮点精度边界 (d12/d18 可能 DIFF: native 浮点 std::round vs Flink BigDecimal) |
--   NULL (v/s) | 大数
-- =============================================================================