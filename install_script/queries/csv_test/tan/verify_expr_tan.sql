-- =============================================================================
-- TAN 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — TAN(numeric) 返回正切 (入参为弧度, tan=sin/cos)。
-- 向量化: tan({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: TanFunction = std::tan)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/tan/verify_expr_tan.csv
--   -> /opt/buildtools/install_script/queries/csv_test/tan/verify_expr_tan.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/tan/verify_expr_tan.csv',
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
  CAST(TAN(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 入参为弧度, tan=sin/cos):
--
-- row_id | x                   | r (TAN)
-- -------|---------------------|---------------------
-- r01    | 0.0                 | 0.0                   (tan(0)=0)
-- r02    | 0.7853981633974483  | 0.9999999999999999    (tan(π/4)≈1)
-- r03    | 0.5235987755982988  | 0.5773502691896257    (tan(π/6)≈1/√3)
-- r04    | 1.0                 | 1.5574077246549023    (tan(1))
-- r05    | -1.0                | -1.5574077246549023   (tan(-1)=-tan(1), 奇函数)
-- r06    | 0.5                 | 0.5463024898437905    (tan(0.5))
-- r07    | -0.5                | -0.5463024898437905   (tan(-0.5), 奇函数)
-- r08    | NULL                | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | π/4(≈1) | π/6(≈1/√3) | 1 | -1(奇函数) | 0.5 | -0.5(奇函数) | NULL 传播
-- =============================================================================
