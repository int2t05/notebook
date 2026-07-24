# 参考：性能画像采集指南

> Agent trigger：已有基线，但无法解释“为什么慢”。
>
> Agent deliverable：输出火焰图证据 + 数据特征摘要，可直接进入瓶颈判定。

## 1. CPU 火焰图采集

### 方式一：async-profiler（调用run-test-all工具）

或者 

```bash
# 找到 Executor PID
jps | grep CoarseGrainedExecutorBackend

# 采集 30 秒 CPU 火焰图（同时捕获 JVM + C++ native 栈）
./asprof -d 30 -e cpu -f /tmp/flamegraph.html <PID>

# 查看：用浏览器打开 /tmp/flamegraph.html
```

> ⚠️ 采集时机：在算子压力最大的阶段（Stage 运行中段）开始采集，避免采到冷启动。

### 方式二：Spark UI 内置（粗粒度，快速上手）
Spark History Server → Application → Stages → 点击某个 Stage → **Event Timeline**
可以直观看到 Task 在 Executor 上的 CPU / Shuffle / GC 时间分布。

---

## 2. 火焰图阅读方法

```
宽度 = 函数占 CPU 时间的比例（越宽越热）
高度 = 调用栈深度（栈顶是实际执行函数）
颜色 = 通常无特殊含义（橙=Java，绿=C++）
```

**读图步骤：**
1. 找**最宽的平台**（平顶函数）→ 即 CPU 热点
2. 看热点函数的**调用链**（向下溯源）→ 找触发路径
3. 判断热点是**"本该在这里"**还是**"不应该在这里"**

---

## 3. 数据特征采集

在 Spark SQL 中执行（替换 `your_table` 和列名）：

```sql
-- null 比例
SELECT
  COUNT(*) AS total,
  COUNT(col_a) AS non_null_a,
  ROUND(1.0 - COUNT(col_a) / COUNT(*), 4) AS null_ratio_a
FROM your_table;

-- 字典率（distinct 值占比，< 5% 认为高字典化）
SELECT
  COUNT(DISTINCT col_a) AS distinct_a,
  COUNT(*) AS total,
  ROUND(COUNT(DISTINCT col_a) * 1.0 / COUNT(*), 4) AS dict_ratio_a
FROM your_table;

-- 数据分布（倾斜检测，Top Key 占比 > 30% 视为倾斜）
SELECT col_a, COUNT(*) AS cnt
FROM your_table
GROUP BY col_a
ORDER BY cnt DESC
LIMIT 10;
```

### 特征摘要模板（填写后传入 Phase 3）

| 列名   | 数据类型 | 行数规模 | null 比例 | 字典率 | 是否倾斜 |
|--------|----------|----------|-----------|--------|----------|
| col_a  | string   | 1亿      | 25%       | 0.1%   | 是（Top1=40%） |
| col_b  | int      | 1亿      | 0%        | —      | 否       |

---

## 4. 内存与 GC 采集（按需）

```bash
# 采集 GC 日志（提交时加 JVM 参数）
--conf spark.executor.extraJavaOptions="-Xlog:gc*:file=/tmp/gc.log:time,uptime:filecount=3,filesize=10m"

# 快速看 GC 频率
grep "Pause Full" /tmp/gc.log | wc -l   # Full GC 次数
grep "Pause Young" /tmp/gc.log | tail -5 # 最近几次 Minor GC 耗时
```

触发时机：Spark UI 显示 **GC Time > 20%** 时才需要深入分析。
