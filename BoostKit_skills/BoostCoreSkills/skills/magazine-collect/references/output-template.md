# 输出模板详细说明（v3 — 精简版）

本文档定义月刊收集 skill 产物 md 的精确结构与写作要求。**写之前必读**。

**本模板与领域解耦**——结构、字段、写作密度的要求适用于任何技术领域；具体筛选关键词、关注对象、对照目标都来自规则文件，不在本文档预设。

本版（v3）相对 v2 的关键变化：

1. **只保留 3 个章节**：〇 源覆盖表 / 一 本期核心脉络 / 二 核心事件
2. **去掉优先级三档**（🔥/🟡/⚪）：所有入选事件都已通过 Step 4 的"特别关注点"筛选，不再分档；标题不加 emoji，事件元数据不写"优先级"行
3. **背景压缩到 1 句话**（最多 2 句）、**启发压缩到 1~2 句话**
4. **删除"按主题归档 / 补充事件 / takeaways / 原文链接合集"四个章节**——Step 4 强筛后核心事件已经够精，二次组织对读者价值有限
5. **排序按日期降序**（最新在上）

设计原则：**宁缺毋滥，信噪比拉满**。一份 10 条全部命中规则文件"特别关注点"的事件，远胜一份 20 条混杂的事件。

---

## 完整模板骨架

> 下方骨架中带 `<...>` 的为占位符，请按实际内容填充；源覆盖表里的具体 URL 行（phoronix/llvmweekly/lists.llvm.org 等）只是**编译器领域的填充示例**，新领域请替换为当前规则文件该板块的实际信息源 URL。

````markdown
# <领域名> 近 <N> 个月（<start> ~ <end>）要闻速览

> 数据来源：<本期实际覆盖的源列表>
> 整理时间：<YYYY-MM-DD>
> 覆盖时段：<YYYY-MM-DD 至 YYYY-MM-DD>
>
> 说明：<如有反爬/绕路/降级，一句话交代；没有可省略此行>

---

## 〇、源覆盖表

| 规则文件列的源 | 抓取方式 | 候选条目 | 入选条目 | 备注 |
|---|---|---|---|---|
| https://www.phoronix.com/linux/LLVM | WebSearch 绕路（直连 Cloudflare 拦截） | 12 | 5 | 二手摘要 |
| https://llvmweekly.org/ | WebFetch 主页 + 抓 #634/#640/#646 三期 | 30+ | 3 | 覆盖窗口 13 期 |
| https://github.com/llvm/llvm-project | WebFetch /releases | 6 个点版本 | 1 | 主仓 commit 走邮件列表 |
| https://lists.llvm.org/pipermail/llvm-commits/ | 月度归档抽查关键词过滤 | 约 1.2 万 → 4 强相关 | 2 | 全量噪声大，按 fetch-strategies 降级 |

---

## 一、本期核心脉络（一句话总结）

- **<主题词>**：<一句话>
- ...（4~7 条 bullet）

---

## 二、核心事件（按日期降序，最新在上）

### <YYYY-MM-DD> ｜ <事件人话标题>

- **URL**：<https://example.com/...>
- **背景**：<1 句话，最多 2 句。回答"为什么这件事现在出现"——给出最小必要的时间/空间上下文。>
- **要点**：
  - <具体做了什么，含可核验细节：数字、版本号、对象/指标/平台名等>
  - <子要点 2>
  - <…>
- **启发**：<1~2 句，actionable。直接告诉读者"如果你在做 X，下一步该 Y"。>

### <YYYY-MM-DD> ｜ <下一个事件>

…
````

---

## 事件入选标准（关联 SKILL.md Step 4）

逐条事件做以下判断，**不入选的事件直接舍弃，不进任何附录段**：

| 事件类型 | 入选与否 |
|---|---|
| **直接命中规则文件该板块的"特别关注点"** | ✅ **必入选** |
| **大版本发布 / 跨板块重大事件**（虽未直接命中关注点，但读者大概率想知道） | ✅ **入选** |
| **命中"筛选类别"但与"特别关注点"无直接交集**（如生态新闻、横评、综述） | ⚠️ **视情况**——对读者"特别关注点"工作有间接价值（如同领域横评数据可被参考）就入选；否则舍弃 |
| **与"特别关注点"无关、纯文档/治理/小特性、非本板块主题的内容** | ❌ **舍弃** |

### 如何提取规则文件该板块的"特别关注点"（通用流程）

跑某板块前，先打开规则文件、定位到该板块的"特别关注点"字段，做以下三件事：

1. **拆出关键词清单**：把字段里的每一个名词/对象/指标拆出来，组成 OR 条件列表。
   - **编译器领域示例**（来自 `examples/compiler-magazine-collect.md` 的 LLVM 板块）：规则文件写 `性能优化（SPECCPU），鲲鹏相关，友商变化（Intel/AMD/海光/龙芯）`，关键词清单 = `SPECCPU` ∪ `鲲鹏 / hip12 / tsv110 / AArch64 / SVE / SME` ∪ `Intel / znver5 / znver6 / Wildcat Lake / Nova Lake` ∪ `AMD` ∪ `海光 / Hygon` ∪ `龙芯 / Loongson`
   - **搜推广领域示例**（假设规则文件该板块写 `召回模型架构、向量检索性能、对标 Meta/Google 推荐系统`）：关键词清单 = `召回 / 双塔 / embedding` ∪ `向量检索 / ANN / HNSW / FAISS / ScaNN` ∪ `Meta` ∪ `Google` ∪ `recsys`
   - **数据库领域示例**（假设规则文件该板块写 `MVCC、向量化执行、对标 ClickHouse/DuckDB`）：关键词清单 = `MVCC / snapshot isolation` ∪ `向量化 / vectorized / columnar` ∪ `ClickHouse` ∪ `DuckDB`

2. **扩展同义词/别名**：每个关键词补上常见的英文/中文别名、产品代号、缩写。Skill **不预设领域同义词表**——按规则文件该板块的领域自己列。

3. **逐条事件命中判定**：抓回的每条事件，看标题/摘要/正文是否命中清单中任一关键词。命中 → 入选；未命中但属"大版本发布 / 跨板块重大事件" → 入选；其余 → 舍弃。

**严禁：** 把过往跑过的领域的关键词清单当作通用筛选词带到新领域。每次跑新板块都从当前规则文件重新提取。

事件总数控制在 **8~15 条** 为宜。

---

## 事件三段式写作规范（背景 / 要点 / 启发）

规则文件原话："**总结和表达：背景，要点，启发**"。每段的职责与字数约束如下。

> **说明：** 本节及下面"反例"段的所有好/坏例子都取自编译器领域（来自 `examples/llvm-2026-02-23_2026-05-23.md`），仅作为**写作密度与具体度**的示范——新领域请按你的规则文件类比，把示例里的"LLVM / Arm C1 / SVE2.1 / 鲲鹏 / 友商"等替换为你领域的具体技术对象与对照对手。**字数约束、具体度要求、actionable 要求都与领域无关，必须遵守。**
>
> **规则文件可能扩展事件三段式：** 例如某板块"总结和表达方式"写"背景，要点，启发，工业界价值，学术界价值"——那就按 5 段写，**额外段同样要满足"具体、可核验、actionable"的密度要求**，不要因为是扩展段就糊弄过去。

### 背景（1 句话，最多 2 句）

**核心约束：只点出"为什么这件事现在出现"，不要长篇上下文铺垫。**

- 大多数情况下 1 句话足够；最多 2 句
- 给出最小必要的时间/空间上下文
- 帮助读者理解事件的"前因"，但不替读者上历史课

**好例子**（1 句）：
> LLVM 22 已在 2 月落地 Arm C1 全系基础 `-mcpu`，本次给旗舰 C1-Ultra 配上完整调度模型。

**好例子**（2 句）：
> AMD HIP 是 AMD 自家 GPU 编程接口，对标 NVIDIA CUDA。本次默认切到 LLVM new offload driver，与上游 CUDA / OpenMP offloading 路径统一。

**坏例子**（太长，3 句以上铺垫）：
> AMD HIP 是 AMD 自家的 GPU 编程接口，对标 NVIDIA CUDA。2024 年起 LLVM 引入了统一的 new offload driver 用以收敛 CUDA / HIP / OpenMP offloading 的差异接口，CUDA 已先于本季度切换。本次 HIP 默认切到 new offload driver，意味着 AMD 也完成了这条迁移路径，与上游统一调度模型对齐。
> ↑ 信息冗余，应该压缩到 1~2 句。

### 要点（典型 3~5 个 bullet，硬上限 ≤10 行）

**核心约束：具体、可核验，但总长度受控。**

- 含具体数字、版本号、对象/平台名、PR/commit 号、测试机型等可核验细节
- 不要泛化，越具体越好
- **总 bullet 行数（含嵌套子项）硬上限 10 行**——超过这个数，说明你在塞"读者不会逐条读完的次要信息"，必须合并同类项或舍弃
- 典型分布是 3~5 条主 bullet、无或少量嵌套；超过 5 条主 bullet 时认真问一遍"这条事件是不是应该拆成两个事件"
- 如果一条事件横跨多个子主题（如大版本发布既有 GC、又有编译器、又有平台变更），优先把每个子主题压缩成 1 行——读者要细节会点 URL，不需要在 digest 里读完整 release notes

**好例子**：
- Apple 的 Amara Emerson 在 LLVM 主干提交：当目标支持 **SVE2.1 或 SME2** 时，AArch64ExpandPseudo 直接生成 `ptrue + multi-vec` 操作替代 N 条单 vec
- x2 case 在代码大小上 neutral，但依赖 microarch 仍可获益
- 新增测试 `sve-multivec-spill-fill.ll`

**坏例子**：
- 改了 SVE
- 性能更好了

### 启发（1~2 句话）

**核心约束：actionable，最短但最有价值。**

- 1 句话最佳；最多 2 句
- 直接告诉读者"如果你在做 X，下一步该 Y"
- 可以涉及规则文件特别关注点提到的对照对象、长期趋势、技术选型建议
- 不要写"这件事很重要，值得关注"这种套话

**好例子**（1 句）：
> 对鲲鹏后续支持 SVE2.1 / SME2 的代次：这是你自动获得的优化，确保 `-mcpu` 字符串带 SVE2.1/SME2 feature bit。

**好例子**（2 句）：
> Linux 端 6× 提速虽然不及 Windows 18× 戏剧化，但绝对数据 ms 级也意味着集群编译任务的 wall clock 显著下降。鲲鹏服务器跑 distcc 类分布式编译场景值得回归测试。

**坏例子**（套话）：
> 这件事很重要，值得关注。

---

## 文件命名与路径规范

- **路径（领域-窗口 + 板块两级子目录）**：`magazine-collect-output/<domain_slug>-<start>_<end>/<board-slug>/<board-slug>-<start>_<end>.md`
  - **每次跑独立一个"领域-窗口"根目录**——下个月再跑同一领域时，新窗口自动落到新目录里，历史月份的产物不会被覆盖，便于跨期对比
  - 领域-窗口根下再按板块各建一个子目录，同一板块在该窗口内的多次重跑（v2 / v3）自然聚在同一处
- **`<规则文件所在目录>/magazine-collect-output/...`**：默认根位置是 *规则文件同级目录* 下新建 `magazine-collect-output/`。把规则文件放在仓库根（如 `magazine-skills/<domain>-magazine-collect.md`）→ 产物落在 `magazine-skills/magazine-collect-output/`。**不要**把规则文件放进 skill 自带的 `examples/` 下再跑，否则产物会落进 skill 内部。
- **`domain_slug`**：从规则文件名 stem 去掉 `-magazine-collect` 后缀推导。例：`compiler-magazine-collect.md` → `compiler`；`recsys-magazine-collect.md` → `recsys`；`db-magazine-collect.md` → `db`。用户调用时可显式指定覆盖。
- **`board-slug`**：板块名的 kebab-case。例如编译器领域 `llvm` / `gcc` / `rust` / `heterogeneous` / `ai-compiler`，搜推广领域 `recall` / `rank` / `rerank` / `ads`，数据库领域 `sql-engine` / `storage` / `txn`——按当前规则文件该板块的名字音译/英译/缩写即可。
- **完整示例**：
  - `magazine-collect-output/compiler-2026-02-23_2026-05-23/llvm/llvm-2026-02-23_2026-05-23.md`
  - `magazine-collect-output/compiler-2026-02-23_2026-05-23/go/go-2026-02-23_2026-05-23.md`
  - `magazine-collect-output/compiler-2026-02-23_2026-05-23/heterogeneous/heterogeneous-2026-02-23_2026-05-23.md`
  - `magazine-collect-output/recsys-2026-02-23_2026-05-23/rank/rank-2026-02-23_2026-05-23.md`
- **同名冲突**：文件已存在时不要覆盖，加后缀 `-v2` / `-v3`：`magazine-collect-output/compiler-2026-02-23_2026-05-23/llvm/llvm-2026-02-23_2026-05-23-v2.md`
- **目录不存在**：如果 `magazine-collect-output/<domain_slug>-<start>_<end>/<board-slug>/` 任一层级还没建好，写入前先创建
- **月刊例外**：`mode=magazine` 产出的月刊 md 落在 `magazine-collect-output/<domain_slug>-<start>_<end>/magazine-<start>_<end>.md`——领域-窗口根下，不进任何板块子目录（它是跨板块汇总产物）

---

## 反例（不要这样写）

### 反例 1：加 emoji 优先级与"优先级"行

不要：

```markdown
### 🔥 2026-02-24 ｜ LLVM/Clang 22.1.0 正式发布
- **优先级**：🔥 高 — 含 Arm C1 全系 + Ampere1C，命中"鲲鹏相关 / AArch64"关注点
- **URL**：...
```

要：

```markdown
### 2026-02-24 ｜ LLVM/Clang 22.1.0 正式发布
- **URL**：...
- **背景**：LLVM 22 系列从 2025-12 完成 feature freeze 并从主干分支，22.1.0 是 2026 首个稳定 feature 版本。
- **要点**：
  - 新增 Arm C1 Nano / Pro / Premium / Ultra 全系 CPU 支持
  - Armv9.7-A (2025) ISA 汇编/反汇编支持
  - ...
- **启发**：对鲲鹏路线工程师：Arm C1 全系上游意味着主线工具链已经具备 Arm 服务器新代次的目标支持；如果你团队还在维护私有 `-mcpu`，可以开始 PoC 切换。
```

### 反例 2：背景写成 3 句以上铺垫

不要把 4 句话的产业背景全塞进去，挑出最关键的那 1 句即可。读者真要补背景可以点 URL。

### 反例 3：启发写"值得关注"套话

不要：
> 这件事很重要，值得关注。

要：
> 把这个 pass 纳入你的基线对照——确认它在你的 workload 上是 net positive；如果你团队维护私有调度模型，参考 C1-Nano 模型的 patch 形态做对照。

### 反例 4：保留四、五、六、七节

不要补回"按主题归档 / 补充事件附录 / 对工程师的 takeaways / 原文链接合集"——精简版模板只有 〇/一/二 三节，少不要、多也不要。

### 反例 5：不写源覆盖表

不要把"某个源没看"藏在文末一句话里。要明确（以编译器领域邮件列表为例）：

| 规则文件列的源 | 抓取方式 | 候选条目 | 入选条目 | 备注 |
|---|---|---|---|---|
| lists.llvm.org/pipermail/llvm-commits/ | 月度归档抽查 + 关键词过滤 | 约 1.2 万条 | 0 | 高噪声源降级；如需 commit 级建议用专用脚本批处理 |

### 反例 6：把过往领域的关键词带到新领域

**不要**：跑搜推广板块时，仍把 `鲲鹏 / SVE / Intel / AMD` 当作筛选关键词——那是编译器领域的关注点，与搜推广完全无关。

**要**：每次跑新板块都重新从规则文件该板块的"特别关注点"字段提取关键词清单。规则文件就是 single source of truth。

### 反例 7：单事件要点写成完整 release notes 摘录（超过 10 行）

**不要**（用 5 个子分类堆 18+ 行）：

```markdown
- **要点**：
  - **运行时性能**：
    - Green Tea GC 默认启用，GC 开销 -10~40%
    - cgo 调用基线开销 -30%
    - 堆基地址随机化（cgo 安全加固）
    - 实验性 goroutine 泄漏检测
  - **编译器**：
    - 切片栈分配扩展到 append 站点
    - B.Loop() 不再阻止内联
    - 链接器可执行文件结构变更
  - **泛型/语言**：
    - 递归类型约束首次合法
    - new 支持初始化表达式
  - **新实验包**：
    - simd/archsimd（amd64 SIMD）
    - runtime/secret（密钥临时数据擦除）
  - **硬件目标**：
    - 龙芯 LoongArch ELF psABI v2.40
    - windows/arm64 内部链接
    - RISC-V race detector
    - S390X 寄存器传参
    - PowerPC ppc64 ELFv1 收尾
    - windows/arm 32-bit 移除
  - **bootstrap 要求**：1.26 需要 1.24.6+
```

**要**（合并同类项，≤10 行；细节留给"启发"段或 URL）：

```markdown
- **要点**：
  - **运行时**：Green Tea GC 默认启用（GC 开销 -10~40%，现代 CPU +10%）；cgo 调用 -30%；新增堆基地址随机化与实验性 goroutine 泄漏检测
  - **编译器**：切片栈分配扩展到 `append` 站点（详见 02-27 博客）；`B.Loop()` 不再阻止内联；链接器可执行文件结构变更（`.go.module` 独立 section、移除 `.gosymtab`）——外部解析工具需适配
  - **泛型/语言**：递归类型约束首次合法（`type Adder[A Adder[A]]`）；`new` 支持初始化表达式
  - **新实验包**：`simd/archsimd`（amd64 128/256/512-bit 向量，ARM64 路径暂缺）；`runtime/secret`（密钥临时数据擦除，已覆盖 linux/arm64）
  - **硬件目标变更（友商对照面）**：龙芯 ELF psABI v2.40 全套重定位常数；windows/arm64 cgo 内部链接；linux/riscv64 race detector；ppc64 ELFv1 收尾（1.27 切 ELFv2）
  - **bootstrap**：1.26 需 1.24.6+；1.28 计划要求 1.26.x+
```

判断标准：bullet 行数（含嵌套）≤10 即可；上面"要"的写法是 6 行，每行合并 2~3 个相关子点。
