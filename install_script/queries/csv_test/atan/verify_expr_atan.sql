-- =============================================================================
-- ATAN 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — ATAN(numeric) 返回反正切 (弧度), 值域 (-π/2, π/2)。
-- 向量化: atan({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::atan)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/atan/verify_expr_atan.csv
--   -> /opt/buildtools/install_script/queries/csv_test/atan/verify_expr_atan.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/atan/verify_expr_atan.csv',
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
  CAST(ATAN(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 返回弧度, 值域 (-π/2, π/2)):
--
-- row_id | x          | r (ATAN)
-- -------|------------|---------------------
-- r01    | 0.0        | 0.0                   (atan(0)=0)
-- r02    | 1.0        | 0.7853981633974483    (atan(1)=π/4)
-- r03    | -1.0       | -0.7853981633974483   (atan(-1)=-π/4, 奇函数)
-- r04    | 10000000000.0 | 1.5707963266948965  (大正数 -> 趋近 π/2)
-- r05    | -10000000000.0 | -1.5707963266948965 (大负数 -> 趋近 -π/2, 奇函数)
-- r06    | 0.5        | 0.4636476090008061    (atan(0.5))
-- r07    | NULL       | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 1(=π/4) | -1(奇函数) | 大正数(趋近 π/2) | 大负数(趋近 -π/2) |
--           小数 | NULL 传播
-- =============================================================================
