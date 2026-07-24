# knowledge-base Skill 设计文档

## 定位

`knowledge-base` 是一个**纯 LLM-driven、零脚本**的知识卡片管理 Skill。它把日常问答、代码分析、技术调研沉淀为带 frontmatter 的结构化 Markdown 卡片，并维护可检索的全局索引与分类索引，解决「分析做完即丢失、下次重复劳动」的问题。

对应 skill 目录：`skills/knowledge-base/`。

## 设计理念

### 1. 内容原文保留，不重组不压缩

知识卡片 = **frontmatter + 内容原样保留**。这是本 skill 最核心的设计决策，也是它区别于「摘要工具」的地方：

- 源材料（已有 `.md` 文档、对话中的完整回答）本身已经是结构化的，二次重组会丢失推导细节与上下文。
- 卡片面向「未来的自己」：不依赖当时的对话上下文就能独立读懂。
- 仅在源材料极其零散时才整理结构（罕见路径）。

> 早期脚手架版本曾强制「问题/背景 → 核心内容 → 关键结论 → 延伸」四段结构，实践中发现会割裂原始分析、增加写入成本，故演进为「原文保留」。

### 2. 两层索引

- **全局索引** `INDEX.md`：跨分类总览，按 category 分组、组内按 created 降序。
- **分类索引** `_INDEX.md`：每个 category 目录一份，含一句话摘要列。

创建卡片时增量追加，`/kb index` 时全量重建。

### 3. Token 节约

写入卡片直接用 `Write` 工具落盘，不在对话里先把内容复述一遍；批量创建时并行写入，减少往返轮次。

## 目录结构

```
skills/knowledge-base/
├── SKILL.md                    # 主说明与执行规则（create/search/index/list 四操作）
├── README.md                   # 使用说明
├── config.yaml                 # 配置：knowledge_root
├── .gitignore                  # 兜底忽略仓库内的 knowledge/ 数据目录
├── references/
│   ├── card-format.md          # 卡片格式规范（frontmatter + 正文原则）
│   └── index-format.md         # 两层索引格式规范
├── templates/
│   └── card-template.md        # 卡片模板
└── evals/
    └── evals.json              # 5 条行为测试用例
```

## 配置：知识库根目录解析

所有卡片与索引写入「知识库根目录」`knowledge_root`，按优先级解析：

1. 环境变量 `KB_ROOT`
2. `config.yaml` 的 `knowledge_root` 字段
3. 默认值 `~/knowledge`

知识库**数据本身存放在仓库之外的用户目录**（默认 `~/knowledge`），天然不在 git 工作区、不会被提交。skill 目录内的 `.gitignore`（规则 `knowledge/`）仅作兜底：当用户把 `knowledge_root` 配成仓库内的相对路径时，阻止知识数据被误提交。本仓库只维护 skill 的「能力定义」，不存放任何用户私有知识内容。

## 操作流程概览

| 操作 | 触发词 | 行为 |
|------|--------|------|
| create | "整理成知识卡片"、`/kb`、`/kb 标题` | 抽取 title/category/tags → 写卡片 → 更新两层索引 |
| search | "搜索知识库"、`/kb search 关键词` | grep frontmatter + INDEX → 列出标题/标签/摘要 |
| index  | "重建索引"、`/kb index` | 扫描全部卡片 frontmatter → 重建两层索引 |
| list   | "列出知识库"、`/kb list [分类]` | 列分类目录与卡片计数 |

详细流程见 `skills/knowledge-base/SKILL.md`。

## 与全局「知识库自动召回」的关系

部分使用者会在全局 `CLAUDE.md` 中配置「任务涉及特定领域时先读 `INDEX.md` 扫描相关卡片」的自动召回规则。本 skill 负责**生产与维护**这些卡片和索引，召回规则负责**消费**它们，二者解耦：

- 召回侧约定：KB 内容是历史参考、不是当前事实，引用前需与代码/数据交叉验证。
- 生产侧（本 skill）只保证卡片结构规范、索引可检索，不对内容时效性背书。

## 扩展点

- **category 命名约定 / tag 标准化词表**：可在 `references/` 下新增规范文件，统一跨项目卡片的分类与标签口径。
- **跨卡片关联**：frontmatter 的 `related` 字段记录关联卡片文件名，未来可据此生成关系图。
