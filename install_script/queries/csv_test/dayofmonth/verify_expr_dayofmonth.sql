-- =============================================================================
-- DAYOFMONTH 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — DAYOFMONTH(date) 返回 1~31，等价 EXTRACT(DAY FROM date)
--       示例: DAYOFMONTH(DATE '1994-09-27') = 27
-- 向量化: dayofmonth({DATE32|INT}) -> INT (不支持 TIMESTAMP 直传, 需 CAST AS DATE)
--
-- 上传 CSV:
--   install_script/queries/csv_test/dayofmonth/verify_expr_dayofmonth.csv -> /tmp/verify_expr_dayofmonth.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_dayofmonth.sql
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/dayofmonth/verify_expr_dayofmonth.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id            STRING,   -- 行标签
  r_dom_date        INT      -- DAYOFMONTH(d)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(DAYOFMONTH(d) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照):
--
-- row_id | d            | ts                      | r_dom_date | r_dom_ts_cast
-- -------|--------------|-------------------------|------------|--------------
-- r01    | 2024-01-01   | 2024-01-01 00:00:00     | 1          | 1    (月初=1)
-- r02    | 2024-01-15   | 2024-01-15 10:00:00     | 15         | 15   (月中=15)
-- r03    | 2024-01-31   | 2024-01-31 23:59:59.999 | 31         | 31   (31天月月末)
-- r04    | 2024-04-30   | 2024-04-30 12:00:00     | 30         | 30   (30天月月末)
-- r05    | 2024-06-30   | 2024-06-30 12:00:00     | 30         | 30   (30天月月末)
-- r06    | 2024-09-30   | 2024-09-30 23:59:59.999 | 30         | 30   (30天月月末)
-- r07    | 2024-11-30   | 2024-11-30 00:00:00     | 30         | 30   (30天月月末)
-- r08    | 2024-02-28   | 2024-02-28 00:00:00     | 28         | 28   (平年2月末=28)
-- r09    | 2020-02-29   | 2020-02-29 12:00:00     | 29         | 29   (闰年2月末=29)
-- r10    | 2024-02-29   | 2024-02-29 12:00:00     | 29         | 29   (闰年2月末=29)
-- r11    | 1994-09-27   | 1994-09-27 15:30:45     | 27         | 27   (经典示例)
-- r12    | 2024-03-01   | 2024-03-01 00:00:00     | 1          | 1    (月初=1)
-- r13    | 2024-07-01   | 2024-07-01 00:00:00     | 1          | 1    (月初=1)
-- r14    | 2024-10-01   | 2024-10-01 00:00:00     | 1          | 1    (月初=1)
-- r15    | 2024-12-31   | 2024-12-31 23:59:59.999 | 31         | 31   (31天月月末)
-- r16    | 2024-05-31   | 2024-05-31 00:00:00     | 31         | 31   (31天月月末)
-- r17    | 2024-07-31   | 2024-07-31 00:00:00     | 31         | 31   (31天月月末)
-- r18    | 2024-08-31   | 2024-08-31 00:00:00     | 31         | 31   (31天月月末)
-- r19    | 2023-11-12   | 2023-11-12 00:00:00     | 12         | 12   (月中=12)
-- r20    | 2023-11-18   | 2023-11-18 00:00:00     | 18         | 18   (月中=18)
-- r21    | 2024-04-15   | 2024-04-15 00:00:00     | 15         | 15   (月中=15)
-- r22    | NULL         | 1994-09-27 10:00:00     | NULL       | 27   (DATE NULL)
-- r23    | 1994-09-27   | NULL                    | 27         | NULL (TIMESTAMP NULL)
-- r24    | NULL         | NULL                    | NULL       | NULL (双 NULL)
--
-- 场景覆盖:
--   月初=1 | 月中=15/12/18 | 月末 28(平年2月)/29(闰年2月)/30(4,6,9,11月)/31(1,3,5,7,8,10,12月)
--   闰年2-29 vs 平年2-28 | 经典 1994-09-27=27 | 历史日期
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
