# Dictionary Vector

## 适用场景

- 字符串列或投影列使用 `OMNI_DICTIONARY` 编码

## 常见问题模式

- `patterns/encoding-compatibility.md`

## 排查入口

- `GetEncoding() == OMNI_DICTIONARY`
- 相关逻辑是否为 dictionary 分支提供了单独实现
- `CopyPositions` / `Slice` 后是否保持索引与底层数据一致

## 已知案例

- Q003：Predicate/string 处理逻辑只支持 flat string vector，遇到 `OMNI_DICTIONARY` 后 `dynamic_cast` 失败并在空指针处 coredump。

## 排查建议

1. string 类型 coredump 时，第一步打印 `GetEncoding()`，不要默认是 flat。
2. dictionary vector 的值访问需要同时看 dictionary index 和 base vector。
3. 修复时要确认 NULL 访问、值访问、copy/slice 三条路径都覆盖 dictionary encoding。
