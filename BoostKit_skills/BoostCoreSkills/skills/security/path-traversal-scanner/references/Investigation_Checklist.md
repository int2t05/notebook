# 手动调查清单 (Investigation Checklist)

## 概述

当静态分析无法确定漏洞存在时，需要手动调查验证。本文档提供系统化的调查方法和清单。

---

## 调查流程

### 步骤1：识别数据源

**目标**：确定数据来自哪里

**调查问题**：
```
□ 数据的直接来源是什么？
  ├─ HTTP请求参数？
  ├─ 命令行参数？
  ├─ 环境变量？
  ├─ 配置文件？
  ├─ 数据库查询？
  ├─ 网络接收？
  ├─ IPC通信？
  └─ 函数参数？

□ 数据的间接来源是什么？
  ├─ 调用链追踪
  ├─ 数据流分析
  └─ 依赖关系分析
```

**调查命令**：
```bash
# 查找变量赋值
grep -rn "variable\s*=" --include="*.py" --include="*.c"

# 查找函数调用
grep -rn "function_name\s*(" --include="*.py" --include="*.c"

# 查找配置读取
grep -rn "config.*read\|config.*load\|config.*parse" --include="*.py"

# 查找环境变量使用
grep -rn "getenv\|os\.environ\|environ\[" --include="*.py" --include="*.c"
```

---

### 步骤2：确定信任边界

**目标**：确定数据是否跨信任边界

**调查问题**：
```
□ 数据是否来自网络？
  ├─ Socket接收？
  ├─ RPC响应？
  ├─ 消息队列？
  ├─ WebSocket？
  └─ HTTP请求？

□ 数据是否来自其他进程？
  ├─ IPC通信？
  ├─ 共享内存？
  ├─ 管道？
  └─ 信号？

□ 数据是否来自用户输入？
  ├─ HTTP参数？
  ├─ CLI参数？
  ├─ 文件上传？
  └─ Cookie？

□ 数据是否在内部信任域内？
  ├─ 硬编码常量？
  ├─ 内部生成？
  ├─ 编译时常量？
  └─ 内部函数返回？
```

**调查命令**：
```bash
# 查找网络相关代码
grep -rn "socket\|recv\|send\|RPC\|grpc" --include="*.py" --include="*.c"

# 查找IPC相关代码
grep -rn "pipe\|shm\|queue\|IPC" --include="*.py" --include="*.c"

# 查找用户输入相关代码
grep -rn "request\.args\|getParameter\|sys\.argv\|argc" --include="*.py" --include="*.c"
```

---

### 步骤3：追踪数据流

**目标**：追踪数据从源到汇的完整路径

**调查问题**：
```
□ 数据经过哪些函数？
  ├─ 函数调用链
  ├─ 参数传递
  └─ 返回值传递

□ 数据经过哪些转换？
  ├─ 编码/解码
  ├─ 格式转换
  ├─ 字符串操作
  └─ 类型转换

□ 是否存在净化/验证？
  ├─ 输入验证
  ├─ 路径规范化
  ├─ 白名单检查
  └─ 危险字符过滤
```

**调查方法**：
```
1. 向后追踪（从Sink到Source）
   - 从文件操作开始
   - 追踪变量来源
   - 追踪函数调用链
   - 找到数据源

2. 向前追踪（从Source到Sink）
   - 从数据入口点开始
   - 追踪数据传播
   - 记录所有转换
   - 确定是否到达Sink

3. 跨文件追踪
   - 构建模块依赖图
   - 追踪导入关系
   - 追踪跨模块数据流
```

---

### 步骤4：验证净化有效性

**目标**：确定净化措施是否有效

**调查问题**：
```
□ 是否存在路径规范化？
  ├─ realpath() / resolve() / normalize()
  ├─ 规范化是否在验证之前？
  └─ 规范化是否完整？

□ 是否存在边界检查？
  ├─ startsWith() / contains()
  ├─ 检查是否在基础目录内？
  └─ 检查是否正确？

□ 是否存在白名单验证？
  ├─ 文件名白名单
  ├─ 路径白名单
  └─ 扩展名白名单

□ 是否存在危险字符过滤？
  ├─ '..' 过滤
  ├─ '/' 过滤
  ├─ '\\' 过滤
  └─ 空字节过滤
```

**常见无效净化**：
```python
# ❌ 无效：可被绕过
filename.replace('../', '')      # 绕过: ....// 或 ..%2f
filename.split('/')[-1]          # 绕过: /etc/passwd
if '../' not in filename:        # 绕过: ..%2f

# ✅ 有效：路径规范化
from pathlib import Path
base_path = Path(base_dir).resolve()
target_path = (base_path / filename).resolve()
if not str(target_path).startswith(str(base_path)):
    raise ValueError("路径穿越检测")
```

---

### 步骤5：评估可利用性

**目标**：确定漏洞是否可被利用

**调查问题**：
```
□ 攻击者能否控制数据？
  ├─ 数据源是否外部可控？
  ├─ 攻击者能否注入任意值？
  └─ 有哪些限制？

□ 攻击者能否构造攻击载荷？
  ├─ 路径穿越序列能否注入？
  ├─ 编码绕过是否可能？
  └─ 有哪些过滤需要绕过？

□ 攻击者能否到达目标文件？
  ├─ 目标文件是否存在？
  ├─ 应用是否有读取权限？
  └─ 路径是否可构造？
```

**攻击载荷测试**：
```bash
# 基本穿越
../../../etc/passwd

# URL编码
..%2f..%2f..%2fetc%2fpasswd

# 双重编码
..%252f..%252f..%252fetc%252fpasswd

# UTF-8编码
%c0%ae%c0%ae%c0%af

# 混合编码
%2e%2e%c0%af

# 绝对路径
/etc/passwd
```

---

## 调查清单

### 完整调查清单

```
【数据源识别】
□ 已识别直接数据源
□ 已识别间接数据源
□ 已追踪完整调用链
□ 已记录所有数据入口点

【信任边界确定】
□ 已确定数据是否来自网络
□ 已确定数据是否来自其他进程
□ 已确定数据是否来自用户输入
□ 已确定数据是否在内部信任域内
□ 已明确信任边界位置

【数据流追踪】
□ 已追踪数据从源到汇的完整路径
□ 已记录所有中间函数
□ 已记录所有数据转换
□ 已识别所有净化/验证点

【净化验证】
□ 已检查路径规范化
□ 已检查边界检查
□ 已检查白名单验证
□ 已检查危险字符过滤
□ 已验证净化有效性

【可利用性评估】
□ 已确定攻击者能否控制数据
□ 已确定攻击者能否构造载荷
□ 已确定攻击者能否到达目标
□ 已构造PoC（如果可利用）

【证据收集】
□ 已收集数据源证据
□ 已收集数据流证据
□ 已收集可利用性证据
□ 已记录所有假设
```

---

## 调查报告模板

```markdown
# 手动调查报告

## 基本信息

**文件**: [filename.ext:line_number](file:///path/to/file#Lline)
**函数**: function_name
**状态**: POTENTIAL / INFORMATIONAL
**调查日期**: YYYY-MM-DD
**调查人员**: 姓名

---

## 数据源分析

**直接数据源**: 
- 变量名: `filename`
- 来源: 函数参数
- 代码位置: file.c:123

**间接数据源**:
- 来源1: config->data_dir
  - 类型: CONFIGURATION
  - 初始化位置: config.c:456
  - 是否跨信任边界: 待确认

- 来源2: getenv("FILE_PATH")
  - 类型: EXTERNAL (环境变量)
  - 是否跨信任边界: 是
  - 攻击者可控: 是

**信任边界**:
- 数据来自: 环境变量
- 信任边界: 外部 → 应用
- 风险级别: 高

---

## 数据流追踪

```
[Source] getenv("FILE_PATH")  [EXTERNAL]
    │
    ▼
[Var] path = getenv(...)  [TAINTED]
    │  位置: config.c:456
    │
    ▼
[Var] config->data_dir = path  [TAINTED]
    │  位置: config.c:457
    │
    ▼
[Param] function_name(config->data_dir, ...)  [TAINTED]
    │  位置: main.c:789
    │
    ▼
[Var] full_path = config->data_dir + "/" + filename  [TAINTED]
    │  位置: file_ops.c:123
    │
    ▼
[Sink] fopen(full_path, "r")  [FILE OPERATION]
    │  位置: file_ops.c:124
    │
    ▼
Result: POTENTIAL - 数据源不明确
```

---

## 净化分析

**存在的净化**:
- ✗ 无路径规范化
- ✗ 无边界检查
- ✗ 无白名单验证
- ✗ 无危险字符过滤

**净化有效性**: 无净化

---

## 可利用性分析

**攻击者可控**: 
- ✅ 环境变量可被攻击者设置
- ❓ config->data_dir 是否受环境变量影响

**攻击载荷**: 
```
export FILE_PATH="/etc/passwd"
./application
```

**限制因素**:
- 需要能够设置环境变量
- 需要应用读取该环境变量

---

## 调查结论

**漏洞状态**: POTENTIAL

**原因**: 
- 环境变量可被攻击者控制
- 数据流路径清晰
- 无有效净化
- 但需确认应用是否实际使用该环境变量

**建议行动**:
1. 确认应用是否使用环境变量 FILE_PATH
2. 如果使用，升级为 CONFIRMED
3. 如果不使用，标记为 FALSE POSITIVE
4. 无论如何添加环境变量验证

**下一步调查**:
```bash
# 查找环境变量使用
grep -rn "FILE_PATH" --include="*.c" --include="*.h"

# 查找配置初始化
grep -rn "data_dir.*=" --include="*.c"
```
```

---

## 常见调查场景

### 场景1：配置文件路径

**问题**: 配置文件路径是否跨信任边界？

**调查步骤**:
```bash
# 1. 查找配置文件路径定义
grep -rn "config.*path\|CONFIG_PATH" --include="*.c"

# 2. 检查配置文件权限
ls -la /path/to/config

# 3. 检查配置文件所有者
stat /path/to/config

# 4. 检查配置文件是否可被用户修改
# - 权限是否过于宽松？
# - 是否在用户目录下？
# - 是否可被其他进程修改？
```

**判断标准**:
- 权限 600/640 + owner root → CONFIGURATION (中风险)
- 权限 644 + owner root → CONFIGURATION (中风险)
- 权限 666 + owner user → EXTERNAL (高风险)
- 在用户目录下 → EXTERNAL (高风险)

### 场景2：跨进程数据

**问题**: IPC数据是否跨信任边界？

**调查步骤**:
```bash
# 1. 查找IPC通信代码
grep -rn "pipe\|shm\|queue\|IPC" --include="*.c"

# 2. 确定通信双方
# - 发送进程是谁？
# - 接收进程是谁？
# - 是否在同一信任域？

# 3. 检查权限控制
# - 共享内存权限？
# - 管道权限？
# - 消息队列权限？
```

**判断标准**:
- 同一用户的不同进程 → CONFIGURATION (中风险)
- 不同用户的进程 → EXTERNAL (高风险)
- 容器间通信 → EXTERNAL (高风险)

### 场景3：数据库查询结果

**问题**: 数据库查询结果是否跨信任边界？

**调查步骤**:
```bash
# 1. 查找数据库查询
grep -rn "SELECT.*FROM\|query\|execute" --include="*.py"

# 2. 追踪查询参数
# - 参数是否来自用户输入？
# - 查询是否可被用户影响？

# 3. 分析查询结果
# - 结果是否包含用户可控数据？
# - 结果是否被用于文件路径？
```

**判断标准**:
- 查询参数来自用户输入 → EXTERNAL (高风险)
- 查询参数来自内部 → INTERNAL (低风险)
- 查询结果包含用户数据 → EXTERNAL (高风险)

---

## 参考资料

- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- CWE-22: Path Traversal: https://cwe.mitre.org/data/definitions/22.html
- SEI CERT: Validate Inputs from Untrusted Sources
