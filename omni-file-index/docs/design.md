# Omni 文件索引前端 — 设计文档

> 日期：2026-07-20
> 范围：OmniAdaptor / OmniStream / OmniOperator 三个项目

## 1. 目标

本地打开一个真实前端工程，以"类文件夹"目录树展示三个 omni 项目的全部源码文件；点击文件即可看到该文件的作用（markdown）。详情页左侧列相关方法/函数/类/对象等实体，右侧为 mermaid 流程图 + 极少通俗文字。全文件覆盖、支持增量扫描新增文件、调 LLM 提炼实体与简洁作用。重点文件的 mermaid 与文字聚焦 **SQL 执行端到端业务流程**。风格简洁、多 mermaid 少文字。

## 2. 三项目关系

```
Flink SQL
  → OmniAdaptor（桥接层，Scala/Java）：计划拦截/翻译/决策下沉 + JNI
  → OmniStream（Flink native 运行时，C++）：plan→算子图、runtime 调度、translate
  → OmniOperator（native 算子库，C++）：算子执行 + 向量化表达式（OmniVec）
  → 结果回传 → Flink → 用户
```

## 3. 总体架构

管线（pipeline/，Node+TS）+ 前端（web/，Vite+React+TS）分离。

```
omni-file-index/
├─ pipeline/src/   scan.ts · llm.ts · extract.ts · build-data.ts · config.ts · types.ts
├─ web/src/        App · 文件树 · 详情页 · 概览页 · mermaid 渲染 · data.json(生成)
├─ key-files.yaml  SQL 端到端链路重点文件清单
├─ .env            ZHIPU_API_KEY / base_url / 模型名
└─ .index/         manifest.json + cache/<hash>.json（运行时缓存，gitignore）
```

数据流：`scan`（哈希比对找新增/变更）→ `extract`（只对新哈希调 GLM，结果按哈希缓存）→ `build-data`（聚合→web/src/data.json）→ `npm run build`（vite-plugin-singlefile 内联全部，产出可双击的 dist/index.html）。

## 4. 增量扫描

- 每文件 `sha256(内容)` 为 key；内容不变永不重调 LLM。manifest 另存 size/mtime 供预筛。
- `scan` 标记新增/变更 pending；未变复用 cache；删除从树移除但 cache 保留。
- `extract` 断点续跑：每文件落盘即缓存，中断重跑自动跳过。并发可配（默认 5），GLM 限速退避。

## 5. LLM 提炼（两档，控成本）

| 档位 | 模型 | 产出 | 量 |
|---|---|---|---|
| 普通文件（全量） | GLM 便宜模型 | 实体列表（函数/类/方法/对象 各带一行作用）+ 简洁作用（1-2 句） | ~4000 |
| 重点文件 | GLM 强模型 | 上述 + 1-2 张 mermaid（流程/时序，聚焦 SQL 执行）+ 2-3 句通俗说明 | ~60-100 |

- 大文件截断（前 30KB + 末尾结构）。
- 普通文件右栏 mermaid **不调 LLM**，由管线按实体机械生成轻量结构图，保证"每文件有图"且零额外成本。
- 强制 JSON schema，解析失败重试一次。

## 6. 重点文件：SQL 端到端链路

`key-files.yaml` 三层各挑入口/核心类（详见清单文件）。可调。

## 7. 前端布局

```
┌──────────────┬─────────────────┬──────────────────────┐
│ 文件树(搜索)  │ 实体 (左)        │ Mermaid + 说明 (右)   │
│ ▾ OmniAdaptor│ ▸ 函数/类/方法/对象│ [SQL 流程 mermaid]    │
│ ▾ OmniStream │                 │ 通俗说明（少文字）     │
│ ▾ OmniOperator│                 │                       │
│ ★重点 +新增   │                 │                       │
└──────────────┴─────────────────┴──────────────────────┘
```

- 树：真实完整目录，折叠展开，类型图标，★重点、+新增标记，顶部搜索过滤。
- 概览页（默认）：三项目关系 + SQL 端到端总览 mermaid。
- 详情页：顶部作用 → 左实体分组 → 右 mermaid（mermaid.js 本地打包离线渲染）+ 极简说明。面包屑 + 跨文件跳转。
- 风格：浅色极简、克制留白、等宽符号、可选暗色切换。
- 交付：`vite-plugin-singlefile` + `base:'./'` → `dist/index.html` 双击离线打开。

## 8. 运行

- 首次：`npm run scan && npm run extract && npm run build-data && npm run build:web` → 双击 `web/dist/index.html`。
- 增量：源码改动后重跑同样命令，仅处理新文件。
- 调试：`npm run dev:web`。
- `.env` 填 `ZHIPU_API_KEY`；无网前端照常打开。

## 9. 取舍

- 首次全量 ~4000 次 GLM 调用（便宜模型），后续增量近零成本；支持 `--limit` 小范围试跑。
- 普通文件 mermaid 为机械结构图（有图但简朴），重点文件为 LLM 画的 SQL 流程图。
