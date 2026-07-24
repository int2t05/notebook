-- =============================================================================
-- PI() 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — PI() 返回接近 pi 的 DOUBLE 值 (Math.PI = 3.141592653589793)
-- 向量化: pi({}) -> DOUBLE (0 参常量函数)
--
-- 上传 CSV:
--   install_script/queries/csv_test/pi/verify_expr_pi.csv -> /opt/buildtools/install_script/queries/csv_test/pi/verify_expr_pi.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

-- PI() 无入参，但 OmniStream offload 需要一个 csv 源来产生行；用一个 dummy 列驱动行数。
CREATE TABLE src (
  row_id STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/pi/verify_expr_pi.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r_pi   DOUBLE
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  PI()
FROM src;

-- =============================================================================
-- 期望输出 (每行 PI() 恒等于 3.141592653589793):
--
-- row_id | r_pi
-- -------|----------------------
-- r01    | 3.141592653589793
-- r02    | 3.141592653589793
-- r03    | 3.141592653589793
--
-- 场景覆盖: 多行验证 0 参常量逐行填充相同值。
-- =============================================================================
