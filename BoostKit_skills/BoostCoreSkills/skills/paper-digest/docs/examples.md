# 完整运行示例

## 场景 1：首次跑（无 key、走 Claude Code 订阅）

```bash
$ cd ~/workspace/skills/skills/paper-digest
# 装 Claude Code 即可，无需任何 API key
$ python3 -m scripts.run \
    --direction "内存库/内存优化/编译器优化" \
    --window "近 1 年"

2026-05-23 22:10:00 [INFO] LLM backend: CLISubprocessLLM (requested=auto)
2026-05-23 22:10:01 [INFO] Phase 0: parsing input
2026-05-23 22:10:15 [INFO] Parsed: keywords=['memory allocator', 'memory management', ...]
2026-05-23 22:10:15 [INFO] Phase 0.5: LLM keyword expansion
2026-05-23 22:10:45 [INFO] Phase 0.5 → 47 expanded keywords, arxiv_categories=['cs.OS', 'cs.PL', 'cs.AR', 'cs.DC']
2026-05-23 22:10:45 [INFO] Archive: paper-digest-output/memory-allocator-memory-management-huge_2025-05-23_2026-05-23
2026-05-23 22:10:45 [INFO] Phase 1A+1B in parallel
2026-05-23 22:13:30 [INFO] Phase 1A.1: LLM proposed 25 unique (name, year) candidates
2026-05-23 22:14:10 [INFO] Phase 1A.2: 21 verified, 4 rejected by DBLP
2026-05-23 22:14:10 [INFO] arXiv search: 47 keywords → 8 chunks
2026-05-23 22:15:00 [INFO] arXiv returned 250 unique papers
2026-05-23 22:15:30 [INFO] Phase 1B.5 curated: labs=4 researchers=3 blogs=2 rfcs=1
2026-05-23 22:15:30 [INFO] Merged 2150 papers (conf + external) for Phase 2
2026-05-23 22:21:18 [INFO] Phase 2.5: fetching abstracts
2026-05-23 22:24:55 [INFO] Phase 3: deep extraction (green + yellow)
2026-05-23 22:51:22 [INFO] Phase 4: rendering
2026-05-23 22:51:23 [INFO] Done. Archive: .../memory-allocator-memory-management-huge_2025-05-23_2026-05-23
```

**默认输出**：`paper-digest-output/<slug>_<start>_<end>/`
- `overview.md`：S/A/B 分档总览
- `conferences/{NAME}-{YEAR}.md`：每个抓到论文的会议·年一份
- `external-sources.md`：arXiv + LLM-curated lab/researcher/blog/rfc
- `manifest.json` + `intermediate/`：中间产物，可断点续跑

---

## 场景 2：预览（不烧大量 token）

```bash
$ python3 -m scripts.run \
    --direction "memory allocator and CXL" \
    --window "近 6 个月" \
    --dry-run

======================================================================
DRY RUN — Phase 0/0.5 done + Phase 1A.1 LLM proposal only.
           No DBLP fetch, no Phase 1B.5 curate, no archive written.
======================================================================
Direction         : memory allocator and CXL
Window            : 2025-11-23 .. 2026-05-23
Phase-0 keywords  : ['memory allocator', 'CXL', 'memory management', ...]
Phase-0.5 expanded: 38 keywords
arXiv categories  : ['cs.OS', 'cs.AR', 'cs.DC', 'cs.PF']
Slug              : memory-allocator-cxl-memory-management

Phase 1A.1 LLM-proposed Top-25 candidates (direction_score / composite / emoji / month / rationale):
   ds=9.5  comp=8.96  🟢🟢🟢  ISMM           2026  M 6  ACM SIGPLAN memory venue
   ds=8.0  comp=7.40   🟢🟢   ASPLOS         2026  M 3  ...
   ...
```

`--dry-run` 跑 Phase 0 + 0.5（两次 LLM 调用）+ Phase 1A.1（一次 LLM 调用），用于检查会扫哪些会议、关键词被展开成什么样、arxiv_categories 是不是合理。

---

## 场景 3：换方向（**零额外编辑，开箱即用**）

```bash
# 跑数据库方向
$ python3 -m scripts.run \
    --direction "database transaction concurrency" \
    --window "近 1 年"
# LLM 自动给出 SIGMOD/VLDB/ICDE 会议候选 + cs.DB 类目 + DB 方向的 lab/researcher

# 跑安全方向
$ python3 -m scripts.run \
    --direction "memory safety fuzzing" \
    --window "近 1 年"
# LLM 自动给出 USENIX-Security/CCS/NDSS 候选 + cs.CR 类目 + 安全方向的 lab/researcher
```

**与旧设计区别**：以前需要先在 `references/profiles/<name>.yaml` 写一个新方向 profile（`direction_match` + `synonym_map` + `arxiv_categories` 都得手填），现在**直接传 `--direction "..."` 即可**。会议元数据 `references/conferences-metadata.yaml` 保留作为 enrichment 层（提供 CCF/CORE/h5/Best Paper），不强制为新方向补条目。

---

## 场景 4：续跑（中途崩了 / 想换 Phase 4 模板）

```bash
# 第一次跑到 Phase 3 中间被 BudgetExceeded 中断
$ python3 -m scripts.run --direction "..." --window "..."
... [ERROR] Budget exceeded: ...
... [INFO] Phase 4: rendering
... [INFO] Done. Tokens used: 200312 / 200000

# 把 max_budget_tokens 调高后续跑
$ vim config.yaml  # standard.max_budget_tokens: 200000 → 400000
$ python3 -m scripts.run --direction "..." --window "..." --resume
... [INFO] Resuming archive: ... (phases done: ['phase0', 'phase0.5', 'phase1', 'phase2'])
... [INFO] Phase 2.5: fetching abstracts ...
... [INFO] Phase 3: deep extraction (green + yellow)
... [INFO] Phase 4: rendering
```

`--resume` 自动跳过已完成 phase；Phase 0.5 / 2.5 / 4 是幂等的，总会重跑。Phase 0 在 resume 时也跳过（从 manifest 读 parsed），避免 LLM 漂移导致 slug 变化。

---

## 场景 5：自定义输出位置 / 每次都留快照

```bash
# 输出到指定路径
$ python3 -m scripts.run --direction "..." --window "..." \
    --output-dir ./my-archive

# 想多次跑同一窗口都保留快照（默认会覆盖）
$ vim config.yaml  # output.include_date_label: true
$ python3 -m scripts.run --direction "..." --window "..."
# 目录变成 paper-digest-output/<slug>_<start>_<end>_run-<YYYY-MM-DD>/
```

---

## 场景 6：切到其它 LLM 后端

```bash
# 当前装了 Gemini CLI 想切过去
$ vim config.yaml
# 改 llm.cli_backend 段为:
#   binary: gemini
#   model_arg: "-m"
#   extra_args: []
#   model_flash: "gemini-2.5-flash"
#   model_strong: "gemini-2.5-pro"

# 验证
$ python3 -m scripts.run --list-backends
CLI backend (binary='gemini'): AVAILABLE at /usr/local/bin/gemini
API backend (env='PAPER_DIGEST_LLM_API_KEY'): NOT CONFIGURED (key unset)

# 跑
$ python3 -m scripts.run --direction "..." --window "..."

# 或临时走 API
$ export PAPER_DIGEST_LLM_API_KEY=sk-...
$ python3 -m scripts.run --backend api --direction "..." --window "..."
```

---

## 调试 tip

- 看每 phase 的中间结果 → `paper-digest-output/<archive>/intermediate/phase*.json`
- 想强制重跑某 phase → 编辑 `manifest.json`，把对应 `phases_completed` 条目删掉再 `--resume`
- Phase 0.5 LLM 扩展的关键词 → `intermediate/phase0.5-focus-areas.md`（人类可读）
- abstract 抓取来源统计 → `intermediate/phase2.5-abstracts.json` 的 `stats` 字段
- Phase 1A LLM 候选被 DBLP rejected 的 → `intermediate/phase1a-conferences.json` 里 `fetch_status=rejected` 的条目
