# ARM A-profile (AArch64/A64) 架构手册查阅 · 总览

> 面向 ARM64 编译器/代码生成优化场景的速查索引。数据来自 ARM 官方机器可读规范（AARCHMRS）
> A-profile，对应手册版本 **M.b**（Arm ARM, DDI 0487 M.b）/ 架构 **v9Ap6-A（Armv9.6）** /
> 发布 **2026-03_rel** / schema 2.8。

本资料包含两类查阅对象，均按功能分类、以表格组织，专有名词保留英文：

| 资料 | 内容 | 规模 | 文件 |
| --- | --- | --- | --- |
| 架构特性 Features | `FEAT_*` 特性：英文标题 / 中文翻译 / 中文介绍 / 引入版本 / 执行状态 / 可选或强制 | 346 项 / 11 个功能域 | [`Features.md`](./Features.md) |
| 指令 Instructions | A64 指令：指令名 / 英文简述 / 中文简介 / 汇编模板(Encoding) / 关联特性 | 2258 条 / 4 个分类 | [`instructions/`](./instructions/00-index.md) |

## 一、架构特性（Features.md）

按 11 个功能域分章，每章一张表。查某个 `FEAT_*` 时直接在 `Features.md` 内搜索特性名。

| 功能域 | 说明 |
| --- | --- |
| 内存管理与地址转换 | 地址转换、TLB、分页粒度、权限等 |
| 内存模型与原子操作 | LSE 原子、内存序、DC/IC 维护等 |
| 浮点 / SIMD / 数据类型 | AdvSIMD、FP16/BF16、矩阵乘加等 |
| SVE 可伸缩向量扩展 | SVE / SVE2 系列 |
| SME 可伸缩矩阵扩展 | SME / SME2、ZA 阵列、流式模式 |
| 安全与内存标记 | PAC、BTI、MTE、RME/CCA、加密指令等 |
| 虚拟化 | EL2、嵌套虚拟化、stage-2 等 |
| 调试与追踪 | 断点/监视点、自托管调试、Trace 等 |
| 性能监控与剖析 | PMU、SPE、BRBE、AMU 等 |
| RAS 可靠性、可用性与可维护性 | 错误记录与处理 |
| 系统控制、异常与执行状态 | 执行状态、异常等级、系统寄存器控制 |

## 二、指令（instructions/）

按 4 个顶层分类拆分为独立文件，避免单文件过大、便于按需加载：

| 分类 | 文件 | 指令数 | 典型用途 |
| --- | --- | --- | --- |
| 基础指令（Base） | [`instructions/base.md`](./instructions/base.md) | 507 | 整数算术/逻辑、访存、分支、系统指令 |
| SIMD 与浮点 | [`instructions/simd-fp.md`](./instructions/simd-fp.md) | 463 | AdvSIMD/NEON 向量、标量浮点、加密 |
| SVE 可伸缩向量 | [`instructions/sve.md`](./instructions/sve.md) | 938 | SVE/SVE2 向量与谓词指令 |
| SME 可伸缩矩阵 | [`instructions/sme.md`](./instructions/sme.md) | 350 | SME/SME2、ZA 阵列、外积累加 |

分类索引见 [`instructions/00-index.md`](./instructions/00-index.md)。

## 三、检索建议（给编译器优化场景）

- **查特性是否在某版本引入 / 是否可选**：搜 `Features.md` 中的 `FEAT_名`，看「引入版本 / 可选或强制」列。
- **查某指令的汇编格式 / 编码模板**：先按功能去对应 `instructions/*.md`，搜助记符；「汇编模板」列即官方 `asmtemplate`。
- **查某指令受哪个特性门控**：看指令表「关联特性」列（如 `FEAT_SVE`、`FEAT_MTE`），再回 `Features.md` 查该特性详情。
- **由特性反查指令**：在指令文件里搜 `FEAT_xxx` 即可列出受其门控的全部指令。

## 数据来源（官方下载地址）

本 skill 自包含，无需任何本地仓库即可查阅。表格由以下 ARM 官方机器可读规范（AARCHMRS A-profile，
v9Ap6-A / 2026-03_rel）转换、翻译、归类而来；如需核对原始数据或自行再生成，从下列地址下载：

- 架构特性（Features）：
  https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-Features/AARCHMRS/AARCHMRS_A_profile-2026-03_96.tar.gz
- A64 指令（Instructions）：
  https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz
- 人类可读手册（Arm ARM, DDI 0487 M.b）：
  https://developer.arm.com/documentation/ddi0487/mb
