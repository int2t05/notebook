-- =============================================================================
-- OVERLAY 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       OVERLAY(string1 PLACING string2 FROM integer1 [ FOR integer2 ])
--       用 string2 替换 string1 中从 integer1 (1-based) 开始的 integer2 个字符
--       (integer2 默认 = string2 的长度)。
--       例: OVERLAY('xxxxxtest' PLACING 'xxxx' FROM 6)      -> "xxxxxxxxx"
--           OVERLAY('xxxxxtest' PLACING 'xxxx' FROM 6 FOR 2) -> "xxxxxxxxxst"
--
-- !! 实现说明 (重要) !!
--   OmniOperator 已有向量化实现 (functions/String.h, OverlayFunction), 注册名 "overlay"
--   (registration/RegisterString.cpp), 1 个重载:
--   入参 {VARCHAR, VARCHAR, INT, INT} -> VARCHAR (仅 4 参数重载)。
--   本函数走向量化执行。
--
--   native 边界语义 (OverlayFunction::call):
--     * pos: 1-based; pos>0 时 startChar0 = min(pos-1, numChars)
--     * len >= 0: 替换 len 个字符; len < 0: 用 replace 的字符长度 (等价 Flink 省略 FOR)
--     * 按 Unicode 码点计数 (非字节), 支持多字节字符 (如中文)
--     * 任一入参 NULL -> 整行 NULL (框架传播)
--     * 结果 = input[0..pos-1) + replace + input[pos+len..end)  (1-based 字符)
--
--   !! 语义对齐注意 !!
--   本测试仅覆盖 native 与 Flink 行为【一致】的场景 (pos 在 [1, numChars] 内、len > 0
--   或省略 FOR)。以下场景两者行为不同, 故【不】纳入黄金对比, 避免误报 DIFF:
--     - pos > numChars: Flink 返回原串; native 追加 replace (结果不同)
--     - pos <= 0:       Flink 返回原串; native 让 part1 为空后拼接 (结果不同)
--     - len = 0:        Flink 丢弃 part3 (插入但不保留后续); native 保留 part3 (结果不同)
--   这些差异源于 Flink SqlFunctionUtils.overlay 的特殊分支, 若需覆盖需单独评估。
--
-- 注意 CSV 以逗号分隔, 故字符串列内不含逗号; null 字面量表示 NULL。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/overlay/verify_expr_overlay.csv
--   -> /opt/buildtools/install_script/queries/csv_test/overlay/verify_expr_overlay.csv
--
-- 对比流程 (见 skills/omniadaptor-vectorized-expression SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_overlay.sql
--   # 确认走 native:
--   tail -n 50 $FLINK_HOME/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
--   # 原生 Flink 基准:
--   cp $FLINK_HOME/bin/config.sh.orig $FLINK_HOME/bin/config.sh   # 切回原生
--   stop-cluster.sh; start-cluster.sh
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_overlay.sql
--   grep -E '^\+I' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
--   # 归一化 diff:
--   bash install_script/queries/csv_test/compare_native_vanilla.sh
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id  STRING,
  s       STRING,
  r       STRING,
  pos     INT,
  len     INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/overlay/verify_expr_overlay.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  r4     STRING,   -- OVERLAY(s PLACING r FROM pos FOR len)        (4-arg)
  r3     STRING    -- OVERLAY(s PLACING r FROM pos)                (3-arg, len 默认 = r 长度)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  OVERLAY(s PLACING r FROM pos FOR len),
  OVERLAY(s PLACING r FROM pos)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r4, r3], 按 row_id 对照):
--
-- 4-arg (r4) = OVERLAY(s PLACING r FROM pos FOR len)
-- 3-arg (r3) = OVERLAY(s PLACING r FROM pos)  -- len 默认 = CHAR_LENGTH(r)
--
-- row_id | s          | r    | pos | len | r4              | r3
-- -------|------------|------|-----|-----|-----------------|----------------
-- o01    | xxxxxtest  | xxxx | 6   | 2   | xxxxxxxxxst     | xxxxxxxxx        (替换2/默认4)
-- o02    | abcdef     | XY   | 1   | 2   | XYcdef          | XYcdef           (从头替换)
-- o03    | abcdef     | XY   | 3   | 2   | abXYef          | abXYef           (中间替换)
-- o04    | abcdef     | XYZW | 5   | 2   | abcdXYZW        | abcdXYZW         (末尾替换, part3空)
-- o05    | hello      | ***  | 2   | 3   | h***o           | h***o            (ell->***)
-- o06    | 你好世界   | XX   | 2   | 1   | 你XX世界        | 你XX界           (Unicode 按字符)
-- o07    | abcdef     | XY   | 6   | 1   | abcdeXY         | abcdeXY          (pos=末字符)
-- o08    | abcdef     | XYZW | 3   | 4   | abXYZW          | abXYZW           (len=剩余长度)
-- o09    | NULL       | XY   | 1   | 1   | NULL            | NULL             (s 为 NULL)
-- o10    | abcdef     | NULL | 1   | 1   | NULL            | NULL             (r 为 NULL)
-- o11    | abcdef     | XY   | NULL| 1   | NULL            | NULL             (pos 为 NULL)
-- o12    | abcdef     | XY   | 1   | NULL| NULL            | NULL             (len 为 NULL)
--
-- 场景覆盖:
--   4-arg 替换 | 3-arg 省略 FOR (默认 len=r 长度) | 从头替换 | 中间替换 | 末尾替换(part3空) |
--   Unicode 按字符计数 | pos=末字符 | len=剩余长度 | 四参任一为 NULL
--   注: pos 均在 [1, numChars] 内, len > 0, 确保 native 与 Flink 行为一致。
-- =============================================================================
