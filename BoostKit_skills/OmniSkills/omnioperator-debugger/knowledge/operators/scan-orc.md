# Scan ORC

## 适用场景

- ORC 读取、STRUCT 字段读取、NULL 读取异常

## 常见问题模式

- `patterns/null-flag-propagation.md`
- `patterns/encoding-compatibility.md`
- `patterns/nested-field-indexing.md`

## 排查入口

- reader 对 NULL 的处理
- complex type / struct field 的字段映射
- reader 输出向量的 encoding 和 null bitmap
- ORC PRESENT stream 到 Omni null bitmap 的语义转换
- STRUCT parent nulls 与 child field nulls 的合并

## 已知案例

- Q002：STRUCT 字段名重复时，Spark schema 可以表达，但 Omni schema 构造要求字段名唯一，需要在转换层递归处理重名字段。
- Q005：STRUCT ORC 读取时，parent nulls 传给 `OmniBooleanRleDecoder::nextNulls()`，如果未实现 parent/child null 合并，会抛 `Not implemented yet for struct type!` 或产生错误 NULL 结果。

## 排查建议

1. 遇到 ORC + STRUCT 问题，先分清是 schema conversion、reader null merge，还是 expression field access。
2. 如果异常发生在 reader 阶段，重点看 `OmniStructColumnReader::next()`、`readNulls(...)`、`OmniBooleanRleDecoder::nextNulls(...)`。
3. 如果异常发生在表达式阶段，转到 `patterns/nested-field-indexing.md`。
