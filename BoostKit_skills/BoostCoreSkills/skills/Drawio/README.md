# Draw.io MCP + Skill Bundle

这是一个**便携式 Draw.io 集成包**，包含：

| 组件 | 说明 |
| --- | --- |
| **MCP Server** | 基于 [`@next-ai-drawio/mcp-server@0.2.0`](https://www.npmjs.com/package/@next-ai-drawio/mcp-server) 的 Model Context Protocol 服务，可在 Trae / Cursor / Claude Desktop / Codex 等支持 MCP 的编辑器中作为工具调用。 |
| **Skill** | 与 MCP 配套的 `drawio-diagrams` Skill，封装了"创建/编辑/导出"图表的标准工作流，使用自然语言描述时由编辑器自动激活。 |

> 把整个文件夹直接拷贝给同事，他/她只需执行一次 `./install.sh` 就能在自己电脑上启用。

---

## 目录结构

```
Drawio/
├── README.md                       本文件
├── install.sh                      一键安装脚本（自动 npm install）
├── mcp/
│   ├── mcp.json                    MCP 注册配置（含占位符 <DRAWIO_BUNDLE>）
│   ├── run-drawio-mcp.sh           MCP 启动脚本（zsh，自动定位 Node）
│   └── drawio/
│       ├── package.json            npm 依赖声明
│       └── package-lock.json       锁定的依赖版本
└── skill/
    └── drawio-diagrams/
        └── SKILL.md                Skill 描述（自动激活规则）
```

---

## 快速开始（推荐）

```bash
cd /Users/<you>/Desktop/Drawio
./install.sh
```

脚本会自动：

1. 在 `mcp/drawio/` 下执行 `npm install` 拉取 `@next-ai-drawio/mcp-server` 及其所有 npm 依赖（约 70+ 个传递依赖，包括 `@modelcontextprotocol/sdk`、`hono`、`express`、`linkedom` 等）。
2. 为启动脚本添加可执行权限。
3. 打印**直接可用的 MCP 配置片段**和 **Skill 安装命令**到终端。

---

## 手动安装

如果你不想跑 `install.sh`，按下面三步操作即可。

### 1. 准备 Node 运行时

MCP 服务需要 **Node.js 18+**。`run-drawio-mcp.sh` 会按以下顺序探测：

1. Trae 自带的 Electron：`/Applications/Trae CN.app/Contents/MacOS/Electron`
2. Homebrew / 系统 Node：`/opt/homebrew/bin/node`、`/usr/local/bin/node`
3. Codex 自带的 Node：`/Applications/Codex.app/Contents/Resources/node`
4. `PATH` 中的 `node`

如以上都不存在，请先安装 [Node.js 18+](https://nodejs.org)。

### 2. 安装 MCP 依赖

```bash
cd /Users/<you>/Desktop/Drawio/mcp/drawio
npm install
```

完成后会生成 `node_modules/@next-ai-drawio/mcp-server/dist/index.js`，启动脚本会调用它。

### 3. 注册 MCP（任选一种编辑器）

把 [`mcp/mcp.json`](mcp/mcp.json) 里的 `<DRAWIO_BUNDLE>` 替换为**本文件夹的绝对路径**，例如：

```json
{
  "mcpServers": {
    "drawio": {
      "command": "/bin/zsh",
      "args": [
        "/Users/lauyarn/Desktop/Drawio/mcp/run-drawio-mcp.sh"
      ],
      "env": {
        "PORT": "6002"
      }
    }
  }
}
```

不同编辑器的注册位置：

| 编辑器 | MCP 配置文件 |
| --- | --- |
| **Trae** | 项目内 `.trae/mcp.json` 或 `~/.trae/mcp.json` |
| **Cursor** | `~/.cursor/mcp.json` |
| **Claude Desktop (macOS)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Codex** | `~/.codex/config.toml`（按 Codex 文档格式嵌入） |

注册完成后**重启编辑器**，MCP 工具 `start_session` / `create_new_diagram` / `get_diagram` / `edit_diagram` / `export_diagram` 就会出现在工具列表中。

### 4. 安装 Skill

把 `skill/drawio-diagrams` 整个目录复制到编辑器扫描的 skills 根目录：

```bash
# Trae
cp -R /Users/<you>/Desktop/Drawio/skill/drawio-diagrams ~/.trae/skills/

# Claude Code
cp -R /Users/<you>/Desktop/Drawio/skill/drawio-diagrams ~/.claude/skills/

# Codex
cp -R /Users/<you>/Desktop/Drawio/skill/drawio-diagrams ~/.codex/skills/
```

（具体路径以你所用编辑器的 Skill 加载根目录为准。）

重启编辑器后，提到"draw.io / drawio / 流程图 / 架构图 / 原理图 / 拓扑图"等关键词时，Skill 会自动激活并指导模型调用 MCP 工具。

---

## MCP 提供的工具

| 工具 | 用途 |
| --- | --- |
| `start_session` | 启动本地 HTTP 服务并在浏览器中打开 Draw.io 实时预览（默认使用 `https://embed.diagrams.net`，可设置环境变量 `DRAWIO_BASE_URL` 改为内网/可信实例）。 |
| `create_new_diagram` | 传入完整 `mxGraphModel` XML，从零创建一张图。**会覆盖当前图**，不可用于修改。 |
| `get_diagram` | 拉取当前图的完整 XML 与单元格 ID（保留用户在浏览器中的手动改动）。修改图前必须先调它。 |
| `edit_diagram` | 按 ID 对单元格执行 `add` / `update` / `delete` 三种操作；`update` 必须提交完整的 `mxCell`。 |
| `export_diagram` | 将当前图导出为 `.drawio`、`.png`、`.svg`。 |

详细的 XML 布局约束、ID 规则、连线规则等见 [`skill/drawio-diagrams/SKILL.md`](skill/drawio-diagrams/SKILL.md)。

---

## 故障排查

| 现象 | 可能原因 | 解决办法 |
| --- | --- | --- |
| 启动报 `Draw.io MCP runtime is missing: .../node_modules/@next-ai-drawio/mcp-server/dist/index.js` | 还没装 npm 依赖 | 在 `mcp/drawio/` 下执行 `npm install` |
| 启动报 `Node.js 18 or newer was not found` | 系统中没有 Node 18+ | 安装 [Node.js 18+](https://nodejs.org) 或在启动脚本里追加自定义路径 |
| 编辑器中看不到 MCP 工具 | `mcp.json` 路径未替换 / 编辑器未重启 | 替换 `<DRAWIO_BUNDLE>` 为绝对路径并重启编辑器 |
| 浏览器没有自动弹出 | 6002 端口被占用 / 编辑器无 GUI | 修改 `mcp.json` 的 `env.PORT`；或直接调用 `export_diagram` 输出 `.drawio` 文件 |
| Skill 没自动激活 | 关键词未命中 / Skill 路径不对 | 把 `skill/drawio-diagrams` 复制到编辑器识别的 skills 根目录；描述里包含"drawio"等关键词 |

---

## 版本与升级

- `@next-ai-drawio/mcp-server` 版本：**0.2.0**（锁定在 `package-lock.json`）
- Node 引擎要求：**>= 18.14.1**
- 升级时只需修改 `mcp/drawio/package.json` 中的版本号，然后 `npm install`。

---

## 许可

`@next-ai-drawio/mcp-server` 遵循 **Apache-2.0** 许可（见 npm 包页面）。
本仓库中的 `install.sh` 与本 README 遵循仓库所在项目的许可。
