# 索引格式规范

> `{knowledge_root}` 为解析后的知识库根目录（见 `SKILL.md` 的「配置：知识库根目录」）。

## 全局索引 INDEX.md

位置：`{knowledge_root}/INDEX.md`

```markdown
# 知识库全局索引

> 知识卡片归档。按 `category/filename` 组织，支持 tag 检索。
>
> 使用: `/kb search 关键词` 搜索 | `/kb list [分类]` 列出 | `/kb create` 创建

| # | 卡片 | 分类 | 标签 | 日期 |
|---|------|------|------|------|
| 1 | [标题](category/filename.md) | `category` | `tag1` `tag2` | YYYY-MM-DD |
| 2 | [标题](category/filename.md) | `category` | `tag1` `tag2` | YYYY-MM-DD |
```

排序：按 category 分组，组内按 created 降序。序号为全局递增。

## 分类索引 _INDEX.md

位置：`{knowledge_root}/{category}/_INDEX.md`

```markdown
# {Category} 知识卡片索引

> {1-2 句描述该分类覆盖的内容}

| # | 卡片 | 标签 | 日期 | 摘要 |
|---|------|------|------|------|
| 1 | [标题](filename.md) | `tag1` `tag2` | YYYY-MM-DD | 一句话摘要 |
| 2 | [标题](filename.md) | `tag1` `tag2` | YYYY-MM-DD | 一句话摘要 |
```

序号为分类内递增。

## 索引更新规则

- 创建卡片时：追加到两层索引末尾，序号递增
- 重建索引（/kb index）时：扫描所有 .md 文件 frontmatter，重新生成，序号重排
- 删除卡片后需手动 `/kb index` 重建
