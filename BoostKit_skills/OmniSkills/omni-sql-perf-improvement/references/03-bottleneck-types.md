# 参考：瓶颈类型详细分析

> Agent trigger：拿到火焰图/指标后，需要把“现象”落到单一主瓶颈。
>
> Agent deliverable：`主瓶颈 + 证据 + 下一步策略文件章节`。

## §计算 — 计算效率低

**确认条件**
- 火焰图：纯计算函数（表达式求值、类型转换、数学运算）占比 > 50%
- CPU 使用率高，但无明显 IO 或 GC 问题

**细化排查**
1. 热点函数是否有可替代的高效实现（SIMD 版本、向量化库）？
2. 循环内是否存在重复计算（不变量外提）？
3. 是否有 O(n²) 或更高复杂度的嵌套循环？
4. 函数调用是否过深（virtual dispatch 开销）？

**结论输出**：锁定热点函数名 + 计算复杂度评估 → 带入 `04-optimization-patterns.md §计算`

---

## §内存 — 内存压力

**确认条件**
- Spark UI：GC Time > 20% of Task Duration
- 火焰图：`malloc` / `new` / `AllocateHeap` 等内存分配函数占比高
- 有 Spill 记录（Memory Spill > 0）

**细化排查**
1. 是否频繁创建临时对象（每行一个对象实例）？
2. 缓冲区大小是否合理（过小导致频繁扩容，过大导致浪费）？
3. 是否存在数据从 off-heap 到 on-heap 的不必要拷贝？
4. 是否有内存泄漏（长期运行内存持续增长）？

**结论输出**：分配热点位置 + 对象生命周期分析 → 带入 `04-optimization-patterns.md §内存`

---

## §null — null 处理低效

**确认条件**
- 数据特征：某列 null 比例 > 20%
- 火焰图：null 检查分支（`isNull` / `checkNull`）出现在计算主路径上

**细化排查**
1. null 判断是否与实际计算混在同一循环，没有提前过滤？
2. 是否使用了位图（null bitmap）还是逐行存储 null 标志？
3. null 列的计算结果是否被后续算子直接丢弃（可以整列跳过）？

**结论输出**：null 位置（filter/join/agg 哪个阶段）+ 可提前过滤的比例 → 带入 `04-optimization-patterns.md §null`

---

## §字典 — 字典编码处理低效

**确认条件**
- 数据特征：列字典率（distinct/total）< 5%（高重复度）
- 火焰图：`decode` / `DictionaryVector` 等解码函数出现在主路径

**细化排查**
1. Filter/Join/Agg 操作是否在解码前还是解码后执行？（应在解码前）
2. 字典编码是否在算子内部被提前展开（lost compression）？
3. 对字典列做 GROUP BY / JOIN 时，是否利用了字典 ID 直接操作？

**结论输出**：编码保留情况 + 解码时机评估 → 带入 `04-optimization-patterns.md §字典`

---

## §倾斜 — 数据倾斜

**确认条件**
- Spark UI：Stage 内 Task 耗时分布极不均匀（最慢 Task > 平均 5×）
- 数据特征：Top Key 占比 > 30%

**细化排查**
1. 倾斜在哪个 Stage（Shuffle / Join / Agg）？
2. 热点 Key 是什么（空字符串、NULL、固定业务值）？
3. 是 Map 端倾斜（输入就倾斜）还是 Reduce 端倾斜（Shuffle 后倾斜）？

**结论输出**：倾斜 Key 分布 + 倾斜阶段 → 带入 `04-optimization-patterns.md §倾斜`

---

## §锁 — 锁竞争

**确认条件**
- 线程 dump：大量线程处于 `BLOCKED` 状态
- perf / async-profiler：`pthread_mutex_lock` / `futex` 等同步原语占比高
- CPU 利用率低但耗时高（等待为主）

**细化排查**
1. 竞争的锁保护的是什么资源（全局缓存 / 共享计数器 / 内存池）？
2. 是否可以改为无锁结构（CAS / thread-local 副本）？
3. 锁的粒度是否可以细化（行级 → 列级，全局 → 分片）？

**结论输出**：竞争锁的名称 + 持有/等待比例 → 带入 `04-optimization-patterns.md §锁`（如需添加）

---

## §DRAM带宽 — DRAM 带宽饱和

**确认条件**（同时满足以下三条）
- 火焰图：reader / scan 类函数（如 `omniruntime::reader`、`OrcColumnReader`、`DFSInputStream`）占比 **> 15%**
- 多轮 SIMD / 快速路径优化后，该占比**基本不变**（变化 < 2% 绝对值）
- 数据量巨大（全表扫描，无运行时过滤器），行数 > 10 亿

**根本原因**

ORC 解码属于顺序 DRAM 读取密集型工作：每行数据都需要从内存读到 CPU。当数据集超出末级 Cache（LLC），CPU 处于等待 DRAM 的状态（memory stall），而非算术运算瓶颈。此时：
- 优化解码函数的 CPU 指令数 → **无效**：减少的指令数抵不过 DRAM 读取延迟
- SVE 向量化解码 → **无效**：吞吐提升被内存等待抵消
- 快速路径消除函数调用开销 → **无效**：开销本质上是 DRAM 指针 stall，而非函数调用

**可优化性**：极低（C++ 层无法减少 DRAM 访问量）

**唯一有效方向**：减少从 DRAM 读取的数据量，例如：
1. **运行时过滤器**：在 ORC scan 层注入 Bloom Filter（合法 join key 集合），跳过不匹配的 stripe
2. **分区裁剪（DPP）**：恢复 BroadcastHashJoin，让 DPP 生效，跳过 99%+ 的 stripe
3. **切换查询**：转向 reader 占比 < 10%、计算算子（HashAgg/Join）占比 > 60% 的查询

**特殊陷阱：`forceShuffledHashJoin=true` 导致结构性 DRAM 瓶颈**

`forceShuffledHashJoin=true` 禁用 Dynamic Partition Pruning（DPP）。DPP 在正常 BroadcastHashJoin 下将 date_dim 过滤后的 date_sk 集合作为运行时过滤器推入 ORC scan，可跳过 99.5% 的 store_sales stripe（数据量减少约 200×）。ShuffledHashJoin 迫使全量 scan，reader 将**永久**成为主瓶颈，C++ 侧无解。

**结论输出**：确认为 DRAM 带宽瓶颈后，**直接建议切换查询或调整 Spark Plan 层策略**，不再继续 C++ 层优化迭代。
