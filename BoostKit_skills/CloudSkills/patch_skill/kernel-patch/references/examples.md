# Examples

## Batch patch-set apply

批量合入只用 `run_patch_sets.py`。

进入任务前先检查 state：

```bash
python3 /path/to/kernel-patch/scripts/task_memory.py inspect \
  --patches-dir /tmp/patches
```

- `exists: false`：说明任务还没开始
- `task_status: running` / `revalidating` / `auto_fixing` / `waiting_after_continue` / `needs_human` / `completed_pending_review`：说明有未结束任务，先恢复，不要重开
- `task_status: ended`：说明旧任务已经结束，不要再把这份 state 当活动上下文读取

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json
```

兼容的扁平 CLI 调用：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --target-repo /path/to/target_repo \
  --target-branch main \
  --reject-dir /tmp/rejects \
  --patches-dir /tmp/patches \
  --config-files /path/to/target_repo/config.aarch64 /path/to/target_repo/config.aarch64-64k \
  --patch-sets-json '[{"name":"TWED","source_repo":"/path/to/source_repo","commits":["abc123","def456"]}]'
```

默认 state 文件会写到 `patches_dir/kernel_patch_state.json`。如果任务中途因冲突暂停，后续继续时可以依赖这个文件恢复测试分支、进度和任务语义。如果批量合入全部成功，脚本会返回 `next_action: "handoff_review"`，并附带可直接触发 `patch-validator` 的 `review_prompt`。

`input.json` 示例：

```json
{
  "target_repo": "/path/to/target_repo",
  "target_branch": "main",
  "reject_dir": "/tmp/rejects",
  "patches_dir": "/tmp/patches",
  "config_files": [
    "/path/to/target_repo/config.aarch64",
    "/path/to/target_repo/config.aarch64-64k"
  ],
  "patch_sets": [
    {
      "name": "TWED",
      "source_repo": "/path/to/source_repo",
      "commits": ["abc123", "def456"]
    }
  ]
}
```

如果返回 `resolve_conflicts`：

1. 解决 `.rej`
2. 在目标仓库执行 `git add -A`
3. 执行 `git am --continue`
4. 重新运行：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --after-continue
```

只在这两个前提同时成立时使用 `--after-continue`：

- 刚刚处理完 `.rej` 并执行过 `git am --continue`
- 当前 task state 仍停在 `waiting_after_continue`

如果当前没有冲突恢复中的 `git am --continue`，或者 test branch 历史与 state 不一致，不要继续重试 `--after-continue`，直接运行 `run_patch_sets.py --reconcile`。

冲突处理时使用这个检查顺序，不要跳步：

1. 运行 `analyze_rej_file.py`，确认当前 `.rej` 的目标文件、hunk 和冲突类型
2. 用搜索在目标文件中定位当前 hunk 落点
3. 只读取目标文件的局部上下文，不要先整文件读取
4. 如果需要确认原 patch 意图，只查看当前 patch 文件里当前目标文件对应的 diff 块，不要先读整份 patch
5. 只修改当前 `.rej` 对应文件里当前 hunk 需要的最小内容
6. `git add -A`
7. `git am --continue`
8. 重新运行 `run_patch_sets.py --after-continue ...`

如果返回 `confirm_semantic_substitution`：

1. 查看返回中的 `semantic_confirmation.validation`
2. 让人类确认该 API/宏/类型替代是否语义等价
3. 确认可接受后运行：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --accept-semantic-substitution
```

如果返回 `escalate_human`：

1. 查看 `validation_status`、`auto_iteration_count`、`artifact_path`
2. 到 `artifact_path` 对应的 gate JSON 查看本轮详细差异
3. 如果已经手工修改当前 HEAD 或 amend 了提交，运行：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --resume-after-fix
```

4. 如果不需要改动当前 HEAD，只是人工接受当前结果，运行：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --human-decision continue
```

5. 如果当前差异属于明确的接受类型，也可以直接运行：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --human-decision accept-semantic
```

或：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --human-decision accept-hunk
```

避免这些坏模式：

- 不要先读完整 `git diff HEAD~1`
- 不要先读完整 `git log`
- 不要因为当前 patch 同时改了别的文件，就把那些改动手工搬到当前冲突文件
- 不要把“已经进入下一个 patch set 的第一个冲突补丁”误报成“还停留在上一个 patch set”

如果需要显式覆盖自动恢复，也可以传：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --resume-test-branch auto-patch-20260312_123456 \
  --resume-set-index 0 \
  --resume-commit-index 0 \
  --after-continue
```

如果仓库提交已经超前于 state，不要手工修改 JSON，直接让 orchestrator 对齐：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --reconcile
```

详细回填判定规则见 `references/state-reconcile.md`。如果是宏定义或接口的相似替代导致差异，也按该文档中的人工确认路径处理，不直接按 `boundary-drift` 处理。

如果需要显式指定测试分支：

```bash
python3 /path/to/kernel-patch/scripts/run_patch_sets.py \
  --input-json /path/to/input.json \
  --resume-test-branch auto-patch-20260312_123456 \
  --reconcile
```

常见错误：

- `unrecognized arguments`：使用了旧的非法参数组合；改用 JSON 入口或上面的扁平兼容参数
- `saved test branch does not exist`：state 文件指向的测试分支已经失效，需要重新启动批量任务
- `boundary-analysis-failed`：边界分析步骤失败，脚本会返回结构化错误而不是 traceback
- `stop_manual_recovery_required`：当前 test branch 已经偏离期望 patch 序列，不能安全自动恢复，需要人工处理
- `escalate_human`：自动复检循环达到上限或命中不可自动修复状态，需要人工修复后再继续

成功交接 review 的示例：

```text
/patch-validator 帮我检查一下 /path/to/target-repo 的分支 auto-patch-20260304_112649 合入的补丁，与 /path/to/patches 里的补丁是否存在差异。
```

review 完成后，把 state 标记为结束：

```bash
python3 /path/to/kernel-patch/scripts/task_memory.py mark-ended \
  --patches-dir /path/to/patches \
  --final-head abcdef123456
```

## Export only

```bash
python3 /path/to/kernel-patch/scripts/export_patches.py \
  --source-repo /path/to/source_repo \
  --output-dir /tmp/patches \
  --commits abc123 def456
```

## Analyze one reject file

```bash
python3 /path/to/kernel-patch/scripts/analyze_rej_file.py \
  --rej-file-path /tmp/rejects/file.rej \
  --repo-path /path/to/target_repo
```

需要查看完整 hunk 正文时，显式切换到完整模式：

```bash
python3 /path/to/kernel-patch/scripts/analyze_rej_file.py \
  --rej-file-path /tmp/rejects/file.rej \
  --repo-path /path/to/target_repo \
  --output-level full
```

## Validate one applied commit

```bash
python3 /path/to/kernel-patch/scripts/validate_applied_patch.py \
  --patch-file /tmp/patches/abc123.patch \
  --repo-path /path/to/target_repo \
  --commit-ref HEAD \
  --config-targets '{"arch/arm64/configs/openeuler_defconfig":["config.aarch64","config.aarch64-64k"]}'
```

## Development-only imports

如果只是在开发或调试 skill，可以 import 函数；这不是批量合入主流程。

```python
from export_patches import export_patches
from apply_patches import apply_single_patch
from validate_applied_patch import validate_applied_patch
```
