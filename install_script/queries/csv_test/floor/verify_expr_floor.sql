-- =============================================================================
-- FLOOR(timepoint TO timeintervalunit) — Flink 原生测试 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       FLOOR(timepoint TO timeintervalunit): 把 timepoint 向下取整到 timeintervalunit 的起点。
--       例: FLOOR(TIME '12:44:31' TO MINUTE) -> 12:44:00。
-- 语法: FLOOR(<timepoint> TO <UNIT>)，TO 关键字必填，UNIT 为裸关键字。
-- 支持的 UNIT: SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR
--              (另有 MILLISECOND/DECADE/CENTURY/MILLENNIUM, 本测试不覆盖)
-- 返回类型 = 输入类型 (TIMESTAMP->TIMESTAMP, DATE->DATE, TIME->TIME), nullable。
--   * TIME 类型只支持天内 UNIT (SECOND/MINUTE/HOUR); DAY 及以上对 TIME 无意义。
-- 关键语义:
--   * 截断到 UNIT 起点向下取整 (floor, 非 round)。
--   * WEEK 以【周日】为周首 (sun=0, sat=6): 周六 2020-02-29 floor TO WEEK -> 周日 2020-02-23。
--   * QUARTER: (month-1)/3*3+1 月 1 日。YEAR: 当年 1 月 1 日。MONTH: 当月 1 日。
--   * 文档示例: FLOOR(TIME '12:44:31' TO MINUTE) -> 12:44:00 (本测试 r08 即用此时间)。
--   * NULL 入参 -> NULL 输出。
--
-- 说明: 本测试只测 Flink 原生 (不涉及 OmniStream 向量化), 用于建立 FLOOR 基准行为。
--
-- 上传 CSV:
--   install_script/queries/csv_test/floor/verify_expr_floor.csv
--   -> /opt/buildtools/install_script/queries/csv_test/floor/verify_expr_floor.csv
--
-- 跑法 (原生 Flink):
--   source /etc/profile
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_floor.sql
--   grep -E '^\+I\[' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  d      DATE,
  ts     TIMESTAMP(3),
  t      TIME(3)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/floor/verify_expr_floor.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id       STRING,
  -- ts (TIMESTAMP) floor 到各 UNIT, 均返回 TIMESTAMP
  f_sec        TIMESTAMP(3),
  f_min        TIMESTAMP(3),
  f_hour       TIMESTAMP(3),
  f_day        TIMESTAMP(3),
  f_week       TIMESTAMP(3),
  f_month      TIMESTAMP(3),
  f_quarter    TIMESTAMP(3),
  f_year       TIMESTAMP(3),
  -- d (DATE) floor 到日期级 UNIT, 均返回 DATE
  fd_day       DATE,
  fd_week      DATE,
  fd_month     DATE,
  fd_quarter   DATE,
  fd_year      DATE,
  -- t (TIME) floor 到天内 UNIT, 均返回 TIME (DAY 及以上对 TIME 无意义)
  ft_sec       TIME(3),
  ft_min       TIME(3),
  ft_hour      TIME(3)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  FLOOR(ts TO SECOND),
  FLOOR(ts TO MINUTE),
  FLOOR(ts TO HOUR),
  FLOOR(ts TO DAY),
  FLOOR(ts TO WEEK),
  FLOOR(ts TO MONTH),
  FLOOR(ts TO QUARTER),
  FLOOR(ts TO YEAR),
  FLOOR(d TO DAY),
  FLOOR(d TO WEEK),
  FLOOR(d TO MONTH),
  FLOOR(d TO QUARTER),
  FLOOR(d TO YEAR),
  FLOOR(t TO SECOND),
  FLOOR(t TO MINUTE),
  FLOOR(t TO HOUR)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, UTC, WEEK 以周日为周首):
-- 列序: row_id | d | ts | t | f_sec..f_year(8, ts) | fd_day..fd_year(5, d) | ft_sec/ft_min/ft_hour(3, t)
--
-- row_id | d            | ts                      | t           | f_sec..f_year (ts, 8 列) | fd_day..fd_year (d, 5 列) | ft_sec | ft_min | ft_hour
-- r01    | 2024-03-15   | 2024-03-15 10:30:45.123 | 10:30:45.123 | 10:30:45 / 10:30:00 / 10:00:00 / 00:00:00 / 03-10 / 03-01 / 01-01 / 01-01 | 03-15 / 03-10 / 03-01 / 01-01 / 01-01 | 10:30:45 | 10:30:00 | 10:00:00
--   (月中周五; WEEK: 周五->周日 03-10)
-- r02    | 2024-01-01   | 2024-01-01 00:00:00.000 | 00:00:00.000 | 00:00:00 x4 / WEEK=2023-12-31 / 01-01 / 01-01 / 01-01 | 01-01 / 2023-12-31 / 01-01 / 01-01 / 01-01 | 00:00:00 | 00:00:00 | 00:00:00
--   (年初周一; WEEK: 周一->前日周日 2023-12-31, 跨年回退; t 已是 00:00:00 各 unit 自身)
-- r03    | 2024-12-31   | 2024-12-31 23:59:59.999 | 23:59:59.999 | 23:59:59 / 23:59:00 / 23:00:00 / 00:00:00 / 12-29 / 12-01 / 10-01 / 01-01 | 12-31 / 12-29 / 12-01 / 10-01 / 01-01 | 23:59:59 | 23:59:00 | 23:00:00
--   (年末周二; QUARTER->Q4 起 10-01; WEEK: 周二->周日 12-29)
-- r04    | 2020-02-29   | 2020-02-29 01:56:59.987 | 01:56:59.987 | 01:56:59 / 01:56:00 / 01:00:00 / 00:00:00 / 02-23 / 02-01 / 01-01 / 01-01 | 02-29 / 02-23 / 02-01 / 01-01 / 01-01 | 01:56:59 | 01:56:00 | 01:00:00
--   (闰日周六; WEEK: 周六->周日 02-23, 与 TimeFunctionsITCase 一致; SECOND 丢毫秒)
-- r05    | 2024-03-31   | 2024-03-31 23:59:59.999 | 23:59:59.999 | 23:59:59 / 23:59:00 / 23:00:00 / 00:00:00 / 03-31 / 03-01 / 01-01 / 01-01 | 03-31 / 03-31 / 03-01 / 01-01 / 01-01 | 23:59:59 | 23:59:00 | 23:00:00
--   (Q1 末周日; WEEK: 已是周日->自身 03-31; QUARTER->Q1 起 01-01)
-- r06    | 2024-04-01   | 2024-04-01 00:00:00.000 | 00:00:00.000 | 00:00:00 x4 / WEEK=2024-03-31 / 04-01 / 04-01 / 01-01 | 04-01 / 2024-03-31 / 04-01 / 04-01 / 01-01 | 00:00:00 | 00:00:00 | 00:00:00
--   (Q2 初周一; WEEK: 周一->前日周日 03-31, 跨月回退; QUARTER->Q2 起 04-01)
-- r07    | 1994-09-27   | 1994-09-27 15:30:45.000 | 15:30:45.000 | 15:30:45 / 15:30:00 / 15:00:00 / 00:00:00 / 09-25 / 09-01 / 07-01 / 01-01 | 09-27 / 09-25 / 09-01 / 07-01 / 01-01 | 15:30:45 | 15:30:00 | 15:00:00
--   (经典周二; WEEK: 周二->周日 09-25; QUARTER->Q3 起 07-01)
-- r08    | NULL         | 2024-03-15 10:30:45.000 | 12:44:31.000 | ts 正常 (同 r01 时间部分) | d 相关全 NULL | 12:44:31 | 12:44:00 | 12:00:00
--   (DATE NULL; t=12:44:31 即 sql_functions.yml 文档示例时间, FLOOR(TO MINUTE)=12:44:00 印证文档)
-- r09    | 1994-09-27   | NULL                    | NULL         | ts 相关全 NULL | d 正常 (同 r07) | NULL | NULL | NULL
--   (TIMESTAMP+TIME NULL: ts/t 相关列全 NULL, d 正常)
-- r10    | NULL         | NULL                    | NULL         | 全 NULL | 全 NULL | NULL | NULL | NULL
--   (三列全 NULL: 全部 NULL)
--
-- 场景覆盖:
--   ts 路径: SECOND/MINUTE/HOUR/DAY/WEEK/MONTH/QUARTER/YEAR 全 8 unit (TIMESTAMP->TIMESTAMP)
--   d  路径: DAY/WEEK/MONTH/QUARTER/YEAR 5 unit (DATE->DATE)
--   t  路径: SECOND/MINUTE/HOUR 3 unit (TIME->TIME; DAY 及以上对 TIME 无意义)
--   边界: 年初(周一->跨年周日)/年末/Q1末(周日自身)/Q2初(周一->跨月周日)/闰日周六
--   WEEK 周首=周日 验证: 周一/周二/周五/周六/周日 各覆盖
--   QUARTER 跨季: Q1末->01-01, Q2初->04-01, Q3->07-01, Q4末->10-01
--   TIME: 文档示例 12:44:31->12:44:00 | 天边界 00:00:00/23:59:59 | 毫秒(SECOND 丢毫秒)
--   NULL 传播: DATE NULL / TIMESTAMP+TIME NULL / 三列全 NULL
-- =============================================================================
