-- =============================================================================
-- ATAN2 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml — ATAN2(numeric1, numeric2) 返回坐标 (numeric1,
--       numeric2) 的反正切 (弧度), 值域 (-π, π]。约定 ATAN2(y, x) = Java Math.atan2(y, x):
--       第一参为 y(纵坐标), 第二参为 x(横坐标), 用两参符号定象限。
-- 向量化: atan2({DOUBLE, DOUBLE}) -> DOUBLE (RegisterMath.cpp, MathFunctions.h:
--   Atan2Function: result = std::atan2(a + 0.0, b + 0.0); a=第一参(y), b=第二参(x))。
--   两参顺序与 Flink/Java 一致, generic 路径按原序转发 operands, 无需重排。
--
-- 上传 CSV:
--   install_script/queries/csv_test/atan2/verify_expr_atan2.csv
--   -> /opt/buildtools/install_script/queries/csv_test/atan2/verify_expr_atan2.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1 + CSV 黄金对比)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  y      DOUBLE,
  x      DOUBLE
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/atan2/verify_expr_atan2.csv',
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
  CAST(ATAN2(y, x) AS DOUBLE)
FROM src;

-- =============================================================================
-- 期望输出 (按 row_id 对照, ATAN2(y,x) 值域 (-π,π], 弧度):
--
-- row_id | y    | x    | r (ATAN2(y,x))
-- -------|------|------|---------------------
-- r01    | 1.0  | 1.0  | 0.7853981633974483    (第一象限, =π/4)
-- r02    | 1.0  | -1.0 | 2.356194490192345     (第二象限, =3π/4)
-- r03    | -1.0 | -1.0 | -2.356194490192345    (第三象限, =-3π/4)
-- r04    | -1.0 | 1.0  | -0.7853981633974483   (第四象限, =-π/4)
-- r05    | 0.0  | 1.0  | 0.0                   (y=0, x>0 -> 0)
-- r06    | 1.0  | 0.0  | 1.5707963267948966    (y>0, x=0 -> π/2)
-- r07    | 0.0  | -1.0 | 3.141592653589793     (y=0, x<0 -> π, 注意值域含 π)
-- r08    | -1.0 | 0.0  | -1.5707963267948966   (y<0, x=0 -> -π/2)
-- r09    | 0.0  | 0.0  | 0.0                   (原点, atan2(0,0)=0)
-- r10    | NULL | 1.0  | NULL                  (y NULL -> NULL 传播)
-- r11    | 1.0  | NULL | NULL                  (x NULL -> NULL 传播)
--
-- 场景覆盖: 四象限(+,+)/(+,-)/(-,-)/(-,+) | 坐标轴(y=0/x>0, y>0/x=0, y=0/x<0, y<0/x=0) |
--           原点(0,0) | 任一参 NULL 传播
-- =============================================================================
