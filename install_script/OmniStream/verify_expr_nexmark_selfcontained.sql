-- Self-contained verification SQL for OmniStream vectorized expressions.
-- Uses the `nexmark` connector (supported by OmniStream's CreateSourceOp,
-- StreamOperatorFactory.cpp format == "nexmark") instead of `datagen`
-- (which OmniStream does NOT support).
--
-- Submit directly via sql-client (bypasses Nexmark run_query.sh / MetricReporter):
--   source /etc/profile
--   export FLINK_PERFORMANCE=false
--   export WRITE_TO_FILE=TRUE
--   > /tmp/flink_output.txt
--   /opt/flink/bin/sql-client.sh -f /tmp/verify_expr_nexmark_selfcontained.sql
--
-- Tune the data volume with 'events.num' below (10000 keeps the output small).

-- 1) Nexmark source (raw events table). connector = nexmark is what OmniStream offloads.
CREATE TABLE nexmark_source (
    event_type int,
    person ROW<
        id  BIGINT,
        name  VARCHAR,
        emailAddress  VARCHAR,
        creditCard  VARCHAR,
        city  VARCHAR,
        state  VARCHAR,
        `dateTime` TIMESTAMP(3),
        extra  VARCHAR>,
    auction ROW<
        id  BIGINT,
        itemName  VARCHAR,
        description  VARCHAR,
        initialBid  BIGINT,
        reserve  BIGINT,
        `dateTime`  TIMESTAMP(3),
        expires  TIMESTAMP(3),
        seller  BIGINT,
        category  BIGINT,
        extra  VARCHAR>,
    bid ROW<
        auction  BIGINT,
        bidder  BIGINT,
        price  BIGINT,
        channel  VARCHAR,
        url  VARCHAR,
        `dateTime`  TIMESTAMP(3),
        extra  VARCHAR>,
    `dateTime` AS
        CASE
            WHEN event_type = 0 THEN person.`dateTime`
            WHEN event_type = 1 THEN auction.`dateTime`
            ELSE bid.`dateTime`
        END,
    WATERMARK FOR `dateTime` AS `dateTime` - INTERVAL '4' SECOND
) WITH (
    'connector' = 'nexmark',
    'first-event.rate' = '1000000',
    'next-event.rate' = '1000000',
    'events.num' = '10000',
    'person.proportion' = '1',
    'auction.proportion' = '3',
    'bid.proportion' = '46'
);

-- 2) bid view (event_type = 2)
CREATE VIEW bid AS
SELECT
    bid.auction,
    bid.bidder,
    bid.price,
    bid.channel,
    bid.url,
    `dateTime`,
    bid.extra
FROM nexmark_source WHERE event_type = 2;

-- 3) print sink
CREATE TABLE sink (
  r_concat_ws      STRING,
  r_replace        STRING,
  r_instr          INT,
  r_md5            STRING,
  r_greatest       BIGINT,
  r_least          BIGINT,
  r_fromunix       STRING,
  r_unix_roundtrip BIGINT,
  r_substring      STRING,
  r_substr         STRING,
  r_concat         STRING
) WITH (
  'connector' = 'print'
);

-- 4) apply the adapted expressions
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
FROM bid;
