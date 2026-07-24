---
name: drawio-diagrams
description: 使用 Draw.io MCP 创建、编辑和导出架构图、流程图、时序关系图、算法原理图及 .drawio 文件。用户提到 draw.io、drawio、流程图、架构图、原理图、拓扑图，或要求修改现有图表时使用。
---

# Draw.io 图表

使用 `drawio` MCP 工具生成可继续编辑的标准 Draw.io 图表，并在浏览器中实时预览。

## 工作流

1. 调用 `start_session` 启动预览会话。
2. 判断任务类型：
   - 从零创建：调用 `create_new_diagram`，传入完整 `mxGraphModel` XML。
   - 修改现有图：先调用 `get_diagram` 获取最新 XML 和单元格 ID，再调用 `edit_diagram`。
   - 仅添加元素：可直接用 `edit_diagram` 的 `add` 操作，但必须使用新 ID。
3. 检查布局、标签、连线和阅读顺序。
4. 用户要求落盘时调用 `export_diagram`，优先导出 `.drawio`；需要展示时再额外导出 `.png` 或 `.svg`。

## 创建规则

- XML 必须包含 `mxGraphModel`、`root`、`id="0"` 和 `id="1"`。
- 顶层图元使用 `parent="1"`，新 ID 不得重复。
- 默认将主要内容控制在 `x=40..760`、`y=40..560`，避免超出单页视口。
- 形状间保留足够间距；标签较长时增加宽高，不让文字溢出。
- 边必须明确指定 `exitX`、`exitY`、`entryX`、`entryY`。
- 多条边不得完全共用路径；必要时使用 waypoint 绕开形状。
- 使用用户的语言书写标题、节点和说明。
- 复杂主题按“总览 -> 核心流程 -> 实现细节 -> 对比/结论”分区。

## 编辑规则

- 不得使用 `create_new_diagram` 修改现有图，它会替换整张图。
- 更新或删除前必须重新调用 `get_diagram`，保留用户在浏览器中的手动改动。
- `update` 必须提交完整的 `mxCell`；`delete` 只传目标 ID。
- 修改后再次调用 `get_diagram` 检查结构是否符合预期。

## 输出与容错

- `start_session` 会启动本机 HTTP 服务并打开浏览器。
- 默认 Draw.io 编辑器来自 `https://embed.diagrams.net`；敏感图表应改用可信的 `DRAWIO_BASE_URL`。
- 导出路径使用工作区内的明确路径，禁止覆盖用户未要求覆盖的文件。
- 如果浏览器无法启动，仍可生成标准 `.drawio` XML 文件，并说明未完成实时预览。
