-- Golden-comparison SQL for OmniStream vectorized expressions.
-- Reads a FIXED CSV file so OmniStream (native) and vanilla Flink consume the
-- exact same bytes -> outputs can be diffed directly.
--
-- Source connector = filesystem + format=csv, which OmniStream offloads via
-- CreateSourceOp (StreamOperatorFactory.cpp, format == "csv"). NOT datagen.
--
-- Upload the CSV first (same path on the server):
--   /tmp/verify_expr_fixed.csv
--
-- Run on NATIVE (OmniStream) cluster:
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   /opt/flink/bin/sql-client.sh -f /tmp/verify_expr_csv_selfcontained.sql
--   # results in /tmp/flink_output.txt
--
-- Run on VANILLA Flink (clean cluster, OmniStream NOT enabled):
--   /opt/flink/bin/sql-client.sh -f /tmp/verify_expr_csv_selfcontained.sql
--   # results printed to TaskManager .out log
--
-- parallelism=1 keeps output row order stable for diffing.
-- local-time-zone fixed so FROM_UNIXTIME / UNIX_TIMESTAMP are deterministic.

SET 'parallelism.default' = '1';
SET 'table.local-time-zone' = 'UTC';

-- Fixed-input source. Columns map by position to the CSV file.
CREATE TABLE src (
  auction BIGINT,
  bidder  BIGINT,
  price   BIGINT,
  channel STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '/opt/buildtools/install_script/queries/csv_test/mixed/verify_expr_fixed.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'
);

CREATE TABLE sink (
  r_concat_ws      STRING,   -- CONCAT_WS('-', auction, bidder)
  r_replace        STRING,   -- REPLACE(auction, bidder, 'X')
  r_instr          INT,      -- INSTR(auction, bidder)
  r_md5            STRING,   -- MD5(auction)
  r_greatest       BIGINT,   -- GREATEST(price, auction)
  r_least          BIGINT,   -- LEAST(price, auction)
  r_fromunix       STRING,   -- FROM_UNIXTIME(bidder)
  r_unix_roundtrip BIGINT,   -- UNIX_TIMESTAMP(FROM_UNIXTIME(bidder))
  r_substring      STRING,   -- SUBSTRING(channel FROM 1 FOR 3)
  r_substr         STRING,   -- SUBSTR(channel, 2, 3)
  r_concat         STRING    -- CONCAT(auction, bidder)
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  CONCAT_WS('-', CAST(auction AS STRING), CAST(bidder AS STRING)),
  REPLACE(CAST(auction AS STRING), CAST(bidder AS STRING), 'X'),
  INSTR(CAST(auction AS STRING), CAST(bidder AS STRING)),
  CAST(MD5(CAST(auction AS STRING)) AS STRING),
  GREATEST(price, auction),
  LEAST(price, auction),
  FROM_UNIXTIME(bidder),
  UNIX_TIMESTAMP(FROM_UNIXTIME(bidder)),
  SUBSTRING(channel FROM 1 FOR 3),
  SUBSTR(channel, 2, 3),
  CONCAT(CAST(auction AS STRING), CAST(bidder AS STRING))
FROM src;
