---
name: arm64-arch-reference
description: >-
  查阅 ARM A-profile（AArch64/A64）架构特性与指令的权威速查表。每当涉及 ARM64/AArch64/A64
  的架构特性（FEAT_*，如 FEAT_SVE/FEAT_LSE/FEAT_MTE/FEAT_BF16）、某特性的引入版本或可选/强制状态、
  指令的助记符/汇编模板/编码（Encoding）、或某指令受哪个特性门控时，都应使用本 skill。
  尤其在做 ARM64 编译器/代码生成（codegen）优化、判断目标指令在哪个架构版本可用、为某指令选择
  feature gate、或核对 SVE/SVE2/SME/SME2、NEON/AdvSIMD、原子(LSE)、PAC/BTI/MTE 等扩展时——
  即使用户没有明说"查手册"，只要在讨论 ARM64 指令或架构特性的细节，也请主动查阅本 skill，
  不要凭记忆作答。数据来自 ARM 官方机器可读规范（AARCHMRS），对应手册版本 M.b（Arm ARM, DDI 0487 M.b）、
  架构 v9Ap6-A（Armv9.6）/ 2026-03_rel。
---

# ARM64 (AArch64/A64) 架构特性与指令速查

本 skill 收录 ARM 官方 A-profile 规范的**全量架构特性**与**全量 A64 指令**，按功能分类成
Markdown 表，供快速、准确地查阅。**优先查表而非凭记忆**——ARM 特性的引入版本、可选/强制状态、
指令的精确汇编模板与门控特性都容易记错。

## 数据版本
手册版本 **M.b**（Arm Architecture Reference Manual for A-profile architecture，DDI 0487 M.b）/
架构 **v9Ap6-A（Armv9.6）** / 发布 **2026-03_rel** / schema 2.8。覆盖 **346 个 `FEAT_*` 特性**
（11 个功能域）与 **2258 条 A64 指令**（4 个分类）。

## 参考文件导航

| 想查什么 | 去哪个文件 |
| --- | --- |
| 架构特性 `FEAT_*`（含中文介绍/引入版本/可选强制/执行状态） | [`references/Features.md`](references/Features.md) |
| 指令分类与总览、检索建议 | [`references/overview.md`](references/overview.md)、[`references/instructions/00-index.md`](references/instructions/00-index.md) |
| 基础指令（整数算术/逻辑、访存、分支、系统） | [`references/instructions/base.md`](references/instructions/base.md)（507 条） |
| SIMD 与浮点（AdvSIMD/NEON、标量浮点、加密） | [`references/instructions/simd-fp.md`](references/instructions/simd-fp.md)（463 条） |
| SVE / SVE2 可伸缩向量指令 | [`references/instructions/sve.md`](references/instructions/sve.md)（938 条） |
| SME / SME2 可伸缩矩阵指令 | [`references/instructions/sme.md`](references/instructions/sme.md)（350 条） |

这些参考文件较大，**按需读取，不要一次性全部载入**。最高效的方式是用 `grep`/搜索定位具体条目，
而不是通读整个文件。

## 表格列含义

**Features.md**：`特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制`。
- 引入版本如 `Armv8.2`；`—` 表示官方描述未注明。
- 执行状态：`AArch64` / `AArch32` / `AArch64+AArch32`。
- 可选/强制：绝大多数特性为可选（OPTIONAL）。

**instructions/\*.md**：`指令名 | 英文简述 | 中文简介 | 汇编模板（Encoding） | 关联特性`。
- 指令名为官方 heading（如 `ADD (immediate)`），同一助记符的不同形态分行列出。
- 汇编模板即官方 `asmtemplate`（如 `ADD <Wd|WSP>, <Wn|WSP>, #<imm>{, <shift>}`），多种编码用换行分隔。
- 关联特性是门控该指令的 `FEAT_*`（如 `FEAT_SVE`、`FEAT_MTE`）；`—` 表示基础指令无特性门控。

## 高效检索方法

- **查某个特性**：在 `Features.md` 搜特性名，例 `grep -i 'FEAT_SVE2\b' Features.md`。
  想知道它在哪个功能域，看所在章节标题。
- **查某条指令**：先按功能去对应 `instructions/*.md`，搜助记符，例
  `grep -iE '^\| `LDR' base.md`。不确定分类时，先看 `00-index.md` 或直接跨文件 grep 助记符。
- **由特性反查指令**：在指令文件里搜 `FEAT_xxx`，列出所有受其门控的指令，例
  `grep 'FEAT_SVE2' sve.md`。这对"某优化依赖的指令需要哪个 feature flag / 哪个架构版本"特别有用。
- **判断指令是否可用 / 需要哪个版本**：查到指令的「关联特性」后，回 `Features.md` 查该特性的
  「引入版本」与「可选/强制」。

## 编译器优化场景提示

做 ARM64 codegen/优化时常见的查询：选用某指令前确认它的门控特性与最低架构版本；为
`-march`/feature 检测对齐 `FEAT_*` 名称；核对指令的精确操作数形态与立即数范围（看汇编模板）；
区分 SVE 与 SVE2、SME 与 SME2、NEON 标量与向量形态。这些都应以本 skill 的表为准。

## 数据来源（官方下载地址）

本 skill 自包含，查阅时只需读取本目录 `references/` 下的表格，不依赖任何外部仓库或本地数据。
表格转换自 ARM 官方机器可读规范（AARCHMRS A-profile，v9Ap6-A / 2026-03_rel）。如需核对原始数据或在新
ARM 版本上自行再生成，从下列官方地址下载源数据：

- 架构特性（Features）：`https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-Features/AARCHMRS/AARCHMRS_A_profile-2026-03_96.tar.gz`
- A64 指令（Instructions）：`https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz`
- 人类可读手册（Arm ARM, DDI 0487 M.b，本数据对应版次 **M.b**）：`https://developer.arm.com/documentation/ddi0487/mb`
