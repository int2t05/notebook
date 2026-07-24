-- =============================================================================
-- BIN(INT) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — BIN(INT) 返回整数的二进制字符串表示。
--   NULL 输入返回 NULL。Flink 实现 = Long.toBinaryString(long)：INT 先 widen 成 64-bit long，
--   故负数产生 64 位补码串（非 32 位）。无符号字符、无前导零。
-- 向量化: bin({INT} | {LONG}) -> VARCHAR
--
-- 上传 CSV:
--   install_script/queries/csv_test/bin/verify_expr_bin.csv -> /opt/buildtools/install_script/queries/csv_test/bin/verify_expr_bin.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  i      INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/bin/verify_expr_bin.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r_bin  STRING
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  BIN(i)
FROM src;

-- =============================================================================
-- 期望输出 (Flink BIN = Long.toBinaryString(widen-to-long)):
--
-- row_id | i     | r_bin
-- -------|-------|------------------------------------------------------------------
-- r01    | 0     | 0
-- r02    | 1     | 1
-- r03    | 4     | 100
-- r04    | 5     | 101
-- r05    | 12    | 1100
-- r06    | 255   | 11111111
-- r07    | 1024  | 10000000000
-- r08    | -1    | 1111111111111111111111111111111111111111111111111111111111111111 (64 个 1)
-- r09    | -5    | 1111111111111111111111111111111111111111111111111111111111111011 (64 位补码)
-- r10    | null  | NULL
--
-- 场景覆盖: 0 | 正数(无前导零) | 大正数 | 负数(64位补码) | NULL
-- =============================================================================
