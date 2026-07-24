-- =============================================================================
-- E() 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — E() 返回接近 e 的 DOUBLE 值 (Math.E = 2.718281828459045)
-- 向量化: e({}) -> DOUBLE (0 参常量函数)
--
-- 上传 CSV:
--   install_script/queries/csv_test/e/verify_expr_e.csv -> /opt/buildtools/install_script/queries/csv_test/e/verify_expr_e.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/e/verify_expr_e.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r_e    DOUBLE
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  E()
FROM src;

-- =============================================================================
-- 期望输出 (每行 E() 恒等于 2.718281828459045):
--
-- row_id | r_e
-- -------|---------------------
-- r01    | 2.718281828459045
-- r02    | 2.718281828459045
-- r03    | 2.718281828459045
--
-- 场景覆盖: 多行验证 0 参常量逐行填充相同值。
-- =============================================================================
