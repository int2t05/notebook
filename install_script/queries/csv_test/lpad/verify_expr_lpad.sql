-- =============================================================================
-- LPAD 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       LPAD(string1, integer, string2):
--       用 string2 在左侧填充 string1 到 integer 字符长;
--       若 string1 长于 integer, 则把 string1 截断到 integer 字符长(取前 integer 字符)。
--       例: LPAD('hi', 4, '??') -> "??hi"; LPAD('hi', 1, '??') -> "h"。
--       yaml 未文档化 NULL/负数/0 边界, 以下期望以 OmniOperator 向量化实现为准。
--
-- !! 实现说明 (重要) !!
--   OmniOperator 已有向量化实现 (functions/String.h, PadFunctionBase<true,T> =
--   LPadFunction), 注册名 "lpad" (registration/RegisterString.cpp), 8 个重载:
--   入参 {VARCHAR/CHAR, INT/LONG, VARCHAR/CHAR} -> VARCHAR。本函数走向量化执行。
--
--   native 边界语义 (PadFunctionBase::call):
--     * size < 0            -> 空串 (非 NULL)
--     * size > 1MB          -> 空串 (非 NULL)
--     * padString 为空      -> 空串 (非 NULL)
--     * 原串字符数 >= size  -> 截断原串到前 size 个 Unicode 字符
--     * 原串字符数 <  size  -> 左侧用 padString 循环填充到 size 字符
--     * 任一入参 NULL       -> 整行 NULL (callNullable 返回 false)
--   注意: size 按 Unicode 码点计数 (非字节), 支持多字节字符 (如中文)。
--
-- 注意 CSV 以逗号分隔, 故字符串列内不含逗号; null 字面量表示 NULL。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/lpad/verify_expr_lpad.csv
--   -> /opt/buildtools/install_script/queries/csv_test/lpad/verify_expr_lpad.csv
--
-- 对比流程 (见 skills/omniadaptor-vectorized-expression SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_lpad.sql
--   # 确认走 native:
--   tail -n 50 $FLINK_HOME/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
--   # 原生 Flink 基准:
--   cp $FLINK_HOME/bin/config.sh.orig $FLINK_HOME/bin/config.sh   # 切回原生
--   stop-cluster.sh; start-cluster.sh
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_lpad.sql
--   grep -E '^\+I' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
--   # 归一化 diff:
--   bash install_script/queries/csv_test/compare_native_vanilla.sh
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING,
  len    INT,
  pad    STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/lpad/verify_expr_lpad.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,   -- 行标签, 便于 diff 对照
  r      STRING    -- LPAD(s, len, pad)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  LPAD(s, len, pad)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r], 按 row_id 对照):
--
-- row_id | s      | len | pad | r
-- -------|--------|-----|-----|----------
-- r01    | hi     | 4   | ??  | ??hi        (正常左填充)
-- r02    | hello  | 2   | ??  | he          (原串长于 len, 截断前缀)
-- r03    | hi     | 0   | ??  | (空串)       (size=0 -> 空串)
-- r04    | hi     | -1  | ??  | (空串)       (size 负数 -> 空串)
-- r05    | ab     | 5   | xyz | xyzab       (多字符 pad, 不完整取前缀)
-- r06    | ab     | 5   | #   | ###ab       (单字符 pad 循环)
-- r07    | abc    | 3   | ?   | abc         (原串长度恰等于 len, 不填充)
-- r08    | 你好   | 4   | ab  | ab你好      (Unicode 按字符计数, 非 4 字节)
-- r09    | (空串) | 3   | ?   | ???         (空原串, 全填充)
-- r10    | NULL   | 3   | ?   | NULL        (s 为 NULL -> 整行 NULL)
-- r11    | abc    | NULL| ?   | NULL        (len 为 NULL -> 整行 NULL)
-- r12    | abc    | 3   | NULL| NULL        (pad 为 NULL -> 整行 NULL)
--
-- 场景覆盖:
--   正常填充 | 截断 | size=0 | size 负数 | 多字符/单字符 pad | 原串恰等于 len |
--   Unicode 多字节 | 空原串 | 三参任一为 NULL
-- =============================================================================
