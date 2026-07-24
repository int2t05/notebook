-- =============================================================================
-- COT 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — COT(numeric) 返回余切 (入参为弧度, cot=cos/sin=1/tan)。
-- 向量化: cot({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: 1/std::tan)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/cot/verify_expr_cot.csv
--   -> /opt/buildtools/install_script/queries/csv_test/cot/verify_expr_cot.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  x      DOUBLE
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/cot/verify_expr_cot.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r      DOUBLE
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  CAST(COT(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 入参为弧度, cot=1/tan):
--
-- row_id | x                   | r (COT)
-- -------|---------------------|---------------------
-- r01    | 0.7853981633974483  | 1.0000000000000002   (cot(π/4)≈1)
-- r02    | 0.5235987755982988  | 1.7320508075688774   (cot(π/6)≈√3)
-- r03    | 1.0471975511965976  | 0.577350269189626    (cot(π/3)≈1/√3)
-- r04    | 1.5707963267948966  | 6.123233995736766E-17 (cot(π/2)≈0, 浮点近零)
-- r05    | 0.5                 | 1.830487721712452    (cot(0.5))
-- r06    | 1.0                 | 0.6420926159343306   (cot(1))
-- r07    | -0.5                | -1.830487721712452   (cot(-0.5)=-cot(0.5), 奇函数)
-- r08    | NULL                | NULL                 (NULL 传播)
--
-- 场景覆盖: π/4(=1) | π/6(=√3) | π/3(=1/√3) | π/2(近零) | 普通小数 | 负数(奇函数) | NULL 传播
-- =============================================================================
