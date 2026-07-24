# 数据类型和表结构参考

## 19种数据类型

| 列名 | Spark数据类型 | 表列名 | 说明 |
|------|-------------|--------|------|
| BOOLEAN | BOOLEAN | c_bool | 布尔型 |
| BYTE | TINYINT | c_byte | 字节类型 |
| SHORT | SMALLINT | c_short | 短整型 |
| INT | INT | c_int | 整型 |
| LONG | BIGINT | c_long | 长整型 |
| FLOAT | FLOAT | c_float | 单精度浮点 |
| DOUBLE | DOUBLE | c_double | 双精度浮点 |
| STRING | STRING | c_string | 字符串 |
| CHAR | CHAR(40) | c_char | 定长字符串 |
| VARCHAR | VARCHAR(40) | c_varchar | 变长字符串 |
| NULL | STRING | c_none | NULL值（值为NULL） |
| DATE | DATE | c_date | 日期 |
| TIMESTAMP | TIMESTAMP | c_timestamp | 时间戳 |
| DECIMAL64 | DECIMAL(18,8) | c_deci64 | 64位Decimal |
| DECIMAL128 | DECIMAL(38,18) | c_decimal128 | 128位Decimal |
| BINARY | BINARY | c_binary | 二进制 |
| ARRAY | ARRAY<INT> | c_array | 数组 |
| MAP | MAP<STRING, INT> | c_map | 映射 |
| STRUCT(ROW) | STRUCT<name:STRING, age:INT> | c_struct | 结构体/行 |

## 表DDL

```sql
DROP TABLE IF EXISTS sve_exp_operator_panoramic;

CREATE TABLE IF NOT EXISTS sve_exp_operator_panoramic(
    id INT,
    c_byte TINYINT,
    c_short SMALLINT,
    c_int INT,
    c_long BIGINT,
    c_float FLOAT,
    c_double DOUBLE,
    c_bool BOOLEAN,
    c_date DATE,
    c_char CHAR(40),
    c_varchar VARCHAR(40),
    c_string STRING,
    c_deci64 DECIMAL(18,8),
    c_decimal128 DECIMAL(38,18),
    c_timestamp TIMESTAMP,
    c_binary BINARY,
    c_none STRING,
    c_array ARRAY<INT>,
    c_map MAP<STRING, INT>,
    c_struct STRUCT<name:STRING, age:INT>
) STORED AS ORC;
```

## 测试数据

```sql
INSERT INTO TABLE sve_exp_operator_panoramic VALUES(
    8,
    -52,                                    -- c_byte
    3966,                                   -- c_short
    -2694959,                               -- c_int
    469891050425260120180,                  -- c_long
    -1475795656.558050,                     -- c_float
    1095435746.669908,                      -- c_double
    true,                                   -- c_bool
    date'1935-03-28',                       -- c_date
    'd步步步dddd',                          -- c_char
    'abcdefghij',                           -- c_varchar
    'Q',                                    -- c_string
    4631274245.92162661,                    -- c_deci64
    76051882560490807662.482874031011839644, -- c_decimal128
    timestamp'1973-08-03 08:00:00',         -- c_timestamp
    '1304699395',                           -- c_binary
    NULL,                                   -- c_none
    array(3,48,87,55,77),                  -- c_array
    map('number', 92,'age',58, 'height', 198), -- c_map
    named_struct('name','bkhzs','age',49)  -- c_struct
);
```

## 数据类型列顺序

CSV文件中数据类型列的顺序：

```python
TYPE_COLUMNS = [
    'BOOLEAN', 'BYTE', 'SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE',
    'STRING', 'CHAR', 'VARCHAR', 'NULL', 'DATE', 'TIMESTAMP',
    'DECIMAL64', 'DECIMAL128', 'BINARY', 'ARRAY', 'MAP', 'STRUCT(ROW)'
]
```
