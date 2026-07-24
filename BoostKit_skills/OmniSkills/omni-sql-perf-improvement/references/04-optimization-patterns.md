# 参考：优化策略详情

> Agent trigger：优化点已识别（可能多个），需要为每个点选具体改动方案。
>
> Agent deliverable：每个优化点对应一个 commit 方案（不同目标不混入同一 commit），并附验证指标。多个小收益点合并验证时，按整体端到端提升判断。

## §计算 — 计算效率优化

### 核心策略

| 策略          | 适用场景                         | 典型收益   |
|---------------|----------------------------------|-----------|
| SIMD 向量化   | 数值批量计算（加减乘比较）        | 2×~8×     |
| 算法降阶      | O(n²) 嵌套循环可转为 Hash/Sort   | 数量级     |
| 循环展开      | 固定长度循环，减少分支跳转        | 10%~30%   |
| 不变量外提    | 循环内重复调用的函数/计算         | 按实际比例 |
| 函数内联      | 高频小函数虚调用开销大            | 5%~20%    |

### SIMD 向量化示例（C++）

```cpp
// Before：逐元素处理
for (int i = 0; i < n; i++) {
    result[i] = a[i] + b[i];
}

// After：使用 AVX2 一次处理 8 个 int32
#include <immintrin.h>
for (int i = 0; i < n; i += 8) {
    __m256i va = _mm256_loadu_si256((__m256i*)(a + i));
    __m256i vb = _mm256_loadu_si256((__m256i*)(b + i));
    _mm256_storeu_si256((__m256i*)(result + i), _mm256_add_epi32(va, vb));
}
```

> ⚠️ 前提：数据内存连续（列存格式天然满足）；需确认目标机器支持 AVX2/AVX512。

### ARM64 Kunpeng 920 SIMD 特别说明

> ⚠️ **指令集规定：严禁使用 NEON（`arm_neon.h`）进行向量化；必须使用 SVE（`arm_sve.h`）。**
> Kunpeng 920 SVE 实现宽度 256-bit；NEON 固定 128-bit 且实测在 ORC 解码路径比 scalar 慢。

在 ARM64（Kunpeng 920 / openEuler）上应用 SVE 向量化**必须**在编码前完成以下检查，否则优化无效甚至变慢：

| 检查项 | 正确做法 | 反例（会失效） |
|--------|---------|--------------|
| **指令集** | 使用 `arm_sve.h`，`svld1_*` / `svst1_*` 等顺序 load/store | 使用 `arm_neon.h` 的任何指令 → **被明确禁止** |
| **批大小（bufferNum）** | 确认实际调用时 batch 足够大（≥ SVE 256-bit 宽度对应的元素数，如 int32 时 ≥ 8） | bufferNum 通常仅几十个元素 → SVE 循环 setup 开销 > 计算节省，实测变慢 |
| **内存访问模式** | 数据顺序连续（stride=1），用 `svld1_*` 顺序 load；**禁止 gather loads** | stride 非 1 → 禁用 `svld1_gather_*`（gather 对非连续地址有收集延迟惩罚，慢于 scalar） |
| **编码类型命中** | 确认火焰图热点函数对应的 ORC 编码分支（DIRECT / PATCHED / DELTA）与 SVE 实现的分支一致 | 热点在 DIRECT 编码路径，但实测数据走的是 PATCHED → SVE 从未执行 |
| **函数占比门槛** | 目标函数火焰图占比 > 5%（绝对值）才值得 SVE 化 | 占比 3%，即使优化到 0% → 端到端仅降 0.3s，在噪声内无法验证 |

---

## §内存 — 内存压力优化

### 核心策略

| 策略           | 适用场景                      | 说明                                 |
|----------------|-------------------------------|--------------------------------------|
| 对象池         | 高频创建/销毁的固定大小对象   | 复用对象，减少 GC 压力               |
| 零拷贝         | 数据在组件间传递              | 传引用/指针而非复制数据              |
| 紧凑数据结构   | 装箱类型（Integer/Long 等）   | 改用原始类型数组                     |
| 缓冲区预分配   | 频繁扩容的动态缓冲区          | 按预期数据量一次性分配               |
| Off-heap       | JVM 堆压力大、GC 频繁         | 使用 Unsafe / Arrow 内存             |

### 对象池示例（Java/Scala）

```java
// 使用 Apache Commons Pool2
GenericObjectPool<MyBuffer> pool = new GenericObjectPool<>(new MyBufferFactory());

MyBuffer buf = pool.borrowObject();
try {
    // 使用 buf
} finally {
    pool.returnObject(buf);  // 归还，不触发 GC
}
```

---

## §null — null 处理优化

### 核心策略：null 位图提前过滤

**原理：** 在表达式求值前，用 null bitmap 批量跳过 null 行，避免进入计算主路径。

```cpp
// Before：逐行判断 null
for (int i = 0; i < batch_size; i++) {
    if (!col->isNull(i)) {
        result[i] = eval_expr(col->getValue(i));
    }
}

// After：先构建有效行索引，批量计算
std::vector<int> valid_rows;
for (int i = 0; i < batch_size; i++) {
    if (!null_bitmap[i]) valid_rows.push_back(i);
}
// 只对 valid_rows 执行计算（可进一步向量化）
for (int idx : valid_rows) {
    result[idx] = eval_expr(col->getValue(idx));
}
```

**进阶：** null 比例 > 80% 时，可以整批跳过计算直接输出 null 批次。

---

## §字典 — 字典编码优化

### 核心策略：延迟解码（Late Materialization）

**原则：** 在 Filter / Join / Agg 等操作中，尽量保持字典编码，只在最终输出时解码。

```
❌ 错误顺序：DECODE → FILTER → AGG → OUTPUT
✓ 正确顺序：FILTER(on dict_id) → AGG(on dict_id) → DECODE → OUTPUT
```

### 字典域直接计算示例

```cpp
// GROUP BY string_col（高字典率）
// Before：比较原始字符串（开销大）
HashMap<String, int64_t> agg_map;
for (int i = 0; i < batch_size; i++) {
    agg_map[col->getString(i)] += value[i];  // 字符串哈希 + 比较
}

// After：用字典 ID 作为 key（开销极小）
HashMap<int32_t, int64_t> agg_map;
for (int i = 0; i < batch_size; i++) {
    agg_map[col->getDictId(i)] += value[i];  // 整数比较
}
// 最后再把 dict_id → string 做一次映射
```

---

## §倾斜 — 数据倾斜优化

### 策略选择

| 场景                    | 推荐策略             | 说明                                      |
|-------------------------|----------------------|-------------------------------------------|
| Join 倾斜（热点 Key）   | 加盐两阶段 Join      | 热点 Key 随机加后缀，扩散到多个 partition  |
| Agg 倾斜（热点 Key）    | 两阶段聚合           | 局部聚合 → Shuffle → 全局聚合              |
| NULL Key 倾斜           | 过滤 + 单独处理      | null key 单独走 broadcast join             |
| 读取倾斜（大文件）      | 分片读取             | 拆分大文件为均匀 split                    |

### 两阶段聚合示例（Spark SQL）

```sql
-- Before：直接聚合（Key=X 的数据全堆到一个 reducer）
SELECT key, SUM(value) FROM t GROUP BY key;

-- After：两阶段（Spark AQE 可自动处理，也可手动加盐）
SELECT key, SUM(partial_sum) FROM (
  SELECT key, SUM(value) AS partial_sum
  FROM t
  GROUP BY key, (RAND() * 100)::INT  -- 局部聚合分散到100个桶
) GROUP BY key;
```

> 💡 OmniOperator 中：检查 Agg 算子是否已实现局部聚合（partial agg）路径，倾斜场景下是否正确触发。
