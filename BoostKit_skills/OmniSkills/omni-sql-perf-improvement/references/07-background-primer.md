# 参考：必备背景知识（调优前 10 分钟速读）

> Agent trigger：日志和火焰图都有，但你不确定术语含义与指标解读。
>
> Agent deliverable：把术语映射成可执行判断条件，再回到主流程推进。

---

## 1) Shuffle 是什么，为什么会慢

### 定义
Shuffle 是“按 key 重新分区并跨节点重分发数据”的过程，包含：
- Shuffle Write：上游 Task 按分区规则落盘
- Shuffle Read：下游 Task 拉取属于自己分区的数据

### 性能影响路径
- **分区不均匀**：少数分区过大，形成长尾 Task
- **网络开销大**：跨节点拉取字节数过高
- **落盘/反序列化开销**：读写与编解码成本上升

### 快速判断
- Stage 中最慢 Task 明显高于中位 Task（例如 > 3x）
- Shuffle Read/Write 字节很高，且分区分布不均

---

## 2) HashAggregation 为什么常成热点

### 定义
HashAggregation 用哈希表实现 `GROUP BY` 聚合：
- key：分组列
- value：聚合状态（sum/count/min/max 等）

### 常见慢点
- **rehash 频繁**：容量不足导致全表搬迁
- **内存访问离散**：缓存命中率低，page fault 增加
- **对象/缓冲分配过多**：GC 与分配成本上升

### 快速判断
- 火焰图中哈希表函数与 `do_page_fault` 占比高
- GC 或内存分配热点伴随出现

---

## 3) Left Semi Join 的语义与优化空间

### 语义
`left semi join` 只保留左表中“在右表存在匹配”的行：
- 输出仅包含左表列
- 右表用于存在性判断，不需要重复 key 的全部行

### 关键推论
如果右表重复 key 很多，先对右表按 join key 去重，通常可减少：
- 右表 Shuffle 数据量
- Join 构建与探测成本

### 快速判断
- 右表行数很大且重复度高
- Join 类型为 semi/anti，右表不参与输出

---

## 4) 你需要的 5 个核心指标

| 指标 | 含义 | 何时告警 |
|------|------|----------|
| Stage Duration | 阶段总耗时 | 与 Native 差距持续 > 10% |
| Task 分位时长（P50/P99） | 长尾程度 | P99 / P50 > 3 |
| Shuffle Read/Write | 重分发成本 | 同 SQL 下显著高于 Native |
| GC Time | 内存压力 | 占 Task Duration > 20% |
| Page Fault 热点占比 | 内存访问模式问题 | `do_page_fault` 进入 TOP 热点 |

---

## 5) 一句话方法论

- **Shuffle 慢**：先看分区均匀性与长尾
- **HashAgg 慢**：先看 rehash、内存布局、page fault
- **Semi Join 慢**：先看右表是否可预去重

如果你已经掌握以上概念，直接回到 `skill.md` 按四阶段执行即可。
