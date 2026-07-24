-- =============================================================================
-- TANH 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — TANH(numeric) 返回双曲正切, 返回类型 DOUBLE。
--       值域 (-1, 1), 奇函数: tanh(-x)=-tanh(x); 大 |x| 趋近 ±1。
-- 向量化: tanh({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: TanhFunction = std::tanh)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/tanh/verify_expr_tanh.csv
--   -> /opt/buildtools/install_script/queries/csv_test/tanh/verify_expr_tanh.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/tanh/verify_expr_tanh.csv',
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
  CAST(TANH(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 双曲正切, 值域 (-1,1)):
--
-- row_id | x     | r (TANH)
-- -------|-------|---------------------
-- r01    | 0.0   | 0.0                   (tanh(0)=0)
-- r02    | 1.0   | 0.7615941559557649    (tanh(1))
-- r03    | -1.0  | -0.7615941559557649   (tanh(-1)=-tanh(1), 奇函数)
-- r04    | 0.5   | 0.46211715726000974   (tanh(0.5))
-- r05    | 10.0  | 0.9999999958776927    (大正数 -> 趋近 1)
-- r06    | -10.0 | -0.9999999958776927   (大负数 -> 趋近 -1, 奇函数)
-- r07    | NULL  | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 1 | -1(奇函数) | 小数 | 大正数(趋近1) | 大负数(趋近-1, 奇函数) | NULL 传播
-- =============================================================================
