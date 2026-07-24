-- =============================================================================
-- SECOND 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — SECOND(timestamp) 等价 EXTRACT(SECOND FROM timestamp)
--       返回一分钟内的秒数 (0-59)，小数秒被截断。
-- 向量化: second({OMNI_TIMESTAMP}) -> INT  (RegisterDateTime.cpp / Second.cpp)
--         OmniOperator 内部按微秒处理, StreamCalcBatch 已在边界完成 ms<->us 换算。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/second/verify_expr_second.csv -> /tmp/verify_expr_second.csv
--
-- 对比流程 (见 .cursor/skills/omniadaptor-vectorized-expression/SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_second.sql
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  ts     TIMESTAMP(3)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/second/verify_expr_second.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id    STRING,   -- 行标签, 便于 diff 对照
  r_second  INT       -- SECOND(ts)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(SECOND(ts) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r_second], 按 row_id 对照):
--
-- row_id | ts                      | r_second
-- -------|-------------------------|---------
-- r01    | 1994-09-27 13:14:15.000 | 15        (普通秒)
-- r02    | 2000-01-01 00:00:00.000 | 0         (最小边界 0)
-- r03    | 1999-12-31 23:59:59.999 | 59        (最大边界 59, 小数秒截断)
-- r04    | 2020-02-29 12:30:45.500 | 45        (闰日 + 小数秒截断)
-- r05    | 1970-01-01 00:00:00.000 | 0         (epoch)
-- r06    | 2024-06-25 08:09:01.001 | 1         (小数秒截断)
-- r07    | NULL                    | NULL      (TIMESTAMP NULL)
-- r08    | 2023-11-09 09:00:30.250 | 30        (小数秒截断)
--
-- 场景覆盖:
--   普通秒 | 0/59 边界 | 小数秒截断 | 闰日 | epoch | NULL
-- =============================================================================
