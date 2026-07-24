-- =============================================================================
-- REPEAT 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       REPEAT(string, int):
--       返回 base string 重复 int 次的串。
--       例: REPEAT('This is a test String.', 2) -> "This is a test String.This is a test String."
--       yaml 未文档化 NULL/负数/0 边界, 以下期望以 OmniOperator 向量化实现为准。
--
-- !! 实现说明 (重要) !!
--   OmniOperator 已有向量化实现 (functions/String.h, RepeatFunction), 注册名 "repeat"
--   (registration/RegisterString.cpp), 4 个重载:
--   入参 {VARCHAR/CHAR, INT/LONG} -> VARCHAR。本函数走向量化执行。
--
--   native 边界语义 (RepeatFunction::call):
--     * n <= 0           -> 空串 (非 NULL)
--     * 原串为空串       -> 空串 (非 NULL)
--     * n 为正           -> 原串按字节 memcpy n 次 (不做 Unicode 解码)
--     * 结果 > 1MB / 溢出 -> 空串 (非 NULL; 注释虽称 error/NULL, 实现为空串)
--     * 任一入参 NULL    -> 整行 NULL (callNullable 返回 false)
--   注意: repeat 按【字节】重复, 多字节字符 (如中文) 仍原样重复整串, 无需字符解码。
--
-- 注意 CSV 以逗号分隔, 故字符串列内不含逗号; null 字面量表示 NULL。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/repeat/verify_expr_repeat.csv
--   -> /opt/buildtools/install_script/queries/csv_test/repeat/verify_expr_repeat.csv
--
-- 对比流程 (见 skills/omniadaptor-vectorized-expression SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_repeat.sql
--   # 确认走 native:
--   tail -n 50 $FLINK_HOME/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
--   # 原生 Flink 基准:
--   cp $FLINK_HOME/bin/config.sh.orig $FLINK_HOME/bin/config.sh   # 切回原生
--   stop-cluster.sh; start-cluster.sh
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_repeat.sql
--   grep -E '^\+I' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
--   # 归一化 diff:
--   bash install_script/queries/csv_test/compare_native_vanilla.sh
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING,
  n      INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/repeat/verify_expr_repeat.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,   -- 行标签, 便于 diff 对照
  r      STRING    -- REPEAT(s, n)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  REPEAT(s, n)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r], 按 row_id 对照):
--
-- row_id | s        | n   | r
-- -------|----------|-----|------------------
-- r01    | ab       | 3   | ababab           (正常重复)
-- r02    | ab       | 0   | (空串)            (n=0 -> 空串)
-- r03    | ab       | -1  | (空串)            (n 负数 -> 空串)
-- r04    | abc      | 1   | abc              (n=1 原样返回)
-- r05    | (空串)   | 5   | (空串)            (空原串 -> 空串)
-- r06    | NULL     | 3   | NULL             (s 为 NULL -> 整行 NULL)
-- r07    | abc      | NULL| NULL             (n 为 NULL -> 整行 NULL)
-- r08    | 你好     | 2   | 你好你好         (多字节按字节重复整串)
--
-- 场景覆盖:
--   正常重复 | n=0 | n 负数 | n=1 | 空原串 | s 为 NULL | n 为 NULL | 多字节
-- =============================================================================
