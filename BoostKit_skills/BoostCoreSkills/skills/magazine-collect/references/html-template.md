# HTML 输出模板（`mode=html` 专用）

本文档定义月刊产物 HTML 版的精确结构与写作要求。Step 9 之前必读。

## 设计原则

1. **邮件客户端兼容优先**：所有样式**内联**（`style="..."` 在每个元素上），不要用 `<style>` 块或外部 stylesheet——Gmail/Outlook/Foxmail 多数会剥离 `<style>` 标签。
2. **不依赖外部资源**：不引用 CDN、外部图片、Web Font、iframe——很多企业邮件防火墙会拦截外链，部分客户端默认禁用远程图片。
3. **保留全部内容**：HTML 是 md 的 1:1 视觉化呈现，不省略事件、不压缩三段式正文。
   - 排版顺序与月刊 md 一致：海报 → 目录 → **本期全局脉络（汇总各板块脉络的高亮卡片）** → 各板块核心事件 → 全月覆盖速览；各板块小节内不再单独放脉络卡片。
4. **可独立打开**：单文件 HTML（无 .css/.js 配套），既能用浏览器双击打开，也能作为邮件正文嵌入。
5. **CJK 友好**：字体栈优先列 `-apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif`，覆盖 macOS / iOS / Windows / Linux 主流场景。
6. **响应式但务实**：最大宽度 800px 居中；窄屏（< 600px）也能勉强读，但不做完整响应式（邮件场景不是 web app）。

---

## 整体骨架

````html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{领域}动态 {YYYY-MM}</title>
</head>
<body style="margin:0;padding:24px 12px;background:#f5f6f8;font-family:-apple-system,'PingFang SC','Microsoft YaHei','Segoe UI',sans-serif;color:#222;line-height:1.65;">

<!-- 外层卡片：边框 + 阴影 -->
<div style="max-width:800px;margin:0 auto;background:#ffffff;border:1px solid #e1e4ea;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);overflow:hidden;">

  <!-- ① 顶部海报 banner -->
  <div style="background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 60%,#06b6d4 100%);padding:36px 32px;color:#ffffff;">
    <div style="font-size:14px;opacity:0.85;letter-spacing:0.1em;">MAGAZINE / {YYYY-MM}</div>
    <h1 style="margin:8px 0 4px;font-size:30px;font-weight:700;letter-spacing:0.02em;">{领域}动态</h1>
    <div style="font-size:14px;opacity:0.85;">{start} ~ {end} · 整理时间 {today}</div>
    <div style="font-size:13px;opacity:0.75;margin-top:6px;">共 {K} 个板块 / 入选事件 {N} 条</div>
  </div>

  <!-- ② 目录 -->
  <div style="padding:24px 32px 0;border-bottom:1px solid #f0f1f3;">
    <div style="font-size:13px;color:#6b7280;letter-spacing:0.1em;margin-bottom:12px;">目录 · TABLE OF CONTENTS</div>
    <ol style="margin:0 0 20px;padding-left:20px;font-size:14px;color:#374151;">
      <li style="margin-bottom:6px;"><a href="#overview" style="color:#1e3a8a;text-decoration:none;">本期全局脉络</a></li>
      <li style="margin-bottom:6px;"><a href="#sec-1" style="color:#1e3a8a;text-decoration:none;">一、{板块 1 名}</a></li>
      <li style="margin-bottom:6px;"><a href="#sec-2" style="color:#1e3a8a;text-decoration:none;">二、{板块 2 名}</a>
        <ul style="margin:4px 0;padding-left:18px;font-size:13px;color:#6b7280;">
          <li><a href="#sec-2-1" style="color:#3b82f6;text-decoration:none;">2.1 {子板块 A}</a></li>
          <li><a href="#sec-2-2" style="color:#3b82f6;text-decoration:none;">2.2 {子板块 B}</a></li>
        </ul>
      </li>
      <!-- ... -->
    </ol>
  </div>

  <!-- ②.5 本期全局脉络：汇总所有板块脉络，紧跟目录、领先正文 -->
  <div id="overview" style="padding:20px 32px;">
    <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:18px 22px;">
      <div style="font-size:16px;color:#8a6d1a;font-weight:700;margin-bottom:4px;">🎯 本期全局脉络</div>
      <div style="font-size:12px;color:#a08a4a;margin-bottom:12px;">先纵览各板块脉络建立全局认识，核心事件见下文对应小节</div>
      <div style="font-size:14px;color:#444;font-weight:700;margin:10px 0 4px;">一、{板块 1 名}</div>
      <ul style="margin:0 0 6px;padding-left:20px;font-size:13px;color:#444;line-height:1.8;"><li>{脉络 bullet}</li></ul>
      <div style="font-size:14px;color:#444;font-weight:700;margin:10px 0 4px;">二、{多叶子节名}</div>
      <ul style="margin:0;padding-left:20px;font-size:13px;color:#444;line-height:1.8;">
        <li><strong>{子板块 A}</strong>：{脉络要点}</li>
        <li><strong>{子板块 B}</strong>：{脉络要点}</li>
      </ul>
    </div>
  </div>

  <!-- ③ 正文：各板块（仅核心事件，脉络已在上方全局脉络区） -->
  <div style="padding:24px 32px;">

    <!-- 单叶子节示例 -->
    <h2 id="sec-1" style="font-size:22px;color:#1e3a8a;margin:32px 0 16px;padding-bottom:8px;border-bottom:2px solid #1e3a8a;">一、{板块 1 名}</h2>

    <!-- 核心事件 -->
    <div style="font-size:14px;color:#6b7280;margin:24px 0 8px;letter-spacing:0.05em;">▸ 核心事件（按日期降序）</div>

    <!-- 每个事件 = 一个卡片 -->
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;padding:16px 20px;margin:12px 0;">
      <div style="font-size:12px;color:#3b82f6;font-weight:600;letter-spacing:0.05em;">{YYYY-MM-DD}</div>
      <h3 style="font-size:17px;margin:4px 0 12px;color:#111827;">{事件标题}</h3>
      <div style="font-size:13px;margin-bottom:8px;"><strong style="color:#374151;">URL：</strong><a href="{原文链接}" style="color:#3b82f6;text-decoration:none;word-break:break-all;">{原文链接}</a></div>
      <div style="font-size:14px;margin-bottom:8px;"><strong style="color:#374151;">背景：</strong>{背景文字}</div>
      <div style="font-size:14px;margin-bottom:8px;"><strong style="color:#374151;">要点：</strong>
        <ul style="margin:4px 0 0;padding-left:20px;">
          <li style="margin-bottom:4px;">{要点 1}</li>
          <li style="margin-bottom:4px;">{要点 2}</li>
        </ul>
      </div>
      <div style="font-size:14px;background:#fefce8;border-left:3px solid #facc15;padding:8px 12px;margin-top:10px;border-radius:0 4px 4px 0;"><strong style="color:#854d0e;">启发：</strong>{启发文字}</div>
    </div>

    <!-- 多叶子节示例 -->
    <h2 id="sec-2" style="font-size:22px;color:#1e3a8a;margin:32px 0 16px;padding-bottom:8px;border-bottom:2px solid #1e3a8a;">二、{多叶子节名}</h2>

    <h3 id="sec-2-1" style="font-size:18px;color:#1e40af;margin:24px 0 12px;padding-left:12px;border-left:4px solid #3b82f6;">2.1 {子板块 A}</h3>
    <!-- 同上：仅事件卡片（该子板块脉络已在顶部「本期全局脉络」区） -->

    <h3 id="sec-2-2" style="font-size:18px;color:#1e40af;margin:24px 0 12px;padding-left:12px;border-left:4px solid #3b82f6;">2.2 {子板块 B}</h3>
    <!-- 同上 -->

  </div>

  <!-- ④ 全月覆盖速览（仅月刊 HTML） -->
  <div style="padding:24px 32px;background:#f9fafb;border-top:1px solid #e5e7eb;">
    <h2 style="font-size:18px;color:#374151;margin:0 0 12px;">全月覆盖速览</h2>
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <thead>
        <tr style="background:#e5e7eb;">
          <th style="padding:8px 10px;text-align:left;border:1px solid #d1d5db;">叶子板块</th>
          <th style="padding:8px 10px;text-align:left;border:1px solid #d1d5db;">候选 → 入选</th>
          <th style="padding:8px 10px;text-align:left;border:1px solid #d1d5db;">跑通源 / 规则列源</th>
          <th style="padding:8px 10px;text-align:left;border:1px solid #d1d5db;">主要降级源</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="padding:8px 10px;border:1px solid #e5e7eb;">{板块}</td>...</tr>
      </tbody>
    </table>
  </div>

  <!-- ⑤ 页脚 -->
  <div style="padding:16px 32px;background:#1f2937;color:#9ca3af;font-size:12px;text-align:center;">
    本月刊由 magazine-collect skill 自动汇总 · 单板块深读请打开 <code style="background:#374151;padding:2px 6px;border-radius:3px;color:#d1d5db;">{output_path}</code>
  </div>

</div>

</body>
</html>
````

---

## 关键样式片段速查

### 海报 banner（顶部）

```html
<div style="background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 60%,#06b6d4 100%);padding:36px 32px;color:#ffffff;">
  <div style="font-size:14px;opacity:0.85;letter-spacing:0.1em;">MAGAZINE / {YYYY-MM}</div>
  <h1 style="margin:8px 0 4px;font-size:30px;font-weight:700;">{领域}动态</h1>
  <div style="font-size:14px;opacity:0.85;">{start} ~ {end}</div>
</div>
```

**配色策略**：深蓝→蓝→青的渐变是技术感 + 阅读友好的组合。如果是某个具体领域（如安全），可以换主色（绿/紫），但保持渐变结构。

### 边框（外层卡片）

```html
<div style="max-width:800px;margin:0 auto;background:#fff;border:1px solid #e1e4ea;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);overflow:hidden;">
  <!-- 全文 -->
</div>
```

注意：`box-shadow` 在部分老 Outlook 不支持但会优雅降级（变成无阴影），不影响内容。`overflow:hidden` 让 banner 的圆角不溢出。

### 本期全局脉络 callout（汇总各板块脉络，紧跟目录、领先正文）

整张卡片放在目录之后、所有板块正文之前；内部按 section 分组——单叶子节用小标题 + bullet，多叶子节用 `<strong>子板块名</strong>：…` 收敛成概览。各板块小节里**不再单独放脉络 callout**。

```html
<div id="overview" style="background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:18px 22px;margin:16px 0;">
  <div style="font-size:16px;color:#8a6d1a;font-weight:700;">🎯 本期全局脉络</div>
  <div style="font-size:14px;color:#444;font-weight:700;margin-top:10px;">一、{板块名}</div>
  <ul style="font-size:13px;"><li>{脉络 bullet}</li></ul>
  <div style="font-size:14px;color:#444;font-weight:700;margin-top:10px;">三、{多叶子节名}</div>
  <ul style="font-size:13px;"><li><strong>{子板块}</strong>：{脉络要点}</li></ul>
</div>
```

### 启发块（高亮收尾）

```html
<div style="background:#fefce8;border-left:3px solid #facc15;padding:8px 12px;margin-top:10px;border-radius:0 4px 4px 0;">
  <strong style="color:#854d0e;">启发：</strong>{actionable 内容}
</div>
```

每个事件卡片末尾用浅黄色 callout 突出"启发"段，让读者快速扫到 actionable 部分。

### 事件标签（日期）

```html
<div style="font-size:12px;color:#3b82f6;font-weight:600;letter-spacing:0.05em;">{YYYY-MM-DD}</div>
```

---

## 月刊 HTML 结构要求

`mode=html` **只产月刊级 HTML**（单板块阅读用 md 即可，不为单板块单独出 HTML）。月刊 HTML 必含：

- 海报 banner 标题 = `{领域}动态`（如"编译技术动态"、"推荐系统动态"）
- **目录必需**（首项为「本期全局脉络」，其后 K 个叶子板块）
- **「本期全局脉络」callout 必需**：紧跟目录、领先所有正文，汇总各板块核心脉络（单叶子节小标题 + bullet，多叶子节子板块收敛）；各板块小节内不再单独放脉络 callout
- 末尾「全月覆盖速览」表格
- 多叶子节子板块用 `N.M` 序号 h3 标题（与 md 月刊一致）
- 1:1 内嵌月刊 md 的所有事件（含完整三段式 + URL）

---

## markdown → HTML 转换约定

LLM 直接转换，不写脚本。常见 md 元素对应 HTML：

| Markdown | HTML 模式 |
|---|---|
| `# 标题` | `<h1 style="...">` |
| `## 本期全局脉络` | 顶部 `<div id="overview">` 高亮 callout（在目录之后、正文之前） |
| `## 一、…` | `<h2 id="sec-N" style="...">` |
| `### 3.1 …` | `<h3 id="sec-3-1" style="...">` |
| `#### YYYY-MM-DD ｜ 标题` | 事件卡片 `<div>...</div>`，标题用 `<h3>` |
| `- **URL**：<url>` | `<div><strong>URL：</strong><a href="">...</a></div>` |
| `- **要点**：` 多行 | `<div><strong>要点：</strong><ul>...</ul></div>` |
| `- **启发**：…` | 浅黄 callout `<div>` |
| `> 引文` | `<blockquote style="border-left:3px solid #d1d5db;padding-left:12px;color:#6b7280;">` |
| 表格 | `<table>` 内联 `border-collapse:collapse;` |
| `**粗体**` | `<strong>` |
| `` `代码` `` | `<code style="background:#f3f4f6;padding:1px 5px;border-radius:3px;font-family:monospace;font-size:90%;">` |

**链接（URL）**：`href` 必须是绝对路径（`https://...`）或邮件内可解析的锚点（`#sec-N`）；不要保留 `./<path>.md` 这种相对 md 路径（邮件客户端无法解析）。

---

## 反例

### 反例 1：用外部 stylesheet 或 `<style>` 块

```html
<!-- 不要 -->
<link rel="stylesheet" href="style.css">
<style> .card { background: #fff; } </style>
```

**Gmail 会剥离 `<style>` 块、`<link>` 完全无法加载**。所有样式必须内联到元素 `style="..."` 属性。

### 反例 2：引用外部图片 / Web Font

```html
<!-- 不要 -->
<img src="https://example.com/logo.png">
<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
```

企业邮件防火墙拦截外链，远程图片在很多客户端默认不显示。所有视觉要靠 CSS 实现，字体走系统 font fallback。

### 反例 3：保留 markdown 相对路径

```html
<!-- 不要 -->
<a href="./llvm/llvm-2026-02-23_2026-05-23.md">详见</a>
```

邮件客户端无法解析 `.md`，也不会解析跨文件相对路径。HTML 月刊里的"详见独立 digest"链接应该删除（HTML 月刊本身已经内嵌全部内容），或者写成绝对 URL（如果有 web 部署）。

### 反例 4：用 flex/grid 复杂布局

```html
<!-- 不要 -->
<div style="display:flex;justify-content:space-between;">
```

老 Outlook（Windows 10/11 desktop client）渲染引擎用的是 Word，对 flex/grid 支持差。复杂布局必须用 `<table>`。

### 反例 5：为了控制体积而精简 HTML

**不要**：为了让 HTML 小于 Gmail 102KB 截断阈值，自作主张精简事件细节、用"其余 X 条事件见 md"占位。这违反"1:1 视觉化"原则。

**要**：HTML 始终输出完整版（与 md 1:1 对应）。Gmail 的 102KB 截断是邮件客户端行为，不是 skill 要替用户优化的事——读者点 "View entire message" 即可看完整内容；Outlook / Foxmail / 钉邮 / 飞书邮箱等多数客户端无此限制。

> Gmail 截断说明：HTML 体积超过 102KB 时，Gmail 会显示 "[Message clipped] View entire message" 提示，读者一键展开。如果团队主要用 Gmail 且不希望读者多点一次，用户可以自己把完整 HTML 当附件挂载、邮件正文另写一段精简版——但这是用户分发决策，不是 skill 行为。

---

## 与 markdown 月刊的关系

| 维度 | markdown 月刊 | HTML 月刊 |
|---|---|---|
| 触发模式 | `mode=magazine` | `mode=html`（要求月刊 md 已存在） |
| 文件路径 | `magazine-collect-output/<domain>-<start>_<end>/magazine-<start>_<end>.md` | `magazine-collect-output/<domain>-<start>_<end>/magazine-<start>_<end>.html` |
| 内容范围 | 完整月刊正文 | 1:1 视觉化 md 全部内容 + 海报 + 边框 |
| 用途 | 归档 / 阅读 / 二次编辑 | 邮件分发 / 浏览器查看 / 截图 |
| 链接形式 | 相对路径 `./<board>/<...>.md` | 绝对 URL 或 `#sec-N` 锚点 |
| 样式 | 无 | 内联 CSS（邮件兼容） |

**核心约束**：HTML 是 markdown 月刊的视觉版本，**不引入新内容**——所有事件、要点、启发都来自 md。这是保证 md 与 HTML 一致性的根本。
