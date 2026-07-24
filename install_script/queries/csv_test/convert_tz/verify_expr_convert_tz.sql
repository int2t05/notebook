-- =============================================================================
-- CONVERT_TZ 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml
--   CONVERT_TZ(string1, string2, string3): 将 datetime string1 (默认 ISO 格式
--   'yyyy-MM-dd HH:mm:ss') 从时区 string2 转换到时区 string3。返回同格式字符串。
--   例: CONVERT_TZ('1970-01-01 00:00:00', 'UTC', 'America/Los_Angeles') -> '1969-12-31 16:00:00'
--   等价 Flink: DateTimeUtils.convertTz(dateStr, tzFrom, tzTo)
-- 向量化: convert_tz(VARCHAR, VARCHAR, VARCHAR) -> VARCHAR (3 个 string 入参, 直接适配, 无 CAST)
--   时区用 tz::locateZone + TimeZone::to_sys/to_local, 正确处理 DST。
--
-- 上传 CSV:
--   install_script/queries/csv_test/convert_tz/verify_expr_convert_tz.csv
--     -> /opt/buildtools/install_script/queries/csv_test/convert_tz/verify_expr_convert_tz.csv
--
-- 用法同 verify_expr_hour.sql (UTC + parallelism=1 + CSV 黄金对比):
--   切原生 Flink 跑基准 -> 切 OmniStream 跑对照 -> 归一化 diff 两份输出。
--
-- 注: CONVERT_TZ 结果不依赖 session 时区(显式给出 from/to), 故 table.local-time-zone
--     设为 UTC 仅为环境一致性。未知时区/无法解析的 datetime 两引擎都返回 NULL。
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id  STRING,
  dt      STRING,
  tz_from STRING,
  tz_to   STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/convert_tz/verify_expr_convert_tz.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r      STRING
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(CONVERT_TZ(dt, tz_from, tz_to) AS STRING)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, UTC, Flink DateTimeUtils.convertTz 语义):
--
-- row_id | dt                   | tz_from             | tz_to               | r
-- -------|----------------------|---------------------|---------------------|----------------------
-- r01    | 1970-01-01 00:00:00  | UTC                 | America/Los_Angeles | 1969-12-31 16:00:00   (PST, UTC-8; sql_functions.yml 经典示例)
-- r02    | 1969-12-31 16:00:00  | America/Los_Angeles | UTC                 | 1970-01-01 00:00:00   (r01 逆转换, 回到 epoch)
-- r03    | 2024-06-15 12:30:45  | UTC                 | UTC                 | 2024-06-15 12:30:45   (同区恒等)
-- r04    | 2024-01-15 08:00:00  | +08:00              | UTC                 | 2024-01-15 00:00:00   (+08 -> UTC, -8h)
-- r05    | 2024-01-15 08:00:00  | GMT-08:00           | UTC                 | 2024-01-15 16:00:00   (GMT-8 -> UTC, +8h; 自定义 GMT ID)
-- r06    | 2024-07-15 00:00:00  | UTC                 | America/Los_Angeles | 2024-07-14 17:00:00   (PDT 夏令时, UTC-7)
-- r07    | 2024-01-15 00:00:00  | UTC                 | America/Los_Angeles | 2024-01-14 16:00:00   (PST 冬令时, UTC-8)
-- r08    | 2024-01-15 00:00:00  | UTC                 | Asia/Kolkata        | 2024-01-15 05:30:00   (+5:30 半小时偏移)
-- r09    | 1970-01-01 00:00:00  | UTC                 | +08:00              | 1970-01-01 08:00:00   (UTC -> +08, +8h, 跨 epoch 边界)
-- r10    | NULL                 | UTC                 | UTC                 | NULL                  (datetime NULL 传播)
-- r11    | not-a-date           | UTC                 | UTC                 | NULL                  (无法解析 -> NULL, 对齐 Flink ParseException->null)
-- r12    | 9999-12-31 23:59:59  | UTC                 | UTC                 | 9999-12-31 23:59:59   (大年份 4 位补零)
-- r13    | 2024-01-15 00:00:00  | Asia/Kolkata        | UTC                 | 2024-01-14 18:30:00   (+5:30 -> UTC, 前一天 18:30; 验证 from/to 顺序非互换)
-- r14    | 2024-03-15 12:00:00  | America/Los_Angeles | Asia/Shanghai       | 2024-03-16 03:00:00   (12:00 PDT=19:00 UTC -> 次日 03:00 +08; 跨日+DST+8h)
-- r15    | 2024-01-15 08:00:00  | UTC                 | +08:00              | 2024-01-15 16:00:00   (UTC -> +08, +8h)
-- r16    | 2024-01-15 23:59:59  | UTC                 | UTC                 | 2024-01-15 23:59:59   (日末秒, 同区恒等)
--
-- 场景覆盖:
--   正常转换 | 同区恒等 | 正/负偏移 | 自定义 GMT ID | 半小时偏移(印度)
--   夏令时(PDT)/冬令时(PST) | 跨 epoch 边界 | 跨日+DST 组合
--   大年份(9999) | 日末秒 | NULL 传播 | 无法解析->NULL
--   from/to 顺序非互换(r08 vs r13) | 经典示例(r01)
--
-- 注: 黄金对比集只含两引擎语义一致的行(合法日期 + 真正无法解析的字符串)。
--   Flink 的 SimpleDateFormat 默认 lenient, 会把 '2024-13-01'/'24:00:00' 等
--   越界字段宽松回滚成合法日期; native 实现为严格解析 -> NULL。这类 lenient/strict
--   差异行不放入黄金集(避免误报), 仅在 UT(MalformedDatetimeString)中验证 native
--   严格语义。如需对齐 lenient 行为可后续在 native 侧放宽解析。
-- =============================================================================
