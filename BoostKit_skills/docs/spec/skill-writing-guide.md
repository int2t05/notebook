<br />

# Boostkit Skill 编写指南

***

## 目录

- [1. 概述](#1-概述)
- [2. 核心概念与设计原则](#2-核心概念与设计原则)
- [3. 文件结构与格式规范](#3-文件结构与格式规范)
- [4. SKILL.md 编写规范](#4-skillmd-编写规范)
- [5. 正文编写与设计模式](#5-正文编写与设计模式)
- [6. 脚本开发规范](#6-脚本开发规范)
- [7. 多 Skill 管理](#7-多-skill-管理)
- [8. Skill 质量检查机制](#8-skill-质量检查机制)
- [9. 测试、评估与迭代优化](#9-测试评估与迭代优化)
- [10. 描述优化与触发精度](#10-描述优化与触发精度)

***

## 1. 概述

### 1.1 文档定位

本指南是**鲲鹏 Boostkit 团队的 Skill 开发规范**，为团队成员在 Skill 的创建、编写、审查、管理和维护全生命周期中提供统一的规范性指导。本指南基于[开放 Skill 标准](https://agentskills.io/home)，结合鲲鹏 Boostkit 团队的实际业务场景和开发流程，将通用 Skill 规范转化为团队可落地执行的具体要求。

### 1.2 目标受众

| 角色            | 职责                     | 本指南的使用方式                                     |
| ------------- | ---------------------- | -------------------------------------------- |
| **Skill 开发者** | 负责 Skill 的设计、编写和实现     | 遵循本指南的编写规范、脚本开发规范和质量检查要求，确保 Skill 符合团队标准     |
| **Skill 审查者** | 负责 Skill 的质量审核和合规性检查   | 依据本指南的质量检查机制和评估流程，对提交的 Skill 进行系统性审查         |
| **Skill 管理者** | 负责 Skill 仓库的整体规划、分类和维护 | 按照本指南的多 Skill 管理规范，组织 Skill 目录结构、处理命名冲突和版本管理 |

### 1.3 适用范围

本指南适用于鲲鹏 Boostkit 团队内所有 Skill 的以下活动：

- **创建**：从需求分析到 Skill 目录搭建、SKILL.md 编写和脚本开发的完整流程
- **审查**：规范检查、功能完整性验证、安全性扫描和性能评估
- **管理**：多 Skill 的分类组织、命名唯一性保障、依赖管理和版本控制
- **维护**：测试评估、迭代优化、描述触发精度调优和故障排除

### 1.4 在团队开发流程中的定位

本指南在鲲鹏 Boostkit 团队开发流程中承担以下定位：

- **规范依据**：作为 Skill 开发各环节的规范性判据，所有 Skill 必须符合本指南的要求方可入库
- **协作基准**：为开发者、审查者和管理者提供统一的协作语言和评判标准，减少沟通成本
- **知识沉淀**：将团队在 Skill 开发中积累的经验、注意事项和最佳实践固化为可检索的规范文档

***

## 2. 核心概念与设计原则

### 2.1 三大核心原则

| 原则        | 说明                                                             | 单 Skill 体现                | 多 Skill 体现                      |
| --------- | -------------------------------------------------------------- | ------------------------- | ------------------------------- |
| **渐进式披露** | 三级信息加载：YAML frontmatter（始终加载）→ SKILL.md 正文（按需加载）→ 链接文件（按需发现） | 单个 Skill 内部按此层级组织内容       | 仓库 README 仅展示索引，详细内容在各 Skill 内部 |
| **可组合性**  | Skill 应能与其他 Skill 并行工作，不应假设自己是唯一可用的能力                          | description 中明确职责边界，不假设独占 | description 包含否定触发，工具调用隔离，避免冲突  |
| **可移植性**  | 同一 Skill 应在不同智能体平台上无需修改即可工作                                    | 不依赖特定平台的专有 API 或配置        | 仓库目录结构与平台无关，Skill 可独立提取使用      |

### 2.2 渐进式披露的 Token 成本

| 层级    | 加载内容             | 加载时机       | Token 成本                  |
| ----- | ---------------- | ---------- | ------------------------- |
| 1. 目录 | 名称 + 描述          | 会话启动时      | 每个 Skill 约 50-100 个 Token |
| 2. 指令 | 完整 `SKILL.md` 正文 | Skill 被激活时 | 建议不超过 5000 个 Token        |
| 3. 资源 | 脚本、参考文档、资产       | 指令引用时按需加载  | 视内容而定                     |

### 2.3 从真实专业知识出发

一个常见的误区是仅依靠大语言模型的通用训练知识来生成 Skill，而不提供领域特定的上下文。结果往往是模糊、通用的流程，而非让 Skill 真正有价值的特定模式、边界情况和约束。

有效的 Skill 应基于真实专业知识：

**从实际任务中提取**：在与智能体的对话中完成一个真实任务，过程中提供上下文、纠正和偏好，然后提取可复用的模式：

- 有效的步骤序列
- 做出的纠正
- 输入/输出格式
- 提供的上下文

**从现有项目制品中提炼**：当有一批现有知识时，可以将其输入大语言模型并要求提炼出 Skill。好的源材料包括：

- 内部文档、运维手册和风格指南
- API 规范、架构和配置文件
- 代码审查评论和问题跟踪
- 版本控制历史，特别是补丁和修复
- 真实的故障案例及其解决方案


***

## 3. 文件结构与格式规范

### 3.1 目录结构

一个 Skill 是一个目录，至少包含一个 `SKILL.md` 文件：

```
skill-name/
├── SKILL.md # 必需：元数据 + 指令
├── scripts/ # 可选：可执行代码
├── references/ # 可选：文档
├── assets/ # 可选：模板、资源
└── ... # 任何附加文件或目录
```


### 3.2 命名规则

| 对象           | 规则                           | 正确示例                             | 错误示例                                        |
| ------------ | ---------------------------- | -------------------------------- | ------------------------------------------- |
| 文件夹名         | kebab-case ，带功能描述            | `pdf-processing`、`data-analysis` | `PDF-Processing`、`pdf_processing`、`skill-1` |
| SKILL.md 文件名 | 必须精确为 `SKILL.md`（大小写敏感）      | `SKILL.md`                       | `SKILL.MD`、`skill.md`、`Skill.md`            |
| name 字段      | kebab-case ，与文件夹名匹配， 1-64 字符 | `my-cool-skill`                  | `My Cool Skill`、`my_cool_skill`             |

**name 字段的详细约束：**

- 仅包含 Unicode 小写字母数字字符（`a-z`、`0-9`）和连字符（`-`）
- 不能以连字符开头或结尾
- 不能包含连续连字符（`--`）
- 必须与父目录名称匹配
- 最长 64 个字符



### 3.3 禁止事项

- **禁止**在 Skill 文件夹内放置 `README.md`（所有文档应放入 `SKILL.md` 或 `references/`）
- **禁止**在 frontmatter 中使用 XML 尖括号（`<` `>`）
- **禁止**使用特定平台的保留字作为 Skill 名称前缀
- **禁止**在 Skill 文件夹内再放置子 Skill


### 3.4 可选目录详解

#### `scripts/`

包含智能体可以运行的可执行代码。脚本应满足以下要求：

- 自包含或明确声明依赖
- 提供有意义的错误提示
- 妥善处理边界情况

支持的语言取决于智能体实现。常见选项包括 Python、Bash 和 JavaScript。


#### `references/`

包含智能体按需读取的附加文档：

- `REFERENCE.md` - 详细的技术参考
- `FORMS.md` - 表单模板或结构化数据格式
- 领域特定文件（`finance.md`、`legal.md` 等）

保持各个参考文件聚焦。智能体按需加载这些文件，文件越小，占用的上下文越少。


#### `assets/`

包含静态资源：

- 模板（文档模板、配置模板）
- 图像（图表、示例）
- 数据文件（查找表、架构）


### 3.5 文件引用规范

引用 Skill 中的其他文件时，使用从 Skill 根目录开始的相对路径：

```markdown
详见[参考指南](references/REFERENCE.md)。

运行提取脚本：
scripts/extract.py
```

保持文件引用从 `SKILL.md` 开始一层深。避免深度嵌套的引用链。

***

## 4. SKILL.md 编写规范

### 4.1 整体结构

`SKILL.md` 文件必须包含 YAML frontmatter，后跟 Markdown 内容：

```markdown
---
name: skill-name
description: Skill 的功能及适用场景描述。
license: Apache-2.0
compatibility: Requires Python 3.14+ and uv
metadata:
 author: example-org
 version: "1.0"
 category: "domain-database"
 tags: [task-software-dev]
allowed-tools: Bash(git:*) Bash(jq:*) Read
---

# Skill 标题

## 指令
（详细指令内容）

## 故障排除
（常见问题与解决方案）
```

### 4.2 Frontmatter 字段详解

#### 4.2.1 `name`（必需）

| 约束    | 说明                       |
| ----- | ------------------------ |
| 格式    | kebab-case ，仅小写字母、数字和连字符 |
| 长度    | 1-64 个字符                 |
| 起止    | 不能以连字符开头或结尾              |
| 连续连字符 | 不允许（`--`）                |
| 匹配    | 必须与父目录名称匹配               |

```yaml
# 有效
name: pdf-processing
name: data-analysis
name: code-review

# 无效
name: PDF-Processing # 不允许大写
name: -pdf # 不能以连字符开头
name: pdf--processing # 不允许连续连字符
```

#### 4.2.2 `description`（必需）—— 最重要的字段

description 是智能体决定是否加载 Skill 的核心依据。描述过于简略，Skill 在该触发时不会触发；描述过于宽泛，Skill 在不该触发时却会触发。

**约束：**

- 1-1024 个字符
- 禁止 XML 标签（`<` `>`）
- 应描述 Skill 的功能及适用场景
- 应包含有助于智能体识别相关任务的具体关键词

**结构公式：** `[功能描述] + [适用场景] + [关键能力]`

```yaml
# 好 - 具体且可操作
description: >
 从 PDF 文件中提取文本和表格，填写 PDF 表单，合并多个 PDF 。
 当处理 PDF 文档或用户提到 PDF 、表单或文档提取时使用。

# 好 - 包含触发短语和否定触发
description: >
 分析 CSV 和表格数据文件——计算汇总统计、添加派生列、生成图表和清理杂乱数据。
 当用户有 CSV 、 TSV 或 Excel 文件并想要探索、转换或可视化数据时使用此 Skill ，
 即使他们没有明确提到"CSV"或"分析"也适用。

# 差 - 太模糊
description: 帮助处理 PDF 。

# 差 - 缺少触发条件
description: 创建复杂的多页文档系统。
```

#### 4.2.3 `license`（可选）

指定 Skill 的许可证。建议保持简短（许可证名称或指向许可证文件的引用）。

```yaml
license: Proprietary. LICENSE.txt has complete terms
```

#### 4.2.4 `compatibility`（可选）

- 如果提供，必须为 1-500 个字符
- 仅在 Skill 有特定环境要求时才需包含
- 可以指明目标产品、所需系统包、网络访问需求等

```yaml
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

#### 4.2.5 `metadata`（可选）

- 从字符串键到字符串值的映射
- 客户端可使用此字段存储规范未定义的附加属性
- 建议键名具有一定的唯一性以避免意外冲突

```yaml
metadata:
 author: example-org
 version: "1.0"
 category: "domain-database"
 tags: [task-software-dev]
```

### 4.3 正文内容

Markdown 正文（ frontmatter 之后）包含 Skill 指令，没有格式限制。编写任何有助于智能体有效执行任务的内容即可。

**推荐章节：**

- 分步指令
- 输入和输出示例
- 常见边界情况

保持主 `SKILL.md` 在 500 行以内，将详细的参考材料移至单独的文件。

### 4.4 推荐结构模板

```markdown
---
name: "your-skill"
description: "[描述]"
---

# Skill 标题

## 指令

### 步骤 1: [第一个主要步骤]
清晰说明该步骤的具体内容。

操作：
1. [具体动作]
2. [具体动作]

### 步骤 2: [第二个主要步骤]
...

## 示例

示例 1: [常见场景]
用户说: "设置一个新的营销活动"
操作:
1. 获取现有活动
2. 使用提供的参数创建新活动
结果: 活动已创建，附带确认链接

## 陷阱

- [违反合理假设的情况]

## 故障排除

### [常见错误]
错误: [错误信息]
原因: [发生原因]
解决方案: [修复方法]
```


***

## 5. 正文编写与设计模式

### 5.1 上下文使用策略

一旦 Skill 激活，其完整的 `SKILL.md` 正文就会加载到智能体的上下文窗口中，与对话历史、系统上下文和其他活动 Skill 并存。Skill 中的每个 Token 都在与其他内容争夺智能体的注意力。

**补充智能体不具备的知识，省略其已掌握的常识**：专注于智能体在没有 Skill 的情况下不会知道的内容——项目特定的约定、领域特定的流程、非显而易见的边界情况，以及要使用的特定工具或 API。你不需要解释什么是 PDF、HTTP 如何工作或数据库迁移做什么。

**设计职责连贯的工作流**：确定 Skill 的覆盖范围，类似于定义函数的职责边界——应封装一个连贯的工作单元，且能与其他 Skill 良好组合。范围过窄的 Skill 会导致单个任务需要加载多个 Skill，增加上下文开销和指令冲突的风险；范围过宽的 Skill 则难以被精确触发。

**合理控制细节程度**：过于详尽的 Skill 可能适得其反——智能体难以从中提取关键信息，反而可能因不适用的指令而偏离正轨。简洁的分步指导配合一个可运行的示例，往往比详尽的文档更有效。

### 5.2 校准控制粒度

并非 Skill 的每个部分都需要同等严格的约束。应将指令的具体程度与任务的不确定性相匹配。

**当多种方法均可奏效时，给予智能体灵活选择的空间**。对于灵活性较高的指令，解释意图往往比生硬的规定更有效——理解指令目的后，智能体能做出更贴合上下文的决策。

**当操作容错性低、一致性要求高或必须严格按序执行时，应给出明确的具体指令**：

```markdown
## 数据库迁移

严格运行以下序列：

python scripts/migrate.py --verify --backup

不要修改命令或添加额外的标志。
```

大多数 Skill 兼具灵活与严格的部分，应分别调整各部分的约束粒度。

### 5.3 高效指令模式

#### 陷阱章节（ Gotchas ）

许多 Skill 中最有价值的内容是陷阱列表（ Gotchas ）——那些违反直觉的特定环境事实：

```markdown
## 陷阱

- `users` 表使用软删除。查询必须包含 `WHERE deleted_at IS NULL`，否则结果将包含已停用的账户。
- 用户 ID 在数据库中是 `user_id`，在认证服务中是 `uid`，在计费 API 中是 `accountId`。三者指的是同一个值。
- `/health` 端点只要 Web 服务器在运行就返回 200 ，即使数据库连接已断开。使用 `/ready` 检查完整服务健康。
```

将陷阱写在 `SKILL.md` 中，这样智能体在遇到相关情况之前就已获知注意事项。

#### 输出格式模板

当需要智能体按特定格式输出时，提供模板。这比用文字描述格式更可靠，因为智能体对具体结构的模式匹配能力更强：

```markdown
## 报告结构

使用此模板，根据具体分析调整章节：

# [分析标题]

## 执行摘要
[关键发现的一段概述]

## 关键发现
- 发现 1 及支持数据
- 发现 2 及支持数据

## 建议
1. 具体可操作的建议
2. 具体可操作的建议
```

#### 多步骤工作流检查清单

显式的检查清单有助于智能体跟踪进度、避免遗漏步骤：

```markdown
## 表单处理工作流

进度：
- [ ] 步骤 1: 分析表单（运行 `scripts/analyze_form.py`）
- [ ] 步骤 2: 创建字段映射（编辑 `fields.json`）
- [ ] 步骤 3: 验证映射（运行 `scripts/validate_fields.py`）
- [ ] 步骤 4: 填写表单（运行 `scripts/fill_form.py`）
- [ ] 步骤 5: 验证输出（运行 `scripts/verify_output.py`）
```
#### 验证循环

指示智能体在继续下一步之前，先验证当前步骤的结果：

```markdown
## 编辑工作流

1. 进行编辑
2. 运行验证：`python scripts/validate.py output/`
3. 如果验证失败：
 - 查看错误消息
 - 修复问题
 - 再次运行验证
4. 仅在验证通过时继续
```

#### 计划-验证-执行

对于批量操作或不可逆操作，让智能体先以结构化格式制定中间计划，再对照事实来源验证，最后执行：

```markdown
## PDF 表单填写

1. 提取表单字段：`python scripts/analyze_form.py input.pdf` → `form_fields.json`
2. 创建 `field_values.json`，将每个字段名映射到其预期值
3. 验证：`python scripts/validate_fields.py form_fields.json field_values.json`
4. 如果验证失败，修改 `field_values.json` 并重新验证
5. 填写表单：`python scripts/fill_form.py input.pdf field_values.json output.pdf`
```

#### 给出默认方案而非罗列选项

当多种工具或方法都可能有效时，选择一个默认方案并简要提及替代方案，而不是将它们作为同等选项罗列：

```markdown
# 太多选项
你可以使用 pypdf 、 pdfplumber 、 PyMuPDF 或 pdf2image...

# 清晰的默认方案加备选方案
使用 pdfplumber 进行文本提取：

import pdfplumber

对于需要 OCR 的扫描 PDF ，改用 pdf2image 配合 pytesseract 。
```

#### 侧重方法而非结论

Skill 应教会智能体解决一类问题的方法，而非仅针对特定实例给出答案：

```markdown
# 特定答案 — 仅适用于该特定任务
将 `orders` 表连接到 `customers` 表的 `customer_id`，
筛选 `region = 'EMEA'`，并对 `amount` 列求和。

# 可复用方法 — 适用于任何分析查询
1. 从 `references/schema.yaml` 读取架构以找到相关表
2. 使用 `_id` 外键约定连接表
3. 将用户请求中的任何筛选器应用为 WHERE 子句
4. 按需聚合数值列并格式化为 Markdown 表格
```

### 5.4 编写风格建议

- **解释原因**：尽量解释每条指令背后的原因。大语言模型理解指令目的后，能做出更贴合上下文的决策
- **保持 Skill 精简**：更少、更精准的指令往往胜过面面俱到的规则
- **从真实执行中提炼**：阅读智能体的执行步骤，而不仅仅是最终输出。如果智能体在无效步骤上浪费时间，应考虑简化或删除相关指令

***

## 6. 脚本开发规范

### 6.1 一次性命令

当现有包已经满足需求时，可以直接在 `SKILL.md` 指令中引用，无需 `scripts/` 目录：

| 工具         | 语言         | 命令示例                                                |
| ---------- | ---------- | --------------------------------------------------- |
| `uvx`      | Python     | `uvx ruff@0.8.0 check .`                            |
| `pipx`     | Python     | `pipx run 'black==24.10.0' .`                       |
| `npx`      | JavaScript | `npx eslint@9 --fix .`                              |
| `bunx`     | Bun        | `bunx eslint@9 --fix .`                             |
| `deno run` | Deno       | `deno run npm:create-vite@6 my-app`                 |
| `go run`   | Go         | `go run golang.org/x/tools/cmd/goimports@v0.28.0 .` |

**提示：**

- 固定版本（如 `npx eslint@9.0.0`），确保命令行为在不同运行间保持一致
- 在 `SKILL.md` 中说明前提条件（如"需要 Node.js 18+"）
- 复杂命令应移入脚本

### 6.2 面向智能体调用的脚本设计

当智能体运行脚本时，它通过读取 stdout 和 stderr 来决定下一步行为。以下设计原则可使脚本更便于智能体调用：

#### 避免交互式提示

这是强制要求。智能体通常在非交互式 shell 中运行，无法响应 TTY 提示、密码对话框或确认菜单。等待交互式输入的脚本会无限期挂起。所有输入应通过命令行标志、环境变量或 stdin 接收。

#### 使用 `--help` 记录用法

`--help` 输出是智能体了解脚本接口的主要方式。包含简要描述、可用标志和使用示例。

#### 编写有用的错误消息

智能体收到错误信息后，错误消息的内容直接决定其下一步的修正策略：

```
错误：--format 必须是以下之一： json, csv, table。收到："xml"
```

#### 使用结构化输出

优先使用结构化格式——JSON、CSV、TSV——而非自由格式文本。将结构化数据输出到 stdout，将进度消息、警告和其他诊断信息输出到 stderr。

#### 其他考虑

- **幂等性**：智能体可能会重试命令。"若不存在则创建"比"创建时遇重复则报错"更安全
- **输入约束**：用明确的错误拒绝模糊输入，而非猜测用户意图
- **试运行支持**：对于破坏性或有状态操作，`--dry-run` 标志可让智能体预览操作效果
- **有意义的退出代码**：为不同的失败类型使用不同的退出代码
- **输出规模可控**：默认输出摘要或合理限制条数，支持 `--offset` 等标志以便智能体按需获取更多信息

### 6.3 从 SKILL.md 引用脚本

使用从 Skill 目录根开始的相对路径引用附带的文件：

````markdown
## 可用脚本

- **`scripts/validate.sh`** — 验证配置文件
- **`scripts/process.py`** — 处理输入数据

## 工作流

1. 运行验证脚本：
 ```bash
 bash scripts/validate.sh "$INPUT_FILE"
```

2. 处理结果：

```bash
python3 scripts/process.py --input results.json
```

````

***

## 7. 多 Skill 管理

### 7.1 小规模场景（ Skill 数量 < 20 个）

当 Skill 数量较少时，在代码仓中采用扁平化的目录结构，在 skills 目录下直接存放各 Skill 子目录：

```
<code_repo>/skills/ # Skill 根目录
├── pdf-processing/ # PDF 处理 Skill
│ ├── SKILL.md
│ └── scripts/
│ └── extract.py
├── data-analysis/ # 数据分析 Skill
│ ├── SKILL.md
│ └── references/
│ └── schema.yaml
├── code-review/ # 代码审查 Skill
  └── SKILL.md
```

**Skill 发现路径**：智能体在会话启动时扫描以下目录：

| 范围 | 路径 | 用途 |
| --- | --- | --- |
| 项目级 | `<project>/.agents/skills/` | 跨客户端互操作性 |
| 项目级 | `<project>/.<your-client>/skills/` | 客户端原生位置 |
| 用户级 | `~/.agents/skills/` | 跨客户端互操作性 |
| 用户级 | `~/.<your-client>/skills/` | 客户端原生位置 |

`.agents/skills/` 路径已成为跨客户端 Skill 共享的通用约定。

### 7.2 大规模场景（ Skill 数量达几十、上百甚至数百个）

当 Skill 数量增长到数十、上百甚至数百个时，扁平结构变得难以管理。应按 Skill 主要用途进行分类存放：

```
skills-repo/ # 仓库根目录
├── README.md # 仓库级说明（面向人类访客）
├── LICENSE # 仓库级许可证
├── task/ # 作业类
│ ├── system-design/ # 系统设计
│ ├── software-dev/ # 软件开发
│ └── ...
├── domain/ # 业务类
│ ├── database/ # 数据库相关
│ ├── bigdata/ # 大数据相关
│ ├── cloud/ # 云计算、容器相关
│ ├── lib/ # 基础库相关
│ ├── media/ # 多媒体相关
│ └── ...
├── utility/ # 工具类
│ ├── vcs/ # Git 工作流、提交消息生成
│ ├── doc/ # 文档处理类
│ └── ...
└── tests/ # 可选 - 仓库级测试
```

**分类方案**：

Skill 按主要用途分为三大类，每个大类包含多个子类，分类标识通过 `metadata.category` 字段标注：

| 大类 | 目录名 | 子类示例 | 说明 |
| --- | --- | --- | --- |
| **作业类** | `task/` | `system-design`（系统设计）、`software-dev`（软件开发）等 | 面向开发流程中具体作业环境的 Skill ，提升各个环节的效率和质量 |
| **业务类** | `domain/` | `database`（数据库）、`bigdata`（大数据）、`cloud`（云计算/容器）、`lib`（基础库）、`media`（多媒体）等 | 面向特定产品领域或业务场景的 Skill ，封装领域专有知识和操作流程 |
| **工具类** | `utility/` | `vcs`（Git 工作流/提交消息生成）、`doc`（文档处理）等 | 面向通用工具操作的 Skill ，不依赖特定业务领域，可跨团队复用 |

**分类规则**：

- **规则一**：分类标识通过 `metadata.category` 字段标注，值必须与所在分类目录名一致
- **规则二**：当 Skill 跨多个分类时，必须选择其最主要的用途作为 `metadata.category` 标识，通过 `metadata.tags` 字段标注其他相关分类

```yaml
# 示例：一个以数据库领域知识为主、同时涉及软件开发流程的 Skill
# 该 Skill 位于 domain/database/ 目录下
metadata:
  category: "domain-database"
  tags: ["task-software-dev"]
```

**分类判断指引**：

通过以下三个问题确定 Skill 所属大类：

**问题 1：Skill 的核心价值是什么？**

| 核心价值 | 分类 |
| --- | --- |
| 封装特定领域知识 | 业务类（domain） |
| 提供通用工程方法，例如代码审查、测试生成 | 作业类（task） |
| 提供工具操作能力（如文档处理、Git 使用） | 工具类（utility） |

**问题 2：Skill 的使用范围？**

| 使用范围 | 分类 |
| --- | --- |
| 仅限制特定产品/领域使用 | 业务类（domain） |
| 按作业流程阶段适用（设计/开发/测试） | 作业类（task） |
| 不依赖特定领域，任何团队都可以使用 | 工具类（utility） |

**问题 3：如果去掉领域知识，Skill 还有价值吗？**

| 回答 | 分类 |
| --- | --- |
| 没有 | 业务类（domain） |
| 有 | 作业类（task） |
| 不涉及领域知识 | 工具类（utility） |

### 7.3 避免多 Skill 冲突的策略

当仓库中存在多个 Skill 时，应通过以下机制确保它们各司其职、互不干扰：

1. **description 边界划分**：使用否定触发
2. **工具调用隔离**：明确各自调用的工具子集
3. **metadata 标签辅助区分**：`metadata.category` 必须与所在分类目录名一致


### 7.4 仓库级 README 规范

仓库根目录的 `README.md` 应包含分类索引和 Skill 清单，列出所有 Skill 的名称、路径、说明和依赖关系。

***

## 8. Skill 质量检查机制

### 8.1 功能完整性验证

#### skills-ref 

- **简介**： skills-ref 是 Agent Skills 官方提供的参考验证库，用于验证 Skill 的 `SKILL.md` frontmatter 是否有效且符合所有命名约定
- **安装**：

```bash
# 使用 npx 直接运行（无需安装）
npx skills-ref validate ./my-skill
```

- **使用方法**：

```bash
# 验证 Skill
skills-ref validate ./my-skill

# 读取 Skill 属性（输出 JSON ）
skills-ref read-properties ./my-skill

# 生成智能体提示的 <available_skills> XML
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

- **适用场景**：验证 SKILL.md frontmatter 格式、name 字段合规性、description 字段有效性

### 8.2 安全性漏洞扫描

Skill 安全性检查应关注以下方面：

#### Frontmatter 安全

- **禁止 XML 尖括号**：frontmatter 中不允许 `<` `>`，因为 frontmatter 会出现在系统提示中，恶意内容可能注入指令
- **占位符检测**：扫描 name、description 和正文中是否包含 `TODO`、`FIXME`、`TBD`、`[PLACEHOLDER]` 等未完成的临时标记

#### 脚本安全

- **敏感信息扫描**：检查脚本中是否包含硬编码的 API 密钥、密码或 Token
- **危险命令检测**：检查 Shell 脚本中的 `rm -rf`、`chmod 777` 等危险命令
- **依赖安全性**：使用 `pip audit` 或 `npm audit` 检查依赖包的已知漏洞

#### skill-scanner（自动化安全扫描工具）

- **简介**：[skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) 是 Cisco AI Defense 团队开源的 AI Agent Skill 安全扫描工具，用于检测提示注入、数据泄露和恶意代码模式。它结合了基于模式的检测（YAML + YARA）、LLM 语义分析和行为数据流分析，在最大化威胁检测覆盖率的同时尽可能减少误报

- **重要提示**：skill-scanner 提供的是尽力检测（best-effort），而非全面覆盖。扫描无发现不代表 Skill 不存在安全风险，人工审查仍然必不可少

- **核心能力**：

| 检测引擎 | 说明 |
| --- | --- |
| 静态分析 | 基于 YAML + YARA 规则的签名检测，识别已知威胁模式 |
| 行为数据流分析 | 追踪数据在 Skill 中的流动路径，检测数据泄露和异常行为 |
| LLM 语义分析 | 使用大语言模型判断 Skill 内容的语义意图，发现绕过签名检测的隐蔽威胁 |
| 云端扫描 | 可选集成 VirusTotal 二进制扫描和 Cisco AI Defense 云服务 |

- **安装**：

```bash
# 使用 uv（推荐）
uv pip install cisco-ai-skill-scanner

# 使用 pip
pip install cisco-ai-skill-scanner

# 如需 AWS Bedrock / Google Gemini / Azure OpenAI 等 LLM 后端支持
pip install cisco-ai-skill-scanner[all]
```

- **使用方法**：

```bash
# 基础扫描（静态分析 + 字节码分析 + 管道分析）
skill-scanner scan /path/to/skill

# 启用行为数据流分析
skill-scanner scan /path/to/skill --use-behavioral

# 启用所有检测引擎
skill-scanner scan /path/to/skill --use-behavioral --use-llm --use-aidefense

# 启用 LLM 分析 + 元分析器（减少误报）
skill-scanner scan /path/to/skill --use-llm --enable-meta

# LLM 多轮共识扫描（多次运行取多数一致结果，提高可靠性）
skill-scanner scan /path/to/skill --use-llm --llm-consensus-runs 3

# 递归扫描多个 Skill
skill-scanner scan-all /path/to/skills --recursive --use-behavioral

# 输出 SARIF 格式（用于 GitHub Code Scanning）
skill-scanner scan /path/to/skill --format sarif --output results.sarif
```

- **环境配置**（可选，用于 LLM 分析器和元分析器）：

```bash
# 配置 LLM 分析器使用的 API
export SKILL_SCANNER_LLM_API_KEY="your_api_key"
export SKILL_SCANNER_LLM_MODEL="claude-3-5-sonnet-20241022"

# 配置 VirusTotal 二进制扫描
export VIRUSTOTAL_API_KEY="your_virustotal_api_key"

# 配置 Cisco AI Defense 云服务
export AI_DEFENSE_API_KEY="your_aidefense_api_key"
```

### 8.3 性能优化建议

#### 上下文大小优化

- 保持 `SKILL.md` 在 500 行以内，建议不超过 5000 个 Token
- 将详细参考材料移至 `references/` 目录
- 使用渐进式披露：告诉智能体何时加载每个文件，而非一次加载所有内容

#### 触发精度优化

- 完善 description 中的细节和关键词，确保 Skill 在应触发时正确触发
- 控制 description 的范围和针对性，避免 Skill 在不应触发时误触发
- 使用否定触发明确边界
- 定期运行触发评估测试

#### 脚本性能优化

- 使用缓存机制避免重复计算
- 默认输出摘要，支持分页参数
- 对于大型输出，使用 `--output` 标志写入文件而非输出到 stdout

***

## 9. 测试、评估与迭代优化

### 9.1 设计测试用例

一个测试用例包含三个部分：

- **提示词**：一个真实的用户消息——用户真正会输入的内容
- **预期输出**：对成功结果的清晰描述
- **输入文件**（可选）： Skill 需要处理的文件

将测试用例存储在 Skill 目录的 `evals/evals.json` 中：

```json
{
 "skill_name": "csv-analyzer",
 "evals": [
 {
 "id": 1,
 "prompt": "我有一个 CSV 文件，包含月度销售数据，在 data/sales_2025.csv 中。你能找出收入最高的 3 个月并制作条形图吗？",
 "expected_output": "一个条形图图像，显示收入最高的 3 个月，带有标签轴和数值。",
 "files": ["evals/files/sales_2025.csv"]
 }
 ]
}
```

**编写好测试提示词的技巧：**

- **从 2-3 个测试用例开始**：在看到第一轮结果前不必过度投入，后续可以扩展
- **变化提示词**：使用不同的措辞、详细程度和正式程度。有些提示词应随意（"嘿，能帮我清理下这个 csv 吗"），有些应精确（"解析 data/input.csv 中的 CSV，删除 B 列为空的行，将结果写入 data/output.csv"）
- **覆盖边界情况**：至少包含一个测试边界条件的提示词——格式异常的输入、不寻常的请求，或 Skill 指令可能产生歧义的情况
- **使用真实的上下文**：真实用户会提及文件路径、列名和个人背景。像"处理这个数据"这样的提示词太模糊，无法测试任何有用的东西

先不必定义具体的通过/失败判定——只需编写提示词和预期输出。待第一轮运行完成后，再添加详细的检查项（即断言）。

### 9.2 运行评估

核心模式是对每个测试用例运行两次：一次**有 Skill**，一次**无 Skill**（基线）。由此获得对比基准。

#### 工作区结构

在 Skill 目录旁边组织一个工作区目录。每轮完整的评估循环对应一个 `iteration-N/` 目录。其中，每个测试用例对应一个评估目录，包含 `with_skill/` 和 `without_skill/` 子目录：

```
csv-analyzer/
├── SKILL.md
└── evals/
    └── evals.json
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/       # 运行产生的文件
    │   │   ├── timing.json    # Token 数和耗时
    │   │   └── grading.json   # 断言结果
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── eval-clean-missing-emails/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json         # 汇总统计
```

手工编写的主要文件是 `evals/evals.json`。其余 JSON 文件（`grading.json`、`timing.json`、`benchmark.json`）在评估过程中由智能体、脚本或人工生成。

#### 启动运行

每次评估运行应从干净的上下文开始——不受前次运行或 Skill 开发过程的残留状态影响。这确保智能体仅遵循 `SKILL.md` 中的指令。在支持子智能体的环境中（如 Claude Code），这种隔离是自然而然的：每个子任务从全新状态开始。没有子智能体时，应为每次运行使用独立的会话。

每次运行需提供：
- Skill 路径（基线运行则不提供）
- 测试提示词
- 输入文件
- 输出目录

以下是单次有 Skill 运行的指令示例：

```
执行此任务：
- Skill 路径: /path/to/csv-analyzer
- 任务: I have a CSV of monthly sales data in data/sales_2025.csv.
  Can you find the top 3 months by revenue and make a bar chart?
- 输入文件: evals/files/sales_2025.csv
- 保存输出至: csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/
```

基线运行使用相同的提示词但不提供 Skill 路径，保存到 `without_skill/outputs/`。

改进现有 Skill 时，应使用前一个版本作为基线。编辑前先做快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），将基线运行指向快照，并保存到 `old_skill/outputs/` 而非 `without_skill/`。

#### 记录耗时数据

耗时数据可用于比较 Skill 相对于基线的时间和 Token 开销——大幅提升输出质量但 Token 消耗增加三倍的 Skill，与既好又省的 Skill，二者的取舍不同。每次运行完成时，记录 Token 数和耗时：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

### 9.3 编写断言

断言是对输出应包含或满足内容的可验证描述。在看到第一轮输出后再添加——通常在 Skill 实际运行之前，你并不清楚"好的输出"具体长什么样。

**好的断言：**

- "输出文件是有效的 JSON" —— 可编程验证
- "条形图有标签轴" —— 具体且可观察
- "报告包含至少 3 条建议" —— 可计数

**弱的断言：**

- "输出是好的" —— 太模糊，无法评分
- "输出使用确切短语'Total Revenue: $X'" —— 过于死板；措辞不同但同样正确的输出会被判为失败

并非所有内容都需要断言。某些品质——如写作风格、视觉设计、输出是否"感觉对"——很难拆解为通过/失败的二元判断。这些更适合在人工审查中发现。断言应只用于可以客观检查的内容。

将断言添加到 `evals/evals.json` 中的每个测试用例：

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"],
      "assertions": [
        "The output includes a bar chart image file",
        "The chart shows exactly 3 months",
        "Both axes are labeled",
        "The chart title or caption mentions revenue"
      ]
    }
  ]
}
```

### 9.4 评分输出

评分是指将每条断言与实际输出逐一对照，判定是否满足，并记录 **PASS** 或 **FAIL** 及具体证据。证据应引用或参考输出内容，而非仅陈述意见。

最简单的方法是将输出和断言交给 LLM 并要求其逐条评估。对于可以通过代码检查的断言（有效 JSON、正确的行数、文件存在且尺寸符合预期），应使用验证脚本——脚本在机械性检查方面比 LLM 判断更可靠，且可跨迭代复用。

```json
{
  "assertion_results": [
    {
      "text": "The output includes a bar chart image file",
      "passed": true,
      "evidence": "Found chart.png (45KB) in outputs directory"
    },
    {
      "text": "The chart shows exactly 3 months",
      "passed": true,
      "evidence": "Chart displays bars for March, July, and November"
    },
    {
      "text": "Both axes are labeled",
      "passed": false,
      "evidence": "Y-axis is labeled 'Revenue ($)' but X-axis has no label"
    },
    {
      "text": "The chart title or caption mentions revenue",
      "passed": true,
      "evidence": "Chart title reads 'Top 3 Months by Revenue'"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

**评分原则：**

- **PASS 判定必须有具体证据支撑**：例如断言要求"包含摘要"，而输出虽有"摘要"标题但内容只有一句模糊的话，则应判为 FAIL——有标题但无实质内容
- **审查断言本身，而不仅仅是结果**：评分时还需审查断言是否合理：是否过于宽松（无论 Skill 质量如何都能通过）、过于严苛（输出很好却仍然失败），或不可验证（仅凭输出无法判断）。在下一轮迭代中修正这些问题

### 9.5 汇总与分析结果

#### 汇总统计

当迭代中所有运行都评分完毕后，计算每种配置的汇总统计并保存到 `benchmark.json`（与评估目录并列，如 `csv-analyzer-workspace/iteration-1/benchmark.json`）：

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 },
      "tokens": { "mean": 3800, "stddev": 400 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 },
      "tokens": { "mean": 2100, "stddev": 300 }
    },
    "delta": {
      "pass_rate": 0.50,
      "time_seconds": 13.0,
      "tokens": 1700
    }
  }
}
```

delta 反映了 Skill 的代价（更多时间、更多 Token）和收益（更高的通过率）。增加 13 秒但通过率提高 50 个百分点的 Skill 可能值得接受；而 Token 消耗翻倍但通过率仅提高 2 个百分点的 Skill 可能得不偿失。

#### 分析模式

汇总统计可能掩盖重要的模式。计算基准数据后：

- **移除或替换在两种配置中都始终通过的断言**：这些断言不提供任何有用信息——模型在没有 Skill 的情况下也能处理。它们虚抬了有 Skill 时的通过率，却不能反映 Skill 的实际价值
- **调查在两种配置中都始终失败的断言**：要么断言有问题（要求模型做不到的事），要么测试用例太难，要么断言检查的方向不对。在下一轮迭代前修正这些
- **研究有 Skill 通过但无 Skill 失败的断言**：这正是 Skill 产生明确价值之处。理解原因——哪些指令或脚本起了作用？
- **结果不一致时收紧指令**：如果同一个评估有时通过有时失败（在基准数据中表现为高 stddev），可能是评估本身不稳定（对模型随机性敏感），也可能是 Skill 指令过于模糊，导致模型每次理解不同。添加示例或更具体的指导以减少歧义
- **检查时间和 Token 异常值**：如果某个评估耗时是其他评估的 3 倍，应阅读其执行记录（模型运行期间的完整操作日志）以定位瓶颈

### 9.6 迭代改进循环

评分和审查后，可从三个信号来源获取改进线索：

- **失败的断言**指向具体的差距——缺失的步骤、不清晰的指令，或 Skill 未处理的情况
- **人工反馈**指向更广泛的质量问题——方法错误、输出结构不佳，或 Skill 产出了技术上正确但无帮助的结果
- **执行记录**揭示问题根因。如果智能体忽略了某条指令，该指令可能存在歧义。如果智能体在无效步骤上浪费时间，那些指令可能需要简化或移除

将这些信号转化为 Skill 改进的最有效方法是：将三个信号来源——连同当前的 `SKILL.md`——一并提供给 LLM，要求其提出修改建议。LLM 能够综合失败断言、审查者意见和执行记录之间的关联模式，人工梳理这些关联会非常繁琐。

向 LLM 提供以下指导原则：

- **从反馈中提炼通用规律**：Skill 将被用于许多不同的提示词，而不仅仅是测试用例。修复应着眼于解决底层问题，而非针对特定示例打补丁
- **保持 Skill 精简**：更少、更好的指令往往胜过面面俱到的规则。如果执行记录显示存在无效操作（不必要的验证、不需要的中间输出），应移除相关指令。如果通过率在添加更多规则后趋于停滞，说明 Skill 可能被过度约束——尝试移除指令，看结果是否保持或改善
- **解释原因**：基于推理的指令（"做 X，因为 Y 往往导致 Z"）比生硬的指令（"始终做 X，永远不做 Y"）效果更好。模型在理解目的时更可靠地遵循指令
- **整合重复工作**：如果每次测试运行都独立编写了类似的辅助脚本（图表构建器、数据解析器），这说明应将这些脚本整合到 Skill 的 `scripts/` 目录中

**迭代循环：**

1. 将评估信号和当前 `SKILL.md` 一并提供给 LLM，要求其提出改进
2. 审查并应用修改
3. 在新的 `iteration-<N+1>/` 目录中重新运行所有测试用例
4. 评分并汇总新结果
5. 人工审查。重复

当结果令人满意、反馈持续为空或不再有明显改进时，即可停止迭代。

### 9.7 使用 skill-creator 自动化评估

skill-creator 是一个元 Skill，专门用于创建、测试、评估和迭代优化 Skill。它可自动完成以下流程：

- 运行评估并生成 `grading.json`
- 汇总基准数据到 `benchmark.json`
- 启动 HTML 查看器供人工审查
- 迭代改进 Skill

**触发方式：**

```markdown
用 skill-creator 创建一个名为「 weekly-report-generator 」的 Skill ，
用于自动生成周度工作汇报。
```

```markdown
用 skill-creator 验证我的 weekly-report-generator Skill ，
检查 SKILL.md 语法、权限设置是否合规
```

***

## 10. 描述优化与触发精度

### 10.1 触发机制原理

Skill 的 `description` 字段是智能体决定是否加载 Skill 的主要机制。智能体在启动时仅加载每个 Skill 的 `name` 和 `description`，并仅凭这些信息判断何时可能相关。

### 10.2 编写有效描述的原则

- **使用祈使语气**：将描述写成给智能体的指令："当...时使用此 Skill"，而非"此 Skill 做..."
- **关注用户意图，而非实现细节**：描述用户想要实现什么，而非 Skill 的内部机制
- **宁可多覆盖，不可遗漏**：明确列出 Skill 适用的上下文，包括用户未直接提及领域名称的情况
- **保持简洁**：通常几句话到一小段即可

### 10.3 触发评估查询设计

创建约 20 个评估查询——8-10 个预期触发的和 8-10 个预期不触发的：

```json
[
 { "query": "我有一个 CSV 文件，包含月度销售数据...", "should_trigger": true },
 { "query": "将这个 JSON 文件转换为 YAML 的最快方法是什么", "should_trigger": false }
]
```

**预期触发的查询**应覆盖：

- 不同的措辞（正式/随意）
- 不同的明确程度
- 不同的详细程度
- 不同的复杂程度

**预期不触发的查询**最有价值的是**近似命中**——与 Skill 共享关键词或概念、但实际需要不同功能的查询。

### 10.4 优化循环

1. **评估**当前描述在训练集和验证集上的表现
2. **识别失败**：哪些预期触发的查询没有触发？哪些预期不触发的查询触发了？
3. **修订描述**：着眼于提炼通用规律

- 预期触发的查询未触发 → 描述范围可能过窄
- 预期不触发的查询误触发 → 描述范围可能过宽
- 避免简单堆砌失败查询中的特定关键词——这会导致过拟合

4. **重复**步骤 1-3，直到训练集查询全部通过或不再有明显改进
5. **选择最佳迭代**，以验证集通过率为依据

通常五次迭代即可收敛。


### 10.5 欠触发与过触发的诊断与解决

| 信号             | 解决方案                              |
| -------------- | --------------------------------- |
| Skill 未在应加载时加载 | 在 description 中补充更多细节和关键词，尤其是技术术语 |
| 用户手动启用 Skill | 添加用户实际会说的触发短语 |
| Skill 在无关查询时加载 | 添加否定触发 |
| 用户禁用 Skill | 缩小 description 的范围，提高针对性 |
| 结果不一致 | 改进指令的明确性，减少歧义 |
| API 调用失败 | 添加错误处理和重试逻辑 |

***
