# knowledge-base — 知识卡片管理 Skill

`knowledge-base` 是一个知识库管理 Agent Skill，用于将问答、分析、技术调研归档为结构化知识卡片，并维护可检索的索引。

## 主要能力

- **创建知识卡片**：从对话中提取关键知识，生成带 frontmatter 的标准 MD 文件（内容原文保留，不重组不压缩）。
- **分类归档**：按 category 自动创建目录，维护分类索引和全局索引。
- **检索**：按关键词、标签、分类搜索知识库。
- **索引重建**：扫描所有卡片重建全局和分类索引。

## 目录说明

- `SKILL.md`：skill 的主说明和执行规则。
- `config.yaml`：配置模板（知识库根目录 `knowledge_root`）。
- `references/`：卡片格式规范、索引格式规范等补充说明。
- `templates/`：卡片模板。
- `evals/evals.json`：skill 行为测试用例。

## 快速使用

skill 安装后，在任意对话中：

```
/kb                          → 从当前对话创建知识卡片
/kb search bitmap            → 搜索包含 "bitmap" 的卡片
/kb list                     → 列出所有分类和卡片数
/kb list jemalloc            → 列出某分类下的卡片
/kb index                    → 重建全部索引
```

> `/kb` 是 `knowledge-base` 的简写触发词，两者等价。

## 配置：知识库根目录

skill 把卡片与索引写入「知识库根目录」`knowledge_root`，按以下顺序解析：

1. 环境变量 `KB_ROOT`（最高优先级）
2. `config.yaml` 的 `knowledge_root` 字段
3. 默认值 `~/knowledge`

编辑 `config.yaml` 即可指定自己的知识库位置：

```yaml
knowledge_root: "~/knowledge"
```

或临时用环境变量覆盖：

```bash
export KB_ROOT=/path/to/your/knowledge
```

知识库目录结构示例：

```
{knowledge_root}/
├── INDEX.md              ← 全局索引
├── jemalloc/
│   ├── _INDEX.md         ← 分类索引
│   ├── bitmap-tree-root-cause.md
│   └── sve2-vectorization.md
├── performance/
│   └── ...
└── workflow/
    └── ...
```

> 注意：知识库数据应存放在仓库之外的用户目录（默认 `~/knowledge`），天然不在 git 工作区。skill 内的 `.gitignore` 仅在你把 `knowledge_root` 配成仓库内路径时，兜底阻止数据被提交。
