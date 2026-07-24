-- =============================================================================
-- IS_DECIMAL(string) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — IS_DECIMAL(string)
--   Returns true if string can be parsed to a valid numeric, otherwise false.
--   Flink 实现: SqlFunctionUtils.isDecimal -> isInteger(s) || isLong(s) || isDouble(s)
--   (等价于能否被 Java Double.parseDouble 解析; 空串/NULL -> false; 数值入参 -> true)
-- 向量化: is_decimal({VARCHAR}|{CHAR}|{数值类型}) -> BOOLEAN
--   注册名 "is_decimal" (RegisterConditional.cpp, Path B VectorFunction)
--
-- 上传 CSV:
--   install_script/queries/csv_test/is_decimal/verify_expr_is_decimal.csv
--   -> /opt/buildtools/install_script/queries/csv_test/is_decimal/verify_expr_is_decimal.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/is_decimal/verify_expr_is_decimal.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id  STRING,
  r_str   BOOLEAN,    -- IS_DECIMAL(s)                              : CSV 字符串列
  r_empty BOOLEAN,    -- IS_DECIMAL('')                             : 空串字面量 -> false
  r_null  BOOLEAN,    -- IS_DECIMAL(CAST(NULL AS STRING))           : NULL -> false
  r_ws    BOOLEAN,    -- IS_DECIMAL('  5  ')                        : 前后空白 -> true
  r_int   BOOLEAN,    -- IS_DECIMAL(CAST(123 AS INT))               : 数值入参(INT) -> true
  r_dbl   BOOLEAN     -- IS_DECIMAL(CAST(1.5 AS DOUBLE))            : 数值入参(DOUBLE) -> true
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  IS_DECIMAL(s),
  IS_DECIMAL(''),
  IS_DECIMAL(CAST(NULL AS STRING)),
  IS_DECIMAL('  5  '),
  IS_DECIMAL(CAST(123 AS INT)),
  IS_DECIMAL(CAST(1.5 AS DOUBLE))
FROM src;

-- =============================================================================
-- 期望输出 (Flink IS_DECIMAL = isInteger||isLong||isDouble ≈ Double.parseDouble 可解析):
--
-- row_id | s        | r_str | r_empty | r_null | r_ws  | r_int | r_dbl
-- -------|----------|-------|---------|--------|-------|-------|------
-- r01    | 1        | true  | false   | false  | true  | true  | true
-- r02    | 123      | true  | false   | false  | true  | true  | true
-- r03    | 0        | true  | false   | false  | true  | true  | true
-- r04    | 42       | true  | false   | false  | true  | true  | true
-- r05    | -123     | true  | false   | false  | true  | true  | true
-- r06    | +123     | true  | false   | false  | true  | true  | true
-- r07    | -0       | true  | false   | false  | true  | true  | true
-- r08    | 11.4445  | true  | false   | false  | true  | true  | true
-- r09    | 3.14     | true  | false   | false  | true  | true  | true
-- r10    | 0.5      | true  | false   | false  | true  | true  | true
-- r11    | .5       | true  | false   | false  | true  | true  | true
-- r12    | 5.       | true  | false   | false  | true  | true  | true
-- r13    | 1e10     | true  | false   | false  | true  | true  | true
-- r14    | 1E10     | true  | false   | false  | true  | true  | true
-- r15    | 1.5e3    | true  | false   | false  | true  | true  | true
-- r16    | 1.5E-3   | true  | false   | false  | true  | true  | true
-- r17    | 2e+5     | true  | false   | false  | true  | true  | true
-- r18    | 1e-10    | true  | false   | false  | true  | true  | true
-- r19    | -3.14    | true  | false   | false  | true  | true  | true
-- r20    | NaN      | true  | false   | false  | true  | true  | true
-- r21    | nan      | true  | false   | false  | true  | true  | true
-- r22    | NAN      | true  | false   | false  | true  | true  | true
-- r23    | Infinity | true  | false   | false  | true  | true  | true
-- r24    | infinity | true  | false   | false  | true  | true  | true
-- r25    | INF      | true  | false   | false  | true  | true  | true
-- r26    | +Infinity| true  | false   | false  | true  | true  | true
-- r27    | -Infinity| true  | false   | false  | true  | true  | true
-- r28    | 5        | true  | false   | false  | true  | true  | true
-- r29    | abc      | false | false   | false  | true  | true  | true
-- r30    | 1.2.3    | false | false   | false  | true  | true  | true
-- r31    | 1e       | false | false   | false  | true  | true  | true
-- r32    | e10      | false | false   | false  | true  | true  | true
-- r33    | 0x10     | false | false   | false  | true  | true  | true
-- r34    | 1f       | false | false   | false  | true  | true  | true
-- r35    | 1d       | false | false   | false  | true  | true  | true
-- r36    | --5      | false | false   | false  | true  | true  | true
-- r37    | null     | false | false   | false  | true  | true  | true   (NULL 入参 -> false)
-- r38    | 1a       | false | false   | false  | true  | true  | true
-- r39    | a1       | false | false   | false  | true  | true  | true
-- r40    | 5.       | true  | false   | false  | true  | true  | true
--
-- 场景覆盖: 整数 | 负数/正号 | 小数(含 .5 / 5.) | 科学计数法 | NaN/Infinity(大小写)
--           | 空白 | 空串 | NULL | 数值入参(INT/DOUBLE) | 非法格式(多小数点/无尾数指数
--           /十六进制/类型后缀/多符号/字母混合)
-- =============================================================================
