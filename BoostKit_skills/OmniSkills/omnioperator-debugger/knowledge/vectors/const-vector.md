# Const Vector

## 适用场景

- 分区列、常量列、slice 后仍保持单值语义的列

## 常见问题模式

- `patterns/null-flag-propagation.md`
- `patterns/encoding-compatibility.md`

## 排查入口

- `GetConstValue()`
- NULL 标记是否被复制
- `SliceVector` / `SliceConstVector` 是否保留 NULL 语义

## 已知案例

- Q001：`SliceConstVector` 构造新 const vector 时只复制 const value，漏掉 `HasNull()` / `IsNull(0)` 对应的 NULL 标记，导致 NULL 分区列变成默认值。

## 排查建议

1. 看到分区列、常量列、单值列结果异常时，先确认是否为 `OMNI_CONST`。
2. 检查所有 slice/copy/rebuild 路径是否同步复制 NULL 语义。
3. 对 const null，不能只看 `GetConstValue()`，必须确认第 0 行是否 NULL。
