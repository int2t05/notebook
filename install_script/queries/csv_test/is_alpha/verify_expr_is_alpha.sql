-- =============================================================================
-- IS_ALPHA(string) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — IS_ALPHA(string)
--   Returns true if all characters in string are letter, otherwise false.
--   Flink 实现: SqlFunctionUtils.isAlpha -> Apache Commons Lang3 StringUtils.isAlpha
--   (仅 ASCII 字母 A-Z/a-z; 空串/NULL -> false; 数值入参 -> false)
-- 向量化: is_alpha({VARCHAR}|{CHAR}|{数值类型}) -> BOOLEAN
--   注册名 "is_alpha" (RegisterConditional.cpp, Path B VectorFunction)
--
-- 上传 CSV:
--   install_script/queries/csv_test/is_alpha/verify_expr_is_alpha.csv
--   -> /opt/buildtools/install_script/queries/csv_test/is_alpha/verify_expr_is_alpha.csv
--
-- 用法: 用 config.sh 切换 OmniStream / 原生 Flink 两种引擎，跑同一份 CSV + SQL，
--   归一化后 diff，验证逐行一致。
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/is_alpha/verify_expr_is_alpha.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id  STRING,
  r_str   BOOLEAN,    -- IS_ALPHA(s)        : CSV 字符串列
  r_empty BOOLEAN,    -- IS_ALPHA('')       : 空串字面量 -> false
  r_null  BOOLEAN,    -- IS_ALPHA(CAST(NULL AS STRING)) : NULL -> false
  r_num   BOOLEAN     -- IS_ALPHA(CAST(123 AS STRING)) : 数值经 CAST -> false
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  IS_ALPHA(s),
  IS_ALPHA(''),
  IS_ALPHA(CAST(NULL AS STRING)),
  IS_ALPHA(CAST(123 AS STRING))
FROM src;

-- =============================================================================
-- 期望输出 (Flink IS_ALPHA = StringUtils.isAlpha, 仅 ASCII 字母):
--
-- row_id | s       | r_str | r_empty | r_null | r_num
-- -------|---------|-------|---------|--------|------
-- r01    | abc     | true  | false   | false  | false
-- r02    | AbC     | true  | false   | false  | false
-- r03    | xyz     | true  | false   | false  | false
-- r04    | Hello   | true  | false   | false  | false
-- r05    | WORLD   | true  | false   | false  | false
-- r06    | abc123  | false | false   | false  | false
-- r07    | 123     | false | false   | false  | false
-- r08    | 11.4445 | false | false   | false  | false
-- r09    | a1      | false | false   | false  | false
-- r10    | 1a      | false | false   | false  | false
-- r11    | abc def | false | false   | false  | false   (含空格)
-- r12    | a-b     | false | false   | false  | false   (含连字符)
-- r13    | a.b     | false | false   | false  | false   (含点)
-- r14    | a_b     | false | false   | false  | false   (含下划线)
-- r15    | 12345   | false | false   | false  | false
-- r16    | null    | false | false   | false  | false   (NULL 入参 -> false)
-- r17    | 中      | false | false   | false  | false   (非 ASCII)
-- r18    | αβγ     | false | false   | false  | false   (希腊字母, 非 ASCII)
-- r19    | café    | false | false   | false  | false   (含重音字母 é)
-- r20    | Ü       | false | false   | false  | false   (非 ASCII)
-- r21    | a       | true  | false   | false  | false
-- r22    | Z       | true  | false   | false  | false
-- r23    | 1       | false | false   | false  | false
-- r24    | abcABC  | true  | false   | false  | false
-- r25    | xyz9    | false | false   | false  | false
-- r26    | HELLO   | true  | false   | false  | false
-- r27    | null    | false | false   | false  | false   (NULL 入参 -> false)
-- r28    | 空      | false | false   | false  | false   (非 ASCII)
-- r29    | ABCDEFG | true  | false   | false  | false
-- r30    | a1b2c3  | false | false   | false  | false
--
-- 场景覆盖: 全字母(大小写/混合) | 含数字 | 全数字 | 含空格/连字符/点/下划线
--           | NULL | 空串字面量 | 数值经 CAST | 非 ASCII(中文/希腊/重音)
-- =============================================================================
