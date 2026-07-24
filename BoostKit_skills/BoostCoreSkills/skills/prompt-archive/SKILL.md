---
name: prompt-archive
description: 提取并归档本机 Claude Code 所有历史会话中"用户真人发出的 prompt"，生成每会话 md + 主索引 + 质量分析报告，支持增量更新。当用户说"归档我的 session prompt""提取历史 prompt""统计我问过的问题""prompt 质量分析""/prompt-archive"时触发。
---

# Prompt 归档与分析 (prompt-archive)

把本机 Claude Code 历史会话里**用户真人发出的 prompt** 提取出来，归档为可读 Markdown 并做质量分析。

## 数据来源与产物

- **输入**：`~/.claude/projects/*/*.jsonl`（仅顶层会话转录；`*/subagents/*` 是子 agent 流量，自动排除）。
- **输出根**：默认 `~/workspace/prompt-archive/`，可用 `--out` 覆盖。
  - `dataset/prompts.jsonl` + `dataset/sessions/<key>.{jsonl,meta.json}` — 机器数据集（每条 prompt 一行，含特征与有效性代理）
  - `sessions/<date>_<项目>_<标题>_<sid8>.md` — 每会话一个，frontmatter + 逐条 prompt（用 `## p<seq>` 真标题，带时间戳/工具数/编辑数/回复 token/中断标记）
  - `INDEX.md` — 主索引：处理截止时间、数据范围、项目概览、按日期倒序分组表、分析报告链接
  - `analysis/<date>-prompt-quality-heuristic.md` — 启发式量化报告（含 Top/Bottom 30 排行，「位置」列可跳转到会话 md 章节）
  - `analysis/<date>-prompt-quality-report.md` — LLM 最佳实践报告（由 Workflow 生成）
  - `.archive-state.json` — 增量 checkpoint（记录处理截止时间，重跑可从此继续）

## 子命令

脚本在 `scripts/`，仅依赖标准库（LLM 深析除外，见下）。以下命令均假设先 `cd skills/prompt-archive`（或软链安装后 `cd ~/.claude/skills/prompt-archive`）。

### extract + render — 增量抽取并渲染
```
cd skills/prompt-archive
python3 scripts/extract.py --out ~/workspace/prompt-archive
python3 scripts/render.py  --out ~/workspace/prompt-archive
```
`extract` 按 mtime+行数做增量：未变会话跳过、变长的重渲染、新会话新增，并打印「新增/更新/跳过」。`render` 由数据集生成每会话 md 与 INDEX。

### analyze — 质量分析（启发式 + 可选 LLM）
1. 启发式打分与选样（标准库）：
   ```
   python3 scripts/analyze.py --out ~/workspace/prompt-archive --date <YYYY-MM-DD>
   ```
   回写 `quality_score`，产出量化报告（Top/Bottom 30 默认）与 `analysis/_sample.json`（Top-K + Bottom-K + 分层代表）。
2. LLM 深析（可选，由主 agent 用 **Workflow** 编排，脚本不发 LLM 请求）：
   - 把选样压成紧凑 args，跑工作流：Load → 并行多维评判（清晰度/具体性/上下文/可执行性 1-5 + 为何高效/低效 + 改写建议）→ 综合中文最佳实践报告。
   - 把返回的报告写入 `analysis/<date>-prompt-quality-report.md`。

### 全流程顺序
**extract → analyze →（可选 LLM 深析）→ render**（render 放最后，INDEX 才能链接到 analysis 报告）：
```
cd skills/prompt-archive
OUT=~/workspace/prompt-archive
python3 scripts/extract.py --out $OUT
python3 scripts/analyze.py --out $OUT --date $(date +%F)
python3 scripts/render.py  --out $OUT
```

## 真人 prompt 判定（核心契约）

保留：`type==user` 且 `message.role==user`、非 `isMeta`/`isSidechain`、`content` 不含 `tool_result`、清洗包裹块后仍有正文。剔除：纯斜杠命令（`/clear` 等）、`[Request interrupted by user]`、`<task-notification>…`、各类 `<command-*>/<bash-*>/<system-reminder>` 包裹块、空串。`[Request interrupted…]` 会把上一条 prompt 标记为 `interrupted`。

注意：带正文的斜杠命令（典型 `/goal`，正文存放在 `<command-args>` 内）会在清洗前被**抢救**重建为 `"<命令> <正文>"`，避免高价值任务规格被静默丢弃。

## 参数

- `--out <dir>`：输出根目录（默认 `~/workspace/prompt-archive`）
- `--projects-root <dir>`：会话根（默认 `~/.claude/projects`）
- `--force`（extract）：忽略 checkpoint 全量重抽
- `--date <YYYY-MM-DD>`（analyze）：报告日期标签（默认取 state 的 last_run）
- `--top / --bottom <N>`（analyze）：排行与选样规模（默认各 30）

## 安装

软链到 `~/.claude/skills/`：

```bash
ln -s "$(pwd)/skills/prompt-archive" ~/.claude/skills/prompt-archive
```
