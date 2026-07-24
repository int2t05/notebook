# Omni 文件索引

OmniAdaptor / OmniStream / OmniOperator 三项目的文件索引前端。本地打开，目录树导航，点击文件看作用（实体 + mermaid）。全文件覆盖、增量扫描、LLM 提炼。重点文件聚焦 SQL 执行端到端流程。

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 填 API key
cp .env.example .env   # 把 ZHIPU_API_KEY 填上

# 3. 扫描 + 提炼 + 构建前端
npm run scan           # 扫描三项目目录，增量哈希
npm run extract        # 调 GLM 提炼（首次较久，可加 -- --limit 20 试跑）
npm run build-data     # 聚合成 web/src/data.json
npm run build:web      # 构建前端

# 4. 打开
# 双击 web/dist/index.html 即可离线浏览
```

试跑：`npm run extract -- --limit 20` 只处理 20 个文件验证。

开发调试前端：`npm run dev:web`。

## 结构

- `pipeline/` 扫描 + LLM 提炼 + 聚合（Node + TS）
- `web/` 前端（Vite + React + TS，构建为单 HTML 离线打开）
- `key-files.yaml` SQL 端到端链路重点文件清单（可调）
- `.index/` 运行时缓存（manifest + 按 hash 的 LLM 结果），gitignore
- `docs/design.md` 设计文档

## 没填 key 也能用

前端构建不依赖 key。可先用 `npm run scan && npm run build-data && npm run build:web` 生成"只有目录树 + 机械结构图"的版本浏览；填 key 跑 `extract` 后再 build 即得到完整图文。
