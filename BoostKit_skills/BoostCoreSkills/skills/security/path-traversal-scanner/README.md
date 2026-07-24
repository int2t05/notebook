# Path Traversal Scanner

路径穿越漏洞扫描器 — 检测 **Path Traversal (CWE-22)** 漏洞并生成审计报告。

## 功能

- 基于信任边界的路径穿越漏洞检测（6 步法）
- 支持多语言（C/C++、Python、Java、JavaScript、Go）

## 核心判断标准

判断文件操作点是否为漏洞，回答两个问题：

1. **谁控制路径？** — 攻击者、管理员、开发者、内部代码？
2. **是否跨越信任边界？** — 数据是否从不可信域流入可信域？

| 路径控制者 | 是否跨越信任边界 | 判定 | 示例 |
|-----------|-----------------|------|------|
| 攻击者 | ✅ 是 | ⚠️ 真问题 | HTTP 参数、JNI 传入数据 |
| 攻击者（受限） | ✅ 是 | ⚠️ 真问题 | 环境变量（SUID 场景） |
| 管理员 | ❌ 否 | ✅ 非问题 | 配置文件字段 |
| 开发者 | ❌ 否 | ✅ 非问题 | API 函数参数、硬编码 |
| 内部代码 | ❌ 否 | ✅ 非问题 | 整数格式化的 /proc 路径 |

## 检测流程（6 步法）

```
Step 1: 识别文件操作 (Sink)    — 扫描 fopen/dlopen/open 等危险函数
    ↓
Step 2: 追踪数据源 (Source)    — 识别外部不可控数据
    ↓
Step 3: 数据流分析             — 追踪从源到汇的完整路径
    ↓
Step 4: 证据收集               — 收集代码证据证明或否定漏洞
    ↓
Step 5: 漏洞分类               — 基于信任边界判定真问题/非问题
    ↓
Step 6: 验证检查               — 检查已有防护措施的有效性
```

## 使用方式

在 Trae IDE 中直接对话触发：

```
"帮我检查 KAE 代码的路径穿越漏洞"
"扫描 Code/myproject 的路径穿越问题"
"检查 src/api/ 的路径穿越漏洞"
```

## 目录结构

```
path-traversal-scanner/
├── SKILL.md                                    # Skill 主文件（方法论、检测流程、分类标准）
├── README.md                                   # 本文件
└── references/
    ├── Report_Template.md                      # 报告模板（真问题/非问题分类模板）
    ├── Trust_Boundary_Guide.md                 # 信任边界指南
    ├── External_Data_Sources.md                # 外部数据源识别指南
    ├── Investigation_Checklist.md              # 手动调查清单
    ├── Secure_Coding_Index.md                  # 安全编码示例索引
    ├── Secure_Coding_Python.md                 # Python 安全编码
    ├── Secure_Coding_Java.md                   # Java 安全编码
    ├── Secure_Coding_C.md                      # C 安全编码
    ├── Secure_Coding_JavaScript.md             # JavaScript 安全编码
    ├── Secure_Coding_Go.md                     # Go 安全编码
    ├── Implementation_Plan.md                  # 实施计划
    └── Path_Security_Check_Symbols_Guide.md    # 路径安全检查符号指南
```

## 报告输出

扫描完成后生成两个文件到 `Report/<日期>/` 目录：

| 文件 | 说明 |
|------|------|
| `<项目>_PathTraversal_Audit_<日期>.md` | 审计报告（真问题 + 非问题 + 判断逻辑 + 修复建议） |
| `<项目>_PathTraversal_Audit_<日期>.log` | 扫描日志（6 步法详细记录） |

### 报告结构

```
结论：N 个真问题 + M 个非问题

├── 一、真问题（⚠️）
│   ├── 为什么是真问题（跨越信任边界 + 无验证 + 攻击者可控）
│   ├── 数据流图
│   ├── 影响和缓解因素
│   └── 修复建议（安全代码示例）
│
├── 二、非问题（✅）
│   └── 为什么不是问题（谁控制路径 + 攻击前提不成立）
│
├── 三、完整扫描记录（所有 Sink 汇总表）
│
└── 四、核心判断逻辑（路径控制者 × 信任边界 → 判定）
```

## 参考标准

- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory
- **CWE-73**: External Control of File Name or Path
- **OWASP Path Traversal**: https://owasp.org/www-community/attacks/Path_Traversal
