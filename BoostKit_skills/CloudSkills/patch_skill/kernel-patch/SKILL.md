---
name: kernel-patch
description: "内核补丁迁移与冲突解决工作流。用于导出 Git 提交为 patch、检查补丁是否已存在、分析 .rej 冲突、按顺序批量合入 patch_sets，并在每个补丁合入后执行确定性 post-apply 门禁校验与自动复检循环。适用于 Linux 内核补丁迁移、config 文件映射同步、顺序合入多个补丁集、补丁边界漂移检查和补丁合入质量校验。"
---

# Kernel Patch Workflow

优先使用 skill 自带脚本。不要为了编排批量补丁合入而额外新写 shell/python 脚本；如果发现 skill 能力缺口，停止并报告缺口。

## Main entrypoints

批量合入 patch sets：

- 使用 [scripts/run_patch_sets.py](scripts/run_patch_sets.py)
- 这是批量合入的唯一 orchestrator
- 正式入口仍然是一个批量 payload；CLI 同时支持 `--input-json` / `--input-json-inline` 和扁平兼容参数
- 完整 payload 用于定义任务和校验恢复上下文，不表示每次都需要重新全量导出所有 patch

单功能任务：

- 检查或收尾任务快照： [scripts/task_memory.py](scripts/task_memory.py)
- 导出补丁： [scripts/export_patches.py](scripts/export_patches.py)
- 分析边界漂移： [scripts/analyze_patch_boundary.py](scripts/analyze_patch_boundary.py)
- 分析 `.rej`： [scripts/analyze_rej_file.py](scripts/analyze_rej_file.py)
  - 默认使用精简输出；只有需要查看完整 hunk 正文时才传 `--output-level full`
- 应用单补丁： [scripts/apply_patches.py](scripts/apply_patches.py)
- 校验已合入提交： [scripts/validate_applied_patch.py](scripts/validate_applied_patch.py)

## Path rules

1. 不要硬编码 skill 安装路径。
2. 运行脚本时可以在任意 cwd；脚本自身会解析 skill 内部路径。
3. 用户工作对象路径可以是绝对路径或相对路径；脚本入口会统一规范化。
4. 返回结果中的路径默认使用绝对路径。

## Batch workflow

对批量补丁合入，只允许这个流程：

1. 先运行 `task_memory.py inspect --patches-dir ...`
   - 如果返回 `exists: false`，说明任务尚未开始，可以开始新的批量任务
   - 如果返回 `task_status: running`、`revalidating`、`auto_fixing`、`waiting_after_continue`、`completed_pending_review` 或 `needs_human`，说明有未结束任务，必须先按 state 恢复，不能假装是新任务
   - 如果返回 `task_status: ended`，说明旧任务已结束；不要再把这份 state 当活动上下文读取
2. 运行 `run_patch_sets.py`
2. 如果返回 `resolve_conflicts`：
   - 先 `git add -A`
   - 用 `analyze_rej_file.py` 分析 `.rej`
   - 按原 hunk 解决冲突
   - 删除源码目录中的 `.rej`，保留 reject 目录备份
   - 运行 `git am --continue`
   - 再次调用 `run_patch_sets.py --after-continue ...` 继续；默认会从批量 state 文件自动恢复 `test_branch`
   - 不要在“无冲突、未执行 `git am --continue`”的场景下调用 `--after-continue`
3. 如果返回 `handoff_review`：
   - 使用返回里的 `review_prompt` 原样拉起 `patch-validator`
   - 不要自行改写 prompt 里的仓库、分支或补丁目录
4. 如果返回 `escalate_human`：
   - 这表示当前补丁在自动复检循环中仍未通过，或命中不可自动修复状态
   - 先根据 `validation_status` / `artifact_path` 判断是“需要修改当前 HEAD”还是“只需要人工接受当前结果”
   - 如果已经手工修改当前 HEAD 或 amend 了提交，调用 `run_patch_sets.py --resume-after-fix`
   - 如果不需要修改当前 HEAD，只是接受当前结果，调用 `run_patch_sets.py --human-decision ...`
5. 如果发现 state 明显落后于实际仓库提交，不要手工改 JSON，也不要手工估算已合入数量：
   - 直接运行 `run_patch_sets.py --reconcile ...`
   - 只有 `run_patch_sets.py` 可以恢复批量游标
   - 如果 `--after-continue` 提示 state 与 test branch 历史不一致，也走 `--reconcile`
   - 详细回填判定规则见 `references/state-reconcile.md`
6. 如果 `patch-validator` 确认整个任务结束，再运行 `task_memory.py mark-ended --patches-dir ... --final-head ...`
7. 如果返回 `stop_validation_failed`、`stop_invalid_input`、`stop_manual_recovery_required` 或 `escalate_human`，立即停止

不要做这些事：

- 不要自己写 `apply_all.sh` 之类的 orchestrator
- 不要用大段 `python -c` 重写 skill 逻辑
- 不要绕过 skill 直接批量 `git am`
- 不要在批量流程里使用 `git am --skip`
- 不要手工编辑 state 文件来“同步进度”
- 批量任务开始后，不要退化为手工逐个调用 `apply_patches.py`

## Read discipline

排查和冲突处理时，默认只读当前补丁、当前文件、当前 hunk 需要的最小上下文。

硬规则：

- 先用搜索定位，再读局部上下文；优先 `rg`，再用 `sed -n start,endp` 或等价方式读取约 20-80 行
- 不要无理由整文件读取；只有文件很短或必须核对整体结构时才允许
- 不要先看完整 `git log`；默认只看 `git log --oneline -n N`、指定路径日志或指定提交
- 不要先看完整 `git diff`；默认只看当前 patch 对应文件块，或指定路径的局部 diff
- 如果 `.rej` 只涉及一个文件，只查看这个文件的局部上下文；不要顺手扩展到同一 patch 的其他文件
- 如果需要确认当前 patch 的预期改动，只查看当前 patch 文件里当前目标文件的 diff 块；不要先读整份 patch

汇报进度时也只基于结构化结果，不要猜：

- 优先读取 `task_memory.py inspect` 返回和 state 文件，不要依赖之前聊天里的自然语言总结
- 用 `run_patch_sets.py` 返回里的 `patch_set_index`、`commit_index` 和最后一条 `results` 判断当前进度
- 如果最后一条记录已经属于下一个 patch set，但 `git_am_status` 是 `paused`，说明已经进入下一个 patch set，只是卡在当前补丁
- 不要把“停在某个 patch set 的某个补丁冲突”表述成“还没有进入下一个 patch set”

## Config mapping

用户主入口提供 `config_files`。批量入口会把它们转换成内部 `config_targets`。

规则：

- `Kconfig` / `Kconfig.*` 属于配置定义文件，直接按原路径应用，不参与映射
- 如果 patch 只涉及一个需要映射的 defconfig/config 源文件，映射到所有用户提供的 `config_files`
- 如果 patch 涉及多个需要映射的 defconfig/config 源文件且无法唯一映射，停止并返回 `config-mapping-required`
- config 路径变化本身不算错误；但映射目标文件必须保留 patch 中要求新增或删除的配置行、注释、空行和分组标题

## Validation rules

每个补丁 `git am --continue` 成功后必须校验。

允许通过：

- `identical`
- `config-mapped-equivalent`

需要自动复检循环（最多 4 轮）：

- `different`
- `semantic-substitution-suspected`
- `missing-hunk`

需要停止：

- `config-mapped-incomplete`
- `config-target-missing`
- `config-unmapped`

边界预分析中：

- `warning-symbol-overlap` 只记录，不阻断
- `already-absorbed` / `requires-prerequisite` 也仅作为 warning，真正阻断以 post-apply 门禁为准

## Batch state

- `run_patch_sets.py` 会把批量进度写入 `patches_dir/.kernel_patch_state.json`
- patch 导出缓存会记录在 state 的 `runtime.exported_patch_index` 中；恢复时优先复用已有 `commit -> patch_file` 映射，仅在缺失时按需重导当前所需 commit
- 批量恢复主键是 `patch_set_index + commit_index`；目标分支上的 commit SHA 仅作为当前观测值记录，`--amend` 后允许变化
- 如果冲突后重新调用 `run_patch_sets.py --after-continue ...`，未显式传 `--resume-*` 时会尝试自动恢复
- 如果仓库进度已经超前于 state，调用 `run_patch_sets.py --reconcile ...` 重新对齐
- 如果是宏定义/接口相似替代导致的差异，不应直接视为需要修复的差异；按 `references/state-reconcile.md` 中的人工确认规则处理
- 显式传入 `--resume-test-branch`、`--resume-set-index`、`--resume-commit-index` 时，CLI 参数优先
- 如果 state 文件与当前任务的 `target_repo`、`target_branch` 或 `patch_sets` 不匹配，脚本会停止而不是误复用旧任务状态
- 批量合入成功后，state 会进入 `completed_pending_review`，并带上 `review_prompt` 供后续拉起 `patch-validator`
- state 文件的 `phase` 语义：
  - `running`：任务进行中
  - `revalidating`：自动复检循环中
  - `auto_fixing`：自动修复/重试阶段
  - `waiting_after_continue`：冲突解决后等待 `--after-continue`
  - `needs_human`：自动循环无法收敛，升级人工
  - `completed_pending_review`：合入完成，等待 review
  - `ended`：任务已结束；下次进入 skill 时不要再把它当作活动任务读取
  - `aborted`：任务异常停止

## References

- Config 映射和校验细节：见 [references/config-files.md](references/config-files.md)
- 冲突分类与处理决策：见 [references/conflict-resolution.md](references/conflict-resolution.md)
- State 回填与人工确认规则：见 [references/state-reconcile.md](references/state-reconcile.md)
- CLI 和端到端示例：见 [references/examples.md](references/examples.md)
