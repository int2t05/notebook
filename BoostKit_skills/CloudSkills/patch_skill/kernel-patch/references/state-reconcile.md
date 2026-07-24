# State Reconcile Rules

## Purpose

这个文档定义 `state -> HEAD` 的回填判定规则。

目标不是“因为 Git 更靠前，就直接把 state 改到最新”，而是：

- 只在确认 `test_branch` 上新增提交严格对应原 patch 序列后续补丁时，允许回填
- 把“自动回填”“人工确认后回填”“必须停止”明确分开

回填动作只能通过 `run_patch_sets.py --reconcile` 完成，不允许手工编辑 state 或 memory JSON。

## Core Principle

只有当 `target_branch..test_branch` 之间新增的提交，能被证明是：

- patch 序列中的连续后续区间
- 顺序正确
- 内容可接受

才允许把 state 更新到 Git 最新状态。

## Automatic Reconcile

同时满足以下条件时，允许自动回填：

1. `test_branch` 存在，且仍属于当前任务
2. `target_branch..test_branch` 的新增提交能按顺序列出
3. 新增提交能映射到 patch 列表中的连续后续补丁
4. 每个新增提交的校验结果都属于：
   - `identical`
   - `config-mapped-equivalent`
5. 当前仓库不处于未完成的 `git am` 中间态

## Manual Confirmation Reconcile

以下情况不应自动回填，但可以在人工确认后允许回填：

- `semantic-substitution-suspected`
- 原 patch 目标宏、函数或类型不存在，但目标仓库存在明确的等价或近似替代
- LLM 做的是局限在当前 patch 语义范围内的 API/宏适配

人工确认通过后，这类提交可以视为“可接受提交”，允许纳入回填范围。主流程中，这类 patch 应先进入 `confirm_semantic_substitution`，再通过 `run_patch_sets.py --accept-semantic-substitution ...` 继续。

## Macro Adaptation Rule

“要合入的宏定义不存在，但相似宏定义存在，LLM 正确识别并修改”：

- 不应视为 `boundary-drift`
- 应视为“语义适配待确认”
- 只有人工确认其符合迁移意图后，才允许作为可接受提交参与回填

必须同时满足：

1. 原 patch 目标宏在目标仓库中不存在
2. 目标仓库中存在明确相似、职责一致或语义等价的宏/接口
3. 修改范围没有扩展到当前 patch 语义之外
4. 没有顺手带入其他 patch 的内容

## Must Stop

以下任一情况命中，都必须停止，不能回填：

- `test_branch` 上混入 patch 序列之外的额外提交
- 新增提交无法映射为 patch 列表中的连续区间
- 提交顺序与 patch 顺序不一致
- 任一新增提交校验结果为：
  - `missing-hunk`
  - `different`
  - `boundary-drift`
  - `config-mapped-incomplete`
  - `config-target-missing`
  - `config-unmapped`
- 当前仓库仍处于 `git am` / `rebase-apply` 未完成状态
- 当前 state 与任务输入本身不匹配

## Fields To Sync After Reconcile

回填通过后，应同步这些字段：

- state:
  - `patch_set_index`
  - `commit_index`
  - `phase`
  - `last_patch_file`
  - `test_branch`
  - `final_head`
- memory:
  - `applied_commit_count`
  - `last_patch_set`
  - `last_commit_index`
  - `last_commit_id`
  - `last_next_action`

## Decision Table

### Allow Automatic Reconcile

- 新增提交严格对应 patch 序列的连续后续补丁
- 每个提交都通过：
  - `identical`
  - `config-mapped-equivalent`

### Allow Reconcile After Manual Confirmation

- 连续后续补丁映射成立
- 但存在 `semantic-substitution-suspected`
- 且人工确认这些差异属于可接受的语义适配

### Reject Reconcile

- 存在额外手工提交
- 存在非连续提交
- 存在真正的 `boundary-drift`
- 存在 config 丢失或删除不完整
- 当前仓库仍停在未完成 `git am` 状态
