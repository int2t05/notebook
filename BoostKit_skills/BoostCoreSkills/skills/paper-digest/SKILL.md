---
name: paper-digest
description: 按"方向 + 时间窗"自动产出论文检索归档：纯 LLM-driven 流水线——Phase 0/0.5 由 LLM 抽核心关键词 + 同义扩展（30-60 短语）+ 推 arxiv_categories；Phase 1A 由 LLM 提议候选会议、DBLP 验证、metadata 补 CCF/CORE/h5；Phase 1B 由 LLM 同时推 arXiv 与 lab/researcher/blog/RFC 外部源；Phase 2/3 LLM 分类与 4 段量化摘要。输出 S/A/B 分档 + 4 段摘要 + 反虚构守门 + 双年/Best Paper 标注的中文 Markdown 归档。无需任何 YAML profile 或方向特定配置——任何方向（内存 / 安全 / 数据库 / ML / ...）直接传 `--direction "..."` 即用。LLM 后端默认走本地 agent CLI（Claude Code / Gemini / Codex 任意，订阅 OAuth、无需 key）；可选切到 DeepSeek 等 OpenAI 协议 endpoint。当用户说"扫一下最近 N 个月的 X 方向论文" / "出一份 X 论文综述" / "X 方向这一年有什么新工作" 等需求时触发。
---

# paper-digest

## 定位

**任意方向 → 论文归档**的通用 skill。给一个研究方向（自由文本）+ 时间窗，输出 S/A/B 三档会议总览 + 每会议的强相关 4 段量化摘要 + 外部源补充。

**完全无 profile / 无方向硬编码**——所有方向相关的决定（关键词扩展、arxiv 分类、会议提议、方向匹配 emoji、外部源选取）都在运行时由 LLM 给出。`references/conferences-metadata.yaml` 是 direction-agnostic 的会议事实库（CCF/CORE/h5/dates/Best Paper），唯一保留的人工维护资产。

## 触发条件

- "扫一下最近 N 个月/年的 {方向} 论文" / "近一年 {方向} 有什么新工作"
- "出一份 {方向} 综述 / 简报" / "给我 {方向} 的归档目录"
- 涉及多个顶会的批量论文巡检 + 4 段量化摘要 + S/A/B 分档输出
- 用户提到「论文检索归档」「会议综合表」「方向匹配度评估」「composite_score 排序」

**不触发**：

- 用户只问某一篇具体论文的细节（用 `code-review` / `pdf` skill）
- 用户要做编译器/项目周报（用 `compiler-weekly-digest` skill）

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `--direction` | ✅ | `"memory allocator and CXL"` / `"内存优化 编译器"` / `"database transaction"` | 自然语言；任意方向 |
| `--window` | ✅ | `"last 6 months"` / `"近 1 年"` / `"2025-11-01..2026-05-22"` / `"Q1 2026"` | 英/中文相对时间或绝对区间 |
| `--backend` |  | `cli` (默认) / `api` / `auto` | LLM 后端：`cli` = 本地 agent CLI；`api` = OpenAI 协议端点；`auto` = CLI 优先 |
| `--quality` |  | `standard` (默认) / `fast` / `deep` | 控制 top-N / token 预算 / 是否对 yellow 抽 4 段 |
| `--no-expand-keywords` |  |  | 关闭 Phase 0.5 LLM 关键词扩展（默认开启）|
| `--output-dir` |  | `./my-archive` | 默认 `paper-digest-output/`（当前 CWD 下）|
| `--dry-run` |  |  | 只跑 Phase 0 + 0.5 + Phase 1A.1 LLM 候选预测；不写归档 |
| `--resume` |  |  | 读 `manifest.json` 跳过已完成 phase；slug 漂移容忍 |
| `--list-backends` |  |  | 打印当前环境可用的 LLM 后端（cli + api）|

## 流水线（5 个主 phase + 2 个副 phase，全部 LLM-driven 或可推导）

```
Phase 0   ─ 输入解析（LLM flash）           direction → 6-10 keywords + exclude + slug + window
            ↓
Phase 0.5 ─ 关键词扩展（LLM strong, 默认开）  → 30-60 keywords + arxiv_categories + exclude
            ↳ 缓存到 intermediate/phase0.5-focus-areas.{md,json}
            ↓
Phase 1A  ── (LLM strong) 提议 Top-N (name, year, direction_score, rationale)
‖           → 每个候选过 DBLP 验证（404 / 空 → 丢，幻觉被 ground truth 挡住）
‖           → conferences-metadata.yaml 补 CCF/CORE/h5/dates/Best Paper
‖           → direction_match emoji 从 direction_score 推导（🟢🟢🟢=9+, 🟢🟢=7+, ...）
Phase 1B  ── 1B.1 arXiv（Phase 0.5 关键词 + 分块查询）
            1B.5 LLM strong 推 lab/researcher/blog/RFC（带 URL，不确定的标 [manual verify]）
            ↓
Phase 2   ─ 粗分类（LLM flash, 25 篇/批 → 🟢/🟡/🔴 + category）
            ↓
Phase 2.5 ─ abstract 抓取（USENIX → S2 by DOI → S2 by title → missing；无 LLM）
            ↓
Phase 3   ─ 详细抽取（LLM strong：4 段量化摘要 + 3-tag，含反虚构 guard）
            ↓
Phase 4   ─ 渲染（Jinja2 模板 → overview + per-conf + external，无 LLM）
```

中间产物全部落 `output/<archive>/intermediate/phase*.json`；`--resume` 跳过已完成阶段。Phase 0.5 / 2.5 / 4 是幂等的，`--resume` 总会重跑（方便只换模板）。

## 关键命令

```bash
cd skills/paper-digest
# 推荐路径：装了 Claude Code / Gemini CLI / Codex CLI 任一即可，**无需任何 key**
python3 -m scripts.run \
  --direction "memory allocator and CXL" \
  --window "近 1 年"

# 想用 DeepSeek / 自建 endpoint（按量计费）：
export PAPER_DIGEST_LLM_API_KEY=sk-...
python3 -m scripts.run --backend api --direction "..." --window "..."

# 预览（Phase 0 + 0.5 + 1A.1 LLM 候选，不烧大量 token）
python3 -m scripts.run --direction "..." --window "..." --dry-run

# 续跑（manifest 已完成的 phase 都跳过）
python3 -m scripts.run --direction "..." --window "..." --resume

# 关掉 Phase 0.5（节省 1 次 strong-model 调用；用 Phase 0 的原始 6-10 keywords）
python3 -m scripts.run --direction "..." --window "..." --no-expand-keywords

# 切换 LLM 后端 CLI（编辑 config.yaml.llm.cli_backend.binary 即可，gemini / codex 同理）
python3 -m scripts.run --list-backends
```

**默认输出**：`paper-digest-output/<slug>_<start>_<end>/`，例 `paper-digest-output/memory-allocator-cxl-memory-management-m_2025-05-23_2026-05-23/`。

## 输出结构

```
paper-digest-output/<archive>/
├── overview.md                 # S/A/B 分档总览 + 优先阅读 top-5 + 外部源摘要
├── conferences/
│   ├── OSDI-2025.md           # 会议简介 + 🟢 4 段量化 + 🟡 一句 + 🔴 速览
│   └── ...
├── external-sources.md         # 🌐 arXiv + 🏛️ lab + 👤 researcher + 📝 blog + 📡 rfc
├── manifest.json               # input / parsed / phases_completed / tokens / archive_dir
├── intermediate/
│   ├── phase0.5-focus-areas.{md,json}  # LLM 扩展的关键词层级
│   ├── phase1a-conferences.json
│   ├── phase1b-external.json
│   ├── phase2-classified.json
│   ├── phase2.5-abstracts.json
│   └── phase3-detailed.json
└── errors.json                 # 若 BudgetExceeded 或 extract 失败
```

## 配置入口

| 文件 | 用途 |
|------|------|
| `config.yaml` | LLM 后端（CLI/API 双轨）+ tier 预算 + 3-tag emoji + 目录命名 |
| `references/conferences-metadata.yaml` | 会议静态元数据（direction-agnostic SSOT）：tier/CCF/CORE/h5/dates/Best Paper |
| `prompts/*.txt` | 5 个 LLM prompt：input-parse / focus-areas-gen / conference-rank / external-curate / coarse-classify / detail-extract |

**没有** `profiles/` 目录、**没有** `external-sources.yaml`，全部直接由 LLM 推导。

## 反虚构保障（Phase 3 关键约束）

- `abstract_source == "missing"` 时：prompt 强制 4 段以 `[信息不足]` 开头；effect 段绝不允许带单位的数字
- extractor 端二次校验：检测 missing 论文输出含 `\d+%/x/×/ms/MB/...` 等带单位数字 → 整段重写为 `[信息不足]`
- effect 必须含真实量化、`[未量化]` 或 `[信息不足]` 之一；2 次重试仍未量化 → 强加 `[未量化]` 前缀
- Phase 1A 的 LLM 候选必须过 DBLP fetch 验证；幻觉 venue/year 直接 drop

## 测试

```bash
cd skills/paper-digest
pip install -e ".[dev]"
pytest                                     # 自动定位 ../../tests/paper-digest
pytest ../../tests/paper-digest/unit -v
pytest ../../tests/paper-digest/integration -v
```

## 设计文档

- [`docs/workflow.md`](./docs/workflow.md) — phase-by-phase 时序图、I/O 形状、错误处理
- [`docs/examples.md`](./docs/examples.md) — 首次跑 / dry-run / 续跑 / 换方向的实际命令样例
- [`docs/process-retrospective.md`](./docs/process-retrospective.md) — 2026-05-22 的手动数据生产过程复盘
