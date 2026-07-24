---
name: ograc-docs-review
description: 
  检视并修复 oGRAC 官方中文文档（docs/zh）的低级错误：错别字、产品命名不一致、中英文混排空格、行内代码缺失、SQL 关键字大小写、Markdown 格式、口语化表述、Shell 代码块可复制性、弯引号等。
  当用户提到「检视/审校/修复/规范化 docs/zh 文档」「文档低级错误」「文档格式检查」「清理口语化」「PR 文档自检」「同步官方文档前批量检查」或任何涉及 oGRAC 中文文档质量批处理的任务时，必须优先调用本 skill。
  即使请求中没有出现「skill」「自动化」等字样，只要与 oGRAC 中文文档的批量质量修复相关，就使用本 skill。
---

# oGRAC 中文文档低级错误检视与修复

## 适用范围

- 路径：`docs/zh/` 下全部 Markdown（含 `_toc.yaml`）。
- 目标：修明确错误，不脑补产品语义。
- 产品名：正文统一用 `oGRAC`；第三方制品名（如 `openGauss-jdbc-x.x.x.jar`）可保留。

## 工作流程

1. **读规则**：先读取 [references/ograc_rules.json](references/ograc_rules.json)。
2. **扫描**：用 `search_patterns` 批量检索。
3. **分类修复**：按 `priority_rules` 优先级处理。
4. **验证**：修复后必须重跑对应 `search_patterns`，确认无残留。
5. **输出**：按下方模板输出，标注每项状态。

## 规则速查

| 主题 | JSON 字段 |
|---|---|
| 优先级与示例 | `priority_rules` |
| 产品命名规范 | `naming_conventions` |
| 中英文混排空格 | `spacing_rules` |
| 行内代码术语 | `inline_code_terms` |
| 口语化替换 | `oral_replacements` |
| 错别字/别字 | `typos` |
| SQL 关键字小写→大写 | `sql_keywords` |
| 代码块语言标签 | `code_block_languages` |
| 检索命令 | `search_patterns` |
| 人工复查项 | `manual_checks` |

## 绝对不修清单

- 产品参数名：`M_RUNING_MODE` 等安装 JSON 键名。
- 架构/口径矛盾：`alter_database.md` / `alter_table.md` 中「主备」表述、`architecture_description.md`「ODBC 尚在开发中」vs release notes「支持 ODBC」、`technical_feature_overview`「存算分离」vs「共享存储」。
- WSR 帮助文本中 `shard` / `shared` / `CN node` 等需对照产品实现的术语。
- 任何你不 100% 确定是「明确低级错误」的内容。

以上条目只能标注 **待确认**，不得擅自修改。

## 特殊 caution

- **YAML**：`_toc.yaml` 直接影响官网构建。修改前确认有门禁或本地可验证；不随意增删条目；`href` 必须与文件名完全一致。
- **引号**：技术参数、URL、命令统一用 ASCII 直引号 `"`。改引号时必须核对上下文语义，不得导致句意反转。
- **Shell 代码块**：删除行首 `$` / `#` 提示符；如需说明环境，用注释 `#` 写在行首或代码块上方。

## 输出模板

先输出一行汇总：

```markdown
共扫描 N 个文件，修复 M 处，待确认 K 处，未处理 L 处；全部修改已重跑检索命令验证（是/否）。
```

再按文件输出：

```markdown
### docs/zh/.../xxx.md
- **P0 错别字**：`NOLOGING` → `NOLOGGING`（第 42 行）— 已修复 / 已验证
- **P1 命名**：`openGaussSpace` → `ogracSpace`（第 15 行）— 已修复 / 已验证
- **P2 Markdown**：` ```SQL ` → ` ```sql `（第 88 行）— 已修复 / 已验证
- **待确认**：`M_RUNING_MODE` 参数名未改（第 120 行，需产品确认）
- **未处理**：`shared` 与 `shard` 混淆（第 200 行，无法判定）
```

状态只能填：`已修复 / 待确认 / 未处理`。修复项必须同时写「已验证」。

## 工作纪律

- 只修明确错误，不脑补产品语义。
- 不确定即 **待确认**，停止，不擅自合并。
- 修改后必须重跑 `search_patterns` 中相关命令，确认无残留。
- 不提交 `.gitignore` 等无关文件的误改。
