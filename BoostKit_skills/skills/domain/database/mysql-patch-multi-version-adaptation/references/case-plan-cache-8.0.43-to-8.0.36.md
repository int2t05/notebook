# 案例：plan cache patch 从 Percona 8.0.43-34 移植到 MySQL 8.0.36

本案例用于指导 optimizer / prepared statement / plan cache 类 patch 的移植。

## 输入

- 源 patch：
  `mysql/boostdb-patches/0001-add-plan-cache-to-improve-select-performance.patch`
- 源版本：
  `percona-server-8.0.43-34`
- 目标版本：
  `mysql-8.0.36`

## patch 设计特征

- 新增 `sql/sql_plan_cache.cc`、`sql/sql_plan_cache.h`
- 接入 `Query_block::optimize()`
- 增加 `plan_cache`、`plan_cache_allow_change_ratio`
- 增加 `Cached_plan_hits`、`Cached_plan_invalidations`、`Cached_plan_count`
- 增加 PSI memory key
- 增加 MTR 用例

## 实际冲突点

### 1. `Scope_guard::release()` 在 8.0.36 不存在

处理方式：

- 改为 `error_guard.commit()`

结论：

- 属于 helper API 差异，不是逻辑冲突

### 2. `sql_lex` 缺少 patch 依赖的状态位

处理方式：

- 增加 `m_has_user_or_system_var`
- 增加 setter/getter
- 在 `LEX::reset()` 中复位

### 3. `mysqld.cc` 状态变量 helper 缺失

处理方式：

- 补 `show_cached_plan_invalidations()`
- 补 `show_cached_plan_count()`

### 4. `psi_memory_key` 注册项缺失

处理方式：

- 增加 `key_memory_plan_cache_mem_root`
- 注册 `plan_cache_mem_root`

### 5. `sql_union.cc` include 不完整

处理方式：

- 补 `sql_parse.h`
- 补 `sql_plan_cache.h`

### 6. `sql_executor.cc` 残留旧声明

处理方式：

- 删除与新声明冲突的旧 `static` 前置声明

### 7. `Query_block::optimize()` 需手工接入 cached plan 逻辑

处理方式：

- 手工改成 `plan_cache::exec_cached_plan(this)` 控制路径

### 8. 测试基线不同

处理方式：

- `memory_key_descriptions.test` 的计数从目标版本基线出发最小调整

## 运行时注意事项

- 使用 GCC 12.3.1 编译后，启动时要补 `LD_LIBRARY_PATH`
- 使用独立 datadir、socket、port 做验证
- `mysqlx` 端口冲突不影响主 SQL 验证，只要主 `mysqld` ready 即可

## 推荐验证动作

### SQL 验证

```sql
SHOW VARIABLES LIKE 'plan_cache%';
SHOW STATUS LIKE 'Cached_plan%';
PREPARE s1 FROM 'SELECT DISTINCT c FROM sbtest1 WHERE id BETWEEN ? AND ? ORDER BY c';
EXECUTE s1 USING @a,@b;
SHOW STATUS LIKE 'Cached_plan%';
```

重点看：

- `Cached_plan_count` 是否生成
- `Cached_plan_hits` 是否递增
- `DISTINCT + ORDER BY` prepared statement 是否稳定

### sysbench 验证

优先复现用户提供的故障路径：

- `--skip-trx=1`
- `--order_ranges=1`
- `--distinct_ranges=1`
- `oltp_read_only run`

期望结果：

- 不再出现 `mysql_stmt_store_result() returned error 0 ()`
- `ignored errors: 0`

## 可固化规则

- 如果 patch 新增 status var，但 8.0.36 缺 helper，优先在 `mysqld.cc` 补 `SHOW_FUNC`
- 如果 patch 从高版本移植到低版本，遇到 scope guard 生命周期 helper 先查 `commit/release/cancel`
- 如果 patch 命中 prepared statement 和 optimizer，要优先验证 prepared SQL，而不是只看普通 SQL
- 如果故障症状在客户端 `store_result`，优先怀疑服务端结果集元数据、临时表、filesort、group cache 生命周期
