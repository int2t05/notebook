-- =============================================================================
-- WEEK 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — WEEK(date) 返回 1~53，等价 EXTRACT(WEEK FROM date)
--       ISO 8601 周编号 (W1 = 含当年第一个周四的周)。示例: WEEK(DATE '1994-09-27') = 39
-- 向量化: week_of_year({DATE32|INT|TIMESTAMP|LONG}) -> INT (原生支持 TIMESTAMP 直传)
--
-- 上传 CSV:
--   install_script/queries/csv_test/week/verify_expr_week.csv -> /tmp/verify_expr_week.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_week.sql
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/week/verify_expr_week.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id         STRING,   -- 行标签
  r_week_date    INT      -- WEEK(d)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(WEEK(d) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, ISO 8601 周):
--
-- row_id | d            | ts                      | r_week_date | r_week_ts_cast
-- -------|--------------|-------------------------|-------------|---------------
-- r01    | 2024-01-01   | 2024-01-01 00:00:00     | 1           | 1    (周一=新年W1)
-- r02    | 2023-01-01   | 2023-01-01 00:00:00     | 52          | 52   (周日=上年W52)
-- r03    | 2021-01-01   | 2021-01-01 00:00:00     | 53          | 53   (周五=上年W53)
-- r04    | 2024-12-30   | 2024-12-30 08:00:00     | 1           | 1    (周一=下年W1)
-- r05    | 2024-12-31   | 2024-12-31 23:59:59.999 | 1           | 1    (周二=下年W1)
-- r06    | 2023-12-31   | 2023-12-31 23:59:59.999 | 52          | 52   (周日=本年W52)
-- r07    | 2020-12-31   | 2020-12-31 12:00:00     | 53          | 53   (周四=本年W53)
-- r08    | 2020-01-01   | 2020-01-01 00:00:00     | 1           | 1    (周三=新年W1)
-- r09    | 1994-09-27   | 1994-09-27 15:30:45     | 39          | 39   (经典示例 W39)
-- r10    | 2024-09-30   | 2024-09-30 23:59:59.999 | 40          | 40   (周一W40)
-- r11    | 2024-10-01   | 2024-10-01 00:00:00     | 40          | 40   (周二同W40)
-- r12    | 2020-02-29   | 2020-02-29 12:00:00     | 9           | 9    (闰年 W9)
-- r13    | 2024-02-29   | 2024-02-29 12:00:00     | 9           | 9    (闰年 W9)
-- r14    | 2024-06-30   | 2024-06-30 12:00:00     | 26          | 26   (周日 W26)
-- r15    | 2023-11-12   | 2023-11-12 00:00:00     | 45          | 45   (周日 W45)
-- r16    | 2023-11-13   | 2023-11-13 00:00:00     | 46          | 46   (周一 W46)
-- r17    | 2023-11-18   | 2023-11-18 00:00:00     | 46          | 46   (周六同W46)
-- r18    | 2024-11-30   | 2024-11-30 00:00:00     | 48          | 48   (周六 W48)
-- r19    | 2024-05-31   | 2024-05-31 00:00:00     | 22          | 22   (周五 W22)
-- r20    | 2024-08-31   | 2024-08-31 00:00:00     | 35          | 35   (周六 W35)
-- r21    | 2024-03-01   | 2024-03-01 00:00:00     | 9           | 9    (周五 W9)
-- r22    | NULL         | 1994-09-27 10:00:00     | NULL        | 39   (DATE NULL)
-- r23    | 1994-09-27   | NULL                    | 39          | NULL (TIMESTAMP NULL)
-- r24    | NULL         | NULL                    | NULL        | NULL (双 NULL)
--
-- 场景覆盖:
--   跨年 ISO 周边界: 新年W1(2024-01-01) | 上年W52(2023-01-01) | 上年W53(2021-01-01)
--                    下年W1(2024-12-30/31) | 本年W52/W53(年末)
--   W39 经典示例 | 同周两天(09-30/10-01 同W40, 11-13/11-18 同W46)
--   闰年 2-29 | 历史日期 | 各月代表点
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
