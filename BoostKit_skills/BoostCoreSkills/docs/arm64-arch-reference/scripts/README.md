# scripts — 构建本 skill 的完整工具链（归档副本）

这些是生成 `references/` 下全部表格的脚本与数据模块的**归档快照**，用于记录与复现。
设计原理见上级目录的 `../DESIGN.md`。

> ⚠️ **这是副本，不能就地运行**：脚本以"脚本同目录"为基准定位输入数据
> （`gen_feat_table.py` 找同目录的 `Features.json`；`gen_instr_table.py` glob 同目录下的
> `Instructions/...` 快照）。要真正再生成，请把这些脚本放到**带官方数据的数据集仓库根目录**
> （含 `Features/`、`Instructions/`），按下文顺序运行。官方数据下载地址见 `../DESIGN.md` 第 2 节。

## 文件清单

| 文件 | 类型 | 角色 |
| --- | --- | --- |
| `gen_feat_table.py` | 脚本 | 读 `Features.json` → 生成特性表 `Features.md`（套 `feat_meta`+`feat_desc`，按域分组，严格校验 META） |
| `feat_meta.py` | 人工数据 | `META[name]=(中文翻译, 功能域)` + `GROUP_ORDER`（11 域）。**新增/翻译特性时改这里** |
| `feat_desc.py` | 生成数据 | `DESC[name]=中文介绍`（346 条），由翻译流水线生成 |
| `gen_instr_table.py` | 脚本 | 解析 A64 索引+单指令 XML → 生成 `instructions/{base,simd-fp,sve,sme}.md`+`00-index.md`（套 `instr_meta`+`instr_desc`） |
| `instr_meta.py` | 人工数据 | 分类配置 `CATEGORY_LABELS` / `INDEX_TO_CATEGORY` |
| `instr_desc.py` | 生成数据 | `INSTR_DESC[iform_id]=中文一行简介`（2258 条），由翻译流水线生成 |
| `prep_translate.py` | 脚本 | 把待译项切批 → `skill_build/desc/in_*.json` + `manifest.json` |
| `translate_workflow.js` | Workflow | 起多个 sonnet 子 agent 翻译，读 `in_*.json` 写 `out_*.json`（经 Claude Code `Workflow` 工具运行；批次清单不写死在脚本里，运行时把 `manifest.json` 内容作为 **args** 传入） |
| `merge_translate.py` | 脚本 | 汇总 `out_*.json` → 生成 `feat_desc.py`/`instr_desc.py`（含空集护栏，不会清空已有翻译） |

依赖：纯标准库 Python 3（`json/re/sys/os/xml.etree/glob`），无第三方包。翻译执行依赖 Claude Code 的 `Workflow` 工具。

## 运行顺序（在数据集仓库根目录）

```bash
# 0. 特性源数据须复制到脚本同目录（gen_feat_table.py 硬编码同目录 Features.json）
cp Features/AARCHMRS_A_profile-2026-03_96/Features.json ./Features.json

# 1. 生成表格（首跑：feat_desc/instr_desc 不存在时自动回退英文）
python3 gen_feat_table.py        # → Features.md（+ skill_build/reference/Features.md）
python3 gen_instr_table.py       # → skill_build/reference/instructions/*.md

# 2. 翻译流水线（生成/更新中文）
python3 prep_translate.py        # 切批 → skill_build/desc/in_*.json + manifest.json
#   用 Claude Code 的 Workflow 工具运行 translate_workflow.js，把 manifest.json 内容作为 args 传入 → out_*.json
python3 merge_translate.py       # 汇总 → feat_desc.py / instr_desc.py

# 3. 用中文重生成，并复制进 skill
python3 gen_feat_table.py && python3 gen_instr_table.py
cp -r skill_build/reference/* ~/.claude/skills/arm64-arch-reference/references/
```

升级 ARM 数据版本的完整流程见 `../DESIGN.md` 第 8 节。
