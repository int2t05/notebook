# Output Window Mismatch

## 适用场景

- 算子存在分批输出或分页输出
- 内部缓存是累计状态，但当前输出只消费其中一个窗口

## 典型症状

- 结果行数异常
- 当前批次数据与前一批或累计缓存错位
- `offset / rowCount / size` 三者关系不一致
- 单批输出正确，多批输出后开始错行或丢行
- 关闭某个 join/project/agg 后结果恢复一致

## 关键观察点

- `probeRowOffset`
- `probeRowCount`
- 当前批次 `rowCount`
- 累计缓存 `size()`
- 当前输出窗口 `[offset, offset + rowCount)`

## 常见关联

- `operators/existence-join.md`
- `cases/q45-existence-join.md`

## 已知案例

- Q007：`existJoinBuildIndex` 为累计缓存，`ConstructExistenceColumn()` 应按 `[probeRowOffset, probeRowOffset + numRows)` 拷贝，而不是从 begin 开始。

## 排查建议

1. 在生成输出列的位置打印窗口起点、窗口长度、累计缓存长度。
2. 对每个输出 batch 保留一组首尾 index，用来判断是否重复使用了上一批窗口。
3. 如果 `debug_e2e_sql_columnar` 显示关闭某个算子后结果恢复一致，优先在该算子的输出构造链路加窗口检查。
