-- =============================================================================
-- HEX(numeric) / HEX(string) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — HEX 返回整数或字符串的十六进制字符串表示。
--   数值: HEX(20)="14", HEX(100)="64", HEX(-1)="FFFFFFFFFFFFFFFF"(64位补码)
--   字符串: HEX("helloworld")="68656C6C6F776F726C64"
--   NULL 输入返回 NULL。
-- 向量化: hex({LONG}/{VARCHAR}/{CHAR}/{VARBINARY}) -> VARCHAR
--   注: native 数值重载仅 {LONG}；INT 入参经 OmniAdaptor CAST AS BIGINT 后下发。
--
-- 上传 CSV:
--   install_script/queries/csv_test/hex/verify_expr_hex.csv -> /opt/buildtools/install_script/queries/csv_test/hex/verify_expr_hex.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  i      INT,        -- HEX(numeric) INT 路径（经 CAST AS BIGINT）
  l      BIGINT,     -- HEX(numeric) BIGINT 路径（直接 {LONG}）
  s      STRING      -- HEX(string) 路径
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/hex/verify_expr_hex.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id   STRING,
  r_hex_i  STRING,   -- HEX(i)
  r_hex_l  STRING,   -- HEX(l)
  r_hex_s  STRING    -- HEX(s)
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  HEX(i),
  HEX(l),
  HEX(s)
FROM src;

-- =============================================================================
-- 期望输出 (字符串列不含逗号以免破坏 CSV):
--
-- row_id | i    | l    | s          | r_hex_i | r_hex_l            | r_hex_s
-- -------|------|------|------------|---------|--------------------|----------------------------
-- r01    | 20   | 20   | helloworld | 14      | 14                 | 68656C6C6F776F726C64
-- r02    | 100  | 100  | abc        | 64      | 64                 | 616263
-- r03    | 255  | 255  | Z          | FF      | FF                 | 5A
-- r04    | 0    | 0    | (空)        | 0       | 0                  | (空字符串)
-- r05    | -1   | -1   | null       | FFFFFFFFFFFFFFFF | FFFFFFFFFFFFFFFF | NULL
-- r06    | null | null | helloworld | NULL    | NULL               | 68656C6C6F776F726C64
--
-- 场景覆盖: 数值(INT路径+BIGINT路径) | 正数/0/负数(64位补码) | 字符串 | NULL
--   注: 空字符串列在 CSV 中难以表达，r04 的 s 用单空格代替（HEX(" ")="20"）。
-- =============================================================================
