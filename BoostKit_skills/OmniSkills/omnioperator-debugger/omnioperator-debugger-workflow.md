# OmniOperator 数据不一致问题调试流程

当 Omni 和 Spark 的结果不一致时，按照以下步骤定位问题。

## 完整调试流程（8 阶段）

### 阶段 1：复现问题

**步骤 1：执行原始 SQL 确认问题**

```python
# 执行 Spark Native 基准测试
run_e2e_sql_native(sql="<q62 SQL text>", database="<database>", timeout_sec=300)

# 执行 Omni 测试
run_e2e_sql(sql="<q62 SQL text>", database="<database>", timeout_sec=300)

# 对比两个工具返回的查询结果行
```

**结果确认**：
- Spark：100 行数据
- Omni：统计出 39 条 `>120 days` 的记录（错误）
- **结论**：问题确实存在，需要进一步定位

### 阶段 2：通过参数控制定位问题算子

**步骤 2：分析 Spark 执行计划**

```sql
-- 查看物理执行计划
EXPLAIN EXTENDED
SELECT ...
FROM web_sales, date_dim
WHERE d_month_seq BETWEEN 1212 AND 1212 + 11
  AND ws_ship_date_sk = d_date_sk
  AND (ws_ship_date_sk - ws_sold_date_sk) > 120;
```

**执行计划分析**（从后往前）：
```
1. Project (投影算子) - 最后执行
   └─ 2. Filter (过滤算子) - 应用 >120 条件
      └─ 3. BroadcastHashJoin (广播连接算子) - ws_ship_date_sk = d_date_sk
         ├─ 4. Scan web_sales (扫描算子)
         └─ 5. Scan date_dim (扫描算子)
```

**步骤 3：从后往前逐个关闭算子**

**为什么从后往前？**
- 后面的算子依赖前面算子的输出
- 从后往前可以隔离问题
- 如果关闭某个算子后结果正确了，说明问题就在这个算子或它依赖的前置算子

**测试 1：关闭 Project 算子**

```sql
SET spark.gluten.sql.columnar.project=false;
-- 执行查询，对比结果
-- 结果：仍然不一致 → 问题不在 Project
```

**测试 2：关闭 Filter 算子**

```sql
SET spark.gluten.sql.columnar.filter=false;
-- 执行查询，对比结果
-- 结果：仍然不一致 → 问题不在 Filter
```

**测试 3：关闭 BroadcastHashJoin 算子**

```sql
SET spark.gluten.sql.columnar.broadcastJoin=false;
-- 执行查询，对比结果
-- 结果：一致了！→ 问题出在 BroadcastHashJoin
```

**结论**：问题定位到 **BroadcastHashJoin（LookupJoin）算子**

### BroadcastHashJoin + ExistenceJoin 专项经验

如果物理计划中的 `BroadcastHashJoin` 带有 `ExistenceJoin(...)`，不要直接套普通 inner/outer join 的输出路径分析。`ExistenceJoin` 不展开 build side rows，而是给 probe side 每一行补一个 existence boolean 列，因此更容易在 output builder 的分页状态上出问题。

优先检查以下链路：

1. `LookupJoinWithExprOperator::AddInput`
   - 确认 probe 侧表达式投影后的 `VectorBatch` 行数、列数和 join key 列正确。

2. `LookupJoinOperator::ProbeBatchForExistenceJoin`
   - 确认每个 probe row 只 append 一次 existence 结果。
   - 确认 `curProbePosition`、hash table partition、lookup 返回的 build row/batch index 没越界。

3. `LookupJoinOutputBuilder::AppendExistenceRow`
   - 确认 `probeRowCount` 与 `existJoinBuildIndex` 的增长关系一致。

4. `LookupJoinOutputBuilder::BuildOutput` / `ConstructExistenceColumn`
   - 重点检查 `probeRowOffset`、`probeRowCount`、`existJoinBuildIndex.size()` 三者关系。
   - `existJoinBuildIndex` 如果是累计缓存，构造当前输出批次时应按当前窗口切片，即 `[probeRowOffset, probeRowOffset + rowCount)`，不要直接整段拷贝。

推荐的不变量检查：

```cpp
OMNI_CHECK(probeRowOffset >= 0, "negative probeRowOffset");
OMNI_CHECK(probeRowCount >= 0, "negative probeRowCount");
OMNI_CHECK(probeRowOffset + rowCount <= existJoinBuildIndex.size(),
    "current existence output window exceeds accumulated existence index");
OMNI_CHECK(probeRowOffset + probeRowCount <= existJoinBuildIndex.size(),
    "remaining existence output window exceeds accumulated existence index");
```

经验判断：如果 SQL 已经 `Fetched N row(s)`，但随后在 driver/executor 退出或 cleanup 阶段失败，优先检查 output builder 的 row offset / row count / accumulated buffer，而不是只盯 coredump 栈顶。

### 阶段 3：简化 SQL

**步骤 4：简化 SQL 隔离核心逻辑**

**简化原则**：
1. **移除不必要的子查询和聚合**：只保留与问题直接相关的逻辑
2. **保留核心计算逻辑**：如果问题在日期差计算，保留 `date1 - date2`
3. **避免优化器干扰**：使用表达式作为过滤条件
4. **先测试全量数据**：去掉 LIMIT，测试完整数据集

**错误示例 vs 正确示例**：

```sql
-- 错误示例：优化器会移除未使用的列
SELECT ws_sold_date_sk
FROM web_sales
WHERE ws_sold_date_sk IS NULL;

-- 正确示例：使用表达式作为过滤条件
SELECT ws_ship_date_sk, ws_sold_date_sk,
       (ws_ship_date_sk - ws_sold_date_sk) as diff
FROM web_sales
WHERE (ws_ship_date_sk - ws_sold_date_sk) IS NULL;
```

**简化 SQL 模板**：

```sql
-- 测试 NULL 值处理
SELECT 
   <column1>,
   <column2>,
   (<column1> - <column2>) as diff,
   CASE WHEN (<column1> - <column2> > <threshold>) THEN 1 ELSE 0 END as flag
FROM <table1>, <table2>
WHERE <join_condition>
  AND (<column1> - <column2>) IS NULL;
```

### 阶段 4：分析算子代码结构

**重要**：在添加调试代码之前，需要先分析算子的代码结构和数据流。

**步骤 5：查找相关代码文件**

```bash
# 在代码库中搜索算子名称
grep -r "BroadcastHashJoin" {{project.remote_work_dir}}/OmniOperator/core/src/
grep -r "LookupJoin" {{project.remote_work_dir}}/OmniOperator/core/src/
```

**找到的关键文件**：
- `lookup_join_expr.cpp` - LookupJoin 带表达式处理的算子
- `lookup_join.cpp` - LookupJoin 基础实现
- `hash_builder_expr.cpp` - HashBuilder 带表达式处理的算子
- `hash_builder.cpp` - HashBuilder 基础实现

**步骤 6：分析数据流**

阅读算子代码，识别关键方法：

```cpp
class LookupJoinWithExprOperator {
    // 关键方法分析：
    
    // 1. AddInput - 接收输入数据
    int32_t AddInput(VectorBatch *vecBatch) {
        // 数据流：
        // 1. 接收 probe 侧输入 vecBatch
        // 2. ProjectVectors - 对输入进行投影（可能改变数据）← 关键路径
        // 3. 传递给 lookupJoinOperator 进行实际的 join 操作
        // 4. 返回结果
    }
    
    // 2. GetOutput - 获取输出数据
    int32_t GetOutput(VectorBatch **outputVecBatch) {
        // 从 lookupJoinOperator 获取输出
    }
};
```

**步骤 7：识别关键调用**

**关键调用特征**：
- 对输入数据进行转换的函数（如 `ProjectVectors`）
- 创建新向量的函数（如 `SliceVector`）
- 表达式求值的函数（如 `ExprEval`）

**步骤 8：确定调试代码添加位置**

**添加位置原则**：
- 在关键调用**前后**都添加打印
- 打印内容应该可以对比（如原始输入 vs 投影后）
- 包含足够的上下文信息（RowCount, VectorCount）

### 阶段 5：添加调试代码

**步骤 10：在关键路径添加 PrintVecBatch**

修改 `lookup_join_expr.cpp`：

```cpp
int32_t LookupJoinWithExprOperator::AddInput(VectorBatch *vecBatch)
{
    if (vecBatch->GetRowCount() <= 0) {
        VectorHelper::FreeVecBatch(vecBatch);
        ResetInputVecBatch();
        return 0;
    }
    
    // [DEBUG] 打印原始输入数据（ProjectVectors 之前）
    std::cout << "[DEBUG] LookupJoinWithExprOperator::AddInput - Original input vecBatch:" << std::endl;
    std::cout << "  RowCount: " << vecBatch->GetRowCount() << ", VectorCount: " << vecBatch->GetVectorCount() << std::endl;
    VectorHelper::PrintVecBatch(vecBatch);
    std::cout << std::endl;
    
    // 关键调用：ProjectVectors 可能对数据进行投影/转换
    auto *newInputVecBatch = OperatorUtil::ProjectVectors(vecBatch, probeTypes, projections, executionContext.get());
    
    // [DEBUG] 打印投影后的数据（ProjectVectors 之后）
    std::cout << "[DEBUG] LookupJoinWithExprOperator::AddInput - After ProjectVectors:" << std::endl;
    std::cout << "  RowCount: " << newInputVecBatch->GetRowCount() << ", VectorCount: " << newInputVecBatch->GetVectorCount() << std::endl;
    VectorHelper::PrintVecBatch(newInputVecBatch);
    std::cout << std::endl;
    
    VectorHelper::FreeVecBatch(vecBatch);
    ResetInputVecBatch();
    lookupJoinOperator->AddInput(newInputVecBatch);
    SetStatus(lookupJoinOperator->GetStatus());
    return 0;
}
```

同样修改 `hash_builder_expr.cpp`。

**步骤 11：处理 CONST 向量打印**

**重要**：分区列会被创建为 `OMNI_ENCODING_CONST` 类型，这是正常现象。

**CONST 向量的特点**：
- 所有行共享同一个值
- 通过 `GetConstValue()` 获取常量值
- NULL 标记需要特殊处理（`HasNull() && IsNull(0)`）

**常见问题场景**：
- 分区列（如 `d_date_sk`）在 Join 后被创建为 CONST 向量
- 当分区列值为 NULL 时，CONST 向量有 NULL 标记
- Slice 操作必须保留 NULL 标记

修改 `vector_helper.h` 的 `PrintVectorValue` 函数：

```cpp
static void PrintVectorValue(BaseVector *vector, int32_t rowIndex)
{
    using namespace omniruntime::type;
    if (vector->IsNull(rowIndex)) {
        std::cout << "NULL" << "\t";
        return;
    }

    auto encoding = vector->GetEncoding();
    if (encoding == vec::OMNI_DICTIONARY) {
        DYNAMIC_TYPE_DISPATCH(PrintDictionaryVectorValue, vector->GetTypeId(), vector, rowIndex);
    } else if (encoding == vec::OMNI_ENCODING_CONST) {
        // 处理 CONST 向量（分区列）
        DYNAMIC_TYPE_DISPATCH(PrintConstVectorValue, vector->GetTypeId(), vector, rowIndex);
    } else {
        DYNAMIC_TYPE_DISPATCH(PrintFlatVectorValue, vector->GetTypeId(), vector, rowIndex);
    }
}

// 添加 CONST 向量打印辅助函数
template <type::DataTypeId typeId>
static void PrintConstVectorValue(BaseVector *vector, int32_t rowIndex)
{
    using T = typename type::NativeType<typeId>::type;
    auto constVec = reinterpret_cast<ConstVector<T> *>(vector);
    std::cout << constVec->GetConstValue() << "\t";
}
```

**向量类型说明**：
- `OMNI_FLAT (0)` - 普通扁平向量
- `OMNI_DICTIONARY (1)` - 字典编码向量
- `OMNI_ENCODING_CONTAINER (2)` - 容器向量
- `OMNI_ENCODING_MAP (3)` - Map 类型向量
- `OMNI_ENCODING_ARRAY (4)` - Array 类型向量
- `OMNI_ENCODING_STRUCT (5)` - Struct 类型向量
- `OMNI_ENCODING_CONST (6)` - 常量向量（分区列）

### 阶段 6：执行测试与分析

**步骤 12：上传文件并编译**

**重要**：只上传修改的代码文件，不要上传整个目录！

```bash
# 只上传修改的单个文件（推荐）
scp -P {{server.port}} /本地路径/lookup_join_expr.cpp {{server.username}}@{{server.host}}:{{project.remote_work_dir}}/OmniOperator/core/src/operator/join/

scp -P {{server.port}} /本地路径/vector_helper.h {{server.username}}@{{server.host}}:{{project.remote_work_dir}}/OmniOperator/core/src/vector/
```

**编译前检查**：

```bash
# 检查是否有正在运行的编译进程
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ps aux | grep build_omniop_330.sh | grep -v grep'

# 检查是否有 make 进程在运行
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ps aux | grep "make\|ninja" | grep -v grep'
```

**选择编译参数**：

```python
# 需要跑 Spark SQL 验证时，统一编译并部署 Omni + Gluten 产物
compile_gluten(
    omni_branch="<omni branch>",
    gluten_branch="<gluten branch>",
)
```

**判断编译完成**：

使用 `get_compile_log()` 查看 `compile_gluten` 日志与最终状态。

**步骤 13：执行测试收集调试输出**

```python
run_e2e_sql(sql="<q62_test_null SQL text>", database="<database>", timeout_sec=300)
```

**步骤 14：分析调试输出**

发现关键问题：

```
[DEBUG] LookupJoinWithExprOperator::AddInput - Original input vecBatch:
  RowCount: 194, VectorCount: 2
  Vector[0] (ws_ship_date_sk): 2451214, 2452551, ... (实际值)
  Vector[1] (ws_sold_date_sk): NULL, NULL, ... (194 条 NULL)

[DEBUG] LookupJoinWithExprOperator::AddInput - After ProjectVectors:
  RowCount: 194, VectorCount: 2
  Vector[0] (ws_ship_date_sk): 2451214, 2452551, ... (保持不变)
  Vector[1] (ws_sold_date_sk): 0, 0, ... (NULL 变成了 0!)
```

**结论**：在 `ProjectVectors` 过程中，`ws_sold_date_sk` 的 NULL 值被错误地转换成了 0。

### 阶段 7：定位根因

**步骤 15：深入分析 ProjectVectors**

追踪代码调用链：

```
ProjectVectors
  → Projection::ProjectVec
    → SliceVector (slice 向量)
      → SliceConstVector (处理 CONST 向量)
```

查看 `SliceConstVector` 函数：

```cpp
static BaseVector *SliceConstVector(BaseVector *vector, int length)
{
    DataTypeId dataTypeId = vector->GetTypeId();
    switch (dataTypeId) {
        case type::OMNI_INT:
        case type::OMNI_DATE32:
            return new ConstVector<int32_t>(
                reinterpret_cast<ConstVector<int32_t> *>(vector)->GetConstValue(), 
                dataTypeId, length);
        // ... 其他类型
    }
}
```

**发现问题**：创建新的 CONST 向量时，只复制了 `GetConstValue()`，**没有复制 NULL 标记**！

### 阶段 8：修复验证

**步骤 16：修复代码**

修改 `vector_helper.h` 的 `SliceConstVector` 函数：

```cpp
static BaseVector *SliceConstVector(BaseVector *vector, int length)
{
    DataTypeId dataTypeId = vector->GetTypeId();
    BaseVector *newConstVec = nullptr;
    switch (dataTypeId) {
        case type::OMNI_INT:
        case type::OMNI_DATE32:
            newConstVec = new ConstVector<int32_t>(
                reinterpret_cast<ConstVector<int32_t> *>(vector)->GetConstValue(), 
                dataTypeId, length);
            break;
        // ... 其他类型
    }
    
    // Copy null flag from source CONST vector if it has nulls
    if (vector->HasNull() && vector->IsNull(0)) {
        newConstVec->SetNulls(0, true, length);
    }
    
    return newConstVec;
}
```

**关键修改**：
1. 将直接返回改为先创建变量 `newConstVec`
2. 在返回前检查原始向量是否有 NULL 标记
3. 如果有，使用 `SetNulls()` 复制到新向量

**步骤 17：重新编译并验证**

```bash
# 重新上传修复后的文件
scp -P {{server.port}} /本地路径/vector_helper.h {{server.username}}@{{server.host}}:{{project.remote_work_dir}}/OmniOperator/core/src/vector/
```

```python
# 重新编译并部署可供 Spark SQL 加载的 Omni + Gluten 产物
compile_gluten(
    omni_branch="<omni branch>",
    gluten_branch="<gluten branch>",
)

# 重新执行测试
run_e2e_sql(sql="<q62_test_null SQL text>", database="<database>", timeout_sec=300)
```

**验证结果**：
- **修复前**：`ws_sold_date_sk` 从 NULL 变成 0
- **修复后**：`ws_sold_date_sk` 保持 NULL
- **完整查询测试**：Omni 和 Spark 返回相同的 100 行结果

## 表达式求值调试

当怀疑某个表达式的计算有问题时，可以采用以下方法：

**步骤 1：查看表达式的中间结果**

```sql
-- 原始查询
SELECT ws_ship_date_sk - ws_sold_date_sk AS diff
FROM web_sales, date_dim
WHERE ws_ship_date_sk = d_date_sk

-- 调试查询：分别查看各个字段的值
SELECT 
  ws_ship_date_sk,
  ws_sold_date_sk,
  ws_sold_date_sk IS NULL as is_null,
  ws_ship_date_sk - ws_sold_date_sk AS diff
FROM web_sales, date_dim
WHERE ws_ship_date_sk = d_date_sk
  AND ws_sold_date_sk IS NULL  -- 专门查看 NULL 值的情况
```

**步骤 2：验证边界条件**

```sql
-- 查看差值的分布
SELECT 
  CASE 
    WHEN diff <= 30 THEN '0-30'
    WHEN diff <= 60 THEN '31-60'
    WHEN diff <= 120 THEN '61-120'
    ELSE '>120'
  END as diff_range,
  COUNT(*) as cnt,
  MIN(diff) as min_diff,
  MAX(diff) as max_diff
FROM (
  SELECT ws_ship_date_sk - ws_sold_date_sk AS diff
  FROM web_sales, date_dim
  WHERE ws_ship_date_sk = d_date_sk
) t
GROUP BY diff_range
ORDER BY diff_range
```

**步骤 3：对比 Omni 和 Spark 的结果**

- 如果 Omni 和 Spark 在 NULL 值处理上不一致，说明是表达式求值的问题
- 重点检查：NULL - 值、值 - NULL、NULL + NULL 等边界情况

## 数据质量检查

在排查列式算子问题前，建议先检查数据质量：

**检查 NULL 值分布**：

```sql
-- 检查关键字段的 NULL 值数量
SELECT 
  COUNT(*) as total_count,
  COUNT(CASE WHEN ws_sold_date_sk IS NULL THEN 1 END) as null_sold_date_sk,
  COUNT(CASE WHEN ws_ship_date_sk IS NULL THEN 1 END) as null_ship_date_sk,
  COUNT(CASE WHEN ws_sold_date_sk IS NOT NULL AND ws_ship_date_sk IS NOT NULL THEN 1 END) as both_not_null
FROM web_sales;
```

**检查 JOIN 条件**：

```sql
-- 检查 JOIN 后丢失的记录
SELECT 
  COUNT(ws.ws_sold_date_sk) as matched_count,
  COUNT(CASE WHEN ws.ws_sold_date_sk IS NULL THEN 1 END) as null_after_join
FROM web_sales ws
LEFT JOIN date_dim d ON ws.ws_ship_date_sk = d.d_date_sk
WHERE d.d_month_seq BETWEEN 1212 AND 1212 + 11;
```

**检查数据范围**：

```sql
-- 检查日期差值的范围
SELECT 
  MIN(ws_ship_date_sk - ws_sold_date_sk) as min_diff,
  MAX(ws_ship_date_sk - ws_sold_date_sk) as max_diff,
  AVG(ws_ship_date_sk - ws_sold_date_sk) as avg_diff
FROM web_sales
WHERE ws_sold_date_sk IS NOT NULL;
```

## 典型问题案例库

### 案例 1：广播连接 NULL 值处理问题

**问题现象**：
- Omni 统计出 39 条 `>120 days` 的记录，Spark 结果为 0
- 涉及表达式：`ws_ship_date_sk - ws_sold_date_sk > 120`

**根因**：
- 39 条记录的 `ws_sold_date_sk` 为 NULL
- Omni 错误地将 NULL 当作 0 处理：`ws_ship_date_sk - 0 = ws_ship_date_sk`
- 导致 `245xxxx > 120` 被错误判断为 true

**解决方法**：
1. 临时方案：关闭广播连接
   ```sql
   SET spark.gluten.sql.columnar.broadcastJoin=false;
   ```
2. 长期方案：修复 Omni 的 NULL 值处理逻辑

**验证 SQL**：

```sql
SELECT COUNT(CASE WHEN (ws_ship_date_sk - ws_sold_date_sk > 120) THEN 1 END) as gt_120_count
FROM web_sales, date_dim
WHERE ws_ship_date_sk = d_date_sk;
```

**教训**：
- 涉及 NULL 值的表达式计算要特别小心
- 广播连接的 NULL 值处理可能是薄弱环节
- 一定要检查数据中是否存在 NULL 值

## 调试最佳实践总结

### 调试流程

1. **先复现问题**：确认问题确实存在
2. **分析执行计划**：使用 `EXPLAIN EXTENDED` 确定算子链
3. **参数控制从后往前**：根据执行计划逆序关闭算子
4. **分析算子代码结构**：阅读代码，理解数据流，确定关键路径
5. **在关键路径添加日志**：在关键调用前后添加打印
6. **简化 SQL**：隔离核心逻辑
7. **验证修复**：与 Spark 结果对比

### 文件上传

- **只上传修改的代码文件**：不要上传整个目录
- **根据修改范围选择编译参数**：`--omni` / `--gluten` / 全量
- **编译前检查之前的编译是否结束**：避免冲突
- **通过库文件时间戳判断编译完成**：`libboostkit-*.so`

### SQL 编写

- **使用表达式作为过滤条件**：避免优化器移除关键列
- **测试 NULL 值时使用表达式 IS NULL**：而不是列 IS NULL
- **先测试全量数据**：再去掉 LIMIT 抽样

### 对比基准

- **必须与 Spark 的结果对比**：Spark 是标准正确的基准
- **检查数据质量**：先检查 NULL 值分布
- **检查 JOIN 条件**：确认 JOIN 后没有丢失记录

