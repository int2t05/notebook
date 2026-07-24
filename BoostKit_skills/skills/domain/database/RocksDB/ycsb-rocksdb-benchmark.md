---
name: "ycsb-rocksdb-benchmark"
description: "使用 YCSB 对 RocksDB 进行性能测试，遍历不同并发数和 workload a-f 场景。当用户需要对 RocksDB 执行 YCSB 基准测试、对比不同并发或负载下的性能时调用此 skill。"
---

# YCSB RocksDB Performance Benchmark

此 skill 用于使用 YCSB (Yahoo! Cloud Serving Benchmark) 对 RocksDB 进行系统性的性能测试，自动遍历指定的并发数列表和 workload a-f 六种场景，收集并汇总测试结果。

## 前置条件

1. 已安装 Java 运行环境 (JDK 8+)
2. 已安装 YCSB (推荐 0.17.0+)
3. 已编译 RocksDB 并构建 YCSB RocksDB binding
4. 确认 YCSB 的 RocksDB binding jar 包已放置在 YCSB 的 `rocksdb/bindings` 目录下

## YCSB Workload 说明

| Workload | 场景描述 | 读写比例 | 核心操作 |
|----------|---------|---------|---------|
| workloada | 读写均衡 | 50% Read / 50% Update | 读+更新 |
| workloadb | 读多写少 | 95% Read / 5% Update | 读为主 |
| workloadc | 只读 | 100% Read | 纯读 |
| workloadd | 读最近写入 | 95% Read / 5% Insert | 读+插入 |
| workloade | 扫描小区间 | 95% Scan / 5% Insert | 范围扫描+插入 |
| workloadf | 读写入均衡 | 50% Read / 50% Insert | 读+插入 |

## 测试脚本

以下脚本将自动遍历并发数和 workload 组合，执行完整的性能测试：

```bash
#!/bin/bash

YCSB_HOME=${YCSB_HOME:-"/opt/YCSB"}
ROCKSDB_DIR=${ROCKSDB_DIR:-"/opt/rocksdb"}
RECORDCOUNT=${RECORDCOUNT:-100000000}
OPERATIONCOUNT=${OPERATIONCOUNT:-100000000}
FIELD_COUNT=${FIELD_COUNT:-1}
READ_ALL_FIELDS=${READ_ALL_FIELDS:-false}
THREAD_LIST=${THREAD_LIST:-"1 4 8 16 32 64"}
WORKLOAD_LIST=${WORKLOAD_LIST:-"a b c d e f"}
RESULT_DIR=${RESULT_DIR:-"./ycsb_results_$(date +%Y%m%d_%H%M%S)"}

mkdir -p "$RESULT_DIR"

echo "========================================="
echo "YCSB RocksDB Performance Benchmark"
echo "========================================="
echo "YCSB_HOME:        $YCSB_HOME"
echo "ROCKSDB_DIR:      $ROCKSDB_DIR"
echo "RECORDCOUNT:      $RECORDCOUNT"
echo "OPERATIONCOUNT:   $OPERATIONCOUNT"
echo "FIELD_COUNT:      $FIELD_COUNT"
echo "READ_ALL_FIELDS:  $READ_ALL_FIELDS"
echo "THREAD_LIST:      $THREAD_LIST"
echo "WORKLOAD_LIST:    $WORKLOAD_LIST"
echo "RESULT_DIR:       $RESULT_DIR"
echo "========================================="

for wl in $WORKLOAD_LIST; do
    WORKLOAD_FILE="$YCSB_HOME/workloads/workload${wl}"

    if [ ! -f "$WORKLOAD_FILE" ]; then
        echo "[ERROR] Workload file not found: $WORKLOAD_FILE"
        continue
    fi

    echo ""
    echo "-----------------------------------------"
    echo "Processing workload${wl}"
    echo "-----------------------------------------"

    for threads in $THREAD_LIST; do
        TAG="workload${wl}_threads${threads}"
        LOAD_LOG="$RESULT_DIR/${TAG}_load.log"
        RUN_LOG="$RESULT_DIR/${TAG}_run.log"

        echo "[INFO] Loading data for $TAG ..."

        $YCSB_HOME/bin/ycsb load rocksdb \
            -P "$WORKLOAD_FILE" \
            -p rocksdb.dir="$ROCKSDB_DIR" \
            -p recordcount="$RECORDCOUNT" \
            -p operationcount="$OPERATIONCOUNT" \
            -p fieldcount="$FIELD_COUNT" \
            -p readallfields="$READ_ALL_FIELDS" \
            -threads "$threads" \
            -s > "$LOAD_LOG" 2>&1

        if [ $? -ne 0 ]; then
            echo "[ERROR] Load failed for $TAG, skipping run phase"
            continue
        fi

        echo "[INFO] Running benchmark for $TAG ..."

        $YCSB_HOME/bin/ycsb run rocksdb \
            -P "$WORKLOAD_FILE" \
            -p rocksdb.dir="$ROCKSDB_DIR" \
            -p recordcount="$RECORDCOUNT" \
            -p operationcount="$OPERATIONCOUNT" \
            -p fieldcount="$FIELD_COUNT" \
            -p readallfields="$READ_ALL_FIELDS" \
            -threads "$threads" \
            -s > "$RUN_LOG" 2>&1

        if [ $? -ne 0 ]; then
            echo "[ERROR] Run failed for $TAG"
            continue
        fi

        echo "[INFO] Completed $TAG"

        rm -rf "$ROCKSDB_DIR"/*
    done
done

echo ""
echo "========================================="
echo "All benchmarks completed. Results in: $RESULT_DIR"
echo "========================================="
```

## 结果解析脚本

测试完成后，使用以下脚本从日志中提取关键指标并生成汇总表：

```bash
#!/bin/bash

RESULT_DIR=${1:-"./ycsb_results"}

if [ ! -d "$RESULT_DIR" ]; then
    echo "Result directory not found: $RESULT_DIR"
    exit 1
fi

echo "Workload,Threads,Throughput(ops/sec),Runtime(ms),Read_AvgLatency(us),Read_95thLatency(us),Read_99thLatency(us),Update_AvgLatency(us),Update_95thLatency(us),Update_99thLatency(us),Insert_AvgLatency(us),Insert_95thLatency(us),Insert_99thLatency(us),Scan_AvgLatency(us),Scan_95thLatency(us),Scan_99thLatency(us)"

for log in $(ls "$RESULT_DIR"/*_run.log 2>/dev/null | sort); do
    TAG=$(basename "$log" _run.log)

    WORKLOAD=$(echo "$TAG" | sed 's/workload\([a-f]\)_threads.*/\1/')
    THREADS=$(echo "$TAG" | sed 's/.*_threads\([0-9]*\)/\1/')

    THROUGHPUT=$(grep '\[OVERALL\], Throughput(ops/sec)' "$log" | tail -1 | awk -F', ' '{print $3}')
    RUNTIME=$(grep '\[OVERALL\], RunTime(ms)' "$log" | tail -1 | awk -F', ' '{print $3}')

    READ_AVG=$(grep '\[READ\], AverageLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    READ_P95=$(grep '\[READ\], 95thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    READ_P99=$(grep '\[READ\], 99thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')

    UPDATE_AVG=$(grep '\[UPDATE\], AverageLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    UPDATE_P95=$(grep '\[UPDATE\], 95thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    UPDATE_P99=$(grep '\[UPDATE\], 99thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')

    INSERT_AVG=$(grep '\[INSERT\], AverageLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    INSERT_P95=$(grep '\[INSERT\], 95thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    INSERT_P99=$(grep '\[INSERT\], 99thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')

    SCAN_AVG=$(grep '\[SCAN\], AverageLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    SCAN_P95=$(grep '\[SCAN\], 95thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')
    SCAN_P99=$(grep '\[SCAN\], 99thPercentileLatency(us)' "$log" | tail -1 | awk -F', ' '{print $3}')

    echo "${WORKLOAD},${THREADS},${THROUGHPUT},${RUNTIME},${READ_AVG},${READ_P95},${READ_P99},${UPDATE_AVG},${UPDATE_P95},${UPDATE_P99},${INSERT_AVG},${INSERT_P95},${INSERT_P99},${SCAN_AVG},${SCAN_P95},${SCAN_P99}"
done
```

## 自定义 Workload 参数

可在运行时通过 `-p` 参数覆盖 workload 文件中的默认配置：

```bash
$YCSB_HOME/bin/ycsb run rocksdb \
    -P "$YCSB_HOME/workloads/workloada" \
    -p rocksdb.dir="$ROCKSDB_DIR" \
    -p recordcount=100000000 \
    -p operationcount=100000000 \
    -p fieldcount=1 \
    -p readallfields=false \
    -p requestdistribution=zipfian \
    -threads 32 \
    -s
```

### 常用可调参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| recordcount | Load 阶段加载的记录数 | 100000000 |
| operationcount | Run 阶段执行的操作总数 | 100000000 |
| fieldcount | 每条记录的字段数 | 1 |
| fieldlength | 每个字段的字节长度 | 100 |
| requestdistribution | 请求分布模式 (uniform/zipfian/latest) | zipfian |
| readallfields | 查询时是否读取所有字段 | false |
| readproportion | 读操作比例 | 由 workload 决定 |
| updateproportion | 更新操作比例 | 由 workload 决定 |
| insertproportion | 插入操作比例 | 由 workload 决定 |
| scanproportion | 扫描操作比例 | 由 workload 决定 |
| maxscanlength | 扫描最大记录数 | 1000 |

## RocksDB 特定参数

通过 `-p` 传递 RocksDB 配置项：

```bash
$YCSB_HOME/bin/ycsb run rocksdb \
    -P "$YCSB_HOME/workloads/workloada" \
    -p rocksdb.dir="$ROCKSDB_DIR" \
    -p rocksdb.write_buffer_size=67108864 \
    -p rocksdb.max_write_buffer_number=3 \
    -p rocksdb.target_file_size_base=67108864 \
    -p rocksdb.max_bytes_for_level_base=268435456 \
    -p rocksdb.block_size=16384 \
    -p rocksdb.cache_size=1073741824 \
    -p rocksdb.compression=snappy \
    -threads 32 \
    -s
```

### 常用 RocksDB 调优参数

| 参数 | 说明 | 建议值 |
|------|------|--------|
| rocksdb.write_buffer_size | MemTable 大小 (字节) | 64MB (67108864) |
| rocksdb.max_write_buffer_number | MemTable 最大数量 | 3 |
| rocksdb.target_file_size_base | SST 文件基础大小 (字节) | 64MB |
| rocksdb.max_bytes_for_level_base | L1 层最大字节数 | 256MB |
| rocksdb.block_size | Block 大小 (字节) | 16KB (16384) |
| rocksdb.cache_size | Block Cache 大小 (字节) | 1GB (1073741824) |
| rocksdb.compression | 压缩算法 | snappy / zlib / none |
| rocksdb.increase_parallelism | 并行度 | CPU 核数 |
| rocksdb.use_fsync | 是否使用 fsync | false |

## 执行流程

1. 确认 YCSB 和 RocksDB binding 已正确安装
2. 设置环境变量：`YCSB_HOME`、`ROCKSDB_DIR`、`RECORDCOUNT`、`OPERATIONCOUNT`、`THREAD_LIST`
3. 执行测试脚本，自动遍历 workload a-f 与指定并发数的所有组合
4. 每个 workload+threads 组合先执行 `load` 阶段加载数据，再执行 `run` 阶段运行测试
5. 每组测试完成后清空 RocksDB 数据目录，避免数据残留影响下一组测试
6. 所有测试完成后，运行结果解析脚本提取关键指标生成 CSV 汇总表

## 结果指标说明

| 指标 | 含义 |
|------|------|
| Throughput(ops/sec) | 吞吐量，每秒操作数 |
| RunTime(ms) | 测试运行总耗时 |
| AverageLatency(us) | 操作平均延迟（微秒） |
| 95thPercentileLatency(us) | 95% 操作的延迟上限（微秒） |
| 99thPercentileLatency(us) | 99% 操作的延迟上限（微秒） |
| MinLatency(us) | 最小延迟（微秒） |
| MaxLatency(us) | 最大延迟（微秒） |

## 注意事项

- 每次 load 前需确保 RocksDB 数据目录为空，否则已有数据会影响测试结果
- workload e (扫描型) 的延迟通常远高于其他 workload，属于正常现象
- 建议在测试前预热系统（如先运行一轮不记录结果的测试），避免冷启动影响
- 测试期间应关闭不必要的系统服务，减少干扰
- 如果测试数据量大，确保磁盘空间充足（估算：recordcount × fieldcount × fieldlength，1亿行×1字段×100字节 ≈ 10GB 原始数据，RocksDB 实际占用取决于压缩和写放大）
- `-s` 参数会将运行时中间状态打印到 stderr，便于监控进度
- 可通过 `-target n` 限制每秒操作数上限，用于测试特定吞吐量下的延迟表现
