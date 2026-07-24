# ARM A-profile 架构特性（FEAT_XXX）一览表

> 本表由 ARM 官方机器可读规范（AARCHMRS A-profile）自动生成，逐条人工翻译并按功能域归类。
> 源数据下载：https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-Features/AARCHMRS/AARCHMRS_A_profile-2026-03_96.tar.gz

| 项目 | 值 |
| --- | --- |
| 架构版本 | v9Ap6-A |
| 发布 ref | 2026-03_rel |
| schema 版本 | 2.8 |
| build | 750 |
| 数据时间戳 | 2026-03-26 20:27:25 |
| FEAT 特性总数 | 346 |

**列说明**：
- **特性名**：官方规范中的 `FEAT_*` 特性标识符。
- **英文标题 / 中文翻译**：官方 `title` 原文及中文译文（专有名词如 SVE、PMU、ASID、ZA 等保留英文）。
- **中文介绍**：依据官方描述（`description.before`）撰写的中文功能简介；缺译时回退英文原文。
- **引入版本**：从特性描述中解析的 “OPTIONAL from ArmvX.Y”；`—` 表示描述未注明。
- **执行状态**：AArch64 / AArch32 / AArch64+AArch32；`—` 表示描述未注明。
- **可选/强制**：`可选` / `可选（ArmvX 起强制）` / `强制` 三态；多数特性为可选扩展，部分在更高架构版本起转为强制。

## 目录

- [内存管理与地址转换](#内存管理与地址转换)（50 项）
- [内存模型与原子操作](#内存模型与原子操作)（20 项）
- [浮点 / SIMD / 数据类型](#浮点--simd--数据类型)（26 项）
- [SVE 可伸缩向量扩展](#sve-可伸缩向量扩展)（15 项）
- [SME 可伸缩矩阵扩展](#sme-可伸缩矩阵扩展)（20 项）
- [安全与内存标记](#安全与内存标记)（63 项）
- [虚拟化](#虚拟化)（18 项）
- [调试与追踪](#调试与追踪)（28 项）
- [性能监控与剖析](#性能监控与剖析)（56 项）
- [RAS 可靠性、可用性与可维护性](#ras-可靠性可用性与可维护性)（11 项）
- [系统控制、异常与执行状态](#系统控制异常与执行状态)（39 项）

## 内存管理与地址转换

共 50 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_ASID16` | 16 bit ASID | 16 位 ASID | 支持 16 位 ASID（地址空间标识符），将可用的地址空间标识数量从 8 位的 256 个提升至 65536 个，有效减少多进程场景下的 TLB 刷新需求。 | Armv8.0 | — | 可选 |
| `FEAT_ETS2` | Enhanced Translation Synchronization | 增强的转换同步 | FEAT_ETS2 引入了增强的内存访问排序要求，专门针对页表遍历（translation table walk）的内存访问，增强了多核环境下 TLB 维护操作的同步语义。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.8 起强制） |
| `FEAT_ETS3` | Enhanced Translation Synchronization | 增强的转换同步 | FEAT_ETS3 在 FEAT_ETS2 基础上进一步扩展，提供更严格的页表遍历内存访问排序要求，以满足更高版本架构对内存一致性的需求。 | Armv8.0 | AArch64+AArch32 | 可选（Armv9.5 起强制） |
| `FEAT_GTG` | Guest translation granule size | 客户机转换粒度大小 | 允许 hypervisor 为第二阶段和第一阶段地址翻译配置不同的页粒度，并允许嵌套 hypervisor 查询可用的第二阶段粒度大小。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_HAF` | Hardware management of the Access flag. | 访问标志的硬件管理 | 支持硬件自动更新翻译表中的访问标志（Access flag），无需软件干预即可追踪页面是否被访问过。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_HAFDBS` | Hardware management of dirty state | 脏状态的硬件管理 | 在 FEAT_HAF 基础上，支持硬件自动管理翻译表中的脏状态（dirty state），记录哪些页面被写入，从而减少软件对翻译表的维护开销。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_HPDS` | Hierarchical permission disables in translations tables | 转换表中的分级权限禁用 | 在翻译表中引入禁用层次权限的机制，允许禁用 APTable、PXNTable 和 UXNTable 等层次权限字段，简化权限管理（不影响 NSTable 位）。 | Armv8.0 | — | 可选（Armv8.1 起强制） |
| `FEAT_IVIPT` | The IVIPT Extension | IVIPT 扩展 | 描述许可的指令缓存实现策略，包括虚拟索引物理标记（VIPT）和物理索引物理标记（PIPT）两种缓存策略，为指令缓存的实现提供规范依据。 | Armv8.0 | — | 强制 |
| `FEAT_TCR2` | Support for TCR2_ELx | 支持 TCR2_ELx | 引入 TCR2_ELx 寄存器，作为 TCR_ELx 的扩展，提供对 EL1&0 和 EL2&0 翻译机制的附加顶层控制功能，增强了内存转换配置的灵活性。 | Armv8.0 | AArch64 | 可选（Armv8.9 起强制） |
| `FEAT_TGran16K` | Support for 16KB memory translation granule size at stage 1 | 阶段 1 支持 16KB 内存转换粒度 | 支持以 16KB 为粒度的第一阶段内存翻译页表，允许系统将 16KB 作为内存映射的基本页大小，适用于需要较大页粒度以减少页表层级的场景。 | Armv8.0 | — | 可选 |
| `FEAT_TGran4K` | Support for 4KB memory translation granule size at stage 1 | 阶段 1 支持 4KB 内存转换粒度 | 支持以 4KB 为粒度的第一阶段内存翻译页表，允许系统将 4KB 作为内存映射的基本页大小，是最常见的内存翻译页面粒度，也是大多数操作系统的默认选择。 | Armv8.0 | — | 可选 |
| `FEAT_TGran64K` | Support for 64KB memory translation granule size at stage 1 | 阶段 1 支持 64KB 内存转换粒度 | 支持在第一阶段地址转换中使用 64KB 内存转换粒度。该特性允许系统使用 64KB 作为页表的基本单元大小，可根据应用场景灵活选择合适的粒度配置。 | Armv8.0 | — | 可选 |
| `FEAT_nTLBPA` | Intermediate caching of translation table walks | 转换表遍历的中间缓存 | 引入一种机制，用于标识处理器的转换表遍历中间缓存是否不包含自上次适用 TLBI 操作完成以来的非一致性缓存旧翻译条目。该特性帮助软件了解实现的 TLB 预取和缓存行为，以便采取正确的 TLB 维护策略。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_AA32HPD` | AArch32 Hierarchical permission disables | AArch32 分级权限禁用 | 将 VMSAv8-64 中的层次权限禁用（APTable、PXNTable、UXNTable）功能扩展到使用长描述符格式的 VMSAv8-32 地址翻译机制，使 AArch32 状态下也能禁用页表层次权限传播。 | Armv8.1 | AArch32 | 可选 |
| `FEAT_DPB` | DC CVAP instruction | DC CVAP 指令 | 引入DC CVAP指令，提供一种将数据从缓存清理（clean）到持久化内存点（Point of Persistence）的机制，用于确保持久内存写入的可靠性。 | Armv8.1 | AArch64 | 可选（Armv8.2 起强制） |
| `FEAT_DPB2` | DC CVADP instruction | DC CVADP 指令 | 在FEAT_DPB基础上重新定义持久化点（Point of Persistence），并新增深度持久化点（Point of Deep Persistence）及DC CVADP指令，支持两级持久化缓存清理，适用于具有多级持久存储的系统。 | Armv8.1 | AArch64 | 可选（Armv8.5 起强制） |
| `FEAT_HPDS2` | Hierarchical permission disables | 分级权限禁用 | 在 FEAT_HPDS 基础上，允许操作系统或 hypervisor 将翻译表末级描述符中最多 4 个比特位用于实现定义的硬件用途，提升灵活性。 | Armv8.1 | AArch64+AArch32 | 可选 |
| `FEAT_LPA` | Large PA and IPA support | 大 PA 与 IPA 支持 | 支持使用 64KB 翻译粒度时，物理地址（PA）和中间物理地址（IPA）空间扩展至最大 52 位，并支持单个一级块描述符覆盖 4TB 地址范围。 | Armv8.1 | AArch64 | 可选 |
| `FEAT_LVA` | Large VA support | 大 VA 支持 | 在使用 VMSAv9-128 翻译格式或 64KB 粒度的 VMSAv8-64 格式时，支持每个翻译表基址寄存器对应最大 52 位的虚拟地址空间，扩展可寻址范围。 | Armv8.1 | AArch64 | 可选 |
| `FEAT_TTCNP` | Translation table Common not private translations | 转换表公共非私有转换 | 允许同一 Inner Shareable 域内的多个 PE 共享同一套地址转换表，适用于 VMSAv8-64 的所有翻译体系和 VMSAv8-32 中使用长描述符格式的翻译阶段。通过标记转换表为“公共”而非“私有”，减少多核系统中冗余的 TLB 维护开销。 | Armv8.1 | AArch64+AArch32 | 可选（Armv8.2 起强制） |
| `FEAT_XNX` | Translation table stage 2 Unprivileged Execute-never | 转换表阶段 2 非特权永不执行 | 在第二阶段转换表中引入非特权执行禁止（Unprivileged Execute-never）控制，允许独立控制内存在 EL0 和 EL1 的可执行性。该能力适用于 VMSAv8-64 和 VMSAv8-32 的第二阶段转换，增强了虚拟化场景下的细粒度执行权限管理。 | Armv8.1 | AArch64+AArch32 | 可选 |
| `FEAT_CCIDX` | Extended cache index | 扩展的缓存索引 | 扩展缓存索引格式，引入64位的CCSIDR_EL1及CCSIDR2_EL1/CCSIDR2寄存器，允许描述具有更多组数和更高关联度的缓存层次结构，同时支持AArch64与AArch32状态。 | Armv8.2 | AArch64+AArch32 | 可选 |
| `FEAT_BBML1` | Translation table break-before-make level 1 | 转换表 break-before-make 级别 1 | 翻译表 break-before-make 第 1 级优化，在更改块或表的翻译粒度时，放宽了必须严格执行 break-before-make 序列的要求，降低 TLB 维护的复杂性。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_BBML2` | Translation table break-before-make level 2 | 转换表 break-before-make 级别 2 | 翻译表 break-before-make 第 2 级优化，在 FEAT_BBML1 基础上进一步放宽更改块或表翻译粒度时的 break-before-make 序列约束，提供更高的 TLB 维护灵活性。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_S2FWB` | Stage 2 forced Write-Back | 阶段 2 强制回写 | 引入第二阶段强制回写（Stage 2 Forced Write-Back）机制，在Hypervisor期望的缓存属性与Guest OS使用的属性不同的系统中减少额外缓存维护操作；启用后，普通可缓存内存的内部与外部共享域之间不再有实质区别。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_TLBIOS` | TLB invalidate instructions in Outer Shareable domain | 外部可共享域的 TLB 失效指令 | 提供可将 TLB 无效化操作扩展至 Outer Shareable 域的 TLBI 维护指令。利用这些指令，软件可以使整个 Outer Shareable 共享域中的 TLB 条目失效，而不仅限于 Inner Shareable 范围。 | Armv8.3 | AArch64 | 可选（Armv8.4 起强制） |
| `FEAT_TLBIRANGE` | TLB invalidate range instructions | TLB 范围失效指令 | 提供针对一段输入地址范围执行 TLB 无效化的 TLBI 维护指令。相比逐条失效，按地址范围批量无效化 TLB 条目可提升虚拟内存管理的效率，尤其适用于大范围地址映射变更的场景。 | Armv8.3 | AArch64 | 可选（Armv8.4 起强制） |
| `FEAT_TTL` | Translation Table Level | 转换表级别（TTL） | 为所有携带虚拟地址（VA）或中间物理地址（IPA）参数的 TLBI 维护指令引入 TTL 字段，用于指明持有被无效化地址叶条目的转换表层级。通过提供层级提示，可减少 TLB 无效化的范围，提高操作效率。 | Armv8.3 | AArch64 | 可选（Armv8.4 起强制） |
| `FEAT_TTST` | Small translation tables | 小型转换表 | Small Translation Tables 特性，通过放宽翻译表大小的下限来支持更小的翻译表。具体表现为提升 TCR_EL1、TCR_EL2、TCR_EL3、VTCR_EL2 和 VSTCR_EL2 中 T0SZ/T1SZ 字段的最大允许值，使系统可配置覆盖更小虚拟地址空间的翻译体系。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_LPA2` | Larger physical address for 4KB and 16KB translation granules | 4KB 和 16KB 粒度的更大物理地址 | 在 4KB 和 16KB 翻译粒度下，将虚拟地址（VA）、中间物理地址（IPA）和物理地址（PA）空间均扩展至最大 52 位，同时支持更大的块描述符覆盖范围。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_CMOW` | Control for cache maintenance permission | 缓存维护权限控制 | 为按虚拟地址执行的缓存维护指令引入权限控制机制：Stage 1转换可配置为在EL0执行缓存维护指令但缺少写权限时产生Permission fault，Stage 2也可对EL0/EL1的此类操作施加类似限制，从而增强系统安全性。 | Armv8.7 | AArch64 | 可选（Armv8.8 起强制） |
| `FEAT_HAFT` | Hardware managed Access Flag for Table descriptors | 表描述符访问标志的硬件管理 | 在 FEAT_HAFDBS 基础上，扩展对翻译表目录描述符（Table descriptor）访问标志的硬件管理支持，使访问标志维护覆盖更多级别的翻译表项。 | Armv8.7 | AArch64 | 可选 |
| `FEAT_AIE` | Memory Attribute Index Enhancement | 内存属性索引增强 | 内存属性索引增强，将第一阶段翻译表描述符的属性索引字段由 3 位扩展为 4 位，最多支持 16 种内存属性，提升内存类型配置的灵活性。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_ATS1A` | Address Translation operations that ignore stage 1 permissions | 忽略阶段 1 权限的地址转换操作 | 引入忽略第一阶段翻译权限的地址翻译操作指令，可在不触发权限检查的情况下获取目标地址及其内存属性，便于特权软件进行地址翻译调试与分析。 | Armv8.8 | — | 可选 |
| `FEAT_S1PIE` | Stage 1 permission indirections | 阶段 1 权限间接 | 引入第一阶段权限间接寻址（Stage 1 Permission Indirection）机制，通过间接索引表设置页表描述符的权限位，提高权限位的使用效率并支持引入更多类型的内存访问权限。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_S1POE` | Stage 1 permission overlays | 阶段 1 权限叠加 | 引入第一阶段权限覆盖（Stage 1 Permission Overlay）机制，允许在所有异常级别（包括EL0）以渐进式收紧权限而无需TLB维护，减少调用特权软件的开销。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_S2PIE` | Stage 2 permission indirections | 阶段 2 权限间接 | 引入第二阶段权限间接寻址（Stage 2 Permission Indirection）机制，通过间接索引表更高效地使用页表描述符中的权限位，并支持引入额外权限类型（包括Mostly Read Only权限）。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_S2POE` | Stage 2 permission overlays | 阶段 2 权限叠加 | 引入第二阶段权限覆盖（Stage 2 Permission Overlay）机制，允许对使用相同第二阶段页表的不同EL1&0上下文提供不同的权限集合，支持渐进式权限收紧而无需修改页表。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_THE` | Translation Hardening Extension | 转换加固扩展 | Translation Hardening Extension，提供一种机制防止翻译表条目被其所属异常级别内的软件任意修改。引入了 Assured Translation 属性、AssuredOnly 属性、第二阶段 TopLevel 检查、Read-Check-Write（RCW/RCWS）指令及相关掩码寄存器，以及第一阶段描述符中的 Protected 属性，显著提升了翻译表的完整性保护能力。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_D128` | 128-bit Translation Tables, 56 bit PA | 128 位转换表，56 位 PA | 引入VMSAv9-128转换系统，支持128位宽的页表描述符和最高56位的物理地址编码，并结合FEAT_LVA/FEAT_LVA3支持56位虚拟地址转换，同时新增可接受128位输入的TLB无效化指令。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_LVA3` | 56-bit VA | 56 位 VA | 引入对 56 位虚拟地址的支持，将 AArch64 状态下可寻址的虚拟地址空间扩展至 56 位，需与 FEAT_D128 和 FEAT_LVA 配合实现。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_OCCMO` | Outer Cacheable Cache Maintenance Operation | 外部可缓存缓存维护操作 | 引入 DC CIVAOC 系统指令，为软件提供将写操作发布（publish）到外层缓存（Outer cache）的机制，有助于提升多处理器系统中缓存一致性操作的效率。 | Armv9.3 | AArch64 | 可选（Armv9.6 起强制） |
| `FEAT_ASID2` | Support for concurrent use of two ASIDs | 支持并发使用两个 ASID | 支持为每个 TTBR_ELx 寄存器各自使用独立的 ASID，允许在同一异常级别上并发维护两个地址空间标识，减少上下文切换时的 TLB 维护开销。 | Armv9.4 | AArch64 | 可选（Armv9.5 起强制） |
| `FEAT_HACDBS` | Hardware accelerator for cleaning Dirty state | 清理脏状态的硬件加速器 | 引入脏状态清除硬件加速器，通过硬件加速将第二阶段描述符从「可写-脏」状态更新为「可写-干净」状态，减少软件参与开销。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_HDBSS` | Hardware Dirty state tracking structure | 硬件脏状态跟踪结构 | 引入硬件脏状态追踪结构（Hardware Dirty State Tracking Structure），增强对第二阶段翻译表描述符脏状态的追踪能力，配合 FEAT_HAFDBS 提升虚拟机内存管理效率。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_TLBIW` | TLBI VMALL for Dirty state | 面向脏状态的 TLBI VMALL | 提供 TLBI VMALL 系列指令，用于从 TLB 条目中清除第二阶段脏状态（dirty state）。通过 TLBI VMALLWS2E1 及其 IS/OS 变体，虚拟机监控器可批量清除第二阶段地址转换缓存中的脏状态标记。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_PoPS` | Point of Physical Storage | 物理存储点（Point of Physical Storage） | 定义物理存储点（Point of Physical Storage, PoPS）的概念，并引入系统指令以执行到PoPS的缓存清理和无效化操作，用于管理内存一致性。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_S2TGran16K` | Support for 16KB memory translation granule size at stage 2 | 阶段 2 支持 16KB 内存转换粒度 | 支持在第二阶段地址转换（Stage 2）中使用 16KB 内存转换粒度。该特性依赖 EL2 和 16KB 转换粒度支持，适用于虚拟化场景下的内存管理配置。 | — | — | 可选 |
| `FEAT_S2TGran4K` | Support for 4KB memory translation granule size at stage 2 | 阶段 2 支持 4KB 内存转换粒度 | 支持在第二阶段地址转换（Stage 2）中使用 4KB 内存转换粒度。该特性依赖 EL2 和 4KB 转换粒度支持，是虚拟化环境下常用的内存管理选项。 | — | — | 可选 |
| `FEAT_S2TGran64K` | Support for 64KB memory translation granule size at stage 2 | 阶段 2 支持 64KB 内存转换粒度 | 支持在第二阶段地址转换（Stage 2）中使用 64KB 内存转换粒度。该特性依赖 EL2 和 64KB 转换粒度支持，适用于需要大粒度映射的虚拟化内存管理场景。 | — | — | 可选 |

## 内存模型与原子操作

共 20 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_DGH` | Data Gathering Hint | 数据聚合提示（Data Gathering Hint） | 在Hint指令空间中引入数据聚集提示（Data Gathering Hint）指令，向处理器提示当前是合适的数据聚集或合并访问的时机，有助于优化内存访问行为。 | Armv8.0 | — | 可选 |
| `FEAT_LOR` | Limited ordering regions | 受限排序区域 | 引入有限排序区域（Limited Ordering Regions）机制，提供特殊的 Load-Acquire 和 Store-Release 指令，对有限观察者集合在物理地址区域内提供内存访问顺序保证，适用于大型系统。 | Armv8.0 | AArch64 | 可选（Armv8.1 起强制） |
| `FEAT_LSE` | Large System Extensions | 大型系统扩展（LSE，原子指令） | 引入大型系统扩展原子指令集，包括比较并交换（CAS/CASP）、原子内存操作（LD<OP>/ST<OP>，支持 ADD、CLR、EOR、SET 等操作）以及交换（SWP）指令，用于多处理器同步。 | Armv8.0 | AArch64 | 可选（Armv8.1 起强制） |
| `FEAT_PRFMSLC` | SLC target support for PRFM and PRFUM instructions | PRFM/PRFUM 指令的 SLC 目标支持 | 为PRFM和PRFUM预取指令引入系统级缓存（System Level Cache, SLC）目标选项，使软件可以将预取提示直接发往系统级缓存层级。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_RPRFM` | Support for Range Prefetch Memory instruction | 支持范围预取内存指令 | 引入范围预取内存提示指令（RPRFM），允许软件指定未来可能访问的地址范围及其预期的复用模式，帮助硬件进行更高效的预取决策。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_LSMAOC` | AArch32 Load/Store Multiple instruction atomicity and ordering controls | AArch32 多寄存器加载/存储原子性与排序控制 | 引入控制机制，禁用 AArch32 多寄存器加载/存储指令的遗留行为，并提供对该遗留行为特定方面的陷入能力，提升与现代内存模型的兼容性。 | Armv8.1 | AArch64+AArch32 | 可选 |
| `FEAT_LRCPC` | Load-Acquire RCpc instructions | Load-Acquire RCpc 指令 | 引入支持弱发布一致性处理器一致（RCpc）模型的 Load-Acquire 指令，允许对不同地址的 Store-Release 和 Load-Acquire 操作重排序，提升性能。 | Armv8.2 | — | 可选（Armv8.3 起强制） |
| `FEAT_LRCPC2` | Load-Acquire RCpc instructions version 2 | Load-Acquire RCpc 指令 v2 | 在 FEAT_LRCPC 基础上，为 LDAPR 和 STLR 指令提供带 9 位无符号立即数偏移的变体，方便通过偏移地址访问 RCpc 语义的内存。 | Armv8.2 | — | 可选（Armv8.4 起强制） |
| `FEAT_LRCPC3` | Load-Acquire RCpc instructions version 3 | Load-Acquire RCpc 指令 v3 | 在 FEAT_LRCPC2 基础上，引入具有释放一致性语义的加载/存储对指令及单寄存器加载/存储指令变体，同时扩展 Advanced SIMD 和浮点指令集中的 RCpc 加载/存储指令。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_LSE2` | Large System Extensions version 2 | 大型系统扩展 v2 | 扩展 Large System Extensions，修改加载和存储操作的单拷贝原子性要求及对齐要求，使更多内存访问场景具备原子性保证。 | Armv8.2 | AArch64 | 可选（Armv8.4 起强制） |
| `FEAT_LS64` | Support for 64-byte loads and stores without status | 无状态的 64 字节加载/存储 | 引入单拷贝原子性的 64 字节加载（LD64B）和存储（ST64B）指令，不返回状态结果，适用于需要大粒度原子访问的场景。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_LS64_ACCDATA` | Support for 64-byte EL0 stores with status | 带状态的 64 字节 EL0 存储 | 引入支持 EL0 级别的单拷贝原子性 64 字节存储指令（ST64BV0），并返回状态结果，状态含义由提供响应的外设定义。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_LS64_V` | Support for 64-byte stores with status | 带状态的 64 字节存储 | 引入带状态返回的单拷贝原子性 64 字节存储指令（ST64BV），状态含义由提供响应的外设定义，适用于需要确认存储结果的场景。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_XS` | XS attribute | XS 属性 | 引入 XS（eXtended Shareability）内存属性，用于标识可能需要较长时间完成的内存访问。提供 DSB 指令和 TLBI 指令的 nXS 变体，这些变体的完成不依赖具有 XS 属性的内存访问完成，从而允许系统在处理慢速内存访问时继续推进屏障操作。 | Armv8.6 | AArch64 | 可选（Armv8.7 起强制） |
| `FEAT_MOPS` | Standardization of memory operations | 内存操作指令标准化 | 提供标准化的内存拷贝和内存置位指令，引入 Memory Copy 与 Memory Set 异常，并新增 HCRX_EL2、SCTLR_EL1、SCTLR_EL2 中相应的控制位，以统一内存批量操作的实现方式。 | Armv8.7 | AArch64 | 可选（Armv8.8 起强制） |
| `FEAT_PCDPHINT` | Producer-Consumer Data Placement Hints | 生产者-消费者数据放置提示 | 提供生产者-消费者数据放置提示指令，用于指示当前线程正在某位置生成数据（其他观察者正在等待），或当前 PE 即将读取可能尚未写入最终值的位置，帮助硬件优化数据传递效率。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_LS64WB` | LS64 for Write-back cacheable memory | 面向回写可缓存内存的 LS64 | 为可回写（Write-back）可缓存内存的访问提供大粒度单拷贝原子加载和存储指令支持，实现无需独立标志访问的可扩展原子消息传递。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_LSE128` | 128-bit Atomics | 128 位原子操作 | 在 FEAT_LSE 基础上引入 128 位原子指令支持，满足对更大数据宽度原子操作的需求。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_LSFE` | Large System Float Extension | 大型系统浮点扩展（浮点原子） | 实现 A64 基础浮点原子内存操作指令（Large System Float Extension），支持对内存中浮点数据的原子读-修改-写操作。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_LSUI` | Unprivileged Load Store | 非特权加载存储 | 引入非特权级加载/存储指令的变体，使特权软件无需清除 PSTATE.PAN 即可访问用户空间内存，简化内核与用户空间之间的数据访问。 | Armv9.5 | AArch64 | 可选（Armv9.6 起强制） |

## 浮点 / SIMD / 数据类型

共 26 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_AdvSIMD` | Advanced SIMD Extension | Advanced SIMD 扩展 | Advanced SIMD 扩展，提供向量单指令多数据（SIMD）和标量单指令单数据（SISD）运算支持，是 Armv8-A 富应用环境的基础能力，覆盖整数、浮点等多种数据类型的并行处理。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_FP` | Floating Point extensions | 浮点扩展 | FEAT_FP 提供了单精度和双精度浮点运算的硬件支持，是 Armv8-A 标准操作系统环境的基础组件，与 Advanced SIMD 协同实现浮点和向量计算能力。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_RDM` | Advanced SIMD rounding double multiply-accumulate instructions | Advanced SIMD 舍入双倍乘加指令 | 引入Advanced SIMD舍入双倍乘加/减（Rounding Double Multiply Add/Subtract）指令（如SQRDMLAH、SQRDMLSH），可提高定点乘累加运算的精度，适用于数字信号处理等场景。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_AA32I8MM` | AArch32 Int8 matrix multiply-accumulate | AArch32 Int8 矩阵乘加 | 在 AArch32 状态下引入整数矩阵乘累加指令和点积指令，用于加速 int8 量化矩阵运算，适用于机器学习推理场景。 | Armv8.1 | AArch32 | 可选 |
| `FEAT_DotProd` | Advanced SIMD dot product instructions | Advanced SIMD 点积指令 | 引入Advanced SIMD四路点积指令，将四个8位整数对的乘积累加到32位整数中，支持有符号和无符号输入，适用于机器学习推理中的矩阵运算加速。 | Armv8.1 | — | 可选 |
| `FEAT_FHM` | Floating-point half-precision to single-precision multiply-add instructions | 浮点半精度到单精度乘加指令 | FEAT_FHM 引入了半精度到单精度的融合乘加（FMA）指令，支持在 A64 和 A32/T32 指令集中对 FP16 操作数进行乘加运算并以 FP32 精度累积结果，适用于混合精度计算场景。 | Armv8.1 | — | 可选 |
| `FEAT_I8MM` | AArch64 Int8 matrix multiply-accumulate | AArch64 Int8 矩阵乘加 | 引入 Advanced SIMD 和 SVE 的 8 位整数矩阵乘累加指令及点积指令，加速机器学习和信号处理中的整数矩阵运算。 | Armv8.1 | AArch64 | 可选（Armv8.6 起强制） |
| `FEAT_AA32BF16` | AArch32 BFloat16 instructions | AArch32 BFloat16 指令 | 在 AArch32 状态下支持 BFloat16（BF16）16 位浮点存储格式，提供 BF16 乘法累加到单精度结果的算术指令、加速点积与矩阵乘累加的指令，以及单精度浮点转 BF16 格式的转换指令。 | Armv8.2 | AArch32 | 可选 |
| `FEAT_BF16` | AArch64 BFloat16 instructions | AArch64 BFloat16 指令 | 在 AArch64 状态下支持 BFloat16 浮点格式，提供 BF16 乘法累加到单精度结果的算术指令、加速点积与矩阵乘累加的指令，以及单精度浮点与 BF16 之间的转换指令，广泛应用于机器学习训练与推理。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_EBF16` | AArch64 Extended BFloat16 behaviors | AArch64 扩展 BFloat16 行为 | 支持扩展BFloat16（BF16）行为，提供更完整的BF16浮点语义支持，包括对sum-of-products类计算指令的浮点行为定义，适用于机器学习等需要低精度浮点加速的场景。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_FCMA` | Floating-point complex number instructions | 浮点复数指令 | FEAT_FCMA 引入了用于复数的浮点乘法和加法指令，支持在 Advanced SIMD 中进行复数运算，适用于信号处理、图形变换等需要复数计算的应用。 | Armv8.2 | — | 可选 |
| `FEAT_FP16` | Half-precision floating-point data processing | 半精度浮点数据处理 | FEAT_FP16 为 Advanced SIMD 和浮点单元引入了半精度（FP16）数据处理指令，支持 FP16 的算术运算和非规格化数清零（FTZ），适用于需要降低内存带宽和提升计算密度的机器学习推理场景。 | Armv8.2 | AArch64+AArch32 | 可选 |
| `FEAT_JSCVT` | JavaScript conversion instructions | JavaScript 转换指令 | 引入 JavaScript 转换指令，将双精度浮点数截断为 32 位有符号整数，并通过条件标志指示转换结果是否在有效范围内，专为 JavaScript 引擎优化。 | Armv8.2 | — | 可选 |
| `FEAT_FRINTTS` | Floating-point to integer instructions | 浮点转整数指令 | 提供将浮点数舍入为整数值浮点数的指令，舍入结果需落在 32 位或 64 位整数的数值范围内。这些指令仅添加至 A64 指令集。 | Armv8.4 | — | 可选 |
| `FEAT_AFP` | Alternate floating-point behavior | 可选浮点行为（Alternate FP） | 为特定浮点指令引入可选的替代行为，包括：对非规格化数（denormal）的输入/输出分别控制刷零、可选的 NaN 传播规则与默认 NaN、对部分 SIMD 标量指令保留高位向量元素，以及调整浮点异常触发规则。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_RPRES` | Increased precision of FRECPE and FRSQRTE | 提高 FRECPE 和 FRSQRTE 精度 | 允许将单精度浮点倒数估算（FRECPE）和倒数平方根估算（FRSQRTE）的精度从8位尾数提升至12位尾数，提高近似计算结果的准确度。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_F8F16MM` | 8-bit floating-point matrix multiply-accumulate to half-precision | 8 位浮点矩阵乘加至半精度 | FEAT_F8F16MM 引入了 Advanced SIMD 和 SVE（非 Streaming 模式下）中 FP8 到半精度（FP16）的矩阵乘累加指令，用于加速低精度神经网络推理中的矩阵计算。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_F8F32MM` | 8-bit floating-point matrix multiply-accumulate to single-precision | 8 位浮点矩阵乘加至单精度 | FEAT_F8F32MM 引入了 Advanced SIMD 和 SVE（非 Streaming 模式下）中 FP8 到单精度（FP32）的矩阵乘累加指令，适合在精度要求略高的 AI 推理场景中使用 FP8 进行高效矩阵运算。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_FAMINMAX` | Floating-point maximum and minimum absolute value instructions | 浮点最大/最小绝对值指令 | FEAT_FAMINMAX 为 Advanced SIMD、SVE 和 SME 引入了 FAMAX 和 FAMIN 指令，用于计算浮点数的最大和最小绝对值，适用于需要绝对值比较的向量运算场景。 | Armv9.2 | — | 可选 |
| `FEAT_FP8` | FP8 convert instructions | FP8 转换指令 | FEAT_FP8 引入了 OFP8（E5M2 和 E4M3）格式支持，并为 Advanced SIMD、SME 和 SVE 提供 FP8 格式转换及浮点缩放（FSCALE）指令，为超低精度 AI 推理计算提供硬件加速基础。 | Armv9.2 | — | 可选 |
| `FEAT_FP8DOT2` | FP8 2-way dot product to half-precision instructions | FP8 2 路点积至半精度指令 | FEAT_FP8DOT2 引入了 Advanced SIMD 和 SVE（非 Streaming 模式）中 FP8 到半精度（FP16）的 2 路点积指令，可用于加速 FP8 精度下的小规模神经网络点积运算。 | Armv9.2 | — | 可选 |
| `FEAT_FP8DOT4` | FP8 4-way dot product to single-precision instructions | FP8 4 路点积至单精度指令 | FEAT_FP8DOT4 引入了 Advanced SIMD 和 SVE（非 Streaming 模式）中 FP8 到单精度（FP32）的 4 路点积指令，适合在 AI 推理中以 FP8 精度高效执行点积计算并以 FP32 累积结果。 | Armv9.2 | — | 可选 |
| `FEAT_FP8FMA` | FP8 multiply-accumulate to half-precision and single-precision instructions | FP8 乘加至半精度和单精度指令 | FEAT_FP8FMA 引入了 Advanced SIMD 和 SVE（非 Streaming 模式）中 FP8 到半精度和单精度的乘累加指令，支持使用 FP8 操作数进行宽化乘加运算，为低精度 AI 推理提供更高吞吐量。 | Armv9.2 | — | 可选 |
| `FEAT_FPMR` | Floating-point Mode Register | 浮点模式寄存器 | FEAT_FPMR 引入了特殊用途寄存器 FPMR（浮点模式寄存器），用于控制 FP8 等低精度浮点运算的模式配置，为 FP8 指令集提供必要的运行时参数支持。 | Armv9.2 | — | 可选 |
| `FEAT_LUT` | Lookup table instructions with 2-bit and 4-bit indices | 2 位和 4 位索引查表指令 | 引入使用 2 位和 4 位索引的查找表指令（LUTI2/LUTI4），支持 Advanced SIMD、SVE2 和 SME2 中的查表操作，加速数据映射和编解码等应用场景。 | Armv9.2 | — | 可选 |
| `FEAT_FPRCVT` | Floating-Point to/from Integer in Scalar FP register | 标量 FP 寄存器中的浮点/整数互转 | FEAT_FPRCVT 引入了 A64 基础浮点与整数之间的转换指令，仅使用标量 SIMD&FP 寄存器作为操作数和结果，且支持不同位宽的输入输出寄存器；在 Streaming SVE 模式下同样支持相应的 Advanced SIMD 标量转换指令。 | Armv9.5 | AArch64 | 可选 |

## SVE 可伸缩向量扩展

共 15 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_F32MM` | Single-precision floating-point matrix multiply-accumulate | 单精度浮点矩阵乘加 | FEAT_F32MM 为 SVE 引入了单精度浮点矩阵乘加（FMMLA）指令，支持在 SVE 向量寄存器上执行单精度矩阵乘累加运算，适用于高性能矩阵计算场景。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_F64MM` | Double-precision floating-point matrix multiply-accumulate | 双精度浮点矩阵乘加 | FEAT_F64MM 为 SVE 引入了双精度浮点矩阵乘加（FMMLA）指令，以及一系列 128 位向量加载（LD1RO*）和向量排列（TRN、UZP、ZIP）的 128 位变体指令，增强了 SVE 对大规模矩阵运算的支持。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_SVE` | Scalable Vector Extension | 可伸缩向量扩展（SVE） | 可伸缩向量扩展（SVE），为 AArch64 引入长度可配置的向量寄存器（128 到 2048 位）和谓词寄存器，支持向量化和谓词化的数据处理指令、Gather/Scatter 访存以及软件管理的推测向量化，是对 Advanced SIMD 功能的重要补充。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_SVE2` | Scalable Vector Extension version 2 | 可伸缩向量扩展 v2 | 可伸缩向量扩展第 2 版（SVE2），是 SVE 的超集，融合了类似 Advanced SIMD 的功能并进行多项增强；Armv9-A 所有支持富操作系统的系统均强制提供 SVE2 硬件支持。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE_AES` | Scalable Vector AES instructions | 可伸缩向量 AES 指令 | 为 SVE 提供可伸缩向量 AES 密码学指令，包括 AESD、AESE、AESIMC、AESMC 以及 128 位多项式乘法指令 PMULLB 和 PMULLT，支持在 SVE 向量宽度下执行 AES 加密运算。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE_BitPerm` | Scalable Vector Bit Permutes instructions | 可伸缩向量位置换指令 | 为 SVE 提供可伸缩向量位置换指令，包括位提取（BEXT）、位沉积（BDEP）和位分组（BGRP）三条指令，用于灵活重排向量寄存器中的位模式。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE_PMULL128` | SVE single-vector Advanced Encryption Standard and 128-bit polynomial multiply long instructions | SVE 单向量 AES 与 128 位多项式长乘指令 | 在非 Streaming SVE 模式下实现 SVE 单向量 AES 指令和 128 位目标元素变体的 PMULLB、PMULLT 多项式乘法长指令，为 SVE 提供 128 位无进位多项式乘法能力，常用于 AES-GCM 等密码算法。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE_SHA3` | Scalable Vector SHA3 instructions | 可伸缩向量 SHA3 指令 | 为 SVE 提供可伸缩向量 SHA3 哈希指令（RAX1），支持在 SVE 向量宽度下执行 SHA3 密码学运算，是 SVE 密码学指令集的组成部分。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE_SM4` | Scalable Vector SM4 instructions | 可伸缩向量 SM4 指令 | 为 SVE 提供可伸缩向量 SM4 密码学指令，包括 SM4E（SM4 加密轮变换）和 SM4EKEY（SM4 密钥扩展）指令，支持在 SVE 向量宽度下执行国密 SM4 算法。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_SVE2p1` | Scalable Vector Extensions version 2.1 | 可伸缩向量扩展 v2.1 | 可伸缩向量扩展 2.1 版本（SVE2.1），在 SVE2 基础上新增非 Streaming 模式下的多向量连续加载/存储指令、谓词计数器指令和通用 SVE 指令，以及其他优化与放宽约束，是 SVE2 能力的进一步完善。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SVE_B16B16` | Non-widening BFloat16 to BFloat16 arithmetic for SVE2 and SME2 | 面向 SVE2 和 SME2 的非加宽 BFloat16→BFloat16 算术 | 为 SVE2 和 SME2 引入非展宽的 BFloat16 到 BFloat16 算术指令，在非 Streaming 模式下为 SVE2 提供，在 Streaming 模式下为 SME2 提供，同时支持 SME Z 寄存器目标的多向量 BF16 指令。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SVE_BFSCALE` | BFloat16 Floating-Point Adjust Exponent | BFloat16 浮点指数调整 | 引入 SVE 和 SME 的 BFloat16 指数调整指令（BFSCALE），在非 Streaming SVE 模式下为 SVE2 提供，在 Streaming SVE 模式下为 SME2 提供，并新增 SME 多向量 BFMUL 指令，支持 BF16 浮点数的指数缩放操作。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SVE_F16F32MM` | SVE Half-precision floating-point matrix multiply-accumulate to single-precision | SVE 半精度浮点矩阵乘加至单精度 | 引入 SVE 半精度浮点矩阵乘累加到单精度的指令，支持以半精度格式输入的矩阵乘法并将结果累加到单精度寄存器，适用于混合精度矩阵计算场景。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SVE2p2` | Scalable Vector Extensions version 2.2 | 可伸缩向量扩展 v2.2 | 可伸缩向量扩展 2.2 版本（SVE2.2），在 SVE2.1 基础上新增浮点取整到浮点值指令、标量索引首/末真谓词元素指令、对所有 SVE 一元指令的清零谓词变体，以及 COMPACT 和 EXPAND 指令的额外变体。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_SVE_AES2` | SVE multi-vector Advanced Encryption Standard and 128-bit polynomial multiply long instructions | SVE 多向量 AES 与 128 位多项式长乘指令 | 在非 Streaming SVE 模式下实现 SVE 多向量 AES 加密指令和 128 位目标元素多项式乘法长指令，是 FEAT_SVE_AES 的多向量增强版本，进一步提升向量密码运算吞吐量。 | Armv9.5 | AArch64 | 可选 |

## SME 可伸缩矩阵扩展

共 20 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_SME` | Scalable Matrix Extension | 可伸缩矩阵扩展（SME） | 引入可伸缩矩阵扩展（Scalable Matrix Extension），提供两种可由软件按需开启的 AArch64 执行模式：ZA 存储启用模式（提供二维 ZA tile 存储及行列操作指令）和 Streaming SVE 模式（采用与 ZA tile 宽度匹配的向量长度，并支持 SVE2 指令子集以及矩阵外积累加指令）。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME2` | Scalable Matrix Extensions version 2 | 可伸缩矩阵扩展 v2 | SME 版本 2 是 FEAT_SME 的超集，扩展了以下能力：支持将 ZA 数组按一维 ZA 向量组寻址（而非仅限二维 tile）、多向量指令集、多向量加载/存储谓词机制，以及专用 512 位查找表寄存器 ZT0（用于数据解压缩）。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME2p1` | Scalable Matrix Extension version 2.1 | 可伸缩矩阵扩展 v2.1 | SME 版本 2.1 是 SME2 的超集，新增了 Streaming SVE 模式下对 SVE RAX1 指令的支持（需 FEAT_SVE_SHA3）、MOVAZ 指令（移动并清零 ZA 向量或 tile 切片）、针对 ZA 向量的 ZERO 指令，以及使用步进编号写入 Z 向量的 LUTI2/LUTI4 查找表指令。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_B16B16` | Non-widening BFloat16 to BFloat16 SME ZA-targeting arithmetic | SME ZA 目标的非加宽 BFloat16→BFloat16 算术 | 为 SME 引入 ZA 目标非扩宽 BFloat16 浮点算术指令，支持在 ZA 数组中对 BFloat16 数据进行原精度（非扩宽）运算，适用于 AI 推理等混合精度计算场景。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_F16F16` | Non-widening half-precision FP16 to FP16 arithmetic for SME2 | SME2 的非加宽半精度 FP16→FP16 算术 | 为 SME2 引入半精度到单精度转换指令及非扩宽半精度 FP16 浮点算术指令，支持在 SME ZA 目标操作中进行半精度浮点的原精度运算和精度转换。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_F64F64` | Double-precision floating-point instructions | 双精度浮点指令（SME） | 表示 SME 支持在 ZA 数组中累加双精度浮点元素的指令，提供高精度矩阵运算能力，适用于科学计算等对精度要求较高的场景。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_F8F16` | SME2 ZA-targeting FP8 multiply-accumulate, dot product, and outer product to half-precision instructions | SME2 ZA 目标 FP8 乘加/点积/外积至半精度指令 | 为 SME 引入 ZA 目标 FP8 到半精度（FP16）的乘累加、点积和外积指令，以及 ZA 目标多向量非扩宽半精度 FADD 和 FSUB 指令，支持低精度浮点计算与半精度结果累加。 | Armv9.2 | — | 可选 |
| `FEAT_SME_F8F32` | SME2 ZA-targeting FP8 multiply-accumulate, dot product, and outer product to single-precision instructions | SME2 ZA 目标 FP8 乘加/点积/外积至单精度指令 | 为 SME 引入 ZA 目标 FP8 到单精度（FP32）的乘累加、点积和外积指令，支持将 FP8 低精度数据扩宽累加至单精度 ZA 数组，适用于低精度推理场景。 | Armv9.2 | — | 可选 |
| `FEAT_SME_FA64` | Full A64 instruction set support in Streaming SVE mode | 流式 SVE 模式下完整 A64 指令集支持 | 表示在 Streaming SVE 模式下支持完整的 A64 指令集执行，使处理器在进入 SME Streaming 模式时无需限制可用指令范围，提升编程灵活性。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_I16I64` | 16-bit to 64-bit integer widening instructions | 16 位到 64 位整数加宽指令 | 表示 SME 支持将 16 位整数数据扩宽累加至 ZA 数组中 64 位整数元素的指令，提供高精度整数矩阵运算能力。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_SME_LUTv2` | Lookup table instructions with 4-bit indices and 8-bit elements | 4 位索引、8 位元素查表指令 | 引入新的查找表指令，包括 LUTI4（4 个寄存器、8 位元素版本）和 MOVT（向量到表的搬移指令），扩展了 SME 在数据解压缩和查表操作方面的能力。 | Armv9.2 | — | 可选 |
| `FEAT_SSVE_FP8DOT2` | SVE FP8 2-way dot product to half-precision instructions in Streaming SVE mode | 流式 SVE 模式 FP8 2 路点积至半精度指令 | 在 Streaming SVE 模式下启用 SVE FP8 到半精度浮点的 2 路点积指令，支持以 FP8 格式输入并累加到半精度结果，适用于 AI 推理等低精度高吞吐计算场景。 | Armv9.2 | — | 可选 |
| `FEAT_SSVE_FP8DOT4` | SVE2 FP8 4-way dot product to single-precision instructions in Streaming SVE mode | 流式 SVE 模式 SVE2 FP8 4 路点积至单精度指令 | 在 Streaming SVE 模式下启用 SVE FP8 到单精度浮点的 4 路点积指令，支持以 FP8 格式输入并累加到单精度结果，进一步提升 Streaming SVE 模式下的低精度矩阵计算能力。 | Armv9.2 | — | 可选 |
| `FEAT_SSVE_FP8FMA` | SVE2 FP8 multiply-accumulate to half-precision and single-precision instructions in Streaming SVE mode | 流式 SVE 模式 SVE2 FP8 乘加至半/单精度指令 | 在 Streaming SVE 模式下启用 SVE FP8 到半精度和单精度浮点的乘累加指令，支持 FP8 输入经展宽后进行乘法累加运算，适用于深度学习等需要高效低精度乘累加的场景。 | Armv9.2 | — | 可选 |
| `FEAT_SME_MOP4` | Quarter-tile outer product instructions | 四分之一片外积指令 | 为 SME 引入四分之一 tile 外积（Quarter-tile outer product）指令，支持在更细粒度的 ZA tile 子块上执行矩阵外积运算，提高矩阵运算的灵活性。 | Armv9.4 | — | 可选 |
| `FEAT_SME_TMOP` | Structured sparsity outer product instructions | 结构化稀疏外积指令 | 为 SME 引入结构化稀疏外积（Structured sparsity outer product）指令，利用矩阵的稀疏结构跳过零元素运算，从而提高稀疏矩阵外积的计算效率。 | Armv9.4 | — | 可选 |
| `FEAT_SSVE_BitPerm` | Streaming Scalable Vector Bit Permutes instructions | 流式可伸缩向量位置换指令 | 在 Streaming SVE 模式下实现 SVE2 的位置换指令（BEXT、BDEP、BGRP），使 PE 在 Streaming SVE 模式中也能执行可伸缩向量位操作，由 ID_AA64SMFR0_EL1.SBitPerm 字段标识。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_SSVE_FEXPA` | Streaming FEXPA instruction | 流式 FEXPA 指令 | 在 Streaming SVE 模式下实现 SVE FEXPA 指令（浮点指数近似展开），使该指令在 SME Streaming SVE 模式中可用，由 ID_AA64SMFR0_EL1.SFEXPA 字段标识。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_SME2p2` | Scalable Matrix Extension version 2.2 | 可伸缩矩阵扩展 v2.2 | SME 版本 2.2 是 SME2.1 的超集，新增了多向量 Z 目标非扩宽浮点 FMUL 指令、四分之一 tile 外积指令、结构化稀疏外积指令，以及在 Streaming SVE 模式下对 SVE2.2 指令的支持。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_SSVE_AES` | Streaming SVE Mode Advanced Encryption Standard and 128-bit polynomial multiply long instructions | 流式 SVE 模式 AES 与 128 位多项式长乘指令 | 在 Streaming SVE 模式下实现 SVE AES 加密指令和 128 位多项式乘法长指令（由 ID_AA64ZFR0_EL1.AES 标识），使 SME 的 Streaming SVE 模式也能执行 AES 相关的向量密码运算。 | Armv9.5 | AArch64 | 可选 |

## 安全与内存标记

共 63 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_AES` | Advanced SIMD AES instructions | Advanced SIMD AES 指令 | 提供 Advanced SIMD AES 加解密指令（AESD、AESE、AESMC、AESIMC），通过硬件加速支持 AES 对称加密算法的高效执行。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_CLRBHB` | Support for Clear Branch History instruction | 支持清除分支历史指令 | 提供CLRBHB指令，用于清除分支历史缓冲区，帮助软件在上下文切换等敏感时机消除分支历史中可能泄露信息的痕迹，以缓解分支历史相关的推测执行侧信道攻击。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.9 起强制） |
| `FEAT_CSV2` | Cache Speculation Variant 2 | 缓存推测变体 2（CSV2） | 提供机制以标识硬件是否能够阻止跨硬件描述上下文的预测资源（如分支目标、数据值、缓存预取）泄露信息，从而缓解基于预测执行的跨上下文侧信道攻击（Spectre变种2类）。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.5 起强制） |
| `FEAT_CSV2_1p1` | Cache Speculation Variant 2 | 缓存推测变体 2 | 在FEAT_CSV2基础上进一步约束分支预测行为：在同一硬件描述上下文内，针对某地址训练的分支目标只能以难以确定的方式影响其他地址处的分支推测执行，但不引入SCXTNUM_ELx寄存器。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_CSV2_1p2` | Cache Speculation Variant 2 version 1.2 | 缓存推测变体 2 v1.2 | 在FEAT_CSV2_1p1基础上引入SCXTNUM_ELx寄存器，但上下文描述中不包含SCXTNUM_ELx的值，分支历史训练跨地址影响推测执行的能力进一步受限。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_CSV2_2` | Cache Speculation Variant 2 version 2 | 缓存推测变体 2 version 2 | 引入SCXTNUM_ELx寄存器，为各异常级别提供上下文编号，使软件能够通过设置不同的上下文编号来隔离分支预测资源，从而防范基于预测资源的跨上下文侧信道攻击。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_CSV2_3` | Cache Speculation Variant 2 version 3 | 缓存推测变体 2 version 3 | 进一步扩展FEAT_CSV2_2，引入机制以标识硬件是否能够阻止在一个硬件描述上下文中训练的基于分支历史的预测资源影响另一上下文的推测执行，提供更强的分支历史隔离保证。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_CSV3` | Cache Speculation Variant 3 | 缓存推测变体 3（CSV3） | 提供机制以标识硬件是否能够防止在推测执行期间加载的、架构上不可访问的数据值被后续指令利用，从而避免敏感数据通过旁路信道（Spectre变种3类）被恶意代码推断出来。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.5 起强制） |
| `FEAT_ECBHB` | Exploitative control using branch history information | 基于分支历史信息的可利用控制（ECBHB） | FEAT_ECBHB 通过限制异常边界附近的分支历史投机行为，防止攻击者利用分支历史信息进行侧信道攻击，从而增强系统安全性。 | Armv8.0 | AArch64 | 可选（Armv8.9 起强制） |
| `FEAT_PAN` | Privileged access never | 特权访问禁止（PAN） | 在 PSTATE 中引入特权访问禁止（PAN）位，当该位为 1 时，EL1 或（E2H 有效时的）EL2 对 EL0 可访问的虚拟内存地址发起特权数据访问将产生权限故障，有效防止特权代码误操作用户数据。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.1 起强制） |
| `FEAT_PMULL` | Advanced SIMD PMULL instructions | Advanced SIMD PMULL 指令 | 提供用于64位多项式乘法的Advanced SIMD指令（PMULL/PMULL2），主要应用于AES等密码学算法中的有限域运算。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_SB` | Speculation Barrier | 推测屏障 | 引入 Speculation Barrier（SB）指令，用于控制推测执行的边界。该屏障指令可阻止处理器跨越屏障点进行推测，有助于缓解基于推测执行的侧信道攻击，在 AArch64 和 AArch32 状态下均可使用。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.5 起强制） |
| `FEAT_SHA1` | Advanced SIMD SHA1 instructions | Advanced SIMD SHA1 指令 | 在 Advanced SIMD 中实现 SHA1 系列加密指令，支持 SHA-1 哈希算法的硬件加速。该特性在 AArch64 和 AArch32 状态下均可使用。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_SHA256` | Advanced SIMD SHA256 instructions | Advanced SIMD SHA256 指令 | 在 Advanced SIMD 中实现 SHA256 系列加密指令，支持 SHA-256 哈希算法的硬件加速。该特性在 AArch64 和 AArch32 状态下均可使用，依赖 FEAT_SHA1。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_SPECRES` | Speculation restriction instructions | 推测限制指令 | 引入预测限制系统指令，阻止处理器基于特定执行上下文中先前执行所收集的信息对后续推测执行产生影响，从而降低可通过侧信道观测到的推测执行风险，在 AArch64 和 AArch32 状态下均可使用。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.5 起强制） |
| `FEAT_SPECRES2` | Enhanced speculation restriction instructions | 增强的推测限制指令 | 在 FEAT_SPECRES 基础上扩展，引入 COSP（Clear Other Speculative Prediction Restriction by Context）指令，进一步限制跨上下文的其他类型推测预测，增强推测执行的安全性。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.9 起强制） |
| `FEAT_SSBS` | Speculative Store Bypass Safe | 推测存储旁路安全（SSBS） | Speculative Store Bypass Safe，允许软件指示硬件是否可以进行可能引发缓存时序侧信道攻击的推测性加载或存储操作，从而帮助防御基于推测执行的信息泄露漏洞。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_SSBS2` | MRS and MSR instructions for SSBS version 2 | SSBS 的 MRS/MSR 指令 v2 | 在 FEAT_SSBS 基础上，提供通过 MSR 和 MRS 指令直接读写 PSTATE.SSBS 字段的能力，方便软件在 AArch64 状态下以更简便的方式控制推测存储旁路安全行为。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_Secure` | Support for Secure state | 支持安全状态 | 为处理器提供 Secure state（安全状态）支持，是 TrustZone 技术的基础，使系统能够在安全世界与非安全世界之间切换，保护安全敏感软件和数据。 | Armv8.0 | — | 可选 |
| `FEAT_PAN2` | AT S1E1R and AT S1E1W instruction variants affected by PSTATE.PAN | 受 PSTATE.PAN 影响的 AT S1E1R/W 指令变体 | 引入 AT S1E1R/AT S1E1W（AArch64）及 ATS1CPR/ATS1CPW（AArch32）指令的变体，这些变体在判断特权访问是否产生权限故障时会将 PSTATE.PAN 位纳入考量，结果反映在 PAR 中。 | Armv8.1 | AArch64+AArch32 | 可选（Armv8.2 起强制） |
| `FEAT_PAN3` | Support for SCTLR_ELx.EPAN | 支持 SCTLR_ELx.EPAN | 在 SCTLR_EL1 和 SCTLR_EL2 中引入 EPAN 控制位，使特权访问禁止（PAN）机制扩展到 Stage 1 地址转换下的指令访问，进一步提升特权级隔离的完整性。 | Armv8.1 | AArch64 | 可选（Armv8.7 起强制） |
| `FEAT_SHA3` | Advanced SIMD SHA3 instructions | Advanced SIMD SHA3 指令 | 为 Advanced SIMD 引入支持 SHA3 功能的指令集，提供 SHA-3 系列哈希算法的硬件加速能力。这些指令仅面向 A64 指令集，依赖 SHA1 和 SHA256 支持。 | Armv8.1 | — | 可选 |
| `FEAT_SHA512` | Advanced SIMD SHA512 instructions | Advanced SIMD SHA512 指令 | 为 Advanced SIMD 引入支持 SHA2-512 功能的指令集，提供 SHA-512 哈希算法的硬件加速能力。这些指令仅面向 A64 指令集，依赖 SHA1 和 SHA256 支持。 | Armv8.1 | — | 可选 |
| `FEAT_SM3` | Advanced SIMD SM3 instructions | Advanced SIMD SM3 指令 | 为 Advanced SIMD 引入支持中国国密算法 SM3 的指令集，提供 SM3 哈希算法的硬件加速能力。这些指令仅面向 A64 指令集。 | Armv8.1 | — | 可选 |
| `FEAT_SM4` | Advanced SIMD SM4 instructions | Advanced SIMD SM4 指令 | 为 Advanced SIMD 引入支持中国国密算法 SM4 的指令集，提供 SM4 分组加密算法的硬件加速能力。这些指令仅面向 A64 指令集。 | Armv8.1 | — | 可选 |
| `FEAT_UAO` | Unprivileged Access Override control | 非特权访问覆盖控制 | 在 PSTATE 中引入 UAO（Unprivileged Access Override）位。当 UAO 有效值为 1 时，特权软件使用非特权内存访问指令（如 LDTR/STTR）发起的访问将被视为特权访问，使特权代码可以方便地访问用户空间内存而无需切换权限级别。 | Armv8.1 | AArch64 | 可选（Armv8.2 起强制） |
| `FEAT_CONSTPACFIELD` | PAC algorithm enhancement | PAC 算法增强 | 增强指针认证（PAC）算法，允许实现在添加PAC时使用虚拟地址第55位来确定PAC字段的大小，即使未启用Top Byte Ignore（TBI）也同样适用，从而更灵活地利用地址空间中的空余位。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_EPAC` | Enhanced pointer authentication | 增强的指针认证 | FEAT_EPAC 扩展了指针认证（PAC）功能，允许对非规范地址执行 PAC 操作时将 PAC 字段置为 0，不过 Arm 已不推荐实现该特性。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_FPAC` | Faulting on AUT* instructions | AUT* 指令认证失败时触发故障 | FEAT_FPAC 扩展了 FEAT_PAuth2，使 AUT* 指令在指针认证失败时触发故障（fault）而非静默地返回错误值，从而增强了指针认证机制对内存安全漏洞的防护能力。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_FPACCOMBINE` | Faulting on combined pointer authentication instructions | 组合指针认证指令的故障 | FEAT_FPACCOMBINE 在 FEAT_FPAC 基础上进一步扩展，使执行组合指针认证（combined pointer authentication）的指令在认证失败时同样触发故障，增强了联合认证操作的安全性。 | Armv8.2 | — | 可选 |
| `FEAT_FPACC_SPEC` | Speculative behavior of pointer authentication instructions | 指针认证指令的推测行为 | FEAT_FPACC_SPEC 扩展了 FEAT_FPACCOMBINE，为指针认证指令引入一致的投机（speculation）影响行为，确保在投机执行场景下认证失败的处理方式保持确定性，防止基于投机执行的侧信道攻击。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_PACIMP` | Pointer authentication - IMPLEMENTATION DEFINED algorithm | 指针认证 — IMPLEMENTATION DEFINED 算法 | 允许在指针认证（PAC）计算中使用实现自定义（IMPLEMENTATION DEFINED）的密码算法，为芯片厂商提供灵活的 PAC 算法选择空间。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_PACQARMA3` | Pointer authentication - QARMA3 algorithm | 指针认证 — QARMA3 算法 | 为指针认证（PAC）引入 QARMA3 密码算法，作为 PAC 计算的标准算法选项之一，与 QARMA5 和 IMPLEMENTATION DEFINED 算法互斥。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_PACQARMA5` | Pointer authentication - QARMA5 algorithm | 指针认证 — QARMA5 算法 | 为指针认证（PAC）引入 QARMA5 密码算法，作为 PAC 计算的标准算法选项之一，与 QARMA3 和 IMPLEMENTATION DEFINED 算法互斥。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_PAuth` | Pointer authentication | 指针认证（PAuth） | 引入指针认证功能，在寄存器内容用作间接分支目标或 load 操作之前对其进行地址认证，要求实现恰好一种 PAC 算法（QARMA5、QARMA3 或 IMPLEMENTATION DEFINED），有效防范指针伪造攻击。 | Armv8.2 | AArch64 | 可选（Armv8.3 起强制） |
| `FEAT_PAuth2` | Enhancements to pointer authentication | 指针认证增强 | 增强指针认证功能，改变 PAC（指针认证码）嵌入指针的机制，提升指针认证的安全性和灵活性，在 Armv8.6 起成为强制特性。 | Armv8.2 | AArch64 | 可选（Armv8.6 起强制） |
| `FEAT_DIT` | Data Independent Timing instructions | 数据无关定时指令 | 引入数据独立时序（Data Independent Timing）机制，允许软件通过设置PSTATE.DIT标志，声明某段代码的执行时序不依赖于特定指令所操作的数据值，从而对抗基于时序的旁路攻击。 | Armv8.3 | AArch64+AArch32 | 可选（Armv8.4 起强制） |
| `FEAT_BTI` | Branch Target Identification | 分支目标识别 | 分支目标识别，通过在翻译表中标记受保护页（GP 字段）并引入 BTI 指令，防止 ROP/JOP 等控制流劫持攻击——只有 BTI 指令标记的位置才是合法的间接分支目标，否则触发 Branch Target 异常。 | Armv8.4 | AArch64 | 可选（Armv8.5 起强制） |
| `FEAT_E0PD` | Preventing EL0 access to halves of address maps | 阻止 EL0 访问地址映射的一半 | 阻止EL0访问地址映射中的半段地址空间，防止用户态代码通过推测执行探测高特权级的内存映射信息，与FEAT_CSV3配合使用以增强对推测执行侧信道攻击的防护。 | Armv8.4 | AArch64 | 可选（Armv8.5 起强制） |
| `FEAT_MTE` | Memory Tagging Extension | 内存标记扩展（MTE） | 内存标记扩展（MTE）提供运行时内存错误检测的架构支持，可始终开启地检测多类内存错误，有助于软件调试并消除内存不安全语言带来的安全漏洞。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_MTE2` | Memory Tagging Extension | 内存标记扩展 2 | 内存标记扩展（MTE）增强版本，在 FEAT_MTE 基础上进一步提供运行时内存错误检测的架构支持，用于软件调试和内存安全漏洞消除。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_RNG` | Random number generator | 随机数生成器 | 引入RNDR和RNDRRS两个系统寄存器，读取时分别返回64位随机数；其中读取RNDRRS会在生成随机数前触发重新播种（reseed），为软件提供架构级的随机数生成能力。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_RNG_TRAP` | Trapping support for RNDR/RNDRRS | RNDR/RNDRRS 的陷阱支持 | 为RNDR和RNDRRS寄存器的读操作引入EL3陷入支持，允许EL3固件拦截并管控低特权级对随机数生成器的访问。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_MTE3` | MTE Asymmetric Fault Handling | MTE 非对称故障处理 | 引入对 MTE 非对称标记检查故障（Tag Check Fault）处理的支持，允许对 load 和 store 操作配置不同的标记检查故障响应策略。 | Armv8.5 | AArch64 | 可选 |
| `FEAT_MTE_ASYNC` | Asynchronous reporting of Tag Check Fault | 标记检查故障的异步报告 | 支持将 MTE 标记检查故障以异步方式累积到 TFSRE0_EL1 或 TFSR_ELx 寄存器，提供低开销的异步内存标记错误上报机制。 | Armv8.5 | AArch64 | 可选 |
| `FEAT_MTE4` | Enhanced Memory Tagging Extension | 增强的内存标记扩展 | 增强型 MTE 扩展，新增规范标记检查（FEAT_MTE_CANONICAL_TAGS）、故障时上报全部非地址位（FEAT_MTE_TAGGED_FAR）、仅对 store 进行标记检查（FEAT_MTE_STORE_ONLY）以及地址标记禁用时的内存标记（FEAT_MTE_NO_ADDRESS_TAGS）等子功能。 | Armv8.7 | AArch64 | 可选 |
| `FEAT_MTE_PERM` | Allocation tag access permission | 分配标记访问权限 | 为 Stage 2 地址转换引入 NoTagAccess 内存属性，通过权限控制限制对分配标记（allocation tag）的访问，为虚拟化场景下的 MTE 提供更细粒度的安全隔离。 | Armv8.7 | AArch64 | 可选 |
| `FEAT_RME` | Realm Management Extension | 领域管理扩展（RME） | Realm管理扩展（RME）是Arm机密计算架构（Arm CCA）的核心组件，引入Root和Realm两种新安全状态及物理地址空间，支持内存粒度在不同物理地址空间之间动态转换，并提供粒度保护检查（GPC）机制，用于实现可动态创建、可证明且可信的执行环境（Realms）。 | Armv9.1 | AArch64 | 可选 |
| `FEAT_MEC` | Memory Encryption Contexts | 内存加密上下文 | 内存加密上下文（MEC）是 RME 扩展的组成部分，为所有物理地址空间提供内存加密上下文，并为 Realm 物理地址空间提供多个加密上下文以分配给各 Realm 虚拟机，由 Realm EL2 负责策略控制，Non-secure、Secure 和 Root 地址空间各拥有独立的加密上下文。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_GCS` | Guarded Control Stack Extension | 受保护控制栈扩展（GCS） | 引入受保护控制栈（Guarded Control Stack），在独立内存区域中存储函数返回地址和异常返回地址，防止其被篡改，从而增强控制流完整性保护。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_CPA` | Instruction-only Checked Pointer Arithmetic | 仅指令的受检指针算术 | 引入一组仅通过指令实现的受检指针算术（Checked Pointer Arithmetic）指令，允许软件在不启用全局系统模式的情况下，通过显式指令对指针合法性进行检查。 | Armv9.4 | AArch64 | 可选（Armv9.5 起强制） |
| `FEAT_CPA2` | Checked Pointer Arithmetic | 受检指针算术 | 引入可启用的受检指针算术（Checked Pointer Arithmetic）机制，能够检测并报告指针高8位的损坏以及乘法溢出导致的数组越界访问，帮助软件在运行时发现内存安全问题。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_PAuth_LR` | Pointer authentication instructions that allow signing of LR using SP and PC as diversifiers | 以 SP 和 PC 为多样化因子对 LR 签名的指针认证指令 | 引入允许使用 SP 和 PC 相对指令地址作为多样化因子（diversifier）对链接寄存器（LR）中 64 位值进行签名的指针认证指令，进一步加固返回地址保护。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_RME_GDI` | RME Granular Data Isolation extension | RME 颗粒数据隔离扩展 | 在RME系统中引入额外的GPT GPI编码，支持将非PE数据流（如DMA等外设）与PE的内存访问进行隔离，实现粒度级别的数据隔离保护。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_RME_GPC2` | RME Granule Protection Check 2 Extension | RME 颗粒保护检查 2 扩展 | 对RME粒度保护检查（GPC）机制进行扩展，引入仅非安全（Non-secure Only）GPI编码和物理地址空间禁用（Physical Address Space Disable）两种机制，支持更灵活的内存隔离模型。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_RME_GPC3` | RME Granule Protection Check 3 Extension | RME 颗粒保护检查 3 扩展 | 进一步扩展RME粒度保护检查，支持在内存映射中定义跳过GPT查找并直接应用默认配置的窗口，同时引入APAS系统指令，为支持内存侧动态PA空间关联的内存区域提供架构化的直接编程接口。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_Armv9_Crypto` | Armv9 Cryptographic Extension | Armv9 加密扩展 | Armv9 密码学扩展，在 AArch64 状态下提供加速加解密运算的硬件指令集，涵盖 AES、SHA1、SHA256、SHA512、SHA3、PMULL 等多种算法，受出口管制约束。 | — | AArch64 | 可选 |
| `FEAT_Crypto` | Cryptographic Extension | 加密扩展 | 提供ARM密码学扩展，通过SIMD向量寄存器加速AES、SHA1、SHA256等加密算法，并支持长多项式乘法，可显著提升加密/解密操作的计算性能。该扩展受出口许可管制。 | — | AArch64+AArch32 | 可选 |
| `FEAT_MTE_ASYM_FAULT` | Memory tagging asymmetric faults | 内存标记非对称故障 | 为 MTE 引入非对称标记检查故障处理支持，可针对 load 和 store 操作分别配置不同的故障响应行为，与 FEAT_MTE3 等价实现。 | — | AArch64 | 可选 |
| `FEAT_MTE_CANONICAL_TAGS` | Canonical Tag checking for Untagged memory | 对未标记内存的规范标记检查 | 为 MTE 引入对未标记内存的规范标记检查（canonical tag checking），确保对未标记内存的访问满足规范要求，属于 FEAT_MTE4 的子功能。 | — | AArch64 | 可选 |
| `FEAT_MTE_NO_ADDRESS_TAGS` | Memory tagging with Address tagging disabled | 禁用地址标记的内存标记 | 支持在地址标记（Address tagging）被禁用时仍可使用 MTE 内存标记功能，解耦内存标记与地址标记的依赖关系，属于 FEAT_MTE4 的子功能。 | — | AArch64 | 可选 |
| `FEAT_MTE_STORE_ONLY` | Store-only Tag Checking | 仅存储标记检查 | 支持仅对 store 操作进行 MTE 标记检查，而不对 load 操作执行标记验证，属于 FEAT_MTE4 的子功能，可用于降低读操作的标记检查开销。 | — | AArch64 | 可选 |
| `FEAT_MTE_TAGGED_FAR` | FAR_ELx on a Tag Check Fault | 标记检查故障时的 FAR_ELx | 在同步 MTE 标记检查故障发生时，支持将故障地址寄存器（FAR_ELx）中的全部非地址位一并上报，提供更完整的故障诊断信息，属于 FEAT_MTE4 的子功能。 | — | AArch64 | 可选 |

## 虚拟化

共 18 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_E2H0` | Programming of HCR_EL2.E2H | HCR_EL2.E2H 的编程控制 | 指示在实现了FEAT_VHE的系统中，HCR_EL2.E2H寄存器字段可以被编程为0（即可禁用EL2宿主模式）。若不支持本特性，则HCR_EL2.E2H为RES1，EL2宿主模式始终启用。 | Armv8.0 | AArch64 | 可选 |
| `FEAT_VHE` | Virtualization Host Extensions | 虚拟化主机扩展（VHE） | Virtualization Host Extensions，为 Non-secure 状态下的 Type 2 虚拟机监控器提供增强支持。VHE 允许宿主操作系统内核直接运行在 EL2，无需进行繁琐的上下文切换，从而降低 Type 2 虚拟化架构的开销。 | Armv8.0 | — | 可选 |
| `FEAT_VMID16` | 16-bit VMID | 16 位 VMID | 将虚拟机标识符（VMID）的位宽扩展至 16 位（原为 8 位），使系统可同时支持最多 65536 个虚拟机标识。该特性在 EL2 使用 AArch64 时生效，适用于需要运行大量虚拟机的大规模虚拟化场景。 | Armv8.0 | — | 可选 |
| `FEAT_EVT` | Enhanced Virtualization Traps | 增强的虚拟化陷阱 | FEAT_EVT 为 EL1 和 EL0 的缓存控制操作引入了附加陷入（trap）机制，通过 HCR_EL2 和 HCR2 寄存器进行配置，这些陷入独立于现有的控制机制，增强了虚拟化环境下对缓存操作的拦截能力。 | Armv8.2 | AArch64+AArch32 | 可选 |
| `FEAT_EVT2` | Enhanced Virtualization Traps 2 | 增强的虚拟化陷阱 2 | FEAT_EVT2 在 FEAT_EVT 基础上扩展，在 HCR_EL2 和 HCR2 中引入更多针对 EL1 和 EL0 系统控制操作的陷入，进一步细化了虚拟化层对低特权级系统寄存器访问的管控。 | Armv8.2 | AArch64+AArch32 | 可选 |
| `FEAT_NV` | Nested Virtualization | 嵌套虚拟化 | 提供嵌套虚拟化支持，允许 Guest Hypervisor 在 EL1 运行时感知不到自身所处异常级别，确保对 HCR_EL2.E2H 有效值的透明兼容。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_IDST` | ID space trap handling | ID 空间陷阱处理 | 规定当读取特性 ID 空间寄存器产生异常时，所有 AArch64 访问均以 EC 码 0x18 通过 ESR_ELx 上报，统一异常处理语义。 | Armv8.3 | AArch64 | 可选（Armv8.4 起强制） |
| `FEAT_NV2` | Enhanced nested virtualization support | 增强的嵌套虚拟化支持 | 增强嵌套虚拟化支持，通过将本应陷入 EL1/EL2 的寄存器访问重定向为内存访问（地址由 VNCR_EL2 决定），减少虚拟化层间的上下文切换开销。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_SEL2` | Secure EL2 | 安全 EL2 | 允许在 Secure 状态下实现 EL2，即安全虚拟化支持。启用 Secure EL2 后，会引入与其他安全转换机制格式相同的地址转换体系，使安全世界也能运行虚拟机监控程序。 | Armv8.3 | — | 可选 |
| `FEAT_NV2p1` | Enhanced nested virtualization support | 增强的嵌套虚拟化支持 | 进一步增强嵌套虚拟化支持，确保 EL1 寄存器中的控制位在对应 EL2 寄存器位为有状态时同样具有状态性，防止 Guest Hypervisor 状态丢失并允许 Host Hypervisor 正确模拟 EL2 环境。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_ECV` | Enhanced Counter Virtualization | 增强的计数器虚拟化 | FEAT_ECV 增强了通用定时器（Generic Timer）架构，提供虚拟计数器和物理计数器的自同步视图，支持事件流速率缩放，并允许 EL2 在 AArch64 状态下对 EL0/EL1 访问计数器和定时器寄存器进行陷入拦截，从而实现更灵活的定时器虚拟化管理。 | Armv8.5 | AArch64+AArch32 | 可选（Armv8.6 起强制） |
| `FEAT_ECV_POFF` | Enhanced Counter Virtualization Physical Offset | 增强计数器虚拟化物理偏移 | FEAT_ECV_POFF 在 FEAT_ECV 基础上，引入了 EL1/EL0 与 EL2/EL3 对物理时间视图之间的偏移量，使虚拟化环境中不同特权级别可呈现不同的物理时间基准。 | Armv8.5 | AArch64+AArch32 | 可选 |
| `FEAT_FGT` | Fine Grain Traps | 细粒度陷阱 | FEAT_FGT 引入了细粒度陷入（Fine-Grained Trap）机制，允许 EL2 对 EL1/EL0 访问单个或少量系统寄存器及指令进行拦截，并支持 EL3/EL2 对调试通信通道寄存器的陷入，从而为虚拟化场景提供更精细的系统寄存器访问控制。 | Armv8.5 | — | 可选 |
| `FEAT_TWED` | Delayed Trapping of WFE | 延迟陷阱 WFE | 引入对 WFE 和 WFET 指令陷入延迟的可配置支持。通过延迟陷入机制，虚拟机监控器可为客户机的 WFE 执行配置一段延迟时间窗口，避免频繁立即陷入 EL2，从而降低虚拟化环境下的陷入开销。 | Armv8.5 | — | 可选 |
| `FEAT_HCX` | Support for the HCRX_EL2 register | 支持 HCRX_EL2 寄存器 | 引入扩展 Hypervisor 配置寄存器 HCRX_EL2，在 HCR_EL2 基础上提供更多虚拟化控制选项，包括定义哪些操作会被陷入 EL2 处理。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_FGT2` | Fine-grained traps 2 | 细粒度陷阱 2 | FEAT_FGT2 扩展了 FEAT_FGT，引入了 HFGITR2_EL2、HFGRTR2_EL2、HFGWTR_EL2、HDFGRTR2_EL2 和 HDFGWTR2_EL2 等新的 Hypervisor 细粒度陷入寄存器，进一步增加了可拦截的系统寄存器和指令范围。 | Armv8.8 | — | 可选 |
| `FEAT_IDTE3` | Trapping ID register accesses to EL3 | 将 ID 寄存器访问陷阱到 EL3 | 引入对 ID 寄存器访问陷入 EL3 的支持，使安全固件能够监控和控制对架构特性标识寄存器的读取行为。 | Armv9.0 | AArch64 | 可选 |
| `FEAT_FGWTE3` | Fine-Grained Write Trap EL3 | EL3 细粒度写陷阱 | FEAT_FGWTE3 为 EL3 引入了对各 _EL3 系统寄存器写访问的细粒度陷入，通过 FGWTE3_EL3 控制寄存器进行配置，且控制位具有粘性（写 0 无效），增强了安全固件对寄存器写操作的防护。 | Armv9.4 | AArch64 | 可选 |

## 调试与追踪

共 28 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_Debugv8p1` | Debug v8.1 | Debug v8.1 | Armv8.1调试架构版本，在Armv8.0调试基础上进行了增量更新，通过DebugVer/CopDbg等字段标识其存在。 | Armv8.0 | — | 可选 |
| `FEAT_DoubleLock` | Double Lock | 双重锁（Double Lock） | 实现操作系统双锁（OS Double Lock）机制，在调试组件中提供双重锁定保护，防止未经授权的调试访问，以加强对调试接口的安全控制。 | Armv8.0 | — | 可选 |
| `FEAT_ETMv4` | Embedded Trace Macrocell version 4 | 嵌入式追踪宏单元 v4（ETM） | FEAT_ETMv4 表示处理器支持嵌入式跟踪宏单元（ETM）架构第 4 版，提供软件执行流的跟踪记录能力，用于程序调试和性能分析。 | Armv8.0 | — | 可选 |
| `FEAT_TRC_EXT` | Trace external registers | 追踪外部寄存器 | 表明处理器支持通过外部方式访问 ETMv4 或 ETE 的跟踪寄存器。外部调试工具可通过标准外部接口读写这些跟踪组件的寄存器，以实现非侵入式跟踪配置与控制。 | Armv8.0 | — | 可选 |
| `FEAT_TRC_SR` | Trace System registers | 追踪系统寄存器 | 表明处理器支持通过系统寄存器访问 ETMv4 或 ETE 的跟踪功能。软件可在 AArch64 和 AArch32 状态下，通过系统寄存器接口对跟踪单元进行编程和控制，实现自托管调试场景下的跟踪管理。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_Debugv8p2` | Debug v8.2 | Debug v8.2 | Armv8.2调试架构版本，增强了OS双锁（Double Lock）状态下寄存器的读取行为约束，扩展了异常捕获调试事件的定义以涵盖复位入口，并改善了安全状态下外部调试访问及PMU计数的软件控制机制。 | Armv8.1 | — | 可选（Armv8.2 起强制） |
| `FEAT_DoPD` | Debug over Powerdown | 掉电后调试（Debug over Powerdown） | 提供调试掉电（Debug over Powerdown）支持，将所有调试和PMU寄存器置于核心电源域，CTI寄存器置于调试电源域，允许在核心掉电期间通过可选的外部上电请求机制维持调试功能，同时不实现软件锁机制。 | Armv8.2 | — | 可选 |
| `FEAT_Debugv8p4` | Debug v8.4 | Debug v8.4 | Armv8.4调试架构版本，通过MDCR_EL3.{EPMAD, EDAD}字段控制非安全态对调试和PMU寄存器的访问，废弃软件锁机制，放宽非侵入式调试控制，并启用调试寄存器的安全与非安全视图分离。 | Armv8.3 | — | 可选（Armv8.4 起强制） |
| `FEAT_TRF` | Self-hosted Trace extensions | 自托管追踪扩展 | Self-hosted Trace Extension，通过系统寄存器在自托管调试环境中对跟踪进行控制。提供禁止特定异常级别和安全状态生成跟踪的控制机制、时间戳偏移配置，以及上下文同步指令 TSB CSYNC，防止跟踪操作访问与系统寄存器访问之间发生重排序。 | Armv8.3 | AArch64+AArch32 | 可选 |
| `FEAT_Debugv8p8` | Debug v8.8 | Debug v8.8 | Armv8.8调试架构版本，支持在产生异常捕获调试事件的异常处理过程中、PE进入暂停状态之前，允许再次触发新的异常，提升调试场景下异常嵌套的灵活性。 | Armv8.7 | AArch64+AArch32 | 可选（Armv8.8 起强制） |
| `FEAT_Debugv8p9` | Debug v8.9 | Debug v8.9 | Armv8.9调试架构版本，支持实现超过16个断点和16个观察点，将外部调试接口中的DBGBCR/DBGWCR寄存器扩展为64位，并新增DSPSR2寄存器以在调试状态下保存更完整的处理器状态。 | Armv8.8 | AArch64+AArch32 | 可选（Armv8.9 起强制） |
| `FEAT_ETE` | Embedded Trace Extension | 嵌入式追踪扩展（ETE） | FEAT_ETE（嵌入式跟踪扩展）提供了一种跟踪单元，用于记录处理器上软件控制流的详细信息，支持过滤特定代码区域或执行阶段，可用于调试和性能优化。 | Armv9.0 | AArch64+AArch32 | 可选 |
| `FEAT_ETEv1p1` | Embedded Trace Extension | 嵌入式追踪扩展 v1.1 | FEAT_ETEv1p1 在 FEAT_ETE 基础上扩展，为跟踪时间戳值提供更灵活的配置，增强了嵌入式跟踪的时序记录能力。 | Armv9.0 | AArch64+AArch32 | 可选 |
| `FEAT_TRBE` | Trace Buffer Extension | 追踪缓冲扩展（TRBE） | Trace Buffer Extension，在 PE 内部引入 Trace Buffer Unit（TBU）支持。启用后，跟踪单元产生的程序流跟踪数据将由 TBU 直接写入内存，而无需经过外部跟踪汇聚器，从而实现低开销的自托管程序追踪。 | Armv9.0 | AArch64+AArch32 | 可选 |
| `FEAT_BRBE` | Branch Record Buffer Extension | 分支记录缓冲扩展 | 分支记录缓冲扩展，提供专用硬件缓冲区用于捕获程序的控制流历史（分支记录），帮助性能分析工具还原代码执行路径。 | Armv9.1 | AArch64 | 可选 |
| `FEAT_ETEv1p2` | Embedded Trace Extension | 嵌入式追踪扩展 v1.2 | FEAT_ETEv1p2 进一步扩展 FEAT_ETE，增加了对 FEAT_RME（Realm 管理扩展）的跟踪支持，使 ETE 能够在 RME 环境中正常工作。 | Armv9.1 | AArch64+AArch32 | 可选 |
| `FEAT_BRBEv1p1` | Branch Record Buffer Extension version 1.1 | 分支记录缓冲扩展 v1.1 | 分支记录缓冲扩展第 1.1 版，在 FEAT_BRBE 基础上新增对 EL3 异常级别的分支记录能力，使安全固件的控制流也可被追踪。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_ABLE` | Address Breakpoint Linking Extension | 地址断点链接扩展 | 地址断点链接扩展，允许将观察点（watchpoint）与地址匹配断点关联，从而在特定地址范围的内存访问触发条件满足时精确命中调试事件。 | Armv9.3 | AArch64+AArch32 | 可选 |
| `FEAT_BWE` | Breakpoint and watchpoint enhancements | 断点与监视点增强 | 断点与观察点增强，引入基于包含范围和排除范围的地址断点类型，使调试器可以更灵活地定义触发条件。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_ETEv1p3` | Embedded Trace Extension version 1.3 | 嵌入式追踪扩展 v1.3 | FEAT_ETEv1p3 扩展了 FEAT_ETE，新增对外部调试请求（ETE External Debug Request）和跟踪输出使能（Trace Output Enable）的支持，进一步完善了嵌入式跟踪的控制能力。 | Armv9.3 | AArch64+AArch32 | 可选（后续版本起强制） |
| `FEAT_ITE` | Instrumentation Trace Extension | 插桩追踪扩展 | 引入仪器化跟踪扩展（Instrumentation Trace Extension），提供 TRCIT 指令将通用寄存器的值注入 ETE 跟踪流，方便软件在追踪数据中插入自定义标记信息。 | Armv9.3 | AArch64+AArch32 | 可选 |
| `FEAT_TRBE_EXT` | Trace Buffer external mode | 追踪缓冲外部模式 | Trace Buffer 外部模式扩展，允许外部调试器和自托管调试器共同使用 Trace Buffer Unit。引入了 TRBDEVARCH、TRBDEVID、TRBDEVID1 等外部寄存器，用于描述 TBU 实现的参数信息。 | Armv9.3 | AArch64+AArch32 | 可选 |
| `FEAT_TRBE_MPAM` | Trace Buffer MPAM extensions | 追踪缓冲 MPAM 扩展 | Trace Buffer MPAM 扩展，允许软件为跟踪数据配置独立的 MPAM PARTID 和 PMG 值。通过 TRBDEVID1 中的 PMG_MAX 和 PARTID_MAX 字段，可确定 MPAM 实现的参数范围，从而对跟踪数据的内存分区进行精细控制。 | Armv9.3 | AArch64+AArch32 | 可选 |
| `FEAT_BWE2` | Breakpoint and watchpoint enhancements 2 | 断点与监视点增强 2 | 断点与观察点增强第 2 版，在 FEAT_BWE 基础上新增能力：当软件访问地址落在用户指定区域之外时，可产生观察点异常或调试事件，支持反向地址范围监控场景。 | Armv9.4 | AArch64+AArch32 | 可选 |
| `FEAT_STEP2` | Enhanced Software Step Extension | 增强的软件单步扩展 | 增强型软件单步调试扩展，允许调试器控制 PE 在单步执行时实际运行的指令，而无需修改内存中的指令内容，从而提供更灵活的调试干预能力。 | Armv9.4 | AArch64+AArch32 | 可选（Armv9.5 起强制） |
| `FEAT_TRBE_EXC` | Trace Buffer Profiling exception extension | 追踪缓冲剖析异常扩展 | Trace Buffer Profiling Exception Extension，为跟踪缓冲区管理事件提供以 TRBE Profiling 异常形式上报的能力。当跟踪缓冲区发生特定管理事件时，可通过专用异常路径通知软件进行处理。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_TRBEv1p1` | Trace Buffer Extension version 1.1 | 追踪缓冲扩展 v1.1 | Trace Buffer Extension 1.1 版本，在原有 TRBE 基础上新增多项功能：支持对 TSB CSYNC 指令的细粒度陷入控制（需 EL2 与 FEAT_FGT）、EL2 可覆盖 TRBLIMITR_EL1.nVM 的控制位，以及对 TRBE Profiling 异常扩展（FEAT_TRBE_EXC）的支持。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_EDHSR` | Support for EDHSR | 支持 EDHSR | FEAT_EDHSR 引入了外部调试寄存器 EDHSR，用于保存调试事件的综合征（syndrome）信息，有助于在外部调试场景中精确定位和诊断调试事件的原因。 | — | — | 可选 |

## 性能监控与剖析

共 56 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_PCSRv8` | PC Sample-based Profiling extension | 基于 PC 采样的剖析扩展 | 引入基于 PC 采样的性能分析扩展（PC Sample-based Profiling），通过外部调试器以粗粒度、非侵入式的方式对程序执行进行性能剖析，适用于 Armv8.0 起的系统。 | Armv8.0 | — | 可选 |
| `FEAT_PMUv3` | PMU extension version 3 | PMU 扩展 v3 | 性能监视器扩展第3版（PMU v3），是一个可选的非侵入式调试组件，提供对处理器运行时事件进行计数和统计的能力，用于性能分析和调优。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3_EXT` | External interface to the Performance Monitors | 性能监视器外部接口 | 表明系统支持通过外部接口访问PMUv3和/或PCSRv8p2的寄存器，允许外部调试或监控工具直接读取性能监视器数据。 | Armv8.0 | — | 可选 |
| `FEAT_PMUv3_EXT32` | 32-bit external interface to the Performance Monitors | 性能监视器 32 位外部接口 | 指示外部性能监视器及CoreSight寄存器以32位寄存器形式实现，提供32位宽的外部访问接口。 | Armv8.0 | — | 可选 |
| `FEAT_PMUv3p1` | Armv8.1 PMU extensions | Armv8.1 PMU 扩展 | PMU v3的Armv8.1增强，将事件编号空间扩展至16位，在MDCR_EL2中新增HPMD位以禁止EL2的事件计数，并要求必须实现STALL_FRONTEND和STALL_BACKEND事件。 | Armv8.0 | AArch64+AArch32 | 可选 |
| `FEAT_PCSRv8p2` | PC Sample-based Profiling Extension | 基于 PC 采样的剖析扩展 | 将可选的基于PC采样的性能分析扩展（PC Sample-based Profiling）的控制与实现，从调试寄存器空间（ED*SR）迁移到性能监视器地址空间（PM*SR）中，使其可通过PMU寄存器访问。 | Armv8.1 | — | 可选 |
| `FEAT_SPE` | Statistical Profiling Extension | 统计剖析扩展（SPE） | 引入统计性能分析扩展（Statistical Profiling Extension），通过对体系结构指令或微架构操作进行随机采样，以非侵入方式对软硬件进行性能剖析，帮助开发者识别性能瓶颈。 | Armv8.1 | AArch64 | 可选 |
| `FEAT_MPAM` | Memory System Resource Partitioning and Monitoring Extension | 内存系统资源分区与监控扩展（MPAM） | 内存系统资源分区与监控扩展（MPAM），为内存系统组件提供对性能资源进行分区的控制框架，支持 v0p1、v1p0 和 v1p1 三个版本。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_MPAMv1p0` | Memory Partitioning and Monitoring Extension version 1.0 | MPAM 扩展 v1.0 | 引入 MPAM 扩展 1.0 版本的支持，提供完整的内存系统资源分区与监控功能，是 MPAM 标准实现之一。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_SPEv1p1` | Statistical Profiling Extension version 1.1 | 统计剖析扩展 v1.1 | Statistical Profiling Extension 的 1.1 版本，新增 Events 数据包中的对齐标志（Alignment Flag）支持及基于该事件的过滤功能，同时支持对 SVE 操作进行性能采样。通过 ID_AA64DFR0_EL1.PMSVer 字段标识。 | Armv8.2 | AArch64 | 可选 |
| `FEAT_AMUv1` | Activity Monitors Extension version 1 | 活动监视器扩展 v1 | 活动监视器扩展第 1 版，提供类似性能监视器子集功能的计数器组，面向系统管理（如功耗调度）而非调试与分析，减少软件开销。 | Armv8.3 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3p4` | Armv8.4 PMU extensions | Armv8.4 PMU 扩展 | PMU v3的Armv8.4增强，引入PMMIR_EL1（AArch64）和PMMIR（AArch32）寄存器，提供关于PMU实现能力的详细信息。 | Armv8.3 | AArch64+AArch32 | 可选 |
| `FEAT_AMU_EXTACR` | Activity Monitors External Control Register | 活动监视器外部控制寄存器 | 实现活动监视器（AMU）外部控制寄存器，用于管理对外部 AMU 寄存器的访问权限；若支持 FEAT_RME，则提供 AMROOTCR 寄存器以区分 Root/Realm/Secure/Non-secure 访问，否则提供 AMSCR 寄存器控制安全与非安全访问。 | Armv8.4 | — | 可选 |
| `FEAT_PMUv3p5` | Armv8.5 PMU extensions | Armv8.5 PMU 扩展 | PMU v3的Armv8.5增强，将事件计数器扩展为64位，并引入在安全状态（Secure state）、EL3和EL2中禁用周期计数器的机制，同时调整PMCR相关字段的行为。 | Armv8.4 | AArch64+AArch32 | 可选 |
| `FEAT_AMUv1p1` | Activity Monitors Extension version 1.1 | 活动监视器扩展 v1.1 | 活动监视器扩展第 1.1 版，在 v1 基础上新增对活动监视器事件计数器的虚拟化支持，并引入控制机制，允许禁止低于最高异常级别的软件访问辅助事件计数器。 | Armv8.5 | — | 可选 |
| `FEAT_HPMN0` | Setting of MDCR_EL2.HPMN to zero | MDCR_EL2.HPMN 可设为零 | 允许 hypervisor 将 MDCR_EL2.HPMN 设置为零，从而为客户操作系统提供零个 PMU 事件计数器，实现对 PMU 资源的严格隔离控制。 | Armv8.5 | AArch64+AArch32 | 可选 |
| `FEAT_MPAMv0p1` | Memory System Resource Partitioning and Monitoring extension version 0.1 | MPAM 扩展 v0.1 | 引入 MPAM 扩展 0.1 版本的支持，作为 MPAM 的一种轻量实现形式，提供内存系统资源分区与监控的基础能力。 | Armv8.5 | AArch64 | 可选 |
| `FEAT_MPAMv1p1` | Memory Partitioning and Monitoring extension version 1.1 | MPAM 扩展 v1.1 | 引入 MPAM 扩展 1.1 版本的支持，在 v1p0 基础上进一步增强内存系统资源分区与监控能力，依赖 FEAT_MPAMv1p0 实现。 | Armv8.5 | AArch64 | 可选 |
| `FEAT_MTPMU` | Multi-threaded PMU extensions | 多线程 PMU 扩展 | 为多线程 PMU 引入控制机制，允许禁用 PMEVTYPER 寄存器中的多线程事件计数（MT 位），在 Armv8.6 起，多线程事件计数仅在同时实现 FEAT_MTPMU 的多线程实现中受支持。 | Armv8.5 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3p7` | Armv8.7 PMU extensions | Armv8.7 PMU 扩展 | PMU v3的Armv8.7增强，支持在事件计数器无符号溢出时冻结PMU所有计数器，并允许在EL3单独禁止事件计数器和周期计数器的计数而不影响安全状态的其他异常级别。 | Armv8.6 | AArch64+AArch32 | 可选 |
| `FEAT_SPE_DPFZS` | Disable Cycle Counter on SPE Freeze | SPE 冻结时禁用周期计数器 | 引入控制机制，允许在统计性能分析缓冲区管理事件触发事件计数冻结时同步禁用周期计数，避免不必要的周期计数干扰性能分析结果。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_SPEv1p2` | Statistical Profiling Extensions version 1.2 | 统计剖析扩展 v1.2 | Statistical Profiling Extension 的 1.2 版本，新增在 SPE 缓冲区管理事件发生后冻结 PMU 事件计数器的控制机制，以及丢弃模式（Discard Mode），允许将所有 SPE 数据直接丢弃而不写入内存。 | Armv8.6 | AArch64 | 可选 |
| `FEAT_PMUv3_TH` | Event counting threshold | 事件计数阈值 | 为每个PMEVTYPER<n>_EL0寄存器引入阈值条件控制，使计数器只有在被追踪事件的计数满足指定阈值条件时才进行计数，支持更精细的性能事件过滤。 | Armv8.7 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3p8` | Armv8.8 PMU extensions | Armv8.8 PMU 扩展 | PMU v3的Armv8.8增强，将通用事件编号空间扩展至新的范围，并规范了写入保留或未实现事件编号时的行为（计数器停止计数且读回写入值）。 | Armv8.7 | AArch64+AArch32 | 可选 |
| `FEAT_SPEv1p3` | Statistical Profiling Extensions version 1.3 | 统计剖析扩展 v1.3 | Statistical Profiling Extension 的 1.3 版本，扩展了对 Tag 操作以及内存复制和内存设置（Memory Copy/Set）操作的采样支持，丰富了 SPE 可分析的指令类型。 | Armv8.7 | AArch64 | 可选 |
| `FEAT_PCSRv8p9` | Armv8.9 PC Sample-based Profiling Extension | Armv8.9 基于 PC 采样的剖析扩展 | 在基于PC采样的性能分析扩展基础上，引入暂停PC采样分析的机制，允许在特定场景下挂起和恢复采样操作。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3_EDGE` | PMU event edge detection | PMU 事件边沿检测 | 为PMU引入边沿检测逻辑，支持对事件阈值穿越（threshold crossing）进行计数，可与阈值特性配合使用以检测事件计数超过特定值的次数。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3_EXT64` | 64-bit external interface to the Performance Monitors | 性能监视器 64 位外部接口 | 指示外部性能监视器寄存器以64位寄存器形式实现（CoreSight管理寄存器仍为32位），提供更宽的64位外部访问接口。 | Armv8.8 | — | 可选 |
| `FEAT_PMUv3_ICNTR` | Fixed-function instruction counter | 固定功能指令计数器 | 为PMU引入固定功能的指令计数器，可直接统计处理器执行的指令数量，无需占用可编程事件计数器。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3_SS` | PMU Snapshot extension | PMU 快照扩展 | 定义与CoreSight PMU快照扩展兼容的实现定义快照扩展，允许在特定时刻原子性地捕获多个PMU计数器的状态。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3p9` | Armv8.9 PMU extensions | Armv8.9 PMU 扩展 | PMU v3的Armv8.9增强，提供对EL0进程的PMU事件计数器分配的更细粒度控制，支持任意组合计数器的清零，允许PMU直接请求PE进入调试状态，并更新了PMU事件定义。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_SPE_FDS` | Statistical Profiling data source filtering | 统计剖析数据源过滤 | 为 SPE 提供数据来源过滤能力，允许根据采样记录中的数据来源包（Data Source packet）的全部或部分字段对样本进行过滤，有助于分析内存访问来源分布。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_SPEv1p4` | Statistical Profiling Extension version 1.4 | 统计剖析扩展 v1.4 | Statistical Profiling Extension 的 1.4 版本，扩展了 Events 数据包内容以提供更多数据来源信息，并在 PMSEVFR_EL1 和 PMSNEVFR_EL1 中新增基于事件的采样记录过滤控制位，增强过滤精度。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_SPMU` | System Performance Monitors Extension | 系统性能监视器扩展 | System Performance Monitors Extension，为系统 PMU（即 PMU 框架中除标准 Performance Monitors Extension PMU 之外的其他 PMU）提供统一的架构系统寄存器和行为规范，使 PE 可以访问这些系统 PMU。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_SPE_SME` | Statistical Profiling extensions for SME | 面向 SME 的统计剖析扩展 | 为 SME 指令提供 Statistical Profiling Extension 支持，使软件在使用 SME 指令时也能被 SPE 采样分析。通过 PMSIDR_EL1.SME 字段标识是否实现。 | Armv9.2 | AArch64 | 可选 |
| `FEAT_EBEP` | Exception-based Event Profiling | 基于异常的事件剖析 | 引入基于异常的事件剖析（Exception-based Event Profiling）支持，将PMU计数器溢出以PMU剖析异常的形式上报，消除中断延迟与抖动对性能剖析精度的影响，从而生成更高质量的性能分析数据。 | Armv9.3 | AArch64+AArch32 | 可选 |
| `FEAT_MPAM_PE_BW_CTRL` | MPAM PE-side Bandwidth Controls | MPAM PE 侧带宽控制 | 为 MPAM 引入 PE 侧带宽控制支持，允许软件对处理器侧的内存访问带宽进行分区和限制，需依赖 MPAM v1p1 或 v0p1 实现。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_PMUv3_SME` | Performance Monitors extensions for SME | 面向 SME 的性能监视器扩展 | 扩展PMU以支持SME，提供过滤控制，使事件计数可区分Streaming SVE模式与Non-streaming SVE模式，便于在使用SME时进行精细化性能分析。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_PMUv3_TH2` | Performance Monitors event counter linking extension | 性能监视器事件计数器链接扩展 | 扩展PMU的阈值功能，允许将一个事件计数器配置为对两个事件的逻辑组合进行计数，实现更复杂的事件关联统计。 | Armv9.4 | AArch64+AArch32 | 可选 |
| `FEAT_SPE_ALTCLK` | Statistical Profiling alternate clock domain extension | 统计剖析备用时钟域扩展 | 为 SPE 提供替代时钟域支持，使其能够在对包含异步加速器（如 Streaming Mode Compute Unit，SMCU）的 PE 进行性能分析时，正确采集跨时钟域的时序数据。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_SPE_EFT` | Statistical Profiling extended filtering by type | 统计剖析按类型扩展过滤 | 扩展 SPE 的采样过滤功能，支持对浮点和 SIMD 操作进行有针对性的过滤分析，使开发者能够专门分析浮点和向量运算的性能特征。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_SPE_FPF` | Statistical Profiling floating-point and SIMD flag extension | 统计剖析浮点与 SIMD 标志扩展 | 扩展 SPE 记录的性能分析信息，在采样记录中标识所采样的标量浮点和 Advanced SIMD 指令，使开发者能够识别和分析浮点与向量运算的性能热点。 | Armv9.4 | AArch64 | 可选 |
| `FEAT_SPMU2` | System Performance Monitors Extension version 2 | 系统性能监视器扩展 v2 | System Performance Monitors Extension 的第 2 版，新增在单次操作中将系统 PMU 的多个事件计数器同时清零的功能，提高计数器管理效率。 | Armv9.4 | AArch64+AArch32 | 可选 |
| `FEAT_PMUv3_EXTPMN` | Reserving PMU event counters for external agents | 为外部代理保留 PMU 事件计数器 | 为外部代理提供预留PMU事件计数器的机制，允许外部系统独占特定计数器以进行外部事件统计，避免软件抢占。 | Armv9.5 | AArch64+AArch32 | 可选 |
| `FEAT_SPE_EXC` | SPE Profiling exception extension | SPE 剖析异常扩展 | 为 SPE 引入异常上报机制，支持将性能分析缓冲区管理事件以 SPE Profiling 异常的形式上报，便于软件以异常处理方式响应采样缓冲区满等事件。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_SPE_nVM` | Statistical Profiling physical addressing mode extension | 统计剖析物理寻址模式扩展 | Statistical Profiling Extension 的物理寻址模式扩展，允许使用物理地址或中间物理地址定义 Profiling Buffer，而非仅限虚拟地址。通过 ID_AA64DFR2_EL1.SPE_nVM 字段标识是否实现。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_SPEv1p5` | Statistical Profiling Extension version 1.5 | 统计剖析扩展 v1.5 | Statistical Profiling Extension 的 1.5 版本，新增对 PSB CSYNC 指令的精细粒度陷阱支持（需 EL2 和 FEAT_FGT），并引入 SPE 性能分析异常扩展（FEAT_SPE_EXC）和物理寻址模式扩展（FEAT_SPE_nVM）。 | Armv9.5 | AArch64 | 可选 |
| `FEAT_AMU_EXT` | External Activity Monitors | 外部活动监视器 | 支持通过外部接口访问活动监视器（Activity Monitors）寄存器，便于系统级工具对活动监视数据进行外部读取和管理。 | — | — | 可选 |
| `FEAT_AMU_EXT32` | 32-bit External Activity Monitors | 32 位外部活动监视器 | 活动监视器（AMU）外部寄存器以 32 位宽度实现，支持通过外部接口访问 AMU 计数器等寄存器。 | — | — | 可选 |
| `FEAT_AMU_EXT64` | 64-bit external Activity Monitors extension | 64 位外部活动监视器扩展 | 活动监视器（AMU）外部寄存器以 64 位宽度实现，支持通过外部接口访问完整精度的 AMU 计数器数据。 | — | — | 可选 |
| `FEAT_SPE_ArchInst` | Statistical Profiling architectural instruction sampling | 统计剖析架构指令采样 | 为 SPE 提供体系结构指令级采样能力，使性能分析单元以体系结构定义的指令为采样对象；若未实现该特性，SPE 则以微架构操作为采样单元。 | — | AArch64 | 可选 |
| `FEAT_SPE_CRR` | Statistical Profiling call return branch records | 统计剖析调用返回分支记录 | 扩展 SPE 的操作类型数据包，在采样记录中提供更详细的分支信息，以区分过程调用（call）和过程返回（return）类型的分支，辅助调用链性能分析。 | — | AArch64 | 可选 |
| `FEAT_SPE_ERnd` | Statistical Profiling random sampling at end of period | 统计剖析周期末随机采样 | 为 SPE 提供二级随机采样计数器（PMSICR_EL1.ECOUNT），在主采样计数器清零且启用随机偏移时使用，提供更精确可控的随机采样间隔机制，避免采样偏差。 | — | AArch64 | 可选 |
| `FEAT_SPE_FnE` | Statistical Profiling inverse event filter | 统计剖析反向事件过滤 | 为 SPE 提供反向事件过滤功能，允许根据采样事件包（Events packet）中指定位的反值对采样记录进行过滤，支持更灵活的性能事件筛选策略。 | — | AArch64 | 可选 |
| `FEAT_SPE_LDS` | Statistical Profiling data source packet generation | 统计剖析数据源数据包生成 | 表示统计性能分析单元（SPU）能够生成数据来源包（Data Source packet），在采样记录中记录被采样加载操作的数据实际来源（如 L1 缓存、L2 缓存、主存等）。 | — | AArch64 | 可选 |
| `FEAT_SPE_PBT` | Statistical Profiling previous branch target | 统计剖析前一分支目标 | Statistical Profiling Extension 的扩展功能，支持生成包含前一次已跳转分支目标地址的数据包，帮助性能分析工具追踪分支跳转行为。通过 PMSIDR_EL1.PBT 字段标识是否实现。 | — | AArch64 | 可选 |

## RAS 可靠性、可用性与可维护性

共 11 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_RAS` | Reliability, Availability and Serviceability (RAS) Extension | 可靠性、可用性与可维护性（RAS）扩展 | 引入可靠性、可用性与可维护性（RAS）扩展，包括错误同步屏障（ESB）指令、错误记录机制、错误同步事件以及外部中止的附加综合信息，提升系统的错误检测与处理能力。 | Armv8.0 | — | 可选（Armv8.2 起强制） |
| `FEAT_SpecSEI` | SError interrupt exceptions from speculative reads of memory | 来自推测性内存读取的 SError 中断异常 | 描述 PE 是否能够从内存的推测性读取（包括推测性指令预取）中产生 SError 中断异常，通过 ID_AA64MMFR1_EL1.SpecSEI 等字段标识该能力是否存在。 | Armv8.0 | — | 可选 |
| `FEAT_IESB` | Implicit Error Synchronization event | 隐式错误同步事件 | 在异常进入和返回时引入隐式错误同步事件，确保在异常边界处对可同步异步错误（如 SError）进行同步，提高 RAS 错误处理的可靠性。 | Armv8.1 | AArch64 | 可选 |
| `FEAT_RASv1p1` | RAS extension v1.1 | RAS 扩展 v1.1 | RAS扩展的v1.1版本，通过系统寄存器访问方式支持额外的ERR<n>MISC<m>寄存器，以及可选的RAS通用故障注入模型扩展，增强错误管理能力。 | Armv8.2 | AArch64+AArch32 | 可选 |
| `FEAT_DoubleFault` | Double Fault Extension | 双重故障扩展 | 引入双故障（Double Fault）扩展，提供错误异常的路由与屏蔽控制机制，允许系统软件更精细地管理RAS错误异常的处理流程。 | Armv8.3 | AArch64 | 可选 |
| `FEAT_ADERR` | Asynchronous Device Error Exceptions | 异步设备错误异常 | 引入对 Device 内存加载操作发生错误时的处理方式控制，允许系统配置该类错误以异步方式上报，而非强制精确同步处理，从而在性能与错误精度之间取得平衡。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_ANERR` | Asynchronous Normal Error Exceptions | 异步普通错误异常 | 引入对 Normal 内存加载操作发生错误时的处理方式控制，允许将此类错误配置为异步方式上报，提高系统在内存错误处理策略上的灵活性。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_DoubleFault2` | Double Fault Extension v2 | 双重故障扩展 v2 | 在FEAT_DoubleFault基础上提供更多错误异常路由与屏蔽控制选项，进一步增强EL1、EL2和EL3之间同步与异步错误异常的分发灵活性，同时依赖FEAT_SCTLR2的支持。 | Armv8.8 | AArch64 | 可选 |
| `FEAT_PFAR` | Physical Fault Address Register Extension | 物理故障地址寄存器扩展 | 引入物理故障地址寄存器（PFAR_ELx），用于记录同步外部中止或SError异常发生时的故障物理地址，便于系统进行精确的错误诊断与定位。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_RASv2` | RAS Extension v2 | RAS 扩展 v2 | RAS扩展的v2版本，引入错误组状态寄存器（ERXGSR_EL1）、控制RAS错误记录系统寄存器写操作陷入EL3的机制，以及ESR_ELx中用于错误异常的附加综合信息，进一步增强RAS功能。 | Armv8.8 | AArch64+AArch32 | 可选 |
| `FEAT_E3DSE` | Delegated SError exception injection | 委派 SError 异常注入 | 为EL3提供委托式SError注入（Delegated SError）机制，允许EL3向低特权级委托SError异常的注入，适用于固件与虚拟机监控器之间的错误传递场景。 | Armv9.4 | AArch64 | 可选 |

## 系统控制、异常与执行状态

共 39 项。

| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |
| --- | --- | --- | --- | --- | --- | --- |
| `FEAT_AA32EL0` | Support for AArch32 at EL0 | EL0 支持 AArch32 | 处理器支持在 EL0 异常级别运行 AArch32 状态，允许 32 位应用程序在用户态执行。 | Armv8.0 | — | 可选 |
| `FEAT_AA32EL1` | Support for AArch32 at EL1 | EL1 支持 AArch32 | 处理器支持在 EL1 异常级别运行 AArch32 状态，允许操作系统内核以 32 位 ARM 模式运行。 | Armv8.0 | — | 可选 |
| `FEAT_AA32EL2` | Support for AArch32 at EL2 | EL2 支持 AArch32 | 处理器支持在 EL2 异常级别运行 AArch32 状态，允许 Hypervisor 以 32 位 ARM 模式运行。 | Armv8.0 | — | 可选 |
| `FEAT_AA32EL3` | Support for AArch32 at EL3 | EL3 支持 AArch32 | 处理器支持在 EL3 异常级别运行 AArch32 状态，允许安全固件以 32 位 ARM 模式运行。 | Armv8.0 | — | 可选 |
| `FEAT_AA64` | PE uses AArch64 after last reboot | 上次复位后 PE 使用 AArch64 | 表示 PE 在最近一次重启后使用 AArch64 执行状态，是 64 位 ARM 架构模式支持的总体标识。 | Armv8.0 | — | 可选 |
| `FEAT_AA64EL0` | Support for AArch64 at EL0 | EL0 支持 AArch64 | 处理器支持在 EL0 异常级别运行 AArch64 状态，允许 64 位用户态应用程序执行。 | Armv8.0 | — | 可选（Armv9.0 起强制） |
| `FEAT_AA64EL1` | Support for AArch64 at EL1 | EL1 支持 AArch64 | 处理器支持在 EL1 异常级别运行 AArch64 状态，允许 64 位操作系统内核执行。 | Armv8.0 | — | 可选（Armv9.0 起强制） |
| `FEAT_AA64EL2` | Support for AArch64 at EL2 | EL2 支持 AArch64 | 处理器支持在 EL2 异常级别运行 AArch64 状态，允许 64 位 Hypervisor 执行。 | Armv8.0 | — | 可选 |
| `FEAT_AA64EL3` | Support for AArch64 at EL3 | EL3 支持 AArch64 | 处理器支持在 EL3 异常级别运行 AArch64 状态，允许 64 位安全固件（如 TrustZone Monitor）执行。 | Armv8.0 | — | 可选 |
| `FEAT_BigEnd` | Support for big-endian at EL1 and above | EL1 及以上支持大端 | 处理器在 EL1 及更高异常级别支持大端字节序（Big-endian），允许操作系统和 Hypervisor 以大端模式运行。 | Armv8.0 | — | 可选 |
| `FEAT_BigEndEL0` | Support for big-endian at EL0 | EL0 支持大端 | 支持在EL0特权级以大端字节序运行，允许用户态程序使用大端内存访问模式。若实现了FEAT_MixedEndEL0，则本特性也必然实现。 | Armv8.0 | — | 可选 |
| `FEAT_CHK` | Check Feature Status | 检查特性状态（CHK） | 引入CHKFEAT指令，使软件能够在运行时检测某些架构特性是否已被启用，便于在不同微架构上进行特性感知的代码路径选择。 | Armv8.0 | AArch64 | 可选（Armv9.4 起强制） |
| `FEAT_CP15SDISABLE2` | CP15SDISABLE2 | CP15SDISABLE2 | 提供实现定义的CP15SDISABLE2信号，当该信号置高时，可阻止对一组安全CP15寄存器的写入操作，与已有的CP15SDISABLE信号类似，仅在EL3以AArch32状态执行时有效。 | Armv8.0 | — | 可选 |
| `FEAT_CRC32` | CRC32 instructions | CRC32 指令 | 引入CRC32系列指令，支持对数据块执行循环冗余校验（CRC）计算，可用于数据完整性验证和错误检测场景，同时支持AArch64与AArch32状态。 | Armv8.0 | AArch64+AArch32 | 可选（Armv8.1 起强制） |
| `FEAT_EL0` | Support for execution at EL0 | 支持在 EL0 执行 | FEAT_EL0 表示处理器支持在 EL0（用户态）执行代码，这是 ARM 架构中最低特权级别，用于运行普通应用程序。 | Armv8.0 | — | 强制 |
| `FEAT_EL1` | Support for execution at EL1 | 支持在 EL1 执行 | FEAT_EL1 表示处理器支持在 EL1（操作系统内核态）执行代码，EL1 是运行富操作系统内核和设备驱动程序的特权级别。 | Armv8.0 | — | 强制 |
| `FEAT_EL2` | Support for execution at EL2 | 支持在 EL2 执行 | FEAT_EL2 表示处理器支持在 EL2（虚拟化层）执行代码，EL2 是 Hypervisor 运行的特权级别，用于实现虚拟机管理与隔离。 | Armv8.0 | — | 可选 |
| `FEAT_EL3` | Support for EL3 | 支持 EL3 | FEAT_EL3 表示处理器支持在 EL3（安全监控层）执行代码，EL3 是最高特权级别，用于运行安全固件和 Trusted Firmware，管理安全状态切换。 | Armv8.0 | — | 可选 |
| `FEAT_LittleEnd` | Support for little-endian at EL1 and above | EL1 及以上支持小端 | 为 EL1 及以上异常级别提供小端字节序（little-endian）配置支持，允许系统在这些特权级别以小端模式运行。 | Armv8.0 | — | 可选 |
| `FEAT_LittleEndEL0` | Support for little-endian at EL0 | EL0 支持小端 | 为 EL0（用户态）提供小端字节序（little-endian）配置支持，使应用程序可以在小端模式下运行。 | Armv8.0 | — | 可选 |
| `FEAT_MixedEnd` | Mixed-endian support | 混合端序支持 | 提供混合字节序（mixed-endian）配置支持，允许系统在大端和小端模式之间灵活切换，适用于 AArch64 和 AArch32 两种状态。 | Armv8.0 | — | 可选 |
| `FEAT_MixedEndEL0` | Mixed-endian support at EL0 | EL0 混合端序支持 | 为 EL0（用户态）提供混合字节序（mixed-endian）支持，允许应用程序以与高特权级不同的字节序运行，提升字节序配置的灵活性。 | Armv8.0 | — | 可选 |
| `FEAT_SCTLR2` | Extension to SCTLR_ELx | SCTLR_ELx 扩展 | 引入 SCTLR2_ELx 寄存器，作为现有 SCTLR_ELx 系统控制寄存器的扩展，提供对内存系统及整体系统行为的顶层控制能力。该特性仅支持 AArch64 状态，从 Armv8.9 起为强制实现。 | Armv8.0 | AArch64 | 可选（Armv8.9 起强制） |
| `FEAT_ASMv8p2` | Armv8.2 changes to the A64 ISA | A64 ISA 的 Armv8.2 变更 | Armv8.2 对 A64 指令集的汇编层面扩展，将 BFC 指令作为 BFM 的别名加入 A64，并要求汇编器实现 BFC 和 REV64 伪指令。 | Armv8.1 | — | 可选（Armv8.2 起强制） |
| `FEAT_FlagM` | Condition flag manipulation instructions | 条件标志操作指令 | 提供直接操作 PSTATE 条件标志位 {N, Z, C, V} 的指令，简化对处理器状态标志的显式读写操作。 | Armv8.1 | — | 可选（Armv8.4 起强制） |
| `FEAT_CNTSC` | Generic Counter Scaling | 通用计数器缩放 | 在内存映射计数器模块中引入缩放寄存器，允许将计数器实际生成的频率相对于计数器ID机制中报告的基础频率进行缩放，为需要不同时间粒度的系统提供灵活配置。 | Armv8.3 | AArch64+AArch32 | 可选 |
| `FEAT_ExS` | Context synchronization and exception handling | 上下文同步与异常处理控制 | FEAT_ExS 提供了一种机制，通过 SCTLR_ELx 寄存器中的字段控制异常进入和异常返回是否作为上下文同步事件（Context Synchronization Event），允许在特定异常级别上启用或禁用此行为以优化性能。 | Armv8.4 | AArch64 | 可选 |
| `FEAT_FlagM2` | Enhancements to flag manipulation instructions | 标志操作指令增强 | 在 FEAT_FlagM 基础上进一步扩展，提供在 PSTATE 条件标志格式（FCMP 指令使用）与另一种替代格式之间相互转换的指令。 | Armv8.4 | — | 可选 |
| `FEAT_WFxT` | WFE and WFI instructions with timeout | 带超时的 WFE 和 WFI 指令 | 引入带超时功能的 WFET 和 WFIT 指令。当虚拟计数器 CNTVCT_EL0 的值首次达到或超过指令中指定的值时，PE 将产生本地超时事件并唤醒，使等待指令可在超时后自动退出，避免无限期挂起。 | Armv8.6 | — | 可选（Armv8.7 起强制） |
| `FEAT_CSSC` | Common Short Sequence Compression instructions | 通用短序列压缩指令 | 引入一组通用短指令序列压缩（Common Short Sequence Compression）指令，利用通用寄存器优化常见短指令序列，包括整数最大值/最小值、绝对值和位操作等，以减少代码体积并提升性能。 | Armv8.7 | AArch64 | 可选（Armv8.9 起强制） |
| `FEAT_HBC` | Hinted conditional branches | 带提示的条件分支 | 引入带提示的条件分支指令 BC.cond，提供 PC 相对偏移的条件跳转，并向处理器提示该分支极少发生方向改变，有助于分支预测优化。 | Armv8.7 | AArch64 | 可选（Armv8.8 起强制） |
| `FEAT_NMI` | Non-maskable Interrupts | 不可屏蔽中断 | 引入不可屏蔽中断（NMI）和少屏蔽中断（LMI）机制，新增独立于 PSTATE.{I, F} 的中断屏蔽模式，以及 PSTATE.ALLINT 位、SCTLR_ELx 中的 NMI/SPINTMASK 控制位，支持更灵活的中断优先级管理。 | Armv8.7 | AArch64 | 可选（Armv8.8 起强制） |
| `FEAT_TIDCP1` | EL0 use of IMPLEMENTATION DEFINED functionality | EL0 使用 IMPLEMENTATION DEFINED 功能 | 在 EL1 和 EL2 引入控制位，用于捕获 EL0 对可能控制实现定义（IMPLEMENTATION DEFINED）功能的寄存器的访问。通过陷入机制，防止 EL0 代码直接使用或探测特定实现的私有功能，增强系统安全性。 | Armv8.7 | — | 可选（Armv8.8 起强制） |
| `FEAT_UINJ` | Injection of Undefined Instruction exceptions | 未定义指令异常注入 | 引入软件注入 Undefined Instruction 异常的支持机制。该特性允许软件主动向目标上下文注入未定义指令异常，可用于虚拟化、仿真或测试等需要精确控制异常的场景。 | Armv9.0 | AArch64 | 可选（Armv9.6 起强制） |
| `FEAT_SYSINSTR128` | 128-bit System instructions | 128 位系统指令 | 引入对自定义实现系统指令的 128 位输入支持，允许实现定义的系统指令接受 128 位宽的操作数，扩展系统指令的数据处理能力。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_SYSREG128` | 128-bit System registers | 128 位系统寄存器 | 引入对 128 位系统寄存器的读写支持，新增 MRRS 指令（将 128 位系统寄存器读入一对 64 位通用寄存器）和 MSRR 指令（将一对 64 位寄存器写入 128 位系统寄存器），并将 PAR_EL1、RCWMASK_EL1、多个 TTBR 等寄存器扩展为 128 位格式。 | Armv9.3 | AArch64 | 可选 |
| `FEAT_CMPBR` | Compare and Branch instructions | 比较并分支指令 | 为A64指令集引入一组比较并分支指令，将比较与条件跳转合并为单条指令，有助于减少代码体积并提升循环和条件分支的执行效率。 | Armv9.5 | AArch64 | 可选（Armv9.6 起强制） |
| `FEAT_SRMASK` | Bitwise System Register Write Masks | 按位系统寄存器写掩码 | 为 EL1 控制寄存器引入别名及按位写掩码（Bitwise Write Masks），从而减少将 EL1 系统寄存器访问陷入 EL2 的次数；同样为 EL2 寄存器提供等效的按位写掩码支持，简化虚拟化场景下的寄存器管理。 | Armv9.5 | AArch64 | 可选（Armv9.6 起强制） |
| `FEAT_AA32` | PE supports AArch32. | PE 支持 AArch32 | 处理器（PE）支持 AArch32 执行状态，可在 32 位 ARM 指令集模式下运行。 | — | — | 可选 |

