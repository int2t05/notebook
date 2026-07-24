---
name: "legal-compliance-checker"
description: "Checks legal compliance for open source projects: LICENSE file presence, license type validation, license conflict detection, and CC BY 4.0 or CC BY-SA 4.0 for documentation. Invoke when user requests legal compliance check, license audit, or open source compliance review."
---

# Legal Compliance Checker

This skill performs comprehensive legal compliance checks for open source software projects.

## Features

### 1. LICENSE File Check
- Scans project root directory for LICENSE files (various naming conventions)
- Supports common LICENSE file names:
  - `LICENSE`
  - `LICENSE.md`
  - `LICENSE.txt`
  - `COPYING`
  - `COPYING.LESSER`
  - `LICENSE-APACHE`
  - `LICENSE-MIT`

### 2. License Type Validation
- Identifies license type from LICENSE file content
- Supports common open source licenses:
  - Apache License 2.0
  - MIT License
  - GNU GPL v2/v3
  - GNU LGPL v2.1/v3
  - BSD 2-Clause/3-Clause
  - Mozilla Public License 2.0
  - Mulan PSL v2
  - CC BY 4.0 (for documentation)

### 3. License Conflict Detection
- Checks compatibility between main project license and dependency licenses
- Identifies potential license conflicts within a repository
- Reports incompatible license combinations
- Provides conflict resolution recommendations

### 4. Documentation License Check (CC BY 4.0 / CC BY-SA 4.0)
- Validates that documentation uses **CC BY 4.0** or **CC BY-SA 4.0** license
- Checks for documentation directories: `docs/`, `documentation/`, `doc/`
- Verifies documentation license files
- **文档许可证检查详细步骤**：
  1. 扫描文档目录下的 LICENSE 文件
  2. 读取 LICENSE 文件内容
  3. 匹配 CC BY 4.0 或 CC BY-SA 4.0 关键特征
  4. 验证许可证声明完整性

### 5. Third-party Dependencies Check
- Scans `thirdpart/`, `thirdparty/`, `vendor/`, `external/` directories
- Checks for LICENSE files in third-party components
- Reports missing licenses in dependencies

---

## License Compatibility Matrix

### Permissive Licenses (Compatible with most licenses)
| License | Compatible With | Notes |
|---------|-----------------|-------|
| MIT | Apache-2.0, BSD, GPL, LGPL, MulanPSLv2 | Most compatible |
| Apache-2.0 | MIT, BSD, GPL-v3+, LGPL-v3+, MulanPSLv2 | Patent grant included |
| BSD-2-Clause | MIT, Apache-2.0, BSD-3-Clause, GPL, LGPL | Simple permissive |
| BSD-3-Clause | MIT, Apache-2.0, BSD-2-Clause, GPL, LGPL | No endorsement clause |
| MulanPSLv2 | MIT, Apache-2.0, BSD, GPL, LGPL | Chinese open source license |

### Copyleft Licenses (Restrictive)
| License | Compatible With | Incompatible With |
|---------|-----------------|-------------------|
| GPL-v2 | GPL-v2, LGPL-v2.1 | Apache-2.0, GPL-v3, MulanPSLv2 |
| GPL-v3 | GPL-v3, LGPL-v3, Apache-2.0 | GPL-v2 |
| LGPL-v2.1 | GPL-v2, LGPL-v2.1 | Apache-2.0, GPL-v3 |
| LGPL-v3 | GPL-v3, LGPL-v3, Apache-2.0 | GPL-v2 |
| MPL-2.0 | MPL-2.0, Apache-2.0, MIT, BSD | GPL-v2 (file-level only) |

### Documentation Licenses
| License | Compatible With | Notes |
|---------|-----------------|-------|
| CC-BY-4.0 | All code licenses | For documentation only |
| CC-BY-SA-4.0 | Most licenses | Share-alike for docs |

---

## Usage Instructions

### Step 1: Identify Target Directory
Ask user for the project root directory to check. If not specified, use current working directory.

### Step 2: Check LICENSE File
```
Search for LICENSE files in root directory using Glob tool with pattern:
- LICENSE*
- COPYING*
```

### Step 3: Analyze License Content
If LICENSE file found:
1. Read the LICENSE file content
2. Identify license type by matching keywords:
   - "Apache License" → Apache 2.0
   - "MIT License" → MIT
   - "GNU General Public License" → GPL
   - "Mulan PSL" → Mulan PSL v2
   - "Creative Commons Attribution" → CC BY

### Step 4: Check License Conflicts
1. Identify main project license
2. Scan all dependency/submodule licenses
3. For each dependency, check compatibility with main license
4. Flag incompatible combinations
5. Provide conflict resolution suggestions

### Step 5: Check Documentation License (CC BY 4.0)
1. Search for documentation directories: `docs/`, `documentation/`, `doc/`
2. For each documentation directory:
   a. Check for LICENSE file using Glob: `docs/LICENSE*`
   b. If LICENSE found, read content and check for CC BY 4.0 keywords:
      - "Creative Commons Attribution"
      - "CC BY 4.0"
      - "creativecommons.org/licenses/by/4.0"
   c. If no LICENSE found, mark as non-compliant
3. Report documentation license compliance status
4. Provide recommendations for non-compliant documentation

### Step 6: Check Third-party Components
1. Scan third-party directories
2. Check each component for LICENSE file
3. Report components without LICENSE

### Step 7: Generate Compliance Report
Create a comprehensive report including:
- LICENSE file status (present/missing)
- License type identification
- **License conflict analysis**
- Documentation license compliance (CC BY 4.0)
- Third-party dependency compliance
- Recommendations for non-compliant items

---

## Conflict Detection Logic

### Conflict Detection Algorithm
```
1. Get main project license (L_main)
2. For each dependency license (L_dep):
   a. Check if L_main is compatible with L_dep
   b. If L_main is copyleft (GPL/LGPL):
      - Verify L_dep is compatible with copyleft requirements
   c. If L_dep is copyleft:
      - Verify L_main can satisfy copyleft requirements
   d. Flag any incompatibilities
3. Report all conflicts with severity levels
```

### Conflict Severity Levels
| Level | Description | Example |
|-------|-------------|---------|
| 🔴 **Critical** | Legal violation, must fix | GPL-v2 project with Apache-2.0 dependency |
| 🟠 **Warning** | Potential issue, review needed | GPL-v2 with GPL-v3 dependency |
| 🟡 **Info** | Note for awareness | Multiple permissive licenses |

### Common Conflict Scenarios

#### Scenario 1: GPL-v2 with Apache-2.0 Dependency
```
Main License: GPL-v2
Dependency License: Apache-2.0
Conflict: 🔴 Critical
Reason: Apache-2.0 has patent grant clause incompatible with GPL-v2
Solution: Upgrade to GPL-v3 or replace dependency
```

#### Scenario 2: Proprietary with GPL Dependency
```
Main License: Proprietary/None
Dependency License: GPL-v3
Conflict: 🔴 Critical
Reason: GPL requires entire project to be GPL
Solution: Add GPL license or remove dependency
```

#### Scenario 3: LGPL with Incompatible Dependency
```
Main License: LGPL-v2.1
Dependency License: Apache-2.0
Conflict: 🟠 Warning
Reason: Apache-2.0 patent grant may conflict with LGPL-v2.1
Solution: Consider upgrading to LGPL-v3
```

---

## Report Format

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

**Conflict Details:**
- [Component A]: [Reason for conflict]
- [Component B]: [Reason for conflict]

### 3. Documentation License
| Directory | License Status | Expected |
|-----------|----------------|----------|
| docs/ | ✅ CC BY 4.0 / ❌ Missing | CC BY 4.0 |

### 4. Third-party Dependencies
| Component | LICENSE Status | License Type |
|-----------|----------------|--------------|
| [Name] | ✅/❌ | [Type] |

### 5. Compliance Summary
- Total items checked: [N]
- Compliant: [N]
- Non-compliant: [N]
- Missing LICENSE: [N]
- **License conflicts: [N]**

### 6. Recommendations
[List of actions to achieve compliance]
- [ ] Resolve license conflict in [Component]
- [ ] Add missing LICENSE file for [Component]
```

---

## Common License Patterns

### Apache 2.0
```
Apache License
Version 2.0, January 2004
```

### MIT
```
MIT License
Permission is hereby granted, free of charge...
```

### Mulan PSL v2
```
Mulan PSL v2
http://license.coscl.org.cn/MulanPSL2
```

### GPL v2
```
GNU General Public License
Version 2
```

### GPL v3
```
GNU General Public License
Version 3
```

### CC BY 4.0
```
Creative Commons Attribution 4.0 International
CC BY 4.0
```

---

## CC BY 4.0 / CC BY-SA 4.0 详细检查指南

### 文档许可证识别特征

#### CC BY 4.0 关键词匹配模式
以下关键词出现表示可能是 CC BY 4.0 许可证：
```
1. "Creative Commons Attribution"
2. "CC BY 4.0"
3. "CC-BY-4.0"
4. "creativecommons.org/licenses/by/4.0"
5. "Attribution 4.0 International"
```

#### CC BY-SA 4.0 关键词匹配模式
以下关键词出现表示可能是 CC BY-SA 4.0 许可证：
```
1. "Creative Commons Attribution-ShareAlike"
2. "CC BY-SA 4.0"
3. "CC-BY-SA-4.0"
4. "creativecommons.org/licenses/by-sa/4.0"
5. "Attribution-ShareAlike 4.0 International"
```

#### 通用识别方法
检查 LICENSE 文件内容，按以下优先级识别：
1. 先检查是否为 CC BY-SA 4.0（包含 "ShareAlike" 或 "by-sa"）
2. 再检查是否为 CC BY 4.0（包含 "Attribution" 但不含 "ShareAlike"）
3. 两者都匹配则报告具体类型

#### CC BY 4.0 完整许可证头
```
Creative Commons Attribution 4.0 International Public License

By exercising the Licensed Rights (defined below), You accept and agree
to be bound by the terms and conditions of this Creative Commons
Attribution 4.0 International Public License ("Public License").
```

#### CC BY 4.0 简化声明格式
```markdown
This documentation is licensed under a Creative Commons Attribution 4.0 International License.

You may share and adapt the material under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, 
  and indicate if changes were made.

Full license text: https://creativecommons.org/licenses/by/4.0/
```

### 文档许可证检查步骤

#### Step 1: 定位文档目录
```
使用 Glob 工具搜索文档目录：
- docs/LICENSE*
- docs/LICENSE.md
- documentation/LICENSE*
- doc/LICENSE*
```

#### Step 2: 读取并分析 LICENSE 文件
```
1. 使用 Read 工具读取 LICENSE 文件内容
2. 搜索 CC BY-SA 4.0 关键词：
   - "ShareAlike"
   - "by-sa"
   - "creativecommons.org/licenses/by-sa"
3. 搜索 CC BY 4.0 关键词：
   - "Creative Commons"
   - "Attribution"
   - "4.0"
   - "creativecommons.org/licenses/by"
```

#### Step 3: 验证文档许可证合规性
```
检查项：
□ LICENSE 文件存在
□ 包含 "Creative Commons" 关键词
□ 包含 "4.0" 版本标识
□ 包含许可证链接 (creativecommons.org/licenses/by/4.0 或 by-sa/4.0)
□ 识别具体类型：
  - 包含 "ShareAlike" → CC BY-SA 4.0
  - 不含 "ShareAlike" → CC BY 4.0
□ 文档文件头部包含许可证声明（可选但推荐）
```

#### Step 4: 生成检查报告
```
报告格式：
| 文档目录 | LICENSE 文件 | 许可证类型 | 合规状态 |
|---------|-------------|-----------|---------|
| docs/ | ✅ 存在 | CC BY 4.0 | ✅ 合规 |
| docs/ | ✅ 存在 | CC BY-SA 4.0 | ✅ 合规 |
| documentation/ | ❌ 不存在 | - | ❌ 不合规 |
```

### 文档许可证检查示例

#### 示例 1: 检查 CC BY 4.0 文档
```
项目结构：
project/
├── docs/
│   ├── LICENSE
│   └── guide.md
└── src/

检查步骤：
1. Glob: docs/LICENSE* → 找到 docs/LICENSE
2. Read: docs/LICENSE → 读取内容
3. Grep: "Creative Commons" → 匹配成功
4. Grep: "Attribution 4.0" → 匹配成功
5. Grep: "ShareAlike" → 未匹配
6. 结论: ✅ CC BY 4.0 合规
```

#### 示例 2: 检查 CC BY-SA 4.0 文档
```
项目结构：
project/
├── docs/
│   ├── LICENSE
│   └── guide.md
└── src/

检查步骤：
1. Glob: docs/LICENSE* → 找到 docs/LICENSE
2. Read: docs/LICENSE → 读取内容
3. Grep: "Creative Commons" → 匹配成功
4. Grep: "ShareAlike" → 匹配成功
5. Grep: "by-sa" → 匹配成功
6. 结论: ✅ CC BY-SA 4.0 合规
```

#### 示例 3: 文档缺少 LICENSE
```
项目结构：
project/
├── docs/
│   └── guide.md  (无 LICENSE)
└── src/

检查步骤：
1. Glob: docs/LICENSE* → 未找到
2. 结论: ❌ 缺少文档 LICENSE，建议添加 CC BY 4.0 或 CC BY-SA 4.0
```

### CC BY 4.0 模板文件

如需创建 CC BY 4.0 LICENSE 文件，可使用以下模板：

```markdown
Creative Commons Attribution 4.0 International Public License

By exercising the Licensed Rights (defined below), You accept and agree
to be bound by the terms and conditions of this Creative Commons
Attribution 4.0 International Public License ("Public License"). To the
extent this Public License may be interpreted as a contract, You are
granted the Licensed Rights in consideration of Your acceptance of these
terms and conditions, and the Licensor grants You such rights in
consideration of benefits the Licensor receives from making the Licensed
Material available under these terms and conditions.

Section 1 – Definitions.

a. Adapted Material means material subject to Copyright and Similar
Rights that is derived from or based upon the Licensed Material and in
which the Licensed Material is translated, altered, arranged, transformed,
or otherwise modified in a manner requiring permission under the Copyright
and Similar Rights held by the Licensor.

b. Adapter's License means the license You apply to Your Copyright and
Similar Rights in Your contributions to Adapted Material in accordance
with the terms and conditions of this Public License.

c. Copyright and Similar Rights means copyright and/or similar rights
related to copyright including, without limitation, performance, broadcast,
sound recording, and Sui Generis Database Rights, without regard as to
how the rights are labeled or categorized.

...

[完整许可证文本请参考: https://creativecommons.org/licenses/by/4.0/legalcode]
```

### CC BY-SA 4.0 模板文件

如需创建 CC BY-SA 4.0 LICENSE 文件，可使用以下模板：

```markdown
Creative Commons Attribution-ShareAlike 4.0 International Public License

By exercising the Licensed Rights (defined below), You accept and agree
to be bound by the terms and conditions of this Creative Commons
Attribution-ShareAlike 4.0 International Public License ("Public License").
To the extent this Public License may be interpreted as a contract, You are
granted the Licensed Rights in consideration of Your acceptance of these
terms and conditions, and the Licensor grants You such rights in
consideration of benefits the Licensor receives from making the Licensed
Material available under these terms and conditions.

Section 1 – Definitions.

a. Adapted Material means material subject to Copyright and Similar
Rights that is derived from or based upon the Licensed Material and in
which the Licensed Material is translated, altered, arranged, transformed,
or otherwise modified in a manner requiring permission under the Copyright
and Similar Rights held by the Licensor. For purposes of this Public License,
where the Licensed Material is a musical work, performance, or sound recording,
Adapted Material is always produced where the Licensed Material is synched
in timed relation with a moving image.

b. Adapter's License means the license You apply to Your Copyright and
Similar Rights in Your contributions to Adapted Material in accordance
with the terms and conditions of this Public License.

...

[完整许可证文本请参考: https://creativecommons.org/licenses/by-sa/4.0/legalcode]
```

### CC BY 4.0 简化声明模板

在文档文件头部添加：
```
<!--
This documentation is licensed under CC BY 4.0.
https://creativecommons.org/licenses/by/4.0/
-->
```

或在 Markdown 文件中添加：
```markdown
> **License**: This document is licensed under [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
```

### CC BY-SA 4.0 简化声明模板

在文档文件头部添加：
```
<!--
This documentation is licensed under CC BY-SA 4.0.
https://creativecommons.org/licenses/by-sa/4.0/
-->
```

或在 Markdown 文件中添加：
```markdown
> **License**: This document is licensed under [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).
```

---

## Example Usage

### Example 1: Check Single Project with Conflict Detection
```
User: Check legal compliance for project at /path/to/project

Actions:
1. Check LICENSE in /path/to/project
2. Identify main project license
3. Scan all dependencies for their licenses
4. Check license compatibility/conflicts
5. Check docs/ for CC BY 4.0
6. Check thirdpart/ for component licenses
7. Generate report with conflict analysis
```

### Example 2: Check Multiple Projects
```
User: Check legal compliance for all projects in /projects/

Actions:
1. List all project directories
2. For each project, perform compliance check
3. Generate consolidated report with all conflicts
```

---

## Compliance Requirements

### For Code
- Root directory MUST contain LICENSE file
- License type MUST be an approved open source license
- Third-party components MUST have their own LICENSE files
- **All dependency licenses MUST be compatible with main license**

### For Documentation
- Documentation SHOULD use CC BY 4.0 or CC BY-SA 4.0 license
- Documentation directory SHOULD contain LICENSE file or license notice

### For Third-party Dependencies
- Each third-party component MUST have LICENSE file
- License compatibility MUST be verified with main project license
- **Conflicts MUST be resolved before distribution**

---

## Notes

- This skill focuses on legal compliance, NOT security
- Use `code-security-audit` skill for security-related checks
- License compatibility analysis follows SPDX license compatibility guidelines
- Complex conflicts may require legal counsel review
- When in doubt, treat as conflict and flag for manual review