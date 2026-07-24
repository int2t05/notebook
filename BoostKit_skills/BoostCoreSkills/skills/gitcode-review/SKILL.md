---
name: gitcode-review
description: GitCode 平台的 Pull Request 代码审查专家。当用户需要审查 GitCode 上的 PR 时使用，包括：(1) 查看 PR 列表，(2) 分析代码变更，(3) 提供中文代码审查报告，(4) 可选地将审查结果提交到 PR 评论区。支持通过 /review 命令或直接提示词触发。
---

# GitCode PR 代码审查 Skill

本 Skill 提供 GitCode 平台的专业代码审查能力，输出中文审查报告。

## 快速开始

### 在 Claude Code 中使用

用户可以通过以下方式触发审查：

```bash
/review              # 列出所有打开的 PR
/review <PR编号>     # 审查指定的 PR
```

### 在其他环境中使用

用户可以直接说：
- "审查这个 PR"
- "帮我 review 一下 PR #2"
- "查看最近的 Pull Request"

## 审查流程

按以下步骤执行代码审查：

### 1. 获取 PR 信息

**如果用户未指定 PR 编号**：

使用 GitCode MCP 工具列出所有 PR：

```
使用 mcp__gitcode__list_pull_requests 工具
参数：owner（仓库所有者）、repo（仓库名称）
```

从 PR 列表中选择最近的或让用户选择要审查的 PR。

**如果用户指定了 PR 编号**：

直接获取该 PR 的详细信息：

```
使用 mcp__gitcode__get_pull_request 工具
参数：owner、repo、pull_number
```

### 2. 获取代码变更

使用 GitCode API 的 compare 端点获取 PR 的 diff：

```bash
curl -s "https://gitcode.com/api/v5/repos/{owner}/{repo}/compare/{base_sha}...{head_sha}?access_token={token}"
```

从 PR 信息中提取：
- `base.sha` - 基础分支的 commit SHA
- `head.sha` - PR 分支的 commit SHA

API 返回的 `files` 数组包含每个文件的：
- `filename` - 文件路径
- `status` - 修改状态（modified/added/deleted）
- `additions` - 新增行数
- `deletions` - 删除行数
- `patch` - diff 格式的代码变更

### 3. 分析代码变更

对每个修改的文件进行分析，关注：

**代码质量**：
- 代码风格是否一致
- 命名是否清晰
- 是否遵循项目约定

**代码正确性**：
- 逻辑是否正确
- 是否有潜在的 bug
- 边界条件处理

**性能影响**：
- 是否有性能问题
- 算法复杂度
- 资源使用

**安全考虑**：
- 是否有安全漏洞
- 输入验证
- 权限检查

**可维护性**：
- 代码是否易于理解
- 是否需要注释
- 是否有重复代码

### 4. 生成中文审查报告

按以下格式输出审查报告：

```markdown
## 代码审查：PR #{编号} - {标题}

### 概述
[简要说明 PR 的目的和主要变更]

### 变更详情
- **文件**: {文件路径}
- **位置**: 第 X-Y 行
- **变更**: +{新增行数} 行，-{删除行数} 行

### 代码质量分析

**优点：**
- ✅ [列出做得好的地方]

**需要改进的地方：**

1. **{问题类别}**
   ```{语言}
   // 当前写法
   {当前代码}

   // 建议改为
   {改进后的代码}
   ```
   - [说明改进原因]

### 潜在问题和风险

1. **{问题标题}**
   - [详细说明]
   - [建议的解决方案]

### 建议的改进版本

```{语言}
{完整的改进代码示例}
```

### 总体评价

**评分**: X/10

**总结**:
- [总体评价]
- [主要优点]
- [主要问题]

**建议操作**:
1. [具体的改进建议]
2. [测试建议]
3. [其他建议]
```

### 5. 询问是否提交评论

审查报告生成后，询问用户：

```
是否需要将此审查报告提交到 PR #{编号} 的评论区？

如果需要，我将使用 mcp__gitcode__create_pull_request_comment 工具提交评论。
```

如果用户同意，使用以下工具提交：

```
使用 mcp__gitcode__create_pull_request_comment 工具
参数：
  - owner: 仓库所有者
  - repo: 仓库名称
  - pull_number: PR 编号
  - body: 审查报告的 Markdown 内容
```

## 审查最佳实践

参考 `references/review-guidelines.md` 了解详细的代码审查指南。

## 注意事项

1. **保持客观和建设性**：提供具体的改进建议，而不是简单的批评
2. **关注重要问题**：优先指出安全、性能和正确性问题
3. **提供示例**：用代码示例说明建议的改进
4. **考虑上下文**：理解 PR 的目的和项目的整体架构
5. **尊重作者**：认可做得好的地方，鼓励持续改进

## 环境要求

- 需要配置 GitCode MCP 服务器
- 需要有效的 GITCODE_TOKEN 环境变量
- 需要对目标仓库有读取权限

## 故障排除

**问题：无法获取 PR 信息**
- 检查 GITCODE_TOKEN 是否有效
- 确认对仓库有访问权限
- 验证 owner 和 repo 参数是否正确

**问题：diff 信息为空**
- 检查 PR 是否已经合并
- 确认 base 和 head SHA 是否正确
- 尝试使用 PR 的 diff_refs 中的 SHA

**问题：无法提交评论**
- 确认对仓库有写入权限
- 检查 PR 是否仍然打开
- 验证评论内容格式是否正确
