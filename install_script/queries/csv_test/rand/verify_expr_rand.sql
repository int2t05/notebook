-- =============================================================================
-- RAND() / RAND(INT) 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml
--   RAND()        返回 [0.0, 1.0) 伪随机 DOUBLE，无种子
--   RAND(INT)     返回 [0.0, 1.0) 伪随机 DOUBLE，带初始种子 INT
-- 向量化: rand({} | {INT} | {LONG}) -> DOUBLE
--
-- 注: 随机函数非确定，native 用 std::mt19937（非 Java LCG），输出不会与 Flink 逐位匹配。
--     本测试聚焦「值域正确性」([0,1)) 与「seeded 可复现性」(native 内部一致)，不逐位对比。
--     compare_native_vanilla.sh 会因随机值不同而报 DIFF —— 这是预期的，需人工核对值域。
--
-- 上传 CSV:
--   install_script/queries/csv_test/rand/verify_expr_rand.csv -> /opt/buildtools/install_script/queries/csv_test/rand/verify_expr_rand.csv
--
-- 用法同 verify_expr_quarter.sql (UTC + parallelism=1)
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  seed   INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/rand/verify_expr_rand.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id    STRING,
  r_rand    DOUBLE,    -- RAND()
  r_rand_s  DOUBLE     -- RAND(seed)
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT
  row_id,
  RAND(),
  RAND(seed)
FROM src;

-- =============================================================================
-- 验证规则（非逐位，因 RNG 不同）:
--   - 所有非 NULL 值 ∈ [0.0, 1.0)
--   - seed NULL 时 RAND(NULL) → NULL（Flink 经 generateCallIfArgsNotNull 短路）
--   - seeded 同种子 native 内部可复现（跨引擎不要求）
--
-- row_id | seed | r_rand(∈[0,1)) | r_rand_s(∈[0,1) 或 NULL)
-- -------|------|----------------|--------------------------
-- r01    | 1    | ∈[0,1)         | ∈[0,1)
-- r02    | 42   | ∈[0,1)         | ∈[0,1)
-- r03    | 100  | ∈[0,1)         | ∈[0,1)
-- r04    | 0    | ∈[0,1)         | ∈[0,1)
-- r05    | null | ∈[0,1)         | NULL
-- =============================================================================
