-- =============================================================================
-- ASIN 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — ASIN(numeric) 返回反正弦 (弧度), 定义域 [-1,1]。
-- 向量化: asin({DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h: std::asin)。
--   越界入参(如 2.0) std::asin 返回 NaN -> 结果 NaN。
--
-- 上传 CSV:
--   install_script/queries/csv_test/asin/verify_expr_asin.csv
--   -> /opt/buildtools/install_script/queries/csv_test/asin/verify_expr_asin.csv
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
  'path' = '/opt/buildtools/install_script/queries/csv_test/asin/verify_expr_asin.csv',
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
  CAST(ASIN(x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, 定义域 [-1,1], 返回弧度):
--
-- row_id | x                   | r (ASIN)
-- -------|---------------------|---------------------
-- r01    | 0.0                 | 0.0                   (asin(0)=0)
-- r02    | 1.0                 | 1.5707963267948966    (asin(1)=π/2, 域上界)
-- r03    | -1.0                | -1.5707963267948966   (asin(-1)=-π/2, 域下界, 奇函数)
-- r04    | 0.5                 | 0.5235987755982989    (asin(0.5)=π/6)
-- r05    | -0.5                | -0.5235987755982989   (asin(-0.5)=-π/6, 奇函数)
-- r06    | 0.8660254037844386  | 1.0471975511965976    (asin(√3/2)=π/3)
-- r07    | 2.0                 | NaN                   (越界, std::asin 返回 NaN)
-- r08    | -2.0                | NaN                   (越界, std::asin 返回 NaN)
-- r09    | NULL                | NULL                  (NULL 传播)
--
-- 场景覆盖: 0 | 域上界(1) | 域下界(-1, 奇函数) | 域内正/负值 | √3/2(π/3) |
--           越界(2.0,-2.0 -> NaN) | NULL 传播
-- =============================================================================
