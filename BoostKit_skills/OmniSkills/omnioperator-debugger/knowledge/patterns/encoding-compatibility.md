# Encoding Compatibility

## 适用场景

- 同一逻辑在 `FLAT` 能工作，但在 `CONST`、`DICTIONARY` 等 encoding 下失败

## 典型症状

- `dynamic_cast` 失败
- 某个 encoding 分支缺失
- 结果只在特定 encoding 下异常
- 代码只按 `OMNI_FLAT` 处理，但输入实际为 `OMNI_DICTIONARY` 或 `OMNI_CONST`
- schema/field name 转换只考虑简单类型，复杂类型嵌套后失效

## 关键观察点

- `GetEncoding()`
- 每种 encoding 是否有单独处理分支
- NULL 语义是否在不同 encoding 下保持一致
- dynamic cast 目标类型是否覆盖当前 encoding 对应的 concrete vector
- nested type 重建时是否保留字段名、nullable、children 类型

## 常见关联

- `vectors/const-vector.md`
- `vectors/dictionary-vector.md`

## 已知案例

- Q002：Spark `StructType` 可以包含重复字段名，但 Omni schema 转换要求字段名唯一，需要在转换层递归 normalize。
- Q003：string column 实际为 `OMNI_DICTIONARY`，代码按 flat string vector 做 `dynamic_cast`，导致空指针和 coredump。

## 排查建议

1. 对 coredump 或类型转换失败，优先打印 `GetEncoding()` 和 vector concrete type。
2. 不要只修 flat 分支；需要确认 const/dictionary 后的值访问、NULL 访问和 copy/slice 语义。
3. 对 complex schema，检查字段名、nullable、child type 是否在递归转换中保持一致。
