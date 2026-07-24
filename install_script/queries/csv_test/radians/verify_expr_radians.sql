-- =============================================================================
-- RADIANS 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — RADIANS(numeric) 返回度数 numeric 的弧度表示
--       (度 -> 弧度, radians = degrees * π / 180; 是 DEGREES 的逆运算)。
-- 向量化: radians({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h:
--   RadiansFunction: result = a * (M_PI / 180.0))。
--
-- 上传 CSV:
--   install_script/queries/csv_test/radians/verify_expr_radians.csv
--   -> /opt/buildtools/install_script/queries/csv_test/radians/verify_expr_radians.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/radians/verify_expr_radians.csv',
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
  CAST(RADIANS(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 度 -> 弧度):
--
-- row_id | x      | r (RADIANS)
-- -------|--------|---------------------
-- r01    | 0.0    | 0.0                   (0° -> 0)
-- r02    | 180.0  | 3.141592653589793     (180° -> π)
-- r03    | 90.0   | 1.5707963267948966    (90° -> π/2)
-- r04    | 360.0  | 6.283185307179586     (360° -> 2π)
-- r05    | -180.0 | -3.141592653589793    (-180° -> -π, 奇函数)
-- r06    | 45.0   | 0.7853981633974483    (45° -> π/4)
-- r07    | 1.0    | 0.017453292519943295  (1° ≈ 0.01745)
-- r08    | NULL   | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 180(=π) | 90(=π/2) | 360(=2π) | -180(=-π, 奇函数) | 45(=π/4) |
--           1°(≈0.01745) | NULL 传播
-- =============================================================================
