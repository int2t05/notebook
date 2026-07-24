---
name: upstream-tech-radar
description: Use when an Arm high-performance engineer needs upstream GitHub signals, peer-repository comparisons, or monthly technology radar reports to guide performance, portability, and optimization decisions.
---

# 上游技术雷达

为本地项目产出固定格式的上游情报月报，但分析视角不是泛技术观察，而是 **Arm 高性能开发工程师** 的决策视角。目标是帮助工程师判断哪些上游变化值得在 Arm 平台优先关注、验证、借鉴或规避，而不是机械罗列最近发生了什么。
这里尤其强调 **指令使能**：不仅看某个上游是不是“做了性能优化”，还要判断它是否真正打开、补齐或推广了某类 Arm 指令路径，以及这种使能最终落在什么热路径、解决什么问题、适合什么应用场景。

## 何时使用

- 用户想跟踪某个上游 GitHub 仓库最近 30 天的技术方向。
- 用户想从 Arm 高性能视角观察 open PR、merged PR、活跃 issue 和 peer repo 变化。
- 用户想知道哪些变化会影响 Arm 平台性能、可移植性、向量化能力、工具链或优化路线。
- 用户想把上游动态转成对本地项目可执行的性能路线建议。
- 用户特别关心哪些变化在推动 `Neon`、`SVE`、`SVE2` 等 Arm 指令能力的使能、扩展或真实落地。

不要用于：

- 单个 PR 的代码审查
- 单个 issue 的答疑
- 一次性仓库事实查询

## 先确认或推断的信息

在开始写报告前，先收集或合理推断：

- 本地项目名称
- 主上游仓库
- 至少一个 peer repository
- 时间窗口，默认最近 30 天
- 关注重点，例如：
  - Arm CPU / SoC / NUMA / 内存子系统
  - SIMD / Neon / SVE / 向量化
  - 编译器、运行时、profiling、benchmark
  - 兼容性、CI、可移植性、性能回归

## 分析规则

1. 优先使用实时 GitHub 信息。
   - 查看主上游 open PR，判断接下来可能落地的功能、优化或维护方向。
   - 优先查看最近 30 天 merged PR 和最近活跃 issue，并按主题聚类，而不是按时间平铺。
   - 如果最近 30 天内样本过少、仓库更新节奏慢，允许扩展为“最近一个月或最近 10 个高质量 PR / issue，以信息量更高的一侧为准”。
   - 所谓“高质量 PR / issue”，指能明显揭示性能方向、指令级优化、平台覆盖、API 路线、维护压力或架构取舍的条目，而不是纯 cosmetic 改动。
   - 查看最近活跃 issue，理解用户和 maintainer 当前最在意什么。
   - 查看 peer repo 同期活动，识别不同技术路线和领先方向。
   - 当用户提到“最新”“最近”“本月”“今天”这类相对时间时，必须以实时数据核实，不要靠记忆回答。
   - 在最终报告里尽量写清楚绝对日期范围，例如 `2026-05-03` 到 `2026-06-02`，避免相对时间歧义。

2. 所有结论都要转成 Arm 高性能语境。
   对每个重要变化，至少回答：
   - 它改了什么
   - 它为什么重要
   - 它对 Arm 平台性能、可移植性或优化空间有什么影响
   - 它更像短期修补，还是长期方向信号
   - 本地项目是否值得跟进
   - 它是否只是一般性重构，还是在真正使能某类 Arm 指令路径

3. 严格区分事实与推断。
   - 事实尽量附上 PR、issue、commit 或仓库链接。
   - 推断必须明确标注，不要把猜测写成事实。
   - 数据缺口、访问缺失或不确定项要坦白写出。

4. 结论必须能指导工程动作。
   报告末尾要明确拆分：
   - 短期值得验证的动作
   - 中期值得规划的方向
   - 继续观察但暂不动作的事项
   - 不建议直接照搬的想法

5. 对高质量条目给出更细的信息密度。
   - 如果某个 PR / issue 具有明显的指令级价值、向量化价值或架构路线价值，不要只写一句摘要。
   - 对这类条目，应尽量补充：
     - 涉及的指令、ISA 或硬件特性，例如 `SVE`、`SVE2`、`Neon`、`SIMD`、`HISTSEG`
     - 这些指令或硬件特性通常解决什么问题，例如分类、掩码生成、批量比较、分段处理、减少分支或改善访存效率
     - 它是在直接调用现有指令能力，还是在补齐此前缺失的指令使能路径
     - 影响的热路径、核心算法或数据布局
     - 更适合什么 workload、输入分布或访问模式
     - 在什么场景下收益可能不明显，或可能受限于实现复杂度、硬件覆盖和回归风险
     - 它更像实验性尝试、局部优化，还是可推广的工程路线
     - 如果本地项目跟进，需要重点验证什么 benchmark 或 workload
   - 高质量条目宁可少写几个，也要写深一点。

6. 采用三层深度分析，而不是所有条目一视同仁。
   - 普通条目：可按模板做简洁归纳，说明改了什么、为什么重要、对 Arm 的意义。
   - 高价值条目：必须继续看 discussion、review、commit 或 diff，提取争议点、设计取舍和代码真正触达的核心路径。
   - 指令级条目：在高价值条目的基础上，还要解释指令或硬件特性的作用机制、典型收益来源、适用场景和不适用场景。
   - 如果某个条目无法拿到足够的讨论或代码上下文，要在报告里明确说明深度受限，而不是假装已经看过。

7. 对高价值条目，至少补齐最小证据链。
   - 仅靠标题和 PR 简介不够。
   - 至少再查看其中两类信息：discussion / review comments、commit message / commit list、文件 diff / patch、相关 issue 讨论。
   - 如果条目最终进入月报重点段落，优先提炼：
     - 讨论里暴露出的核心争议、阻塞点或 maintainer 判断标准
     - 代码改动实际触达的模块、函数、热路径或数据结构
     - 是否只是 plumbing / wiring，还是确实改变了关键实现路径
     - 对本地项目最值得复用的思路，而不是简单复述改动内容

## 最小执行流程

在真实环境中执行这个 skill 时，建议遵循这个最小流程：

1. 确认主上游、peer repo 和时间窗口。
2. 抓取主上游 open PR、最近 30 天 merged PR、最近活跃 issue。
3. 如果样本太少，就扩展成“最近一个月或最近 10 个高质量 PR / issue”的混合样本。
4. 抓取 peer repo 同期 open PR / merged PR / 活跃 issue 或至少 merged PR 与活跃 issue。
5. 按 [references/analysis-dimensions.md](references/analysis-dimensions.md) 做 Arm 视角归类。
6. 对准备写成重点段落的高价值条目，继续补看 discussion、review、commit 或 diff。
7. 按 [references/monthly-report-template.md](references/monthly-report-template.md) 生成固定格式报告。

如果实时抓取失败，要在报告末尾明确说明缺口，而不是静默降级。

## 固定输出要求

始终使用 [references/monthly-report-template.md](references/monthly-report-template.md) 的固定结构输出。

输出时遵守这些规则：

- 按主题聚类，例如性能、API、兼容性、工具链、测试、可维护性、生态集成。
- 每个重点结论尽量附仓库链接、PR 编号或 issue 编号。
- 忽略纯 cosmetic churn，除非它反映出更大的维护方向。
- 不要写成新闻播报，要写成技术判断。

## 判断维度

使用 [references/analysis-dimensions.md](references/analysis-dimensions.md) 判断哪些变化具有战略意义。

使用 [references/repo-comparison-playbook.md](references/repo-comparison-playbook.md) 比较主上游和 peer repository。

## 好结果的标准

一份合格输出应该回答清楚：

- 哪些上游特性最可能影响 Arm 平台上的性能上限或工程路线？
- 哪些 merged work 说明维护者正在认真投入某个方向？
- 当前社区最焦虑或最频繁讨论的问题是什么？
- peer repo 最近做了什么，会改变本地项目的参考基线？
- 本地项目应该优先验证、延后规划、持续观察、还是明确规避哪些方向？

## 默认假设

除非用户另行指定：

- 默认看最近 30 天
- 默认输出月度技术雷达
- 默认把主上游作为方向主信号源
- 默认至少包含一个 peer repository 对比
- 默认以 Arm 高性能开发工程师的视角给出短期、中期和观察项建议
