-- =============================================================================
-- RAND_INTEGER(INT) / RAND_INTEGER(INT1, INT2) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml
--   RAND_INTEGER(INT)         返回 [0, INT) 伪随机整数
--   RAND_INTEGER(INT1, INT2)  返回 [0, INT2) 伪随机整数，INT1 为种子
-- 向量化: rand_integer({INT} | {INT, INT}) -> INT
--
-- 注: 随机函数非确定，native 用 std::mt19937 + seed+partitionId（非 Java LCG），输出不会与
--     Flink 逐位匹配。本测试聚焦「值域正确性」([0,bound)) 与「bound<=0/NULL → NULL」。
--     compare_native_vanilla.sh 会因随机值不同而报 DIFF —— 预期，需人工核对值域与 NULL。
--
-- 上传 CSV:
--   install_script/queries/csv_test/rand_integer/verify_expr_rand_integer.csv -> /opt/buildtools/install_script/queries/csv_test/rand_integer/verify_expr_rand_integer.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  seed   INT,
  bound  INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/rand_integer/verify_expr_rand_integer.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id     STRING,
  r_ri_b     INT,    -- RAND_INTEGER(bound)
  r_ri_sb    INT     -- RAND_INTEGER(seed, bound)
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  RAND_INTEGER(bound),
  RAND_INTEGER(seed, bound)
FROM src;

-- =============================================================================
-- 验证规则（非逐位，因 RNG 不同）:
--   - 非 NULL 值 ∈ [0, bound)
--   - bound=1 → 恒 0
--   - bound<=0 → NULL（native 设计决策：返回 NULL 而非抛异常）
--   - bound NULL → NULL；seed NULL → NULL
--
-- row_id | seed | bound | r_ri_b            | r_ri_sb
-- -------|------|-------|-------------------|-------------------
-- r01    | 1    | 1     | 0                 | 0
-- r02    | 42   | 10    | ∈[0,10)           | ∈[0,10)
-- r03    | 7    | 100   | ∈[0,100)          | ∈[0,100)
-- r04    | 0    | 0     | NULL              | NULL
-- r05    | 0    | -5    | NULL              | NULL
-- r06    | null | 10    | ∈[0,10)           | NULL
-- r07    | 42   | null  | NULL              | NULL
-- r08    | null | null  | NULL              | NULL
-- =============================================================================
