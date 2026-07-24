# upstream-tech-radar

`upstream-tech-radar` 是一个面向 **Arm 高性能开发工程师** 的分析型 Skill。它把“看主上游 open PR、看近 30 天 merged PR、看活跃 issue、看 peer repo”这套信息采样流程，整理成固定格式的月度技术雷达，帮助工程师从 Arm 平台性能、可移植性、向量化与工具链演进的视角获取前沿信息，并转成对本地项目有价值的技术判断。

它特别强调 **指令使能** 这条主线：不仅关注某个仓库最近有没有性能优化，还要判断它是否在打开、补齐或推广某类 Arm 指令能力，例如 `Neon`、`SVE`、`SVE2`、特定分类/扫描/掩码生成路径，进一步分析这些能力会落在哪些热路径、适合什么 workload、对本地项目是否值得跟进。

## 与 magazine-collect 的区别

这个 skill 和仓库里的 `magazine-collect` 看起来都像“收集近期动态”，但它们的目标完全不一样：

- `magazine-collect` 是 **通用领域月刊收集**。重点是按规则文件去多个信息源抓内容、做领域月报、digest 或季报，适合编译器、推荐系统、数据库、安全等任意领域。
- `upstream-tech-radar` 是 **面向 Arm 高性能工程的上游技术雷达**。重点不是“这个领域最近发生了什么”，而是“某个主上游仓库和 peer repo 的变化，哪些真正会影响 Arm 平台性能路线、指令级优化、指令使能、工具链选择和本地项目决策”。

更直接地说：

- `magazine-collect` 关注的是 **领域信息覆盖面**，产物更像月刊、要闻汇总、情报 digest。
- `upstream-tech-radar` 关注的是 **上游代码与讨论里的工程信号**，产物更像技术判断、优化路线分析和行动建议。

因此这两个 skill 的关注点也不同：

- `magazine-collect` 更看重信息源组织、时间窗覆盖、板块汇总、写作表达。
- `upstream-tech-radar` 更看重 open PR、merged PR、active issue、peer repo 对比，以及 discussion / review / diff 里暴露出的真实技术路线。
- `upstream-tech-radar` 特别关心“某个优化是不是只是一般性重构”，还是“它真正使能了某类 Arm 指令路径，改变了热循环的实现方式，或提高了某类 workload 在 Arm 上的收益上限”。

如果你只是想做“近几个月这个领域的大事速览”，优先用 `magazine-collect`。如果你想判断“这个上游仓库的变化，对 Arm 高性能开发到底意味着什么”，优先用 `upstream-tech-radar`。

## 适用场景

- 需要判断某个上游仓库最近一个月的技术方向和维护重点，而且关心它对 Arm 平台的真实影响。
- 需要给本地项目做“上游动态雷达”“同类仓库技术路线对比”“Arm 优化路线参考”。
- 需要把 GitHub 活跃度转成可执行建议，例如“哪些优化值得先在 Arm 机器上验证”“哪些变化可能影响跨架构性能基线”。
- 需要长期跟踪编译器、运行时、基础库、benchmark、profiling 工具或系统基础设施的演进趋势。

不适合的场景：

- 只看单个 PR 或单个 issue。
- 只想知道某个仓库的基础事实信息。
- 只做一次性代码评审，不需要月度趋势归纳。

## 核心思路

- 以实时 GitHub 信息为主，优先看 open PR、最近合并 PR、活跃 issue、peer repo 最近活动。
- 不停留在“发生了什么”，而是继续解释“为什么重要”“这反映了什么技术方向”“对 Arm 平台意味着什么”“对本地项目意味着什么”。
- 对 peer repo 的比较强调可迁移经验，而不是简单判断谁更强，尤其关注 Arm 上的性能策略差异、向量化路线和可移植性成本。
- 输出必须是固定格式月报，便于连续多期横向对比。

## Arm 视角下的关注重点

这个 skill 的默认分析视角不是泛技术观察，而是一个 Arm 高性能开发工程师会优先追问的问题：

- 这个变化是否影响 Arm CPU 上的吞吐、延迟、缓存命中、内存带宽利用率或尾延迟？
- 这个变化是否涉及 Neon / SVE / SIMD / 向量化、数据布局、批处理、zero-copy 或 cache-friendly 设计？
- 这个变化是否影响 GCC / LLVM / Clang / sanitizer / CI matrix / profiling 工具链？
- 这个变化是否会改变 Arm 与 x86 在实现路径、性能方法论或可维护性上的对比基线？
- 这个变化是否值得本地项目优先在 Arm 环境验证，还是只适合作为观察项？

## 指令级价值约束

这个 skill 需要比普通“项目动态汇总”更进一步：**对有指令级价值的高质量条目展开更细的信息**。

这里的“指令级价值”包括但不限于：

- 明确涉及 `SVE`、`SVE2`、`Neon`、`SIMD`、`HISTSEG` 等 ISA / 指令特性的优化
- 与向量化、热路径、branch reduction、cache-friendly layout、batching、escaping、zero-copy 直接相关的实现
- 会影响 Arm 上热点循环、数据搬运、内存访问模式或吞吐上限的改动

遇到这类高质量 PR / issue 时，不应该只写一句“做了某某优化”，而应该尽量回答：

- 具体涉及哪类指令、ISA 或硬件能力
- 这些指令或硬件能力通常用来解决什么问题，例如批量分类、掩码生成、减少分支、加速字符串扫描或改善访存模式
- 它作用在哪条热路径
- 它更适合什么应用场景、输入分布或 workload
- 在什么场景下可能收益有限，或者会引入复杂度与维护成本
- 它更像实验性 patch、局部优化，还是可推广路线
- 本地项目若跟进，最该验证的 workload 是什么

## 三层深度规则

这个 skill 不要求所有条目都写得一样深，而是要求按价值分层：

- 普通条目：说明改了什么、为什么重要、对 Arm 的意义。
- 高价值条目：必须额外查看 discussion、review、commit 或 diff，提炼设计取舍、争议点和代码触达路径。
- 指令级条目：在高价值条目的基础上，还要解释指令或硬件特性的作用机制、典型收益来源、适用场景和不适用场景。

这意味着最终输出不是“每条都讲一点”，而是“少数重点条目讲透，其余条目讲清”。

## 高价值条目的最小证据链

如果一个 PR / issue 要进入月报里的重点段落，不能只靠标题和摘要判断。至少要再补看其中两类信息：

- discussion / review comments
- commit message / commit list
- 文件 diff / patch
- 相关 issue 讨论

重点不是复述，而是提取：

- maintainer 真正在意什么
- 条目卡住或推进的原因是什么
- 代码改动实际触达了哪些核心模块、函数、热路径或数据结构
- 哪些点对本地项目有迁移价值，哪些点只是上游特定上下文成立

## 使用方式

直接用自然语言调用即可，例如：

```text
分析 sonic-cpp 最近 30 天的上游动态，站在 Arm 高性能工程师视角，顺便和 simdjson、yyjson 做对比，给出我们接下来两个月值得跟进的方向。
```

```text
帮我做一份 vLLM 的 upstream tech radar，重点看 Arm 平台上的性能、兼容性和社区 issue 压力。
```

```text
给我们的本地项目做一份月度技术雷达：主上游是 openssl，peer repo 看 boringssl 和 rustls，重点关注 Arm 上的算法路径、工具链和性能实现差异。
```

调用时建议明确这些信息：

| 参数 | 默认值 | 说明 |
|---|---|---|
| 本地项目名 | 必要时从上下文推断 | 报告里会用来写建议 |
| 主上游仓库 | 必填 | 例如 `owner/repo` |
| 对比仓库 | 至少 1 个更好 | 没给时可按上下文推断 |
| 时间窗口 | 最近 30 天 | 月报默认窗口 |
| 关注点 | 无 | 可指定 Arm 性能、SVE/Neon、编译器、运行时、兼容性、测试、生态等 |

## 实时性约束

- 这个 skill 处理的是上游“最新动态”，因此默认必须基于 **实时 GitHub 数据**。
- 当用户说“最新”“最近”“本月”“今天”“过去 30 天”时，不应凭记忆作答。
- 报告里尽量写清楚绝对日期范围，例如 `2026-05-03` 到 `2026-06-02`，避免相对时间歧义。
- 如果某个仓库或接口抓取失败，应该在“信息来源与不确定性说明”中明确写出，而不是默默跳过。

## 采样边界不要卡死

默认仍然优先看最近 30 天，但不要机械卡死在这个窗口：

- 如果仓库最近 30 天更新充分，就以最近 30 天为主。
- 如果仓库更新较慢、样本太少，可以扩展成“最近一个月或最近 10 个高质量 PR / issue，以信息量更高的一侧为准”。
- 如果某个仓库 PR 很少但 issue 很关键，允许 issue 比例更高。
- 如果某个仓库 merged PR 很少但 open PR 里有明显的 Arm 指令级优化信号，也应该重点展开。

## 输出结构

最终报告必须遵循 [`references/monthly-report-template.md`](./references/monthly-report-template.md)：

1. 本期结论摘要
2. 来自 Open PR 的潜在方向信号
3. 最近 30 天已合并的重要变化
4. 活跃 Issue 主题
5. Peer Repository 对比
6. 对本地项目的 Arm 技术启发
7. 建议动作
8. 信息来源与不确定性说明

其中高价值条目建议额外补这些信息块：

- 讨论里暴露的争议点
- 代码改动触达的核心路径
- 指令 / ISA 的作用
- 更适合的应用场景
- 暂不适合照搬的边界

## 判断标准

判断一个变化是否值得进入雷达，不要只看“改动大小”，而要看它是否反映出这些维度中的真实信号：

- 性能方向，尤其是 Arm 热路径、缓存行为、内存效率和向量化策略
- API / feature surface
- 兼容性与平台覆盖
- 可靠性与正确性
- 工具链与可维护性
- 社区信号
- 对本地 Arm 优化路线的战略意义

具体判定问题见 [`references/analysis-dimensions.md`](./references/analysis-dimensions.md)。

对 peer repo 的对比方法见 [`references/repo-comparison-playbook.md`](./references/repo-comparison-playbook.md)。

## 目录结构

```text
skills/upstream-tech-radar/
├── SKILL.md
├── README.md
└── references/
    ├── analysis-dimensions.md
    ├── monthly-report-template.md
    └── repo-comparison-playbook.md
```

## 维护建议

- 如果后续扩展报告版式，优先改 `references/monthly-report-template.md`。
- 如果发现“重要但容易漏判”的变化类型，补充到 `references/analysis-dimensions.md`。
- 如果后续沉淀出更稳定的 peer repo 对比方法，再补充到 `references/repo-comparison-playbook.md`。
- 这个 skill 当前是“方法型文档 skill”，不依赖脚本；如未来引入自动化抓取脚本，再补充对应测试和运行说明。
- 如果后面要增强仓库贡献说服力，建议补一份真实样例输出，例如“某个 Arm 相关基础库的月度雷达报告”。

## 环境验证与前置条件

这个 skill 本身不绑定脚本，但如果要在服务器或远端环境验证“能否拿到最新数据”，至少需要：

- 能访问 GitHub 网页或 GitHub API
- 基本命令行工具，例如 `curl`
- 可选的 Python 运行时，方便做轻量 JSON 解析

一个最小可行验证流程是：

1. 验证环境里存在 `curl` 或等价 HTTP 工具。
2. 访问 GitHub API，确认能读到目标仓库的基础信息。
3. 再验证能拉到 open PR、最近 30 天 merged PR、活跃 issue 这三类数据中的至少两类。
4. 最后确认这些数据足以按固定模板生成报告。

如果后续要把它工程化成半自动化流程，再考虑补 `scripts/`。
