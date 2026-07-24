# Q62 ConstVector NULL Case

## 问题现象

- SQL：`q62.sql` / `q62_test_null`
- Native Spark：`>120 days` 分桶结果为 `0`
- Original Omni：`>120 days` 分桶结果为 `39`
- 差异集中在分区列为 `NULL` 的数据，Omni 将 NULL 当成默认值参与计算

## 版本信息

- Gluten commit：`e751224`
- OmniOperator commit：`141e0c97`
- 相关 PR：`https://gitcode.com/openeuler/OmniOperator/pull/358`

## skill 执行步骤

本案例的主路径为：结果对比 -> 定位 NULL 分区列 -> 检查向量 encoding -> 检查 slice/copy 后 NULL 标记。

1. 使用 `run_e2e_sql_native` 获取 Spark 基线
2. 使用 `run_e2e_sql` 复现 Omni 结果不一致
3. 将 SQL 收敛到只验证 NULL 分区列参与计算的最小场景
4. 在 native 侧检查输入向量 encoding，确认列为 `CONST`
5. 检查 `SliceConstVector` 是否只复制值而没有复制 NULL 标记
6. 修复后重新运行 Native/Omni 对比

## 关键证据

- `SliceConstVector` 使用 `GetConstValue()` 构造新 const vector
- 原始 const vector 的第 0 行为 NULL
- 新 const vector 没有同步 `SetNulls`，导致 NULL 被下游解释为默认值

## 根因

`SliceConstVector` 只复制了 const value，没有复制 const vector 的 NULL bitmap。
当分区列全 NULL 或当前 const 值为 NULL 时，新向量仍表现为非 NULL 默认值。

## 修复

在 `OmniOperator/core/src/vector/vector_helper.h` 的 `SliceConstVector` 中，构造新 const vector 后同步 NULL 语义：

```cpp
if (vector->HasNull() && vector->IsNull(0)) {
    newConstVec->SetNulls(0, true, length);
}
```

## 验证结果

- 修复后 Omni 与 Native 在 q62 NULL 分区列场景下结果一致
- NULL 不再被错误转换为 `0`、空串或 false

## 对应经验

- 参见 `knowledge/vectors/const-vector.md`
- 参见 `knowledge/patterns/null-flag-propagation.md`
- 当结果差异只发生在 NULL、分区列、常量列附近时，应优先检查 const vector 的 slice/copy/rebuild 路径
