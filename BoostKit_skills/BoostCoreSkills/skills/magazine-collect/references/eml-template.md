# `.eml` 邮件打包模板（`mode=eml` 专用）

本文档定义月刊 HTML 视觉版打包为 `.eml` 邮件文件的精确流程。Step 10 之前必读。

## 设计原则

1. **只做格式打包，不做内容生成。** HTML 内容由 Step 9 产出，本步只是把它套上 MIME 信封，让邮件客户端识别为"邮件"。
2. **不调 SMTP，不带凭据。** `.eml` 是本地静态文件，双击由用户的邮件客户端打开后再人工确认发送。skill 不掌握 SMTP 服务器、不存储任何邮箱密码。
3. **不预填发件人。** 让用户在邮件客户端里用其当前登录账号自动作为发件人，避免 skill 跑出来的 `.eml` 跨用户/跨账号时出现 From 不一致或被反垃圾标记。
4. **保留 plain text 兜底。** `multipart/alternative` 同时塞 `text/plain` 和 `text/html`，老旧客户端能看到一行说明，新客户端直接渲染 HTML。
5. **不依赖外部库。** 仅用 Python 标准库 `email.message.EmailMessage`——所有 MIME 编码（中文 Subject 的 base64、HTML 主体的 quoted-printable）由标准库处理。
6. **写一次性脚本，不要 hand-craft MIME。** 中文需要正确的 charset/transfer-encoding 协商，hand-craft 极易出错；用 `EmailMessage` API 让标准库生成正确的 envelope。

---

## 何时触发

- 用户说 **"做成邮件版 / 打包成 eml / 转邮件 / 邮件可直接发送"** 等 → `mode=eml`
- `mode=eml` **必须先有月刊 HTML**（即先跑过 `mode=html`，对应 `magazine-<start>_<end>.html` 已存在于"领域-窗口"根目录）
- 模式链条：`single` < `magazine` < `html` < `eml`，eml 自动包含所有前置步骤

---

## 输入与输出

| 项 | 路径 |
|---|---|
| 输入 HTML | `magazine-collect-output/<domain>-<start>_<end>/magazine-<start>_<end>.html` |
| 输出 `.eml` | `magazine-collect-output/<domain>-<start>_<end>/magazine-<start>_<end>.eml` |
| 打包脚本 | `magazine-collect-output/<domain>-<start>_<end>/build_eml.py`（与产物同目录，方便用户日后手动重跑） |

`.eml` 文件大小一般约为 HTML 的 1.5 倍（quoted-printable 对中文有 ~30% 膨胀）。

---

## 打包脚本模板

LLM 在 Step 10 用 `Write` 把下面的脚本写到 `build_eml.py`，把 `{SUBJECT}` 占位符替换为本期月刊的人话标题，然后用 `Bash` 跑一遍。除占位符外，**脚本主体不要改动**。

```python
#!/usr/bin/env python3
"""Wrap the magazine HTML into a ready-to-open .eml file."""

from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 找到同目录下的月刊 HTML（命名由 Step 9 固定，但保留 glob 以防多版本）
candidates = sorted(HERE.glob("magazine-*.html"))
assert candidates, f"no magazine-*.html found in {HERE}"
HTML_PATH = candidates[-1]
EML_PATH = HTML_PATH.with_suffix(".eml")

SUBJECT = "{SUBJECT}"       # 例：编译技术动态 2026-05(2026-02-23 ~ 2026-05-23)
FROM_ADDR = ""              # 留空：让邮件客户端用当前登录账号作为发件人
TO_ADDR = ""                # 留空：用户在客户端里填收件人

html = HTML_PATH.read_text(encoding="utf-8")

plain_fallback = (
    "本邮件为 HTML 杂志版面，请使用支持 HTML 的邮件客户端查看。\n"
    f"标题：{SUBJECT}\n"
)

msg = EmailMessage()
msg["Subject"] = SUBJECT
if FROM_ADDR:
    msg["From"] = FROM_ADDR
if TO_ADDR:
    msg["To"] = TO_ADDR
msg["Date"] = formatdate(localtime=True)
msg["Message-ID"] = make_msgid(domain="magazine.local")
msg.set_content(plain_fallback, subtype="plain", charset="utf-8")
msg.add_alternative(html, subtype="html", charset="utf-8")

EML_PATH.write_bytes(bytes(msg))
print(f"OK -> {EML_PATH}  ({EML_PATH.stat().st_size} bytes)")
```

### 占位符约定

| 占位符 | 替换为 | 示例 |
|---|---|---|
| `{SUBJECT}` | 月刊人话标题，与 HTML banner 主标一致；含期号或时间窗 | `编译技术动态 2026-05(2026-02-23 ~ 2026-05-23)` |

`FROM_ADDR` / `TO_ADDR` **保持留空字符串**，不要替换。

---

## 校验

跑完后用 `head -10` 看一眼 `.eml` 头部，应至少包含：

```
Subject: =?utf-8?b?...?= ...
Date: ...
Message-ID: <...@magazine.local>
MIME-Version: 1.0
Content-Type: multipart/alternative;
 boundary="..."
```

中文 Subject 一定是 `=?utf-8?b?...?=`（RFC 2047 编码）格式，不能是裸 UTF-8 字节——后者会让部分客户端显示为乱码。HTML 主体所在分段的 `Content-Transfer-Encoding` 一定是 `quoted-printable`（不是 `8bit`），否则 SMTP relay 时可能被截行。

---

## 邮件客户端兼容性提示

`.eml` 双击打开会跳进系统默认邮件客户端。**不同客户端对内联 CSS 的支持差异较大**，HTML 模板（见 `html-template.md`）已经在这一层做了大量兼容处理，但仍有少数特性会退化：

| 客户端 | 渲染引擎 | 已知问题 |
|---|---|---|
| Apple Mail（macOS / iOS） | WebKit | 全部支持，渲染最接近浏览器 |
| Foxmail（Win/Mac） | Chromium | 基本与浏览器一致 |
| Outlook 桌面版（Win） | **Word 引擎** | 不支持 `box-shadow`、`border-radius`（部分场景）；`linear-gradient` 背景可能退化为透明，banner 区块会变成纯色——但事件卡片、目录、callout 等都正常 |
| Outlook 网页版 / 新版 Outlook | Edge/Chromium | 全部支持 |
| 钉邮 / 飞书邮箱 | Chromium 内核 | 全部支持 |

> 如果团队主体是 Outlook 桌面版，需要让 banner 渐变背景也兼容——下一版 `html-template.md` 可以加 VML `<v:rect>` fallback。目前 banner 退化为纯色 `#1e3a8a` 并不影响信息阅读。

---

## 用户工作流（写在 Step 7 summary 里告诉用户）

1. 打开 Finder / 文件管理器，定位到 `magazine-<start>_<end>.eml`
2. **双击**它（或在 Mac 终端用 `open <path>`）
3. 系统默认邮件客户端弹出新邮件窗口：
   - 标题已预填
   - 发件人为当前登录账号（自动）
   - 正文为渲染后的月刊视觉版
4. 填收件人 / 抄送，必要时微调正文，点 **发送**

---

## 失败模式备忘

- **不要把 `From` 字段硬编码到脚本里。** 跨账号、跨用户跑这个 skill 都会撞上不一致问题。让客户端用当前登录账号最自然。
- **不要往 `.eml` 里塞附件**（除非用户显式要求）。月刊 HTML 是邮件正文（inline body），不是 attachment——加成附件会让收件人多一步"下载附件→双击打开"，违背"打开邮件直接看到杂志"的初衷。
- **不要用 `text/html` 单 part 邮件**，必须 `multipart/alternative`——避免部分企业反垃圾网关因"无 plain text 兜底"而降权或退信。
- **不要把 HTML 的 `<style>` 块剥到 `.eml` 头部的 CSS**——HTML 已经全 inline style（见 `html-template.md` 设计原则），不要再做"邮件 CSS 优化"的二次加工。
- **不要为 `.eml` 用 7bit 编码**。中文用 `quoted-printable`（标准库自动处理）；强行 8bit 会让一部分 SMTP relay 报错。
- **不要在 skill 里写 SMTP 发送代码。** 自动发送涉及凭据与组织邮件策略，远超 skill 范围。skill 的边界止于"生成本地 .eml 文件"。
