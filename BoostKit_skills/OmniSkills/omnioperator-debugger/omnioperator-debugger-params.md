# OmniOperator 列式算子参数参考

## 列式算子 Enable 参数

### 扫描相关算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_BATCHSCAN_ENABLED | spark.gluten.sql.columnar.batchscan | true | 列式批扫描 | 可选尝试 |
| COLUMNAR_FILESCAN_ENABLED | spark.gluten.sql.columnar.filescan | true | 列式文件扫描 | 必须尝试 |
| COLUMNAR_HIVETABLESCAN_ENABLED | spark.gluten.sql.columnar.hivetablescan | true | 列式 Hive 表扫描 | 可选尝试 |
| COLUMNAR_HIVETABLESCAN_NESTED_COLUMN_PRUNING_ENABLED | spark.gluten.sql.columnar.enableNestedColumnPruningInHiveTableScan | true | Hive 表扫描嵌套列裁剪 | 可选尝试 |
| VANILLA_VECTORIZED_READERS_ENABLED | spark.gluten.sql.columnar.enableVanillaVectorizedReaders | true | 原生向量化扫描 | 可选尝试 |

### 聚合相关算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_HASHAGG_ENABLED | spark.gluten.sql.columnar.hashagg | true | 列式哈希聚合 | 必须尝试 |
| COLUMNAR_FORCE_HASHAGG_ENABLED | spark.gluten.sql.columnar.force.hashagg | true | 强制使用哈希聚合 | 可选尝试 |
| MERGE_TWO_PHASES_ENABLED | spark.gluten.sql.mergeTwoPhasesAggregate.enabled | true | 合并两阶段聚合 | 可选尝试 |
| VELOX_FLUSHABLE_PARTIAL_AGGREGATION_ENABLED | spark.gluten.sql.columnar.backend.velox.flushablePartialAggregation | true | Velox 可刷新部分聚合 | 可选尝试 |
| ENABLE_ADAPTIVE_PARTIAL_AGGREGATION | spark.gluten.sql.columnar.backend.omni.adaptivePartialAggregation.enabled | true | Omni 自适应部分聚合 | 可选尝试 |

### 投影和过滤算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_PROJECT_ENABLED | spark.gluten.sql.columnar.project | true | 列式投影 | 必须尝试 |
| COLUMNAR_FILTER_ENABLED | spark.gluten.sql.columnar.filter | true | 列式过滤 | 必须尝试 |
| ENABLE_COLUMNAR_PROJECT_COLLAPSE | spark.gluten.sql.columnar.project.collapse | true | 列式投影合并 | 可选尝试 |
| ENABLE_COLUMNAR_PARTIAL_PROJECT | spark.gluten.sql.columnar.partial.project | true | 列式部分投影 | 可选尝试 |
| COMBINE_PROJECT_FILTER_ENABLED | spark.gluten.sql.columnar.backend.omni.combineProjectFilter | true | 合并投影和过滤 | 可选尝试 |

### 排序和窗口算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_SORT_ENABLED | spark.gluten.sql.columnar.sort | true | 列式排序 | 必须尝试 |
| COLUMNAR_WINDOW_ENABLED | spark.gluten.sql.columnar.window | true | 列式窗口函数 | 必须尝试 |
| COLUMNAR_WINDOW_GROUP_LIMIT_ENABLED | spark.gluten.sql.columnar.window.group.limit | true | 列式窗口分组限制 | 可选尝试 |
| ENABLE_COLUMNAR_TOP_N_SORT | spark.gluten.sql.columnar.backend.omni.topNSort | true | 列式 TopN 排序 | 可选尝试 |

### 连接算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_SHUFFLED_HASH_JOIN_ENABLED | spark.gluten.sql.columnar.shuffledHashJoin | true | 列式 Shuffle 哈希连接 | 必须尝试 |
| COLUMNAR_SHUFFLED_HASH_JOIN_OPTIMIZE_BUILD_SIDE | spark.gluten.sql.columnar.shuffledHashJoin.optimizeBuildSide | true | 优化哈希连接构建侧 | 可选尝试 |
| COLUMNAR_FORCE_SHUFFLED_HASH_JOIN_ENABLED | spark.gluten.sql.columnar.forceShuffledHashJoin | true | 强制使用 Shuffle 哈希连接 | 优先尝试 |
| COLUMNAR_SORTMERGEJOIN_ENABLED | spark.gluten.sql.columnar.sortMergeJoin | true | 列式排序合并连接 | 必须尝试 |
| COLUMNAR_BROADCAST_JOIN_ENABLED | spark.gluten.sql.columnar.broadcastJoin | true | 列式广播连接 | 必须尝试 |
| COLUMNAR_OMNI_PREFER_SHUFFLED_HASH_JOIN | spark.gluten.sql.columnar.backend.omni.preferShuffledHashJoin | false | 优先使用 Shuffle 哈希连接 | 可选尝试 |
| ENABLE_JOIN_REORDER_ENHANCE | spark.gluten.sql.columnar.backend.omni.joinReorderEnhance | true | 连接重排序增强 | 可选尝试 |
| ENABLE_DEDUP_LEFT_SEMI_JOIN | spark.gluten.sql.columnar.backend.omni.dedupLeftSemiJoin | false | 左半连接去重 | 可选尝试 |

### 其他算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| COLUMNAR_COLUMNAR_TO_ROW_ENABLED | spark.gluten.sql.columnar.columnarToRow | true | 列式转行 | 必须尝试 |
| COLUMNAR_UNION_ENABLED | spark.gluten.sql.columnar.union | true | 列式 Union | 必须尝试 |
| NATIVE_UNION_ENABLED | spark.gluten.sql.native.union | false | 原生 Union | 可选尝试 |
| COLUMNAR_EXPAND_ENABLED | spark.gluten.sql.columnar.expand | true | 列式 Expand | 必须尝试 |
| COLUMNAR_BROADCAST_EXCHANGE_ENABLED | spark.gluten.sql.columnar.broadcastExchange | true | 列式广播交换 | 必须尝试 |
| COLUMNAR_COALESCE_ENABLED | spark.gluten.sql.columnar.coalesce | true | 列式 Coalesce | 可选尝试 |
| COLUMNAR_LIMIT_ENABLED | spark.gluten.sql.columnar.limit | true | 列式 Limit | 可选尝试 |
| COLUMNAR_GENERATE_ENABLED | spark.gluten.sql.columnar.generate | true | 列式 Generate | 可选尝试 |
| COLUMNAR_TAKE_ORDERED_AND_PROJECT_ENABLED | spark.gluten.sql.columnar.takeOrderedAndProject | true | 列式 TakeOrderedAndProject | 可选尝试 |
| COLUMNAR_SAMPLE_ENABLED | spark.gluten.sql.columnarSampleEnabled | false | 列式采样 | 可选尝试 |
| COLUMNAR_ARROW_UDF_ENABLED | spark.gluten.sql.columnar.arrowUdf | true | 列式 Arrow UDF | 可选尝试 |
| CARTESIAN_PRODUCT_TRANSFORMER_ENABLED | spark.gluten.sql.cartesianProductTransformerEnabled | true | 笛卡尔积转换器 | 可选尝试 |
| BROADCAST_NESTED_LOOP_JOIN_TRANSFORMER_ENABLED | spark.gluten.sql.broadcastNestedLoopJoinTransformerEnabled | true | 广播嵌套循环连接转换器 | 可选尝试 |

### Omni 特定算子

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| ENABLE_OMNI_EXP_CHECK | spark.gluten.sql.columnar.backend.omni.omniExpCheck | true | Omni 表达式检查 | 可选尝试 |
| ENABLE_OMNI_UNIXTIME_FUNCTION | spark.gluten.sql.columnar.backend.omni.unixTimeFunc.enabled | true | Omni Unix 时间函数 | 可选尝试 |
| ENABLE_SHARE_BROADCAST_JOIN_HASH_TABLE | spark.gluten.sql.columnar.backend.omni.broadcastJoin.sharehashtable | true | 共享广播连接哈希表 | 可选尝试 |
| ENABLE_SHARE_BROADCAST_JOIN_NESTED_TABLE | spark.gluten.sql.columnar.backend.omni.broadcastNestedJoin.shareBuildTable | true | 共享广播嵌套连接构建表 | 可选尝试 |
| ENABLE_REWRITE_SELF_JOIN_IN_IN_PREDICATE | spark.gluten.sql.columnar.backend.omni.rewriteSelfJoinInInPredicate | false | 重写 IN 谓词中的自连接 | 可选尝试 |
| ENABLE_OMNI_ROW_SHUFFLE | spark.gluten.sql.columnar.backend.omni.rowShuffle.enabled | true | Omni 行 Shuffle | 可选尝试 |
| COLUMNAR_OMNI_ENABLE_VEC_PREDICATE_FILTER | spark.gluten.sql.columnar.backend.omni.vec.predicate.enabled | true | 向量化谓词过滤 | 可选尝试 |
| COLUMNAR_OMNI_ENABLE_DELAY_CARTESIAN_PRODUCT | spark.gluten.sql.columnar.backend.omni.enableDelayCartesianProduct.enabled | true | 延迟笛卡尔积 | 可选尝试 |
| ENABLE_ROLLUP_OPTIMIZATION | spark.gluten.sql.columnar.backend.omni.rollupOptimization.enabled | true | Rollup 优化 | 可选尝试 |

### 优化规则

| 参数名 | 配置键 | 默认值 | 说明 | 优先级 |
|--------|--------|--------|------|--------|
| ENABLE_REWRITE_DATE_TIMESTAMP_COMPARISON | spark.gluten.sql.rewrite.dateTimestampComparison | true | 重写日期时间戳比较 | 可选尝试 |
| ENABLE_COLLAPSE_GET_JSON_OBJECT | spark.gluten.sql.collapseGetJsonObject.enabled | false | 折叠 get_json_object | 可选尝试 |
| ENABLE_CH_REWRITE_DATE_CONVERSION | spark.gluten.sql.columnar.backend.ch.rewrite.dateConversion | true | CH 后端重写日期转换 | 可选尝试 |
| ENABLE_COMMON_SUBEXPRESSION_ELIMINATE | spark.gluten.sql.commonSubexpressionEliminate | true | 公共子表达式消除 | 可选尝试 |
| ENABLE_COUNT_DISTINCT_WITHOUT_EXPAND | spark.gluten.sql.countDistinctWithoutExpand | false | 不使用 Expand 的 Count Distinct | 可选尝试 |
| ENABLE_EXTENDED_COLUMN_PRUNING | spark.gluten.sql.extendedColumnPruning.enabled | true | 扩展列裁剪 | 可选尝试 |
| COMBINE_JOINED_AGGREGATES_ENABLED | spark.gluten.sql.columnar.backend.omni.combineJoinedAggregates | false | 合并连接的聚合 | 可选尝试 |
| FILTER_MERGE_ENABLE | spark.gluten.sql.columnar.backend.omni.filterMerge | false | 过滤合并 | 可选尝试 |
| PUSH_ORDERED_LIMIT_THROUGH_AGG_ENABLE | spark.gluten.sql.columnar.backend.omni.pushOrderedLimitThroughAggEnable | false | 将有序 Limit 推过聚合 | 可选尝试 |

## 物理计划中的列式算子标识

- `ScanTransformer` - 列式扫描
- `OmniBroadcastHashJoinExecTransformer` - Omni 列式广播哈希连接
- `OmniHashAggregateExecTransformer` - Omni 列式哈希聚合
- `OmniAdaptiveHashAggregateExecTransformer` - Omni 自适应哈希聚合
- `OmniColumnarShuffleExchange` - Omni 列式 Shuffle 交换
- `OmniAQEShuffleRead` - Omni AQE Shuffle 读取
- `ProjectExecTransformer` - 列式投影
- `TakeOrderedAndProjectExecTransformer` - 列式排序和投影
- `OmniColumnarToRow` - Omni 列式转行
- `ColumnarBroadcastExchange` - 列式广播交换

## 常用 SET 语句示例

```sql
-- 关闭聚合相关算子
SET spark.gluten.sql.columnar.backend.omni.adaptivePartialAggregation=false;
SET spark.gluten.sql.columnar.hashagg=false;
SET spark.gluten.sql.columnar.mergeTwoPhasesAggregate.enabled=false;

-- 关闭连接相关算子
SET spark.gluten.sql.columnar.broadcastJoin=false;
SET spark.gluten.sql.columnar.shuffledHashJoin=false;
SET spark.gluten.sql.columnar.sortMergeJoin=false;

-- 关闭排序和投影算子
SET spark.gluten.sql.columnar.sort=false;
SET spark.gluten.sql.columnar.project=false;
SET spark.gluten.sql.columnar.takeOrderedAndProject=false;

-- 关闭扫描算子
SET spark.gluten.sql.columnar.filescan=false;
SET spark.gluten.sql.columnar.enableVanillaVectorizedReaders=false;
```

## 获取物理计划

如果已经执行过测试，可以直接从日志目录获取 Application ID 和物理计划：

```bash
# 1. 从日志目录查找最新的测试报告
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && ls -lt perf_report_omni_*/ | head -1'

# 2. 从最新测试的日志中获取 Application ID
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && cat perf_report_omni_*/logs/<SQL_NAME>.log | grep "Application Id"'

# 3. 通过 Spark UI API 获取物理计划
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'curl -s "http://localhost:18080/api/v1/applications/<Application_ID>/sql"'
```

## 查看算子详细信息

```bash
# 获取特定算子的完整配置
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'curl -s "http://localhost:18080/api/v1/applications/<Application_ID>/sql" | python3 -c "
import sys, json
data = json.load(sys.stdin)
nodes = data.get(\"plan\", {}).get(\"nodes\", [])
for i, node in enumerate(nodes):
    name = node.get(\"nodeName\", \"\")
    if \"OmniBroadcastHashJoin\" in name:
        print(f\"节点 {i}: {name}\")
        print(f\"  左键：{node.get(\"leftKeys\", [])}\")
        print(f\"  右键：{node.get(\"rightKeys\", [])}\")
        print(f\"  连接类型：{node.get(\"joinType\", \"\")}\")
        print(f\"  构建侧：{node.get(\"buildSide\", \"\")}\")
        print()
"'
```

## 典型的算子链顺序

从后往前（数据流方向）：

1. `OmniColumnarToRow` - 列式转行
2. `TakeOrderedAndProjectExecTransformer` - 排序+LIMIT
3. `OmniHashAggregateExecTransformer` - 最终聚合
4. `OmniAQEShuffleRead` - AQE Shuffle 读取
5. `OmniColumnarShuffleExchange` - Shuffle
6. `OmniAdaptiveHashAggregateExecTransformer` - 局部聚合
7. `OmniBroadcastHashJoinExecTransformer` - 广播连接
8. `ScanTransformer` - 扫描

