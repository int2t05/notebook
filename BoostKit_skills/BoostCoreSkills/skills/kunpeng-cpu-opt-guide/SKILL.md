---
name: kunpeng-cpu-opt-guide
description: >
  鲲鹏处理器（TSV110/HIP09/HIP12）微架构优化参考，覆盖指令延迟、流水线端口、性能陷阱。
  当需要了解目标 CPU 微架构特性来优化 C/C++ 代码、选择指令序列、调优编译选项或分析性能瓶颈时使用。
  其他性能优化 Skill（如 e2e-auto-optimize、gcc-profile-auto-tune）可在优化推理时引用本 Skill
  获取 CPU 特定的端口分配和指令延迟数据。
---

# 鲲鹏 CPU 微架构优化指南

本 Skill 收录三代鲲鹏处理器的微架构逆向分析数据（来源于 GCC pipeline model），供 Agent 在性能优化推理中精确引用目标 CPU 的指令延迟、执行端口分配和性能陷阱。

## CPU 自动检测

在开始优化前，先确定当前机器的 CPU 型号。

### 检测方法

```bash
# 方法 1: 先确认是否为鲲鹏平台（所有 Linux 通用，推荐）
grep -m1 "^CPU implementer" /proc/cpuinfo | awk '{print $3}'
# 0x48 = HiSilicon (鲲鹏)

# 方法 2: 读取 Part ID 精确区分三代鲲鹏
grep -m1 "^CPU part" /proc/cpuinfo | awk '{print $3}'
# 0xd01 = TSV110, 0xd02 = HIP09, 0xd06 = HIP12

# 方法 3: 从 /proc/cpuinfo 读 Features/Flags（备用）
grep -m1 "^Features" /proc/cpuinfo
lscpu | grep -E "^Flags|^标记"
```

### 识别逻辑

```
第一步：确认平台
  CPU implementer = 0x48 → 继续下一步
  CPU implementer ≠ 0x48 → 非鲲鹏平台，本 Skill 不适用

第二步：按 Part ID 区分三代鲲鹏（最可靠）
  CPU part = 0xd06 → HIP12 (ARMv9.2-A + SVE2)
  CPU part = 0xd02 → HIP09 (ARMv8.5-A + SVE)
  CPU part = 0xd01 → TSV110 (ARMv8.2-A)

第三步：Part ID 不可读时，按 Flags/标记 兜底
  sve2 存在 → HIP12
  sve 存在但 sve2 不存在 → HIP09
  sve 和 sve2 都不存在 → TSV110

非鲲鹏平台（如 Intel/AMD/Ampere/Graviton/A64FX）：本 Skill 不适用，请停止使用本 Skill 的数据，
推荐改用 arm64-arch-reference Skill 获取通用 ARM 架构特性参考。
```

> 为什么不能先按 `sve/sve2` 判断：SVE/SVE2 并非鲲鹏独占（如 Fujitsu A64FX、AWS Graviton4、NVIDIA Grace 也支持），先查 implementer 可避免误判。

**空结果处理**：如果以上 grep 命令无输出（某些定制内核/proc 格式不同），尝试以下回退方法：

```bash
# 回退 1: 直接读 /proc/cpuinfo 全文查找 implementer/part/flags
grep -i "implementer\|part\|sve\|neon\|asimd" /proc/cpuinfo | head -10

# 回退 2: 使用 lscpu 全部输出
lscpu | head -25
```

如果仍无法确定 CPU 型号，报出检测到的 CPU 信息由人工判断，不要猜测。

### 三代 CPU 关键区分

| 特征 | TSV110 | HIP09 | HIP12 |
|------|--------|-------|-------|
| **ISA** | ARMv8.2-A | ARMv8.5-A + SVE | ARMv9.2-A + SVE2 |
| **Part ID** | `0xd01` | `0xd02` | `0xd06` |
| **Implementer ID** | `0x48` | `0x48` | `0x48` |
| **型号名称 (lscpu)** | `Kunpeng-920` | `Kunpeng-920` 系列 | `Kunpeng` 系列 |
| **每核线程数** | 1 | 2 | 2 |
| **SVE 级别** | 无 | SVE | SVE2 |
| **独特 ISA 标记** | — | `svef32mm`, `svef64mm` | `sve2bitperm`, `sve2aes`, `sve2sm4`, `hbc`, `ls64` |
| **参考文件** | `references/tsv110-pipeline.md` | `references/hip09-pipeline.md` | `references/hip12-pipeline.md` |

## 横向对比总表

> **注意**: 本表为快速横向对比用摘要，**数据以各 CPU reference 文件为准**（`references/tsv110-pipeline.md`、`references/hip09-pipeline.md`、`references/hip12-pipeline.md`）。Reference 文件包含更完整的延迟数据、端口分配细节和优化建议。当汇总表与 reference 数据冲突时，以 reference 为准。
>
> **端口命名约定**: 三代 CPU 使用不同的端口命名体系，且功能分配并不对称，请勿按编号直接映射：
> - TSV110: `ALU1/2/3` + `MDU` + `FSU1/2`（FSU1 主做整数乘/移位/FP 除/AES，FSU2 主做 FP sqrt/大部分 FP/SIMD）
> - HIP09: `ALUs0-3` + `ALUm0-1` + `FSU0-3`（4 路对称 FSU，SVE 与 NEON 共享 FSU0-3，AES 用 FSU0/2）
> - HIP12: `ALU0/1/3/4`（简单）+ `ALU2/5`（复杂）+ `V0-3`（FP/SIMD/SVE，4 路但 FCMP/部分 SHA 仅 V0/V2）
>
> 本汇总表及场景路由中使用的端口名称与各 reference 文件中保持一致，跳转到具体 reference 时请注意命名体系差异。

### 执行资源

| 资源 | TSV110 | HIP09 | HIP12 |
|------|--------|-------|-------|
| **简单 ALU** | 3 (ALU1/2/3) | 4 (ALUs0-3) | 4 (ALU0/1/3/4) |
| **复杂 ALU** | 1 (MDU) | 2 (ALUm0/1) | 2 (ALU2/5) |
| **整数 ALU 合计** | 3 简单 + 1 复杂 | 4 简单 + 2 复杂 | 4 简单 + 2 复杂 = 6 路 |
| **基本整数可走宽度** | 3 路 | 4 路 | 6 路 |
| **Branch 单元** | 2 (BRU 复用 ALU2/3) | 2 (BRU0/1) | 2 (B0/1) |
| **Load 流水线** | 2 (LS1/2) | 2 (LD0/1) | 3 (LD0-2) |
| **Store 流水线** | 2 (LS1/2) | 2 (ST0/1 + STD0/1) | 2 (ST0/1 + STD0/1) |
| **FP/SIMD 单元** | 2 非对称 (FSU1/2) | 4 (FSU0-3) | 4 (V0-3) |
| **SVE 发射** | 无 | 与 NEON 共享 FSU0-3（AES 用 FSU0/2） | 4路 (V0-3) |
| **独立 automaton** | 2 (int + fsu) | 3 (int + ldst + fsu) | 3 (int + ldst + v) |

### 关键指令延迟对比（周期）

| 指令类别 | TSV110 | HIP09 | HIP12 |
|----------|--------|-------|-------|
| 整数 ALU 基本 | 1 | 1 | **1** (6路发射) |
| 整数乘法 (32/64) | 3 | 3 | **3** (2路) / long: 2 |
| 整数除法 (32/64) | 10 | 10 | **8** |
| 整数 MLA | — | — | **4** (占双资源) |
| FP add/sub | 5 | **2** | **2** |
| FP mul | 5 | **3** | **3** |
| FP FMA | 7 | **4** | **4** |
| FP div (single) | 12 | **7** | **6** |
| FP div (double) | 12 | **10** | **8** |
| FP sqrt (single) | 24 | **9** | **6** |
| FP sqrt (double) | 24 | **15** | **8** |
| NEON 基本 ALU | 2 | **1** | **1** |
| NEON MUL (D-form) | 4 | **3** | **3** |
| NEON MLA | 4 | **4** | **3** |
| NEON DOT | — | **6** | **3** |
| NEON FP mul | 5 | 3 (S:5) | **3** |
| NEON FP FMA | 7 | **4** | **4** |
| NEON FP div (S) | — | 15 | **6** |
| NEON FP sqrt (S) | — | 25 | **6** |
| LD1 1-2reg | 6 | 6 | **6** (3路load) |
| ST1 1reg | 0 | 2 | **1** |
| 分支 (B/BR) | 0 | 2 (占ALU!) | **1** (不占ALU) |
| AES | 3 (仅FSU1) | 2 (FSU0\|2) | **2** (4路V) |
| SHA256 fast | 2 (仅FSU1) | 2 (仅FSU2) | **2** (仅V0\|2) |

### 每域理论发射宽度

> 注意：下表按独立 automaton 划分。不同 automaton 之间可并发发射，同一 automaton 内的单元竞争同一组发射槽。

| 域 / automaton | TSV110 | HIP09 | HIP12 |
|----|--------|-------|-------|
| 整数/Load/Store (`tsv110`/`hip09`/`hip12`) | 3 ALU + 1 MDU + 2 BRU(复用) + 2 LS | 4 ALUs + 2 ALUm + 2 BRU(复用) | 4 简单 ALU + 2 复杂 ALU + 2 Branch |
| Load/Store (`hip09_ldst`/`hip12_ldst`) | —（与整数同域） | 2 Load + 2 Store + 2 STD | 3 Load + 2 Store + 2 STD |
| FP/SIMD/SVE (`tsv110_fsu`/`hip09_fsu`/`hip12_v`) | 2 FSU | 4 FSU（SVE 复用 FSU0-3） | 4 V |
| **并发能力** | int/ldst ‖ fsu | int ‖ ldst ‖ fsu | int ‖ ldst ‖ v |

## 场景路由指南

根据优化任务的类型，选择对应的 CPU reference 章节。**注意各 CPU reference 文件章节编号不同**，以下按 CPU 分别标注：

### 整数密集型代码
关注指令延迟表中的整数/分支部分：
- TSV110: `references/tsv110-pipeline.md` §2.1（整数指令）+ §2.2（分支指令）
- HIP09: `references/hip09-pipeline.md` §2.1（整数指令）+ §2.2（分支指令）
- HIP12: `references/hip12-pipeline.md` §2.1（整数指令）+ §2.2（分支指令）
- TSV110: 注意 MDU 拥塞，flags 仅 ALU2/3
- HIP09: 利用 4路 ALUs，注意 flags 仅 ALUs2/3，除法仅 ALUm0
- HIP12: `logics_imm` 仅 ALU2/5 (2路)，MLA 占双资源

### 浮点密集型代码
关注指令延迟表中的标量浮点部分：
- TSV110: §2.4（标量浮点）— FP div 仅 FSU1，FP sqrt 仅 FSU2，可并行发射
- HIP09: §2.4（标量浮点）— FP abs/neg 仅 1cy，FCMP 占 ALU，FCCMP 极重(7cy)
- HIP12: §2.4（标量浮点）— FCMP 仅 V0/V2(2路)，FCSEL 6cy 高延迟，f_cvti2f 7cy 极重

### SIMD/NEON 向量化
关注指令延迟表中的 NEON 部分：
- TSV110: §2.5（NEON 整数）+ §2.6（NEON 浮点）— mul/shift 独占 FSU1，Q-form 延迟 = D-form ×2
- HIP09: §2.5（ASIMD/NEON，整数与浮点合并）— DOT=6cy，BFMMLA=9cy，TBL1=1cy / TBL4=4cy
- HIP12: §2.5（NEON 整数 + 浮点在同一节内）— DOT=3cy，MUL/MLA 统一 3cy，DUP=6cy 重，shift_acc 旁路仅 1cy

### AI/ML 推理（DOT/BF16/矩阵乘）
- TSV110: 无 DOT/BF16 支持
- HIP09: §2.5 — SDOT/UDOT=6cy，BFMMLA=9cy
- HIP12: §2.5 — SDOT/UDOT=**3cy**（优先使用），SVE2 I8MM/BF16

### Crypto（AES/SHA/SM）
- TSV110: §2.8（Crypto）— AES=3cy 仅 FSU1，SHA slow=5cy
- HIP09: §2.7（Crypto）— AES=2cy 双路(FSU0|2)，SHA3=**1cy**，SHA 仅 FSU2
- HIP12: §2.6（Crypto）— AES=2cy **4路**(V0-3)，SHA256/SHA512/SM3 仅 V0|2

### SVE/SVE2 向量化
- TSV110: 不支持
- HIP09: §2.6（SVE）— 与 NEON 共享 FSU0-3，无独立 SVE 专用流水线
- HIP12: §2.7（SVE2）— 4路 SVE2，含 BITPERM/AES/SM4/SHA3 扩展

### Load/Store 密集
- TSV110: §2.3（Load/Store）+ §2.7（NEON Load/Store）— NEON Complex Store 阻塞**全部端口** 2 周期，最严重陷阱
- HIP09: §2.3（Load/Store）— LD4 4reg=13cy，ST3/4 需额外 FSU 资源
- HIP12: §2.3（Load/Store）— 3路 Load，基本 Store 仅 1cy

## 性能陷阱速查

| 陷阱 | TSV110 | HIP09 | HIP12 |
|------|--------|-------|-------|
| **最严重** | ST2/ST3/ST4 阻塞全部端口 2cy | LD4 4reg 13cy | `logics_imm` 仅 ALU2/5 (2路) |
| **FP 比较** | FCMP=4cy (vs 整数1cy) | FCMP 占用 ALUs23 | FCMP 仅 V0/V2 |
| **GP↔SIMD 传输** | GP→Q=4cy 占 ALU1 | DUP/INS=4cy 占 ALU | DUP=6cy, f_mcrr=10cy |
| **向量除法** | — | FDIV=15cy, FSQRT=25cy | FDIV_S=6cy（可用硬件） |
| **交叉存储** | ST2+ 阻塞全部端口 | ST3/4 7-10cy+FSU | ST3/4=4cy |
| **FP 转换** | i2f=5cy 占 ALU1 | f2i=5cy 占 ALUs23 | i2f=**7cy** 级联 |
| **除法串行** | 双除法全串行 | 双除法(仅ALUm0)全串行 | 双除法全串行 |

## 其他 Skill 引用规则

当 `e2e-auto-optimize`、`gcc-profile-auto-tune`、`hyperscan-dev` 等 Skill 需要 CPU 微架构数据时：

1. **先检测 CPU 型号**：执行本 Skill 的"CPU 自动检测"部分
2. **读取对应 reference**：根据检测结果加载 `references/<cpu>-pipeline.md`
3. **关注目标章节**（章节编号因 CPU 而异）：
   - Flag 选型 → 查微架构概览（TSV110/HIP12: §1 + 优化建议 §5；HIP09: §1 + 优化建议 §4）
   - 指令替换 → 查指令延迟表（各 CPU 均使用 §2 下属章节，具体子节编号见上方"场景路由指南"）
   - 瓶颈归因 → 查调度总结与性能陷阱（TSV110/HIP12: §6 + §7；HIP09: §5 + §6）
4. **引用格式**：在推理链中注明"根据 kunpeng-cpu-opt-guide，HIP12 上 FCMP 仅在 V0/V2 执行（2路），密集浮点比较需要关注 V0/V2 争用"

## 与其他 Skill 的关系

- **arm64-arch-reference**（本仓库 Skill #13）：提供 ARM A-profile 架构特性（FEAT_*）和 A64 指令权威速查表。本 Skill 侧重鲲鹏微架构层面的指令延迟和端口分配，两者互补：
  - arm64-arch-reference 回答"某指令在 ARMvX.Y 上是否可用、属于哪个 Feature"
  - kunpeng-cpu-opt-guide 回答"该指令在鲲鹏上跑多快、走哪个端口、有什么陷阱"
  - 性能优化时可先用 arm64-arch-reference 确认指令可用性，再用本 Skill 评估鲲鹏平台上的微架构代价
- **e2e-auto-optimize / gcc-profile-auto-tune**：这些 Skill 在优化推理时应引用本 Skill 获取目标 CPU 的端口分配和指令延迟数据，引用方式见上方"其他 Skill 引用规则"

## 数据说明

### 指令延迟 vs 编译器代价模型

本 Skill 中出现两类数值，含义不同：

- **指令延迟（cycles）**：来自 GCC pipeline model（`*.md` 中的 `define_insn_reservation`），表示该指令从发射到结果可用大约需要多少个时钟周期。用于软件流水、依赖链分析和指令替换决策。
- **调优代价模型（cost）**：来自 `aarch64-cost-tables.h`（`*_extra_costs`），是 GCC 做编译器内部启发式（如强度削弱、循环展开、向量化收益估算）时使用的**相对代价**。表中数值通常是在基础指令代价之上的额外开销，不直接等于硬件周期。

引用时请区分：评估单条指令在关键路径上的等待时间用「延迟」；评估编译器优化选择用「cost」。

### 验证方法

这些数据来自 GCC pipeline model 逆向推导，建议在实际优化前用以下方式抽样验证：

```bash
# 用 llvm-mca 估算吞吐（若 LLVM 支持对应 CPU）
llvm-mca -mcpu=tsv110 -iterations=100 < test.s

# 用内联汇编 + perf 测实际周期
gcc -O2 -mcpu=tsv110 -o ubench ubench.c
perf stat -e cycles,instructions ./ubench
```

## 数据版本

| CPU | 来源文件 | GCC 版本 | 逆向基准 |
|-----|---------|---------|---------|
| TSV110 | `gcc/config/aarch64/tsv110.md` + `aarch64-cost-tables.h` | GCC 14.3.0 | GCC pipeline model |
| HIP09 | `gcc/config/aarch64/hip09.md` + `aarch64-cost-tables.h` | GCC 14.3.0 | GCC pipeline model |
| HIP12 | `gcc/config/aarch64/hip12.md` + `aarch64-cost-tables.h` | GCC 14.3.0 | GCC pipeline model |
