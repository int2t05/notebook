CREATE TABLE nexmark_qexpr (
  raw_channel VARCHAR,
  r_concat VARCHAR,
  r_concat_ws VARCHAR,
  r_substring VARCHAR,
  r_replace VARCHAR,
  r_md5 VARCHAR,
  r_instr INT,
  raw_price BIGINT,
  r_greatest BIGINT,
  r_least BIGINT,
  r_round DOUBLE,
  r_fromunix VARCHAR,
  r_unix_roundtrip BIGINT
) WITH (
  'connector' = 'blackhole'
);

INSERT INTO nexmark_qexpr
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
