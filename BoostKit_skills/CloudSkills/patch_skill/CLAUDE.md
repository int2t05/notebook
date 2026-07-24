# Project Instructions

这个仓库中的 `kernel-patch` 是一个受约束的批量补丁合入 workflow。

当任务涉及 `kernel-patch`、批量 patch set 合入、冲突恢复、config 映射、patch review handoff 时，必须先读取：

- `kernel-patch/SKILL.md`
- `kernel-patch/references/examples.md`

## Kernel Patch Guardrails

- 批量补丁合入的唯一 orchestrator 是 `kernel-patch/scripts/run_patch_sets.py`
- 不要自己编排批量 `git am`
- 不要自己写临时 shell/python orchestrator 替代 `run_patch_sets.py`
- 不要在批量流程里使用 `git am --skip`
- 不要手工编辑 `.kernel_patch_state.json` 或 `.kernel_patch_memory.json`
- 不要手工估算“已经合入多少补丁”
- 不要把 `git status`、零散 `git log` 或主观判断当作“批量已完成”的依据

## Required Batch Flow

批量补丁任务只能按这个顺序执行：

1. 先运行 `kernel-patch/scripts/task_memory.py inspect`
2. 再运行 `kernel-patch/scripts/run_patch_sets.py`
3. 如果冲突暂停：
   - `git add -A`
   - `git am --continue`
   - 再次运行 `kernel-patch/scripts/run_patch_sets.py --after-continue`
4. 如果发现仓库进度领先于 state/memory：
   - 只能运行 `kernel-patch/scripts/run_patch_sets.py --reconcile`
5. 如果返回 `handoff_review`：
   - 必须使用返回的 `review_prompt` 拉起 `patch-validator`
6. `patch-validator` 完成后，才允许把任务标记为结束

## Completion Rules

- 只有 `run_patch_sets.py` 返回 `next_action: "handoff_review"`，才允许说“合入阶段完成”
- 只有 `patch-validator` 完成后，才允许说“整个任务结束”
- 如果返回以下任一状态，必须停止，不得继续手工推进：
  - `stop_validation_failed`
  - `stop_boundary_drift`
  - `stop_invalid_input`
  - `stop_manual_recovery_required`

## Escalation Rule

如果你发现当前任务需要做的动作不在 `run_patch_sets.py`、`task_memory.py`、`analyze_rej_file.py` 和 `patch-validator` 的既定流程里，不要自行发挥，直接报告 workflow 能力缺口。
