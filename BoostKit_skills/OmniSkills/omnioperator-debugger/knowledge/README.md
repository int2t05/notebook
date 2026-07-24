# Knowledge Index

本目录用于沉淀跨 issue 可复用的调试知识，不保存完整 issue 历史。

## 目录结构

```text
knowledge/
├── README.md
├── operators/
│   ├── broadcast-hash-join.md
│   ├── existence-join.md
│   └── scan-orc.md
├── patterns/
│   ├── cross-batch-copy.md
│   ├── encoding-compatibility.md
│   ├── nested-field-indexing.md
│   ├── null-flag-propagation.md
│   ├── output-window-mismatch.md
│   └── state-lifecycle-race.md
└── vectors/
    ├── const-vector.md
    └── dictionary-vector.md
```

## 组织原则

- `patterns/`：按问题模式或根因模式组织，可跨 operator、跨模块复用
- `operators/`：按算子入口组织，用于快速定位某类算子常见问题与对应 pattern
- `vectors/`：按向量编码或向量语义组织，用于沉淀 `CONST`、`DICTIONARY`、NULL 标记等知识

## 使用规则

- 优先先写 `patterns/`，再由 `operators/` 或 `vectors/` 链接过去
- 如果一个问题能脱离具体 issue 单独成立，优先沉淀到 `knowledge/`
- 如果一个问题只对某次调试过程有意义，不放到 `knowledge/`

## 已吸收的 issue 经验

这里记录的是从既有 issue 目录抽象出的可复用经验；不是 issue 全量迁移清单。

| issue | 主要现象 | 沉淀位置 |
| --- | --- | --- |
| Q001 q62 const vector null | 分区 NULL 列经 const vector slice 后变成默认值 | `patterns/null-flag-propagation.md`、`vectors/const-vector.md`、`cases/q62-const-vector-null.md` |
| Q002 q9 duplicate field name | Spark 允许 STRUCT 重名字段，Omni schema 转换失败 | `patterns/encoding-compatibility.md`、`operators/scan-orc.md` |
| Q003 q3 dictionary encoding | string dictionary vector 走 flat 分支导致 coredump | `patterns/encoding-compatibility.md`、`vectors/dictionary-vector.md` |
| Q004 struct field coredump | struct field index 被当成顶层列 index 使用 | `patterns/nested-field-indexing.md` |
| Q005 struct ORC nulls | ORC STRUCT parent null 合并语义错误或未实现 | `patterns/null-flag-propagation.md`、`operators/scan-orc.md` |
| Q006 complex type shuffle | 跨 batch 状态、复用 buffer、生命周期竞争导致复杂类型异常 | `patterns/cross-batch-copy.md`、`patterns/state-lifecycle-race.md` |
| Q007 q45 existence join | ExistenceJoin 累计缓存未按当前输出窗口切片 | `patterns/output-window-mismatch.md`、`operators/existence-join.md`、`cases/q45-existence-join.md` |
