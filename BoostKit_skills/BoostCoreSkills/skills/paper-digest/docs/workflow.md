# 流水线工作流（Plan A — 纯 LLM-driven）

> 一次 `python3 -m scripts.run --direction ... --window ...` 走完整 0 → 0.5 → 1A/1B → 2 → 2.5 → 3 → 4 流程。中间产物全为 JSON，落 `output/<archive>/intermediate/`；`--resume` 读 manifest 跳过已完成阶段。
> **Plan A 之后无 profile YAML**：所有方向相关决策由 LLM 在运行时给出。

---

## Phase 0 — 输入解析

**输入**：CLI 参数 `--direction <NL>` `--window <NL>`

**做什么**：
1. `parse_time_window` 把窗口表达式（`last 6 months` / `近 1 年` / `Q1 2026` / `2025-11-01..2026-05-22`）解析成绝对 `(start, end)`。
2. `prompts/input-parse.txt` 让 flash model 把 direction 转换成 `keywords (6-10) + exclude`（JSON）。
3. 拼出 `slug` 与 `window_label`，用于归档目录名。

**输出**：`manifest.json` 的 `parsed` 字段。

---

## Phase 0.5 — LLM 关键词扩展（默认开启）

**输入**：Phase 0 的 6-10 核心关键词 + direction 原文。

**做什么**：
1. `prompts/focus-areas-gen.txt` 让 strong model 把关键词扩成 **30-60 个 primary/secondary/tertiary 分级关键词** + 推荐 `arxiv_categories: [cs.X, cs.Y, ...]` + 补充 `exclude`。
2. 落 `intermediate/phase0.5-focus-areas.{md,json}`。
3. `--resume` 时自动复用，不重复调 LLM。
4. `--no-expand-keywords` 关闭此 phase，下游 Phase 1B 只用 Phase 0 的原始关键词 + 默认 arxiv 类目。

**输出**：`phase0.5-focus-areas.json`（含 `primary/secondary/tertiary/exclude/arxiv_categories/scoring_dimensions`）+ 人类可读 markdown。

---

## Phase 1A — 会议候选 + DBLP 验证 + metadata 增强

**输入**：Phase 0/0.5 关键词 + direction 原文 + 窗口。

**做什么**：
1. **1A.1 LLM 提议**：`prompts/conference-rank.txt` 让 strong model 给出 Top-N `(name, year, expected_month, direction_score 0-10, rationale)`。无 profile hint，LLM 凭训练数据回忆该方向值得跟踪的会议。
2. **1A.2 DBLP 验证**：每个候选过 `fetch_program(name, year)`。404 / 空页面 → 标 `fetch_status=rejected`、丢弃（LLM 幻觉的 venue/year 被 ground truth 挡住）。
3. **1A.3 metadata fallback**：当验证后剩下 < top_n 候选时，从 `conferences-metadata.yaml` 取窗口内的已知会议补齐。
4. **1A.4 enrichment**：对每个验证通过的候选，从 metadata 取 `(ccf, core, h5, dates, venue, best_papers, full_name)` 注入。
5. **direction_match emoji**：在 Python 端 `score_to_emoji(direction_score)` 映射：≥9 → 🟢🟢🟢，≥7 → 🟢🟢，≥5 → 🟢，≥3 → 🟡。
6. **composite_score**：`direction_score × 0.6 + (ccf+core)/2 × 0.3 + h5_norm × 0.1`，全部 Python 端算。

**输出**：`intermediate/phase1a-conferences.json`

---

## Phase 1B — arXiv + LLM-driven 外部源 curate

**输入**：Phase 0.5 扩展后的关键词 + direction 原文 + Phase 0.5 推的 arxiv_categories。

**做什么**：
1. **1B.1 arXiv**：把 30-60 个扩展关键词每 6 个一组分块（arXiv 在长 OR 串上会静默失败），对每块生成 `(ti: OR ...) AND (cat: ...)` 查询、按 `submittedDate desc` 翻最多 4 页。解析 Atom XML、按窗口过滤、去重。
2. **1B.5 LLM curate**：`prompts/external-curate.txt` 让 strong model 推 8-15 条 lab/researcher/blog/RFC 条目（带 URL）。LLM 不确定 URL 时**必须标 `[manual verify]`**（前端高亮提示人工核对）。
3. 1B.1 与 1B.5 的产物都转成「论文形状」`{id, title, url, date, relevance, ...}` 注入 Phase 2 候选池。

**输出**：`intermediate/phase1b-external.json`

---

## Phase 2 — 粗分类

**输入**：Phase 1A + 1B 合并的全部候选论文。

**做什么**：
1. 用 `exclude_keywords` 做标题预过滤，命中即直接 red + `category=excluded_by_filter`。
2. 剩余按 25 篇/批喂给 flash model（`prompts/coarse-classify.txt`），输出每篇的 `relevance ∈ {green, yellow, red}` + `reason`。
3. 单批 JSON 解析失败 → 整批 mark `relevance=unknown` + 在 reason 写错误。

**输出**：`intermediate/phase2-classified.json`

---

## Phase 2.5 — abstract 抓取（关键反虚构）

**输入**：Phase 2 标记 green/yellow 的论文。

**做什么**（无 LLM）：
1. arXiv 的 abstract 在 Phase 1B 已经填好，pass-through。
2. USENIX 会议页（OSDI/ATC/NSDI/Security/FAST）直接 HTML 抓取。
3. 兜底 Semantic Scholar API：按 DOI → 按 title 搜并校验前 60 字符。
4. 全失败 → `abstract = ""`、`abstract_source = "missing"`。Phase 3 prompt 看到 `missing` 必须走 `[信息不足]` 通道。

**输出**：`intermediate/phase2.5-abstracts.json`

---

## Phase 3 — 4 段量化摘要

**输入**：Phase 2.5 后带 abstract（或显式 missing）的 green/yellow 论文。

**做什么**：
1. 单篇调 strong model（`prompts/detail-extract.txt`），强制 JSON 输出：4 段摘要 + 3-tag + tag_notes。
2. effect 段必须含真实量化数字、`[未量化]` 或 `[信息不足]` 之一；2 次重试仍未量化 → 强加 `[未量化]` 前缀。
3. `abstract_source==missing` 时启用反虚构 guard：任何带单位的数字出现在 4 段任一段中 → 整段重写为 `[信息不足]`。
4. JSON 解析失败 vs API 错误分别记 `tag_notes.error`。

**输出**：`intermediate/phase3-detailed.json`

---

## Phase 4 — 渲染

**输入**：所有中间产物 + manifest。

**做什么**（无 LLM）：
1. 加载 `references/conferences-metadata.yaml` 补 CCF/CORE/h5/dates/Best Paper。
2. 用每个候选自带的 `direction_match` emoji（Phase 1A 已设）。
3. 按 year columns 把候选 + 元数据已知但未抓的会议·年合并，渲染 S/A/B/未分档表。
4. 每个抓到论文的会议·年单独渲染 `conferences/{NAME}-{YEAR}.md`。
5. arXiv + LLM-curated 外部源汇总到 `external-sources.md`。

**输出**：`overview.md` + `conferences/*.md` + `external-sources.md` + `manifest.json` 末次状态。

---

## 续跑 / 单 phase 重跑

- `--resume` 读 `manifest.json` 里的 `phases_completed`；命中即跳过对应 phase，直接读取上一次落盘的 JSON。
- Phase 0.5 / 2.5 / 4 都是幂等（无 LLM 或可缓存），每次 `--resume` 都会重跑；这样可以"只改模板/抽 abstract 一遍"。
- 想强制重跑某 phase：删掉 `manifest.json` 里对应条目，再 `--resume`。

---

## 错误处理

- `BudgetExceeded` 在 Phase 2/3 中间抛出 → 当前 phase 停在已完成论文，错误写 `errors.json`，Phase 4 仍然渲染已有内容。
- 单会议 `fetch_program` 失败 → 该会议 `papers=[]`、`fetch_status=error`/`rejected`，其他会议不受影响。
- 单批 classify JSON 解析失败 → 整批 25 篇 mark `relevance=unknown`，下一批继续。
- Phase 1B.5 LLM 失败 → external curated 列表为空，arXiv 还在；不阻塞流水线。
