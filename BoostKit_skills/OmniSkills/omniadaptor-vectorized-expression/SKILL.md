---
name: omniadaptor-vectorized-expression
description: 在 OmniAdaptor 中适配 OmniOperator「向量化表达式框架」的端到端流程（先调研后适配 + 结果正确性对比）。当用户需要在 OmniStream/OmniAdaptor 中新增或使能某个 Flink SQL 表达式/函数走 native 向量化执行时使用。流程要点：适配前必须先调研 flink/docs/data/sql_functions.yml 与 OmniOperator 向量化实现，核对支持类型与语义、入参类型匹配；测试用 CSV 黄金对比（通过 config.sh 切换 OmniStream/原生 Flink，对比两边输出文件是否逐行一致）。触发词：向量化表达式适配、vectorization 表达式、向量化函数适配、preferVectorization、RexNodeUtil 向量化、表达式正确性对比、CSV 黄金对比、sql_functions 调研。
---

# OmniAdaptor 向量化表达式适配

在 OmniAdaptor（Flink Calcite 侧）把一个 Flink SQL 函数翻译成 OmniStream 能识别的 JSON 表达式协议，使其走 OmniOperator 的**向量化表达式框架**（`StreamCalcBatch.cpp` 已设 `preferVectorization=true`）执行，并完成「**调研 → 改代码 → 上传 → 构建 → 正确性对比 → 报告**」闭环。

> 本 skill 针对 OmniOperator 的**向量化表达式框架**。两条贯穿全程的核心原则：
> 1. **先调研后适配**：动 `RexNodeUtil.java` 之前，必须核对 `flink/docs/data/sql_functions.yml`（语义/类型）与 OmniOperator 向量化实现（注册类型/语义），并检查入参类型是否匹配。跳过调研会导致类型不支持、语义不一致。
> 2. **结果正确性对比**：不能只看是否走 native；必须用 CSV 黄金对比确认 OmniStream 与原生 Flink 的计算结果**逐行一致**。

## 配置说明

| 占位符 | 说明 | 默认值 |
|--------|------|--------|
| `<SKILL_DIR>` | 本 skill 所在目录 | 当前工作区 `.agents/skills/omniadaptor-vectorized-expression` |
| `<REMOTE_CODE_ROOT>` | 远端代码根目录 | `/opt/buildtools` |
| `<DEPENDENCY_LIB_DIR>` | 依赖库目录（jar/so 部署） | `/home/Dependency_library` |
| `<FLINK_HOME>` | Flink 安装目录 | `/opt/flink` |

## 关键环境信息

| 项 | 值 |
|----|----|
| 目标服务器 | 通过 `ssh-skill` 查询获取服务器别名（见下方「获取服务器别名」），后续所有远端操作均用该别名 |
| 远端代码根目录 | `<REMOTE_CODE_ROOT>`（本地 `OmniAdaptor/` → 远端 `<REMOTE_CODE_ROOT>/OmniAdaptor/`） |
| SSH/传输方式 | 一律走 `ssh-skill` 的 Python 脚本（`ssh_execute.py`/`ssh_upload.py`/`ssh_download.py`），配置由 `ssh-skill` 统一管理，禁止直接 `ssh`/`scp` |
| 依赖库目录 | `<DEPENDENCY_LIB_DIR>`（jar/so 部署到此处） |
| Flink 目录 | `<FLINK_HOME>` |
| 向量化函数实现 | `OmniOperatorJIT/core/src/vectorization/functions/*.{h,cpp}` |
| 向量化函数注册 | `OmniOperatorJIT/core/src/vectorization/registration/Register*.cpp` + `RegistrationHelpers.h` |
| 函数语义/类型参考 | `OmniAdaptor/omnihelper/src/main/resources/flink/docs/data/sql_functions.yml` |
| 函数字典 | `OmniAdaptor/omnihelper/resources/flink_function_dictionary.json` |
| 协议生成 | `OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java` |

### 获取服务器别名（首次远端操作前必做）

所有远端信息由 `ssh-skill` 统一管理，本 skill 不再保存任何服务器 IP/端口/密钥。首次需要连远端时，先用 `ssh-skill` 查询目标服务器，拿到别名后在后续脚本中使用：

```bash
# 查找目标 OmniAdaptor 构建服务器（按关键词，如 OmniAdaptor / buildtools / 目标 IP）
python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_config_manager_v3.py" find "<关键词>"

# 若查不到任何匹配，列出全部已配置服务器人工确认
python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_config_manager_v3.py" list-servers
```

- 从返回 JSON 中取 `alias` 字段作为后续所有远端命令的 `<别名>`。
- 若确实没有对应服务器配置，**先向用户确认服务器信息**，再用 `ssh_config_manager_v3.py create` 登记别名，切勿在本 skill 内硬编码 IP/端口/密钥。

## 工作流程总览

复制以下清单跟踪进度：

```
向量化适配进度:
- [ ] 步骤 1: 调研（sql_functions.yml 语义/类型 + OmniOperator 向量化注册类型 + 入参匹配）
- [ ] 步骤 2: 表达式适配（改 3 处 RexNodeUtil + 1 处字典，注意类型匹配）
- [ ] 步骤 3: 上传修改文件到服务器
- [ ] 步骤 4: 按需重新构建并修复报错
- [ ] 步骤 5: 结果正确性对比（CSV 黄金对比，config.sh 切换两引擎）
- [ ] 步骤 6: 生成总结报告
```

---

## 步骤 1：调研（适配前必做，不可跳过）

目的：在动 `RexNodeUtil.java` 之前，先确认「Flink 侧语义/类型」与「OmniOperator 向量化侧实现/注册类型」是否一致、入参类型是否被支持。**类型不支持、语义不一致等问题都源于跳过这一步。**

### 1.1 调研 Flink 侧语义与支持类型 —— `flink/docs/data/sql_functions.yml`

按函数名（如 `INSTR`、`FROM_UNIXTIME`、`GREATEST`）检索该文件，确认：
- **签名与语义**：参数个数、参数类型、返回类型、NULL 行为、边界行为（如下标从 1 还是 0、越界如何处理、负数行为）。
- **类型覆盖**：该函数在 Flink 中允许哪些入参类型（如 `numeric` 泛指 TINYINT/SMALLINT/INT/BIGINT/FLOAT/DOUBLE/DECIMAL；`string` 指 CHAR/VARCHAR）。

记录下「Flink 期望语义」，作为后续正确性对比的预期基准。

### 1.2 调研 OmniOperator 向量化实现与注册类型

向量化框架是 Velox 风格的 SimpleFunction 注册：每个函数通过
`RegisterFunction<T, Ret, Arg...>(name, {OMNI_ARG_TYPES...}, OMNI_RET_TYPE)` 显式声明**入参 OMNI 类型**与**返回 OMNI 类型**。

操作：
1. 在 `vectorization/registration/Register*.cpp` 中找到目标函数的注册（按 `name` 字符串检索，如 `"from_unixtime"`、`"instr"`）。确认：
   - **注册名**（dispatch 唯一键，通常小写；注意个别用 CamelCase 对齐 Gluten，如 `DateFormat`）。
   - **每个重载注册的入参 OMNI 类型集合**（如 `{OMNI_LONG}`、`{OMNI_VARCHAR, OMNI_VARCHAR}`、`{OMNI_INT, OMNI_INT}`）。常见批量注册见 `RegistrationHelpers.h`（如 `RegisterUnaryNumeric` 覆盖 BYTE/SHORT/INT/LONG/FLOAT/DOUBLE/DECIMAL）。
2. 在 `vectorization/functions/<Name>.{h,cpp}` 中阅读 `call(...)`/`callNullable(...)` 实现，确认**语义是否与 1.1 的 Flink 语义一致**（下标基准、NULL 处理、舍入、时区等）。

### 1.3 类型匹配判定（核心）

把「`RexNodeUtil` 将要传入的入参类型」与「1.2 中向量化注册支持的 OMNI 类型集合」逐一比对：

| 情况 | 处置 |
|------|------|
| 入参类型已被注册覆盖，语义一致 | 直接适配（步骤 2） |
| 入参类型未被覆盖，但**仅需在 OmniAdaptor 侧加 CAST** 转成已支持类型即可，且不改变语义 | 在 `RexNodeUtil` 生成 CAST 子表达式，继续步骤 2 |
| 入参类型未被覆盖，需在 OmniOperator 侧注册新的参数类型 | **向用户报告**，OmniOperator 不支持该类型，流程结束 |
| 语义不一致（下标/NULL/边界/时区等不同），或需**新增/修改 OmniOperator 向量化实现**、新增类型重载、改注册等重大改动 | **向用户报告**，OmniOperator 不支持该函数语义，流程结束 |

> 在 OmniAdaptor 侧加 CAST 的判据：目标类型已被向量化注册支持、且 CAST 本身语义安全（不丢精度/不改变结果）。否则归类为「OmniOperator 不支持」，向用户报告后流程结束。

### 1.4 调研结论（写入最终报告）

输出一份简表：函数名、Flink 语义要点、向量化注册名与支持类型、入参类型匹配结论（直接/加 CAST/OmniOperator 不支持）。

---

## 步骤 2：表达式适配

> 仅在步骤 1 判定为「直接适配」或「OmniAdaptor 加 CAST」时进行；若 OmniOperator 不支持（类型未覆盖/语义不一致），流程已在步骤 1 结束。

以 `abs` 为模板，改 **2 个文件、共 4 处**。

### 2.1 函数字典 `OmniAdaptor/omnihelper/resources/flink_function_dictionary.json`

把目标函数标记为支持，`is_supported_type` **只写步骤 1.3 确认向量化真正支持（或可经 CAST 安全转换）的类型**：

```json
{"func_name": "ABS", "is_support_func": true, "is_supported_type": ["BIGINT", "INTEGER", "DOUBLE"]}
```

### 2.2 `RexNodeUtil.java`（`omni-table-planner` 模块）

路径：`OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java`，改 **3 处**：

**(a) `specialOperatorMap` 静态注册**（约第 104 行）：

```java
specialOperatorMap.put("ABS", SpecialExprType.ABS);
```

> key 必须与 Calcite `RexCall.getOperator().getName()` 完全一致（通常大写）。

**(b) `SpecialExprType` 枚举**（约第 199 行）新增枚举值。

**(c) `buildJsonMap` 的 `switch (specialType)` 分支**（约第 673 行起）生成 JSON：

```java
case ABS:
    jsonMap.put("exprType", "FUNCTION");
    setDataType(rexCall, jsonMap, "returnType");
    jsonMap.put("function_name", "abs");
    List<Map<String, Object>> absArgList = new ArrayList<>();
    absArgList.add(buildJsonMap(operands.get(0)));
    jsonMap.put("arguments", absArgList);
    break;
```

要点：
- `function_name` 必须与**向量化注册名严格一致**（步骤 1.2 的注册名，通常小写；个别 CamelCase）。这是 dispatch 唯一键。
- **入参类型匹配**：若步骤 1.3 判定需 CAST，则在此处对 `operands.get(i)` 包一层 CAST 子表达式（参考已有 `CAST` 分支的 JSON 构造），把类型转成向量化已注册的类型，再放入 `arguments`。
- 多参函数依次 `add(buildJsonMap(operands.get(i)))`，顺序须与向量化 `call(...)` 形参顺序一致。
- 复杂入参/字面量改写参考 `CAST`/`DATE_FORMAT`/`COALESCE` 等已有分支。

### 2.3 自检

- 4 处命名一致（算子名 / 枚举 / `function_name`）。
- `function_name` 与向量化注册名核对无误。
- 字典类型 ⊆ 向量化支持类型（或已在 (c) 中加 CAST 兜底）。
- `arguments` 顺序与向量化 `call` 形参顺序一致。

---

## 步骤 3：上传修改文件到服务器

用 `ssh-skill`（禁止直接 ssh/scp）。`<别名>` 来自「获取服务器别名」小节的 `ssh-skill find`/`list-servers` 查询结果；不在此硬编码 IP/端口/密钥。只上传实际改动的文件，命令加 `MSYS_NO_PATHCONV=1` 前缀：

```bash
MSYS_NO_PATHCONV=1 python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_upload.py" <别名> "OmniAdaptor/omnihelper/resources/flink_function_dictionary.json" "<REMOTE_CODE_ROOT>/OmniAdaptor/omnihelper/resources/flink_function_dictionary.json"

MSYS_NO_PATHCONV=1 python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_upload.py" <别名> "OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java" "<REMOTE_CODE_ROOT>/OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java"
```

上传后用一条 `ssh_execute.py` `grep` 校验远端文件已更新。

> 若步骤 1.3 判定需改 OmniOperator 向量化实现（已获用户确认），同时上传对应 `vectorization/functions/*` 与 `registration/Register*.cpp`，并在步骤 4 一并重建 OmniOperator + OmniStream。

---

## 步骤 4：按需重新构建并修复报错

**按需构建**，只重建受影响模块：

| 改动范围 | 需重建 | 脚本 |
|----------|--------|------|
| 仅 `RexNodeUtil.java` + 字典（纯 planner 侧，主场景） | OmniAdaptor（mvn） | `bash <REMOTE_CODE_ROOT>/OmniAdaptor/install_omni_adaptor.sh` |
| 同时改了 OmniStream C++ | + OmniStream cpp | `bash <REMOTE_CODE_ROOT>/OmniAdaptor/install_omni_stream.sh Release` |
| 同时改了 OmniOperator 向量化实现 | + OmniOperator | `bash <REMOTE_CODE_ROOT>/OmniOperatorJIT/build_scripts/build.sh release:java` |

### 重建 OmniAdaptor（默认场景）

远端代码已存在，**不要重新 git clone**，直接增量构建：

```bash
python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_execute.py" <别名> "source /etc/profile && cd <REMOTE_CODE_ROOT>/OmniAdaptor/omnistream/omniop-flink-extension/omni-flink-bundle && mvn clean package -DskipTests -pl omni-table-planner -am" --timeout 1200
```

成功后部署 jar 到依赖目录：

```bash
python "<SKILL_DIR>/references/ssh-skill/scripts/ssh_execute.py" <别名> "cp <REMOTE_CODE_ROOT>/OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/target/omni-table-planner-*.jar <DEPENDENCY_LIB_DIR>/"
```

### 修复报错（循环）

1. 仔细读 maven/编译报错，多数源于步骤 2 的 4 处不一致（枚举漏加、case 拼写、缺分号/import）。
2. 本地用 StrReplace 修改 → 步骤 3 重新上传 → 重新构建，直到 `BUILD SUCCESS`。
3. 构建耗时较长，`--timeout` ≥ 1200s，按需用 `AwaitShell` 监控。

---

## 步骤 5：结果正确性对比（CSV 黄金对比）

核心思想：让 **OmniStream（使能）** 与 **原生 Flink（关闭 OmniStream）** 读取**同一份固定 CSV**、跑**同一条 SQL**，逐行对比输出是否一致。通过修改 `$FLINK_HOME/bin/config.sh` 在两种引擎间切换。

### 5.1 生成测试数据与 SQL（覆盖步骤 1 调研的各场景）

依据步骤 1.1 的 `sql_functions.yml` 语义，设计 CSV 行覆盖：**正常值、边界值（下标越界/长度不足/0/负数）、NULL、各支持类型、大数（超 int 范围）**。

CSV 规则（OmniStream `CsvConverter` 解析）：逗号分隔、无表头、字符串不加引号且不含逗号、`null` 字面量表示 NULL、按列位置映射。

参考 SQL 样例（`filesystem` + `csv` 源，OmniStream 通过 `format=="csv"` offload；`print` sink）：

```sql
SET 'parallelism.default' = '1';          -- 行序稳定，便于 diff
SET 'table.local-time-zone' = 'UTC';      -- 时间类函数可复现

CREATE TABLE src (
  a BIGINT, b BIGINT, c BIGINT, s STRING
) WITH (
  'connector' = 'filesystem',
  'path' = '<REMOTE_CODE_ROOT>/install_script/queries/csv_test/<func>/verify_expr_fixed.csv',
  'format' = 'csv',
  'csv.null-literal' = 'null'             -- 与 OmniStream 的 null 字面量对齐
);

CREATE TABLE sink (
  r1 BIGINT, r2 STRING, r3 INT   -- 按被测函数返回类型声明
) WITH ('connector' = 'print');

INSERT INTO sink
SELECT GREATEST(a, c), FROM_UNIXTIME(b), INSTR(CAST(a AS STRING), CAST(b AS STRING))
FROM src;   -- 替换为被测函数，覆盖各场景
```

把 CSV 与 SQL 上传到服务器 `<REMOTE_CODE_ROOT>/install_script/queries/csv_test/<func>`（用 ssh-skill upload）。

### 5.2 引擎切换（修改 `<FLINK_HOME>/bin/config.sh`）

`config.sh` 的 `constructFlinkClassPath` 决定是否加载 OmniAdaptor jar：
- **使能 OmniStream**：注释原 `echo "$FLINK_CLASSPATH""$FLINK_DIST"`，改为把 `flink-tnel` jar 前置：

```bash
sed -i '/^    echo "$FLINK_CLASSPATH""$FLINK_DIST"/ {
	s|echo "$FLINK_CLASSPATH""$FLINK_DIST"|# echo "$FLINK_CLASSPATH""$FLINK_DIST"|
	a\    PATCH=<DEPENDENCY_LIB_DIR>/flink-tnel-0.1-SNAPSHOT.jar
	a\    echo "$PATCH":"$FLINK_CLASSPATH""$FLINK_DIST"
}' <FLINK_HOME>/bin/config.sh
```

- **切回原生 Flink**：还原 `config.sh`（去掉 PATCH 行、恢复原 echo）。建议先备份再切换：

```bash
# 一次性备份原始版本
cp <FLINK_HOME>/bin/config.sh <FLINK_HOME>/bin/config.sh.bak
# 切回原生 Flink：用原始版本覆盖
cp <FLINK_HOME>/bin/config.sh.bak <FLINK_HOME>/bin/config.sh
```

> 每次切换后都必须重启集群才生效。

### 5.3 跑「原生 Flink」基准

```bash
source /etc/profile
# 确保 config.sh 为原始版本（未使能 OmniStream）
cp <FLINK_HOME>/bin/config.sh.bak <FLINK_HOME>/bin/config.sh
stop-cluster.sh
ps -ef | grep flink   # 残余进程则 kill，保证干净集群
start-cluster.sh
<FLINK_HOME>/bin/sql-client.sh -f <REMOTE_CODE_ROOT>/install_script/queries/csv_test/<func>/verify_expr_csv.sql
# 原生结果在 TaskManager .out
grep -E '^\+I' <FLINK_HOME>/log/flink-root-taskexecutor-*.out > /tmp/flink_vanilla_output.txt
```

### 5.4 跑「OmniStream」对照

> ⚠️ **务必在 `start-cluster.sh` 之前 export 环境变量**：`WRITE_TO_FILE`/`FLINK_PERFORMANCE` 由集群启动时的 TaskManager 进程读取，只有在启动前 export 才会生效并产生 `/tmp/flink_output.txt`。若先 `start-cluster.sh` 再 export，或在已运行的集群上 export，都不会有该输出文件（需先 `stop-cluster.sh` 再重新按顺序执行）。

```bash
source /etc/profile
# 使能 OmniStream（见 5.2 的 sed）
stop-cluster.sh
ps -ef | grep flink   # 残余进程则 kill
# 关键顺序：先 export，再 start-cluster.sh，否则不会生成 /tmp/flink_output.txt
export FLINK_PERFORMANCE=1
export WRITE_TO_FILE=/tmp/flink_output.txt
start-cluster.sh
# 提交后输出在 /tmp/flink_output.txt
<FLINK_HOME>/bin/sql-client.sh -f <REMOTE_CODE_ROOT>/install_script/queries/csv_test/<func>/verify_expr_csv.sql
# 确认走 native
tail -n 50 <FLINK_HOME>/log/flink-root-taskexecutor-0*.out | grep "welcome to native"
# 查看 <FLINK_HOME>/log/flink-root-sql-client-*.log 日志，检查是否有 Calc 算子的 SUITABLE 标志
tail -n 50 <FLINK_HOME>/log/flink-root-sql-client-*.log | grep "SUITABLE"
# OmniStream 结果在 /tmp/flink_output.txt
```

### 5.5 对比两份输出

两边输出格式不同需归一化：原生 `print` 为 `+I[v1, v2, ...]`，OmniStream 为 `+I,v1,v2,...`。归一化后排序 diff：

```bash
norm() { sed -E -e 's/^\+I\[/+I,/' -e 's/\]$//' -e 's/^[+-]I,//' -e 's/, /,/g' "$1" | sort; }
diff <(norm /tmp/flink_output.txt) <(norm /tmp/flink_vanilla_output.txt) && echo "RESULT: IDENTICAL" || echo "RESULT: DIFF FOUND"
```

### 5.6 结果判定

- **完全一致** → 适配正确，进入步骤 6。
- **不一致** → 回到步骤 1 复查：是否 `function_name`/注册名不符（未走 native）、入参类型未匹配（CAST 缺失或类型不被支持）、或语义不一致（需用户确认改 OmniOperator）。修正后回到对应步骤重跑。
- **未打印 `welcome to native`** → 表达式未被 offload，检查字典 `is_support_func`/类型、JSON 协议字段、`function_name`。

---

## 步骤 6：生成总结报告

```markdown
# 向量化表达式适配总结报告

## 1. 调研结论
| 函数 | Flink 语义要点(sql_functions.yml) | 向量化注册名 | 向量化支持类型 | 入参匹配结论 |
|------|-----------------------------------|--------------|----------------|--------------|
| ABS  | 返回绝对值；numeric             | abs          | BYTE/SHORT/INT/LONG/FLOAT/DOUBLE/DECIMAL | 直接适配 |

## 2. 修改文件
- flink_function_dictionary.json：使能 ABS（类型 ...）
- RexNodeUtil.java：specialOperatorMap / SpecialExprType / buildJsonMap case
- （如有）OmniOperator 向量化实现：... （已获用户确认）

## 3. 构建结果
- 重建模块 / BUILD SUCCESS / 失败与修复

## 4. 正确性对比
- 测试 CSV 覆盖场景：正常/边界/NULL/各类型/大数
- 走 native：是（welcome to native）
- OmniStream vs 原生 Flink：IDENTICAL / 差异点与修复

## 5. 遗留问题 / 后续建议
```

---

## 强制规则

- **适配前必须先调研**（步骤 1），核对 `flink/docs/data/sql_functions.yml` 语义/类型与向量化注册类型；跳过调研属违规。
- **OmniOperator 不支持即报告**：入参类型未被向量化注册覆盖、或语义不一致（下标/NULL/边界/时区等）、或需新增/修改 OmniOperator 向量化实现时，**向用户说明不支持原因和差异**，不再继续适配。
- **仅在 OmniAdaptor 侧加 CAST**：仅当目标类型已被向量化注册支持且 CAST 语义安全（不丢精度/不改变结果）时，才可在 OmniAdaptor 侧加 CAST。
- **测试以结果正确性为准**（步骤 5），不能只看是否走 native；必须 OmniStream 与原生 Flink 输出逐行一致。
- 所有 SSH/上传/远端命令通过 `ssh-skill` 的 Python 脚本（`<SKILL_DIR>/references/ssh-skill/scripts/`），禁止直接 `ssh`/`scp`；传输命令加 `MSYS_NO_PATHCONV=1`。
- **不在本 skill 内硬编码任何服务器 IP/端口/用户/密钥**；服务器别名一律先用 `ssh-skill`（`ssh_config_manager_v3.py find`/`list-servers`）查询获取，查不到时先与用户确认再 `create`。
- 远端已存在代码仓时不执行 `git clone`，直接增量构建；只上传/只重建实际改动涉及的文件与模块。
- `function_name` 必须与 OmniOperator 向量化注册名严格一致。
- 远端命令前先 `source /etc/profile`；每次切换 `<FLINK_HOME>/bin/config.sh` 后必须 `stop-cluster.sh`/`start-cluster.sh` 重启。
- 环境相关路径使用占位符（`<REMOTE_CODE_ROOT>`、`<DEPENDENCY_LIB_DIR>`、`<FLINK_HOME>`），禁止在 SKILL.md 中硬编码绝对路径。
