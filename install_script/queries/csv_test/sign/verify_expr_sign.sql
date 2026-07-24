-- =============================================================================
-- SIGN 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — SIGN(numeric) 返回 signum 符号函数:
--       正数 -> 1, 0 -> 0, 负数 -> -1。
-- 向量化: sign({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h:
--   SignFunction: NaN->NaN; 否则 (a==0)?0.0 : (a>0)?1.0 : -1.0)。
--   原生仅注册 DOUBLE 重载, 返回 DOUBLE(-1.0/0.0/1.0)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/sign/verify_expr_sign.csv
--   -> /opt/buildtools/install_script/queries/csv_test/sign/verify_expr_sign.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/sign/verify_expr_sign.csv',
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
  CAST(SIGN(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 符号函数 -> -1.0/0.0/1.0):
--
-- row_id | x        | r (SIGN)
-- -------|----------|----------
-- r01    | 3.14     | 1.0       (正数 -> 1)
-- r02    | 0.0      | 0.0       (零 -> 0)
-- r03    | -2.71    | -1.0      (负数 -> -1)
-- r04    | 5.0      | 1.0       (正整数 -> 1)
-- r05    | -0.001   | -1.0      (小负数 -> -1)
-- r06    | 0.001    | 1.0       (小正数 -> 1)
-- r07    | -100.0   | -1.0      (大负数 -> -1)
-- r08    | NULL     | NULL      (NULL 传播)
--
-- 场景覆盖: 正数(=1) | 零(=0) | 负数(=-1) | 小正/负数 | 大正/负数 | NULL 传播
-- =============================================================================
