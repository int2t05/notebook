-- =============================================================================
-- FROM_BASE64 向量化表达式 — CSV 黄金对比 SQL
-- 语义: flink/docs/data/sql_functions.yml —
--       FROM_BASE64(string): 返回 string 的 base64 解码结果; string 为 NULL 时返回 NULL。
--       例: FROM_BASE64('aGVsbG8gd29ybGQ=') -> 'hello world'。返回类型 STRING(VARCHAR)。
--
-- !! 实现说明 (重要, 见报告) !!
--   OmniOperator 向量化 unbase64 注册为 {OMNI_VARCHAR} -> OMNI_VARBINARY,
--   返回类型是 VARBINARY 而非 Flink 期望的 VARCHAR; 且:
--     - VectorFunction::Find 按 (name + 入参 + 返回类型) 精确匹配, 返回类型必须一致;
--     - VARBINARY 输出无 RowData 序列化器 (marshaller 数组无该项), 无法落到 sink;
--     - 无 codegen unbase64, 无向量化 CAST(VARBINARY->VARCHAR)。
--   因此本表达式需要在 OmniOperator 侧补一个返回 VARCHAR 的 unbase64 重载
--   (或新增 VARBINARY->VARCHAR 向量化 CAST + VARBINARY marshaller) 后才能跑通,
--   属于需用户确认的 C++ 改动。本 SQL 先按 FROM_BASE64 最终语义(返回 STRING)编写。
--
-- 上传 CSV 到服务器:
--   install_script/queries/csv_test/from_base64/verify_expr_from_base64.csv -> /tmp/verify_expr_from_base64.csv
--
-- 对比流程 (见 .cursor/skills/omniadaptor-vectorized-expression/SKILL.md 步骤 5):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   $FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr_from_base64.sql
-- =============================================================================

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

CREATE TABLE src (
  row_id STRING,
  b64    STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/from_base64/verify_expr_from_base64.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  row_id STRING,   -- 行标签, 便于 diff 对照
  r      STRING    -- FROM_BASE64(b64)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  row_id,
  FROM_BASE64(b64)
FROM src;

-- =============================================================================
-- 期望输出 (print sink 形如 +I[row_id, r], 按 row_id 对照):
--
-- row_id | b64                  | r
-- -------|----------------------|---------------
-- r01    | aGVsbG8gd29ybGQ=     | hello world    (经典示例)
-- r02    | YQ==                 | a              (1 字节, 双 padding)
-- r03    | YWI=                 | ab             (2 字节, 单 padding)
-- r04    | YWJj                 | abc            (3 字节, 无 padding)
-- r05    | (空串)               | (空串)          (空输入 -> 空串)
-- r06    | NULL                 | NULL           (NULL 透传)
-- r07    | aGVsbG8=             | hello
-- r08    | MTIzNDU2Nzg5MA==     | 1234567890     (纯数字串)
--
-- 场景覆盖:
--   经典示例 | 1/2/3 字节 padding 变体 | 空串 | NULL | 数字串
-- 说明: 非法 base64 输入在 Flink 与 OmniOperator 下行为可能不同(报错/NULL),
--       为保证黄金对比逐行一致, 本用例仅覆盖合法输入。
-- =============================================================================
