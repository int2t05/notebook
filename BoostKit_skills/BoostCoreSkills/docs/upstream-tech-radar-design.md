# upstream-tech-radar design

## Goal

整理 `upstream-tech-radar` 为可在 `skills_bk` 仓库中贡献和维护的标准 Skill 目录，并把定位从“通用上游雷达”收紧为“Arm 高性能开发工程师获取前沿信息的上游技术雷达”。

## Scope

- 新增 `skills/upstream-tech-radar/`
- 补充中文的人类可读 `README.md`
- 保留并迁移原始 skill 的 3 份参考文档
- 在 `docs/` 下补一份设计说明
- 在 `tests/` 下补一组结构校验测试
- 更新根 README 的技能索引

## Design Choices

### 1. 保留方法骨架，但改变视角

原始 skill 已经有比较完整的方法论，因此不重写核心分析框架，而是重点做两类改造：

- 把 `SKILL.md` 重组为更适合公共仓库、也更利于 Agent 触发的结构
- 把“通用技术观察”收紧为“Arm 高性能工程判断”

### 2. 中文主文案，保留规范 frontmatter

考虑到用户明确要求中文表达，本次以中文作为 `SKILL.md`、`README.md` 和 `references/` 的主文案语言；仅在 frontmatter `description` 中继续保留以 `Use when...` 开头的英文规范格式，以兼容 Skill 检索约束。

### 3. 继续保持 documentation-first

这个 skill 当前没有脚本依赖，属于“方法型 skill”，因此本次不额外引入 `scripts/`、配置文件或自动抓取代码，避免为了贡献而过度工程化。

### 4. 用轻量测试替代伪功能测试

既然 skill 本身没有可执行流水线，测试不应伪装成功能测试。本次测试仅做结构与约束验证：

- 关键文件存在
- `SKILL.md` frontmatter 合法
- `description` 以 `Use when` 开头
- README 和 SKILL 中引用的 reference 文件都存在
- Skill 文案明确包含 Arm 高性能开发工程师视角

### 5. 允许在真实服务器上验证方法可行性

虽然当前 skill 没有内置脚本，但它强调“最新动态”必须来自实时数据，因此允许在真实服务器环境中验证：

- 是否具备抓取 GitHub 最新信息的网络能力
- 是否能读取 open PR、merged PR、活跃 issue
- 是否能支撑固定模板月报生成

### 6. 对高价值条目要求更深的证据链

后续增强方向不是继续堆更多“关注点”，而是把分析深度固化成规则：

- 普通条目允许简明归纳
- 高价值条目要求继续看 discussion、review、commit 和 diff
- 指令级条目要求解释指令或硬件特性的作用、适用场景和边界

这样 skill 产出的月报会更像技术判断，而不是项目动态摘要。

## Files Added

```text
docs/upstream-tech-radar-design.md
skills/upstream-tech-radar/
tests/upstream-tech-radar/test_skill_structure.py
```

## Follow-up Suggestions

- 如果后续要把这个 skill 做成半自动化工作流，可以新增 `scripts/` 和对应 pytest。
- 如果后续要提升贡献说服力，建议补一份真实样例输出，例如某个 Arm 相关基础库或性能组件的月度雷达。
- 如果仓库后面引入统一校验脚本，可以把这份结构测试并入统一 validator。
