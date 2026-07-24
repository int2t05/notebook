# Secure Compile Checker

安全编译选项检查器 — 基于 **BoostKit SecureCompile** 规范，检测 C/C++ 项目的安全编译选项合规性。

## 功能

- 6 步方法论检查安全编译选项合规性
- 支持 CMake、Autotools、Makefile、Meson、Bazel 等构建系统
- 逐目标检查，区分动态库和可执行文件
- 条件编译分支覆盖分析
- 生成合规矩阵、风险分级、修复建议

## 核心原则

1. **逐目标检查** — 每个构建目标单独检查，目标 A 配置不代表目标 B 也配置
2. **条件分支覆盖** — 安全选项必须在所有分支生效
3. **区分动态库/可执行文件** — 动态库检查 `-fPIC`，可执行文件检查 `-fPIE -pie`
4. **只检查生产目标** — 排除 test/fuzz/perf/benchmark 目标
5. **证据溯源** — 每个判断标注源文件和行号

## 检查流程（6 步法）

```
Step 1: 项目语言检测          — 确定是否为 C/C++ 项目
    ↓
Step 2: 构建系统识别          — 找出所有生产构建目标
    ↓
Step 3: 编译选项提取          — 逐目标提取安全编译选项
    ↓
Step 4: 必须项检查            — 检查 9 项必须配置选项
    ↓
Step 5: 建议项检查            — 检查 5 项建议配置选项
    ↓
Step 6: 生成报告和日志
```

## 检查标准

### 必须项（9 项）

| # | 选项 | 适用目标 | 作用 |
|---|------|---------|------|
| 1 | `-fPIC` | 动态库 | ASLR 位置无关代码 |
| 2 | `-fPIE` + `-pie` | 可执行文件 | ASLR 位置无关可执行文件 |
| 3 | `-fstack-protector-strong` | 全部 | 栈溢出保护 |
| 4 | `-Wl,-z,relro` | 全部 | GOT 表部分只读 |
| 5 | `-Wl,-z,relro,-z,now` | 全部 | GOT 表完全只读 (Full RELRO) |
| 6 | `-Wl,-z,noexecstack` | 全部 | 栈不可执行 |
| 7 | `-s` / `strip` | 全部 | 符号剥离 |
| 8 | 禁止 RPATH | 全部 | 防止动态库劫持 |
| 9 | `-D_FORTIFY_SOURCE=2` + `-O2` | 全部 | 缓冲区溢出检测 |

> **注意**: `-fPIC` 仅适用于动态库，`-fPIE -pie` 仅适用于可执行文件，两者不混用。  
> `-Wl,-z,noexecstack` 对动态库和可执行文件**都适用**，不应标记为不适用。

### 建议项（5 项）

| # | 选项 | 作用 |
|---|------|------|
| 1 | `-fvisibility=hidden` | 隐藏非导出符号，减少攻击面 |
| 2 | `-ftrapv` | 有符号整数溢出检测 |
| 3 | `-fstack-check` | 栈溢出检测 |
| 4 | `-fstack-clash-protection` | 栈冲突保护 |
| 5 | `-D_FORTIFY_SOURCE=2` + `-O2` | 缓冲区溢出检测（同必须项 9） |

### 目标类型与适用选项

| 选项 | 动态库 (.so) | 可执行文件 |
|------|-------------|-----------|
| `-fPIC` | ✅ 适用 | ❌ 不适用 |
| `-fPIE -pie` | ❌ 不适用 | ✅ 适用 |
| `-Wl,-z,noexecstack` | ✅ 适用 | ✅ 适用 |
| 其他必须项 | ✅ 适用 | ✅ 适用 |

## 使用方式

在 Trae IDE 中直接对话触发：

```
"检查下 knet 的安全编译选项"
"检查下 BoostKit_Code_SelfDev.md 的安全编译选项"
"检查下 HPCKit_Code.md 的安全编译选项"
```

支持单个仓库检查和批量检查（通过 .md 文件中的仓库列表）。

## 目录结构

```
secure-compile-checker/
├── SKILL.md      # Skill 主文件（6 步方法论、检查标准、报告模板、日志模板）
└── README.md     # 本文件
```

## 报告输出

扫描完成后生成两个文件到 `Report/<日期>/` 目录：

| 文件 | 说明 |
|------|------|
| `<项目>_SecureCompile_Report_<日期>.md` | 检查报告（合规矩阵、风险分级、修复建议） |
| `<项目>_SecureCompile_Log_<日期>.log` | 扫描日志（6 步法详细记录） |

### 报告结构

```
├── 1. 检查标准（必须项 + 建议项）
├── 2. 项目分类（C/C++ vs 非 C/C++）
├── 3. 合规矩阵（✅/❌/⚠️/➖ 逐项逐目标）
├── 4. 风险分级（🔴 高 / 🟡 中 / 🟢 低）
├── 5. 共性问题分析
├── 6. 修复建议（通用模板 + 特定修复）
├── 7. 统计摘要
└── 8. 逐仓库详细分析
```

### 合规率计算

```
合规率 = 已配置项数 / 适用项总数（排除不适用项）
```

### 风险分级

| 等级 | 合规率 | 说明 |
|------|--------|------|
| 🔴 高风险 | ≤ 20% | 安全编译选项严重缺失 |
| 🟡 中风险 | 21%-60% | 存在部分缺失 |
| 🟢 低风险 | ≥ 60% | 配置较完善 |

## 参考标准

- **BoostKit SecureCompile**: [SecureCompile(C&C++).md](https://gitcode.com/boostkit/community/blob/master/docs/security-Committee/SecureCompile(C&C++).md)
- **CWE-119**: Improper Restriction of Operations within the Bounds of a Memory Buffer
- **CWE-120**: Buffer Copy without Checking Size of Input
- **CWE-787**: Out-of-bounds Write
- **OWASP**: Security Misconfiguration
