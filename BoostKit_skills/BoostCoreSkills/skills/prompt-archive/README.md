# prompt-archive

提取并归档本机 Claude Code 所有历史会话中「用户真人发出的 prompt」，生成每会话 Markdown + 主索引 + 质量分析报告，支持增量更新。

把散落在 `~/.claude/projects/` 里的会话转录，变成「我问过什么 / 哪些问得好」的可检索、可分析归档。

## 主要能力

- **真人 prompt 抽取**：从顶层会话转录中精确识别用户真正发出的 prompt，排除工具结果、系统注入、子 agent 流量等噪声；带正文的斜杠命令（如 `/goal`，正文在 `<command-args>` 内）会被抢救保留。
- **有效性关联**：每条 prompt 关联其后的 assistant 回复，统计工具调用数、文件编辑数、回复 token、是否被中断，作为「这条 prompt 触发了多有效的行动」的代理指标。
- **每会话归档**：生成 `sessions/<date>_<项目>_<标题>_<sid8>.md`，frontmatter + 逐条 prompt（`## p<seq>` 真标题，支持锚点跳转）。
- **主索引**：`INDEX.md` 含处理截止时间、项目概览、按日期倒序分组表、分析报告链接。
- **质量分析**：启发式 5 维打分（长度/结构/上下文/有效性）+ Top/Bottom 30 排行（「位置」列跳转到原文）；可选 LLM 深析产出最佳实践报告。
- **增量更新**：按 mtime + 行数做 checkpoint，未变会话自动跳过；记录处理截止时间，重跑从该点继续。

## 数据流

```
~/.claude/projects/*/*.jsonl   （顶层会话转录，排除 */subagents/*）
        │  extract.py（真人 prompt 判定 + 关联回复统计 + 增量 checkpoint）
        ▼
dataset/prompts.jsonl + dataset/sessions/<key>.{jsonl,meta.json} + .archive-state.json
        │
   ┌────┴──────────────────────────┐
 analyze.py（启发式打分 + 选样）   render.py（每会话 md + INDEX）
        │
 （可选）LLM 深析 Workflow → analysis/<date>-prompt-quality-report.md
```

顺序固定 **extract → analyze →（可选 LLM 深析）→ render**：render 放最后，INDEX 才能链接到分析报告。

## 目录结构

```
skills/prompt-archive/
├── SKILL.md          # 触发条件 + 命令入口
├── README.md         # 本文件
└── scripts/          # 仅依赖标准库
    ├── extract.py    # 抽取 + 增量 checkpoint
    ├── analyze.py    # 启发式打分 + 选样
    └── render.py     # 渲染每会话 md + INDEX
```

## 用法

```
cd skills/prompt-archive
OUT=~/workspace/prompt-archive

python3 scripts/extract.py --out $OUT            # 增量抽取 → dataset
python3 scripts/analyze.py --out $OUT --date $(date +%F)   # 启发式打分 + Top/Bottom 30
python3 scripts/render.py  --out $OUT            # 生成 sessions/*.md + INDEX.md
```

参数说明见 SKILL.md。
