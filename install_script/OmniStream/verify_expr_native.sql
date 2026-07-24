CREATE TABLE nexmark_src (
  event_type int,
  person ROW<id BIGINT, name VARCHAR, emailAddress VARCHAR, creditCard VARCHAR, city VARCHAR, state VARCHAR, `dateTime` TIMESTAMP(3), extra VARCHAR>,
  auction ROW<id BIGINT, itemName VARCHAR, description VARCHAR, initialBid BIGINT, reserve BIGINT, `dateTime` TIMESTAMP(3), expires TIMESTAMP(3), seller BIGINT, category BIGINT, extra VARCHAR>,
  bid ROW<auction BIGINT, bidder BIGINT, price BIGINT, channel VARCHAR, url VARCHAR, `dateTime` TIMESTAMP(3), extra VARCHAR>,
  `dateTime` AS CASE WHEN event_type = 0 THEN person.`dateTime` WHEN event_type = 1 THEN auction.`dateTime` ELSE bid.`dateTime` END,
  WATERMARK FOR `dateTime` AS `dateTime` - INTERVAL '4' SECOND
) WITH (
  'connector' = 'nexmark',
  'first-event.rate' = '1000',
  'next-event.rate' = '1000',
  'events.num' = '2000',
  'person.proportion' = '1',
  'auction.proportion' = '1',
  'bid.proportion' = '20'
);

CREATE VIEW bid AS
SELECT bid.auction, bid.bidder, bid.price, bid.channel, bid.url, `dateTime`, bid.extra
FROM nexmark_src WHERE event_type = 2;

CREATE TABLE sink (
  raw_channel STRING,
  r_concat STRING,
  r_concat_ws STRING,
  r_substring STRING,
  r_replace STRING,
  r_md5 STRING,
  r_instr INT,
  raw_price BIGINT,
  r_greatest BIGINT,
  r_least BIGINT,
  r_round DOUBLE,
  r_fromunix STRING,
  r_unix_roundtrip BIGINT
) WITH (
  'connector' = 'blackhole'
);

INSERT INTO sink
SELECT
  channel,
  CONCAT(channel, channel),
  CONCAT_WS('-', channel, channel),
  SUBSTRING(channel, 1, 3),
  REPLACE(channel, 'a', 'a'),
  MD5(channel),
  INSTR(channel, channel),
  price,
  GREATEST(price, bidder),
  LEAST(price, bidder),
  ROUND(CAST(price AS DOUBLE), 2),
  FROM_UNIXTIME(price),
  UNIX_TIMESTAMP(FROM_UNIXTIME(price))
FROM bid;
