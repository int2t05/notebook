-- =============================================================================
-- TO_DATE 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — TO_DATE(string1[, string2]) -> DATE
--       默认格式 'yyyy-MM-dd'；2-arg 用 Java SimpleDateFormat 模式；按 UTC 解析。
-- 向量化: to_date({VARCHAR,VARCHAR}|{CHAR,VARCHAR}) -> DATE32
--         (1-arg 在 OmniAdaptor 侧合成默认格式 'yyyy-MM-dd' 字面量再下发)
--
-- 注意(语义对齐): Flink 1-arg 手写解析器会在首个空格处截断(允许 'yyyy-MM-dd HH:mm:ss'
--   这类带时间的串)；向量化 to_date 用 strptime 严格按 'yyyy-MM-dd' 匹配，带时间尾的串
--   会解析失败→NULL。为保两引擎逐行一致，1-arg 路径只用纯日期串；带时间的串一律走 2-arg
--   且格式与串完全匹配的路径。
--
-- 上传 CSV:
--   install_script/queries/csv_test/to_date/verify_expr_to_date.csv -> /tmp/verify_expr_to_date.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_to_date.sql
--   grep -E '^\+I\[' $FLINK_HOME/log/flink-*-taskexecutor-*.out > /tmp/vanilla_out.txt
--   bash install_script/queries/csv_test/compare_native_vanilla.sh /tmp/flink_output.txt /tmp/vanilla_out.txt
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING,        -- 待解析的日期串
  f      STRING         -- 显式格式(2-arg 路径用)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/to_date/verify_expr_to_date.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id         STRING,
  r_to_date_def  DATE,    -- TO_DATE(s)  默认格式路径
  r_to_date_fmt  DATE     -- TO_DATE(s, f) 显式格式路径
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  TO_DATE(s),
  TO_DATE(s, f)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, UTC, 默认格式 'yyyy-MM-dd'):
--
-- row_id | s                    | f                  | r_to_date_def | r_to_date_fmt
-- -------|----------------------|--------------------|---------------|---------------
-- r01    | 1970-01-01           | yyyy-MM-dd         | 1970-01-01    | 1970-01-01   (epoch)
-- r02    | 2024-01-01           | yyyy-MM-dd         | 2024-01-01    | 2024-01-01   (年初)
-- r03    | 2024-01-15           | yyyy-MM-dd         | 2024-01-15    | 2024-01-15   (1月中)
-- r04    | 2024-12-31           | yyyy-MM-dd         | 2024-12-31    | 2024-12-31   (年末)
-- r05    | 2024/01/15           | yyyy/MM/dd         | NULL          | 2024-01-15   (1-arg默认不认斜杠;2-arg认)
-- r06    | 2020-02-29           | yyyy-MM-dd         | 2020-02-29    | 2020-02-29   (闰年2-29)
-- r07    | 1994-09-27           | yyyy-MM-dd         | 1994-09-27    | 1994-09-27   (经典日期)
-- r08    | 1969-12-31           | yyyy-MM-dd         | 1969-12-31    | 1969-12-31   (epoch前一天,负days)
-- r09    | 2024-01-15 10:30:45  | yyyy-MM-dd HH:mm:ss| NULL          | 2024-01-15   (带时间走2-arg;1-arg默认拒绝)
-- r10    | 2024/12/31 23:59:59  | yyyy/MM/dd HH:mm:ss| NULL          | 2024-12-31   (斜杠+时间走2-arg)
-- r11    | not-a-date           | yyyy-MM-dd         | NULL          | NULL         (非法串)
-- r12    | 2024-13-45           | yyyy-MM-dd         | NULL          | NULL         (非法月日,越界)
-- r13    | NULL                 | yyyy-MM-dd         | NULL          | NULL         (s NULL)
-- r14    | 2024-01-15           | NULL               | 2024-01-15    | NULL         (f NULL,2-arg->NULL)
-- r15    | NULL                 | NULL               | NULL          | NULL         (双 NULL)
--
-- 场景覆盖:
--   正常日期(默认+显式) | 斜杠格式(2-arg专属) | 闰年2-29 | 历史日期 | epoch/epoch前一天
--   带时间分量(2-arg 匹配格式,1-arg 默认拒绝->NULL 以保一致)
--   非法串/越界月日 -> NULL | s NULL | f NULL(2-arg->NULL) | 双 NULL
--   两路径对照: TO_DATE(s) vs TO_DATE(s,f) 揭示默认格式与显式格式的差异
-- =============================================================================
