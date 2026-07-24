# Nested Field Indexing

## 适用场景

- STRUCT 字段访问、nested projection、field expression eval
- 表达式中出现 `col_struct.field`、`col_struct.child.grandchild`

## 典型症状

- Spark Native 正常，Omni 在 struct field access 时 coredump
- `SetIsField`、字段标记、字段投影作用到了错误的顶层列
- field index 在 nested schema 中正确，但被误当作 top-level column index

## 关键观察点

- 当前 index 是 child field index 还是 top-level vector index
- `FieldExpr::input` 是否需要向上递归找到根输入列
- `vecBatch_` 访问前是否做了 null/range 检查

## 已知案例

- Q004：`ExprEval::Visit(const FieldExpr &e)` 使用 `e.colVal` 标记 `vecBatch_`，但 `e.colVal` 是 STRUCT 内部字段序号，不是顶层列序号，导致访问错误 vector 并 coredump。

## 排查建议

1. 对 nested field 问题，不要只看当前字段名；先区分 logical field index 和 physical input vector index。
2. 打印表达式树，从当前 `FieldExpr` 沿 `input` 回溯到顶层输入列。
3. 所有用 nested field index 访问顶层 batch 的地方，都需要单独检查。
