# Kernel-Patch / Patch-Validator 测试报告

## 数据来源

当前测试报告基于当前仓库 `patch_skill/测试汇总/` 目录下的 merged-diff Markdown 报告汇总，主要包括：

- `patch_skill/测试汇总/TLBI_patch_validation_report.md`
- `patch_skill/测试汇总/TLBI+IPI_patch_validation_report.md`
- `patch_skill/测试汇总/hdbss_patch_validation_report.md`
- `patch_skill/测试汇总/virt_dev_irqbypass_patch_validation_report.md`
- `patch_skill/测试汇总/vtimer_patch_validation_report.md`

这些报告的生成时间均为 2026 年 3 月 31 日，模式均为 `merged-diff`。

## 汇总结果

### 统计口径说明

本报告以 **skill 真实补丁合入质量** 为口径汇总，而不是直接照搬 `merged-diff` 原始差异数。

这里的统计分为三类：

- 通过补丁：补丁已正确合入，结果可接受
- 合入错误补丁：补丁已进入目标分支，但合入结果错误
- 未合入补丁：补丁没有成功进入目标分支

特别说明：

- 汇总数字不是工具原始输出的直接照抄，而是经过人工确认后修正的结果
- 对语义替换、patch hunk 部分已存在等可确认的合入偏差，若人工确认结果可接受，则按“通过补丁”统计
- `config` 映射导致的差异，不归类为“合入错误”
- 某些 `merged-diff` 的 `DIFFERENT` 仅反映落地形式不同，不代表 skill 合入失败
- 当前样本中，除 `TLBI+IPI` 组合用例外，其余测试用例均按“通过”统计

### 真实合入质量汇总

| 指标 | 数量 |
|------|------|
| 总测试补丁数量 | 95 |
| 通过补丁数量 | 87 |
| 合入错误补丁 | 6 |
| 未合入补丁 | 2 |

说明：

- 上述汇总数字已经过人工确认修正，不等同于 `patch-validator` 原始报告中的表面差异数量。
- 87 个“通过补丁”中，包含所有非 `TLBI+IPI` 用例的补丁，以及 `TLBI+IPI` 中正确合入的补丁。
- 其中一部分补丁虽然存在表面 diff 偏差，但经人工确认属于语义替换或 patch hunk 部分已存在，因此仍按“通过补丁”处理。
- 6 个“合入错误补丁”全部来自 `TLBI+IPI_patch_validation_report.md`。
- 2 个“未合入补丁”也全部来自 `TLBI+IPI_patch_validation_report.md`。

### 实际合入错误结论

从当前测试样本看，只有 `TLBI+IPI_patch_validation_report.md` 中出现了真实补丁合入错误。

原因不是单个 patch 本身无法处理，而是：

- 该用例把两个 patch set 一起合入
- 总 patch 数达到 37 个，超出了当前单 agent 工作模式下较稳妥的上下文范围
- 在长链路执行过程中，LLM 更容易跳出 `kernel-patch` skill 的约束流程
- 一旦脱离 skill 约束，状态判断、恢复动作和 review handoff 的一致性会下降，从而引入真实合入错误

相对地，其他测试报告虽然可能存在 `merged-diff` 层面的差异，但不应归类为真实合入错误，尤其是 config 映射相关差异。

## 分组结果

| 用例 | 总补丁数 | 通过 | 合入错误 | 未合入 |
|------|---------|------|---------|-------|
| TLBI | 15 | 15 | 0 | 0 |
| TLBI + IPI | 37 | 29 | 6 | 2 |
| hdbss | 8 | 8 | 0 | 0 |
| virt_dev_irqbypass | 13 | 13 | 0 | 0 |
| vtimer | 22 | 22 | 0 | 0 |

## 结果解读

- 当前 skill 流程已经能够完成批量补丁导出、合入和 merged-diff 复核。
- 95 个测试补丁中，87 个正确通过，说明当前 skill 在常规 patch set 规模下能够保持较好的自动化合入质量。
- 真实合入质量问题集中在 `TLBI+IPI` 组合用例：6 个补丁合入错误，2 个补丁未合入。
- 除 `TLBI+IPI` 外，其余测试用例均通过。
- 当前最明确的风险点，是“两个 patch set 一起合入”导致上下文超限后，LLM 跳出 skill 限制。
- `config` 映射问题不是合入错误，不应作为 skill 失败补丁统计。

## 当前限制

### 单 Agent 限制

当前 skill 工作模式本质上是单 agent 串行处理：

- 同一时刻只围绕一个主上下文推进
- patch set 很长时，所有中间状态、冲突信息、人工决策和 review 结果都依赖单条上下文链维持
- 当补丁数量较多、冲突较复杂或恢复轮次较多时，更容易触发上下文窗口压力

### 上下文限制带来的影响

在 patch 数量超过一定规模时，容易出现以下问题：

- agent 跳出 skill 约束，不再严格遵循既定工作流
- 对当前 patch set 进度、当前 commit、当前 phase 的表述变得不稳定
- 错误地把临时 git 观察结果当成批量状态事实来源
- 在冲突恢复、人工接受或 review handoff 阶段遗漏必需步骤
- 最终导致补丁合入质量下降，特别是大 patch set 和多轮恢复场景

### 当前建议

- 长 patch set 尽量分批执行，避免一次性给出过长提交列表
- 避免把多个较长 patch set 合并成一次超长任务，尤其不要把类似 `TLBI + IPI` 这种组合系列直接放在一个超大上下文里处理
- 每轮恢复都优先依赖状态文件和结构化返回结果，而不是聊天上下文
- 当 `kernel-patch` 已返回 `handoff_review` 时，立即切到 `patch-validator`
- 对超长 patch set，建议把 patch 系列拆成多个逻辑 patch set，降低单次上下文负担
