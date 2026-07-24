# Existence Join

## 适用场景

- 物理计划中出现 `BroadcastHashJoin ... ExistenceJoin(...)`
- `OR + IN subquery` 一类 SQL 容易走到这条路径

## 常见问题模式

- `patterns/output-window-mismatch.md`
- `patterns/cross-batch-copy.md`

## 关键链路

- `ProbeBatchForExistenceJoin`
- `AppendExistenceRow`
- `BuildOutput`
- `ConstructExistenceColumn`

## 关键观察变量

- `probeRowOffset`
- `probeRowCount`
- 当前输出 `rowCount`
- `existJoinBuildIndex.size()`

## 代表案例

- `cases/q45-existence-join.md`
