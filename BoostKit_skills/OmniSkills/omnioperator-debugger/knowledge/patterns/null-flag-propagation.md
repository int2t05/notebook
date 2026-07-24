# Null Flag Propagation

## 适用场景

- 向量切片、复制、重建、投影后需要保留 NULL 语义

## 典型症状

- 原本为 NULL 的值变成默认值 `0`、空串或 false
- 值被复制，但 null bitmap 没有复制
- STRUCT / ARRAY 的父级 NULL 没有正确传递给子字段
- ORC PRESENT stream 与 Omni null bitmap 的 bit 语义被混淆

## 关键观察点

- `HasNull()`
- `IsNull(row)`
- 新向量是否同步设置 nulls
- parent nulls 与 child nulls 的合并逻辑
- 当前模块中 bit `1` 表示 NULL 还是 not-null

## 常见关联

- `vectors/const-vector.md`
- `operators/scan-orc.md`
- `cases/q62-const-vector-null.md`

## 已知案例

- Q001：`SliceConstVector` 只复制 `GetConstValue()`，没有复制 NULL 标记，导致 NULL 分区列被当作默认值。
- Q005：ORC STRUCT 读取中 parent nulls 传入 `OmniBooleanRleDecoder::nextNulls()`，如果不合并或 bit 语义反了，会导致 STRUCT 子字段 NULL 结果错误。

## 排查建议

1. 先确认差异是否只集中在 NULL 数据、分区列、常量列或 complex type 子字段。
2. 再检查 vector rebuild/slice/copy 路径是否只复制值，没有复制 null bitmap。
3. 对 ORC reader，单独确认 ORC PRESENT stream 与 Omni null bitmap 的语义转换。
