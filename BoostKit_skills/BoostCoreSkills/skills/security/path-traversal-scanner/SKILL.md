---
name: "path-traversal-scanner"
description: "Detects path traversal vulnerabilities and generates PoC for verification. Invoke when user requests path traversal check, directory traversal scan, file path security review, or repository-wide vulnerability scan."
---

# Path Traversal Scanner

路径穿越漏洞扫描器 - 检测 **Path Traversal (CWE-22)** 漏洞并生成PoC验证。

## 目录

- [概述](#概述)
- [使用时机](#使用时机)
- [核心方法论](#核心方法论)
- [漏洞分类标准](#漏洞分类标准)
- [报告模板](#报告模板)
- [手动调查清单](#手动调查清单)
- [参考资料](#参考资料)

---

## 概述

路径穿越攻击允许攻击者通过操纵文件路径访问预期目录之外的文件和目录。

**核心原理：**
```
外部数据 → 路径构造 → 文件操作
   ↓           ↓          ↓
 污点数据   未验证    安全漏洞
```

**关键概念：信任边界 (Trust Boundary)**

任何跨越信任边界的数据（用户输入、网络报文、其他进程数据等）都必须视为不可信数据，需要验证和净化。

**详细说明**：参见 [Trust_Boundary_Guide.md](./references/Trust_Boundary_Guide.md)

---

## 使用时机

当以下情况时调用此skill：

- 用户请求路径穿越漏洞扫描
- 用户询问目录遍历检查
- 用户需要文件路径安全审查
- 用户提到 CWE-22 或路径注入
- 安全审计需要路径处理验证

---

## 核心方法论

### ⚠️ 强制要求

**必须为每个潜在漏洞执行完整的数据流分析，不得在无证据情况下报告漏洞。**

### 检测流程（6步法）

```
Step 1: 识别文件操作 (Sink) [强制]
    ↓
Step 2: 追踪数据源 (Source) [强制]
    ↓
Step 3: 数据流分析 [强制]
    ↓
Step 4: 证据收集 [强制]
    ↓
Step 5: 漏洞分类 [强制]
    ↓
Step 6: 验证检查 [强制]
```

**⚠️ 所有步骤均为强制项，必须完整执行，不得跳过任何步骤。**

---

### Step 1: 识别文件操作 (Sink) [强制]

**⚠️ 关键：必须识别所有文件操作点，不得遗漏任何潜在Sink**

**危险函数清单：**

| 语言 | 危险函数 |
|------|----------|
| Python | `open()`, `os.path.join()`, `os.open()`, `shutil.copy()`, `tarfile.extract()` |
| Java | `new File()`, `FileInputStream`, `FileReader`, `Paths.get()` |
| JavaScript | `fs.readFile()`, `fs.open()`, `fs.createReadStream()`, `path.join()` |
| C/C++ | `fopen()`, `open()`, `dlopen()`, `shm_open()`, `stat()`, `access()` |
| PHP | `include()`, `require()`, `fopen()`, `file_get_contents()`, `readfile()` |
| Go | `os.Open()`, `ioutil.ReadFile()`, `filepath.Join()` |

**扫描命令：**
```bash
# Python
grep -rn "open\s*(\|os\.path\.join\|shutil\.copy" --include="*.py"

# Java
grep -rn "new File\s*(\|FileInputStream\|FileReader" --include="*.java"

# C/C++
grep -rn "fopen\s*(\|open\s*(\|dlopen\s*(\|shm_open" --include="*.c" --include="*.cpp"

# JavaScript
grep -rn "fs\.readFile\|fs\.open\|path\.join" --include="*.js"

# PHP
grep -rn "include\s*(\|require\s*(\|fopen\s*(" --include="*.php"
```

---

### Step 2: 追踪数据源 (Source) [强制]

**⚠️ 关键：必须追踪每个文件操作的数据源，识别所有外部不可控数据**

**数据源风险分类：**

| 分类 | 风险级别 | 数据源示例 |
|------|----------|------------|
| **EXTERNAL** (外部不可控) | 高风险 ⚠️ | HTTP参数、CLI参数、Socket数据、RPC响应、消息队列、IPC通信、环境变量、数据库查询（受用户影响） |
| **INTERNAL** (内部可控) | 低风险 ✓ | 硬编码字符串、随机生成值、编译时常量、内部函数返回值 |
| **CONFIGURATION** (配置/管理) | 中风险 ⚡ | 管理员配置、系统环境变量、部署参数 |

**信任边界规则**：任何跨越信任边界的数据都必须视为 EXTERNAL (高风险)

**详细分类和示例**：参见 [External_Data_Sources.md](./references/External_Data_Sources.md)

---

### Step 3: 数据流分析 [强制]

**⚠️ 关键：必须执行完整的数据流分析**

**分析步骤：**
```
1. 识别 Sink (文件操作)
2. 向后追踪所有数据源
3. 识别信任边界（数据是否跨信任域）
4. 对每个源确定：
   - 是否外部可控（跨信任边界）？
   - 是否内部生成？
   - 是否来自配置？
5. 追踪所有转换和净化
6. 确定污点数据是否到达 Sink
```

**数据流图示例：**
```
[Source] socket.recv(1024)  [EXTERNAL - 网络数据]
    │
    ▼
[Var] filename = data.decode()  [TAINTED]
    │
    ▼
[Op] path = "/data/" + filename  [TAINTED]
    │
    ▼
[Sink] open(path, 'r')  [VULNERABLE!]
```

---

### Step 4: 证据收集 [强制]

**⚠️ 关键：必须收集证据证明或否定漏洞**

**证据清单：**

```
1. 数据源证据：
   □ 数据来自哪里？
   □ 源是外部还是内部？
   □ **信任边界在哪里？**
   □ 攻击者能否控制该值？
   □ 展示证明数据源的代码片段

2. 数据流证据：
   □ 展示从源到汇的完整路径
   □ 记录所有中间转换
   □ 识别任何净化/验证
   □ 证明污点数据到达汇

3. 可利用性证据：
   □ 攻击者能否控制完整路径？
   □ 是否有限制？
   □ 攻击者可注入什么值？
   □ 如可利用，展示攻击向量
```

---

### Step 5: 漏洞分类 [强制]

**⚠️ 关键：必须基于信任边界严格分类，明确区分真问题和非问题**

**核心判断标准**：回答两个问题 → 1. 谁控制路径？ 2. 是否跨越信任边界？

#### ⚠️ 真问题 — 跨越信任边界 + 无验证

```
✓ 数据源是外部（跨信任边界）：攻击者可控制路径
✓ 污点数据到达文件操作
✓ 无有效净化/验证
→ 报告为 ⚠️ 真问题，提供修复建议
```

**常见真问题场景**：
- HTTP 参数/网络报文 → 文件操作（CWE-22）
- JNI/IPC/RPC 跨语言/跨进程数据 → 文件操作（CWE-22/CWE-73）
- SUID 进程中 getenv() → 文件操作（CWE-73，应使用 secure_getenv）

#### ✅ 非问题 — 未跨越信任边界

```
✗ 路径由管理员控制（配置文件需 root 修改）
✗ 路径由开发者控制（API 函数参数、硬编码字符串）
✗ 路径由内部代码控制（整数格式化的 /proc 路径）
✗ 存在有效净化（realpath 规范化 + 白名单验证）
→ 报告为 ✅ 非问题，说明为什么不是漏洞
```

**常见非问题场景**：
- 配置文件字段（需 root 修改）→ 管理员是可信的
- API 函数参数（调用者传路径）→ 调用者和被调函数在同一信任域
- 命令行工具用户参数 → 用户控制自己的程序
- 环境变量（非 SUID 进程）→ 部署系统/管理员控制
- dlopen API 参数 → 调用者决定加载什么库
- 硬编码字符串 → 无外部输入参与

**⚠️ 重要**：非问题也必须在报告中列出，说明为什么不是漏洞，让读者知道哪些地方已检查过。

---

### Step 6: 验证检查 [强制]

**⚠️ 关键：必须检查所有验证措施，确保漏洞报告的准确性**

检查是否存在以下验证：

- [ ] **信任边界识别**（明确区分内外部数据）
- [ ] 路径规范化 (`realpath()`, `resolve()`, `normalize()`)
- [ ] 路径边界检查 (`startsWith()`, `contains()`)
- [ ] 白名单验证
- [ ] 输入净化

---

## 漏洞分类标准

### 核心判断标准

判断文件操作点是否为漏洞，回答两个问题：

1. **谁控制路径？** — 攻击者、管理员、开发者、内部代码？
2. **是否跨越信任边界？** — 数据是否从不可信域流入可信域？

### 判断矩阵

| 路径控制者 | 是否跨越信任边界 | 判定 | 示例 |
|-----------|-----------------|------|------|
| 攻击者 | ✅ 是 | ⚠️ 真问题 | HTTP 参数、网络报文、JNI 传入数据 |
| 攻击者（受限） | ✅ 是 | ⚠️ 真问题（需评估影响） | 环境变量（SUID 场景） |
| 管理员 | ❌ 否 | ✅ 非问题 | 配置文件字段、部署环境变量 |
| 开发者 | ❌ 否 | ✅ 非问题 | 硬编码路径、API 函数参数 |
| 内部代码 | ❌ 否 | ✅ 非问题 | 整数格式化的 /proc 路径 |

### 分类决策树

```
发现文件操作
    │
    ├─ 谁控制路径？
    │   ├─ 攻击者可控制 → 是否跨越信任边界？
    │   │   ├─ 是 → ⚠️ 真问题
    │   │   └─ 否（不可能）→ 检查是否有误解
    │   │
    │   ├─ 管理员控制 → ✅ 非问题
    │   │   └─ 管理员是可信的，攻击前提不成立
    │   │
    │   ├─ 开发者控制 → ✅ 非问题
    │   │   └─ API 参数、硬编码路径，同一信任域
    │   │
    │   └─ 内部代码控制 → ✅ 非问题
    │       └─ 整数格式化、随机生成值，无法注入
    │
    └─ 特殊场景
        ├─ SUID 进程 + getenv() → ⚠️ 真问题（应用 secure_getenv）
        ├─ 跨 JNI/IPC/RPC 边界 → ⚠️ 真问题（需验证接收端）
        └─ 有 realpath + 白名单 → ✅ 非问题（防护有效）
```

### 常见非问题场景（不要误报）

| 场景 | 为什么不是漏洞 |
|------|---------------|
| 命令行工具，用户指定路径 | 用户控制自己的程序，不是攻击 |
| 库函数 API，调用者传路径 | 调用者和被调函数在同一信任域 |
| 配置文件字段（需 root 修改） | root 是可信的，root 想做任何事直接做就行 |
| 环境变量（非 SUID 进程） | 部署系统/管理员控制，不是攻击者 |
| dlopen API 参数 | 调用者决定加载什么库，正常行为 |
| 硬编码字符串 | 无外部输入参与 |

---

## 报告模板

详细的报告模板请参考 [Report_Template.md](./references/Report_Template.md)，包括：

- **完整报告模板** - 真问题/非问题明确区分的报告格式
- **真问题详情模板** - 外部输入、SUID getenv、跨 JNI/IPC 边界等场景模板
- **非问题详情模板** - 配置文件、API 参数、环境变量、硬编码路径等场景模板
- **日志文件模板** - 6 步法扫描日志格式
- **核心判断标准** - "谁控制路径" + "是否跨越信任边界" 判断矩阵

**快速参考**：

### 核心判断标准

判断文件操作点是否为漏洞，回答两个问题：
1. **谁控制路径？** — 攻击者、管理员、开发者、内部代码？
2. **是否跨越信任边界？** — 数据是否从不可信域流入可信域？

| 路径控制者 | 是否跨越信任边界 | 判定 |
|-----------|-----------------|------|
| 攻击者 | ✅ 是 | ⚠️ 真问题 |
| 管理员 | ❌ 否 | ✅ 非问题 |
| 开发者 | ❌ 否 | ✅ 非问题 |
| 内部代码 | ❌ 否 | ✅ 非问题 |

### 报告基本结构

```markdown
## 结论：发现 N 个真问题 + M 个非问题

### ⚠️ 问题 #1：[标题]
**为什么是真问题**：1. 跨越信任边界 2. 无验证 3. 攻击者可控
**修复建议**：[安全代码]

### ✅ 非问题 #1：[标题]
**为什么不是问题**：1. 路径由管理员控制 2. 攻击前提不成立
> 关键判断：谁控制路径的值？是管理员，不是攻击者。

### 核心判断逻辑
| 场景 | 路径控制者 | 是否跨越信任边界 | 是否漏洞 |
```

---

## 手动调查清单

当静态分析无法确定漏洞时，执行以下调查：

```
【数据源识别】
□ 已识别直接数据源
□ 已识别间接数据源
□ 已追踪完整调用链

【信任边界确定】
□ 已确定数据是否来自网络
□ 已确定数据是否来自其他进程
□ 已确定数据是否来自用户输入
□ 已确定数据是否在内部信任域内

【数据流追踪】
□ 已追踪数据从源到汇的完整路径
□ 已记录所有中间函数
□ 已识别所有净化/验证点

【净化验证】
□ 已检查路径规范化
□ 已检查边界检查
□ 已检查白名单验证

【可利用性评估】
□ 已确定攻击者能否控制数据
□ 已确定攻击者能否构造载荷
□ 已构造PoC（如果可利用）
```

**详细调查流程和报告模板**：参见 [Investigation_Checklist.md](./references/Investigation_Checklist.md)

---

## 参考资料

### 在线参考

- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory
  - https://cwe.mitre.org/data/definitions/22.html

- **OWASP Path Traversal**: 
  - https://owasp.org/www-community/attacks/Path_Traversal

- **OWASP Testing Guide**: Testing for Path Traversal
  - https://owasp.org/www-project-web-security-testing-guide/

- **SEI CERT Coding Standards**:
  - https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+Coding+Standards

- **Trust Boundary (信任边界)**:
  - https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/
  - 关键概念：任何跨越信任边界的数据都必须验证

### 本地参考文档

所有详细参考文档位于 `./references/` 目录：

- **[Trust_Boundary_Guide.md](./references/Trust_Boundary_Guide.md)** - 信任边界指南
  - 信任边界核心概念和可视化
  - 4类信任边界详细说明（网络、用户、进程、配置）
  - 信任边界决策树和识别清单
  - 常见错误和安全示例

- **[External_Data_Sources.md](./references/External_Data_Sources.md)** - 外部数据源识别指南
  - 数据源分类（EXTERNAL/INTERNAL/CONFIGURATION）
  - 每类数据源的代码示例（多语言）
  - 数据源识别流程和决策树
  - 常见错误和检查清单

- **[Secure_Coding_Index.md](./references/Secure_Coding_Index.md)** - 安全编码示例索引
  - 通用验证函数（路径穿越检测、路径规范化验证）
  - TOCTOU竞态条件警告和缓解措施
  - 生产环境建议和参考资料
  - 按语言拆分的详细示例：
    - [Secure_Coding_Python.md](./references/Secure_Coding_Python.md) - Python安全编码
    - [Secure_Coding_Java.md](./references/Secure_Coding_Java.md) - Java安全编码
    - [Secure_Coding_C.md](./references/Secure_Coding_C.md) - C安全编码
    - [Secure_Coding_JavaScript.md](./references/Secure_Coding_JavaScript.md) - JavaScript安全编码
    - [Secure_Coding_Go.md](./references/Secure_Coding_Go.md) - Go安全编码

- **[Implementation_Plan.md](./references/Implementation_Plan.md)** - 实施计划
  - 4个实施阶段（P0-P3）详细计划
  - 时间表、资源需求、成功标准
  - 验证步骤和关键指标
  - 风险评估和缓解措施

- **[Investigation_Checklist.md](./references/Investigation_Checklist.md)** - 手动调查清单
  - 5步调查流程（数据源→信任边界→数据流→净化→可利用性）
  - 完整调查清单和报告模板
  - 常见调查场景（配置文件、跨进程、数据库）
  - 调查命令和判断标准

- **[Report_Template.md](./references/Report_Template.md)** - 报告模板
  - 漏洞报告结构和详情模板
  - 信任边界总结模板
  - 手动调查报告模板
  - 执行摘要和建议措施模板

- **[Path_Security_Check_Symbols_Guide.md](./references/Path_Security_Check_Symbols_Guide.md)** - 路径安全检查符号指南
  - 完整的危险符号和攻击载荷列表
  - 增强检测代码（100%覆盖）
  - 145个测试用例
  - 多层解码检测策略

---

## 使用示例

### 单文件扫描
```
用户: "检查此代码的路径穿越漏洞"
代理: [调用 path-traversal-scanner skill]
      - 扫描代码库查找文件操作
      - 追踪数据源到文件路径
      - 识别信任边界
      - 检查验证
      - 生成带可点击链接的漏洞报告
```

### 仓库级扫描
```
用户: "扫描整个仓库的路径穿越漏洞"
用户: "检查 Code/myproject 的路径穿越问题"

代理: [调用 path-traversal-scanner skill]
      步骤1: 枚举所有源文件
      步骤2: 扫描危险文件操作
      步骤3: 追踪数据源（识别信任边界）
      步骤4: 数据流分析
      步骤5: 漏洞分类
      步骤6: 生成综合报告
```

### 扫描特定目录
```
用户: "检查 src/api/ 的路径穿越漏洞"
代理: [调用 path-traversal-scanner skill]
      - 仅扫描 src/api/ 目录
      - 应用相同检测方法论
      - 识别信任边界
      - 生成针对性报告
```
