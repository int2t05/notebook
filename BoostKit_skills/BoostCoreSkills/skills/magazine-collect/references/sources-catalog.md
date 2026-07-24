# 信息源抓取经验沉淀

本文档是"**已经跑过的信息源**"的抓取经验速查表，作用是让下一次再遇到同一个源时不用从头试错。

**本表只是经验沉淀，不是覆盖清单**：
- 当前已沉淀的源以编译器/语言/AI 编译类为主——这是 skill 早期跑过的领域，自然先有这些经验
- **任何领域跑完一轮后，把新出现的源经验补到本表对应类别下即可**——新领域不需要预先占位 section，跑出来什么补什么
- 如果某个源不在本表里，按 `fetch-strategies.md` 里"通用源类型"先归类（项目官方/Weekly/代码仓/邮件列表/学术/公司新闻/技术媒体）再抓取；跑通后回到本表补一行
- 已有经验若过时（如曾经友好的源新加了反爬），抓取实战中发现后直接更新本表

字段含义：
- **抓取友好度**：✅ 直接 WebFetch / ⚠️ 部分受限 / ❌ 反爬严重需绕路
- **建议路径**：进入这个站点后，最高 ROI 的页面是哪一类
- **替代源**：抓不到时可以转向的镜像/转述源

---

## 编译器主线

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `phoronix.com/linux/LLVM` | ❌ | 列表页 → 标题日期 URL | `linux.org` 转载、`forums.phoronix.com`、`daily.dev`、X@MichaelLarabel |
| `phoronix.com/linux/GNU` | ❌ | 同上 | 同上 |
| `llvmweekly.org` | ✅ | 列表页 → 每期 issue | — |
| `github.com/llvm/llvm-project/releases` | ✅ | release 页面 → 官方 notes | `github.com/llvm/llvm-project/blob/main/llvm/docs/ReleaseNotes.md` |
| `lists.llvm.org/pipermail/llvm-commits/` | ⚠️ | 月度归档 → 标题筛选 | 噪声大，**优先用 llvmweekly 反向定位**，不要直接读 |
| `gcc.gnu.org/pipermail/gcc-patches/` | ⚠️ | 月度归档 | 同上，可看 GCC release notes |
| `github.com/gcc-mirror/gcc` | ⚠️ | **此仓库不发 release**（只是镜像），不要去 `/releases` 找。版本信息走 `gcc-announce` mailing list 与 `gcc.gnu.org/gcc-XX/` | `gcc.gnu.org/pipermail/gcc-announce/`、`gcc.gnu.org/gcc-XX/changes.html` |
| `gcc.gnu.org/pipermail/gcc-announce/` | ✅ | 月度归档 → 找 `GCC X.Y Released` 标题 | — |
| `gcc.gnu.org/gcc-XX/` 与 `gcc.gnu.org/gcc-XX/changes.html` | ✅ | release 系列主页 + 详细 changes 页 | — |
| `discourse.llvm.org` | ✅ | 各子论坛热点 / MLIR 分区 | — |

## 语言生态

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `blog.rust-lang.org` | ✅ | 主页 → 近 3 个月 post | — |
| `this-week-in-rust.org` | ✅ | 列表页 → 每期 | — |
| `github.com/rust-lang/rust/releases` | ✅ | release tag | — |
| `go.dev/blog/` | ✅ | 主页 → 近 3 个月 post | — |
| `github.com/golang/go/releases` | ❌ | **此仓库不发 GitHub release**（只打 git tag），不要直连。版本元数据走 `go.dev/doc/devel/release` + `go.dev/doc/go1.XX`，点版本公告走 `golang-announce` 邮件列表 | `go.dev/doc/devel/release`、`golang-announce` Google Groups |
| `groups.google.com/g/golang-announce` | ⚠️ | 点版本 + 安全公告。直连 HTTP 403 概率高 | 走 `WebSearch "Go 1.X.Y released"` 拿摘要；或看 dev.to / phoronix 等转述 |
| `go.dev/doc/devel/release` | ✅ | 总览所有发布与节奏 | — |
| `go.dev/doc/go1.XX` | ✅ | 单版本完整 release notes（最高 ROI 入口） | — |
| `tip.golang.org/doc/` | ⚠️ | 主页只是学习资源入口，不含版本变更信息 | 拿下个版本 tip：`tip.golang.org/doc/go1.XX` 或 `tip.golang.org/doc/next` |
| `tip.golang.org/doc/next` | ✅ | 下个版本 release notes 当前草稿 | — |
| `infoq.com/java/news/` | ⚠️ | 列表页 | 部分文章付费墙，可看 abstract |
| `openjdk.org` | ✅ | JEP 索引 | `openjdk.org/jeps/0` |
| `github.com/openjdk/jdk` | ✅ | release tag、JEP issue | — |
| `docs.python.org/3.XX/whatsnew/` | ✅ | 直接 fetch 对应版本 | — |
| `peps.python.org/pep-0000/` | ✅ | PEP index | — |
| `github.com/python/cpython` | ✅ | release tag | — |
| `webassembly.org/news/` | ✅ | 列表页 | `bytecodealliance.org/articles` |
| `bytecodealliance.org/articles` | ✅ | 列表页 | — |
| `github.com/WebAssembly/proposals` | ✅ | issues / README | — |

## 异构 / GPU / 加速器

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `developer.nvidia.com/blog` | ✅ | 主页 → 按 tag 过滤（CUDA / GPU） | — |
| `gpuopen.com` | ✅ | 主页 → 技术文章 | — |
| `intel.com/content/.../heterogeneous.html` | ⚠️ | 主页 → 看 announcement / case study | `newsroom.intel.com` 同步公告 |
| `riscv.org` | ✅ | news + blog | — |
| `rocm.docs.amd.com` | ✅ | 最新 release notes | — |
| `intel.com/.../oneapi.html` | ⚠️ | release notes | — |
| `hiascend.com` | ⚠️ (GFW 不稳定) | 新闻 / 开发者中心 | 可直接搜索"昇腾 + 版本号" |

## AI 编译

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `discuss.tvm.apache.org` | ✅ | 热点话题 / 最新发布 | — |
| `iree.dev/community/blog/` | ✅ | 列表页 | — |
| `pytorch.org/blog/` | ✅ | 列表页 | — |
| `modular.com/blog` | ✅ | 列表页 | — |
| `discourse.llvm.org/c/mlir/31` | ✅ | MLIR 子论坛热帖 | — |
| `github.com/triton-lang/triton` | ✅ | release + 重要 PR | — |
| `openxla.org` | ✅ | release notes、blog | `github.com/openxla/xla/releases` |
| `github.com/NVIDIA/TensorRT-LLM` | ✅ | release + CHANGELOG | — |
| `github.com/vllm-project/vllm` | ✅ | release + CHANGELOG | — |

## 论文 / 学术

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `arxiv.org/list/cs.AR/recent` | ✅ | 列表页（仅标题摘要） | — |
| `arxiv.org/list/cs.PL/recent` | ✅ | 同上 | — |
| `arxiv.org` （PDF） | ❌（PDF 不要 fetch） | 只读 abstract 页 | — |
| `dl.acm.org` | ⚠️ (大量付费) | abstract 页 | 看 author 个人主页或 arXiv 预印本 |
| `mlsys.org` | ✅ | 历年 proceedings | — |
| `infoworld.com` | ⚠️ | 列表页 | 同 phoronix，可走搜索引擎 |

## 厂商 PR / 新闻

| 源 | 抓取友好度 | 建议路径 | 替代源 |
|---|---|---|---|
| `microsoft.com/.../research/blog/` | ✅ | 列表页 | — |
| `newsroom.intel.com` | ✅ | 列表页 | — |
| `newsroom.arm.com` | ✅ | 列表页 | — |

---

## 源信噪比速判

按"做月刊 digest 的有用度"打分，遇到时间紧时可以优先这些：

| 优先级 | 类型 | 代表 |
|---|---|---|
| ★★★★★ | Weekly / Monthly curate | llvmweekly、this-week-in-rust |
| ★★★★ | 官方 release notes / changelog | github releases、whatsnew、JEP index |
| ★★★★ | 项目官方博客 | rust-lang blog、go.dev blog、pytorch blog |
| ★★★ | 主流技术媒体 | phoronix、infoq |
| ★★★ | 厂商技术博客 | NVIDIA / Intel developer blog |
| ★★ | 论坛 / 邮件列表（话题筛选后） | discourse.llvm.org、lists.llvm.org |
| ★★ | 学术列表（标题筛选后） | arXiv cs.PL / cs.AR |
| ★ | 厂商 PR 稿 / newsroom | newsroom.intel.com、newsroom.arm.com |

---

## 维护说明

- 用户提供新的规则文件时，如果出现了**本表未收录**的源（不论哪个领域），跑完一次后把这个源的抓取经验**补到这里**（友好度、建议路径、是否要绕路）
- 经验补在最贴近的现有大类下即可（编译器主线 / 语言生态 / 异构-GPU-加速器 / AI 编译 / 论文-学术 / 厂商-PR）；若新领域明显不属于任何已有大类，**直接在文件末尾新建一个大类**，类名按领域命名（如 `## 推荐系统` / `## 数据库` / `## 安全` 等），不需要预先占位
- 抓取实战中发现某个源策略不再适用（如曾经友好的源新加了反爬、或某 weekly 停更），也回来更新这里
- 这个文件不是 prompt 的一部分（Agent 只在需要查某个源时按需读），所以可以放心扩充——长度增长不影响 skill 主体性能
