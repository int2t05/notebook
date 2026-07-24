SET 'pipeline.operator-chaining' = 'false';

CREATE TABLE sink (
  r_concat STRING
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT CONCAT(CAST(n AS STRING), CAST(i AS STRING), CAST(n AS STRING))
FROM (VALUES (5, -2, 12345, CAST(1609459200 AS BIGINT))) AS T(i, j, n, ts);
