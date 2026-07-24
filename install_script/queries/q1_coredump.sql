CREATE TABLE nexmark_q1 (
  r_concat STRING
) WITH (
  'connector' = 'print'
);

INSERT INTO nexmark_q1
SELECT
    CONCAT(channel, channel, CAST(bidder AS STRING))
FROM bid;