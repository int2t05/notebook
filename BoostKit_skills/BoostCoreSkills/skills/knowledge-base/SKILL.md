---
name: knowledge-base
description: 知识卡片管理 — 创建、搜索、索引、列出。用于将问答、分析、技术调研归档为结构化知识卡片并维护可检索索引。当用户说"整理成知识卡片"、"写一张卡片"、"搜索知识库"、"重建索引"，或使用 kb/knowledge-base create/search/index/list 等命令时触发。
---

# 知识库管理 Skill (knowledge-base)

将问答、分析、技术调研归档为带 frontmatter 的结构化知识卡片，并维护可检索的全局索引与分类索引。

## 配置：知识库根目录

所有操作都作用于一个「知识库根目录」`{knowledge_root}`。执行任何操作前，先按以下顺序解析它：

1. 环境变量 `KB_ROOT`（最高优先级）
2. 本 skill 目录下 `config.yaml` 的 `knowledge_root` 字段
3. 默认值 `~/knowledge`

bash 示例统一用 `"${KB_ROOT:-$HOME/knowledge}"` 表示「环境变量优先、否则用默认」。注意 **tilde 展开陷阱**：bash 在双引号内、以及变量赋值后再使用时都**不会**对 `~` 做展开，`ROOT="~/knowledge"` 会指向一个名为字面 `~` 的相对目录。因此若从 `config.yaml` 读到的 `knowledge_root` 以 `~` 开头，代入前必须先展开为绝对路径，例如 `raw="$(grep ... config.yaml)"; ROOT="${raw/#\~/$HOME}"`，**切勿**直接写成 `ROOT="~/..."`。后文出现的 `{knowledge_root}` 均指解析后的实际绝对路径。

> 示例：某用户把 `knowledge_root` 配为 `/home/hxq/workspace/knowledge`，则所有卡片与索引都落在该目录下。

## 参数解析

从用户输入中识别操作类型:
- **create** (默认): "整理成知识卡片"、"写一张卡片"、"kb create"、或直接 `/kb 标题`
- **search**: "搜索知识库"、"kb search 关键词"、"知识库里有没有 X"
- **index**: "重建索引"、"kb index"
- **list**: "列出知识库"、"kb list [分类]"

---

## 操作: CREATE

当用户要求创建知识卡片时，按以下流程执行:

### 1. 确定卡片元信息

从对话上下文或用户指令中提取:
- **title**: 卡片标题（一句话结论式，不要用问句）
- **category**: 分类目录名（kebab-case，如 `jemalloc`、`performance`、`aarch64`、`workflow`）
- **tags**: 3-6 个标签，用于跨目录检索
- **related**: 关联卡片的文件名（不含 .md），可留空

如果用户没指定 category，从内容推断并确认。

### 2. 生成文件名

文件名格式: `{简短描述}.md` (kebab-case，不带日期前缀，20 字符内)
路径: `{knowledge_root}/{category}/{filename}.md`

如果 category 目录不存在，自动创建。

### 3. 写入卡片内容

卡片 = **frontmatter + 内容原样保留**。不对内容做重组或压缩。

```markdown
---
title: "{title}"
category: {category}
tags: [{tag1}, {tag2}, ...]
created: {YYYY-MM-DD}
related: [{related1}, {related2}, ...]
source: {来源说明，如 "opt-fill-tiny 分支优化分析" 或 "问答"}
---

# {title}

{内容直接写入，保持原有结构}
```

**内容来源与处理方式**:

| 来源 | 处理 |
|------|------|
| 已有 `.md` 文档 | 全文保留，只加 frontmatter |
| 对话中的完整回答 | 保留回答原文，调整标题使其结论化 |
| 极零散的片段信息 | 仅此情况下才整理结构（罕见） |

**写入原则**:
- 一张卡片回答一个"为什么"或记录一个完整技术点
- 面向未来的自己：不需要回忆当时的对话上下文就能理解
- 不使用 emoji（除非用户要求）
- 不对内容做压缩、摘要、重组——源材料（无论是文档还是问答回答）本身已经结构化

**Token 节约原则**:
- 写入卡片时直接用 Write 工具写入，不要先在对话中输出内容再写入
- 不要重复对话中已有的分析内容到输出文本
- 批量创建时并行写入多张卡片，减少来回轮次

### 4. 更新索引

**分类索引** (`{knowledge_root}/{category}/_INDEX.md`):

如果不存在，创建:
```markdown
# {Category} 知识卡片索引

> {1-2 句描述该分类覆盖的内容}

| # | 卡片 | 标签 | 日期 | 摘要 |
|---|------|------|------|------|
```

在表格末尾追加一行（序号递增）:
```
| {N} | [{title}]({filename}.md) | `{tag1}` `{tag2}` | {date} | {一句话摘要} |
```

**全局索引** (`{knowledge_root}/INDEX.md`):

如果不存在，创建:
```markdown
# 知识库全局索引

> 知识卡片归档。按 `category/filename` 组织，支持 tag 检索。
>
> 使用: `/kb search 关键词` 搜索 | `/kb list [分类]` 列出 | `/kb create` 创建

| # | 卡片 | 分类 | 标签 | 日期 |
|---|------|------|------|------|
```

在表格末尾追加一行（序号为全局递增）:
```
| {N} | [{title}]({category}/{filename}.md) | `{category}` | `{tag1}` `{tag2}` | {date} |
```

### 5. 输出确认

完成后输出:
```
已创建: {knowledge_root}/{category}/{filename}.md
标签: {tags}
索引已更新: INDEX.md + {category}/_INDEX.md
```

---

## 操作: SEARCH

当用户搜索知识库时:

### 1. 搜索策略

按以下顺序搜索 `{knowledge_root}`:

```bash
ROOT="${KB_ROOT:-$HOME/knowledge}"
# 先搜 frontmatter 的 tags 和 title
grep -rl "关键词" "$ROOT" --include="*.md"

# 再搜全局索引的标签列
grep -i "关键词" "$ROOT/INDEX.md"
```

### 2. 展示结果

列出匹配的卡片:
```
搜索 "bitmap" 找到 3 张卡片:

1. [BITMAP_USE_TREE 触发机制与 T3 优化](jemalloc/bitmap-tree-root-cause.md)
   tags: bitmap, performance, aarch64
   摘要: 4K vs 64K 页下 bitmap tree 模式的触发条件...

2. [cfs_lu 向量化分析与 SVE2 优化](jemalloc/sve2-vectorization.md)
   tags: bitmap, sve2, vectorization
   摘要: ...
```

如果用户指定了子目录，只搜该目录。

### 3. 后续操作

搜索结果出来后，等待用户指令:
- "读第 1 个" → Read 该卡片内容
- "和当前问题有什么关联" → 读取卡片后结合当前上下文分析

---

## 操作: INDEX

重建全局索引和所有分类索引:

```bash
ROOT="${KB_ROOT:-$HOME/knowledge}"
# 扫描所有 .md 文件（排除 INDEX.md 和 _INDEX.md）
find "$ROOT" -name "*.md" ! -name "INDEX.md" ! -name "_INDEX.md" -type f
```

对每个文件:
1. 读取 frontmatter 提取 title, category, tags, created
2. 重建 INDEX.md 表格（按 category 分组，组内按 created 降序）
3. 重建每个 category 的 _INDEX.md

完成后输出回执，例如：`已重建 INDEX.md + {N} 个分类索引，共处理 {M} 张卡片`。

---

## 操作: LIST

列出知识库结构:

```bash
ROOT="${KB_ROOT:-$HOME/knowledge}"
# 无参数: 列出所有分类和卡片数
find "$ROOT" -maxdepth 1 -type d | sort

# 有参数: 列出该分类下的卡片
ls "$ROOT/{category}/"
```

输出格式:
```
知识库 ({knowledge_root}):
  jemalloc/     3 张卡片
  performance/  1 张卡片
  workflow/     2 张卡片
  ───────────
  共 6 张卡片，3 个分类
```

---

## 参考

- 卡片格式规范：`references/card-format.md`
- 索引格式规范：`references/index-format.md`
- 卡片模板：`templates/card-template.md`
- 行为测试用例：`evals/evals.json`
