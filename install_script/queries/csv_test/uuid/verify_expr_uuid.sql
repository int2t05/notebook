-- =============================================================================
-- UUID() 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — UUID() 返回 RFC 4122 type-4 伪随机 UUID 字符串
--   (如 "3d3c68f7-f608-473f-b60c-b0c44ad4cc4e")，36 字符，8-4-4-4-12 十六进制格式。
-- 向量化: uuid({}) -> VARCHAR (0 参，每行随机)
--
-- 注: UUID 非确定，native 用 std::mt19937 生成（非 Java SecureRandom），输出不会与 Flink
--     逐位匹配。本测试聚焦「格式正确性」(36 字符、8-4-4-4-12、version=4) 与「多行互异」。
--     compare_native_vanilla.sh 会因值不同而报 DIFF —— 预期，需人工核对格式。
--
-- 上传 CSV:
--   install_script/queries/csv_test/uuid/verify_expr_uuid.csv -> /opt/buildtools/install_script/queries/csv_test/uuid/verify_expr_uuid.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/uuid/verify_expr_uuid.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id  STRING,
  r_uuid  STRING
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  UUID()
FROM src;

-- =============================================================================
-- 验证规则（非逐位，因 RNG 不同）:
--   - 每行 UUID() 为 36 字符，格式 8-4-4-4-12 十六进制
--   - 第 3 段以 '4' 开头（RFC4122 version 4）
--   - 第 4 段首位为 {8,9,a,b}（RFC4122 variant）
--   - 多行 UUID 互异（每行随机）
--
-- row_id | r_uuid (36 字符 UUID v4)
-- -------|--------------------------------------
-- r01    | xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
-- r02    | xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
-- r03    | xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
-- r04    | xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
-- =============================================================================
