# 参考：鲲鹏硬件背景与软件亲和性（Omni 算子优化）

> Agent trigger：任务运行在鲲鹏/ARM64，或同一 SQL 在 x86 与 ARM64 收益差异明显。
>
> Agent deliverable：把硬件约束转成实现与验证动作（布局、并发、分区、回退）。

---

## 1) 鲲鹏相关硬件事实（对算子优化有直接影响）

1. ARM64 架构 + SIMD（NEON）
   - 鲲鹏平台基于 ARM64（AArch64）生态，向量化路径通常依赖 NEON。
   - 对 Omni 算子意味着：批处理、列式布局、连续访问更容易兑现 SIMD 收益。

2. 多核并行 + NUMA/内存局部性敏感
   - 大规模并发时，跨 NUMA 节点访存会放大延迟与带宽抖动。
   - 对 Omni 算子意味着：线程绑核、内存本地化、减少跨节点共享写非常关键。

3. 内存与缓存层级对访问模式敏感
   - 随机访问、频繁 rehash、全表 memset 往往更容易触发 page fault 与缓存失配。
   - 对 Omni 算子意味着：优先“索引移动而非数据搬运”、降低大块无效写。

> 说明：不同鲲鹏型号核数/缓存/频率存在差异，优化时以“访问模式与并发模型”优先，而非硬编码某个规格数值。

---

## 2) 软件亲和性要求（从“可跑”到“跑得快”）

### 2.1 数据与执行模型
- 列式优先：算子间尽量维持列式/向量化批处理，减少行列来回转换。
- 零拷贝优先：跨模块传递优先共享内存视图，避免反复序列化/反序列化。
- 热路径特化：针对高频类型（int64/string/decimal）做专用路径，减少分支。

### 2.2 并发与内存模型
- 减少跨线程共享写：共享计数器、全局锁、全局 freelist 都是常见瓶颈。
- 结构分离（SoA）优先：将 flag/状态与 payload 拆分，提升缓存友好性。
- 预估容量：哈希结构按基数预分配，减少 rehash 与迁移。

### 2.3 Spark/Omni 集成侧
- 对 Shuffle 重路径，优先确认是否启用 OmniShuffle/OCK 相关能力与依赖库。
- 对执行计划，优先让“减量操作”前置（TopN、半连接右表去重、谓词下推）。

---

## 3) 鲲鹏场景下的算子设计检查单（固定流程）

### Step A：确认环境（先排除配置问题）
- 运行架构是否为 `aarch64`
- Shuffle 管理器与 OCK 相关参数是否按发布文档配置
- Spark 与插件版本是否匹配（避免“有功能但没生效”）

### Step B：确认瓶颈类型（先证据后改代码）
- History 看 Stage/Task 分布：是否长尾、是否倾斜
- 火焰图看热点：On-CPU 还是 Off-CPU（等待/锁/IO）
- 指标联动看内存：GC、Spill、page fault 是否共振

### Step C：按硬件亲和改造（小步快跑）
- Shuffle 倾斜：先保守回退到更稳定分区策略，再评估自定义 hash
- HashAgg 热点：先改容量与布局（rehash、flag 分离、连续数组）
- Join 冗余：先做右表去重/前置过滤，减少后续搬运与探测

### Step D：三方验证（必须）
- `Native vs Omni-Before vs Omni-After`
- 同数据、同资源、同参数，至少 3 次取均值
- 输出收益 + 适用边界 + 回退条件

---

## 4) 鲲鹏常见“高收益低风险”改动

1. 索引排序替代数据排序
   - 排序时交换索引，避免大对象搬移。
2. 哈希表 flag 拆分
   - 降低 memset 字节数，提升局部性。
3. 半连接右表预去重
   - 先减量再 Shuffle/Join。
4. 分区策略保守化
   - 对异常长尾 SQL，优先回退稳定分区算法验证假设。

---

## 5) 何时优先查本文件

- 同一 SQL 在 x86 正常、在鲲鹏明显变慢
- 火焰图热点集中在内存访问或锁等待
- 已做常规 Spark 参数调优但收益有限

---

## 6) 参考来源（权威与可追溯）

- 鲲鹏 BoostKit OmniShuffle 配置文档（hikunpeng）
  - https://www.hikunpeng.com/doc_center/source/zh/kunpengboostkithistory/230RC5/bds/kunpengbds_omniruntime_20_0144.html
- Spark SQL Performance Tuning（Apache Spark 官方）
  - https://spark.apache.org/docs/3.5.2/sql-performance-tuning.html
- Spark Monitoring and Instrumentation（Apache Spark 官方）
  - https://spark.apache.org/docs/3.5.7/monitoring.html
- Spark Flame Graph Support PR（Apache Spark）
  - https://github.com/apache/spark/pull/42988
- Flink 火焰图说明（用于补充 On-CPU/Off-CPU 概念）
  - https://nightlies.apache.org/flink/flink-docs-stable/zh/docs/ops/debugging/flame_graphs/
