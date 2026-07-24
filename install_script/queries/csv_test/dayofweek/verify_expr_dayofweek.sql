-- =============================================================================
-- DAYOFWEEK 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — DAYOFWEEK(date) 返回 1~7，等价 EXTRACT(DOW FROM date)
--       约定: 1=周日(Sunday) .. 7=周六(Saturday)。示例: DAYOFWEEK(DATE '1994-09-27') = 3 (周二)
-- 向量化: dayofweek({DATE32|INT}) -> INT (不支持 TIMESTAMP 直传, 需 CAST AS DATE)
--
-- 上传 CSV:
--   install_script/queries/csv_test/dayofweek/verify_expr_dayofweek.csv -> /tmp/verify_expr_dayofweek.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_dayofweek.sql
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/dayofweek/verify_expr_dayofweek.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id            STRING,   -- 行标签
  r_dow_date        INT      -- DAYOFWEEK(d)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(DAYOFWEEK(d) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 1=周日..7=周六):
--
-- row_id | d            | 星期 | ts                      | r_dow_date | r_dow_ts_cast
-- -------|--------------|------|-------------------------|------------|--------------
-- r01    | 2023-11-12   | 周日 | 2023-11-12 00:00:00     | 1          | 1    (Sunday=1)
-- r02    | 2023-11-13   | 周一 | 2023-11-13 00:00:00     | 2          | 2    (Monday=2)
-- r03    | 1994-09-27   | 周二 | 1994-09-27 15:30:45     | 3          | 3    (经典示例 Tue=3)
-- r04    | 2023-11-14   | 周二 | 2023-11-14 00:00:00     | 3          | 3    (Tuesday=3)
-- r05    | 2023-11-15   | 周三 | 2023-11-15 00:00:00     | 4          | 4    (Wednesday=4)
-- r06    | 2023-11-16   | 周四 | 2023-11-16 00:00:00     | 5          | 5    (Thursday=5)
-- r07    | 2023-11-17   | 周五 | 2023-11-17 00:00:00     | 6          | 6    (Friday=6)
-- r08    | 2023-11-18   | 周六 | 2023-11-18 00:00:00     | 7          | 7    (Saturday=7)
-- r09    | 2024-02-29   | 周四 | 2024-02-29 12:00:00     | 5          | 5    (闰年2-29 Thu=5)
-- r10    | 2020-02-29   | 周六 | 2020-02-29 12:00:00     | 7          | 7    (闰年2-29 Sat=7)
-- r11    | 2024-01-01   | 周一 | 2024-01-01 00:00:00     | 2          | 2    (新年 Mon=2)
-- r12    | 2023-01-01   | 周日 | 2023-01-01 00:00:00     | 1          | 1    (新年 Sun=1)
-- r13    | 2024-12-31   | 周二 | 2024-12-31 23:59:59.999 | 3          | 3    (年末 Tue=3)
-- r14    | 2024-12-30   | 周一 | 2024-12-30 08:00:00     | 2          | 2    (年末前 Mon=2)
-- r15    | 2024-09-30   | 周一 | 2024-09-30 23:59:59.999 | 2          | 2    (9月末 Mon=2)
-- r16    | 2024-10-01   | 周二 | 2024-10-01 00:00:00     | 3          | 3    (10月初 Tue=3)
-- r17    | 2024-06-30   | 周日 | 2024-06-30 12:00:00     | 1          | 1    (6月末 Sun=1)
-- r18    | 2024-11-30   | 周六 | 2024-11-30 00:00:00     | 7          | 7    (11月末 Sat=7)
-- r19    | 2024-05-31   | 周五 | 2024-05-31 00:00:00     | 6          | 6    (5月末 Fri=6)
-- r20    | 2024-08-31   | 周六 | 2024-08-31 00:00:00     | 7          | 7    (8月末 Sat=7)
-- r21    | 2024-04-01   | 周一 | 2024-04-01 00:00:00     | 2          | 2    (4月初 Mon=2)
-- r22    | NULL         |  --  | 1994-09-27 10:00:00     | NULL       | 3    (DATE NULL)
-- r23    | 1994-09-27   | 周二 | NULL                    | 3          | NULL (TIMESTAMP NULL)
-- r24    | NULL         |  --  | NULL                    | NULL       | NULL (双 NULL)
--
-- 场景覆盖:
--   1~7 全部 7 个星期值(周日~周六) | 1994-09-27 周二=3 经典示例
--   闰年2-29 两年不同星期(2020=周六/2024=周四) | 跨年日期 | 各月末星期
--   DATE 直传 | TIMESTAMP CAST AS DATE | 各列 NULL 传播
-- =============================================================================
