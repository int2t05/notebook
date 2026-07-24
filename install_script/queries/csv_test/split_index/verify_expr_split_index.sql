-- =============================================================================
-- SPLIT_INDEX 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       SPLIT_INDEX(string1, string2, integer1):
--       用 string2 分隔 string1, 返回第 integer1 个 (zero-based, 从 0 计数) 子串。
--       integer1 为负 -> NULL; 下标越界 -> NULL; 任一参数为 NULL -> NULL。
--
-- !! 实现说明 (重要) !!
--   OmniOperator 目前仅有 codegen 实现 "SplitIndex" (func_registry_string.cpp,
--   签名 {OMNI_VARCHAR, OMNI_CHAR, OMNI_INT})，没有向量化实现。
--   StreamCalcBatch 设了 preferVectorization=true，但 ExprVerifier 在发现某函数无
--   向量化实现时会令整批 isSupportVectorization=false，从而整批回退到 codegen 执行
--   (useCodegen = !(prefer && supportVec) && supportCodegen)。
--   因此本用例必须保证整条 SQL 的所有表达式都能 codegen (此处仅 SPLIT_INDEX),
--   否则若与“仅支持向量化”的表达式混用, 会强制走向量化并报
--   "Vector function not found for function: SplitIndex"。
--   另: 分隔符需为 CHAR 字面量 (如 '|'), 才能匹配 codegen 的 {VARCHAR, CHAR, INT} 签名。
--
-- 注意 CSV 以逗号分隔, 故被切分串内统一用 '|' 作分隔符, 避免与 CSV 列冲突。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/split_index/verify_expr_split_index.csv -> /tmp/verify_expr_split_index.csv
--
-- 对比流程 (见 .cursor/skills/omniadaptor-vectorized-expression/SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_split_index.sql
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING,
  idx    INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/split_index/verify_expr_split_index.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,   -- 行标签, 便于 diff 对照
  r      STRING    -- SPLIT_INDEX(s, '|', idx)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  SPLIT_INDEX(s, '|', idx)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r], 按 row_id 对照):
--
-- row_id | s                       | idx | r
-- -------|-------------------------|-----|----------
-- r01    | a|b|c                   | 0   | a         (zero-based 第 0 个)
-- r02    | a|b|c                   | 1   | b
-- r03    | a|b|c                   | 2   | c         (最后一个)
-- r04    | a|b|c                   | 3   | NULL      (下标越界)
-- r05    | a|b|c                   | -1  | NULL      (负下标)
-- r06    | hello|world             | 1   | world
-- r07    | single                  | 0   | single    (无分隔符, 下标 0 取整串)
-- r08    | single                  | 1   | NULL      (无分隔符, 下标 1 越界)
-- r09    | NULL                    | 0   | NULL      (输入串 NULL)
-- r10    | x||z                    | 1   | (空串)     (相邻分隔符产生空子串)
-- r11    | x||z                    | 0   | x
-- r12    | 2026-06-25|q22|nexmark  | 2   | nexmark
--
-- 场景覆盖:
--   正常下标 0/中/末 | 下标越界 | 负下标 | 无分隔符 | 输入 NULL | 空子串 | 多字符子串
-- =============================================================================
