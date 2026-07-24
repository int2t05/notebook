---
name: patch-validator
description: 校验 git format-patch 格式的补丁文件与目标 git 仓库的合入情况。支持两种模式：(1) 应用校验，逐个分析每个补丁的每个 hunk 是否可以应用到目标分支；(2) 已合入差异校验，将本地补丁与目标仓库中已合入提交的 diff 做逐行比较，识别缺失行、额外行和删除侧不一致，并生成详细的 Markdown 格式报告。当用户需要验证补丁是否可以应用到目标仓库、检查本地补丁与上游已合入补丁是否完全一致、或生成补丁状态报告时使用此技能。
---

# Patch Validator

## Overview

Patch Validator 是一个用于校验 git format-patch 格式补丁文件的技能。它支持两类分析：

- `applicability`: 检查补丁是否还能应用到目标分支
- `merged-diff`: 先遍历本地 `.patch` 文件，再为每个 patch 在目标分支中定位对应提交并检查两者 diff 是否完全一致

**适用场景**:
- 在应用补丁前预检查兼容性
- 验证补丁集是否能顺利迁移到目标分支
- 检查本地补丁与目标仓库已合入补丁是否有遗漏或额外变更
- 生成补丁应用状态报告
- 排查补丁冲突原因

## Quick Start

```bash
# 基本用法：应用校验
/patch-validator --patches /path/to/patches --repo /path/to/repo --branch main --mode applicability

# 基本用法：已合入差异校验
/patch-validator --patches /path/to/patches --repo /path/to/repo --branch main --mode merged-diff

# 完整参数示例
/patch-validator \
  --patches ./patches \
  --repo /path/to/linux-source \
  --branch stable-6.6 \
  --upstream-branch main \
  --mode merged-diff \
  --output validation_result.json
```

## Workflow

### 1. 准备工作

在运行校验之前，确保：

1. **补丁目录**: 包含 `.patch` 格式文件的目录
2. **目标仓库**: 有效的 git 仓库路径
3. **目标分支**: 要校验的目标分支名称

```bash
# 生成补丁文件示例
git format-patch -o patches/ origin/main..HEAD

# 确认目标分支
cd /path/to/repo
git checkout target-branch
```
***重要**
1. 如果用户在描述中给了补丁文件名，但名称明显是截断的、带省略的、或只给了前半段：

1.1 先读取补丁文件头中的 `Subject:` 和 `From <sha>`，不要只依赖截断后的文件名
1.2 目标提交到本地 `.patch` 的映射顺序固定为：`subject -> hash -> diff`
1.3 `Subject:` 如果折行，必须把后续 header continuation line 拼回完整标题后再匹配
1.4 只有在以上三步都无法唯一定位时，才判断本地补丁不存在或匹配歧义

不要因为用户提供的是截断名称，或者本地 patch 文件名被文件系统截断，就直接下结论说文件不存在。

### 2. 执行校验

使用 `validate_patches.py` 脚本执行校验：

```bash
python3 scripts/validate_patches.py \
  --patches /path/to/patches \
  --repo /path/to/repo \
  --branch main \
  --mode applicability \
  --tolerance 3 \
  --threshold 0.9 \
  --output validation_result.json

# 已合入差异校验
python3 scripts/validate_patches.py \
  --patches /path/to/patches \
  --repo /path/to/repo \
  --branch main \
  --upstream-branch origin/main \
  --mode merged-diff \
  --output validation_result.json
```

**参数说明**:

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--patches, -p` | 补丁文件目录 | 必需 |
| `--repo, -r` | 目标 git 仓库路径 | 必需 |
| `--branch, -b` | 目标分支 | HEAD |
| `--upstream-branch` | `merged-diff` 模式下用于限制搜索范围的上游分支；默认自动探测 | 空 |
| `--global-search` | 扫描整个目标分支历史，关闭默认的上游范围收缩 | False |
| `--mode` | `applicability` 或 `merged-diff` | `applicability` |
| `--tolerance, -t` | 行号偏移容忍度（行） | 3 |
| `--threshold` | 相似度阈值 | 0.9 |
| `--commit` | `merged-diff` + `explicit` 模式下指定目标提交 hash | 空 |
| `--output, -o` | JSON 输出文件 | validation_result.json |
| `--no-git-apply` | 跳过 git apply --check | False |

### 3. 生成报告

使用校验结果生成 Markdown 报告：

```bash
python3 scripts/generate_report.py \
  --input validation_result.json \
  --output patch_validation_report.md
```

### 4. 解读结果

查看生成的报告了解：
- `applicability` 模式下的 hunk 匹配状态和失败原因
- `merged-diff` 模式下的补丁匹配状态
- 本地补丁缺失的新增行、目标提交额外的新增行、删除侧不一致

## Hunk 状态说明

| 状态 | 图标 | 含义 |
|------|------|------|
| CLEAN | ✅ | 无误差，可精确应用 |
| VARIATION | ⚠️ | 存在误差，有轻微偏移但可应用 |
| FAILED | ❌ | 错误，无法应用 |

## 已合入差异状态说明

| 状态 | 图标 | 含义 |
|------|------|------|
| IDENTICAL | ✅ | 本地补丁与目标仓库已合入提交的 diff 完全一致 |
| DIFFERENT | ❌ | 已找到对应提交，但 diff 内容存在差异 |
| UNMATCHED | ❓ | 无法定位对应已合入提交 |
| AMBIGUOUS | ⚠️ | 找到多个候选提交，无法安全自动判断 |

### 状态判定逻辑

1. **CLEAN (无误差)**
   - 上下文行完全匹配
   - 相似度 = 100%
   - 无行号偏移

2. **VARIATION (存在误差)**
   - 上下文行在容忍范围内找到匹配
   - 相似度 >= 阈值 (默认 90%)
   - 可能有行号偏移或空白字符差异

3. **FAILED (错误)**
   - 无法在容忍范围内找到匹配
   - 相似度 < 阈值
   - 文件不存在或有代码冲突

## 模糊匹配算法

当精确匹配失败时，使用模糊匹配算法：

```python
# 在容忍范围内搜索最佳匹配
for offset in range(-tolerance, tolerance + 1):
    actual_pos = expected_start + offset
    similarity = calculate_similarity(context_lines, file_content, actual_pos)
    if similarity > threshold:
        return VARIATION
```

**关键参数**:
- `tolerance`: 搜索范围，默认 ±3 行
- `threshold`: 相似度阈值，默认 0.9 (90%)

## 依赖

### Python 依赖

```bash
# 必需
pip install unidiff  # 推荐用于更好的补丁解析

# 可选（如已安装 git 命令行工具则不需要）
pip install GitPython
```

### 系统依赖

- Python 3.7+
- Git 命令行工具

## 常见问题

### Q: 如何处理 VARIATION 状态的 hunks？

A: VARIATION 状态通常可以正常应用。`git apply` 命令可以自动处理轻微的行号偏移。建议：
- 检查偏移量是否合理
- 确认没有遗漏依赖补丁
- 使用 `git apply --verbose` 查看详情

### Q: 如何处理 FAILED 状态的 hunks？

A: FAILED 状态需要手动处理：
1. 检查目标文件是否存在
2. 确认目标分支是否正确
3. 查看上下文预览，手动查找匹配位置
4. 考虑使用 `git apply --3way` 三方合并
5. 必要时手动合并冲突

### Q: 如何调整匹配精度？

A: 通过参数调整：
- 增大 `--tolerance` 允许更大的行号偏移
- 降低 `--threshold` 允许更低的相似度匹配
- 注意：过低的阈值可能导致误匹配

### Q: `merged-diff` 模式会把纯空白差异当成补丁差异吗？

A: 不会。`merged-diff` 在比较 hunk 内容时会忽略缩进和连续空白字符差异，重点识别真实的新增行、删除行和文本内容变化。

### Q: `merged-diff` 模式如何定位“目标提交 -> 本地 patch 文件”？

A: 固定使用以下顺序：
- 先用完整 `Subject:` 做规范化匹配，支持本地文件名截断
- 再用提交 hash 前缀与 patch 文件名前缀或 patch header 中的 `From <sha>` 匹配
- 最后用 `git patch-id --stable` 做 diff 级别兜底匹配
- 若任一步骤出现多个候选，则直接标记为 `AMBIGUOUS`

### Q: `merged-diff` 默认会扫描整个目标分支吗？

A: 不会。默认会先尝试自动探测 `--branch` 的 upstream，并只扫描 `merge-base(upstream, branch)..branch` 之间的非 merge 提交。只有在以下两种场景才会改用其他策略：
- 你显式传了 `--upstream-branch`
- 你显式传了 `--global-search`

如果 upstream 无法自动探测，脚本会直接报错，并提示你补充 `--upstream-branch` 或改用 `--global-search`。

## Resources

### scripts/

- `validate_patches.py` - 核心校验脚本，支持 `applicability` 与 `merged-diff` 两种模式
- `generate_report.py` - 报告生成脚本，从 JSON 结果生成 Markdown 报告

### references/

- `report_template.md` - 报告解读指南，包含常见误差模式和排查方法

---

*此技能用于 Linux 内核开发和维护场景中的补丁管理和校验*
