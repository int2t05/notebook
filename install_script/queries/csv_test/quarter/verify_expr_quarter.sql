-- =============================================================================
-- QUARTER 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — QUARTER(date) 返回 1~4
-- 向量化: quarter({DATE32|INT}) -> INT (不支持 TIMESTAMP 直传, 需 CAST AS DATE)
--
-- 上传 CSV:
--   install_script/OmniStream/verify_expr_quarter.csv -> /tmp/verify_expr_quarter.csv
--
-- 用法同 verify_expr_year.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  d      DATE,
  ts     TIMESTAMP(3)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/quarter/verify_expr_quarter.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id            STRING,   -- 行标签
  r_quarter_date    INT,      -- QUARTER(d)
  r_quarter_ts_cast INT       -- QUARTER(CAST(ts AS DATE)) — 适配路径
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(QUARTER(d) AS INT),
  CAST(QUARTER(CAST(ts AS DATE)) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | d            | ts                      | r_quarter_date | r_quarter_ts_cast
-- -------|--------------|-------------------------|----------------|------------------
-- r01    | 2024-01-15   | 2024-01-15 10:00:00     | 1              | 1    (Q1 月中)
-- r02    | 2024-03-31   | 2024-03-31 23:59:59.999 | 1              | 1    (Q1 末)
-- r03    | 2024-04-01   | 2024-04-01 00:00:00     | 2              | 2    (Q2 初)
-- r04    | 2024-06-30   | 2024-06-30 12:00:00     | 2              | 2    (Q2 末)
-- r05    | 2024-07-01   | 2024-07-01 00:00:00     | 3              | 3    (Q3 初)
-- r06    | 2024-09-30   | 2024-09-30 23:59:59.999 | 3              | 3    (Q3 末)
-- r07    | 2024-10-01   | 2024-10-01 00:00:00     | 4              | 4    (Q4 初)
-- r08    | 2024-12-31   | 2024-12-31 23:59:59.999 | 4              | 4    (Q4 末)
-- r09    | 2020-02-29   | 2020-02-29 12:00:00     | 1              | 1    (闰年 Q1)
-- r10    | 1994-09-27   | 1994-09-27 15:30:45     | 3              | 3    (经典 Q3)
-- r11    | NULL         | 1994-09-27 10:00:00     | NULL           | 3    (DATE NULL)
-- r12    | 1994-09-27   | NULL                    | 3              | NULL (TIMESTAMP NULL)
-- r13    | NULL         | NULL                    | NULL           | NULL (双 NULL)
--
-- 场景覆盖:
--   Q1~Q4 各季度月中 + 季度末/初边界 | 闰年 2-29 | 历史日期
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
