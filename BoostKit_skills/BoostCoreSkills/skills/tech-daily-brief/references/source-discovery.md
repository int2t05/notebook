# 源自动发现 + 源画像模板

新关注集第一次跑时没有源画像。本文件讲**如何为一个关注集里的每个类型自动发现三维度最匹配的源**，以及把发现结果写成什么格式。目标：发现一次、缓存复用，之后每天不用重新发现。

> 一个关注集（如 `compiler-mem`）含多个**类型**（如 GCC / LLVM / Go / Java / AI编译 / 内存库）。**一份**画像（`<标签>/sources.profile.md`）覆盖全部类型——下面的"维度发现启发式"对**每个类型**各跑一遍，最后按类型组织进一份画像（模板见文末）。

## 总原则

- **优先一手、稳定、可程序化访问的源**：官方博客 > 聚合周报 > 代码仓 release/commit > 邮件列表 > 二手新闻媒体。
- **每个源都要在发现阶段验证可达 + 验证时效**：`WebSearch` 找到候选后，至少 `WebFetch` 一次确认不是死链/纯反爬墙；**还要看它是否仍在更新**——若某"发布/新闻"页最新条目已是一两年前（实测 `gcc.gnu.org/news.html` 末条停在 2024-10），**别把它当发布跟踪源**，换成 live 的 release-series changelog（如 `gcc.gnu.org/gcc-16/changes.html`）或邮件列表 status report。拿不到就标 `[需人工核验]` 写进画像但降权。
- **每条特别关注点至少配 1 个能命中它的源（HARD）**：先提炼关注点，再确保**每条关注点都有专属源**。实测最大坑是"关注点列了 AI 编译/张量编译器，上游却零 Triton/TVM/IREE/XLA 仓库、论文无 MLSys、cs.LG 没扫"——关注点与源脱节会让后续在没扫的源上下"无货"结论。发现完成后自检：逐条关注点 → 指到至少一个源。
- **覆盖盲区自查**：按领域语义补齐常被遗漏的"轴"——
  - 领域含**安全/加固**面 → 加 `arXiv cs.CR` + 安全顶会（USENIX Security / IEEE S&P / CCS）+ 加固实现仓（如分配器领域的 PartitionAlloc、Scudo、hardened_malloc）。
  - 领域含 **AI/ML** 面 → 加 MLSys + 对应框架/编译器上游（Triton/TVM/IREE/XLA 等）。
  - 领域有**内核侧**面 → 加 LWN.net + 对应子系统 git 树（如 `git.kernel.org/.../slab.git`）+ 邮件列表镜像。
- **宁可少而准**：每维度 4–8 个高质量源够用，但**关注点全覆盖优先于源数量克制**——先保证每条关注点有源，再谈精简。
- **沉淀关注点**：发现源的同时，结合领域语义提炼 3–6 条「特别关注点」（这是后续强筛的唯一硬标准），并推一份"友商/对照对象"清单（若该领域有竞争格局）。

## 维度① 📄 论文：要发现什么

1. **arXiv 分类**：根据领域语义推 1–4 个 arxiv category。常见映射：
   - 体系结构/硬件 → `cs.AR`；编程语言/编译 → `cs.PL`；分布式/系统 → `cs.DC`、`cs.OS`；
   - 数据库 → `cs.DB`；安全 → `cs.CR`；机器学习系统 → `cs.LG` + `cs.DC`；网络 → `cs.NI`。
   - 不确定时用 `WebSearch "arxiv <领域英文> recent"` 看命中论文落在哪些分类。
2. **关键词**：抽 6–12 个领域核心英文关键词 + 同义扩展（供 arXiv/检索用）。
3. **顶会**：列该领域 2–6 个顶会（如系统：OSDI/SOSP/ATC/EuroSys；编译：PLDI/CGO/CC；数据库：SIGMOD/VLDB；安全：S&P/USENIX Security/CCS）。看"近 30 天有没有发布录用名单/proceedings"或"即将召开"。
4. **其他**：领域内知名 lab / researcher 主页、OpenReview、相关 blog。

> 论文源发现不必很全——arXiv 分类 + 关键词 + 2–3 个顶会就能覆盖日常。深度论文综述交给 `paper-digest`。

## 维度② 📰 资讯：要发现什么

1. **官方/项目博客**：领域核心项目的官方 blog / news 页（一手、最权威）。
2. **技术媒体**：覆盖该领域的媒体（如系统软件类常见 Phoronix、InfoQ、The Register；AI 类 VentureBeat、The Decoder 等）。**注意反爬**：Phoronix 等用搜索绕行。
3. **X/推特关键账号**：领域内关键人物/项目官号。X 反爬严重，发现时记下 handle，抓取时走"搜索引擎检索该账号近期推文 / nitter 镜像 / 账号对应的博客/RSS"，详见 dimension-playbooks。抓不到如实标注。
4. **厂商 newsroom / newsletter**：相关厂商发布页、领域 weekly newsletter（如 DB Weekly、This Week in Rust 之类）。

发现方法：`WebSearch "<领域> blog OR newsletter OR weekly"`、`WebSearch "<领域> news site"`、`WebSearch "<核心项目> official blog"`，逐个 `WebFetch` 验证可达性与更新频率。

## 维度③ 💻 上游代码：要发现什么

1. **主仓库**：领域最核心的 1–3 个上游 repo（GitHub/GitLab）。记下 `owner/repo` + 关注的子目录（如只看性能关键路径，参考 compiler-weekly-digest 对 LLVM 只看 `llvm/`、Go 只看若干 perf 路径）。
   - **关注子目录要"按关注点反推全集"，别只列一个后端（HARD）**：列关注子目录时回看该类型的**全部关注点**，把每条关注点对应的子目录都列上——否则后续 commit 扫描会被 path 收窄到一个后端、漏掉其他后端上命中关注点的提交。典型：**GCC** 的关注点含 Arm（→`gcc/config/aarch64/`、`gcc/tree-vect*`）**和**友商 Intel/AMD/海光/龙芯（→`gcc/config/i386/`、`gcc/config/loongarch/`），所以子目录必须三者都列，不能只写 aarch64（实测只写 aarch64 漏了 i386 的 b64fc29 memset/memcpy 优化）。**LLVM** 同理（`llvm/lib/Target/AArch64` + `X86` + `LoongArch`）。
2. **peer / 对照仓库**：竞争或可对照的仓库（看不同技术路线）。
3. **patch archive / 邮件列表**：很多上游（GCC、LLVM、Linux 子系统）真正的评审在邮件列表/patch archive：
   - GCC：`gcc.gnu.org/pipermail/gcc-patches`
   - LLVM：`lists.llvm.org/pipermail/llvm-commits`、Discourse `discourse.llvm.org`
   - Linux 子系统：对应 `lore.kernel.org/<list>`
   - 用 `WebSearch "<项目> mailing list patches"` / `"<项目> lore.kernel.org"` 发现。
4. **release notes / changelog**：项目 releases 页。

发现方法：`WebSearch "<领域核心项目> github"`、`WebSearch "<项目> mailing list"`，确认仓库活跃度（近期有无 commit）。

## 源画像模板（一份/关注集，按类型组织）

发现完成后，写**一份**到 `<标签>/sources.profile.md`。结构 = 关注集级「共享特别关注点」+ 每个类型一节（含该类型三维度源 + 类型特有关注点）：

```markdown
# 源画像：<标签>（关注集）

> 自动发现于 <YYYY-MM-DD>，可手动编辑。改动后下次跑以改后为准。
> 类型：GCC · LLVM · Go · Java · AI编译 · 内存库
> 一句话定位：<这组类型合起来读者最关心什么>

## 共享特别关注点（所有类型通用的强筛标准）
- 性能优化（SPECCPU / 吞吐 / footprint / PGO / LTO）
- Arm / AArch64 · 鲲鹏（SVE/Neon、codegen、调度模型、页大小）
- 友商动向（Intel / AMD / 海光 Hygon / 龙芯 LoongArch 的工具链/库 enablement）
- 版本发布里程碑

---

## 类型：GCC
**类型特有关注点**：<如 aarch64 后端 codegen、cost model、向量化>
### 📄 论文
- arXiv 分类：<cs.PL ...> ｜ 关键词：<...> ｜ 顶会：<PLDI/CGO/CC ...> ｜ 其他：<...>
### 📰 资讯
- 官方/博客：<gcc-16/changes.html(live) ...> ｜ 技术媒体：<LWN / Phoronix(反爬) ...> ｜ X：<@handle ...> ｜ newsletter：<...>
### 💻 上游代码
- 主仓：<gcc-mirror/gcc（关注 gcc/config/aarch64/）> ｜ 邮件列表：<gcc.gnu.org/pipermail/gcc-patches> ｜ release：<changes.html>
- 子窗：资讯近1天/上游近1天/邮件列表近3天/论文近7天（清淡日放宽近7天）

## 类型：LLVM
…（同上三维度）

## 类型：Go
## 类型：Java
## 类型：AI编译
## 类型：内存库
…

## 发现备注
- <哪些源验证可达、哪些反爬需绕行(Phoronix/Anubis/X)、哪些 [需人工核验]、哪些关注点跨类型拼源>
```

**每个类型都要过"关注点↔源配对"与"覆盖盲区自查"两关**（见总原则）：如 AI编译类型配 MLSys + Triton/TVM/IREE/XLA + cs.LG/cs.DC；内存库类型配 cs.CR + USENIX Security + Scudo/PartitionAlloc + 内核 slab 树 + LWN；Java 配 OpenJDK + hotspot-compiler-dev；Go 配 golang/go + go.dev。

## 增量精炼

源画像不是一次定死的。每天跑完若发现：某源连续多天 0 产出 / 反爬无法绕行 / 有更好的新源——可在画像「发现备注」里记一句，并在回复用户时提示"建议把源 X 换成 Y"，把增删决策权交还用户，不要静默改画像的核心源列表。增删类型 = 直接编辑画像（加/删一节）。
