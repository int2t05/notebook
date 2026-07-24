# 补采建议

当现有 topdown 数据只能形成假设时，按疑点选择最小补采集合。命令中的 `<pid>`、`<cgroup>`、`<container>` 和设备路径需要按实际环境替换。

## CPU 时间和调度

用于区分“每条指令变慢”和“在线进程拿不到 CPU 时间”。

```bash
pidstat -p <pid> -u -w 1
```

检查：

- `%CPU` 是否下降。
- `cswch/s`、`nvcswch/s` 是否上升。
- 混部后是否出现明显调度挤压。

## cgroup CPU 限流

用于判断 CPU quota/throttling 是否解释 P99 劣化。

```bash
cat /sys/fs/cgroup/<cgroup>/cpu.stat
```

重点看：

- `nr_throttled`
- `throttled_usec`
- `nr_periods`

如果混部后 `nr_throttled` 或 `throttled_usec` 上升，CPU 限流可能比微架构瓶颈更直接。

## perf stat 进程级计数

用于补足 IPC、cache miss、branch miss 等基础证据。

```bash
perf stat -p <pid> -I 1000 -e cycles,instructions,cache-references,cache-misses,branches,branch-misses,LLC-loads,LLC-load-misses
```

输出时优先计算：

- IPC
- MPKI
- LLC miss rate
- Branch miss rate

## NUMA 位置和远端内存

用于验证 NUMA 或 remote memory 假设。

```bash
numastat -p <pid>
numactl --show
```

检查：

- 进程内存是否集中在远端 NUMA 节点。
- CPU 绑定和内存分配是否跨 NUMA。

## 内存带宽和 LLC

用于验证 LLC/DRAM 干扰假设。工具依平台而定，优先使用平台官方工具或已有监控。

可采集项：

- socket 或 NUMA 级内存读写带宽。
- LLC occupancy、LLC miss、LLC hit/miss rate。
- MPAM/RDT/CAT 分区配置和使用情况。

如果没有平台工具，至少补采进程级 `perf stat` 的 LLC 相关事件，并对比离线任务 on/off 窗口。

## DevKit topdown 复采

用于确认两点快照不是偶发噪声。

```bash
devkit tuner top-down -d 60
```

建议：

- 纯在线至少采 2 到 3 次。
- 混部稳定阶段至少采 2 到 3 次。
- 每次记录业务 QPS、P99、离线任务状态、CPU 频率和采集范围。

## 频率、功耗和温度

用于排除 package 级功耗或降频影响。

可采集项：

- CPU frequency。
- governor。
- thermal throttling。
- power limit events。

如果 `cycles/request` 上升但 cache/memory 信号不强，优先补采这一组。
