# 知识卡片格式规范

## Frontmatter（必需）

```yaml
---
title: "一句话结论式标题"
category: kebab-case-分类名
tags: [tag1, tag2, tag3]        # 3-6 个，用于跨目录检索
created: YYYY-MM-DD
related: [other-card-name]      # 关联卡片文件名（不含 .md），可为空
source: "来源说明"              # 如 "opt-fill-tiny 优化分析" 或 "问答"
---
```

## 正文

frontmatter 之后直接写入内容原文，保持原有章节结构。

- 已有 `.md` 文档：全文保留
- 对话中的完整回答：保留原文，调整标题使其结论化
- 不做内容压缩、重组、摘要

## 写入原则

1. 一张卡片回答一个"为什么"或记录一个完整技术点
2. 面向未来的自己：不需要回忆当时的对话就能理解
3. 不对内容做压缩——源材料本身已经结构化
4. 不使用 emoji
5. 文件名：kebab-case，20 字符内，无日期前缀
6. 写入时直接用 Write 工具，不要先在对话中输出内容再写入
