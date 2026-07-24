---
name: "secure-compile-checker"
description: "Checks C/C++ code for secure compile options compliance based on BoostKit SecureCompile standards. Invoke when user requests secure compile check, build security review, or hardening verification."
---

# Secure Compile Checker

This skill checks whether C/C++ code is compiled with secure compile options as specified in [SecureCompile(C&C++).md](https://gitcode.com/boostkit/community/blob/master/docs/security-Commitize/SecureCompile(C&C++).md).

## Core Principles

1. **逐目标检查**: 不是看项目整体有没有某个选项，而是**每个构建目标**单独检查。目标 A 配置了 `-fPIC` 不代表目标 B 也配置了。
2. **条件编译分支**: 必须检查安全选项是否在**所有分支**生效。例如 `configure.ac` 中仅在 OpenSSL 1.1.1 分支设置安全选项，OpenSSL 3.0+ 分支缺失，应标记为 ⚠️ 部分配置。
3. **区分动态库和可执行文件**: 动态库(.so)检查 `-fPIC`，可执行文件检查 `-fPIE -pie`，不混用。
4. **只检查生产目标**: fuzz/ut/perf 测试目标不检查，因为它们不会部署到生产环境。
5. **证据溯源**: 每个判断都标注源文件和行号，可以回溯验证。

---

## Execution Steps (6-Step Methodology)

### Step 1: 项目语言检测 [强制]

**目标**: 确定项目是否为 C/C++ 项目，决定是否需要检查安全编译选项。

**方法**:
1. 扫描源文件扩展名统计数量
   - C: `.c`, `.h`
   - C++: `.cpp`, `.cxx`, `.cc`, `.c++`, `.hpp`, `.hxx`, `.hh`
   - Java: `.java` | Python: `.py` | Go: `.go` | Rust: `.rs`
2. 检测构建系统特征文件
   - C/C++: `CMakeLists.txt`, `Makefile`, `configure.ac`, `meson.build`
   - Java: `pom.xml`, `build.gradle` | Python: `setup.py`, `pyproject.toml`
   - Go: `go.mod` | Rust: `Cargo.toml`
3. 综合判定主语言

**语言分类**:

| 语言 | 是否检查编译选项 | 原因 |
|------|-----------------|------|
| C / C++ | ✅ 是 | 需要编译器安全选项保护 |
| Java | ❌ 否 | JVM 有内置安全机制 |
| Python | ❌ 否 | 解释型语言 |
| Go | ❌ 否 | 内置安全特性 |
| Rust | ❌ 否 | 默认内存安全 |
| JavaScript/TS | ❌ 否 | 解释/V8 引擎 |
| C# | ❌ 否 | .NET 运行时 |

**非 C/C++ 项目输出**:
```markdown
## <project_name>

**Language**: <detected_language>
**Status**: ⏭ Skipped (Non-C/C++ project)

Secure compile options check is only applicable to C/C++ projects.
```

---

### Step 2: 构建系统识别 [强制]

**目标**: 识别构建系统类型，找出所有生产构建目标，排除测试目标。

**方法**:
1. 查找构建配置文件:

| 构建系统 | 文件模式 |
|---------|---------|
| CMake | `CMakeLists.txt`, `*.cmake` |
| Autotools | `configure.ac`, `Makefile.am` |
| Make | `Makefile`, `Makefile.in` |
| Meson | `meson.build`, `meson.options` |
| Bazel | `BUILD`, `BUILD.bazel` |
| QMake | `*.pro` |
| SCons | `SConstruct`, `SConscript` |

2. 识别生产构建目标:

| 构建系统 | 动态库目标 | 可执行文件目标 |
|---------|-----------|--------------|
| CMake | `add_library(... SHARED)` | `add_executable(...)` |
| Autotools | `lib_LTLIBRARIES` | `bin_PROGRAMS` |
| Make | `$(CC) -shared` / `.so` 目标 | 无 `-shared` 的链接目标 |

3. 排除测试/调试目标（不检查安全编译选项）:
   - 路径含 `test/`, `tests/`, `ut/`, `fuzz/`, `perf/`, `benchmark/`
   - 目标名含 `test`, `fuzz`, `perf`, `benchmark`, `demo`, `example`
   - 构建类型为 `Debug`, `Coverage`, `Sanitizer`

4. 检查构建脚本（`build.sh`, `Makefile` 等）中是否有额外的 strip/rpath 操作

**输出**: 列出所有生产构建目标及其类型（动态库/可执行文件）、源码位置、构建文件路径。

---

### Step 3: 编译选项提取 [强制]

**目标**: 从构建文件中逐目标提取所有安全相关的编译和链接选项。

**方法**:
1. 逐个读取每个生产目标对应的构建文件
2. 提取以下变量中的安全相关选项:
   - `CFLAGS` / `CXXFLAGS` — 编译选项
   - `LDFLAGS` / `LDFLAGS` — 链接选项
   - `target_compile_options` — CMake 目标编译选项
   - `target_link_options` — CMake 目标链接选项
3. **条件编译分支分析** [关键]:
   - CMake: 检查 `if()` / `elseif()` / `else()` 分支
   - Autotools: 检查 `AS_IF()` / `AM_CONDITIONAL` 分支
   - Makefile: 检查 `ifeq` / `ifdef` 分支
   - **必须确认安全选项在所有分支是否生效**
4. 检查选项继承关系:
   - CMake: `CMAKE_C_FLAGS` → 子目标继承
   - Autotools: `AC_SUBST([CFLAGS])` → 覆盖而非追加
   - Makefile: `CFLAGS +=` 追加 vs `CFLAGS =` 覆盖
5. 记录每个选项的**源文件和行号**

**提取模式**:

CMake:
```cmake
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIE")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -pie")
target_compile_options(target PRIVATE -fstack-protector-strong)
target_link_options(target PRIVATE -Wl,-z,relro,-z,now)
```

Autotools:
```makefile
CFLAGS += -fPIC -fstack-protector-strong
LDFLAGS += -Wl,-z,relro,-z,now
```
```m4
AC_SUBST([CFLAGS], ["-Wl,-z,relro,-z,now -fstack-protector-strong"])
```

Makefile:
```makefile
CFLAGS := -Wall -fPIC -fstack-protector-strong
LDFLAGS += -Wl,-z,relro,-z,now -Wl,-z,noexecstack -s
```

---

### Step 4: 必须配置选项检查 [强制]

**目标**: 逐目标检查 9 项必须配置的安全编译选项。

**必须选项列表**:

| # | 选项 | 适用目标 | 作用 | 检查方式 |
|---|------|---------|------|---------|
| 1 | `-fPIC` / `-fpic` | 动态库 | ASLR 位置无关代码 | grep 构建文件 |
| 2 | `-fPIE` + `-pie` | 可执行文件 | ASLR 位置无关可执行 | grep 构建文件 |
| 3 | `-fstack-protector-strong` 或 `-fstack-protector-all` | 所有 | 栈溢出保护 | grep 构建文件 |
| 4 | `-Wl,-z,relro` | 所有 | GOT 表部分只读 | grep 构建文件 |
| 5 | `-Wl,-z,relro,-z,now` | 所有 | GOT 表完全只读 (Full RELRO) | grep 构建文件 |
| 6 | `-Wl,-z,noexecstack` | 所有 | 栈不可执行 | grep 构建文件 |
| 7 | `-s` 或 `strip` | 所有 | 符号剥离 | grep 构建文件 + build.sh |
| 8 | 禁止 RPATH | 所有 | 防止动态库劫持 | grep 构建文件（应**不存在** rpath） |
| 9 | `-D_FORTIFY_SOURCE=2` + `-O2` | 所有 | 缓冲区溢出检测 | grep 构建文件 |

**逐目标检查规则**:

| 目标类型 | 检查项 | 不适用项 |
|---------|--------|---------|
| 动态库(.so) | 1,3,4,5,6,7,8,9 | 2 (PIE 不适用) |
| 可执行文件 | 2,3,4,5,6,7,8,9 | 1 (PIC 不适用) |

**判定标准**:

| 状态 | 含义 |
|------|------|
| ✅ | 所有目标均已配置 |
| ⚠️ | 部分目标配置 / 仅特定条件分支配置 |
| ❌ | 所有目标均未配置 |
| ⚪ | 不适用（如动态库不检查 PIE） |

**条件分支检查** [关键]:
- 如果安全选项仅在某个条件分支（如特定 OpenSSL 版本、特定平台）配置，其他分支缺失 → 标记为 ⚠️
- 如果 `AC_SUBST([CFLAGS], ...)` 会覆盖而非追加 Makefile.am 中的 CFLAGS → 需明确指出覆盖风险
- 如果安全选项通过变量继承（如 CMAKE_C_FLAGS）而非显式声明 → 标记为 ⚠️ 并说明

**RPATH 检查** (反向检查):
- 搜索 `-Wl,-rpath,` 或 `-Wl,--rpath` 或 `RPATH`
- 存在 → ❌ (应禁止)
- 不存在 → ✅
- `-Wl,--disable-new-dtags` → 可接受（防止 RUNPATH 生成）

---

### Step 5: 建议配置选项检查 [强制]

**目标**: 逐目标检查 5 项建议配置的安全编译选项。

| # | 选项 | 作用 |
|---|------|------|
| 1 | `-D_FORTIFY_SOURCE=2` + `-O2` | 缓冲区溢出检测（同必须项 9） |
| 2 | `-fvisibility=hidden` | 符号可见性控制，减少攻击面 |
| 3 | `-ftrapv` | 有符号整数溢出检测 |
| 4 | `-fstack-check` | 栈溢出检测 |
| 5 | `-fstack-clash-protection` | 栈冲突保护 |

**判定标准**: 同 Step 4

---

### Step 6: 生成报告和日志 [强制]

**目标**: 生成完整的安全编译选项检查报告和日志。

**必须生成 2 个文件**:

| 文件 | 路径 | 内容 |
|------|------|------|
| 报告 | `Report/<YYYY-MM-DD>/<ProjectName>_SecureCompile_Report_<YYYY-MM-DD>.md` | 检查结果、修复建议 |
| 日志 | `Report/<YYYY-MM-DD>/<ProjectName>_SecureCompile_Report_<YYYY-MM-DD>.log` | 扫描过程详细记录 |

---

## Report Template

```markdown
# <ProjectName> 安全编译选项检查报告

**检查日期**: <YYYY-MM-DD>
**项目**: <repo_url_or_path>
**语言**: <C/C++>
**构建系统**: <CMake/Autotools/Makefile/...>
**标准依据**: BoostKit SecureCompile(C&C++)标准

---

## 〇、项目结构与构建目标说明

<项目> 包含 **N 个生产构建目标**：

```
<ProjectName>/
├── <path1>/CMakeLists.txt          ← 定义 X 个目标
│   ├── <target1>  (动态库 .so)     ← 功能说明
│   └── <target2>  (可执行文件)     ← 功能说明
│
└── <path2>/Makefile.am             ← 定义 Y 个目标
    └── <target3>  (动态库 .so)     ← 功能说明
```

| 构建目标 | 类型 | 源码位置 | 构建文件 | 功能说明 |
|---------|------|---------|---------|---------|
| **<target1>** | 动态库 | `<path>` | `<build_file:line>` | 功能描述 |
| **<target2>** | 可执行文件 | `<path>` | `<build_file:line>` | 功能描述 |

**依赖关系**：
```
<target2> (可执行文件)
    └── <target1> (动态库)
```

---

## 一、检查结果汇总

| 分类 | 数量 | 占比 |
|------|------|------|
| ✅ 已配置 | X | XX.X% |
| ❌ 未配置 | Y | YY.Y% |
| **总计（必须项）** | **9** | **100%** |

### 合规评分

| 目标 | 必须项合规 | 建议项合规 | 综合评分 |
|------|-----------|-----------|---------|
| <target1> | X/9 (XX%) | Y/5 (YY%) | ZZ.Z% |
| <target2> | X/9 (XX%) | Y/5 (YY%) | ZZ.Z% |
| **项目整体** | **X/9 (XX%)** | **Y/5 (YY%)** | **ZZ.Z%** |

> 如有严重不足的目标，在此突出警告。

---

## 二、必须配置选项检查

### 2.1 ASLR - 位置无关代码 (-fPIC)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/❌ | `<file:line>` |
| <target2> | ⚪ | 不适用（可执行文件） |

**风险说明**: 缺少 `-fPIC` 的风险描述。

### 2.2 ASLR - 位置无关可执行 (-fPIE + -pie)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ⚪ | 不适用（动态库） |
| <target2> | ✅/❌ | `<file:line>` |

### 2.3 栈保护 (-fstack-protector-strong)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/⚠️/❌ | `<file:line>` |

### 2.4 RELRO Partial (-Wl,-z,relro)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/⚠️/❌ | `<file:line>` |

### 2.5 RELRO Full (-Wl,-z,relro,-z,now)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/⚠️/❌ | `<file:line>` |

### 2.6 不可执行栈 (-Wl,-z,noexecstack)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/❌ | `<file:line>` |

### 2.7 符号剥离 (-s / strip)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/❌ | `<file:line>` |

### 2.8 禁止 RPATH

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/❌ | `<file:line>` |

### 2.9 FORTIFY_SOURCE (-D_FORTIFY_SOURCE=2 -O2)

| 目标 | 状态 | 证据 |
|------|------|------|
| <target1> | ✅/⚠️/❌ | `<file:line>` |

---

## 三、建议配置选项检查

### 3.1 FORTIFY_SOURCE (-D_FORTIFY_SOURCE=2 -O2)

| 目标 | 状态 |
|------|------|
| <target1> | ✅/❌ |

### 3.2 符号可见性 (-fvisibility=hidden)

| 目标 | 状态 |
|------|------|
| <target1> | ✅/❌ |

### 3.3 整数溢出检测 (-ftrapv)

| 目标 | 状态 |
|------|------|
| <target1> | ✅/❌ |

### 3.4 栈溢出检测 (-fstack-check)

| 目标 | 状态 |
|------|------|
| <target1> | ✅/❌ |

### 3.5 栈冲突保护 (-fstack-clash-protection)

| 目标 | 状态 |
|------|------|
| <target1> | ✅/❌ |

---

## 四、逐目标详细分析

### 4.1 <target1> (<类型>) — 评分: XX.X%

**构建文件**: `<build_file>`

```
<提取的 CFLAGS / LDFLAGS 原文>
```

| 选项 | 状态 | 备注 |
|------|------|------|
| -fPIC | ✅/❌ | |
| ... | ... | |

### 4.2 <target2> (<类型>) — 评分: XX.X%

(同上格式)

---

## 五、修复建议

### 🔴 优先级：高 — <严重问题标题>

<问题描述和修复方案，包含代码示例>

```makefile
# 修改前
<原代码>

# 修改后
<修复后代码>
```

### 🟡 优先级：中 — <中等问题标题>

<问题描述和修复方案>

### 🟢 优先级：低 — <低优先级建议>

<建议描述>

---

## 六、检查结果矩阵

| 安全编译选项 | <target1> | <target2> | <target3> | 标准 |
|-------------|-----------|-----------|-----------|------|
| **-fPIC** | ✅/❌ | ✅/❌ | ⚪ | 必须 |
| **-fPIE -pie** | ⚪ | ✅/❌ | ⚪ | 必须 |
| **-fstack-protector-strong** | ✅/⚠️/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-Wl,-z,relro** | ✅/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-Wl,-z,relro,-z,now** | ✅/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-Wl,-z,noexecstack** | ✅/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-s / strip** | ✅/❌ | ✅/❌ | ✅/❌ | 必须 |
| **禁止 RPATH** | ✅/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-D_FORTIFY_SOURCE=2** | ✅/⚠️/❌ | ✅/❌ | ✅/❌ | 必须 |
| **-fvisibility=hidden** | ✅/❌ | ✅/❌ | ✅/❌ | 建议 |
| **-ftrapv** | ✅/❌ | ✅/❌ | ✅/❌ | 建议 |
| **-fstack-check** | ✅/❌ | ✅/❌ | ✅/❌ | 建议 |
| **-fstack-clash-protection** | ✅/❌ | ✅/❌ | ✅/❌ | 建议 |

> ✅ 已配置 | ❌ 未配置 | ⚠️ 部分配置（仅特定分支） | ⚪ 不适用

---

## 七、总结

<项目安全编译选项配置的整体评价，包含：>
1. 各目标配置水平对比
2. 最需要修复的组件
3. 条件分支缺失情况
4. 全局缺失项
```

---

## Log Template

日志文件记录扫描的每个步骤和决策过程：

```
================================================================================
<ProjectName> 安全编译选项检查日志
================================================================================
检查日期: <YYYY-MM-DD>
项目: <repo_url_or_path>
语言: <C/C++>
构建系统: <type>
标准依据: BoostKit SecureCompile(C&C++)标准
================================================================================

最终结论: 必须选项 X/9 (XX.X%), 建议选项 Y/5 (YY.Y%), 综合评分 ZZ.Z%

================================================================================
[STEP 1] 项目语言检测
================================================================================

  检测方法: 文件扩展名分析 + 构建系统检测
  源文件扩展名: <.c, .h, .cpp, ...>
  构建系统: <CMake/Autotools/...>
  语言判定: <C/C++>
  是否需要检查编译选项: ✅ 是 / ❌ 否

================================================================================
[STEP 2] 构建系统识别
================================================================================

  生产构建目标 (N个):
    1. <target1> — <build_file> (<类型>)
    2. <target2> — <build_file> (<类型>)

  排除的测试目标:
    - <test_target1> (原因: 测试目标)
    - <test_target2> (原因: fuzz 目标)

  构建脚本: <build.sh>

================================================================================
[STEP 3] 编译选项提取
================================================================================

  [3.1] <target1> (<build_file>)
    CFLAGS = <提取的编译选项>
    LDFLAGS = <提取的链接选项>
    条件分支: <描述条件编译分支情况>

  [3.2] <target2> (<build_file>)
    CFLAGS = <提取的编译选项>
    LDFLAGS = <提取的链接选项>

================================================================================
[STEP 4] 必须配置选项检查
================================================================================

  [4.1] ASLR - PIC (-fPIC)
    <target1>: ✅ <file:line>
    <target2>: ❌ 未配置
    判定: ⚠️ 部分缺失

  (逐项记录...)

================================================================================
[STEP 5] 建议配置选项检查
================================================================================

  (逐项记录...)

================================================================================
[STEP 6] 关键风险分析
================================================================================

  🔴 高风险 — <描述>
  🟡 中风险 — <描述>
  🟢 低风险 — <描述>

================================================================================
扫描统计
================================================================================

  项目语言:         <C/C++>
  构建系统:         <type>
  生产构建目标数:   N
  测试构建目标数:   M (不检查)
  必须选项合规率:   XX.X% (X/9)
  建议选项合规率:   XX.X% (Y/5)
  综合评分:         ZZ.Z%

  各目标评分:
    <target1>:       XX.X% ✅/❌
    <target2>:       XX.X% ✅/❌

================================================================================
扫描完成
================================================================================
```

---

## Scoring Methodology

### 单目标评分计算

```
必须项得分 = (已配置必须项数 / 适用必须项总数) × 70
建议项得分 = (已配置建议项数 / 适用建议项总数) × 30
综合评分 = 必须项得分 + 建议项得分
```

### 项目整体评分

```
项目必须项合规率 = 所有目标已配置必须项数之和 / 所有目标适用必须项总数
项目建议项合规率 = 所有目标已配置建议项数之和 / 所有目标适用建议项总数
项目综合评分 = 项目必须项合规率 × 70 + 项目建议项合规率 × 30
```

### 评分等级

| 评分 | 等级 | 说明 |
|------|------|------|
| ≥ 85% | ✅ 良好 | 安全编译选项配置完善 |
| 60-84% | ⚠️ 一般 | 存在部分缺失，需修复 |
| < 60% | ❌ 不足 | 安全编译选项严重缺失，需立即修复 |

---

## Notes

1. **ASLR Check**:
   - 动态库(.so): 检查 `-fPIC` 或 `-fpic`
   - 可执行文件: 检查 `-fPIE`/`-fpie` + `-pie`
   - 如果动态库同时配置了 `-fPIC` 和 `-fPIE`，`-fPIC` 优先，功能不受影响，但属于配置冗余

2. **Stack Protector**:
   - 优先 `-fstack-protector-strong`（平衡保护和性能）
   - `-fstack-protector-all` 也可接受但性能开销更大
   - 如果同时配置了 `-fstack-protector-all` 和 `-fstack-protector-strong`，后者优先

3. **RELRO**:
   - Full RELRO (`-Wl,-z,relro,-z,now`) 优于 Partial (`-Wl,-z,relro`)
   - 配置了 Full RELRO 即满足 Partial RELRO 要求

4. **RPATH** (反向检查):
   - 存在 `-Wl,-rpath,` 或 `-Wl,--rpath` → ❌
   - 不存在 → ✅
   - `-Wl,--disable-new-dtags` → 可接受

5. **Strip**:
   - 检查 `-s` 链接选项
   - 检查 `strip` 命令在构建脚本中
   - 检查 `objcopy --strip-all` + `--add-gnu-debuglink`（最佳实践）

6. **FORTIFY_SOURCE**:
   - 必须同时配置 `-D_FORTIFY_SOURCE=2` 和 `-O2`（或更高优化级别）
   - 仅配置 `-D_FORTIFY_SOURCE=2` 无 `-O2` 无效

7. **条件分支覆盖**:
   - `AC_SUBST([CFLAGS], ...)` 会**覆盖** Makefile.am 中的 CFLAGS，而非追加
   - CMake `set(CMAKE_C_FLAGS ...)` 会覆盖，`set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ...")` 追加
   - Makefile `CFLAGS =` 覆盖，`CFLAGS +=` 追加

## Reference

Based on: [SecureCompile(C&C++).md](https://gitcode.com/boostkit/community/blob/master/docs/security-Committee/SecureCompile(C&C++).md)
