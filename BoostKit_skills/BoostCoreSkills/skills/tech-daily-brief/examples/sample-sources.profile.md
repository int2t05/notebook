# 源画像：compiler-mem（关注集）

> 自动发现于 2026-06-28，可手动编辑。改动后下次跑以改后为准。
> 类型：GCC · LLVM · Go · Java · AI编译 · 内存库
> 一句话定位：编译器工具链(GCC/LLVM/Go/Java/AI编译) + 内存库 的每日动态，聚焦性能、Arm·鲲鹏、友商与 AI 编译。

## 共享特别关注点（所有类型通用的强筛标准）
- 性能优化（SPECCPU / 吞吐 / footprint / PGO / LTO / BOLT）
- Arm / AArch64 · 鲲鹏（SVE/Neon、codegen、cost model、调度模型、页大小）
- 友商动向（Intel / AMD / 海光 Hygon / 龙芯 LoongArch 的工具链/库 enablement）
- 版本发布里程碑（GCC/LLVM/Go/JDK/jemalloc 等主版本）

---

## 类型：GCC
**类型特有关注点**：aarch64 后端 codegen、cost model / tuning model、自动向量化（SVE/NEON、SLP、predicated tail）、指令调度（dispatch / 多发射核）、i386 后端的友商 enablement（Hygon/Intel/AMD 的 march·mtune 串）。
### 📄 论文
- arXiv 分类：cs.PL、cs.AR、cs.PF（辅以 cs.SE / cs.LG 收 LLM-for-compiler / 自动调优）｜ 关键词：auto-vectorization、SVE/NEON codegen、cost model、instruction scheduling、PGO、LTO、superoptimization、reassociation ｜ 顶会：PLDI / CGO / CC / ASPLOS ｜ 其他：`arxiv.org/list/cs.PL/recent`
### 📰 资讯
- 官方/博客：`gcc.gnu.org/gcc-16/changes.html`（live；GCC 16.1.0 已 2026-04-30 发布）、`gcc-17/changes.html`（trunk 占位页）、Arm developer community blog（GCC release 解读）｜ 技术媒体：Phoronix（反爬 403 + web.archive WebFetch 被禁，走「关注点扇出 site: + RSS + Wayback CDX」）、LWN.net ｜ X：—（未配通；GCC 关键开发者推文走搜索转述）｜ newsletter：—
### 💻 上游代码
- 主仓：gcc-mirror/gcc（关注 `gcc/config/aarch64/`、`tree-vect-*`、i386 友商 enablement）｜ 邮件列表：`gcc.gnu.org/pipermail/gcc-patches`（pipermail 静态归档可读，绕过 sourceware Anubis）｜ release：gcc-mirror/gcc tags（`releases/gcc-N`）+ `gcc-N/changes.html`
- 子窗：资讯近 1 天（周日空 → 友商命中破窗近 7 天）/ 上游近 1 天（空 → 近 7 天）/ 邮件列表近 3 天（pipermail 近 1 月归档，per-message 日期低置信）/ 论文近 7 天（命中关注点破窗近 7 天）

## 类型：LLVM
**类型特有关注点**：AArch64 后端 codegen（调度模型 / cost model / 指令选择）、LoopVectorize 与 NEON↔SVE 再向量化、BOLT、**鲲鹏 HIP12(Kunpeng 950) 使能**、`llvm.pext`/`llvm.pdep` 等位操作 intrinsic、MLIR 内编译。

### 📄 论文
- arXiv 分类：`cs.PL`（主）· `cs.AR` · `cs.PF` ｜ 关键词：LLVM, MLIR, LoopVectorize, SVE/NEON, AArch64 codegen, superoptimizer, autovectorization, PGO/LTO ｜ 顶会：CGO · PLDI · CC · ICS ｜ 其他：`arxiv.org/list/cs.PL/recent`（HTML 列表，入选抽样 `abs/<id>` 核对）

### 📰 资讯
- 官方/博客：`blog.llvm.org`（低频，最新文 2026-01-19）· **LLVM Weekly**（`llvmweekly.org`，周更 digest）｜ 论坛：**`discourse.llvm.org/latest`**（按 AArch64 / IR-Optimizations / Loop Optimizations tag 扫，**含老帖新活跃 RFC**）｜ 技术媒体：Phoronix（反爬，关注点扇出 `site:` + RSS + Wayback CDX）· LWN ｜ X：—（暂无稳定 handle）

### 💻 上游代码
- 主仓：**`llvm/llvm-project`**（关注 `llvm/lib/Target/AArch64/`、`llvm/lib/Transforms/Vectorize/`、`bolt/`）｜ 邮件列表：`lists.llvm.org/pipermail/llvm-commits`（Anubis 时走 `mail-archive.com` 镜像）｜ **Releases/tags 单独查**：`github.com/llvm/llvm-project/releases`（22.1.8 = 2026-06-16）
- 子窗：资讯近 1 天（周末放宽近 3–7 天）/ 上游近 1 天（周末放宽近 7 天）/ 邮件列表近 3 天 / 论文近 7 天；**命中专项（HIP12 / pext-pdep）/ 版本里程碑放宽近 7 天并标实际日期**

## 类型：Go

**类型特有关注点**：SSA 后端 / cmd/compile codegen 正确性 · GOEXPERIMENT=simd（`simd` 可移植包 + `simd/archsimd`，**arm64 Neon 128-bit**）· arm64 codegen · PGO / 新内联器(newinliner) · runtime 内存分配快路径 · GC(Green Tea) · 版本里程碑(Go 1.26.x / Go 1.27 dev)

### 📄 论文
- arXiv 分类：`cs.PL`（主，编译/语言）· `cs.LG`+`cs.DC`（runtime/GC/调度协同）· 偶 `cs.PF`(性能评测) ｜ 关键词：Go runtime, garbage collector / mark-scan locality, escape analysis, PGO, SSA backend, SIMD codegen, goroutine scheduler ｜ 顶会：PLDI / CGO / OOPSLA / ISMM(GC) ｜ 其他：Go team 设计文档(design proposals)、go.dev/blog 技术深文
- 说明：Go 编译器/runtime 的工程优化**几乎不走 arXiv**，多以 design doc + go.dev/blog 形式发布；本维度低频，论文检索作"扫一眼"，深度交给关注集级 cs.PL 扫描与 `paper-digest`。

### 📰 资讯
- 官方/博客：`https://go.dev/blog/all`（一手最权威，活跃但低频，最新 2026-05-21）· **`https://go.dev/doc/go1.27`**（Go 1.27 living release notes，WIP 草稿，确认 portable `simd` 包 + archsimd arm64 Neon）· `https://go.dev/doc/devel/release`（patch 发布跟踪）
- 技术媒体：InfoWorld / The New Stack（Go 版本/GC 报道，二手）· 个人技术博客(如 marselester archsimd 系列、hitzhangjie GC 深读) — 二手，标日期
- X / 社区：`@golang`（X 反爬，走搜索转述/对应博客）· golang-weekly newsletter
- 子窗：资讯近 1 天（周末/低频放宽近 3 天）；命中里程碑(Go 1.27/友商) 放宽近 7 天并标实际日期

### 💻 上游代码
- 主仓：`golang/go`（GitHub 镜像；上游真身 = `go.googlesource.com/go` Gerrit）。关注子目录：`src/cmd/compile/internal/ssa/`(及 `_gen/simdARM64.rules`)、`src/cmd/compile/internal/arm64/`、`src/cmd/compile/internal/inline/`(PGO)、`src/simd/` + `src/simd/archsimd/`、`src/runtime/`(malloc/mgc/调度)、`src/cmd/internal/obj/arm64/`
- 评审/邮件列表：`go-review.googlesource.com`(Gerrit，JS 渲染难直抓——以 GitHub 镜像合入视图替代，每条 commit 内嵌其 CL 号可溯源)、`golang-dev` Google Group、`golang/go` issues(proposal)
- Releases/tags：`golang/go` tags + `go.dev/doc/devel/release`（**每期必单独查一次**；当前 go1.26.4 / go1.25.11 均 2026-06-02，Go 1.27 预计 2026-08）
- 子窗：commit/PR 近 1 天；周末放宽近 7 天；入窗以合入(merge to master)日为准，非作者写作日

## 类型：Java
**类型特有关注点**：C2 JIT（分层编译策略 / 逃逸分析 BCEscapeAnalyzer / 向量节点 codegen）、aarch64 intrinsic（加密 P-256/X25519、数学、字符串）、Vector API（Panama，Float16 / SVE·NEON codegen、值类前置依赖）、Valhalla 值类型（flattening / 标量替换）、Project Leyden AOT（AOTCache 与分层编译策略交互）、JDK 版本里程碑（26 GA / 27 Rampdown）。

### 📄 论文
- arXiv 分类：`cs.PL`（主：JIT / 字节码 / 值类型 / 托管运行时向量化）｜ 兼扫 `cs.AR`（codegen 协同设计）、`cs.PF`（perf 评测）
- 关键词：JIT compilation, HotSpot, JVM, managed runtime, escape analysis, value types / Project Valhalla, SIMD / Vector API, tiered compilation, AOT / Leyden, scalar replacement, on-stack replacement
- 顶会：PLDI / OOPSLA / CGO / ECOOP（+ VMIL、MoreVMs workshop）——JVM/JIT 专向论文低频，按会期发布；日扫常空
- 其他：cr.openjdk.org 设计稿（如 John Rose values 笔记）、OpenJDK wiki
### 📰 资讯
- 官方/博客：**inside.java**（活跃，含 `tag/hotspot`、`tag/valhalla`、"JEP targeted to JDK N" 公告）｜ Oracle Java 博客 `blogs.oracle.com/java` ｜ `openjdk.org/jeps/<n>`
- 技术媒体：**InfoQ Java 频道**（Java News Roundup 周报，周一发）｜ **JVM Weekly**（Substack 聚合，落地页常抓不到期号列表，降权）
- X：`@OpenJDK`（反爬，走搜索/转述，抓不到如实标）
### 💻 上游代码
- 主仓：**openjdk/jdk**（关注 `src/hotspot/cpu/aarch64/`、C2 `src/hotspot/share/opto/`、Vector API `jdk.incubator.vector` + `PhaseVector`、AOT `src/hotspot/share/{ci,cds,classfile}`）——GitHub API `?since=` 取 commit 流，**逐条 committer date 核窗**
- 邮件列表：`hotspot-compiler-dev` / `leyden-dev` / `valhalla-dev`（mail.openjdk.org；pipermail 反爬、mail-archive 镜像不全，集成补丁以 openjdk/jdk commit 为准）
- releases / 里程碑：`openjdk.org/projects/jdk/27`（RDP1）、`jdk.java.net` EA、JBS `bugs.openjdk.org`（详情页反爬，配 GitHub API commit message + WebSearch 取上下文）
- 子窗：资讯近 1 天（周末放宽近 3 天，命中关注点放宽近 7 天）/ 上游 commit 近 1 天（周末放宽近 7 天）/ 邮件列表近 3 天 / 论文近 7 天

## 类型：AI编译
**类型特有关注点**：新 IR / pass / lowering（MLIR dialect、TVM TIRx/Relax、StableHLO）、张量 codegen 与可伸缩向量化（scalable vector → SVE/RVV）、算子融合、autotuning（MetaSchedule / Triton autotuner / Helion）、量化 codegen（MXFP4/FP8/sub-byte）、CPU/GPU 后端 codegen（LLVMCPU ukernel、XeGPU、Gluon）、张量编译栈版本里程碑（Triton/TVM/IREE/XLA releases）。叠加共享关注点：性能优化、Arm·AArch64·鲲鹏、友商动向（Intel XeGPU / AMD CDNA·Triton / 海光 / 龙芯）、版本发布。

### 📄 论文
- arXiv 分类：`cs.PL`（张量编译/codegen，主）、`cs.LG`（ML 系统/张量编译）、`cs.DC`（并行/调度/serving kernel）、偶涉 `cs.AR`/`cs.PF`。检索入口：`arxiv.org/list/cs.PL/recent`、`arxiv.org/list/cs.DC/recent`、`arxiv.org/list/cs.LG/recent`（HTML 列表优先，**不**用 export API）。
- 关键词：tensor compiler, code generation/codegen, MLIR, GPU kernel/Triton, operator fusion, autotuning, quantization codegen (MXFP4/FP8/sub-byte), polyhedral, e-graph/equality saturation, superoptimization, scalable vectorization。
- 顶会：MLSys 2026（已结束，扫 accepted papers）、CGO/PLDI（编译侧张量）、OSDI/ATC（系统侧张量编译/serving）。
- 子窗：arXiv 近 7 天；会议近 30 天录用 + 即将召开。新 arXiv ID（`2606.xxxxx`）入选须抽样直取 `abs/<id>` 反虚构核对。

### 📰 资讯
- 官方/项目博客（一手）：PyTorch 博客 `pytorch.org/blog/`（torch.compile / Inductor / Triton / Helion 内核，活跃，06-25 有新文）；TVM discuss `discuss.tvm.apache.org/latest`（按最近活跃扫，RFC 常老帖新活跃）；OpenXLA / Google Developers Blog（XLA/StableHLO）；Arm Community blog（AArch64 视角的 AI codegen）。
- 聚合：LLVM Weekly（覆盖 MLIR/Triton 上游动态，周更）。
- X/推特：Triton/TVM/MLIR 核心开发者 + 项目官号；X 反爬走搜索转述 / 对应博客 RSS，抓不到如实标。
- 子窗：近 1 天（薄则近 3 天）；命中关注点的友商/里程碑放宽近 7 天并标实际日期。

### 💻 上游代码
- 主仓（owner/repo + 关注子目录）：`triton-lang/triton`、`apache/tvm`（TIRx/Relax/ARITH）、`iree-org/iree`（`compiler/.../Codegen/LLVMCPU`、GPU codegen）、`openxla/xla`（`xla/service/`）、`openxla/stablehlo`、MLIR 在 `llvm/llvm-project/mlir/`、`pytorch/pytorch`（`torch/_inductor`）。
- peer/对照：`NVIDIA/cutlass`、`google/jax`（XLA 前端）、`bytecodealliance/wasmtime`（Cranelift）。
- 社区/评审：TVM discuss、Triton/IREE GitHub Discussions、discourse.llvm.org（MLIR RFC）。
- Releases/tags：每个主仓单独查一次 releases（Triton/TVM/IREE/XLA/StableHLO 版本里程碑只在 releases 可见）。
- 子窗：commit/PR 近 1 天；社区/邮件列表近 3 天；周末/清淡日 fallback 近 7 天，窗外里程碑单独标注。

## 类型：内存库
**类型特有关注点**：大页/THP/HPA · 碎片/footprint · 锁竞争/NUMA/分片 · 安全加固(MTE/Scudo/PartitionAlloc/hardened_malloc) · 内核 SLUB/slab。
### 📄 论文
- arXiv cs.OS(主)/cs.DC/cs.PL/cs.AR(PIM)/cs.CR(安全主轴) + 关键词(memory allocator/malloc/fragmentation/THP/NUMA/footprint + UAF/MTE/CHERI/secure allocator) + 顶会以ISMM为第一优先(2026与PLDI'26同场,录用见conf.researchr.org/home/ismm-2026 + ACM DL 10.1145/3814942),辅以ASPLOS/OSDI/SOSP/ATC/EuroSys/PLDI及安全顶会USENIX Security/S&P/CCS/NDSS。子窗arXiv近7天/会议近30天。已验证ISMM26页与ACM proceedings可达,抽样arXiv ID真实。
### 📰 资讯
- 一手官方博客engineering.fb.com(Meta/jemalloc,2026-03-02续投声明✓)、microsoft.github.io/mimalloc、abseil.io(tcmalloc)、llvm.org Scudo文档、GrapheneOS/grapheneos.social(hardened_malloc/MTE);技术媒体LWN.net(内核mm/slab/THP一手,2026-06周刊活跃✓,首周订阅墙)、Phoronix(Cloudflare反爬,WebSearch site:绕行)、The Register/InfoQ;社区theconsensus.dev + daanx/mimalloc-bench;X反爬走Mastodon/搜索转述。子窗近1天(薄则近3天)。
### 💻 上游代码
- 主仓jemalloc/jemalloc(dev分支,2026-06-28仍活跃,重点hpa.c/pa.c/arena.c/sec.c)、google/tcmalloc、microsoft/mimalloc(dev/dev-slice)、bminor/glibc(malloc/镜像);peer/对照GrapheneOS/hardened_malloc、llvm-project compiler-rt/lib/scudo/standalone、PartitionAlloc(chromium源树base/allocator/partition_allocator,无独立repo)、torvalds/linux(mm/slub.c·slab_common.c)、mimalloc-bench;邮件列表sourceware libc-alpha pipermail(glibc一手,2026-01活跃)、lore.kernel.org/linux-mm、patchwork linux-mm、vbabka slab.git(Anubis);release: jemalloc 5.3.1、glibc 2.43(2026-01-23)、mimalloc/tcmalloc/LLVM。子窗commit近1天/邮件列表近3天/清淡日近7天。
- 子窗：资讯近1天(薄则近3天)/上游 commit 近1天·邮件列表近3天·清淡日近7天/论文近7天

## 发现备注
- 反爬：Phoronix(Cloudflare/Anubis,走关注点扇出 site:+RSS+Wayback CDX)、X(未配通,搜索转述)、sourceware/lore(Anubis,走 pipermail/mail-archive 镜像/git.kernel.org 子树)。
- [需人工核验]：MLSys/PLDI/ISMM 2026 正式录用名单页上线时间；Go Gerrit/golang-dev 为 JS 渲染、走 GitHub 镜像替代。