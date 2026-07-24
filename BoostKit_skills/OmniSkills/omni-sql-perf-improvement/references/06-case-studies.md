# 参考：性能调优案例拆解（课程案例扩展版）

> Agent trigger：不知道先改哪里，或需要“先证据后改动”的可复用套路。
>
> Agent deliverable：按“现象 -> 证据 -> 假设 -> 改动 -> 验证”输出可复盘案例。

---

## 案例1：Spark-extension（Shuffle 分区回退）

### 1) 现象
- SQL11 中 Omni 比 Spark 原生慢 60+ 秒
- Spark 原生 Task 时延分布均匀；Omni 存在明显长尾 Task
- 版本整体上 SQL11 从落后 11.4% 变为提升 18.4%（回退后）

### 2) 关键证据
- Stage 级别指标：Omni 的最慢 Task 远高于中位数 Task
- 长尾集中在 `ShuffleExchange` 前后阶段
- 数据倾斜信号：分区间输入行数/字节差异明显

### 3) 推断链路
1. 长尾通常来自“分区不均匀”或“热点 key”
2. 问题出现在 Shuffle 阶段，优先怀疑分区 hash 逻辑
3. 若 Omni 的分区计算与 Spark 原生不同，可能触发额外倾斜

### 4) 优化动作
- 修改 `ColumnarShuffleExchangeExec`
- 针对 SQL11 的相关 ShuffleExchange，将分区 hash 计算回退为 Spark 原生方案

### 5) 为什么有效
- Spark 原生分区策略在大规模场景更稳定，分区均匀性风险更低
- 长尾任务减少后，Stage 完成时间由“最慢分区”决定的问题得到缓解

### 6) 验证要点（必做）
- 对比回退前后：P50/P90/P99 Task 时长
- 对比分区行数分布：最大分区 / 中位分区 比值
- 对比总耗时：Omni-Before / Omni-After / Native 三方

---

## 案例2：Native 算子（HashAggregation 内存访问优化）

### 1) 现象
- SQL65/78/97 慢于 Spark 原生
- HashAggregation CPU 占比高（65/97 达 50%）
- 火焰图中 `do_page_fault` 占比较高

### 2) 关键证据
- 火焰图：`do_page_fault` + 哈希表相关函数为热点
- 代码走读：哈希表 rehash 次数多、数据拷贝多

### 3) 优化方案1（容量与扩容策略）
- 调大哈希表初始容量
- 调整扩容方式，降低 rehash 频率

**效果1**
- SQL65 +10%，SQL97 +17%，SQL78 +10%
- 从“落后”转为“提升或持平”，但 SQL65 仍落后

### 4) 优化方案2（slot flag 结构拆分）
- 将“slot 是否空闲”的 flag 从 slot 结构体中移出
- 使用独立数组管理 flag，减少 `memset` 覆盖字节数

**效果2**
- `do_page_fault` 占比：13% → 1.3%
- SQL65 +15%，SQL97 +40%
- 相比 Spark 原生均有提升

### 5) 机制解释（核心认知）
- rehash 少：减少全表搬迁与随机内存访问
- flag 拆分：减少无效内存写，提升缓存局部性
- page fault 降低：内存访问模式更连续、更可预测

### 6) 可复用检查项
- 哈希表初始容量是否可按基数估计
- 扩容阈值和增长倍率是否过于激进
- 热路径是否存在“大块 memset + 稀疏访问”

---

## 案例3：执行计划优化（Left Semi Join 右表预去重）

### 1) 现象
- SQL14a/14b 包含 `left semi join`
- 右表规模 10 亿级，Join 前后耗时高

### 2) 关键语义
- Left Semi Join 只输出左表
- 右表只用于“是否存在”判断
- 右表重复 key 对语义无增益，但会增加 Shuffle/Join 成本

### 3) 优化动作
- 在右表 Shuffle 前增加 HashAggregation 去重
- 本质是先 `DISTINCT right_key` 再参与 semi join

### 4) 为什么有效
- 减少右表参与 Shuffle 的数据量
- 降低 Join 构建与探测成本
- 对“重复度高的右表”收益显著

### 5) 优化效果
- SQL14a/14b 提升 20%+
- 相比之前 Omni 版本提升 13%+
- 相比 Spark 提升 30%

### 6) 适用边界
- 适用：右表重复 key 比例高、semi/anti join 语义
- 谨慎：右表本身已唯一、去重代价高于收益时

---

## 案例4：SortAgg 流式聚合热路径优化（两步法）

**算子：** `OmniSortAggregateExecTransformer`
**数据：** TPC-DS SF100 `store_sales`（~288M 行），GROUP BY `ss_store_sk`
**SQL：** `SELECT ss_store_sk, collect_set(ss_item_sk), count(*), sum(ss_sales_price) FROM store_sales GROUP BY ss_store_sk`

### 1) 现象
- Omni 热跑 ~0.054 min，Native 热跑 0.017 min，latency_ratio ≈ **3.2**
- 火焰图：`ProcessGroup`/`AccumulateRow` 占主体（>60%）

### 2) 优化 1：批次区间 ProcessGroup（commit `17cf1cd2`）

**根因：** `AddInput` 对每行独立调用 `ProcessGroup(state, batch, row, 1)`，
288M 行 = 288M 次函数调用，函数栈开销压过聚合计算本身。

**改动：** 检测同 key 的连续 run，将整段 run `[runStart, row)` 一次调用：
```cpp
// Before：逐行调用
AccumulateRow(projBatch, row);   // ProcessGroup × 288M

// After：run-range 批次调用
agg->ProcessGroup(stateBuffer_.get(), projBatch, runStart, row - runStart);
// ProcessGroup 从 288M 次 → ~70k 次（4000× 减少）
```

**阶段 1 结果：** 热跑 0.054 → **0.026 min**，ratio 3.2 → **≈ 1.53**

### 3) 优化 2：SerializeKey → KeysEqual 零分配比较（commit `bcfd43e8`）

**根因（优化 1 后新浮现）：** key 变化检测路径 `SerializeKey` 每行构造 `std::string`，
288M 行 = 288M 次堆分配，在高并发下触发 allocator 竞争。

**改动：** 用直接类型化比较替换 string 序列化，零堆分配，遇第一个不等列即短路：
```cpp
// Before：每行 string 堆分配
std::string currKey = SerializeKey(projBatch, groupByNum_, row);
if (currKey != lastKeyStr_) { ... }

// After：零分配，按列类型 switch 直接比较
if (!KeysEqual(projBatch, row, lastKeyBatch_, groupByNum_)) { ... }
// KeysEqual：for each col → switch(typeId) → compare raw value → short-circuit
```

**阶段 2 结果：** 消除 288M string malloc；热跑在测量误差范围内（0.026 → 0.028 min，noise），
ratio 维持 **≈ 1.65**；内存压力收益在更大数据量/高并发场景更显著。

### 4) 可复用检查项

| 检查项 | 触发条件 |
|--------|---------|
| 流式聚合/排序类算子是否逐行调用 `ProcessGroup` | 火焰图 `ProcessGroup` 占比 >30% |
| key 比较路径是否有 string 序列化/堆分配 | 火焰图出现 `std::string` 构造、`malloc`/`free` 热点 |
| 是否可利用"已排序"语义将逐行调用合并为区间调用 | 算子输入保证按 key 排序（SortAgg/StreamAgg） |
| 零分配比较是否可按类型 switch + 短路实现 | group-by key 列类型有限（INT/LONG/VARCHAR 等） |

### 5) 报告结构要求（本案例示范）

优化报告必须按阶段记录，不能只写最终结果：
```
基线（Before）→ 优化 1 改动 + 阶段 1 ratio → 优化 2 改动 + 阶段 2 ratio → 总结
```

---

## 四个案例的统一方法（可直接套用）

1. **先看现象**：慢在哪个 Stage/算子，是长尾还是平均慢
2. **再抓证据**：History + 火焰图 + 数据特征
3. **最后改最小闭环**：优先做“低风险、可回退”改动
4. **三方验证**：Before / After / Native，不做单点对比
5. **沉淀可复用规则**：把一次优化提炼成下次的检查项
