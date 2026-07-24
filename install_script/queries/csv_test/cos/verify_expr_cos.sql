-- =============================================================================
-- COS 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — COS(numeric) 返回余弦 (入参为弧度)。
-- 向量化: cos({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::cos)。
--
-- 上传 CSV:
--   install_script/queries/csv_test/cos/verify_expr_cos.csv
--   -> /opt/buildtools/install_script/queries/csv_test/cos/verify_expr_cos.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/cos/verify_expr_cos.csv',
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
  CAST(COS(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 入参为弧度):
--
-- row_id | x        | r (COS)
-- -------|----------|---------------------
-- r01    | 0.0      | 1.0                   (cos(0)=1)
-- r02    | 1.0471975511965976 | 0.5000000000000001  (cos(π/3)≈0.5)
-- r03    | 0.7853981633974483 | 0.7071067811865476  (cos(π/4)≈√2/2)
-- r04    | 3.141592653589793  | -1.0                (cos(π)=-1)
-- r05    | 1.5707963267948966 | 6.123233995736766E-17 (cos(π/2)≈0, 浮点近零)
-- r06    | -1.0     | 0.5403023058681398    (cos(-1)=cos(1), 偶函数)
-- r07    | NULL     | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | π/3(=0.5) | π/4(=√2/2) | π(=-1) | π/2(近零) | 负数(偶函数) | NULL 传播
-- =============================================================================
