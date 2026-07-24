---
name: kunpeng-library-opportunity
description: 分析运行中的 Linux C/C++ 服务、RPC 服务、数据库和大数据组件，识别动态库、疑似静态链接库、ELF 与 proc 证据，结合 perf-hotspot 采样结果判断鲲鹏 BoostKit/BoostCore 库使能机会，例如 KAE、KUAF、zlib、zstd、lz4、snappy、kpglibc、protobuf、sonic-cpp、KQMalloc、ISA-L、SPDK 和 AVX2KI。
---

# 鲲鹏库使能机会分析

## 概览

使用本 Skill 将一个 Linux 进程、可执行文件或服务启动命令，转化成一份有证据链的鲲鹏 BoostKit/BoostCore 库使能机会报告。

坚持“先证据、后建议”：先确认实际加载了什么、可能静态链接了什么、热点在哪里，再判断哪些鲲鹏优化库值得验证。

## 工作流

1. 确认分析目标和权限。
   - 运行中服务优先使用 PID，并记录可执行文件路径。
   - 补充启动命令、容器环境、CPU 架构、操作系统、页大小，以及是否有代表性业务流量。
   - 在生产环境执行 `perf`、`strace`、ptrace、重启服务、修改 `LD_PRELOAD` 前，必须让用户明确确认。

2. 采集库依赖清单。
   - 优先在目标 Linux 机器上运行本 Skill 自带采集脚本：

```bash
python3 scripts/collect_elf_inventory.py --pid <pid> --out inventory.json
python3 scripts/collect_elf_inventory.py --binary /path/to/service --out inventory.json
```

   - 需要静态链接线索时加入 `--include-strings`：

```bash
python3 scripts/collect_elf_inventory.py --pid <pid> --include-strings --out inventory.json
```

   - 如果目标机没有 Python，手工采集同等证据：

```bash
readlink -f /proc/<pid>/exe
tr '\0' '\n' < /proc/<pid>/environ
cat /proc/<pid>/maps
readelf -d /path/to/service
objdump -p /path/to/service
ldd /path/to/service
nm -D /path/to/service
strings -a -n 6 /path/to/service
```

   - 只对可信二进制运行 `ldd`；未知或不可信二进制优先使用 `readelf -d`。
   - 容器场景要说明是在容器内采集，还是从宿主机通过 `/proc/<pid>/root` 和命名空间采集。

3. 区分事实和推断。
   - `/proc/<pid>/maps`、`ldd`、ELF `NEEDED` 是动态库直接证据。
   - 静态库不能只靠名字下结论；只有构建信息、包信息、符号、字符串、源码或编译参数能支撑“疑似”或“确认”。
   - `not found`、已删除映射、异常 `RPATH/RUNPATH`、`LD_PRELOAD` 都要单独记录，因为它们会影响库是否真正生效。

4. 需要性能证据时调用 `$perf-hotspot`。
   - 如果本地已安装 `$perf-hotspot`，优先使用它完成 `perf stat`、`perf record/report`、PMU、SPE、DDRC/L3C 等采样和解读。
   - 如果未安装，提示用户可从 `https://gitcode.com/boostkit/skills/tree/master/BoostCoreSkills/skills/perf-hotspot` 安装，或临时按该 Skill 的方法采集 perf 结果。
   - 本 Skill 不重复维护 perf 方法细节，只消费 perf 结论并把热点映射到库使能机会。
   - 常见热点到候选库的映射：
     - `malloc`、`free`、分配器锁、page fault、RSS 异常增长：验证 KQMalloc。
     - `EVP_*`、`SSL_*`、`AES*`、`SHA*`、`RSA*`、`deflate`、`inflate`、gzip/zlib：验证 KAE 或压缩库优化。
     - `ZSTD_*`、`LZ4_*`、`snappy`、zlib：验证 KZL 压缩库优化补丁。
     - `memcpy`、`memmove`、`memcmp`、`memset`、`strlen`、`strcmp`、时间函数：验证 kpglibc 或系统库优化。
     - `google::protobuf`、`ParseFrom*`、`SerializeTo*`、arena allocation：验证 protobuf 优化。
     - JSON 解析/序列化热点：只有迁移成本可接受时，评估 sonic-cpp。
     - CRC、纠删码、RAID、SPDK BDEV 压缩/加密：评估 ISA-L、SPDK 或 KAE。

5. 对照 BoostCore/BoostKit 候选库。
   - 产出建议前读取 `references/boostcore-libraries.md`。
   - 如果用户要求最新社区状态，重新拉取或查看上游仓库，不要只依赖本地快照。
   - 推荐必须包含证据、候选库、使能路径、风险和最小验证方案。

6. 输出机会报告。
   - 目标摘要：PID、二进制、架构、OS、容器上下文、页大小、CPU 型号。
   - 动态库清单：已加载库、ELF `NEEDED`、缺失库、`LD_PRELOAD`、`RPATH/RUNPATH`。
   - 疑似静态库：候选库、证据、置信度、还需要什么证据确认。
   - perf 热点摘要：仅在用户提供或通过 `$perf-hotspot` 采样后输出。
   - 鲲鹏机会矩阵：候选库、证据、为什么可能有效、使能/迁移路径、风险、验证命令。
   - 下一步命令：给出用户可以直接运行的最小命令集。

## 判断标准

- 没有 `maps`、`ldd`、`readelf`、环境变量或运行日志证据时，不要声称某个 BoostKit 库已经使能。
- CPU 未确认时，不要直接建议启用 KQMalloc；KQMalloc 只面向鲲鹏处理器场景。
- `LD_PRELOAD`、替换分配器、替换 glibc、硬件加速都按“需要基准测试的实验”处理，不当作无风险默认动作。
- 数据库和大数据套件要检查插件目录、native codec、JNI/native library、存储引擎模块，而不只是主进程二进制。
- RPC 服务要重点检查 TLS、压缩、序列化、内存分配器、网络事件循环和系统调用热点。

## 资源

- `scripts/collect_elf_inventory.py`：在 Linux 目标机上采集 PID 或 ELF 二进制的库依赖、ELF、`/proc` 和候选信号。
- `references/boostcore-libraries.md`：基于 BoostCore 仓库整理的候选库匹配参考。

## 与其他 Skill 的协作

- `$perf-hotspot`：负责 perf、SPE、PMU、缓存、DDRC/L3C 等 CPU 热点采集与微架构解读。
- 本 Skill：负责把库依赖、疑似静态链接、perf 热点和 BoostCore/BoostKit 候选库关联起来，形成使能机会报告。
