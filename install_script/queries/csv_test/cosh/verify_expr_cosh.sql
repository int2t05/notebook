-- =============================================================================
-- COSH 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — COSH(numeric) 返回双曲余弦, 返回类型 DOUBLE。
-- 向量化: cosh({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::cosh)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/cosh/verify_expr_cosh.csv
--   -> /opt/buildtools/install_script/queries/csv_test/cosh/verify_expr_cosh.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/cosh/verify_expr_cosh.csv',
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
  CAST(COSH(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | x    | r (COSH)
-- -------|------|---------------------
-- r01    | 0.0  | 1.0                   (cosh(0)=1)
-- r02    | 1.0  | 1.5430806348152437    (cosh(1))
-- r03    | -1.0 | 1.5430806348152437    (cosh(-1)=cosh(1), 偶函数)
-- r04    | 2.0  | 3.7621956910836314    (cosh(2))
-- r05    | NULL | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 正数 | 负数(偶函数验证 cosh(-x)=cosh(x)) | NULL 传播
-- =============================================================================
