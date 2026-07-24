SET 'pipeline.operator-chaining' = 'false';
CREATE TABLE bid (
  auction  BIGINT,
  bidder   BIGINT,
  price    BIGINT,
  channel  STRING,
  url      STRING,
  `dateTime` TIMESTAMP(3),
  extra    STRING
) WITH (
  'connector' = 'datagen',
  'number-of-rows' = '10',
  'fields.auction.kind' = 'sequence', 'fields.auction.start' = '1001', 'fields.auction.end' = '1010',
  'fields.bidder.kind'  = 'sequence', 'fields.bidder.start'  = '1609459200', 'fields.bidder.end'  = '1609459209',
  'fields.price.kind'   = 'sequence', 'fields.price.start'   = '100', 'fields.price.end'   = '109'
);

CREATE TABLE sink (
  r_concat_ws      STRING,   -- CONCAT_WS('-', str1, str2)
  r_replace        STRING,   -- REPLACE(str1, str2, 'X')
  r_instr          INT,      -- INSTR(str1, str2)
  r_md5            STRING,   -- MD5(str1)
  r_greatest       BIGINT,   -- GREATEST(x, y)
  r_least          BIGINT,   -- LEAST(x, y)
  r_fromunix       STRING,   -- FROM_UNIXTIME(ts)
  r_unix_roundtrip BIGINT,    -- UNIX_TIMESTAMP(FROM_UNIXTIME(ts))
  r_concat         STRING   -- CONCAT(str1, str2)
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
  CONCAT(CAST(auction AS STRING), CAST(bidder AS STRING))
FROM bid;

