# legal-compliance-checker

`legal-compliance-checker` 是一个用于开源项目法务合规检查的 Agent skill。它面向开源合规审计场景，支持检查代码仓库中的 LICENSE 文件、许可证类型验证、许可证冲突检测、文档许可证合规（CC BY 4.0 / CC BY-SA 4.0）以及第三方依赖合规性，并提供详细的合规报告。

## 主要能力

- **LICENSE 文件检查**：扫描项目根目录，识别各种命名约定的 LICENSE 文件（LICENSE、LICENSE.md、LICENSE.txt、COPYING 等）。
- **许可证类型验证**：识别 Apache 2.0、MIT、GPL v2/v3、LGPL v2.1/v3、BSD 2-Clause/3-Clause、Mulan PSL v2 等主流开源许可证。
- **许可证冲突检测**：检查主项目许可证与依赖许可证之间的兼容性，识别潜在的法律风险。
- **文档许可证检查**：验证文档目录（docs/、documentation/、doc/）下的 LICENSE 文件是否符合 CC BY 4.0 或 CC BY-SA 4.0 要求。
- **第三方依赖检查**：扫描 thirdpart/、thirdparty/、vendor/、external/ 目录，检查第三方组件的 LICENSE 合规性。
- **合规报告生成**：输出结构化的法务合规报告，包含合规状态、冲突分析、整改建议。

## 目录说明

- `SKILL.md`：skill 的主说明，包含全部检查规则、兼容性矩阵和工作流程。

## 快速使用

找到 skill 的安装目录，例如 `~/.agents/skills/legal-compliance-checker`。

**直接调用**

```
prompt: /legal-compliance-checker 检查当前项目的法务合规性
```

**指定检查目标**

```
prompt: /legal-compliance-checker 检查 /path/to/project 目录的法务合规性
```

**批量检查多个项目**

```
prompt: /legal-compliance-checker 检查 /projects/ 目录下所有项目的法务合规性
```

## 检查类别一览

| 类别 | 检查内容 | 典型模式 |
|------|----------|----------|
| LICENSE 文件 | 根目录许可证文件存在性 | `LICENSE`, `LICENSE.md`, `COPYING` |
| 许可证类型 | Apache/MIT/GPL/LGPL/BSD/Mulan PSL | `Apache License`, `MIT License`, `Mulan PSL` |
| 许可证冲突 | 主项目与依赖的许可证兼容性 | GPL v2 与 Apache 2.0 冲突 |
| 文档许可证 | CC BY 4.0 / CC BY-SA 4.0 | `Creative Commons Attribution`, `ShareAlike` |
| 第三方依赖 | thirdpart/vendor 目录下的 LICENSE | `thirdpart/sdma/LICENSE` |

## 支持的许可证类型

### 宽松许可证（Permissive）

| 许可证 | 关键词 | 特点 |
|--------|--------|------|
| MIT | `MIT License`, `Permission is hereby granted` | 最宽松，几乎无限制 |
| Apache 2.0 | `Apache License`, `Version 2.0` | 包含专利授权条款 |
| BSD 2-Clause | `BSD 2-Clause`, `Redistribution and use` | 简单宽松 |
| BSD 3-Clause | `BSD 3-Clause`, `Neither the name` | 禁止背书条款 |
| Mulan PSL v2 | `Mulan PSL`, `木兰宽松许可证` | 中国开源许可证 |

### Copyleft 许可证（传染性）

| 许可证 | 关键词 | 特点 |
|--------|--------|------|
| GPL v2 | `GNU General Public License`, `Version 2` | 强传染性，衍生作品必须 GPL |
| GPL v3 | `GNU General Public License`, `Version 3` | 包含专利和反 DRM 条款 |
| LGPL v2.1 | `GNU Lesser General Public License`, `Version 2.1` | 允许动态链接 |
| LGPL v3 | `GNU Lesser General Public License`, `Version 3` | LGPL v2.1 的升级版 |

### 文档许可证

| 许可证 | 关键词 | 特点 |
|--------|--------|------|
| CC BY 4.0 | `Creative Commons Attribution`, `CC BY 4.0` | 仅要求署名 |
| CC BY-SA 4.0 | `Attribution-ShareAlike`, `CC BY-SA 4.0` | 署名 + 相同方式共享 |

## 检查模式

### LICENSE 文件检查

扫描项目根目录下的 LICENSE 文件：

```bash
# 检查 LICENSE 文件是否存在
ls -la LICENSE* COPYING* 2>/dev/null

# 读取 LICENSE 内容
cat LICENSE | head -30
```

### 许可证类型识别

通过关键词匹配识别许可证类型：

```bash
# 识别 Apache 2.0
grep -i "Apache License" LICENSE | grep -i "Version 2.0"

# 识别 MIT
grep -i "MIT License" LICENSE

# 识别 Mulan PSL v2
grep -i "Mulan PSL" LICENSE

# 识别 GPL
grep -i "GNU General Public License" LICENSE

# 识别 BSD
grep -i "BSD.*Clause" LICENSE
```

### 文档许可证检查

检查文档目录下的 LICENSE 文件：

```bash
# 检查 docs 目录下的 LICENSE
ls -la docs/LICENSE* 2>/dev/null

# 识别 CC BY 4.0
grep -i "Creative Commons Attribution" docs/LICENSE | grep -v "ShareAlike"

# 识别 CC BY-SA 4.0
grep -i "ShareAlike" docs/LICENSE
grep -i "creativecommons.org/licenses/by-sa" docs/LICENSE
```

### 第三方依赖检查

扫描第三方依赖目录：

```bash
# 检查 thirdpart 目录
find thirdpart -name "LICENSE*" -o -name "COPYING*"

# 检查 vendor 目录
find vendor -name "LICENSE*" -o -name "COPYING*"

# 检查 external 目录
find external -name "LICENSE*" -o -name "COPYING*"
```

## 许可证兼容性矩阵

### 宽松许可证兼容性

| 主许可证 | 兼容的依赖许可证 | 不兼容的依赖许可证 |
|----------|------------------|-------------------|
| MIT | Apache 2.0, BSD, GPL, LGPL, Mulan PSL v2 | 无 |
| Apache 2.0 | MIT, BSD, GPL v3+, LGPL v3+, Mulan PSL v2 | GPL v2 |
| BSD 2-Clause | MIT, Apache 2.0, BSD 3-Clause, GPL, LGPL | 无 |
| BSD 3-Clause | MIT, Apache 2.0, BSD 2-Clause, GPL, LGPL | 无 |
| Mulan PSL v2 | MIT, Apache 2.0, BSD, GPL, LGPL | 无 |

### Copyleft 许可证兼容性

| 主许可证 | 兼容的依赖许可证 | 不兼容的依赖许可证 |
|----------|------------------|-------------------|
| GPL v2 | GPL v2, LGPL v2.1 | Apache 2.0, GPL v3, Mulan PSL v2 |
| GPL v3 | GPL v3, LGPL v3, Apache 2.0 | GPL v2 |
| LGPL v2.1 | GPL v2, LGPL v2.1 | Apache 2.0, GPL v3 |
| LGPL v3 | GPL v3, LGPL v3, Apache 2.0 | GPL v2 |

## 冲突检测逻辑

### 冲突严重级别

| 级别 | 描述 | 示例 |
|------|------|------|
| 🔴 **Critical** | 法律违规，必须修复 | GPL v2 项目使用 Apache 2.0 依赖 |
| 🟠 **Warning** | 潜在问题，需审查 | GPL v2 项目使用 GPL v3 依赖 |
| 🟡 **Info** | 提示信息 | 多个宽松许可证共存 |

### 常见冲突场景

#### 场景 1：GPL v2 与 Apache 2.0 依赖

```
主许可证: GPL v2
依赖许可证: Apache 2.0
冲突级别: 🔴 Critical
原因: Apache 2.0 的专利授权条款与 GPL v2 不兼容
解决方案: 升级到 GPL v3 或替换依赖
```

#### 场景 2：私有项目使用 GPL 依赖

```
主许可证: 私有/无
依赖许可证: GPL v3
冲突级别: 🔴 Critical
原因: GPL 要求整个项目必须开源
解决方案: 添加 GPL 许可证或移除依赖
```

#### 场景 3：LGPL v2.1 与 Apache 2.0 依赖

```
主许可证: LGPL v2.1
依赖许可证: Apache 2.0
冲突级别: 🟠 Warning
原因: Apache 2.0 专利授权可能与 LGPL v2.1 冲突
解决方案: 考虑升级到 LGPL v3
```

## 检查工作流程

```
Step 1: LICENSE 文件定位 → 扫描根目录下的 LICENSE 文件
    ↓
Step 2: 许可证类型识别 → 通过关键词匹配识别许可证类型
    ↓
Step 3: 依赖许可证扫描 → 扫描所有依赖的许可证
    ↓
Step 4: 冲突检测 → 检查主许可证与依赖许可证的兼容性
    ↓
Step 5: 文档许可证检查 → 验证 docs/ 目录下的 CC BY 4.0 / CC BY-SA 4.0
    ↓
Step 6: 第三方依赖检查 → 检查 thirdpart/vendor 目录的 LICENSE
    ↓
Step 7: 结果分类 → 按合规状态和冲突级别整理
    ↓
Step 8: 报告生成 → 输出结构化合规报告
```

## 合规要求

### 代码合规要求

- 根目录 **必须** 包含 LICENSE 文件
- 许可证类型 **必须** 是认可的开源许可证
- 第三方组件 **必须** 有自己的 LICENSE 文件
- 所有依赖许可证 **必须** 与主许可证兼容

### 文档合规要求

- 文档 **应该** 使用 CC BY 4.0 或 CC BY-SA 4.0 许可证
- 文档目录 **应该** 包含 LICENSE 文件或许可证声明

### 第三方依赖合规要求

- 每个第三方组件 **必须** 有 LICENSE 文件
- 许可证兼容性 **必须** 与主项目许可证验证
- 冲突 **必须** 在分发前解决

## 报告格式

```markdown
# Legal Compliance Report

## Project: [Project Name]

### 1. LICENSE File Status
| Status | License Type | File Path |
|--------|--------------|-----------|
| ✅/❌ | [Type] | [Path] |

### 2. License Conflict Analysis
| Component | License | Main License | Status | Severity |
|-----------|---------|--------------|--------|----------|
| [Name] | [Type] | [Main] | ✅ Compatible / 🔴 Conflict | Critical/Warning/Info |

### 3. Documentation License
| Directory | License Status | Expected |
|-----------|----------------|----------|
| docs/ | ✅ CC BY 4.0 / ✅ CC BY-SA 4.0 / ❌ Missing | CC BY 4.0 / CC BY-SA 4.0 |

### 4. Third-party Dependencies
| Component | LICENSE Status | License Type |
|-----------|----------------|--------------|
| [Name] | ✅/❌ | [Type] |

### 5. Compliance Summary
- Total items checked: [N]
- Compliant: [N]
- Non-compliant: [N]
- Missing LICENSE: [N]
- License conflicts: [N]

### 6. Recommendations
- [ ] Resolve license conflict in [Component]
- [ ] Add missing LICENSE file for [Component]
- [ ] Add CC BY 4.0 / CC BY-SA 4.0 for documentation
```

## 安全边界

- 检查过程只读取文件内容，不修改任何文件。
- 不自动添加或修改 LICENSE 文件，仅提供建议。
- 不提供法律意见，复杂冲突需咨询法务。
- 遵循 SPDX 许可证兼容性指南。
- 当不确定时，标记为冲突并建议人工审查。

## 注意事项

- 本 skill 专注于法务合规，**不** 检查安全问题。
- 如需安全检查，请使用 `code-security-audit` skill。
- 许可证兼容性分析遵循 SPDX 许可证兼容性指南。
- 复杂冲突可能需要法务人员审查。
- 私有许可证（如 Private Repository Source Code License）会被标记为非开源许可证。
