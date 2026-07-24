# paper-digest

`paper-digest` 是一个**论文检索归档**类 Agent Skill：按"方向 + 时间窗"自动收集顶会论文 + arXiv 全文，经过 4 阶段（+ Phase 2.5 abstract 抓取）coarse-to-fine 流水线后产出带 CCF/CORE/h5 元数据、S/A/B 分档、强相关 emoji 标注的中文 Markdown 归档。

设计目标只有一个：**让一线工程师在 30 分钟内对一个新方向的近 N 个月文献获得「该读哪几篇 / 大概在讲什么 / 学术 or 工业 / 是否开源 / 有没有原型」的判断**。

## 主要能力

- **关键词扩展（Phase 0.5）**：LLM strong 把 Phase 0 抽的 6-10 核心关键词扩到 30-60 个 primary/secondary/tertiary 分级关键词，并推荐对应的 arXiv 类目。
- **会议候选（Phase 1A）**：LLM strong 提议 Top-N 候选 `(name, year, direction_score, rationale)`，每个候选过 DBLP `fetch_program` 验证（404/空 → 丢，幻觉成本被 ground truth 挡住）；`conferences-metadata.yaml` 仅作 CCF/CORE/h5/dates/Best Paper 的 enrichment 层。`direction_match` emoji 由 LLM 给的 `direction_score` 在 Python 端推导。
- **外部源（Phase 1B）**：
  - 1B.1 arXiv 用 Phase 0.5 扩展后的关键词分块查询、按 `submittedDate desc` 分页采集
  - 1B.5 LLM strong 同时推 lab/researcher/blog/RFC 条目（带 URL，不确定的标 `[manual verify]`）
- **粗分类（Phase 2）**：exclude 关键词预过滤；剩余按 25 篇/批过 LLM flash model，输出 🟢/🟡/🔴 + reason + category。
- **abstract 抓取（Phase 2.5）**：USENIX 直爬 → Semantic Scholar by DOI → S2 by title → missing；为 Phase 3 反虚构守门。
- **4 段量化摘要（Phase 3）**：🟢/🟡 进 strong model，强制 "背景 / 核心 / 效果（带数字）/ 启发"；effect 必须给量化指标或显式标 `[未量化]` / `[信息不足]`；abstract missing 时反虚构 guard 强制重写。
- **渲染（Phase 4）**：从 metadata 取 CCF/CORE/h5/Best Paper + 候选自带的 direction_match → Jinja2 → overview + per-conf + external。
- **token 预算硬限**：跨 phase 累计 token，超限即停 + 错误归档。
- **可重跑**：`--resume` 读 manifest.json 跳过已完成 phase。Phase 2.5 / Phase 4 幂等。
- **dry-run 预览**：`--dry-run` 只跑 Phase 0，打印将要扫的会议候选 + 关键词同义扩展结果，不烧 token。

## 目录说明（Plan A — pure LLM-driven，零方向硬编码）

```
skills/paper-digest/
├── SKILL.md                # 必填：触发条件 + 命令入口
├── README.md               # 本文件
├── config.yaml             # LLM 后端（CLI/API）+ tier 预算 + 3-tag emoji + 目录命名
├── pyproject.toml          # 依赖
├── prompts/                # 6 个 LLM prompt（每个对应一个 LLM 调用阶段）
│   ├── input-parse.txt        # Phase 0: direction → keywords
│   ├── focus-areas-gen.txt    # Phase 0.5: 关键词扩展到 30-60
│   ├── conference-rank.txt    # Phase 1A.1: LLM 提议候选会议
│   ├── external-curate.txt    # Phase 1B.5: LLM 推 lab/researcher/blog/RFC
│   ├── coarse-classify.txt    # Phase 2: 25 篇/批分类
│   └── detail-extract.txt     # Phase 3: 4 段量化摘要
├── scripts/
│   ├── input_parser.py         # Phase 0
│   ├── focus_areas.py          # Phase 0.5（默认开启）
│   ├── conference_discoverer.py  # Phase 1A（LLM 提议 → DBLP 验证 → metadata 补）
│   ├── external_discoverer.py  # Phase 1B.1 arXiv + 1B.5 LLM curate
│   ├── classifier.py           # Phase 2
│   ├── abstract_fetcher.py     # Phase 2.5（无 LLM）
│   ├── extractor.py            # Phase 3
│   ├── renderer.py             # Phase 4（无 LLM）
│   ├── run.py                  # 主 entry point
│   └── utils.py                # LLMClient / CLISubprocessLLM / Archive / DBLP
├── templates/              # 3 个 Jinja2 输出模板
│   ├── overview.md.j2
│   ├── conference.md.j2
│   └── external.md.j2
├── references/             # 唯一保留的人工数据资产
│   └── conferences-metadata.yaml   # 会议事实库：tier/CCF/CORE/h5/dates/Best Paper
│                                   # direction-agnostic SSOT
└── docs/                   # workflow / examples / process-retrospective
```

**注意删除**（已迁移到 LLM-driven 路径）：
- 无 `references/profiles/`（方向相关一切在运行时由 LLM 决定）
- 无 `references/external-sources.yaml`（被 Phase 1B.5 LLM curate 取代）
- 无 `scripts/profile_loader.py`

## 安装

**作为 Agent Skill**：见仓库根 `README.md` 的"安装 Skills"节，使用 `npx skills add boostkit/skills --skill paper-digest` 注册到 Agent 工具（Claude Code / OpenCode / CodeBuddy / TRAE 等）。

**本地开发 / 直接命令行使用**：见下面"快速开始"。

## 快速开始

### 1. 安装运行依赖

```bash
cd skills/paper-digest
pip install -e ".[dev]"
```

### 2. 选择 LLM 后端（**API key 是可选的**）

**默认路径（推荐 · 无需 key）**：装了 Claude Code / Gemini CLI / Codex CLI 任一即可，本 skill 默认走 `--backend cli`，子进程调用 `claude -p ...`（订阅 OAuth）。要切换到 gemini / codex，编辑 `config.yaml` 的 `llm.cli_backend.binary` + `model_flash/strong` 即可，不动代码。

**API 路径（可选 · 按量计费 / 多并发）**：

```bash
cp .env.example .env  # 编辑取消注释，填 PAPER_DIGEST_LLM_API_KEY=sk-...
# 或直接 export PAPER_DIGEST_LLM_API_KEY=sk-...
python3 -m scripts.run --backend api ...
```

查看当前环境哪些后端可用：

```bash
python3 -m scripts.run --list-backends
```

### 3. 跑一个方向

```bash
python3 -m scripts.run \
  --direction "memory allocator and CXL" \
  --window "近 1 年"
```

默认产出到 `paper-digest-output/<slug>_<start>_<end>/`（当前工作目录下；目录名含起止日期一目了然）。

如需自定义：加 `--output-dir ./my-path` 覆盖。约 5~30 分钟（视方向广度和会议数）。

### 4. 看产出

入口是 `paper-digest-output/.../overview.md`：

- 顶部：时间窗 + 关键词 + 论文总数
- 中部：S 档 / A 档 / B 档三表，含 CCF/CORE/h5、日期&地点、🟢 数、方向匹配 emoji、composite_score
- 底部：外部源摘要 + 错误归档

每个 S/A 档会议有独立 md 链接到 `conferences/{NAME}-{YEAR}.md`：

- 🟢 强相关：4 段量化摘要 + 3-tag（工业/开源/可落地性）+ 🏆 Best Paper 标记（若元数据有）
- 🟡 中相关：一句话内容描述 + 3-tag
- 🔴 其他：标题 + PDF + 排除原因子分类

## 三档分类的判定标准

### 相关性（Phase 2 LLM 给）

| Emoji | 含义 | 判定 |
|-------|------|------|
| 🟢 强相关 | 论文核心命题就是当前 direction 关心的问题 | 标题/摘要里有 ≥2 个目标 keyword + LLM 判定 |
| 🟡 中相关 | 部分组件涉及，或思路可迁移到当前方向 | LLM 判定为「side-related」|
| 🔴 弱相关 | 与方向几乎无关，或仅 keyword 表面 match | exclude pre-filter 命中 / LLM 判定 off-topic |

### 工业合作

🏭 工业主导（一作即工业实验室）/ 🤝 学+工合作 / 🏛️ 纯学术

### 开源

📦 已开源（artifact + 代码可用）/ 📋 部分开源（仅 artifact）/ 🔒 未开源

### 可落地性

🚀 高（产品级 / 已上生产）/ 🔬 中（PoC / 原型）/ 📐 低（理论 / 形式化）

## 加新方向（零 YAML 编辑）

Plan A 之后，**没有 profile YAML 需要写**。直接传 `--direction` 即可：

```bash
python3 -m scripts.run \
  --direction "database transaction concurrency control" \
  --window "近 1 年"
```

发生的事：
- Phase 0 LLM 从你的 direction 抽 6-10 个核心关键词
- Phase 0.5 LLM 扩到 30-60 个 + 推 `arxiv_categories: ["cs.DB", "cs.DC", ...]`
- Phase 1A LLM 提议 SIGMOD / VLDB / ICDE / CIDR 等候选；DBLP 验证后保留真实的
- Phase 1B.5 LLM 推数据库方向的顶级实验室 / 研究者 / blog

如果新方向涉及未登记的会议，可选地给 `references/conferences-metadata.yaml` 补条目（tier/CCF/CORE/h5/full_name/years），下游 Phase 4 渲染会自动用这些 enrichment 信息。**不补也能跑**——会议会以 `未/—/—` 的 CCF/CORE/h5 显示。

## 静态会议元数据

`references/conferences-metadata.yaml` 维护一份顶级/强相关会议的小表，含：

```yaml
OSDI:
  tier: S                       # S / A / B
  ccf: A                        # CCF 推荐目录档
  core: "A*"                    # CORE 2023
  h5: 68                        # Google Scholar h5-index
  full_name: "USENIX Symposium on Operating Systems Design and Implementation"
  years:
    2025:
      dates: "2025-07-07~09"
      venue: "Boston, MA"
      acceptance_rate: "14.6%"
      best_papers:
        - "Tiered Memory Management Beyond Hotness"
      outstanding_papers: []
```

注意：**`direction_match` 不在元数据里**——它由 Phase 1A 的 LLM 输出 `direction_score` 决定，在 Python 端通过 `score_to_emoji` 映射为 🟢🟢🟢 / 🟢🟢 / 🟢 / 🟡。同一会议在不同方向跑出来 emoji 不一样，由 LLM 现场判定。

Phase 4 render 时按 conference name + year 查表，把 CCF/CORE/h5 / 日期 / Best Paper 标注合并到输出。元数据缺失时降级为「未/未/—」而不是渲染失败。

## 续跑 / 单 phase 重跑

```bash
# 第一次跑（被 BudgetExceeded 打断也没关系，phase4 还是会渲染已有的）
python3 -m scripts.run --direction "..." --window "..."

# 续跑：跳过已完成 phase
python3 -m scripts.run --direction "..." --window "..." --resume

# 想强制重跑某 phase？编辑 archive/manifest.json，删掉对应 phases_completed 条目再 --resume
```

Phase 2.5（abstract 抓取）和 Phase 4（渲染）都是幂等的，`--resume` 总会重跑。

## 当前限制

- `fast` / `deep` 两档 quality 与 `standard` 走同一流水线，仅 top-N / budget / extract_yellow 不同；端到端只对 `standard` 做过基线验证。
- arXiv 抓取使用 `arxiv.org/api/query`，无 cookie / rate-limit handling（节流靠分块查询 + UA 标识）。
- Best Paper / Outstanding 标注完全依赖手维护的 metadata（未自动从 DBLP/官网抓）。
- Phase 1B.5 LLM-curated 外部源的 URL **不会自动验证**；LLM 在不确定时应标 `[manual verify]`，前端高亮提示用户人工核对。

## 测试

```bash
cd skills/paper-digest
pip install -e ".[dev]"
pytest                                     # 自动定位 ../../tests/paper-digest
# 或显式：
pytest ../../tests/paper-digest/unit -v
pytest ../../tests/paper-digest/integration -v
```

## 与仓库根约束对齐

- 命名：`paper-digest`（kebab-case）✅
- SKILL.md 严格命名 ✅
- 测试在 `tests/paper-digest/`（仓库顶层）✅
- 设计稿不入库 git 历史：`docs/wip/` 在 `.gitignore` 里，纯本地草稿，不会出现在 commit / PR 中，也不被任何代码读取

## Phase 0.5 — LLM 关键词扩展（默认开启）

跑一次会议归档时，Phase 0.5 默认会触发：LLM strong 把 Phase 0 的 6-10 核心关键词扩到 30-60 个 primary/secondary/tertiary 分级关键词、给出建议的 `arxiv_categories`、提供 `exclude` 黑名单。结果落 `intermediate/phase0.5-focus-areas.{md,json}`；`--resume` 会自动复用、不重复消耗 token。

要节省 1 次 strong-model 调用、只用 Phase 0 的原始关键词，传 `--no-expand-keywords`。

## Phase 1A 设计

Phase 1A 是 **LLM-driven 提议 + DBLP 验证 + metadata 增强** 三步合一：

1. **LLM 提议**：给 LLM `(direction, keywords, window, today)`，让它给出 Top-N `(name, year, expected_month, direction_score, rationale)`。LLM 比写死的 metadata.yaml 更全面（能想到新成立的会议、新方向的 venue）。
2. **DBLP 验证**：每个候选都用 `fetch_program(name, year)` 探测 DBLP；404 / 空页面直接丢，幻觉成本被 ground truth 挡住。
3. **metadata 增强**：从 `conferences-metadata.yaml` 取 `(ccf, core, h5, dates, venue, best_papers, full_name)` 补到通过验证的候选上，做 composite_score 排序与 Phase 4 渲染。

`direction_match` emoji 由候选的 `direction_score` 在 Python 端通过 `score_to_emoji` 映射得到（🟢🟢🟢 = 9+, 🟢🟢 = 7+, 🟢 = 5+, 🟡 = 3+，否则空）。不再需要 profile YAML 维护这个字段。

`metadata.yaml` 是 **enrichment 层**，不是 candidate 来源。只有 LLM 不可用（API/CLI 都没装）时才回退到 metadata-only 枚举。

## Phase 1B.5 — LLM-driven 外部源

跟 Phase 1A 思路一致：LLM strong 列出该方向值得跟踪的 lab/researcher/blog/RFC（带 URL，不确定时标 `[manual verify]`），整合进 `external-sources.md` 一节按 source 分组展示。

**不会自动 fetch URL 验证存在性**——LLM 偶尔会给错链接，所以 `[manual verify]` 这条约束很重要。如果用户想加额外手维护源，可以在 `intermediate/phase1b-external.json` 里手动追加条目然后 `--resume`。
