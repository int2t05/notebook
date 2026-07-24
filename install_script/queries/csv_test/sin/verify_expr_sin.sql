-- =============================================================================
-- SIN 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — SIN(numeric) 返回正弦 (入参为弧度)。
-- 向量化: sin({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: SinFunction = std::sin)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/sin/verify_expr_sin.csv
--   -> /opt/buildtools/install_script/queries/csv_test/sin/verify_expr_sin.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/sin/verify_expr_sin.csv',
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
  CAST(SIN(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 入参为弧度):
--
-- row_id | x                   | r (SIN)
-- -------|---------------------|---------------------
-- r01    | 0.0                 | 0.0                   (sin(0)=0)
-- r02    | 1.5707963267948966  | 1.0                   (sin(π/2)=1)
-- r03    | 0.5235987755982988  | 0.49999999999999994   (sin(π/6)≈0.5)
-- r04    | 1.0                 | 0.8414709848078965    (sin(1))
-- r05    | -1.0                | -0.8414709848078965   (sin(-1)=-sin(1), 奇函数)
-- r06    | 3.141592653589793   | 1.2246467991473532E-16 (sin(π)≈0, 浮点近零)
-- r07    | 0.7853981633974483  | 0.7071067811865475    (sin(π/4)≈√2/2)
-- r08    | NULL                | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | π/2(=1) | π/6(≈0.5) | 1 | -1(奇函数) | π(近零) | π/4(√2/2) | NULL 传播
-- =============================================================================
