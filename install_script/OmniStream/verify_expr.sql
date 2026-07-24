SET 'pipeline.operator-chaining' = 'false';

CREATE TABLE src (
  i INT,
  j INT,
  n INT,
  ts BIGINT
) WITH (
  'connector' = 'datagen',
  'fields.i.kind' = 'sequence', 'fields.i.start' = '5', 'fields.i.end' = '5',
  'fields.j.kind' = 'sequence', 'fields.j.start' = '-2', 'fields.j.end' = '-2',
  'fields.n.kind' = 'sequence', 'fields.n.start' = '12345', 'fields.n.end' = '12345',
  'fields.ts.kind' = 'sequence', 'fields.ts.start' = '1609459200', 'fields.ts.end' = '1609459200'
);

CREATE TABLE sink (
  r_round DOUBLE,
  r_greatest INT,
  r_least INT,
  r_concat STRING,
  r_concat_ws STRING,
  r_replace STRING,
  r_substring STRING,
  r_instr INT,
  r_md5 STRING,
  r_fromunix STRING,
  r_unix_roundtrip BIGINT
) WITH (
  'connector' = 'print'
);

INSERT INTO sink
SELECT
  ROUND(CAST(n AS DOUBLE) / 10000, 2),
  GREATEST(i, j),
  LEAST(i, j),
  CONCAT(CAST(n AS STRING), CAST(i AS STRING)),
  CONCAT_WS('-', CAST(n AS STRING), CAST(i AS STRING)),
  REPLACE(CAST(n AS STRING), '2', 'X'),
  SUBSTRING(CAST(n AS STRING), 1, 3),
  INSTR(CAST(n AS STRING), '34'),
  MD5(CAST(n AS STRING)),
  FROM_UNIXTIME(ts),
  UNIX_TIMESTAMP(FROM_UNIXTIME(ts))
FROM src;
