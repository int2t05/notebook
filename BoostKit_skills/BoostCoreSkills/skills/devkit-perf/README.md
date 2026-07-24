# devkit-perf Top-Down 性能分析

`devkit-perf` 是面向 `devkit tuner top-down` 的基础使用 Skill，用于快速采集 CPU 微架构 Top-Down 指标，判断程序主要受 **Retiring / Bad Speculation / Frontend Bound / Backend Bound** 哪一类因素限制。

`devkit-perf` focuses on the practical use of `devkit tuner top-down`, helping users collect and interpret CPU pipeline bottleneck metrics.

## 分析定位

```
devkit-perf              perf-topdown               perf-hotspot
────────────             ────────────               ────────────
devkit 工具使用           Top-Down + perf 交叉验证    perf 采样/注解/SPE 深入
WHAT/WHY 初诊             WHY 校验和决策树            WHERE/HOW 定位到函数和指令
```

## 核心能力

- **一条命令采集 Top-Down 指标**：使用 `devkit tuner top-down -L 0` 获取完整层级的流水线瓶颈分解
- **四大类快速判读**：识别 Retiring、Bad Speculation、Frontend Bound、Backend Bound 的主导瓶颈
- **Backend 细分诊断**：区分 Core Bound 和 Memory Bound，进一步查看执行端口、FSU Stall、Ptag stall、L1/L2/L3/DRAM Bound
- **对比分析工作流**：用同一采集级别对比不同实现、不同核数或不同参数下的性能变化
- **常见报错处理**：覆盖 workload 退出太快、CPU 绑核参数冲突、采样开销过高等问题
- **指标参考入口**：更完整的指标含义见 `references/metrics.md`

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill devkit-perf -g -y
```

### 采集完整 Top-Down 报告

```bash
devkit tuner top-down -L 0 ./benchmark [args...]
```

- `-L 0` 表示采集全部指标层级
- devkit 会启动 workload、采集 PMU 计数器并打印报告
- 采集结束后会生成 `.tar` 文件，可用 `devkit report` 复查

### 常用选项

| 选项 | 含义 | 典型场景 |
|------|------|----------|
| `-L {0..6}` | 采集层级；`0` 为全部，`1` 为概要，`2` Core，`3` Memory，`5` BadSpec，`6` Frontend | 默认用 `-L 0`，定位后再缩小范围 |
| `-d <sec>` | 采集持续时间 | 长时间运行服务或循环 workload |
| `-D <sec>` | 延迟启动采集 | 跳过初始化阶段 |
| `-i <sec>` | 子报告采样间隔 | 观察性能随时间变化 |

## Top-Down 报告解读

Level 1 会把流水线 slot 分为四大类，通常先看最大的一项：

| 分类 | 含义 | 占比高时说明 |
|------|------|--------------|
| **Retiring** | 成功退休的 uOps，占比越高越好 | 执行效率较好，IPC 通常较高 |
| **Bad Speculation** | 分支预测失败等错误推测造成的浪费 | 分支不可预测、间接跳转或 pipeline flush 较多 |
| **Frontend Bound** | 前端无法及时供给指令 | ICache/ITLB miss、取指或解码带宽不足 |
| **Backend Bound** | 后端无法接收更多 uOps | 等数据或执行资源饱和，是最常见瓶颈 |

### Backend Bound 细分

| 子类 | 含义 | 重点指标 |
|------|------|----------|
| **Core Bound** | 数据已就绪，但执行单元或微架构资源成为瓶颈 | `Exe Ports Util`、`0 ports non serialize`、`FSU Stall`、`Ptag_stall` |
| **Memory Bound** | 后端在等待缓存或内存数据 | `L1 Bound`、`L2 Bound`、`L3 or DRAM Bound`、`Store Bound` |

经验判断：

- `0 ports non serialize` 高：执行端口忙，通常是计算饱和
- `FSU Stall` 高：浮点/Store 单元压力大，常见于写回较重的矩阵计算
- `Ptag_stall` 高：物理寄存器或 rename 资源紧张，常见于展开过深、临时变量过多
- `L1 Structure hazard` 高：L1 端口竞争，load/store 与计算争用明显
- `L3 or DRAM Bound` 高：数据到达 DRAM 或共享缓存层，常对应带宽墙或 cache blocking 不足

### Frontend 和 Bad Speculation

| 指标 | 典型含义 | 常见优化方向 |
|------|----------|--------------|
| `ICache Miss` | 热代码体积过大或布局不佳 | 减少热路径代码体积，优化函数布局 |
| `ITLB Miss` | 指令页分布过散 | 改善代码布局，减少热路径跨页 |
| `Fetch Bandwidth Bound` | 解码/取指带宽跟不上 | 简化热循环指令流 |
| `Branch Mispredicts` | 分支方向预测错误 | 改写不可预测分支，减少间接跳转 |

## 对比分析工作流

对比两个实现、两个参数或两个核数时，保持采集配置一致：

```bash
devkit tuner top-down -L 0 ./bench_a 2>&1 | tee bench_a.topdown.log
devkit tuner top-down -L 0 ./bench_b 2>&1 | tee bench_b.topdown.log
```

建议优先比较这些指标：

| 指标 | 看什么 |
|------|--------|
| IPC | 哪个实现每周期完成更多指令 |
| Retiring | 有用工作占比是否提升 |
| Backend Bound | 是否主要卡在后端 |
| Memory Bound | 是否等待缓存/内存数据 |
| Core Bound / 0 ports busy | 是否计算单元饱和 |
| Frontend Bound | 是否取指/解码压力变大 |
| FSU Stall / Ptag stall | 是否出现微架构资源压力 |
| L1 Structure Hazard | 是否有 L1 端口竞争 |

对比时重点看**变化量**：绝对数值有平台差异，但同平台、同采集方式下的差异通常更可靠。

## 示例：计算饱和 vs 内存受限

| 指标 | 纯 FMLA 循环 | DGEMM/矩阵计算 | 诊断 |
|------|-------------|----------------|------|
| Memory Bound | 很低 | 上升 | DGEMM 需要从缓存/内存取矩阵数据 |
| 0 ports busy | 较高 | 下降 | 纯 FMLA 更接近执行端口饱和 |
| L1 Structure Hazard | 接近 0 | 上升 | A/B/C 访问与计算争用 L1 端口 |
| Frontend Bound | 很低 | 可能上升 | 分块、边界处理和调度代码更复杂 |

## 在 AI Agent 工具中使用

### Claude Code

当你提到 devkit、top-down、CPU 微架构瓶颈、Frontend/Core/Memory bound 或程序为什么 stall 时，Skill 会自动激活：

```
帮我用 devkit tuner top-down 分析 ./benchmark 的瓶颈
解释这份 top-down 报告里 Backend Bound 为什么高
对比 bench_a 和 bench_b 的 IPC、Retiring、Memory Bound
这个 workload 退出太快，devkit 采不到数据，怎么处理
```

### CodeBuddy / Codex / Trae

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill devkit-perf -a <agent-name> -g -y
```

### 常用提示语

| 任务 | 提示语 |
|------|--------|
| 快速采集 | "用 devkit tuner top-down -L 0 采集 benchmark 的 Top-Down 报告" |
| 四分类解读 | "解释 Retiring、Bad Speculation、Frontend Bound、Backend Bound 哪个是主瓶颈" |
| Backend 细分 | "继续分析 Core Bound 和 Memory Bound 的细分指标" |
| 对比实现 | "对比两个 top-down 日志，找出性能差异来自哪里" |
| 报错排查 | "devkit 提示 no such process，帮我判断 workload 是否太短" |

## 与其他 perf Skill 的关系

| Skill | 职责 | 与本 Skill 关系 |
|-------|------|----------------|
| `devkit-perf`（本 Skill） | devkit tuner top-down 基本使用和指标初诊 | 先用它快速判断主瓶颈方向 |
| `perf-topdown` | devkit top-down 与 perf 数据的交叉验证 | 当需要确认 WHY 是否与 perf 采样一致时使用 |
| `perf-hotspot` | Linux perf、PMU、SPE、DDRC、函数/指令热点深入分析 | 当需要定位到具体函数、指令或硬件事件来源时使用 |

## 前置条件

- Linux 环境
- 已安装 `devkit` tuner
- 目标程序运行时间足够长，建议至少数百毫秒以上
- 建议二进制带符号编译（如 `-g`），并在需要时使用 `taskset -c N` 绑核

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `no such process` | workload 退出太快，devkit 还未完成采集 | 增大输入规模、增加迭代次数或延长运行时间 |
| `Options -c/--cpu, workload cannot be used together` | devkit 的 `-c` 与直接启动 workload 冲突 | 在 workload 内部设置绑核，或用 `taskset` 包住命令 |
| 四大类占比明显不接近 100% | 采集开销或 workload 太短导致数据不稳定 | 延长运行时间，跳过初始化阶段，重复采集确认 |
| 指标变化很大 | 频率缩放、调度迁移或系统噪声 | 固定 CPU 频率、绑核、减少后台负载，多次取稳定结果 |

## 当前限制

- 主要面向 ARM AArch64 平台
- 指标阈值与微架构相关，不同 CPU 需要结合平台经验校准
- Top-Down 只能指出瓶颈类别；定位到具体函数/指令通常需要结合 `perf-hotspot`
- 对极短 workload 不稳定，建议放大运行时间后再采集
