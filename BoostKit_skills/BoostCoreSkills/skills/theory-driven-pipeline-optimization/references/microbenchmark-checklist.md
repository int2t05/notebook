# 微基准检查清单

## 目标定义

- 明确要回答的问题：核心指令 latency、核心指令 throughput、组合 overlap、density、layout、memory、frontend。
- 固定处理单位：byte、block、item、round、pair、iteration。
- 记录 CPU、频率、编译器、编译参数、commit、命令、输入规模。

## 代码设计

- 先为每类核心指令写 dependent latency 版本。
- 再为每类核心指令写 independent throughput 版本。
- 对算法中真实相邻的指令组写 mix 版本。
- 一次只改变一个变量。
- 依赖链和独立寄存器版本都要测。
- 循环体足够长，避免分支和计时开销主导。
- 使用对齐 buffer，不要用栈地址结论替代真实 load/store 行为。
- 对 load/store 测试，区分 L1 resident、streaming、random、cross-page。
- 对汇编函数，遵守 ABI，保存 callee-saved 寄存器。
- 防止编译器删除工作：返回 checksum、写 volatile sink 或使用汇编约束。

## 运行控制

- 固定 CPU 亲和性。
- 尽量固定频率或记录频率。
- 预热 cache 和 branch predictor，或明确测 cold path。
- 重复运行：优先 `perf stat -r 5`。
- 记录均值和方差；方差大时先修 benchmark。

## 数据采集

最低配置：

```bash
perf stat -r 5 -e cycles,instructions taskset -c <cpu> ./bench
```

按需增加：

- cache/TLB：`l1d_cache_refill,l2d_cache_refill,l3d_cache_refill,l1d_tlb_refill`
- branch：`br_mis_pred,br_retired`
- stall：平台可用的 frontend/backend/core/memory stall event
- annotate：`perf record` + `perf annotate`
- SPE：load latency、data source、TLB、per-instruction event

## 可信度检查

- IPC 是否落在合理区间。
- instructions/unit 是否符合静态预期。
- cycles/unit 是否随 unroll 或输入规模稳定。
- throughput 版本的 inst/unit 是否符合核心指令计数。
- latency 版本是否真的构成依赖链。
- variant 与 baseline 的差值是否大于噪声。
- perf/devkit 结果是否与吞吐变化方向一致。
