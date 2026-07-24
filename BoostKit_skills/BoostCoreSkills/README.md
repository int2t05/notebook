# Boostkit Skills 代码仓设计文档（鲲鹏基础加速域）

## 项目概述

### 项目定位

鲲鹏基础加速域 Agent Skills：将鲲鹏软件栈专家经验与能力模块化、可复用，使能用户与开发者。

在 AI 智能体（Agent）上下文中，技能（Skills）是为扩展 Agent 能力而设计的模块化功能单元。每个 Skill 封装了指令、元数据及可选资源（如可执行脚本、模板），当 Agent（比如 OpenClaw、OpenCode 等）通过意图识别匹配到相关上下文时，自动调用对应 Skill。

本仓库是一个基于开源 Agent 能力提供 Skills 参考的核心仓库，专注于 **Agent Skills for Kunpeng** 的开发与管理，旨在促进鲲鹏基础加速域专家 Skills 的协同开发和创新。

### 核心目标

- 为开发者提供鲲鹏基础加速域 Agent Skills 参考
- 促进 Agent Skills 的协同开发、共享和创新

### 为什么使用 Agent Skills？

[Agent Skills](https://agentskills.io/home) 是基于文件系统的可复用资源，旨在为 Agent 有效注入特定领域的专业知识和能力，包括工作流、上下文环境和最佳实践，从而将通用型 Agent 转化为专家型 Agent。与一次性对话的提示词（Prompts）不同，Skills 支持按需加载，避免在多轮对话中重复提供相同指示。

核心优势：

- 赋予 Agent 专精能力：为鲲鹏基础加速域任务定制稳定工作流，实现领域泛化。
- 减少重复工作：一次创建，多平台复用（OpenClaw、OpenCode、CodeBuddy、TRAE 等）。
- 组合能力：通过整合多个 Skills 构建复杂工作流程。

### 目标用户

- 鲲鹏社区开发者
- 场景化应用开发者
- 内外部合作伙伴

### SKILL 命名规范

- `SKILL.md` 文件必须严格命名为 `SKILL.md`（区分大小写），不接受任何变体（如 `SKILL.MD`、`skill.md`）。
- SKILL 文件夹命名必须使用**烤串命名法（kebab-case）**，例如 `e2e-auto-optimize`。
  - ✅ 正确示例：`e2e-auto-optimize`
  - ❌ 错误示例：`E2E auto Optimize`（含空格）
  - ❌ 错误示例：`e2e_auto_optimize`（使用下划线）
  - ❌ 错误示例：`E2EAutoOptimize`（使用大写）

### 存放规则

- 将SKILL放到`skills`目录下
- 将SKILL的设计文档放到`docs`目录下
- 将SKILL的测试代码放到`tests`目录下

## 项目架构设计

### 整体架构

```text
agent-skills/
├── skills/                         # 技能核心目录（扁平化结构）
│   ├── skill-name-1/               # 技能 1
│   ├── skill-name-2/               # 技能 2
│   └── skill-name-n/               # 技能 N
├── docs/                           # 文档目录
│   ├── design/                     # 设计文档
│   ├── guides/                     # 开发指南
│   └── examples/                   # 示例文档
├── tests/                          # 测试目录
│   ├── test-data/                  # 测试数据集
│   ├── validators/                 # 验证脚本
│   └── expected-results/           # 预期结果
├── scripts/                        # 脚本工具
│   └── validate_skills.py          # 技能验证脚本
├── template/                       # 技能模板
│   └── SKILL.md                    # 标准技能模板
├── README.md                       # 项目说明文档
├── AGENTS.md                       # AI 编程助手指南
└── .gitignore                      # Git 忽略配置
```

## 安装 Skills

建议使用 [Skills 管理工具](https://github.com/vercel-labs/skills)（`npx skills`）安装 Skills。以下为常用命令示例：

```bash
# 列出 kunpeng/agent-skills 仓库中包含的所有 Skills
npx skills add https://gitcode.com/boostkit/skills.git --list

# 安装指定 Skill
npx skills add https://gitcode.com/boostkit/skills.git --skill e2e-auto-optimize

# 将 Skills 安装到特定 Agent（例如 trae 和 opencode）
npx skills add https://gitcode.com/boostkit/skills.git -a trae -a opencode

# 非交互式安装（适合 CI/CD 场景）
npx skills add https://gitcode.com/boostkit/skills.git --skill e2e-auto-optimize -g -a opencode -y

# 安装仓库中的所有 Skills
npx skills add https://gitcode.com/boostkit/skills.git --all
```
`常用agent：trae, opencode, claude-code, codex`


## SKILL 索引目录

> 当前索引以单表方式维护，便于统一检索与扩展。

| 序号 | Skill 名称 | 相对路径 | 简述 | 开发人员 | 维护人员 |
|---|---|---|---|---|---|
| 1 | e2e-auto-optimize | skills/e2e-auto-optimize | 针对加速库端到端的性能优化 skills。 | 王绍宇 | 王绍宇 |
| 2 | gitcode-review | skills/gitcode-review | 对gitcode PR进行AI检视的skill。 | 王绍宇 | 王绍宇 |
| 3 | magazine-collect | skills/magazine-collect | 按月刊收集规则（如 compiler-magazine-collect.md）对技术领域近 N 月动态做 LLM-first 汇总，产出单板块中文 digest md；`mode=magazine` 全量跑并拼接月刊；`mode=html` 产月刊 HTML 视觉版；`mode=eml` 把 HTML 打包为可双击直发的 `.eml` 邮件版。 | 黄晓权 | 黄晓权 |
| 4 | paper-digest | skills/paper-digest | 按"方向 + 时间窗"自动收集内存库/编译器优化方向论文：4 阶段流水线（动态发现 + 粗分类 + 4 段摘要 + Jinja 渲染），支持 Claude subagent 或 DeepSeek API 作为 LLM 后端。 | 黄晓权 | 黄晓权 |
| 5 | devkit-perf | skills/devkit-perf | 使用 `devkit tuner top-down` 采集并解读 CPU 微架构 Top-Down 指标，识别 Frontend/Core/Memory 等流水线瓶颈。 | 廖思睿 | 廖思睿 |
| 6 | perf-hotspot | skills/perf-hotspot | 基于 Linux perf、ARM SPE、PMU 事件和 DDRC/L3C 计数器进行 CPU 热点、缓存、指令级流水线和带宽分析。 | 廖思睿 | 廖思睿 |
| 7 | perf-topdown | skills/perf-topdown | 联合 devkit Top-Down 与 perf 数据进行性能瓶颈交叉验证，定位程序未达到理论峰值的原因。 | 廖思睿 | 廖思睿 |
| 8 | dev-container-manager | skills/dev-container-manager | 管理远程 Linux 服务器上的 Docker 开发容器，支持资源探测、NUMA 感知 CPU 分配、SSH 密钥生成和容器生命周期管理。 | 廖思睿 | 廖思睿 |
| 9 | knowledge-base | skills/knowledge-base | 知识卡片管理：创建/搜索/索引/列出，将问答与分析归档为结构化知识卡片并维护可检索索引。设计文档见 docs/knowledge-base-design.md。 | 黄晓权 | 黄晓权 |
| 10 | prompt-archive | skills/prompt-archive | 提取并归档本机 Claude Code 历史会话中「用户真人发出的 prompt」，生成每会话 md + 主索引 + 质量分析报告（启发式 5 维打分 + Top/Bottom 排行 + 可选 LLM 深析），支持增量更新。设计文档见 docs/prompt-archive-design.md。 | 黄晓权 | 黄晓权 |
| 11 | remote-vm-builder | skills/remote-vm-builder | 在远程 SSH 可达的 libvirt/KVM Linux 宿主机上创建和管理 Linux cloud-image VM，支持内置 OS catalog、自定义镜像 URL、宿主机能力查询和 VM 生命周期管理。 | 于智洹 | 于智洹 |
| 12 | upstream-tech-radar | skills/upstream-tech-radar | 以 Arm 高性能开发工程师视角分析主上游仓库的 open PR、近 30 天 merged PR、活跃 issue 以及 peer repo 动态，输出固定格式的月度技术雷达，并给出对本地项目的短期、中期和观察项建议。设计文档见 docs/upstream-tech-radar-design.md。 | 叶韦宏 | 叶韦宏 |
| 13 | arm64-arch-reference | skills/arm64-arch-reference | 查阅 ARM A-profile（AArch64/A64）架构特性（FEAT_*）与 A64 指令的权威速查表，覆盖特性引入版本、可选/强制状态、指令汇编模板/编码（Encoding）及「指令受哪个特性门控」，数据源自 ARM 官方机器可读规范（AARCHMRS，对应手册 DDI 0487 M.b / Armv9.6）。设计文档见 docs/arm64-arch-reference/DESIGN.md。 | 王如锋 | 王如锋 |
| 14 | feature-design-doc | skills/feature-design-doc | 阅读某性能/优化特性的源码,产出图文并茂、可交付的设计文档(Markdown + Word/docx),支持中文/英文/中英双语;固化章节骨架、结构图 SVG 矢量 + 行为图 PlantUML、严格 docx 排版(中文宋体五号/英文 Times New Roman 五号/全黑无斜体/单倍行距段后6磅)、英文版图内文字也译英、图片与文档同级同次提交。 | 黄晓权 | 黄晓权 |
| 15 | theory-driven-pipeline-optimization | skills/theory-driven-pipeline-optimization | 面向计算密集型 kernel 的理论性能上限分析：识别核心指令和依赖链，编写微基准测量指令时延、吞吐和组合执行成本，再根据算法指令计数、依赖图和数据移动推导 theoretical cycles/unit、理论吞吐上限和优化 headroom。 | 韦安琪 | 韦安琪 |
| 16 | kunpeng-library-opportunity | skills/kunpeng-library-opportunity | 分析运行中的 Linux C/C++ 服务、例如RPC 服务组件，识别动态库、疑似静态链接库、ELF 与 proc 证据，结合 perf-hotspot 采样结果判断鲲鹏 BoostKit/BoostCore 库使能机会，例如 KAE、zlib、zstd、lz4、snappy、kpglibc、protobuf、sonic-cpp、KQMalloc、和 AVX2KI。 | 龚晓婷 | 龚晓婷 |
| 17 | kunpeng-cpu-opt-guide | skills/kunpeng-cpu-opt-guide | 鲲鹏处理器微架构优化参考（TSV110/HIP09/HIP12），覆盖指令延迟、流水线端口、性能陷阱、CPU 自动检测与横向对比。供其他性能优化 Skill 引用。 | 李彦成 | 李彦成 |
| 18 | tech-daily-brief | skills/tech-daily-brief | 把一组类型（如 GCC/LLVM/Go/Java/AI编译/内存库）当作一个关注集，每天产出一份中文《每日简报》md——按类型平铺、每类型各带「论文/资讯/上游代码」三维度；每个「类型×维度」的信息源由 LLM 自动发现并缓存为「源画像」、每日复用增量去重；反爬源走「关注点扇出 site: + RSS + Wayback CDX」绕行；产物双归档到公开仓库 + ai-docs。 | 黄晓权 | 黄晓权 |



---

## 免责声明

1. 本仓库中的 Agent Skills 内容、代码、配置及示例仅供技术参考和学习使用，不代表其适用于任何生产环境、商业场景或关键业务系统。
2. 开发者在使用本仓库内容时，应自行评估其安全性、兼容性和适用性。作者及贡献者不对因使用本仓库内容导致的任何直接或间接损失承担责任，包括但不限于数据丢失、系统故障、业务中断、经济损失等。
3. 本仓库内容可能涉及第三方依赖或接口调用示例，相关权限及合规性需由开发者自行核实。作者及贡献者不承担与第三方服务相关的任何责任。
4. 本仓库中的 Agent Skills 示例仅为功能演示，不保证其完整性、准确性、时效性。作者及贡献者有权随时修改或删除内容，无需另行通知。
5. 除非另有明确约定，本仓库所有内容均基于开源协议发布，不提供任何形式的技术支持、维护承诺或担保。
