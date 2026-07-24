-- =============================================================================
-- DAYOFYEAR 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — DAYOFYEAR(date) 返回 1~366，等价 EXTRACT(DOY FROM date)
--       示例: DAYOFYEAR(DATE '1994-09-27') = 270
-- 向量化: dayofyear({DATE32|INT}) -> INT (不支持 TIMESTAMP 直传, 需 CAST AS DATE)
--
-- 上传 CSV:
--   install_script/queries/csv_test/dayofyear/verify_expr_dayofyear.csv -> /tmp/verify_expr_dayofyear.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_dayofyear.sql
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/dayofyear/verify_expr_dayofyear.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id            STRING,   -- 行标签
  r_doy_date        INT      -- DAYOFYEAR(d)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(DAYOFYEAR(d) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | d            | ts                      | r_doy_date | r_doy_ts_cast
-- -------|--------------|-------------------------|------------|--------------
-- r01    | 2024-01-01   | 2024-01-01 00:00:00     | 1          | 1    (年初=1)
-- r02    | 2024-01-02   | 2024-01-02 00:00:00     | 2          | 2    (年第2天)
-- r03    | 2024-12-30   | 2024-12-30 08:00:00     | 365        | 365  (闰年第365天)
-- r04    | 2024-12-31   | 2024-12-31 23:59:59.999 | 366        | 366  (闰年年末=366)
-- r05    | 2023-12-31   | 2023-12-31 23:59:59.999 | 365        | 365  (平年年末=365)
-- r06    | 2020-12-31   | 2020-12-31 12:00:00     | 366        | 366  (闰年年末=366)
-- r07    | 2020-02-29   | 2020-02-29 12:00:00     | 60         | 60   (闰年2-29=60)
-- r08    | 2024-02-29   | 2024-02-29 12:00:00     | 60         | 60   (闰年2-29=60)
-- r09    | 2024-03-01   | 2024-03-01 00:00:00     | 61         | 61   (闰年3-1=61)
-- r10    | 2023-03-01   | 2023-03-01 00:00:00     | 60         | 60   (平年3-1=60)
-- r11    | 1994-09-27   | 1994-09-27 15:30:45     | 270        | 270  (经典示例)
-- r12    | 2024-09-30   | 2024-09-30 23:59:59.999 | 274        | 274  (9月末=274)
-- r13    | 2024-10-01   | 2024-10-01 00:00:00     | 275        | 275  (10月初=275)
-- r14    | 2024-06-30   | 2024-06-30 12:00:00     | 182        | 182  (6月末=182)
-- r15    | 2024-07-01   | 2024-07-01 00:00:00     | 183        | 183  (7月初=183)
-- r16    | 2024-04-01   | 2024-04-01 00:00:00     | 92         | 92   (4月初=92)
-- r17    | 2024-05-31   | 2024-05-31 00:00:00     | 152        | 152  (5月末=152)
-- r18    | 2024-08-31   | 2024-08-31 00:00:00     | 244        | 244  (8月末=244)
-- r19    | 2024-11-30   | 2024-11-30 00:00:00     | 335        | 335  (11月末=335)
-- r20    | 2023-11-12   | 2023-11-12 00:00:00     | 316        | 316  (11月周日=316)
-- r21    | 2023-11-18   | 2023-11-18 00:00:00     | 322        | 322  (11月周六=322)
-- r22    | NULL         | 1994-09-27 10:00:00     | NULL       | 270  (DATE NULL)
-- r23    | 1994-09-27   | NULL                    | 270        | NULL (TIMESTAMP NULL)
-- r24    | NULL         | NULL                    | NULL       | NULL (双 NULL)
--
-- 场景覆盖:
--   年初=1 | 年末 365(平年)/366(闰年) | 闰年2-29=60 | 闰年3-1=61 vs 平年3-1=60
--   月初/月末累积天数(4-1,6-30,7-1,9-30,10-1) | 经典 1994-09-27=270 | 历史日期
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
