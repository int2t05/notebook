# Cases Index

`cases/` 只保存代表性主案例，用来示范如何使用 skill 完成一次定位。
相似问题或更细的 issue 经验应优先抽取到 `knowledge/`，避免这里变成完整 issue 归档。

## 当前案例

| case | 覆盖的问题类型 | 对应 knowledge |
| --- | --- | --- |
| `q45-existence-join.md` | `BroadcastHashJoin + ExistenceJoin` 结果行数不一致，累计缓存未按当前输出窗口切片 | `knowledge/operators/existence-join.md`、`knowledge/patterns/output-window-mismatch.md` |
| `q62-const-vector-null.md` | `ConstVector` slice 后 NULL 标记丢失，NULL 被当成默认值 | `knowledge/vectors/const-vector.md`、`knowledge/patterns/null-flag-propagation.md` |

## 未单独建 case 的 issue

以下 issue 已抽象进 `knowledge/`，暂不单独建 case：

- q3 dictionary encoding：见 `knowledge/vectors/dictionary-vector.md`
- q4 struct field coredump：见 `knowledge/patterns/nested-field-indexing.md`
- q5 struct ORC nulls：见 `knowledge/operators/scan-orc.md`
- q9 duplicate field name：见 `knowledge/operators/scan-orc.md`
- q17 complex type shuffle：见 `knowledge/patterns/cross-batch-copy.md`、`knowledge/patterns/state-lifecycle-race.md`
