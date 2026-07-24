-- =============================================================================
-- DEGREES 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — DEGREES(numeric) 返回弧度 numeric 的度数表示
--       (弧度 -> 度, degrees = radians * 180 / π)。
-- 向量化: degrees({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h:
--   DegreesFunction: result = a * (180.0 / M_PI))。
--
-- 上传 CSV:
--   install_script/queries/csv_test/degrees/verify_expr_degrees.csv
--   -> /opt/buildtools/install_script/queries/csv_test/degrees/verify_expr_degrees.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/degrees/verify_expr_degrees.csv',
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
  CAST(DEGREES(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 弧度 -> 度):
--
-- row_id | x                   | r (DEGREES)
-- -------|---------------------|---------------------
-- r01    | 0.0                 | 0.0                   (0 弧度 -> 0°)
-- r02    | 3.141592653589793   | 180.0                 (π -> 180°)
-- r03    | 1.5707963267948966  | 90.0                  (π/2 -> 90°)
-- r04    | 6.283185307179586   | 360.0                 (2π -> 360°)
-- r05    | -3.141592653589793  | -180.0                (-π -> -180°, 奇函数)
-- r06    | 0.7853981633974483  | 45.0                  (π/4 -> 45°)
-- r07    | 1.0                 | 57.29577951308232     (1 弧度 ≈ 57.2958°)
-- r08    | NULL                | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | π(=180) | π/2(=90) | 2π(=360) | -π(=-180, 奇函数) | π/4(=45) |
--           1 弧度(≈57.3) | NULL 传播
-- =============================================================================
