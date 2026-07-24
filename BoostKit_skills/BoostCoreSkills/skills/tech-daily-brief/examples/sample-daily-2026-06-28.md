# 每日简报 · 2026-06-28 · [compiler-mem]

> 关注集：compiler-mem（类型：GCC、LLVM、Go、Java、AI编译、内存库） ｜ 全局窗口：近 1 天（各维度智能子窗，周日清淡已放宽并标注） ｜ 整理时间：2026-06-28

## 今日全局脉络
- **[GCC·友商]** 海光 Model 8「Suzhou」(`c86-4g-m8`) 推进 GCC 17（06-23）；同期 Intel 一行改 generic x86 误预测代价，SPEC 544.nab_r 在 Granite Rapids/Zen5 **+12%**（06-24）——上游主线同时承载国产 x86 enablement 与跨厂商 generic 调优。
- **[LLVM·鲲鹏]** 鲲鹏 950 核(HIP12)的 AArch64 定义已合入 LLVM 主线（PR #203446，Armv8.7-A+SVE2），并落地跨架构位操作 intrinsic `llvm.pext/pdep`（#200570）统一 x86 BMI2 与 AArch64 bext/bdep。
- **[GCC·codegen]** aarch64 后端两条性能向提交：SVE partial-mode `vec_init` 从栈往返改 `insr` 寄存器插入（06-24）、多发射核 dispatch 调度修回归被救活（06-26）。
- **[AI编译]** 张量编译栈本周末补「可伸缩向量化 + CPU 后端」：TVM 落地 scalable Ramp lowering（SVE/RVV 抓手）；AMD 借 PyTorch 官博推 TokenSpeed-Kernel（MI355X，06-25）。
- **[Go]** Go 1.27(dev) SIMD 实验密集落地：`archsimd` 补齐 arm64 Neon 128-bit；runtime malloc 快路径重构落 master（统一 fast/slow + 提前 acquirem）。
- **[Java]** OpenJDK 上游压在 C2 JIT：Vector API/Panama codegen 正确性连修 4 处；Valhalla「Better Tools for Value Types」（06-21）。
- **[内存库]** jemalloc dev 06-28 仍在 push（SEC-in-PAC 砍锁竞争 + 修 struct 布局回退）；Linux 7.2 合并窗 SLUB 快路径 + 类型感知 allocation tokens；ISMM 2026 九篇 4 篇直击分配器/大页/CXL/CHERI。

## 目录

[GCC](#gcc) ｜ [LLVM](#llvm) ｜ [Go](#go) ｜ [Java](#java) ｜ [AI编译](#ai编译) ｜ [内存库](#内存库)

## GCC

### 📄 论文（近 7 天）

- **AutoPass: Evidence-Guided LLM Agents for Compiler Performance Tuning** ｜ arXiv:2606.20373（cs.SE/cs.AI，v1 2026-06-18）｜ [链接](https://arxiv.org/abs/2606.20373)
  - 用多智能体 LLM 查询编译器内部状态、分析 IR，靠运行时反馈迭代调 pass 序列与参数（免训练/免微调）；在 LLVM `-O3` 之上，嵌入式 ARM64 提速 1.117x、x86-64 提速 1.043x（作者称，已直取 abs 页核对）。
  - 相关性：命中「性能优化（pass 调度/自动调优）」+「Arm/AArch64」；虽以 LLVM 为载体，pass 排序与 cost 调参的思路对 GCC 的 `-O3` 调优、PGO 同样适用。
  - 日期说明：v1 2026-06-18 略早于近 7 天窗（06-21），因正中性能+ARM64 关注点破窗收录、已核 abs 页。注：检索快照另提到「PGO 对 ARM64 SLP 向量化覆盖率」的具体数字，但 abs 页摘要未确认，故不采纳那组数字。

- **Axon: A Synthesizing Superoptimizer for Tensor Programs** ｜ arXiv:2606.26344（cs.PL/cs.CL/cs.PF，2026-06-24）｜ [链接](https://arxiv.org/abs/2606.26344)
  - 面向 tile 化 AI 加速器：用程序综合枚举语义等价变体、SMT 验证正确性，再按实测择优 tiling / 指令选择 / 数据布局 / 算子融合；abs 未给具体加速比。
  - 相关性：超优化 / 指令选择 / 数据布局方法学，对做 codegen cost model 的人有参考；但靶子是 AI 加速器而非通用 CPU 后端，对 GCC aarch64 直接相关性偏弱（列为次条）。

### 📰 资讯（近 1 天空 → 友商命中破窗近 7 天）

> 周日，GCC 一手博客 / 项目页（gcc-16/17 changes.html）近 1 天无新发。以下 2 条为命中「友商」关注点、按 v3 破窗到近 7 天收录的 Phoronix 报道；Phoronix WebFetch 返回 403、web.archive WebFetch 被禁，正文细节据搜索快照整理、发布日经 Wayback CDX 核对。

### 2026-06-24 ｜ 改一行 x86 generic 调优表，SPEC nab_r 在 Granite Rapids / Zen5 上 +12%
- **URL**：https://www.phoronix.com/news/GCC-x86-Generic-Mispredict
- **背景**：Intel 工程师 Lili Cui 发现现代 CPU 流水线更深、分支误预测代价更高，而 generic x86 tuning 表里的 misprediction cost 偏低。
- **要点**：
  - 把 generic 调优的 branch mispredict scale ×3（一行改动），SPEC CPU 2017 的 544.nab_r 在 Intel Granite Rapids 上 +12.7%、AMD Zen 5 上 +12.1%。
  - 走 generic tuning（非特定 `-march`），对未指定微架构编译的二进制普遍受益；预计随 GCC 17（2027）落地。
- **启发**：做鲲鹏 / aarch64 tuning 的同理可复盘 aarch64 generic cost 表里 `branch_cost` / 误预测项是否同样偏低——深流水核上调高误预测代价，可能同样换来 SPEC 收益。

### 2026-06-23 ｜ 海光 Model 8「Suzhou」（c86-4g-m8）进入 GCC 编译器
- **URL**：https://www.phoronix.com/news/Hygon-c86-4g-m8-Suzhou-GCC
- **背景**：海光 Family 18h Model 8（代号 Suzhou，Model 7「Chengdu」的继任者）新一代 x86 处理器的初始 enablement 上游到 GCC。
- **要点**：
  - 目标进入 GCC 17；ISA 能力含 AVX-512 等现代特性。
  - 紧随 2026-04 月底已合入 GCC 17 的海光 C86-4G-M4/M6/M7（Chengdu）系列；LLVM/Clang 侧亦已跟进 c86-4g 目标。
  - 发布日核对：Wayback CDX 首快照 2026-06-23，搜索快照亦标「Written on 23 June 2026」。
- **启发**：友商把自家 CPU 的 `-march`/`-mtune` 持续往上游主线推，是判断其产品节奏与编译器生态投入的风向标；做国产化工具链对标可跟踪 GCC i386 后端里 Hygon family 的 march 串演进。

### 💻 上游代码（近 1 天空 → 放宽近 7 天）

> gcc-mirror/gcc 的 `gcc/config/aarch64` 路径近 1 天（06-27/06-28，周日）无新提交。以下取近 7 天（06-24..06-26）落 master 的 aarch64 提交，入窗以 committer 日为准，日期逐条经 GitHub API commit 数据核对，链接用全 40 位 sha。

- **AArch64/SVE：优化 partial SVE 向量模式的 vec_init** ｜ [b3acc5dd98f44d152c9ac3bef9f26ab2d3fecef1](https://github.com/gcc-mirror/gcc/commit/b3acc5dd98f44d152c9ac3bef9f26ab2d3fecef1)（作者写作 2026-02-10，合入 2026-06-24）
  - 改了什么：让 `vec_init<mode><Vel>` 接受全部 SVE 向量模式（含 VNx8QI/VNx4QI/…/VNx4BF 等 partial 模式），`aarch64_sve_expand_vector_init` 相应处理 partial 模式；`vec_shl_insert_<mode>` 由 SVE_FULL 放宽到 SVE_ALL。
  - 为什么重要 / 对 Arm·性能的意义：当 BB（基本块）SLP 向量化扩展到 predicated tail 后会尝试更多 store，但旧 cost model 假设 `vec_init` 廉价、实际却生成一串经 4 个栈临时槽的「写-改-读」`st1b/strb/ld1b` 序列；改后编成 `mov z31.b, w0` + 3×`insr`，从栈往返退化为寄存器内插入——直击 SVE codegen 热路径与 cost model 偏差。指令级看：`insr` 把标量插进向量，省去经内存往返的 load-to-use 停顿（注：作者自评「尚非最优但已是大改进」）。

- **AArch64：让 dispatch 调度在多发射核上重新可达** ｜ [d90c9f7ae7bf07902954265d62cfa679a7183e0c](https://github.com/gcc-mirror/gcc/commit/d90c9f7ae7bf07902954265d62cfa679a7183e0c)（作者 2026-06-21，合入 2026-06-26）
  - 改了什么：r16-4079 引入的 aarch64 dispatch 调度此前因 `choose_ready()` 只在 `dfa_lookahead<=0` 或首条 ready 为 SCHED_GROUP_P 时才走 dispatch 路径，叠加 r16-6155 让 SCHED_GROUP_P 绕过 dispatch，结果多发射核上 DFA lookahead 路径被优先、dispatch 调度实际被关闭。本补丁在 `aarch64_sched_first_cycle_multipass_dfa_lookahead` 加 `IS_DISPATCH_ON` 判断，dispatch 启用时返回 0，让 dispatch 路径重新可达。
  - 为什么重要：dispatch 调度面向多发射 aarch64 核的发射端口建模，是指令调度对宽发射微架构的关键开关；这是一次「修回归、把已落地特性救活」的修补，对依赖 dispatch 调度的 tuning model（鲲鹏 / Neoverse 类宽发射核）直接相关。

- **aarch64：为 sub-64-bit AdvSIMD 向量拆分 r→w move [PR125716]** ｜ [4c63fdea7468ff398e8bc6fac5c56fc51123a98c](https://github.com/gcc-mirror/gcc/commit/4c63fdea7468ff398e8bc6fac5c56fc51123a98c)（作者 2026-06-23，合入 2026-06-25）
  - 改了什么：给 `*aarch64_simd_mov<mode>` 为 VSUB64 类型补 `(?w,r)` 备选，修复在 GP↔FP 传输代价为 2 时、V2HI 等 sub-64-bit 向量的 reg-reg 传输缺 (w,r) 备选而在 reload 阶段崩溃；新增专用 JSON tuning 文件保证 GP2FP cost=2 的测试（混合 PR125716/PR125947 用例）。
  - 为什么重要：correctness 修复（ICE），但牵涉 LRA/reload 在传输代价=2 这个「魔法值」下不再尝试其他 reload 的行为（代码引 `lra-constraints.cc:4245`）——对自定义 tuning model 调 GP2FP 代价的 aarch64 目标是真实雷区。

- **target hook `reassociation_width` 改吃 tree_code（plumbing，触及 aarch64/loongarch/i386 等）** ｜ [92d206fab98c71b25325399fc8c053c3caa8ddce](https://github.com/gcc-mirror/gcc/commit/92d206fab98c71b25325399fc8c053c3caa8ddce)（合入 2026-06-25）
  - 改了什么：`reassociation_width` target hook 形参从 `unsigned int` 改成 `tree_code`，前向声明 `enum tree_code`，同步改 aarch64/loongarch/mips/rs6000/i386 各后端实现并修 i386 端 bogus 比较。
  - 为什么重要：纯接口 plumbing，本身不改性能；但 reassociation 宽度直接影响浮点/整数运算树的重结合并行度，后端据此返回 width——为后续各后端按指令类型（而非笼统）细化 reassociation 宽度铺路。

- **gcc-patches 评审中（2026-June 归档，未逐封核日期，低置信）** ｜ [thread 索引](https://gcc.gnu.org/pipermail/gcc-patches/2026-June/thread.html)
  - 正在评审、尚未落 master 的 aarch64 高相关线程：SVE2p3/SME2p3 dot product 与 conversion intrinsics、F16F32DOT、FEAT_FPRCVT、range prefetch intrinsic（Armv9.x 新 ISA enablement）；「Adjust alignment tunings for Olympus」「Adjust vectorizer loads+store issue info for Olympus」（Arm Olympus 核 tuning）；「Extend BB SLP vectorization to use predicated tails」（即上面 vec_init 优化的上层动机）。
  - 友商侧：RISC-V「Add XuanTie C908 tuning and scheduler model」（平头哥玄铁 C908 调度模型）。
  - 说明：pipermail thread 索引不提供可靠 per-message 日期，以上仅据 6 月归档线程标题、未逐封核对发布日，低置信；已落 master 的 vec_init / AdvSIMD 拆分见上方提交（日期已核）。

## LLVM

### 📄 论文（近 7 天）

- **Reading AI Model Compilation in MLIR Through the Lens of Formal Theories** ｜ arXiv:2606.25244 ｜ [链接](https://arxiv.org/abs/2606.25244)
  - 把 MLIR 的工程概念（IR 抽象、interface、match-and-rewrite、flow analysis、type conversion、staged lowering）一一对应到形式理论（项重写系统、精化演算、抽象解释），用来回答"一个抽象的'完备'到底意味着什么、工程取舍在哪偏离了理想设计"。
  - 相关性：MLIR 内编译是本类型特有关注点；为做张量/AI 编译下降（lowering）正确性与抽象边界提供理论框架。（abs 页已核：作者 Javed Absar，提交 2026-06-24）

- **Axon: A Synthesizing Superoptimizer for Tensor Programs** ｜ arXiv:2606.26344 ｜ [链接](https://arxiv.org/abs/2606.26344)
  - 用程序综合 + SMT 求解自动从语义生成目标指令、免手写规则地做张量 kernel 超优化：探索 tiling 配置、算子融合降访存、计算图上的代数变换，面向 tile-based AI 加速器程序。
  - 相关性：超优化（superoptimizer）是编译器关键路径研究方向；abstract 未给量化加速比（作者：Kothari/Zhu/Kroening/Sung，提交 2026-06-24，已核）。

- **（低置信·会议）The Data Must Flow (To Vector Processors): Searching Program Variants to Improve Compiler Auto-Vectorization** ｜ ICS'2026 ｜ [检索来源](https://spcl.inf.ethz.ch/Publications/.pdf/vector_paper.pdf)
  - 方向：搜索程序变体以提升编译器自动向量化能力，评测覆盖 x86 与 **AArch64**（用到 NVIDIA LLVM Grace 工具链）。搜索摘要称 SVE 上 geomean 1.94× 加速，**该数字未直取原文核对，不作确证**。
  - 相关性：正中"LoopVectorize + AArch64 + LLVM 工具链"；**仅据 WebSearch 摘要、未核原文标题/日期/数字，标低置信**。

### 📰 资讯（近 1 天 → 周末放宽近 3–7 天）

### 2026-06-24 ｜ LoopVectorizer 要做"再向量化"：把定长 NEON 循环升宽到可伸缩 SVE（RFC）
- **URL**：https://discourse.llvm.org/t/rfc-re-vectorisation-to-wider-vectors-in-loopvectorizer/91071
- **背景**：现有 LoopVectorizer 会跳过"已经在用定长向量（如 NEON）"的循环；存量 NEON 代码量大，想无源码改写地迁到 SVE。（gbossu 发起，cc fhahn / david-arm；06-15 发帖、**06-24 仍活跃**——正是 playbook 提醒的"老帖新活跃 RFC"）
- **要点**：
  - 提议新增 opt-in 模式 `-vectorize-vector-loops`，对已是定长向量的循环再做一次向量化、升到 scalable 向量。
  - 实现思路：把定长向量当作更宽 scalable 向量里的"段（segment）"，如 `<8 x i16>` NEON load 变 `<vscale x 8 x i16>` 的 SVE 操作。
  - 原型刻意保守：关闭 tail folding、拒绝 scalable 输入（避免对已 scalable 的代码重复向量化）；**RFC 未给 benchmark 数字**。
- **启发**：做鲲鹏/AArch64 性能的读者值得跟进——这是把存量 NEON 资产平滑迁 SVE 的官方路线信号；HIP12(Kunpeng 950) 带 SVE2，落地后对定长向量热循环可能直接受益，建议关注其 cost model 如何判定"升宽是否划算"。

### 2026-06-22 ｜ LLVM Weekly #651：HIP12、pext/pdep、22.1.8、ClangIR 93%
- **URL**：https://llvmweekly.org/issue/651
- **背景**：本周唯一新周报 digest（#652 预计约 06-29）；把上周散落的高价值提交聚合，正好覆盖本类型两条专项靶心。
- **要点**：
  - **鲲鹏 HIP12 AArch64 核初始定义**合入（详见 💻 上游）；**`llvm.pext`/`llvm.pdep` 跨架构位操作 intrinsic** 合入。
  - **LLVM 22.1.8** 发布（tagged 2026-06-16，例行 patch 版）。
  - ClangIR 上游进度："`-fclangir` 构建的 clang 现可编译约 93% 的翻译单元"。
  - **BOLT：并行 DWARF 处理**（d3ac9b5），大二进制 debug section 更新提速。
  - 其他：CHERI capability 对齐支持（7dc09d0）、RISC-V Core-V XCV 厂商扩展上游、CMake 最低版本拟提到 3.31。
- **启发**：把 HIP12 与 pext/pdep 当"鲲鹏 950 LLVM 使能起步"一并读——前者给出 -mcpu、后者给出可移植位操作原语（在 SVE2 BitPerm 上可原生落地）；做 BOLT 大二进制优化的可关注并行 DWARF 这条提速。

### 2026-06-25~27 ｜ discourse 近 3 天其他活跃 RFC 速览
- **URL**：https://discourse.llvm.org/latest （以下逐条 topic 未单独抓取，日期据 /latest 列表）
- **背景**：周末严格近 1 天资讯几乎为空，按 `/latest` 最近活跃补窗内动态。
- **要点**：
  - **[RFC] LoopSplitUtils**（Loop Optimizations，06-26）：通用循环迭代空间切分工具——循环优化基础设施。
  - **[RFC] [LTO] [lld] LTO with linker scripts, implemented**（IR & Optimizations，06-25，14 回复）：让 LTO 与 linker script 共存——命中共享关注点 LTO。
  - **[RFC] Yet another strict FP**（06-26，35 回复，1448 浏览，本周热帖）：严格浮点语义再讨论。
  - **[RFC] CopySanitizer (CSan)**（06-25，16 回复）：运行时检测不必要的对象拷贝——性能诊断向。
- **启发**：LTO-with-linker-scripts 与 LoopSplitUtils 两条对做 footprint/LTO 与循环变换的读者有跟进价值；本条为窗内活跃度速览，深读请进各 topic。

### 💻 上游代码（近 1 天 → 周末放宽近 7 天）

> 专项靶心两条（HIP12 / pext-pdep）均 2026-06-16 合入，略超 7 天窗，因正中本类型专项关注点按里程碑放宽收录、已标实际日期；其余为 06-25/26 在窗提交。

- **鲲鹏 HIP12（Kunpeng 950）AArch64 核：初始支持合入主线** ｜ 2026-06-16 ｜ PR [#203446](https://github.com/llvm/llvm-project/pull/203446) ｜ commit [`d87350127163aab4bb710d284e4d0ca97d2652f9`](https://github.com/llvm/llvm-project/commit/d87350127163aab4bb710d284e4d0ca97d2652f9)
  - 改了什么：新增 `-mcpu=hip12`，定位 **Kunpeng 950 处理器、Armv8.7-A**；启用 **SVE2（BitPerm/AES/SHA3/SM4）**、crypto（AES/SHA/SM3/SM4）、AdvSIMD（NEON/BF16/dotprod/matmul）、PMU/SPE/BRBE/ETE/TRBE、PAC/RME；cache line 64B、CPU part `0xd06`。改 `AArch64Processors.td`/`AArch64Subtarget.cpp`/`TargetParser/Host.cpp` 等 10 文件。
  - 为什么重要 / 对本方向(及 Arm·性能)的意义：**这是 LLVM 侧使能鲲鹏 950 的第一步**，但目前**仅 core 定义**——调度模型暂借 `NeoverseV2Model` 占位（注释 TODO 留专属 hip12 模型）、tuning 仅给函数对齐 16B/循环对齐 4B/VScale=2/简化 tail-folding，**专属 cost/sched 模型与深度调优未到位**。reviewer（jthackray/bryanpkc/davemgreen）快速批准，共识是"初始核定义先合、调优后补"。做鲲鹏性能的读者：现在 `-mcpu=hip12` 能编但还吃 NeoverseV2 的调度画像，针对性收益要等后续模型。

- **跨架构位操作 intrinsic：`llvm.pext` / `llvm.pdep`** ｜ 2026-06-16 ｜ PR [#200570](https://github.com/llvm/llvm-project/pull/200570) ｜ commit [`bf8b7787f96a9e6d42c5fc4f49c25352b81e90cb`](https://github.com/llvm/llvm-project/commit/bf8b7787f96a9e6d42c5fc4f49c25352b81e90cb)
  - 改了什么：引入 `llvm.pext`（按 mask 抽取位并低位紧凑）/`llvm.pdep`（把低位按 mask 散布），满足 `pdep(pext(v,m),m) == v & m`。**x86-64 下降到 BMI2 PEXT/PDEP，AArch64 下降到 bext/bdep（SVE2 BitPerm），无原生指令目标走 `TargetLowering` 标量展开兜底**。命名经讨论从 `bext/bdep` 改名为 `pext/pdep`，避让 RISC-V 单比特 `bext` 与计划中的 `bitextract` 一等指令。
  - 为什么重要 / 对本方向(及 Arm·性能)的意义：位操作密集 codegen（位打包/网络协议/压缩/位棋盘）从此有**可移植 IR 原语**，前端无需手写架构内联汇编。与 HIP12 呼应——鲲鹏 950 带 **SVE2 BitPerm**，这两条 intrinsic 在该核上可原生落 `bext/bdep`，是"使能 + 可用原语"配套到位的信号。

- **AArch64：带 reduction 的小循环最大 interleave 因子提到 4** ｜ 2026-06-26 ｜ PR [#205612](https://github.com/llvm/llvm-project/pull/205612)（commit 短 sha `d445267`，作者 davemgreen）
  - 改了什么：对**含无序 reduction 且 VF ≤ 4** 的循环，把 AArch64 默认最大 interleave 因子从 2 提到 4；其余情况不变，避免对已高度向量化的循环过度展开。
  - 为什么重要 / 对本方向(及 Arm·性能)的意义：小 reduction 循环有多条独立累加流可并行，提 interleave 直接吃 ILP——对 AArch64 reduction 吞吐是实打实的 codegen 改进（commit 未给 benchmark 数字，限定 VF≤4 即为避免"过度 unroll 反降速"）。做点积/归约热循环的可留意。

- **AArch64：修正 Cortex-A510 LDn（结构化向量 load）调度信息** ｜ 2026-06-25 ｜ PR [#205518](https://github.com/llvm/llvm-project/pull/205518) ｜ commit [`647c29886973c7111a32702e3c7a5ccc33a9feeb`](https://github.com/llvm/llvm-project/commit/647c29886973c7111a32702e3c7a5ccc33a9feeb)
  - 改了什么：A510 上 LD1/LD2/LD3/LD4 各元素结构/数据类型的 latency/throughput 此前与 A510 Software Optimization Guide 不符，按官方优化指南校正 cycle 数，并按 C1 CPU 风格重排/重命名定义。
  - 为什么重要 / 对本方向(及 Arm·性能)的意义：调度模型是 AArch64 性能画像基石——LDn 时延/吞吐报错会让指令调度与 cost model 系统性误判；校准后编译器对 A510 的性能预测更贴硬件。这类"对齐官方优化指南"的修正，正是 HIP12 后续要补的专属调度模型的范式。

- **AArch64 SVE：补 MLA 乘加的可交换 instcombine 规范化** ｜ 2026-06-26 ｜ PR [#205526](https://github.com/llvm/llvm-project/pull/205526) ｜ commit [`a0248a26dd3496e72290ef60846a980c9a1293d7`](https://github.com/llvm/llvm-project/commit/a0248a26dd3496e72290ef60846a980c9a1293d7)
  - 改了什么：SVE MLA 当第一个乘数是常量、第二个不是时交换两乘数操作数（`II.setArgOperand` 调换），把两种顺序在 instcombine 阶段规范化为一种。
  - 为什么重要 / 对本方向(及 Arm·性能)的意义：免去为两种操作数顺序各维护一套匹配 pattern，让已有非交换 pattern 覆盖全部情形——SVE codegen 更稳更省，属向量化路径的健壮性改进（plumbing 级，但减少 codegen 漏匹配）。

- **AArch64 其他在窗 codegen 提交（简记）** ｜ 2026-06-25~26
  - **[ISel] 用 AES 改进 clmul v4i32 下降** ｜ PR [#204542](https://github.com/llvm/llvm-project/pull/204542)（短 sha `a61830a`）：无 PMULL 时借 AES 路径做无进位乘法 v4i32。
  - **保留 SDNode flags：定长向量降为 scalable 操作时** ｜ PR [#204616](https://github.com/llvm/llvm-project/pull/204616)（短 sha `383f858`）：定长→scalable lowering 时保住 fast-math 等 flag，避免丢优化机会。
  - 仅据 commit 标题 + PR 摘要，深度有限。

## Go

### 📄 论文（近 7 天）

> 本窗口内无强相关新增 Go 论文。Go 编译器/runtime 的优化工作几乎不以 arXiv 论文形式发布（多走 design proposal + go.dev/blog），本维度对 Go 类型天然清淡。近 7 天 arXiv `cs.PL`/`cs.LG` 关键词检索未命中 Go 专属强相关工作；唯一沾边的 *Zorya: Automated Concolic Execution of Single-Threaded Go Binaries*（arXiv 2512.10799）为 2025-12 旧文且偏二进制分析、非编译/runtime 性能向，**超窗不收**。今日 Go 的真正动向在 💻 上游。

### 📰 资讯（近 1 天 → 周末放宽近 3 天）

> 本窗口内无强相关一手报道。go.dev/blog 最新一篇仍是 2026-05-21《Introducing the pkg.go.dev API》；go.dev/doc/devel/release 在 6-21~6-28 无新 patch 版本（最近 go1.26.4 / go1.25.11 均为 2026-06-02）。Go 是低频领域且周末无新发——**今天真正的新动向在 💻 上游的 SIMD/archsimd 与 malloc 快路径**。以下为帮助读者建立背景的参考（非今日新发，已标日期、与今日条目分开）：

**背景参考（窗口外·living doc）**
- **Go 1.27 release notes（草稿，预计 2026-08 发布）** ｜ <https://go.dev/doc/go1.27>
  - 一手确认本周上游 SIMD 提交的发布目标：Go 1.27 新增**可移植、向量长度无关的 `simd` 包**（全架构、`GOEXPERIMENT=simd`、提供 `Int8s`/`Float32s` 等无固定宽度向量类型）；`simd/archsimd` **修订 amd64 API 并新增 arm64 "Neon" 128-bit 与 WebAssembly 128-bit SIMD**（128-bit 覆盖 wasm/arm64/amd64，256/512-bit 限部分 amd64，尚不稳定）。
  - 该页为持续更新的 living 草稿，非"今日新发"，作背景锚点用。

**背景参考（窗口外·二手）**
- **Go archsimd 预览（2026-01-23，marselester 博客）** ｜ <https://marselester.com/go-archsimd-preview.html>
  - 仅 amd64（早于本周 arm64 Neon 支持）：用 `Int64x4`/`Int64x2` 写向量化 sum，基准较标量快约 47.6%（含边界检查）~54.7%（消除边界检查），消除分支检查另贡献约 7.1%。可佐证 archsimd 的收益量级，但 arm64 收益需 Go 1.27 后另测。

### 💻 上游代码（近 1 天 → 周末放宽近 7 天，2026-06-22 ~ 06-26）

> Releases/tags 已单独查：窗内无新 tag（最新 go1.26.4 / go1.25.11 均 2026-06-02）。以下据 `golang/go` GitHub 镜像合入视图，逐条 committer(合入)日核对；入窗按合入日。

**主题一：SIMD 实验（GOEXPERIMENT=simd）补 arm64 Neon + 修向量 codegen** — 本周 Go 后端最热的一条线，正对 Go 1.27 草稿"archsimd 加 arm64 Neon 128-bit + 新增可移植 simd 包"的发布目标。

- **arm64 SIMD IfElse / bitSelect 语义修正** ｜ <https://github.com/golang/go/commit/a2b3c73f7534ad35dfa947bc1b748f8d943c190e> (合入 2026-06-24)
  - 改了什么：arm64 的 IfElse 行为与其他平台相反，本 CL 把 arm64 的 IfElse 及底层 bitSelect 一并反转以对齐 Wasm 的 BitSelect 语义；同改 `arm64/simdssa.go`、`ssa/_gen/simdARM64.rules`、`rewriteARM64.go` 与 simdgen 的 Moves 算子 yaml，并让 Masked/IfElse 测试可移植（go-review CL 793361）。
  - 为什么重要 / 对 Arm·性能的意义：IfElse(向量 blend/选择)是 SIMD 的基础原语，语义反了会让 arm64 上的向量化结果直接算错——这类 codegen 正确性修复是 archsimd arm64 Neon 后端从"能编译"走向"可用"的硬门槛。指令级：对应 Neon 的位选择族(BSL/BIT/BIF)。

- **AMD64 mask 寄存器优化修复** ｜ <https://github.com/golang/go/commit/6565f5517ef29eb854377c7db2f967f2627a4e16> (合入 2026-06-26)
  - 改了什么：修正 AMD64 mask 优化对指令语义的误解——XORQ 是对 64 个 mask 位整体做 quadword，而非"2/4/8 个 Q 的 mask 位"；改 `AMD64.rules` + `rewriteAMD64.go`，并补宽度×元素数组合的测试（Fixes #80140，CL 794680）。
  - 为什么重要：AVX-512 风格 mask 寄存器 codegen 的正确性修复；虽是 amd64，但与 arm64 那条同属 archsimd 在各平台补齐 mask/blend 语义、为上层可移植 `simd` 包打地基。

- **SIMD 实验配套硬化（一批）** ｜ Wasm Get/SetElem 越界常量修复 <https://github.com/golang/go/commit/48bf92284cb3923db5190e2de5bc85282e68b76b> (06-25) + 测试去重/portable 化 <https://github.com/golang/go/commit/0f0fb7add0e5af727be0e6ab83284f5185ee42b6> / <https://github.com/golang/go/commit/b350da230f3d2d955159266c58d60fa68323f44c> / <https://github.com/golang/go/commit/cdf96936c0018ec224216bc79cc3ef8e6db71d88> / <https://github.com/golang/go/commit/c554c53ac8df4e3128d592489faa13149b69a324> (06-23~06-25)
  - 改了什么：让 Wasm `Get/SetElem` 在越界常量下正确工作；并把 arm64/amd64/wasm 的 archsimd 测试统一去重、改名、portable 化。
  - 为什么重要：plumbing 为主，但密度说明 SIMD 实验正进入"跨 amd64/arm64/wasm 统一测试矩阵"的收尾期，配合 Go 1.27 发布窗。

**主题二：runtime malloc 快路径重构（内存 / 性能）**

- **malloc 快路径全程持有 M + 统一 fast/slow 块** ｜ <https://github.com/golang/go/commit/63b51fc270d9d061d823ae274de15b8af8b3a54d> + <https://github.com/golang/go/commit/fe4da8e5c517753b7ec416f9f1bec144d2f76946> (均合入 2026-06-25)
  - 改了什么：fe4da8e 把 `mallocStub` 的 fast(`!isSlowPath`) 与 slow 逻辑各自合并为单块（纯重构、便于阅读与后续改动）；63b51fc 在 `forceSlowPath` 检查**之前**就 `acquirem` 并持有到 `inlinedStub`，保证一旦决定走快路径 GC 就无法启动（For #79667 / #79699，CL 794120/794121）。
  - 为什么重要 / 性能意义：size-specialized malloc 的快路径假设 GC 标记不在进行；而 `forceSlowPath` 检查此前在任何加锁之外——当**内联被关闭**时存在可抢占调用，可能让 GC 周期插入而破坏该假设。这是对分配热路径的"锁定 M"正确性加固，也是后续把 `acquirem` 提前、精简快路径的铺垫，直接落在内存分配热路径与性能关注点上。

**主题三：PGO × 新内联器**

- **PGO profile 透传到内联器与函数体 reader** ｜ <https://github.com/golang/go/commit/e296659b1222b1813bff7f310478ee3ac042902e> (合入 2026-06-22)
  - 改了什么：内联导入泛型函数的实例化时会触发对新实例化函数的 `CanInlineFuncs`，此前该路径即使开了 PGO 也用 nil profile 调用，导致 newinliner 下 `revisitInlinability` 误判不可内联、与 PGO 实际要内联冲突而**编译器崩溃**；本 CL 把 profile 一路透传（Fixes #80064，CL 793042）。
  - 为什么重要：PGO + 泛型 + 新内联器三者交互的崩溃修复，是 PGO/newinliner 走向稳定的必要 plumbing。

**主题四：codegen 正确性 + runtime 杂项（简）**

- **codegen 修复** ｜ OINDEXMAP 无效代码生成 <https://github.com/golang/go/commit/2a4fbc3f244e575342c48907fbd17faf3333631c> (06-23) · 死代码中堆变量不再强制要求 Heapaddr <https://github.com/golang/go/commit/9c9e880fe150c27e742bfabe9c145feef7e5928f> (06-23) — 仅据 commit message，深度受限。
- **runtime** ｜ deconflict gscan 与 mutex profiler <https://github.com/golang/go/commit/29c1c946aa2fc8303f534ba85f534ae05cef6c2f>（作者写于 06-08、**合入 06-24**，按合入日入窗）：修内部 mutex 竞争测量在 Gscan 置位时不安全的 unlock2/profInsert 交互（For #58277）；另修 sbrk 平台 `sysFreeOS` 空指针 <https://github.com/golang/go/commit/649897800b5114739fe83e0e053d363167441ffc> (06-24)。

## Java

### 📄 论文（近 7 天）

> 本窗口内无强相关新增。

- 已扫 arXiv `cs.PL/recent`（近百篇，论文窗近 7 天），无 JVM / HotSpot / JIT / 字节码 / 值类型方向条目；最接近的两篇（张量程序超优化、面向超维计算的编译器近似调优）属张量 / AI 编译，应归「AI 编译」类型，非 Java-runtime。
- 说明：JVM/JIT 专向论文结构性低频（多散落 PLDI / OOPSLA / CGO / VMIL·MoreVMs workshop，按会期发布），日扫常空；本维度为「**有源覆盖、无关注点命中**」而非「无源覆盖」。深度论文综述交 `paper-digest`。

### 📰 资讯（近 1 天 → 周末放宽近 3 天；命中关注点条放宽近 7 天）

> 周末资讯极薄：OpenJDK 官方近 3 天仅 1 期播客；唯一命中本类型关注点的是 06-21 的 Valhalla 文章（按"命中关注点放宽近 7 天"收录）。本周真正的技术新动向在 💻 上游（Vector API C2 修复、aarch64 加密 intrinsic、Leyden AOTCache 分层编译修复）。

#### 2026-06-25 ｜ inside.java 播客 60 期：JEP 如何驱动 Java 演进
- **URL**：https://inside.java/2026/06/25/podcast-060/
- **背景**：周末严格近 3 天窗内 OpenJDK 官方唯一新发条目，"Ask the Architects" 系列。
- **要点**：
  - 讲 JEP（JDK Enhancement Proposal）流程如何作为 Java 演进的组织机制；偏路线 / 流程，非具体 codegen / perf 技术点。
  - 与本周 JDK 27 进入 Rampdown Phase 1（RDP1、GA 排期 2027-03）的里程碑背景呼应。
- **启发**：想跟 C2 / Leyden / Valhalla 落地节奏的读者，本期资讯只是流程层，技术增量看 💻 上游小节。

#### 2026-06-21 ｜「Better Tools for Immutable Data」：Valhalla 值类型与不可变数据的 JVM 优化（窗口外·命中关注点，近 7 天）
- **URL**：https://inside.java/2026/06/21/better-tools-immutable-data/
- **背景**：Java 语言架构师 Dan Smith（Valhalla 规范牵头）的 JavaOne 2026 演讲整理；命中本类型 Valhalla 关注点，按"命中关注点放宽近 7 天"收录，实际日期 06-21。
- **要点**：
  - 串讲一组不可变数据特性：records + record patterns + derived record creation（"withers"）、**value classes / value objects（Valhalla）**、flexible constructor bodies（早期字段初始化）、lazy constants API、static final 初始化诊断、以及替代不安全反射改写的 marshalling API。
  - 明确讨论"这些特性使能哪些 JVM 优化"——值类无对象身份 → 可做平坦化(flattening) / 标量替换，是 Vector API 从 incubator 转 preview 的前置依赖。
  - 末尾抛出方向问题："未来要不要 immutable arrays？"
- **启发**：做 SIMD / Vector API 的读者应盯 Valhalla 值类落地节奏——Vector 类型改成 value class 后才能去掉装箱、打通 Float16 / 向量寄存器平坦化；当前 Vector API 仍卡在第 12 次 incubator（JEP 537，inside.java 标记 05-25 targeted JDK 27）等 Valhalla。

> 背景参考（非今日新发，不计入今日条目）：inside.java「Performance Improvements in JDK 26」（06-09）；InfoQ Java News Roundup 最新一期为 06-15（已超 7 天窗，本窗口无新期）；06-22 一期未检索到 / 可能未发。

### 💻 上游代码（近 1 天 → 周末放宽近 7 天）

> 数据源：openjdk/jdk GitHub API（`since=2026-06-21`，64 条提交），逐条以 API committer date 核窗。hotspot-compiler-dev 邮件列表 pipermail 反爬(403)、mail-archive 镜像缺失(404) 未抓通——集成补丁已由 openjdk/jdk commit 覆盖，纯 review-stage 讨论可能漏（见 flags）。

**A. Vector API（Panama）C2 codegen 正确性连修 4 处** —— 命中 Vector API + C2 JIT 关注点，本周上游最密集的一条线
- **C2 Vector API：`collect_unique_inputs(n)==1` 断言失败(not unary)** ｜ https://github.com/openjdk/jdk/commit/548a95379f159a0dc369f6bb80d8167ec835c7cd （JDK-8386163，06-27，评审 vlivanov / epeter）
  - 改了什么：修一处 C2 在向量节点输入收集时把非一元节点误当一元导致的断言崩溃。
  - 为什么重要：Vector API 走 C2 自动向量化 / 显式 SIMD 的 codegen 路径，断言崩溃即编译失败 / 回退解释执行；这类 correctness 修复是 Vector API 稳定可用的底盘。
- **Float16Vector NaN 规范化用于 hashCode 计算** ｜ https://github.com/openjdk/jdk/commit/8740fbb4eeaf742e88999d4f243e29d53d17be2b （JDK-8386255，06-26，评审 psandoz / sherman）
  - 改了什么：Float16（半精度）向量在算 hashCode 时对 NaN 做规范化，保证不同 NaN 位模式哈希一致。
  - 为什么重要：Float16 是 AI / 低精度数值的关键类型，Vector API 半精度支持正在补齐语义边角；psandoz(Paul Sandoz) 是 Vector API/Panama 负责人。
- **C2 `PhaseVector::expand_vunbox_node` 不再把 payload 类型注入 load** ｜ https://github.com/openjdk/jdk/commit/35ff862a547deb137bbb0a073ded0d3729d4dad3 （JDK-8387012，06-24）
  - 改了什么：向量 unbox 展开时修正 load 节点的类型注入，避免类型信息错误传播。
- **C2 Vector API：`VectorNode::push_through_replicate` 缺失截断** ｜ https://github.com/openjdk/jdk/commit/ee9616d4a43006f932774f9a5d421dc46a91d5d6 （JDK-8386155，06-23）
  - 改了什么：向量 replicate 下推时补上子字(subword)截断，修正窄类型语义。

**B. AArch64 加密 intrinsic 加速** —— 命中 Arm·鲲鹏关注点；评审人 aph(Andrew Haley) / adinn(Andrew Dinn) 为 aarch64 端口维护者（指令级条目）
- **加速 aarch64 上的 P-256 椭圆曲线算术** ｜ https://github.com/openjdk/jdk/commit/f1cd7f6ab9c162736ea3fc8f1523294ec004776e （JDK-8355216，06-24，评审 adinn / aph）
  - 改了什么：为 NIST P-256 的模运算新增手写 aarch64 intrinsic，替代通用 Java 大数 limb 运算。
  - 指令机制 / 收益来源：椭圆曲线模乘的瓶颈在 64×64→128 位乘法与进位链，aarch64 用 `MUL` + `UMULH`（取高 64 位）配合 `ADCS`/`ADC` 进位链可显著压缩指令数；直接利好 TLS 握手 / ECDSA·ECDH 在鲲鹏上的吞吐。
  - 注：提交信息未带基准数字，收益描述据 JBS 标题 + 评审，未见实测百分比（不臆造）。
- **X25519 使用 aarch64 intrinsic** ｜ https://github.com/openjdk/jdk/commit/3f03e104edbcfdc8465415e20882950d2b7d3dee （JDK-8385304，06-25，评审 adinn / shade）
  - 改了什么：Curve25519（X25519 ECDH 密钥交换）的标量乘走 aarch64 intrinsic 路径，与上面 P-256 同属一波 aarch64 椭圆曲线加速。
  - 为什么重要：X25519 是 TLS 1.3 默认密钥交换之一，aarch64 加速直接落到握手延迟；与本周 JDK 27 的后量子 / 混合密钥交换收尾同期，密码学热路径在持续 Arm 化。
- （次要）**修 aarch64 ML-KEM / ML-DSA intrinsic 代码的文档注释笔误** ｜ https://github.com/openjdk/jdk/commit/e356cbb3958dcd3329765716d8b5376c6a213e89 （JDK-8384847，06-23）—— 旁证 aarch64 已有后量子(ML-KEM/ML-DSA) intrinsic，本周仅文档修补。

**C. Project Leyden / AOT：分层编译策略退化修复** —— 命中性能 + AOT/Leyden 关注点（高价值）
- **AOTCache 在场时峰值吞吐偏低** ｜ https://github.com/openjdk/jdk/commit/ce93858acd423e1fa1011358cff9fc495182aca6 （JDK-8386852，06-23，评审 kvn / iveresov / shade）
  - 改了什么 / 根因：据社区讨论(IBM Ashutosh Mehra 定位)，当 AOT 训练数据存在时，tier-2 方法晋升的"安全网"被禁用——"足够老"的方法本应不论队列长度都被提拔出 tier-2，但该安全网在有 AOT 训练数据时关闭，导致方法卡在 tier-2、不再升 tier-3/tier-4，C2 编译变少，峰值吞吐下降。补丁去掉该 guard，恢复晋升。
  - 为什么重要 / 对方向的意义：这是 Project Leyden AOTCache 与 HotSpot 分层编译策略交互的真实回归——AOT 加速冷启动的同时不能牺牲稳态峰值；评审人 kvn(Vladimir Kozlov) / iveresov(Igor Veresov) 是 C2 / 分层编译核心。补丁称去掉 guard 后两个框架的峰值性能、达峰时间均改善（提交未附绝对数字，不臆造）。

**D. C2 JIT 健壮性 / 正确性修复（一簇崩溃 & 溢出）**
- C2 编译代码因缺失 ctrl 触发 SIGSEGV ｜ https://github.com/openjdk/jdk/commit/b6e7b2b29213134a1a35fe34501b2fb94c04d70a （JDK-8385420，06-26）
- C2 `ArrayCopyNode::finish_transform()` 处理 clone 时 "named projection 2 not found" 崩溃 ｜ https://github.com/openjdk/jdk/commit/07a52da1fed10623f66bf424a1c5b10bd07ad25e （JDK-8387015，06-25）
- C2 `BCEscapeAnalyzer::iterate_blocks` 可能整数溢出 ｜ https://github.com/openjdk/jdk/commit/bd8072d22ced9a75da0d6578df66be65f886c746 （JDK-8379816，06-25）—— 逃逸分析（标量替换前置）健壮性。
- C2 CountedLoop 对 subword 截断 iv 的检测加 fuzzer 测试 ｜ https://github.com/openjdk/jdk/commit/ad075c96bfb35e02eed3ff55d2805dd55a9995d0 （JDK-8386597，06-23）

**E. JIT profiling 工具 / 自动向量化 / AArch64 杂项**
- Linux `perf` map 应记录各个 vtable trampoline ｜ https://github.com/openjdk/jdk/commit/b5fba9428e24b34dc26c3642c9f28593ab7bdd39 （JDK-8387148，06-25）—— 让 `perf annotate` 能把 JIT 生成的 trampoline 归因到具体符号，利好 JIT 代码的 perf 热点分析。
- Jtreg `compiler/vectorization/TestVectorAlgorithms` 在 JDK-8373026 后失败修复 ｜ https://github.com/openjdk/jdk/commit/b16d8fa414e44367a208fbb28015a3adc50cc5a8 （JDK-8376803，06-22）—— 自动向量化回归守护。
- 启用 PAC 的 AArch64 Linux 未打印告警信息修复 ｜ https://github.com/openjdk/jdk/commit/a0c0ab80d3b0206494b3495b4e1b483a7b61636d （JDK-8386944，06-22）—— Pointer Authentication(PAC) 在 aarch64 的诊断完善。

**F. Shenandoah GC 性能（perf 关注点）**
- 给热点原子计数器填充以避免分配路径上的伪共享(false sharing) ｜ https://github.com/openjdk/jdk/commit/b06aa89c60cfad9621af227f42c993c6d96beecf （JDK-8386992，06-23，评审 shade / ruili）—— cache line 伪共享是多核(尤其鲲鹏高核数)分配路径常见瓶颈，pad 到独立 cache line 缓解争用。
- 重构标记循环内联 ｜ https://github.com/openjdk/jdk/commit/da7bde5f14b75259d20c80021f83e6f95cf2049d （JDK-8385643，06-25）

**里程碑（关注点 F）**：JDK 27 已进入 Rampdown Phase 1，上游可见收尾提交——RDP1 L10n 资源更新 https://github.com/openjdk/jdk/commit/12d7e6186622506cb19aad0e3d9e9256531e2851 （JDK-8385927，06-22）、为 JDK 27 build 27 更新 `--release 26` 符号信息 https://github.com/openjdk/jdk/commit/d1905ef91a194f57e81bc2d3a6ad0dec98ca8096 （JDK-8386081，06-25）。JDK 27 GA 排期 2027-03。

## AI编译

### 📄 论文（近 7 天）

> 窗口 2026-06-21~06-28。arXiv 周末不发新刊，入选 2 篇均来自 06-24 cs.PL，新 ID 已直取 `abs/` 核对真实存在（标题/作者/日期一致）。

- **Axon: A Synthesizing Superoptimizer for Tensor Programs** ｜ arXiv:2606.26344（2026-06-24，cs.PL）｜ [链接](https://arxiv.org/abs/2606.26344)
  - 面向 tile 化 AI 加速器，用**程序综合**从语义规格自动生成目标指令，并以 SMT 校验"语义等价的程序变体"，再经验性地搜 tiling / 指令选择 / 算子融合配置选最快 kernel——把过去靠专家手工的 tiling+融合+选指令做成超优化（superoptimization）搜索。作者：Akash Kothari, Shaowei Zhu, Daniel Kroening, Chungha Sung。
  - 相关性：正中本类型「张量 codegen + autotuning + 算子融合」与共享「性能优化」；超优化思路对鲲鹏/CPU 张量后端选指令也有借鉴价值（抓到摘要，但原文未给具体加速数字，不编造）。

- **Reading AI Model Compilation in MLIR Through the Lens of Formal Theories** ｜ arXiv:2606.25244（2026-06-24，cs.PL）｜ [链接](https://arxiv.org/abs/2606.25244)
  - 把 MLIR 的工程实践（IR 抽象、match-and-rewrite、staged lowering）逐一对应到形式理论（项重写系统、refinement calculus、抽象解释），论证好抽象的理论根基、以及实现在哪偏离理想设计。作者：Javed Absar。
  - 相关性：命中本类型「新 IR / pass / lowering」与 MLIR 设计方法论；做 MLIR pass / dialect 的人可借它判断抽象是否完备（综述/观点型，无量化收益，低信息密度但方向强相关）。

> 备注：cs.DC 06-24 的 **EmuGEMM**（arXiv:2606.25453，Ozaki Scheme 融合 Tensor Core kernel，称在 Blackwell 上较 cuBLAS TF32 快至 1.7×）已核为**手写 kernel 实现、非 codegen/编译器工作**，按"张量编译"口径不入选，仅备注。

### 📰 资讯（近 3 天）

> 近 1 天（06-27~06-28）无 AI 编译一手新文；放宽近 3 天命中 PyTorch 官博 1 篇（正中 AI codegen + 友商 AMD + 量化）。

#### 2026-06-25 ｜ PyTorch 官博推 TokenSpeed-Kernel：多硬件可移植 LLM 推理算子层，AMD Gluon kernel 端到端提速 1.6–3.6×
- **URL**：https://pytorch.org/blog/lightseek-tokenspeed-kernel/
- **背景**：LLM 推理后端按硬件碎片化（每家加速器各写一套 attention/MoE/GEMM kernel），LightSeek 基金会把"算子选择"从运行时解耦成一个可移植的 kernel 注册/选择子系统，由 AMD Triton 团队联署在 PyTorch 官博发布。
- **要点**：
  - 元数据驱动的 kernel 注册/选择：`@register_kernel` 声明算子族、solution、平台能力、tensor 格式签名、特性 traits 与优先级；selector 按平台能力 + 格式签名筛选并缓存——运行时只描述"算子问题"而不点名"AMD kernel / Triton kernel"。
  - 覆盖推理主力算子：attention（`mha_prefill` / `mha_decode_with_kvcache`，含 sliding-window、attention sink）、MoE（`moe_apply` 路由+expert GEMM+激活+combine）、GEMM、多卡通信、量化与采样。
  - 多后端实测（GPT-OSS 120B）：AMD MI355X/CDNA4 用 **Gluon kernel** 较 Triton baseline，attention 提 **1.4–2.3×**、MoE decode 提 **1.7–2.1×**，端到端吞吐 **1.6–3.6×**；NVIDIA Blackwell 走 TensorRT-LLM（FlashInfer 包装），MXFP4 MoE 走 flashinfer_trtllm；Triton 作为全平台可移植 baseline。
  - AMD 专用包 `tokenspeed-kernel-amd` 单独发 PyPI，供 vLLM 等推理引擎直接复用。
- **启发**：做 AArch64/鲲鹏张量推理后端的同学可借鉴这套"算子族 + 平台 traits + 格式签名"的注册/选择层，把鲲鹏 kernel 作为一个 backend 注册进同一抽象；MXFP4 量化 MoE 已成 AMD/NVIDIA 双线发力点，值得跟踪其 kernel 形态。

> **窗口外·同主题上下文（非今日新发）**：PyTorch 官博 06-18《From Minutes to Seconds: LLM-Guided Autotuning for Helion Kernels》（Jason Ansel 等，LLM 引导 Helion kernel autotuning，命中关注点但已 10 天）、05-27《Why Is PyTorch Compile So Fast: Kernel Fusion》（Inductor 融合原理）——本周末资讯薄，真正的新动向集中在 💻 上游。

### 💻 上游代码（近 7 天）

> 近 1 天 commit 有量但偏 plumbing；周末 fallback 到近 7 天（06-21~06-28）按主题聚类取高价值。入选条目日期均直取 commit 页核对，链接用全 40 位 sha。

- **TVM：TIRx 打通可伸缩向量 Ramp lowering（SVE/RVV 方向）** ｜ [#19866](https://github.com/apache/tvm/commit/81e62ecbb27724794940ce13e551e43313cae0c7)（2026-06-26）
  - 改了什么：CodeGenLLVM 原来对 `Ramp(base,stride,lanes)` 只能逐 lane 插入构造**定宽**向量，对运行时 lane 数未知的**可伸缩向量**直接拒绝；本补丁新增一条 scalable 整型 Ramp 的 lowering 路径，用 `splat(base) + stepvector()*splat(stride)`（LLVM≥20 走 `llvm.stepvector`）生成。
  - 为什么重要 / 对本方向（及 Arm·性能）的意义：这是**指令级**改动——直接打通向量化 TIR/TIRx 把归纳表达式 lower 到 **RVV/SVE 式可伸缩向量**，是 TVM 张量后端拥抱 AArch64 SVE / RISC-V RVV 的关键一步，正中「Arm·AArch64」与「张量 codegen」关注点。

- **IREE：C-bitcode ukernel 框架跑通 LLVMCPU 端到端 codegen** ｜ [#24571](https://github.com/iree-org/iree/commit/6b78497e50092a09c97c3af683bed0c41fba5293)（2026-06-24）
  - 改了什么：为新的 C-bitcode ukernel 框架补了一条 `iree-opt` 端到端 lit 测试，驱动完整 LLVMCPU codegen 流水线处理 `inner_tiled` 派遣，断言 bitcode 以 `objects(...)` 一等属性抵达 `hal.executable.variant`、`llvm.func @iree_uk_mma_…` 带 `hal.import.bitcode=true` 全链路打通。
  - 为什么重要 / 对本方向（及 Arm·性能）的意义：ukernel（微内核）是 IREE 在 **CPU 后端**塞入手调高性能 kernel（如 MMA）的机制，端到端 codegen 跑通意味着该框架可用——对 AArch64/CPU 张量 codegen 落地直接相关。

- **MLIR：SCF 单次迭代循环提升 + XeGPU 连续性分析（Intel GPU）** ｜ [SCF #205826](https://github.com/llvm/llvm-project/commit/9623f43b8bc667dd2b76067a4fb4f4353f985f95)（2026-06-26）、[XeGPU #201684](https://github.com/llvm/llvm-project/commit/dd5357d38d6b73e3a687bcc5ea8cb3a858fb3fea)（2026-06-26）
  - 改了什么：SCF 把"上界=步长的单次迭代循环"直接 promote 掉（消循环开销）；XeGPU 新增 contiguity 分析、VectorToXeGPU 修正 0D memref 处理、`isa<>` 支持 uarch 检查。
  - 为什么重要 / 对本方向（及友商·性能）的意义：SCF 提升是张量循环嵌套常见的标量化/降开销优化；XeGPU 是 **Intel GPU**（友商 Intel）在 MLIR 的张量 dialect，连续性分析为其向量化访存铺路——命中「友商动向 Intel」与「IR/pass」。

- **XLA：buffer assignment 重写为 O(N log M) sweep-line（FAST_MERGE）** ｜ [commit 172ec6f](https://github.com/openxla/xla/commit/172ec6fd5abaecf7bebb3ffda5553a8fb95527df)（2026-06-26）
  - 改了什么：为 `AssignBuffersForComputations` 引入新的 sweep-line buffer 分配算法 `FAST_MERGE`：按 live-range start 递增处理 buffer，用 min-heap 跟踪活跃分配、从空闲池复用过期分配；复杂度从默认 O(N·M)（最坏 O(N²)）降到 **O(N log M)**。
  - 为什么重要 / 对本方向（及性能）的意义：编译期可扩展性 + 内存复用直接优化——大模型图的 buffer 分配是 XLA 编译耗时/显存占用热点，正中共享「性能优化（footprint/编译吞吐）」关注点。

- **Triton：Python 绑定切 nanobind + MXFP4 matmul autotune + 新增 tl.atomic_poll** ｜ [#10283 nanobind](https://github.com/triton-lang/triton/commit/ec2b08420d586062d55dbbd7745b737185781a74)（06-24）、[#10682 BN512 MXFP4 调优](https://github.com/triton-lang/triton/commit/f09600a11a3bd029e3326f9f41131c2249e134cb)（06-23）、[#10723 atomic_poll](https://github.com/triton-lang/triton/commit/8bf4c663603ad5eb54f371580ecdb6c94a404395)（06-26）
  - 改了什么：Python 绑定从 pybind 迁到 **nanobind**（更轻、构建/调用开销更低）；为 **BN512 shuffled MXFP4 matmul** 调 autotune 配置；语言层新增 `tl.atomic_poll` 原子操作；另有 autotuner 修复（top_k 取整为 0 时至少保 1 个 config，#10689）。
  - 为什么重要 / 对本方向（及性能）的意义：nanobind 降低前端开销利好编译/启动延迟；MXFP4 调优与 TokenSpeed 资讯里的 MXFP4 MoE 同频——**MXFP4 量化 matmul** 正成张量编译栈热点；命中「量化 codegen + autotuning」。

- **TVM/Relax：IR 类型系统大重构（StructInfo↔Type 统一、PrimType 收敛、ARITH 热路径提速）** ｜ [#19853 统一 StructInfo 与 Type](https://github.com/apache/tvm/commit/1bb5cf6102da318f4dece97c5665047d0ee7717a)（06-21）、[#19885 ARITH 用 IntImm 走标量热路径](https://github.com/apache/tvm/commit/6ea9599c2ba86249a0dcd4ccb5e2b208fe06c61b)（06-25）
  - 改了什么：本周末 TVM 一连串 REFACTOR——统一 Relax `StructInfo` 与 `Type`、把 `PrimExpr` 类型机制收敛到 `PrimType`、phase out `Downcast`/Relax `PrimType` 包装；ARITH 在 canonical 标量热路径改用 `IntImm` 减开销。
  - 为什么重要 / 对本方向的意义：这是 TVM "TIRx + Relax 现代化"路线（对应 discuss 上 tqchen 的《Evolving and Modernize Tensor-level IR》RFC）的落地批次，IR 类型基座统一是后续 codegen/调度演进的地基；ARITH 热路径提速是编译期性能改善。属架构方向信号，多为 plumbing（仅据 commit 标题+正文，未逐文件读 diff）。

## 内存库

### 📄 论文（近 7 天）
> arXiv 严格 7 天窗(2026-06-21~06-28)内 cs.OS / cs.DC / cs.CR 均无强相关分配器新论文(cs.OS 11 篇仅 2 篇沾内存:CXL 池化 2606.24079、带宽调控 2606.23945,皆非分配器)。本维度由 **ISMM 2026** 支撑——会议 2026-06-16 随 PLDI'26 于 Boulder 召开,落在近 30 天会议窗内;ISMM 是本领域全年第一优先会,今年共 9 篇,以下 4 篇直击分配器/大页/内存分层/安全加固关注点。

- **Reconsidering "Reconsidering Custom Memory Allocation"** ｜ ISMM 2026 / arXiv:2605.17119 ｜ [arXiv](https://arxiv.org/abs/2605.17119) · [DOI](https://doi.org/10.1145/3814942.3816132)
  - van Kempen 与 Emery Berger 用现代硬件 + 现代通用分配器(jemalloc/mimalloc/tcmalloc)重做 Berger 本人约 25 年前的经典实验,扩到 Clang/Blender 等真实大程序,并刻画碎片如何影响 locality;结论:region/custom 区域分配在今天仍保有性能优势(作者称)。
  - 相关性:正中关注点①性能优化 + ⑤碎片/内存效率——"通用分配器 vs 自定义/区域分配"是 jemalloc/tcmalloc 用户长期争点,且本文直接 benchmark 了三大主流分配器,结论对生产选型有指导意义。

- **Enabling Huge Pages for Real-World Executables** ｜ ISMM 2026 ｜ [DOI](https://doi.org/10.1145/3814942.3816136)
  - Nadav Amit(Technion):huge page 能大幅降地址翻译开销,但用于**可执行代码页**长期受 binary 格式 / page cache / loader 机制限制(现有做法把代码拷进匿名内存);本文消除这些结构性障碍,让真实可执行文件直接用大页。
  - 相关性:关注点④大页/THP——与 jemalloc HPA、AArch64 上 THP 利用率同一主线,把大页从数据页推进到代码页。

- **Bandwidth Speaks, We Listen: Dynamic Memory Interleaving for Tiering** ｜ ISMM 2026 ｜ [DOI](https://doi.org/10.1145/3814942.3816137)
  - UW-Madison + Micron:DMI 在线监测机器带宽利用率,动态决定何时/如何在本地与远端(CXL)内存间交织数据以最大化带宽;作者称带宽密集型应用比 SOTA 带宽感知分层系统快达 26%,延迟敏感型不退化。
  - 相关性:关注点⑥NUMA/多核扩展性 + 内存分层——CXL/分层与跨节点局部性,是大规模 jemalloc/tcmalloc 部署的下一道战场。

- **Interpreter Memory Safety via Differential Fuzzing with a CHERI on Top** ｜ ISMM 2026 ｜ [DOI](https://doi.org/10.1145/3814942.3816133)
  - Glasgow/Leeds:借 CHERI(指针能力)硬件做差分模糊测试,捕获解释器中的内存安全 bug。
  - 相关性:关注点⑦安全加固(CHERI/指针标记)——与 MTE、hardened_malloc、Scudo 同属堆安全对照线;偏解释器模糊测试、与分配器本体关系较弱,低权重列出。

> 同场 ISMM 2026 另 5 篇偏 GC/GPU/架构,与分配器本体关系较弱,仅作会议窗上下文不展开:《Going Where No GC Has Gone Before》、《Much Ado About Offset Vectors》(Blackburn, Google;GC 堆表示)、《Stride-Aware Page Prefetching for GPU Unified Memory》、《Consistency and Coherence of the NVIDIA Grace-Hopper Superchip》、《Stretch: A Fault-Driven DSM Runtime》。

### 📰 资讯（近 1 天 → 周末放宽）
> 子窗：资讯近 1 天（2026-06-27→28，周日清淡日）；命中关注点的内核 mm/slab 里程碑回看近 1 周，更早的同主题/版本里程碑单列为「背景参考」，不充作今日新发。

今日窗内**无用户态分配器（jemalloc / tcmalloc / mimalloc / glibc malloc）的新版本或一手博客**；真正的新动向在**内核内存管理侧**——一条 THP/HugeTLB 统一的 RFC，与正在关窗的 Linux 7.2 slab 分配器优化。

### 2026-06-27 ｜ 字节跳动提出 "Reserved THP"：把 HugeTLB 的"预留+保证分配"塞进可换出的 THP
- **URL**：https://www.phoronix.com/news/Reserved-THP-Linux （Phoronix 反爬，WebFetch 返回 403 未读正文；要点据 `site:phoronix.com` 搜索摘要 + linux-mm RFC 转述整理）
- **背景**：内核现有两套大页机制各有短板——HugeTLB 能预留、保证在预留池内分配，但不支持 swap；THP 与核心 mm 深度集成、可换出，却不能预留、分配不保证。字节跳动工程师 Qi Zheng 发 RFC patch series 想合二为一。
- **要点**：
  - Reserved THP = 可通过 `madvise()` 预留并消费的 THP，普通内存分配不能占用这部分；因其本质仍是 THP，可相对容易地支持 swap。
  - 落地诉求来自字节内部：热升级（hot-upgrade）场景要预留内存，同时又要能把暂时不用的部分换出去——这正是 HugeTLB 做不到的。
  - 目前为 RFC（linux-mm），尚无明确目标内核版本；未拿到逐封邮件 / 具体补丁数（低置信：仅据 Phoronix 摘要，未读邮件列表原帖）。
- **启发**：jemalloc 的 HPA、以及任何把吞吐 / CPU 效率押在 THP 命中率上的分配器，都受制于"内核能不能稳定给到 2MB 大页"。若 Reserved THP 让 THP 也能"预留+保证分配"，用户态分配器的 HPA 命中率与 CPU 效率有望直接受益——值得跟踪它能否进主线，以及对 `MADV_HUGEPAGE` 语义的影响。

### 2026-06-17 ｜ Linux 7.2 slab 分配器拿到一批快路径优化（7.2 合并窗本周末 06-28 关窗）
- **URL**：https://www.phoronix.com/news/Linux-7.2-Slab ；同合并窗的 mm 合入 https://www.phoronix.com/news/Linux-7.2-MM （均 Cloudflare 反爬，据 `site:` 搜索摘要整理，未读正文）
- **背景**：Linux 7.2 合并窗本周末（今天 06-28）关窗，内核 mm/slab 的 PR 在这两周陆续落入 Vlastimil Babka 的 slab 树与 Andrew Morton 的 mm 树。slab PR 于 06-17 报道（窗口外·同主题里程碑，因合并窗当下正关窗、属命中关注点 #8 故收录并标实际日期）。
- **要点**：
  - **延后 freelist 构建**：把 freelist 构建推迟到从新 slab 批量分配之后——ZTE 的 Shengming Hu 报 `slub_bulk_bench` 单对象耗时降约 42%–70%（`CONFIG_SLAB_FREELIST_RANDOM=n`）、约 58%–69%（`=y`）。
  - **批量 detach/reattach partial slab**：`will-it-scale` 的 mmap 基准 +2%–5%。
  - **allocation tokens**：借 LLVM Clang 22++ 的编译器特性，按"分配对象类型"更聪明地给 kmalloc cache 分桶（局部性 + 抗 cross-cache 攻击）。
  - 同合并窗的 mm PR（06-24 报道）头条是 MGLRU 页回收（MongoDB +30%~100%）与 folio swap 统一——属**页回收**而非堆分配器，本领域只取其 slab 部分（该 06-24 日期为低置信：另一来源给 03-18，疑与早前 MGLRU 补丁文混淆）。
- **启发**：内核侧 SLUB 仍在快路径上挤性能，且开始用"对象类型感知"做缓存分桶——做内核内存子系统 / 容器密度优化的，关注 7.2 发布后 `slub_bulk_bench`/`will-it-scale` 的实测，以及 allocation tokens 对 kmalloc 分桶策略（与安全加固）的影响。

#### 背景参考（非今日新发，标注原始日期，仅作上下文，不计入今日入选）
- **glibc 在 AArch64 默认开启 2MB THP（malloc）**｜2025-12-10｜https://www.phoronix.com/news/Glibc-malloc-2MB-THP-AArch64 — Arm 工程师 Dev Jain 提交，SPEC +6.25%；当前 Arm 开箱内存性能的关键背景（关注点 #2/#4）。
- **LWN：Automatic mTHP creation in 7.2**｜2026-06-11（载于 06-18 周刊）｜https://lwn.net/Articles/1077459/ — 7.2 自动创建多尺寸 THP（mTHP），与上面 Reserved THP 同属"让 THP 更可用"的主线（关注点 #4；LWN 免费版有约 1 周时效墙）。
- **jemalloc 生态**：Meta 续投声明（2026-03-02，engineering.fb.com）、jemalloc 5.3.1（2026-04-14，近 4 年首发）、mimalloc v3.3.2/v2.3.2（2026-04-29）、"Who even uses jemalloc in 2026"（theconsensus.dev，2026-04-16）——均窗外，无新进展。

> 今日资讯偏内核 mm；用户态分配器的新动向（若有）更可能落在 💻 上游 维度的 dev 分支 commit。

### 💻 上游代码（近 1 天 → 放宽近 7 天）
> 周末清淡日:提交窗放宽到**近 7 天(2026-06-21 ~ 06-28)**、邮件列表**近 7 天**。入窗以**合入/提交(committer)日**为准;每条入选均直取 commit 对象 / 单封邮件核对真实日期(不信列表页/归档索引聚合日期)。**Releases 已单独查过一步**:jemalloc 5.3.1(2026-04-13)、mimalloc v3.3.2(2026-04-29)、hardened_malloc 14(2026-02-22)、tcmalloc(无 GitHub release)——窗内均无新版本。

- **jemalloc:把 SEC 缓存前置到 PAC ecache 砍锁竞争,附一则"struct 字段顺序挤出热 cacheline、默认关特性也退 2%"的布局回归修复(今日 06-28 落 dev)** ｜ 主体 [9c1a484](https://github.com/jemalloc/jemalloc/commit/9c1a484e1de990678986b5e4a6c7768dba25e0b2)(merged 06-24)+ 布局修复 [db15a39](https://github.com/jemalloc/jemalloc/commit/db15a39d75d59fd20bb2ed10905297f312054d32)(merged 06-28)+ HPA purge 选项清理 [43a8adc](https://github.com/jemalloc/jemalloc/commit/43a8adc1874d1e910d1fff3d476e9088df0c973f)(06-28)+ SEC stats 无锁 [2043c6a](https://github.com/jemalloc/jemalloc/commit/2043c6ab58639a51c559580f513022f2d8e2d483)(06-24)
  - 改了什么:
    - `9c1a484`:在 PAC 的 ecache 前加一层 **per-shard Small Extent Cache(SEC)**。命中 SEC 的 alloc/dalloc 不再抢 ecache mutex,溢出才回落到后端 ecache(含 `ecache_pinned`)。由 `experimental_pac_sec_nshards` 门控,**默认 0(关闭)**;为支持 HPA 与 PAC 各自独立的 SEC 实例,`sec_alloc/sec_dalloc/sec_fill` 改为显式传 shard 参数,HPA/PAC 用各自 TSD shard 槽。
    - `2043c6a`:per-bin SEC 统计(`bytes_cur/nmisses/nhits/...`)改成 `sec_bin_t` 内的 `atomic_zu_t`;写仍持 `bin->mtx`,但 `sec_stats_merge` 改用 `ATOMIC_RELAXED` 无锁读,消除与 `arena->stats.mtx` 间的 lock-rank 反转。
    - `db15a39`(今日落):`9c1a484` 把 `sec_t` 内嵌进 `pac_t`(+~48B),因 `pac_t` 排在 `pa_shard_s` 里 hot 的 `hpa/edata_cache` 字段之前,结构变大把热字段整体后移——**即使 SEC 默认关闭、没有任何 SEC 代码执行**,也让 free/extent 路径在 fill-flush 微基准(500 线程/256B)上回退约 **2%**,纯 struct-layout 效应。修法:把 `pac` 挪到 `pa_shard_s` **最后一个字段**,让其增长只推移尾部 `all_bins[]` 柔性数组。纯重排,无功能改动。
    - `43a8adc`(今日落):删掉无用的 `experimental_hpa_max_purge_nhp` 选项,改由 `hpa_dirty_mult / hpa_purge_threshold / hpa_min_purge_interval_ms / hpa_min_purge_delay_ms` 提供更细的 purge 速率控制。
  - 为什么重要 / 对本领域的意义:
    - 命中关注点 1(锁竞争)+ 6(sharding/扩展性):SEC 是 jemalloc 既有的"tcache 之外第二层 per-shard 缓存",这次把它**从 HPA 推广到 PAC**,直削 ecache mutex 争用——多核/NUMA 下 free/extent 热路径的老大难。门控默认关、可独立 `nshards` 调,属"先落地基础设施、后调参开启"的典型节奏。
    - `db15a39` 是一则极具教学价值的 **Arm/性能 cacheline 案例**:一个默认关、零代码执行的特性,仅因 struct 字段顺序把热字段挤出 cacheline 就让微基准退 2%。提醒做 AArch64 布局优化的人——`pa_shard_s` 这类高频结构体的**字段排布本身就是性能面**;"把可变长字段移到末尾"可复用为方法。
    - 两条 06-28 的 commit 是今天(周日)真正新落 dev 的动作,印证"jemalloc dev 仍高度活跃"。

- **tcmalloc:HugeRegion/HugePageFiller 内存归还转向"更激进、更默认地还给 OS",THP collapse 强类型化** ｜ 无条件释放 [e60257b](https://github.com/google/tcmalloc/commit/e60257b57cee4b51ff55de98d357677b03b72d29)(06-22)+ 忽略 desired limit [434afcce](https://github.com/google/tcmalloc/commit/434afcce0a25018433e48b9b3330c6ffd7cd13fb)(06-23)+ 删 release-free-swapped opt-out [fcb66dd](https://github.com/google/tcmalloc/commit/fcb66dd4a493)(06-24)+ enable_collapse 强类型 [b444342](https://github.com/google/tcmalloc/commit/b444342be8d60ee0cd448c24853409daf653bc77)(06-26)+ reuse size class 实验接线 [e940a71](https://github.com/google/tcmalloc/commit/e940a71b806f)(06-24)
  - 改了什么:`e60257b` 当 adaptive release 关闭时从 HugeRegion **无条件释放**一部分内存(并加测试);`434afcce` HugeRegion adaptive release 忽略 desired limit;`fcb66dd` 删掉 `release-free-swapped` 的 opt-out 开关与相关代码(该行为转为**默认、不再可关**);`b444342` 把 `HugePageFiller::TreatHugepageTrackers` 里的 `enable_collapse` 做强类型化(THP collapse 路径);`e940a71` 接线一个 "reuse size class" 实验。
  - 为什么重要 / 对本领域的意义:命中关注点 4(大页/THP)+ 5(回收)。HugeRegion 是 tcmalloc 管理大块(>2MB)分配的区域,这一串提交把归还策略从"自适应/带阈值"推向"更激进默认还 OS"并清掉历史 opt-out——**方向信号是 footprint 优先、减少 swapped-but-retained**。对生产 RSS 敏感的读者:`release-free-swapped` opt-out 被移除意味着默认会更主动释放被换出的空闲页,部署前值得评估对你 workload 的 page-fault/抖动影响。

- **mimalloc(dev):atomic_yield 加退避、delayed_free 偏向 part 而非 all** ｜ atomic_yield backoff [9285427](https://github.com/microsoft/mimalloc/commit/92854277385e)(06-23, issue #1317)+ delayed_free 策略 [580c503](https://github.com/microsoft/mimalloc/commit/580c50391e04)(06-23);另有 PR #1293/#1294 backport、osx `reinit_lock` fork 修复 #1315(06-22)
  - 改了什么:`9285427` 给 `atomic_yield` 的 `sleep(0)` 路径加 backoff(自旋退避),缓解高争用忙等(issue #1317);`580c503` 只在 abandonment(线程退出/堆遗弃)时用 `delayed_free_all`,其余情况优先 `delayed_free_part`,缩小一次性清空延迟释放队列的代价。
  - 为什么重要 / 对本领域的意义:命中关注点 6(扩展性)+ 1(争用)。两条都是并发热路径微调——退避降低多核下 CAS 空转的功耗与延迟,`delayed_free` 的 part/all 取舍影响跨线程 free 的尾延迟。属持续打磨,v3.3.2(04-29)后 dev 仍在收口这类并发细节。

- **Linux 内核:slab 7.2 合并窗口落地——`alloc_flags`/`slab_alloc_context` 新参数 + 类型感知的 "allocation tokens"** ｜ part2 merge [335c347](https://github.com/torvalds/linux/commit/335c347686e7)(Linus 树,06-22,入窗锚点);part1 merge [f8115f0](https://github.com/torvalds/linux/commit/f8115f0e8a05)(06-16,窗口边界外、同一合并窗口·上下文)
  - 改了什么:
    - part2(06-22 入 mainline):引入 **`alloc_flags` 参数 + `slab_alloc_context` 结构**(类比 page allocator),在不新增/复用 gfp flag 的前提下调节 slab 行为;`SLAB_ALLOC_NOLOCK` 用于实现 `kmalloc_nolock()` 而不再依赖"无 `__GFP_RECLAIM`"的脆弱判断;`SLAB_ALLOC_NO_RECURSE` 取代 `__GFP_NO_OBJ_EXT`;新增 `kmem_buckets_alloc_track_caller()`;`kmalloc_flags()` 对 mm 内部暴露 `alloc_flags`。
    - part1(06-16):支持 **"allocation tokens"(需 Clang 22+)**——按分配对象**类型**更聪明地切分 kmalloc cache,可替代原先"按调用点地址哈希"的随机切分,**确定性地把"含指针"与"不含指针"的类型分桶**;另含 `kmem_cache_alloc_bulk()`/`mempool_alloc_bulk()` API 简化、**sheaves refill 的性能改进**与清理。
  - 为什么重要 / 对本领域的意义:命中关注点 8(内核 SLUB/slab)里程碑,Vlastimil Babka 树。**allocation tokens 是安全+性能双收**——按类型确定性分桶比地址哈希更难被堆风水利用(削弱 UAF 跨类型重用),同时对 cache 局部性友好;sheaves(per-CPU 数组缓存)refill 优化延续 kmalloc 快路径扩展性主线。注:part1(allocation tokens/sheaves)merge 在 06-16,落近 7 天窗外 1 天,但与 06-22 part2 属同一 7.2 合并窗口,作为同主题上下文一并交代,入窗锚点是 06-22 的 part2 merge。

- **glibc malloc(libc-alpha 评审):fork-handler ABBA 死锁修复 + malloc/ld.so 不重复查 THP;2.44 进入 soft freeze** ｜ 归档索引 [libc-alpha 2026-June](https://sourceware.org/pipermail/libc-alpha/2026-June/date.html);相关单封:ABBA 死锁 #178409、THP-twice v2 #178390、2.44 soft freeze #178291(日期均逐封直取核对)
  - 改了什么(均为**评审中补丁,尚未合入 master**;bminor/glibc `malloc/` 窗内 0 commit 印证):
    - **ABBA deadlock in fork handlers**(H.J. Lu,06-26):修复 malloc fork handler 里的 ABBA 锁序死锁;讨论串带**完整复现用例 + GDB backtrace**,在两种不同 allocator 环境下都能触发,已开 Bugzilla。
    - **Don't call `__get_thp_mode/__get_thp_size` twice**(v2,06-26):ld.so 与 malloc 都会探测内核 THP mode 与 THP page size,补丁避免在 `GLIBC_TUNABLES=glibc.elf.thp=1` 路径上重复查询。
    - **Soft freeze for the glibc-2.44 release**(06-22):glibc 2.44 进入 soft freeze——继 2.43(2026-01-23)之后的下一个半年版,即上述 malloc 改动的落地窗口。
  - 为什么重要 / 对本领域的意义:命中关注点 3(友商/arch malloc 调优)+ 4(THP)。ABBA 死锁是 **fork + 多分配器**场景的真实正确性坑(对"用 jemalloc/tcmalloc 替换默认 malloc 又 fork"的服务有参考价值);THP 查询去重是启动期微优化。2.44 soft freeze 意味着这些 patch 要么本周期合入、要么滑到下半年。
  - **窗外·Arm 强相关上下文**:同档期 libc-alpha 还在评审 "**malloc: aarch64: Add ifuncs for malloc functions**"(Yury Khrustalev / Arm,最新 v6 于 **06-15**,落近 7 天窗外),为 AArch64 上 malloc 提供 ifunc 运行时派发——这是关注点 2(AArch64/鲲鹏)直接相关项,本期未入窗,留待后续跟踪。

- **hardened_malloc:新增原生 arm64 CI(跑 MTE/memtag 测试)+ clang-tidy 清理** ｜ arm64 CI [cd2315c](https://github.com/GrapheneOS/hardened_malloc/commit/cd2315cedff5)(06-27)+ memtag_test 文档修订 [1808bf3](https://github.com/GrapheneOS/hardened_malloc/commit/1808bf382dc6)(06-26)+ 一批 clang-tidy lint 关停(06-21)
  - 改了什么:GitHub CI 新增 arm64 任务(让 MTE/memtag 相关测试跑在**真实 arm64** 上);修 `memtag_test.cc`/README 文字;关闭若干 clang-tidy lint、按 `__clang__` 宏判定编译器。
  - 为什么重要 / 对本领域的意义:命中关注点 2(AArch64)+ 7(安全/MTE)。多为 plumbing,但"在原生 arm64 上跑 MTE 测试"提升了 hardened_malloc 在 Arm MTE 路径上的回归可信度,可与 Scudo/jemalloc 的 MTE 工作互为对照。价值偏低,仅作覆盖完整性收录。

## 源覆盖表
| 类型 | 维度 | 源 | 抓取方式 | 候选→入选 | 备注 |
|---|---|---|---|---|---|
| GCC | 论文 | arXiv cs.PL/recent + cs.SE | HTML list + abs 抽样核对 | 15→2 | AutoPass(06-18 破窗)/Axon(06-24)；新 ID 2606.20373/2606.26344 已直取 abs 核 |
| GCC | 论文 | arXiv 关键词检索(vectorization/PGO) | WebSearch | ~10→0 | 命中多为 2503/2505/2602 旧文，无新增入选 |
| GCC | 资讯 | Phoronix | 关注点扇出 site:(海光/LoongArch/AArch64/GCC) + Wayback CDX | 友商扇出 ~12→2 | 反爬 403 + web.archive WebFetch 被禁；06-24 +12% x86、06-23 海光 Suzhou；CDX 核发布日 |
| GCC | 资讯 | GCC 官方博客 / gcc-1x changes.html(live) | WebFetch | 0→0 | 周日近 1 天无一手新发；changes 仅用于核 SVE/向量化背景 |
| GCC | 资讯 | LWN.net / Arm dev blog | 扇出未命中 | 0→0 | 本窗无 GCC 相关一手新报道 |
| GCC | 上游 | gcc-mirror/gcc (config/aarch64) | GitHub API since=2026-06-24 | 4→4 | 06-24..06-26 落 master；逐条核 committer 日 |
| GCC | 上游 | gcc-patches 邮件列表 | pipermail 2026-June thread.html | 多→1(roundup) | Anubis 绕行成功(pipermail 可读)；未逐封核日期，低置信 |
| GCC | 上游 | gcc-mirror Releases/tags | GitHub API tags | 1→0 | releases/gcc-16.1.0 标签=2026-04-30，出窗(非本周里程碑) |
| GCC | 上游 | gcc-17/changes.html (trunk) | WebFetch | 0→0 | 占位页，无 aarch64 新条目 |
| LLVM | 论文 | arXiv cs.PL recent | HTML list + abs 抽样核对 | ~15→2 | 2606.25244(MLIR形式理论)/2606.26344(Axon超优化)，均 06-24 abs 核实 |
| LLVM | 论文 | 顶会 ICS'2026 / 检索 | WebSearch 摘要 | 1→1(低置信) | 自动向量化 x86+AArch64；称 SVE geomean 1.94×，未核原文/数字 |
| LLVM | 资讯 | discourse.llvm.org/latest | /latest + tag 扫 | ~10→2 | 命中 NEON→SVE 再向量化 RFC(老帖06-15新活跃06-24)+本周活跃 RFC 速览 |
| LLVM | 资讯 | LLVM Weekly | WebFetch #651 | 1→1 | 06-22 digest，含 HIP12/pext-pdep/22.1.8/ClangIR 93%/BOLT 并行DWARF |
| LLVM | 资讯 | blog.llvm.org | WebFetch | 0→0 | 最新文 2026-01-19，窗内无更新(正常低频) |
| LLVM | 资讯 | Phoronix(反爬) | 关注点扇出 site:+RSS | 多→0 | 窗内无新 LLVM/AArch64 一手文；Hygon x86 c86-4g 为 06-09(超窗,归 GCC) |
| LLVM | 上游 | llvm/llvm-project AArch64 commits | GitHub commits 页 + 逐条 commit 核 | ~12→5 | 06-25~26 在窗(interleave-4/A510 sched/SVE MLA/clmul/preserve-flags) |
| LLVM | 上游 | llvm/llvm-project PR(专项) | PR 页核 merge 日 | 2→2 | HIP12 #203446 / pext-pdep #200570，均 06-16 merge(窗外·命中专项,已标日期) |
| LLVM | 上游 | llvm/llvm-project Releases/tags | releases 页单独查 | 1→0(并入资讯) | 22.1.8 tagged 06-16，例行 patch 版 |
| LLVM | 上游 | BOLT(子项目) | LLVM Weekly #651 | 1→0(并入周报) | 并行 DWARF 处理 d3ac9b5，未单独抓 commit |
| LLVM | 上游 | lists.llvm.org llvm-commits | 未抓(Anubis风险) | 0→0 | 本期以 GitHub commits/PR 页直取核对替代，覆盖充分 |
| Go | 论文 | arXiv cs.PL/cs.LG + WebSearch(Go compiler/runtime/GC) | 关键词检索 | ~5→0 | 窗内无 Go 专属强相关；Zorya(2512.10799)为 2025-12 且非 perf，超窗不收 |
| Go | 资讯 | go.dev/blog/all | WebFetch 列表页 | 0→0 | 最新 2026-05-21，窗内无新发 |
| Go | 资讯 | go.dev/doc/go1.27 (living release notes) | WebFetch | 1→0(背景) | WIP 草稿，确认 portable simd 包 + archsimd arm64 Neon；非"今日新发" |
| Go | 资讯 | go.dev/doc/devel/release | WebFetch | 2→0 | go1.26.4/go1.25.11 均 2026-06-02，窗内无新 patch |
| Go | 资讯 | marselester archsimd preview | WebSearch+WebFetch | 1→0(背景) | 2026-01-23 超窗、amd64-only，作收益量级背景 |
| Go | 上游 | golang/go (GitHub 镜像) commits | GitHub API since 06-21，5 路径(ssa/arm64/runtime/simd/obj)过滤 | 34→9 | committer(合入)日逐条核对；9 commits 归为 6 主题条 |
| Go | 上游 | golang/go Releases/tags | GitHub API + release 页 | —→0 | 单独查；窗内无新 tag，最新 go1.26.4 2026-06-02，Go 1.27 预计 08 月 |
| Go | 上游 | go-review Gerrit / golang-dev | WebFetch | 0→0 | JS 渲染未抓通；以 GitHub 镜像合入视图替代，每条 commit 内嵌其 go-review CL 号可溯源 |
| Java | 论文 | arXiv cs.PL/recent | HTML list 扫描 + 关键词过滤 | ~100→0 | 无 JVM/JIT/值类型方向；有源覆盖、无关注点命中（非无货） |
| Java | 资讯 | inside.java（官方） | WebFetch 首页 + tag/valhalla + tag/hotspot | 5→2 | 06-25 播客(窗内) + 06-21 Valhalla(7d 窗外·命中关注点) |
| Java | 资讯 | InfoQ Java Roundup | WebSearch | 1→0 | 最新 jun15(13 天前)超窗，无窗内期号；jun22 未检索到 |
| Java | 资讯 | JVM Weekly | WebFetch | 0→0 | 落地页无近期期号列表，未取到（降权） |
| Java | 资讯 | JEP 537 Vector API 12th | WebSearch + inside.java | 1→0 | inside.java 标记日 05-25 超窗；新动向落 上游 |
| Java | 上游 | openjdk/jdk commits | GitHub API since=2026-06-21 | 64→17 | hotspot/cpu/aarch64 + share/opto + Vector；逐条 API committer date |
| Java | 上游 | hotspot-compiler-dev 列表 | pipermail(403) + mail-archive(404) | —→0 | 反爬/镜像缺失未抓通；集成补丁已由 openjdk/jdk commit 覆盖（见 flags） |
| Java | 上游 | JDK 27 releases/RDP1 | commit 流 RDP1 标记提交 | —→1 | JDK 27 Rampdown Phase 1，GA 2027-03 里程碑 |
| Java | 上游 | JBS bugs.openjdk.org | WebFetch(403) | —→0 | 详情页反爬；改用 GitHub API commit message + WebSearch 取上下文 |
| AI编译 | 论文 | arXiv cs.PL/recent | WebFetch 列表→abs 逐篇核对 | 10→2 | Axon(2606.26344)、MLIR formal theories(2606.25244)，均 06-24 实存；新 ID 已抽样核对 |
| AI编译 | 论文 | arXiv cs.DC/recent | WebFetch 列表+abs | 6→0 | EmuGEMM(2606.25453) 核为手写 kernel 非 codegen，按口径不入选；其余偏 serving |
| AI编译 | 论文 | arXiv cs.LG / WebSearch | 关键词搜索 | 多→0 | 召回多为 2024/2025 旧文，窗内无新增强相关 ML 系统编译论文 |
| AI编译 | 资讯 | PyTorch 博客 | WebFetch 列表→详情页(2 次) | 10→1 | TokenSpeed-Kernel(06-25) 入选，含实测数字；Helion(06-18)/Compile fusion(05-27) 列窗外上下文 |
| AI编译 | 资讯 | TVM discuss /latest | WebFetch | —→0 | 列表返回含旧帖排序，TIRx RFC 明显活跃但无法可靠取近 3 天活跃日，仅佐证上游重构；近 1 天无一手新文 |
| AI编译 | 资讯 | LLVM Weekly | 复用(归 LLVM 类型扫) | —→0 | 覆盖 MLIR/Triton 上游，本类型动态已由上游直采 |
| AI编译 | 上游 | apache/tvm | GitHub API commits since 06-21 | 35→2 | scalable Ramp(#19866)、IR 类型系统重构(#19853/#19885)；含 releases 查(下条) |
| AI编译 | 上游 | iree-org/iree | GitHub API commits + 详情页 | 9→1 | ukernel 框架端到端 codegen(#24571) |
| AI编译 | 上游 | llvm/llvm-project (path=mlir) | GitHub API commits since 06-26 | 18→1(聚类2commit) | SCF 单迭代循环提升(#205826)+XeGPU 连续性分析(#201684, Intel) |
| AI编译 | 上游 | openxla/xla | GitHub API commits + 详情页 | 30+→1 | sweep-line buffer assignment O(NlogM) FAST_MERGE |
| AI编译 | 上游 | triton-lang/triton | GitHub API commits since 06-21 | 36→1(聚类3commit) | nanobind(#10283)+MXFP4 autotune(#10682)+atomic_poll(#10723) |
| AI编译 | 上游 | openxla/stablehlo | GitHub API commits+releases | 2→0 | 仅 2 条(LLVM 集成/整型卷积累加)，无强相关；最近 release 仍 v1.0.0(2024) |
| AI编译 | 上游 | pytorch/pytorch (torch/_inductor) | GitHub API path commits | 8→0 | 多为 CUDAGraph/dynamo plumbing，张量编译关键路径无突出新增 |
| AI编译 | 上游 | Releases/tags(Triton/TVM/IREE/XLA/StableHLO) | GitHub API releases | 5仓→0(窗内) | Triton v3.7.1=06-18(窗外里程碑)、TVM v0.24.0 仅排期 RFC、StableHLO 无新 release |
| 内存库 | 论文 | ISMM 2026 (conf.researchr papers track + ACM DOI) | WebFetch program/track 两次核对 | 9→4 | 会议 2026-06-16 召开,在近 30 天会议窗内;9 篇全量核到标题+作者+DOI,余 5 篇为 GC/GPU/DSM/Grace-Hopper 相邻,降级为上下文 |
| 内存库 | 论文 | arXiv cs.OS recent | WebFetch 列表 | 11→0 | 仅 2 篇沾内存(CXL 池化 2606.24079、带宽调控 2606.23945),非分配器,过滤后 0 |
| 内存库 | 论文 | arXiv cs.DC recent | WebFetch 列表 | 0→0 | 无分配器/内存管理相关 |
| 内存库 | 论文 | arXiv cs.CR recent | WebFetch 列表 | 0→0 | 7 天窗内无 UAF/双重释放/MTE/CHERI/hardened-malloc 新文 |
| 内存库 | 论文 | arXiv 定向搜索 (malloc/slab/THP/memory-safety 2606) | WebSearch ×2 | 多→0 | 命中均为旧文(StarMalloc 2403.09435 / Exgen 2510.10219 / SpeedMalloc 2508.20253 / Reconsidering 2605.17119),无 7 天窗新条目 |
| 内存库 | 论文 | arXiv abs/2605.17119 抽样核对 | WebFetch abs 直取 | 1→1 | 反虚构抽样:标题/作者(van Kempen, Berger)/2026-05-16/ISMM DOI 10.1145/3814942.3816132 均真实存在 |
| 内存库 | 资讯 | Phoronix（Cloudflare 反爬） | site: 关注点扇出 + 镜像，WebFetch 403 | ~12→2 | 走 `site:phoronix.com` 搜 jemalloc/mimalloc/glibc/SLUB/THP/海光/LoongArch 取日期与要点，未读正文 |
| 内存库 | 资讯 | Phoronix · Reserved THP RFC | site: 搜索 | 1→1 | 2026-06-27 入选（THP/HugeTLB 统一，关注点 #4） |
| 内存库 | 资讯 | Phoronix · Linux 7.2 slab / MM | site: 搜索 | 2→1 | slab（06-17）入选为里程碑；MM/MGLRU（06-24 头条页回收）降级，仅取 slab 部分；06-24 日期低置信 |
| 内存库 | 资讯 | Meta engineering.fb.com（jemalloc 一手） | WebSearch | 1→0 | 续投声明 2026-03-02，窗外背景 |
| 内存库 | 资讯 | LWN.net（mm/slab/THP 一手） | WebFetch 周刊列表 | 2→0 | 06-25/06-18 周刊；mTHP（06-11）/写回/KASAN 仅背景，且有约 1 周时效墙 |
| 内存库 | 资讯 | mimalloc 官网 / Releases | WebSearch | 1→0 | v3.3.2/v2.3.2/v1.9.10 均 2026-04-29，窗外 |
| 内存库 | 资讯 | tcmalloc / abseil.io | WebSearch | 1→0 | 无窗内官方发布；仅第三方部署新闻（InMotion 05 月、MongoDB 8.0），不入选 |
| 内存库 | 资讯 | GrapheneOS hardened_malloc（安全加固） | WebSearch + WebFetch | 1→0 | 6 月有『小优化』打包进 OS release，但无独立 allocator 里程碑、未拿到精确日期，低置信，未单列 |
| 内存库 | 资讯 | discourse.llvm.org（Scudo/PartitionAlloc） | WebFetch /帖 | 2→0 | Allocator Partitioning Hints RFC 末活跃 2025-08；LLVM-libc Scudo RFC 03-19；均窗外 |
| 内存库 | 资讯 | The Register / InfoQ | site: 搜索 | 2→0 | Bun 1.1.13 Libpas（04 月）、Squidbleed（06-23 Squid 堆 overread CVE，非分配器设计）——无强相关 |
| 内存库 | 资讯 | X / @phoronix 等 | WebSearch 转述 | -→0 | x.com 未抓通，仅作旁证不入选，不编造推文 |
| 内存库 | 资讯 | Wayback CDX（Phoronix 发现兜底） | Bash curl / WebFetch web.archive.org | 0 | 两路均失败（Bash 504、WebFetch『unable to fetch / Socket closed』），发现改靠 site: 扇出 |
| 内存库 | 上游 | jemalloc/jemalloc dev | GitHub API commits + 逐条 commit 对象核 committer date | 4→4(聚为 1 条) | 全在窗(06-24~28),2 笔今日(06-28)落;SEC-in-PAC 主线 |
| 内存库 | 上游 | google/tcmalloc | GitHub API commits | 7→5(聚为 1 条) | HugeRegion/HugePageFiller 内存归还主题,06-22~26 |
| 内存库 | 上游 | microsoft/mimalloc dev | GitHub API commits | 7→3(聚为 1 条) | 06-22/23 并发微调,余为 backport/osx |
| 内存库 | 上游 | torvalds/linux mm/slub·slab_common·slab.h | GitHub API commits(lore Anubis,改走镜像) | ~18→1(+1 窗外上下文) | 7.2 合并窗口 part2(06-22)入窗,part1(06-16)同窗口上下文 |
| 内存库 | 上游 | GrapheneOS/hardened_malloc | GitHub API commits | 12→1 | arm64 CI(06-27),余 clang-tidy/plumbing |
| 内存库 | 上游 | llvm scudo/standalone | GitHub API commits | 3→0 | 最新 06-18,落近 7 天窗外;含 realloc-shrink retag(MTE)#204031 06-16 |
| 内存库 | 上游 | glibc libc-alpha(sourceware) | pipermail date.html 解析 + 逐封核对真实日期 | 669 封→3(malloc 相关) | ABBA 死锁/THP-twice 06-26、2.44 soft freeze 06-22;aarch64 ifuncs v6=06-15 窗外 |
| 内存库 | 上游 | bminor/glibc malloc/ | GitHub API commits(path=malloc) | 0→0 | malloc/ 窗内无 commit(评审仍在 libc-alpha) |
| 内存库 | Releases | jemalloc / mimalloc / tcmalloc / hardened_malloc | GitHub API releases(单独一步) | 4→0 | 均无窗内新版本:je 5.3.1=04-13、mi v3.3.2=04-29、hm 14=02-22、tc 无 GH release |
| 内存库 | 上游 | chromium PartitionAlloc | chromium gitiles ?format=JSON | 0→0 | 403 需登录,未抓通(auth/反爬墙) |
| 内存库 | 上游 | lore.kernel.org/linux-mm | WebFetch | 0→0 | Anubis 挑战墙,已用 torvalds/linux GitHub 镜像绕行覆盖 slab |
| 内存库 | 上游 | daanx/mimalloc-bench | 横评基准(非代码主源,本期未单抓) | —→0 | 无窗内动态 |
