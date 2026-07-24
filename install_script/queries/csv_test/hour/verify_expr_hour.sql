-- =============================================================================
-- HOUR 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — HOUR(timestamp) 返回 0~23 的小时数
--       等价 EXTRACT(HOUR FROM timestamp)。例: HOUR(TIMESTAMP '1994-09-27 13:14:15') 返回 13
-- 向量化: hour({TIMESTAMP|LONG}) -> INT (直接支持 TIMESTAMP 直传, 无需 CAST)
-- 注: HOUR 只对时间戳有意义(从时间分量取小时), 故本测试用 TIMESTAMP(0) 列, 不再用 DATE 列
--
-- 上传 CSV:
--   install_script/queries/csv_test/hour/verify_expr_hour.csv -> /opt/buildtools/install_script/queries/csv_test/hour/verify_expr_hour.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================
 
SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';
 
CREATE TABLE src (
  row_id STRING,
  ts     TIMESTAMP(0)
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/hour/verify_expr_hour.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);
 
CREATE TABLE sink (
  row_id   STRING,   -- 行标签
  r_hour   INT       -- HOUR(ts)
) WITH (
  'connector' = 'print'
);
 
INSERT INTO sink
SELECT
  row_id,
  CAST(HOUR(ts) AS INT)
FROM src;
 
-- =============================================================================
-- 期望输出 (按 row_id 对照, UTC, HOUR 取 0~23):
--
-- row_id | ts                    | r_hour
-- -------|-----------------------|-------
-- r01    | 2024-01-15 00:00:00   | 0     (零点/午夜)
-- r02    | 2024-01-15 01:00:00   | 1     (凌晨1点)
-- r03    | 2024-01-15 09:00:00   | 9     (上午9点)
-- r04    | 2024-01-15 12:00:00   | 12    (正午12点)
-- r05    | 2024-01-15 13:14:15   | 13    (经典示例 13:14:15)
-- r06    | 2024-01-15 23:00:00   | 23    (23点/小时上界)
-- r07    | 2024-01-15 23:59:59   | 23    (跨日前最后一秒, 仍 23)
-- r08    | 2024-01-16 00:00:00   | 0     (跨日零点, 回到 0)
-- r09    | 1994-09-27 13:14:15   | 13    (历史日期经典)
-- r10    | 2024-12-31 23:59:59   | 23    (年末最后一秒)
-- r11    | 2024-03-10 02:30:00   | 2     (夏令时边界附近, UTC 无 DST, 正常取 2)
-- r12    | NULL                  | NULL  (TIMESTAMP NULL)
--
-- 场景覆盖:
--   小时边界 0/1/12/23 | 跨日 23:59:59→次日 00:00:00(23→0) | 跨年 23:59:59
--   上午/下午/正午 | 经典 13:14:15(=13) | 历史日期 | NULL 传播
--   TIMESTAMP(0) 秒精度(无小数秒), 验证 native 直传 TIMESTAMP 路径(不经 CAST AS DATE)
-- =============================================================================
 