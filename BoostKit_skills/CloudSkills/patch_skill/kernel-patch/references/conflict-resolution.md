# Conflict Resolution

## Required sequence

批量流程返回 `resolve_conflicts` 后，只允许按这个顺序执行：

1. `git add -A`
2. `analyze_rej_file.py`
3. 只按原 hunk 解决冲突
4. 删除源码目录中的 `.rej`
5. `git am --continue`
6. 重新调用 `run_patch_sets.py --after-continue ...`

批量任务续跑时，优先继续调用 `run_patch_sets.py`。不要改成手工逐个调用 `apply_patches.py`，否则需要调用方自己维护 `test_branch`，容易意外新建分支。

## Conflict classes

### `config-sync`

特征：

- 目标文件是 defconfig / `.config` / `.cfg`
- 或 `.rej` 中主要内容是 `CONFIG_*`

处理：

- 只同步到入口提供的 `config_files` 推导出的目标 config
- 不要把原 defconfig 路径当作最终提交目标

`Kconfig` / `Kconfig.*` 冲突不属于 `config-sync`，按普通源码冲突处理。

### `manual-edit-risk`

特征：

- 删除侧不一致
- hunk 被改写
- 有额外非 config 代码变化

处理：

- 重新对齐原 hunk
- 不要顺手吸收相邻补丁内容
- 默认只修改当前 `.rej` 指向的文件
- 默认只修改当前 hunk 附近的最小上下文
- 不要因为猜测依赖关系，就把当前 patch 里其他文件的改动迁移到当前冲突文件
- 如果当前冲突文件是 `arm.c`，不要顺手去补别的文件；如果当前冲突不在 `arm.c`，也不要把 `arm.c` 里的改动挪过来
- 如果怀疑当前 patch 还有别的必要修改，先查看当前 patch 中该文件对应的 diff 块，再决定；不要直接猜

### `semantic-substitution-suspected`

特征：

- 文本不同但可能是 API 适配

处理：

- 自动复检循环会先跑（最多 4 轮）
- 如果返回 `escalate_human` 再人工介入
- 优先检查是否做了 hunk 外的额外改动
- 优先检查是否把原 patch 其他文件里的改动错误加到了当前文件

## Stop conditions

这些状态必须停止，不要继续下一个补丁：

- `different`
- `config-mapped-incomplete`
- `config-target-missing`
- `config-unmapped`

## Hard rules

- 永远先 `git add -A`
- 永远用 `git am --continue`
- 不要用 `git commit`
- 不要新写 skill 外的 orchestrator 脚本
- 不要用整文件阅读替代局部定位；先搜再看局部
- 当前 `.rej` 只覆盖一个文件时，不要扩展修改到别的文件
- 原 patch 修改多个文件、但当前冲突只出在一个文件时，只解决冲突文件中的拒绝 hunk；其他无冲突文件默认视为 `git am` 已正常处理
