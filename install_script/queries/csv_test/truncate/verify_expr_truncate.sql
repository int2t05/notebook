-- =============================================================================
-- TRUNCATE(numeric1, integer2) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — TRUNCATE(numeric1[, integer2]) 截断到 integer2 位小数。
--   向零截断(RoundingMode.DOWN，非四舍五入)。integer2 可负(小数点左侧 n 位变零)。
--   1-arg 形式 TRUNCATE(x) ≡ TRUNCATE(x, 0)。
--   NULL 输入返回 NULL。返回类型同 numeric1。
--   例: TRUNCATE(42.324,2)=42.32, TRUNCATE(42.324)=42.0, TRUNCATE(42.324,-1)=40.0
-- 向量化: truncate({INT|BIGINT|FLOAT|DOUBLE, INT} | {INT|BIGINT|FLOAT|DOUBLE}) -> 同入参类型
--   注: native 不支持 DECIMAL；DECIMAL 入参不 offload。
--
-- 上传 CSV:
--   install_script/queries/csv_test/truncate/verify_expr_truncate.csv -> /opt/buildtools/install_script/queries/csv_test/truncate/verify_expr_truncate.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  d      DOUBLE,
  n      INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/truncate/verify_expr_truncate.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id        STRING,
  r_trunc_d2    DOUBLE,    -- TRUNCATE(d, 2)
  r_trunc_d0    DOUBLE,    -- TRUNCATE(d)  (1-arg, = TRUNCATE(d,0))
  r_trunc_neg1  DOUBLE,    -- TRUNCATE(d, -1)
  r_trunc_neg2  DOUBLE     -- TRUNCATE(d, -2)
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  TRUNCATE(d, 2),
  TRUNCATE(d),
  TRUNCATE(d, -1),
  TRUNCATE(d, -2)
FROM src;

-- =============================================================================
-- 期望输出 (向零截断 DOWN):
--
-- row_id | d       | n  | r_trunc_d2 | r_trunc_d0 | r_trunc_neg1 | r_trunc_neg2
-- -------|--------|----|------------|------------|--------------|--------------
-- r01    | 42.324 | 2  | 42.32      | 42.0       | 40.0         | 0.0
-- r02    | -42.324| 1  | -42.32     | -42.0      | -40.0        | -0.0
-- r03    | 2.7    | 0  | 2.7        | 2.0        | 0.0          | 0.0
-- r04    | -2.7   | -1 | -2.7       | -2.0       | -0.0         | -0.0
-- r05    | 1234.5678 | 3 | 1234.56   | 1234.0     | 1230.0       | 1200.0
-- r06    | 0.999  | 5  | 0.999      | 0.0        | 0.0          | 0.0
-- r07    | null   | 2  | NULL       | NULL       | NULL         | NULL
-- r08    | 42.324 | null | NULL     | 42.0       | NULL         | NULL
--
-- 场景覆盖:
--   正数/负数向零截断(2位/0位/负位) | 1-arg 形式 | 大数 | 小数(scale>小数位不变) | NULL d | NULL n
--   关键对比: TRUNCATE(2.7,0)=2.0 (truncate) vs ROUND(2.7,0)=3.0
-- =============================================================================
