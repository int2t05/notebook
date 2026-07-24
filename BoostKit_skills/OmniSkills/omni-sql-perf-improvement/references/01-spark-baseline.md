# 参考：建立 Spark 原生性能基线

> Agent trigger：开始任何优化任务前，且当前任务没有可比较基线。
>
> Agent deliverable：产出可复现的 `Native vs Omni-Before` 基线表，作为后续验收锚点。

## 1. 测试环境准备

### 关闭 Omni 后端（跑原生基线时）
```properties
# spark-defaults.conf 或提交参数
spark.plugins=                          # 去掉 GlutenPlugin
spark.gluten.enabled=false              # 或直接禁用
```

### 开启 Omni 后端（跑 Omni 基线时）
```properties
spark.plugins=io.glutenproject.GlutenPlugin
spark.gluten.enabled=true
```

### 测试数据建议
| 场景         | 数据量建议     | 说明                         |
|-------------|--------------|------------------------------|
| 功能验证     | 100MB~1GB    | 快速迭代                     |
| 性能基线     | 10GB~100GB   | 接近生产规模                 |
| 倾斜测试     | 自定义分布    | 某列 Top Key 占比 > 30%      |
| 类型覆盖     | 含全类型列    | int/bigint/string/decimal/ts |

---

## 2. 关键指标采集

### Spark History Server（使用\scripts\spark_stage_details脚本）

重点关注列：
- **Duration**：Task 总耗时
- **GC Time**：GC 占比（> 20% 说明内存压力）
- **Shuffle Read / Write**：数据量是否合理
- **Spill（Memory/Disk）**：有 Spill 说明内存不足

---

## 3. 对比记录模板

| 指标               | Spark 原生  | Omni       | 差距比         |
|--------------------|------------|------------|----------------|
| Stage 总耗时 (s)   | ___        | ___        | Omni/Native=_× |
| CPU 时间 (s)       | ___        | ___        | ___            |
| GC 时间 (s)        | ___        | ___        | ___            |
| Shuffle Write (GB) | ___        | ___        | ___            |
| Spill (GB)         | ___        | ___        | ___            |
| Peak Memory (GB)   | ___        | ___        | ___            |

**优化目标锚点：** 使 Omni 在主要指标上 ≤ Spark 原生的 1.1×，或达到预设 SLA。

---

## 4. 常见基线陷阱

| 陷阱                   | 避免方法                                  |
|------------------------|------------------------------------------|
| 第一次运行含 JIT 预热   | 每个配置跑 3 次，取第 2、3 次均值          |
| 数据缓存影响            | 每次测试前 `spark.catalog.clearCache()`  |
| AQE 导致分区数变化      | 对比时固定 `spark.sql.shuffle.partitions` |
| Executor 资源不同       | 保持两次测试的 core/memory 配置完全一致   |
