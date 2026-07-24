-- =============================================================================
-- SINH 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — SINH(numeric) 返回双曲正弦, 返回类型 DOUBLE。
-- 向量化: sinh({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::sinh)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/sinh/verify_expr_sinh.csv
--   -> /opt/buildtools/install_script/queries/csv_test/sinh/verify_expr_sinh.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/sinh/verify_expr_sinh.csv',
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
  CAST(SINH(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | x    | r (SINH)
-- -------|------|---------------------
-- r01    | 0.0  | 0.0                   (sinh(0)=0)
-- r02    | 1.0  | 1.1752011936438014    (sinh(1))
-- r03    | -1.0 | -1.1752011936438014   (sinh(-1)=-sinh(1), 奇函数)
-- r04    | 2.0  | 3.6268604078470186    (sinh(2))
-- r05    | 0.5  | 0.5210953054937474    (sinh(0.5))
-- r06    | NULL | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 正数 | 负数(奇函数验证) | 小数 | NULL 传播
-- =============================================================================
