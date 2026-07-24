-- =============================================================================
-- REGEXP_EXTRACT 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       REGEXP_EXTRACT(string1, string2[, integer]):
--       用正则 string2 从 string1 中提取, integer 为分组索引。
--       分组索引从 1 开始, 0 表示匹配整个正则; 不应超过已定义分组数。
--       第 3 参数可选, 省略时默认 group index = 0 (匹配整个正则)。
--       例: REGEXP_EXTRACT('foothebar', 'foo(.*?)(bar)', 2) -> "bar"。
--
-- !! 实现说明 (重要) !!
--   OmniOperator 向量化实现: functions/RegexpExtract.{h,cpp} (RegexpExtractFunction, 基于 re2),
--   注册名 "regexp_extract" (registration/RegisterString.cpp),
--   签名 {OMNI_VARCHAR, OMNI_VARCHAR, OMNI_INT} -> OMNI_VARCHAR。
--   RexNodeUtil buildJsonMap 的 REGEXP_EXTRACT 分支已对齐此向量化注册名,
--   并支持可选第 3 参数 (省略时补 group index=0 字面量)。
--
--   native 边界语义 (RegexpExtract.cpp, re2 实现):
--     * group index = 0   -> 匹配整个正则 (groups[0])
--     * group index 越界  -> 空串 (非 NULL)
--     * 无匹配            -> 空串 (非 NULL)
--     * 任一入参 NULL     -> 整行 NULL (str 或 pattern 为 NULL)
--     * 空 pattern        -> 抛异常 (patternStr must not empty)
--   注意: 与旧 codegen "regex_extract_null" (wregex) 不同 — 旧实现无匹配返回 NULL,
--         向量化 re2 实现无匹配返回空串。本测试以向量化 re2 语义为期望。
--
-- 注意 CSV 以逗号分隔, 故字符串列内不含逗号; null 字面量表示 NULL。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/regexp_extract/verify_expr_regexp_extract.csv
--   -> /opt/buildtools/install_script/queries/csv_test/regexp_extract/verify_expr_regexp_extract.csv
--
-- 对比流程 (见 skills/omniadaptor-vectorized-expression SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_regexp_extract.sql
--   # 确认走 native:
--   tail -n 50 $FLINK_HOME/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
--   # 原生 Flink 基准:
--   cp $FLINK_HOME/bin/config.sh.orig $FLINK_HOME/bin/config.sh   # 切回原生
--   stop-cluster.sh; start-cluster.sh
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_regexp_extract.sql
--   grep -E '^\+I' $FLINK_HOME/log/flink-root-taskexecutor-*.out > /tmp/vanilla_out.txt
--   # 归一化 diff:
--   bash install_script/queries/csv_test/compare_native_vanilla.sh
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  s      STRING,
  p      STRING,
  g      INT
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/regexp_extract/verify_expr_regexp_extract.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,
  -- 3 参数调用: REGEXP_EXTRACT(s, p, g)  覆盖正常/越界/无匹配/NULL/group0
  r3     STRING,
  -- 2 参数调用: REGEXP_EXTRACT(s, p)  省略 group index, 默认 0 (匹配整个正则)
  r2     STRING
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  REGEXP_EXTRACT(s, p, g),
  REGEXP_EXTRACT(s, p)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r3, r2], 按 row_id 对照):
--   向量化 re2 语义: 无匹配/越界 -> 空串; NULL -> NULL; group0 -> 整个正则匹配
--
-- row_id | s          | p            | g  | r3 (3参)    | r2 (2参,默认g=0)
-- -------|------------|--------------|----|-------------|------------------
-- r01    | foothebar  | foo(.*?)(bar)| 2  | bar         | foothebar        (g=2取第2组; g=0整个正则)
-- r02    | foothebar  | foo(.*?)(bar)| 1  | the         | foothebar        (g=1取第1组)
-- r03    | foothebar  | foo(.*?)(bar)| 0  | foothebar   | foothebar        (g=0整个正则)
-- r04    | foothebar  | foo(.*?)(bar)| 3  | (空串)       | foothebar        (g越界,只有2组->空串)
-- r05    | noMatchHere| foo(.*?)(bar)| 1  | (空串)       | (空串)            (无匹配->空串)
-- r06    | abc123def  | ([0-9]+)     | 1  | 123         | abc123def        (数字提取, g=1组)
-- r07    | hello.world| ([^.]+)      | 1  | hello       | hello.world      (取第一个非点串)
-- r08    | NULL       | foo(.*?)(bar)| 1  | NULL        | NULL             (s为NULL->整行NULL)
-- r09    | foothebar  | NULL         | 1  | NULL        | NULL             (p为NULL->整行NULL)
-- r10    | NULL       | NULL         | 1  | NULL        | NULL             (s,p均NULL->NULL)
-- r11    | foothebar  | foo(.*?)(bar)| -1 | (未定义)     | foothebar        (g负数,native未显式校验,行为未定义)
--
-- 场景覆盖:
--   3参数正常(g=1/2) | g=0整个正则 | g越界->空串 | 无匹配->空串 | 数字提取 | 点分隔提取 |
--   s NULL | p NULL | s,p均NULL | g负数(边界,期望以native为准,可能空串或异常) |
--   2参数省略g(默认0) 各场景与3参数g=0对照
--
-- 注意:
--   - r11 (g=-1) native re2 实现未显式校验负数, 行为未定义。
--     原生 Flink (JVM) 对 g=-1 的处理也可能不同。
--     若对比时 r11 不一致, 可从 CSV 中移除该行后单独评估。
--   - 空 pattern 在 native 会抛异常, 故未放入 CSV (避免任务失败)。
-- =============================================================================
