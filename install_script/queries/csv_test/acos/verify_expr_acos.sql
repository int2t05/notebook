-- =============================================================================
-- ACOS 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — ACOS(numeric) 返回反余弦 (弧度), 定义域 [-1,1]。
-- 向量化: acos({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::acos)。
--   越界入参(如 2.0) std::acos 返回 NaN -> 结果 NaN。
--
-- 上传 CSV:
--   install_script/queries/csv_test/acos/verify_expr_acos.csv
--   -> /opt/buildtools/install_script/queries/csv_test/acos/verify_expr_acos.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  x      DOUBLE
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/acos/verify_expr_acos.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r      DOUBLE
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(ACOS(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 定义域 [-1,1], 返回弧度 [0,π]):
--
-- row_id | x                   | r (ACOS)
-- -------|---------------------|---------------------
-- r01    | 1.0                 | 0.0                   (acos(1)=0, 域上界)
-- r02    | -1.0                | 3.141592653589793     (acos(-1)=π, 域下界)
-- r03    | 0.0                 | 1.5707963267948966    (acos(0)=π/2)
-- r04    | 0.5                 | 1.0471975511965979    (acos(0.5)=π/3)
-- r05    | -0.5                | 2.0943951023931957    (acos(-0.5)=2π/3)
-- r06    | 0.8660254037844386  | 0.5235987755982988    (acos(√3/2)=π/6)
-- r07    | 2.0                 | NaN                   (越界, std::acos 返回 NaN)
-- r08    | -2.0                | NaN                   (越界, std::acos 返回 NaN)
-- r09    | NULL                | NULL                  (NULL 传播)
--
-- 场景覆盖: 域上界(1=0) | 域下界(-1=π) | 0(=π/2) | 域内正/负值 | √3/2(π/6) |
--           越界(2.0,-2.0 -> NaN) | NULL 传播
-- =============================================================================
