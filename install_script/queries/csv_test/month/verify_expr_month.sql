-- =============================================================================
-- MONTH 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — MONTH(date) 返回 1~12，等价 EXTRACT(MONTH FROM date)
-- 向量化: month({DATE32|INT}) -> INT (不支持 TIMESTAMP 直传, 需 CAST AS DATE)
--
-- 上传 CSV:
--   install_script/queries/csv_test/month/verify_expr_month.csv -> /tmp/verify_expr_month.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_month.sql
--   grep -E '^\+I\[' $FLINK_HOME/log/flink-*-taskexecutor-*.out > /tmp/vanilla_out.txt
--   bash install_script/queries/csv_test/compare_native_vanilla.sh /tmp/flink_output.txt /tmp/vanilla_out.txt
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  d      DATE,
  ts     TIMESTAMP(3)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/month/verify_expr_month.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id          STRING,   -- 行标签
  r_month_date    INT      -- MONTH(d)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(MONTH(d) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | d            | ts                      | r_month_date | r_month_ts_cast
-- -------|--------------|-------------------------|--------------|----------------
-- r01    | 2024-01-01   | 2024-01-01 00:00:00     | 1            | 1    (年初/1月)
-- r02    | 2024-01-15   | 2024-01-15 10:00:00     | 1            | 1    (1月中)
-- r03    | 2024-03-31   | 2024-03-31 23:59:59.999 | 3            | 3    (3月末)
-- r04    | 2024-04-01   | 2024-04-01 00:00:00     | 4            | 4    (4月初)
-- r05    | 2024-06-30   | 2024-06-30 12:00:00     | 6            | 6    (6月末)
-- r06    | 2024-07-01   | 2024-07-01 00:00:00     | 7            | 7    (7月初)
-- r07    | 2024-09-30   | 2024-09-30 23:59:59.999 | 9            | 9    (9月末)
-- r08    | 2024-10-01   | 2024-10-01 00:00:00     | 10           | 10   (10月初)
-- r09    | 2024-12-30   | 2024-12-30 08:00:00     | 12           | 12   (12月末)
-- r10    | 2024-12-31   | 2024-12-31 23:59:59.999 | 12           | 12   (年末/12月)
-- r11    | 2020-02-29   | 2020-02-29 12:00:00     | 2            | 2    (闰年2月)
-- r12    | 1994-09-27   | 1994-09-27 15:30:45     | 9            | 9    (经典9月)
-- r13    | 2023-01-01   | 2023-01-01 00:00:00     | 1            | 1    (ISO周跨年仍1月)
-- r14    | 2021-01-01   | 2021-01-01 00:00:00     | 1            | 1    (ISO W53仍1月)
-- r15    | 2023-11-12   | 2023-11-12 00:00:00     | 11           | 11   (11月周日)
-- r16    | 2023-11-13   | 2023-11-13 00:00:00     | 11           | 11   (11月周一)
-- r17    | 2023-11-14   | 2023-11-14 00:00:00     | 11           | 11   (11月周二)
-- r18    | 2023-11-15   | 2023-11-15 00:00:00     | 11           | 11   (11月周三)
-- r19    | 2023-11-16   | 2023-11-16 00:00:00     | 11           | 11   (11月周四)
-- r20    | 2023-11-17   | 2023-11-17 00:00:00     | 11           | 11   (11月周五)
-- r21    | 2023-11-18   | 2023-11-18 00:00:00     | 11           | 11   (11月周六)
-- r22    | NULL         | 1994-09-27 10:00:00     | NULL         | 9    (DATE NULL)
-- r23    | 1994-09-27   | NULL                    | 9            | NULL (TIMESTAMP NULL)
-- r24    | NULL         | NULL                    | NULL         | NULL (双 NULL)
--
-- 场景覆盖:
--   1~12 各月月初/月末边界 | 闰年 2-29 | ISO 周跨年(W52/W53)月份不变 | 历史日期
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
