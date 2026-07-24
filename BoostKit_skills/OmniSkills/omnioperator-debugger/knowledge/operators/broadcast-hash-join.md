# Broadcast Hash Join

## 适用场景

- `debug_e2e_sql_columnar` 显示 `broadcastJoin=false` 后结果恢复一致

## 常见问题模式

- `patterns/cross-batch-copy.md`
- `patterns/output-window-mismatch.md`
- `patterns/null-flag-propagation.md`

## 排查入口

- 先确认是否是普通 join 还是 `ExistenceJoin`
- 再看 build/probe 两侧输出路径是否存在窗口或 NULL 语义问题
- 对 ExistenceJoin，继续阅读 `operators/existence-join.md`
- 对非 ExistenceJoin，重点检查 build side key/value、probe side selection、输出 batch 边界
