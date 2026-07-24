-- =============================================================================
-- TO_TIMESTAMP 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml
--   TO_TIMESTAMP(string1[, string2]) 默认格式 'yyyy-MM-dd HH:mm:ss', UTC+0
-- 向量化: get_timestamp({VARCHAR,VARCHAR}) -> TIMESTAMP
--
-- 上传 CSV:
--   install_script/OmniStream/verify_expr_to_timestamp.csv -> /tmp/verify_expr_to_timestamp.csv
--
-- CSV 列约定:
--   s_def  — 单参 TO_TIMESTAMP(s_def) 测试 (默认格式)
--   s_fmt + fmt — 双参 TO_TIMESTAMP(s_fmt, fmt) 测试
--   同一行只填其中一种路径, 避免混测
--
-- 用法同 verify_expr_year.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s_def  STRING,
  s_fmt  STRING,
  fmt    STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/to_timestamp/verify_expr_to_timestamp.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id     STRING,
  r_default  TIMESTAMP(3),   -- TO_TIMESTAMP(s_def)  单参默认格式
  r_custom   TIMESTAMP(3)    -- TO_TIMESTAMP(s_fmt, fmt)  双参自定义格式
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  TO_TIMESTAMP(s_def),
  TO_TIMESTAMP(s_fmt, fmt)
FROM src;

-- =============================================================================
-- 期望输出 (UTC, 按 row_id 对照; print 中 TIMESTAMP 形如 2021-01-01T00:00:00):
--
-- row_id | 测试路径              | 输入                              | 期望 r_default / r_custom
-- -------|-----------------------|-----------------------------------|---------------------------
-- r01    | 默认格式-午夜         | 2021-01-01 00:00:00               | 2021-01-01 00:00:00 / NULL
-- r02    | 默认格式-带时分秒     | 1994-09-27 15:30:45               | 1994-09-27 15:30:45 / NULL
-- r03    | 默认格式-闰日         | 2020-02-29 12:34:56               | 2020-02-29 12:34:56 / NULL
-- r04    | 默认格式-年末         | 2024-12-31 23:59:59               | 2024-12-31 23:59:59 / NULL
-- r05    | 默认格式-普通时刻     | 2024-06-15 08:30:00               | 2024-06-15 08:30:00 / NULL
-- r06    | 自定义 yyyy-MM-dd     | 2024-06-15 + yyyy-MM-dd           | NULL / 2024-06-15 00:00:00
-- r07    | 自定义含毫秒          | 2020-02-29 12:34:56.789 + SSS     | NULL / 2020-02-29 12:34:56.789
-- r08    | 自定义仅日期          | 1994-09-27 + yyyy-MM-dd           | NULL / 1994-09-27 00:00:00
-- r09    | 非法字符串            | not-a-date + yyyy-MM-dd           | NULL / NULL (解析失败)
-- r10    | 非法月份(自定义格式)  | 2021-13-01 00:00:00 + yyyy-MM-dd HH:mm:ss | NULL / NULL
-- r11    | 全 NULL               | null,null,null                    | NULL / NULL
-- r12    | 默认格式-新年         | 2024-01-01 00:00:00               | 2024-01-01 00:00:00 / NULL
-- r13    | 自定义无毫秒格式      | 2024-06-15 08:30:00 + yyyy-MM-dd HH:mm:ss
--        |                       |                                   | NULL / 2024-06-15 08:30:00
--
-- 场景覆盖:
--   默认格式: 午夜/带时分秒/闰日/年末/新年
--   自定义格式: yyyy-MM-dd | yyyy-MM-dd HH:mm:ss | yyyy-MM-dd HH:mm:ss.SSS
--   解析失败: 非日期串 | 非法月份
--   NULL 传播: 输入串 NULL | 全列 NULL
-- =============================================================================
