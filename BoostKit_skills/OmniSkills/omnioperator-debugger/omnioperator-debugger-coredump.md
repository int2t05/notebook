# OmniOperator Coredump 调试指南

当 OmniOperator 出现 coredump 时，按照以下步骤定位问题。

## 第 0 步：开启 Core Dump 生成（可选）

**重要**：如果系统未开启 core dump 生成，需要先配置：

```bash
# 1. 备份原有配置
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cp /proc/sys/kernel/core_pattern /tmp/core_pattern_bak'

# 2. 设置 core dump 文件生成路径（当前目录 + 进程 ID + 时间戳）
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'echo "`pwd`/core-%p-%t" | tee /proc/sys/kernel/core_pattern'

# 3. 验证设置
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cat /proc/sys/kernel/core_pattern'

# 4. 测试完成后恢复原有配置
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cp /tmp/core_pattern_bak /proc/sys/kernel/core_pattern'
```

**配置说明**：
- `core-%p-%t`：生成的文件名为 `core-进程 ID-时间戳`
- 默认情况下，core dump 文件会生成在当前工作目录
- 也可以通过 `/proc/sys/kernel/core_uses_pid` 控制是否在文件名中包含 PID

## 第 1 步：添加日志定位问题

### 在可疑代码路径添加日志

```cpp
// 在可能出问题的代码分支添加日志
std::cout << "[DEBUG] Function XYZ - vector count: " << vecCount 
          << ", row count: " << rowCount << std::endl;

// 检查指针有效性
if (ptr == nullptr) {
    std::cout << "[ERROR] Null pointer detected in Function XYZ" << std::endl;
}

// 打印代码分支
std::cout << "[TRACE] Entering branch A, encoding: " << (int)encoding << std::endl;
```

### 打印变量值

```cpp
// 打印关键变量
std::cout << "[DEBUG] Variable values: a=" << a << ", b=" << b 
          << ", result=" << result << std::endl;

// 打印向量信息
std::cout << "[DEBUG] Vector info - type: " << (int)vector->GetTypeId()
          << ", encoding: " << (int)vector->GetEncoding()
          << ", size: " << vector->size() << std::endl;
```

## 第 2 步：查看日志

### 查看 Spark 日志

```bash
# 从日志文件中提取错误信息
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'grep -iP "Error|Exception" -A 10 /path/to/log.txt | head -n 100'

# 查看完整的错误堆栈
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cat {{project.test_work_dir}}/perf_report_omni_*/logs/*.log | grep -A 50 "ERROR"'
```

### 查找 coredump 日志

如果发生 coredump，通过 `-XX:ErrorFile` 参数确定 coredump 日志目录：

```bash
# 查看 coredump 日志文件列表
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ls {{project.test_work_dir}}/*/spark_error_pid*.log | head -n 2'

# 查找最新的 coredump 日志
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'find {{project.test_work_dir}} -name "spark_error_*.log" -type f -mmin -60 | head -5'
```

### 分析 coredump 原因和错误栈

```bash
# 查看 fatal error 和 native stack
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'grep -P "A fatal error|Native" -A 20 {{project.test_work_dir}}/*/spark_error_pid*.log'

# 查看完整的 coredump 日志
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cat {{project.test_work_dir}}/*/spark_error_pid*.log'
```

**关键信息**：
- **Problematic frame**：崩溃发生的具体函数
- **SIGSEGV**：段错误（内存访问错误）
- **Native frames**：C++ 错误栈
- **Register info**：寄存器状态

### cleanup / destructor 栈不一定是第一现场

如果 coredump 的 native stack 落在 cleanup、析构或 LLVM/codegen 释放路径，例如：

- `FilterCodeGen::~FilterCodeGen`
- `ExpressionCodeGen::~ExpressionCodeGen`
- `LLVMEngine::~LLVMEngine`
- `llvm::orc::ExecutionSession::endSession`
- `std::unique_ptr<llvm::orc::LLJIT>::~unique_ptr`

不要立即把这些栈顶函数当作根因。它们经常只是最后触发崩溃的位置，真正的内存踩踏或状态损坏可能发生在更早的算子执行阶段。

建议处理顺序：

1. 先确认 SQL 是否已经完成核心执行。
   - 如果日志里已经出现 `Fetched N row(s)`，但随后失败，优先怀疑输出构造、分页状态、operator close/clear 或析构前状态不一致。

2. 根据物理计划回到对应算子链路。
   - 例如 `BroadcastHashJoin + ExistenceJoin` 应优先检查 `LookupJoinOperator::ProbeBatchForExistenceJoin` 和 `LookupJoinOutputBuilder`。

3. 用 `OMNI_CHECK` 抢第一现场。
   - 对 row index、batch index、partition、buffer size、offset/count、append/consume/clear 关系加检查。
   - 目标是把 `SIGSEGV` 转成可读的 `CHECK_ERROR`，让日志直接报告哪个不变量被破坏。

4. 对分页输出算子重点检查窗口语义。
   - 如果 builder 同时维护累计缓存和当前待输出数量，要区分 accumulated size、`rowCount`、`rowOffset` 和 remaining count。
   - 构造当前输出批次时，应验证当前窗口是否落在累计缓存范围内。

## 第 3 步：使用 GDB 分析 Core Dump（推荐）

**重要**：GDB 分析比日志更强大，可以直接查看堆栈、变量和内存状态。

### 查找 Core Dump 文件

```bash
# 查找最新的 core dump 文件
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ls -lt {{project.test_work_dir}}/core* | head -1'

# 查找所有 core dump 文件
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ls -lh {{project.test_work_dir}}/core*'
```

### 使用 GDB 分析 Core Dump

**基本分析（获取调用堆栈）**：

```bash
# 获取 backtrace（调用堆栈）
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "bt" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 获取 backtrace 和局部变量（推荐）
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "bt full" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'
```

**分析所有线程**：

```bash
# 获取所有线程的 backtrace
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "thread apply all bt" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 获取所有线程的 backtrace 和变量
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "thread apply all bt full" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'
```

**查看线程信息**：

```bash
# 列出所有线程
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "info threads" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 切换到指定线程并查看堆栈
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "thread 1" -ex "bt" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'
```

**查看变量和内存**：

```bash
# 打印变量值
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "frame 5" -ex "print variable" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 以十六进制打印指针
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "frame 5" -ex "print/x ptr" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 查看内存内容
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "x/20x 0xADDRESS" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'
```

**查看源代码和寄存器**：

```bash
# 显示源代码
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "frame 5" -ex "list" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 显示寄存器状态
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "info registers" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'

# 反汇编代码
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'cd {{project.test_work_dir}} && gdb -batch -ex "disas" /opt/omni-operator/lib/libspark_columnar_plugin.so core-<pid>-<timestamp>'
```

### GDB 常用命令速查表

| 命令 | 简写 | 说明 |
|------|------|------|
| `backtrace` | `bt` | 显示调用堆栈 |
| `backtrace full` | `bt full` | 显示堆栈和局部变量 |
| `thread apply all bt` | - | 显示所有线程的堆栈 |
| `thread <id>` | - | 切换到指定线程 |
| `info threads` | - | 显示所有线程信息 |
| `frame <n>` | `f <n>` | 切换到指定堆栈帧 |
| `info locals` | - | 显示当前帧的局部变量 |
| `print <var>` | `p <var>` | 打印变量值 |
| `print/x <var>` | `p/x <var>` | 以十六进制打印 |
| `x/<n>x <addr>` | - | 查看内存内容 |
| `list` | `l` | 显示源代码 |
| `info registers` | `info reg` | 显示寄存器状态 |
| `disassemble` | `disas` | 反汇编代码 |

### 完整的 GDB 分析示例

```bash
# 1. 查找最新的 core dump 文件
CORE_FILE=$(ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ls -t {{project.test_work_dir}}/core* | head -1')
echo "Found core file: $CORE_FILE"

# 2. 使用 GDB 分析（获取完整堆栈和变量）
ssh -p {{server.port}} {{server.username}}@{{server.host}} "cd {{project.test_work_dir}} && gdb -batch -ex 'bt full' /opt/omni-operator/lib/libspark_columnar_plugin.so $CORE_FILE" | tee gdb_analysis.log

# 3. 查看分析结果
cat gdb_analysis.log
```

### 分析结果解读

**典型输出示例**：

```
#0  0x0000fffe8dfa2060 in std::shared_ptr::get() at shared_ptr.h:1325
    this = 0x58
#1  0x0000fffe8df83dfc in common::SetDictionaryStringVectorValue() at PredicateUtil.cpp:380
    value = "corpunivamalg #12"
    offset = 1894
    baseVector = 0xfffde033fa00
    selectedBaseVector = 0x0  ← 空指针！
#2  0x0000fffe8df85c40 in common::GetFlatBaseVectorsFromBitMark() at PredicateUtil.cpp:558
    dictBaseVector = 0xfffde033fa00
    dictSelectedBaseVector = 0x0  ← 空指针！
```

**关键信息**：
- **帧编号**：`#0` 是最顶层（崩溃点），数字越大越底层
- **函数名和文件位置**：精确指出崩溃位置
- **变量值**：帮助定位问题根因（如 `selectedBaseVector = 0x0`）
- **this 指针**：`this = 0x58` 表示访问了接近 NULL 的地址

## 第 4 步：结合代码分析

### 定位问题代码

根据 coredump 日志或 GDB 分析中的函数名，在代码库中找到对应文件：

```bash
# 在本地代码库搜索相关函数
grep -rn "function_name" {{project.remote_work_dir}}

# 使用 IDE 搜索函数定义
# 在 VSCode 或 CLion 中使用 "Go to Symbol" 功能
```

### 常见崩溃原因

1. **空指针解引用**：未检查指针是否为 nullptr
2. **数组越界**：访问超出 vector 范围的索引
3. **类型转换错误**：错误的 reinterpret_cast
4. **未初始化的变量**：使用了未初始化的指针或引用
5. **内存释放后使用**：Use-after-free

### 示例分析

```cpp
// 问题代码示例
auto value = static_cast<ContainerVector *>(vector)->GetValue(vecIdx);
auto valueVec = reinterpret_cast<BaseVector *>(value);
DYNAMIC_TYPE_DISPATCH(PrintFlatVectorValue, valueVec->GetTypeId(), valueVec, rowIndex);
// 如果 valueVec 为 nullptr，会导致 SIGSEGV

// 修复代码
auto value = static_cast<ContainerVector *>(vector)->GetValue(vecIdx);
if (value == nullptr) {
    std::cout << "[ERROR] GetValue returned nullptr, vecIdx: " << vecIdx << std::endl;
    continue;
}
auto valueVec = reinterpret_cast<BaseVector *>(value);
if (valueVec == nullptr) {
    std::cout << "[ERROR] valueVec is nullptr" << std::endl;
    continue;
}
DYNAMIC_TYPE_DISPATCH(PrintFlatVectorValue, valueVec->GetTypeId(), valueVec, rowIndex);
```

### 验证修复

```bash
# 修改代码后重新上传
scp -P {{server.port}} /本地路径/fixed_file.cpp {{server.username}}@{{server.host}}:{{project.remote_work_dir}}/OmniOperator/core/src/
```

```python
# 重新编译并部署可供 Spark SQL 加载的 Omni + Gluten 产物
compile_gluten(
    omni_branch="<omni branch>",
    gluten_branch="<gluten branch>",
)

# 重新执行测试
run_e2e_sql(sql="<q62_test SQL text>", database="<database>", timeout_sec=300)
```

```bash
# 检查是否还有 coredump
ssh -p {{server.port}} {{server.username}}@{{server.host}} 'ls {{project.test_work_dir}}/*/spark_error_*.log | wc -l'
```

