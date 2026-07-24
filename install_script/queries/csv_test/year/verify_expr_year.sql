-- =============================================================================
-- YEAR 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — YEAR(date) 等价 EXTRACT(YEAR FROM date)
-- 向量化: year({DATE32|INT|TIMESTAMP}) -> INT
--
-- 上传 CSV 到服务器:
--   install_script/OmniStream/verify_expr_year.csv -> /tmp/verify_expr_year.csv
--
-- 对比流程 (见 .cursor/skills/omniadaptor-vectorized-expression/SKILL.md 步骤 5):
--   1. SET table.local-time-zone = 'UTC' 保证 TIMESTAMP 路径时区确定
--   2. 原生 Flink 跑一遍 -> TaskManager .out
--   3. OmniStream 使能后跑一遍 -> /tmp/flink_output.txt
--   4. compare_native_vanilla.sh 或 norm+diff 逐行对比
--
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_year.sql
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  ts     TIMESTAMP(3)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/year/verify_expr_year.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id       STRING,   -- 行标签, 便于 diff 对照
  r_year_ts    INT       -- YEAR(ts)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(YEAR(ts) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r_year_date, r_year_ts], 按 row_id 对照):
--
-- row_id | d            | ts                      | r_year_date | r_year_ts
-- -------|--------------|-------------------------|-------------|----------
-- r01    | 1994-09-27   | 1994-09-27 12:00:00     | 1994        | 1994
-- r02    | 2000-01-01   | 2000-01-01 00:00:00     | 2000        | 2000      (年初边界)
-- r03    | 1999-12-31   | 1999-12-31 23:59:59.999 | 1999        | 1999      (年末边界)
-- r04    | 2020-02-29   | 2020-02-29 12:00:00     | 2020        | 2020      (闰日)
-- r05    | 1970-01-01   | 1970-01-01 00:00:00     | 1970        | 1970      (epoch)
-- r06    | 2099-12-31   | 2099-12-31 23:59:59.999 | 2099        | 2099      (远未来)
-- r07    | NULL         | 1994-09-27 08:30:00     | NULL        | 1994      (DATE NULL)
-- r08    | 1994-09-27   | NULL                    | 1994        | NULL      (TIMESTAMP NULL)
-- r09    | NULL         | NULL                    | NULL        | NULL      (双 NULL)
-- r10    | 2024-01-01   | 2024-01-01 00:00:00.123 | 2024        | 2024      (TIMESTAMP 新年)
-- r11    | 2023-12-31   | 2023-12-31 23:59:59.999 | 2023        | 2023      (TIMESTAMP 年末 UTC)
-- r12    | 1989-11-09   | 1989-11-09 09:00:00     | 1989        | 1989      (普通 TIMESTAMP)
--
-- 场景覆盖:
--   正常年中/历史日期 | 年初/年末边界 | 闰年 2-29 | epoch | 远未来
--   DATE NULL | TIMESTAMP NULL | 双 NULL | DATE 与 TIMESTAMP 双路径
-- =============================================================================
