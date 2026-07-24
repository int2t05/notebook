# 干扰模式参考

## CPU 算力竞争

典型信号：

- CPU utilization 或 run queue 上升。
- 在线业务获得的 CPU 时间减少。
- 延迟上升，但 cache 和 memory 指标没有出现明显新压力。
- 出现 cgroup throttling 或 CPU quota 压力。

反证检查：

- 在线流量是否上升？
- CPU quota、cpuset 或调度策略是否变化？
- CPU 频率是否下降？

验证动作：

- 临时将离线负载 pin 到独立 CPU。
- 提高在线业务 CPU quota 或隔离在线 cpuset。
- 对比在线业务 cycles/request 和调度延迟。

## LLC 或缓存容量竞争

典型信号：

- LLC miss rate 或 LLC MPKI 上升。
- IPC 下降，并且 cycles/request 上升。
- Memory bandwidth 可能中等幅度上升。
- 离线负载启动后在线业务延迟上升。

反证检查：

- 请求 mix 是否变得更不利于缓存？
- 在线和离线负载是否共享同一个 socket 或 LLC domain？

验证动作：

- 将离线负载迁移到另一个 socket 或 LLC domain。
- 如果平台支持，应用 cache partitioning。
- 降低离线负载 cache footprint 并对比 LLC MPKI。

## 内存带宽竞争

典型信号：

- Memory bandwidth 接近平台上限或显著上升。
- 如果有 topdown 指标，backend/memory bound 上升。
- LLC misses 可能上升，也可能长期保持高位。
- IPC 下降，尾延迟上升。

反证检查：

- Memory bandwidth 是否按节点或 socket 范围采集？
- 在线业务请求率或 payload 大小是否变化？

验证动作：

- 限速或暂停离线负载的内存密集阶段。
- 将离线负载迁移到其他 NUMA 节点或 socket。
- 对比离线负载 on/off 窗口下的 bandwidth 和 latency。

## NUMA 或远端内存影响

典型信号：

- Remote memory access 上升。
- 对内存延迟敏感的在线业务劣化。
- 调度或重启后 CPU 和 memory placement 发生变化。
- 劣化现象集中在特定 socket。

反证检查：

- Pod 或进程是否发生迁移？
- 内存是否在 cpuset/NUMA 绑定变化前已经分配？

验证动作：

- 将 CPU 和 memory pin 到同一个 NUMA 节点。
- 对比 local 和 remote memory counters。
- 使用显式 NUMA 策略重启在线服务。

## 前端、分支或指令缓存压力

典型信号：

- Frontend bound、i-cache miss、ITLB miss 或 branch miss rate 上升。
- IPC 下降，但没有明显内存带宽饱和。
- 请求 mix 或代码路径发生变化。

反证检查：

- 是否有发布、feature flag 或请求类型变化？
- branch 和 i-cache 指标是否能按在线业务范围采集，而不是只有节点级数据？

验证动作：

- 对比 per-request instruction count 和 branch miss rate。
- 在纯在线模式下用相同请求 mix 复现。

## 频率、功耗或温度干扰

典型信号：

- 混部窗口内 CPU frequency 下降。
- Package power、thermal throttling 或 turbo 行为变化。
- Instructions/request 接近不变，但 cycles/request 上升。

反证检查：

- 风扇、功耗策略、BIOS 配置或 governor 是否变化？
- 离线负载是否造成 package 级功耗压力？

验证动作：

- 对比固定频率或受控 governor 下的运行结果。
- 检查 thermal 和 power-limit events。
- 临时降低离线负载 CPU 强度。

## I/O、Page Fault 或内核噪声

典型信号：

- PMU 信号不强，但延迟随 context switches、page faults、interrupts 或 I/O wait 上升。
- System time 上升。
- Major faults 或磁盘/网络活动与业务劣化对齐。

反证检查：

- PMU 指标是否按在线业务范围采集？
- logging、checkpointing、compaction 或 GC 是否启动？

验证动作：

- 检查 context switches、page faults、interrupts、I/O wait 和 syscall traces。
- 暂停可疑的 I/O 密集阶段并对比延迟。

