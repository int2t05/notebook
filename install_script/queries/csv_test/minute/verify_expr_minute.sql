-- =============================================================================
-- MINUTE 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — MINUTE(timestamp) 返回 0~59 的分钟数
--       等价 EXTRACT(MINUTE FROM timestamp)。例: MINUTE(TIMESTAMP '1994-09-27 13:14:15') 返回 14
-- 向量化: minute({TIMESTAMP}) -> INT (直接支持 TIMESTAMP 直传, 无需 CAST)
-- 注: MINUTE 只对时间戳有意义(从时间分量取分钟), 故本测试用 TIMESTAMP(0) 列
--       native minute 实现内部读 session timezone(QueryConfig), 无需适配层注入 tz 字面量
--
-- 上传 CSV:
--   install_script/queries/csv_test/minute/verify_expr_minute.csv -> /opt/buildtools/install_script/queries/csv_test/minute/verify_expr_minute.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/minute/verify_expr_minute.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id    STRING,   -- 行标签
  r_minute  INT       -- MINUTE(ts)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(MINUTE(ts) AS INT)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, UTC, MINUTE 取 0~59):
--
-- row_id | ts                    | r_minute
-- -------|-----------------------|---------
-- r01    | 2024-01-15 13:00:00   | 0      (整点, 分钟=0)
-- r02    | 2024-01-15 13:01:00   | 1      (分钟=1)
-- r03    | 2024-01-15 13:14:15   | 14     (经典示例 13:14:15 -> 14)
-- r04    | 2024-01-15 13:30:00   | 30     (半点)
-- r05    | 2024-01-15 13:59:00   | 59     (分钟上界)
-- r06    | 2024-01-15 13:59:59   | 59     (跨小时前最后一秒, 仍 59)
-- r07    | 2024-01-15 14:00:00   | 0      (跨小时整点, 回到 0)
-- r08    | 1994-09-27 13:14:15   | 14     (历史日期经典)
-- r09    | 2024-12-31 23:59:59   | 59     (年末最后一秒)
-- r10    | 2024-03-10 02:30:45   | 30     (DST 边界附近, UTC 无 DST, 正常取 30)
-- r11    | 2024-01-15 00:00:00   | 0      (零点零分)
-- r12    | NULL                  | NULL   (TIMESTAMP NULL)
--
-- 场景覆盖:
--   分钟边界 0/1/30/59 | 跨小时 13:59:59→14:00:00(59→0) | 跨年 23:59:59
--   整点(=0) | 经典 13:14:15(=14) | 历史日期 | 零点 | NULL 传播
--   TIMESTAMP(0) 秒精度(无小数秒), 验证 native 直传 TIMESTAMP 路径(不经 CAST AS DATE)
-- =============================================================================
