---
name: omniadaptor-vectorized-expression
description: 在 OmniAdaptor 适配 OmniOperator「向量化表达式框架」的 OmniAdaptor 侧适配流程（先调研后适配）。当用户需要在 OmniStream/OmniAdaptor 中新增或使能某个 Flink SQL 表达式/函数走 native 向量化执行时使用。流程要点：本地改 RexNodeUtil/函数字典前先调研（omnihelper 函数字典语义/类型 + OmniOperator 向量化注册类型 + 入参匹配）；本地改完由 VSCode SFTP 自动同步远端；构建委派 omnistream-build-deploy，正确性对比委派 omnistream-expression-test。触发词：向量化表达式适配、vectorization 表达式、向量化函数适配、preferVectorization、RexNodeUtil 向量化、函数字典调研、CSV 黄金对比。
---

# OmniAdaptor 向量化表达式适配

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时替换。

> 📖 **表达式开发权威指南**:全链路架构、Type A/B/C/D 分类、框架原理(Expr/Visitor/JSONParser/FunctionRegistry)、json_value 深度案例、C 函数规范与排错,见 [表达式开发指南.md](../omnistream-expression-dev-test/references/表达式开发指南.md)。本 skill 聚焦 OmniAdaptor 侧适配(调研 + 改 RexNodeUtil/函数字典),权威指南为总纲。

在 OmniAdaptor（Flink Calcite 侧）把一个 Flink SQL 函数翻译成 OmniStream 能识别的 JSON 表达式协议，使其走 OmniOperator **向量化表达式框架**（`StreamCalcBatch.cpp` 已设 `preferVectorization=true`）执行。

> 本 skill 只做 **OmniAdaptor 侧适配**（调研 + 改 `RexNodeUtil`/字典）。两条核心原则：
> 1. **先调研后适配**：动 `RexNodeUtil.java` 前，必须核对函数字典语义/类型与 OmniOperator 向量化注册类型，并检查入参类型匹配。跳过调研会导致类型不支持、语义不一致。
> 2. **结果正确性对比**（委派 `omnistream-expression-test`）：不能只看是否走 native；必须 native 与原生 Flink 逐行一致。

## 本地开发模式（SFTP 自动同步）

三仓库均在本地工作目录（`OmniStream`/`OmniAdaptor`/`OmniOperator`），VSCode SFTP 插件保存即自动同步到远端代码根(见 AGENTS.md §5 `OMNI_CODE_ROOT`)。故：
- **调研**：读本地源码（无需远端）。
- **适配**：改本地文件，保存即同步，无需手动上传。
- **构建/对比**：委派 `omnistream-build-deploy` / `omnistream-expression-test`（远端直接 ssh）。

| 本地路径（调研/适配对象） | 说明 |
|---|---|
| `../OmniAdaptor/omnihelper/resources/flink_function_dictionary.json` 等 | Flink 函数字典（语义/类型/支持） |
| `../OmniAdaptor/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java` | JSON 协议生成（适配主改动） |
| `../OmniOperator/core/src/vectorization/registration/Register*.cpp` | 向量化函数注册（注册名/类型） |
| `../OmniOperator/core/src/vectorization/functions/<Name>.{h,cpp}` | 向量化函数实现（call 语义） |

## skill 边界（不做什么）

| 不做 | 委派给 |
|------|--------|
| 三仓库编译 / 部署到 Flink / native 使能 | `omnistream-build-deploy`（步骤 4） |
| 表达式 native vs vanilla 黄金对比 / 报告 | `omnistream-expression-test`（步骤 5） |
| OmniOperator 向量化函数实现（.h/.cpp/Register） | `omnioperator-expression-dev`（步骤 1 判定需改实现时，报告用户后转交） |
| 表达式生态支持现状扫描 | `flink-native-expression-analysis` |
| 全周期编排 | `omnistream-expression-dev-test` |

> 本 skill 与 `omnistream-expression-dev-test` 的区别：本 skill 只做适配（函数已实现或将由 `omnioperator-expression-dev` 实现）；dev-test 是编排层，串联实现+适配+编译+测试全周期。

## 工作流程总览

```
向量化适配进度:
- [ ] 步骤 1: 调研（本地函数字典 语义/类型 + OmniOperator 向量化注册类型 + 入参匹配）
- [ ] 步骤 2: 表达式适配（本地改 3 处 RexNodeUtil + 1 处字典，注意类型匹配）
- [ ] 步骤 3: SFTP 自动同步（保存即同步，无需手动上传）
- [ ] 步骤 4: 重新构建（委派 omnistream-build-deploy：adaptor_build / omnistream_incr / operator_build + deploy）
- [ ] 步骤 5: 结果正确性对比（委派 omnistream-expression-test：native vs vanilla 黄金对比）
- [ ] 步骤 6: 生成总结报告
```

---

## 步骤 1：调研（适配前必做，不可跳过）

目的：动 `RexNodeUtil.java` 前，先确认「Flink 侧语义/类型」与「OmniOperator 向量化侧实现/注册类型」是否一致、入参类型是否被支持。

### 1.1 调研 Flink 侧语义与支持类型 —— `omnihelper/resources/` 函数字典

按函数名（如 `INSTR`、`FROM_UNIXTIME`、`GREATEST`）检索本地 `../OmniAdaptor/omnihelper/resources/` 下函数字典（`flink_function_dictionary.json` 记函数与支持类型、`flink_function_return_type.json` 记返回类型、`flink_op_dictionary.json` 记算子映射），确认：
- **签名与语义**：参数个数、参数类型、返回类型、NULL 行为、边界行为（下标从 1 还是 0、越界如何处理、负数行为）。
- **类型覆盖**：该函数在 Flink 中允许哪些入参类型（`numeric` 泛指 TINYINT/SMALLINT/INT/BIGINT/FLOAT/DOUBLE/DECIMAL；`string` 指 CHAR/VARCHAR）。

> 注：无 `sql_functions.yml`（属 Flink 上游，未打包进 omnihelper）；以 omnihelper 函数字典为 Flink 侧语义基准。记录「Flink 期望语义」，作为后续正确性对比的预期基准。

### 1.2 调研 OmniOperator 向量化实现与注册类型

向量化框架是 Velox 风格的 SimpleFunction 注册：每个函数通过 `RegisterFunction<T, Ret, Arg...>(name, {OMNI_ARG_TYPES...}, OMNI_RET_TYPE)` 显式声明**入参 OMNI 类型**与**返回 OMNI 类型**。

操作：
1. 在本地 `../OmniOperator/core/src/vectorization/registration/Register*.cpp` 中按 `name` 字符串检索目标函数注册（如 `"from_unixtime"`、`"instr"`）。确认：
   - **注册名**（dispatch 唯一键，通常小写；个别 CamelCase 对齐 Gluten，如 `DateFormat`）。
   - **每个重载注册的入参 OMNI 类型集合**（如 `{OMNI_LONG}`、`{OMNI_VARCHAR, OMNI_VARCHAR}`）。批量注册见 `RegistrationHelpers.h`（如 `RegisterUnaryNumeric` 覆盖 BYTE/SHORT/INT/LONG/FLOAT/DOUBLE/DECIMAL）。
2. 在 `../OmniOperator/core/src/vectorization/functions/<Name>.{h,cpp}` 阅读实现（`call(...)`/`callNullable(...)`），确认**语义是否与 1.1 的 Flink 语义一致**（下标基准、NULL 处理、舍入、时区等）。

### 1.3 类型匹配判定（核心）

把「`RexNodeUtil` 将要传入的入参类型」与「1.2 中向量化注册支持的 OMNI 类型集合」逐一比对：

| 情况 | 处置 |
|------|------|
| 入参类型已被注册覆盖，语义一致 | 直接适配（步骤 2） |
| 入参类型未被覆盖，但**仅需在 OmniAdaptor 侧加 CAST** 转成已支持类型，且不改变语义 | 在 `RexNodeUtil` 生成 CAST 子表达式，继续步骤 2 |
| 入参类型未被覆盖，需在 OmniOperator 侧注册新的参数类型 | **向用户报告**，OmniOperator 不支持该类型，流程结束 |
| 语义不一致（下标/NULL/边界/时区等），或需**新增/修改 OmniOperator 向量化实现**、新增类型重载、改注册等重大改动 | **向用户报告**，OmniOperator 不支持该函数语义，流程结束 |

> 在 OmniAdaptor 侧加 CAST 的判据：目标类型已被向量化注册支持、且 CAST 本身语义安全（不丢精度/不改变结果）。否则归类为「OmniOperator 不支持」，向用户报告后流程结束。

### 1.4 调研结论（写入最终报告）

输出简表：函数名、Flink 语义要点、向量化注册名与支持类型、入参类型匹配结论（直接/加 CAST/OmniOperator 不支持）。

---

## 步骤 2：表达式适配

> 仅在步骤 1 判定为「直接适配」或「OmniAdaptor 加 CAST」时进行；若 OmniOperator 不支持，流程已在步骤 1 结束。

以 `abs` 为模板，改 **2 个文件、共 4 处**。

### 2.1 函数字典 `../OmniAdaptor/omnihelper/resources/flink_function_dictionary.json`

把目标函数标记为支持，`is_supported_type` **只写步骤 1.3 确认向量化真正支持（或可经 CAST 安全转换）的类型**（下例以 `ABS` 为模板；源码中 ABS 尚未适配，`is_support_func` 当前为 `false`）：

```json
{"func_name": "ABS", "is_support_func": true, "is_supported_type": ["BIGINT", "INTEGER", "DOUBLE"]}
```

### 2.2 `RexNodeUtil.java`（本地路径见上方表格）

改 **3 处**：

**(a) `specialOperatorMap` 静态注册**（约第 81 行）：
```java
specialOperatorMap.put("ABS", SpecialExprType.ABS);
```
> key 必须与 Calcite `RexCall.getOperator().getName()` 完全一致（通常大写）。

**(b) `SpecialExprType` 枚举**（约第 178 行）新增枚举值。

**(c) `buildJsonMap` 的 `switch (specialType)` 分支**（`buildJsonMap` 约第 252 行 / `switch` 约第 286 行起）生成 JSON：
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
- `function_name` 必须与**向量化注册名严格一致**（步骤 1.2 注册名，通常小写；个别 CamelCase）。这是 dispatch 唯一键。
- **入参类型匹配**：若步骤 1.3 判定需 CAST，则在此处对 `operands.get(i)` 包一层 CAST 子表达式（参考已有 `CAST` 分支），把类型转成向量化已注册的类型，再放入 `arguments`。
- 多参函数依次 `add(buildJsonMap(operands.get(i)))`，顺序须与向量化 `call(...)` 形参顺序一致。

### 2.3 自检

- 4 处命名一致（算子名 / 枚举 / `function_name`）。
- `function_name` 与向量化注册名核对无误。
- 字典类型 ⊆ 向量化支持类型（或已在 (c) 中加 CAST 兜底）。
- `arguments` 顺序与向量化 `call` 形参顺序一致。

### 2.4 常见踩坑

- **OmniAdaptor 不能直接 import Guava 类**：`omni-table-planner` 依赖的 Flink table-planner 对 Guava 做了 relocate/shade，`import com.google.common.collect.Range;` 会报 `package com.google.common.collect does not exist`。处理 Sarg 的 `rangeSet.asRanges()` 时用 `forEach(r -> ...)` 让类型推断（不显式命名 `Range`），或用 `Object[]` 收集边界。**改 RexNodeUtil 前先确认要用的类是否被 Flink shaded**（Guava/Netty/Avro 等常被 relocate）。
- **加 `#include` 前先查依赖是否已引入**：OmniOperator 侧新增函数 include 的头（`util/compiler_util.h`、`util/omni_exception.h`、`vectorization/VectorFunction.h`、`Comparisons.h`、`registration/SimpleFunctionRegistry.h` 等）必须是仓库已有文件，不引入新外部依赖；参考同目录已有函数（如 `In.cpp`/`ConcatFunction.h`）的 include 列表对齐。
- **SEARCH/Sarg 多段形态**：`RexNodeUtil case SEARCH` 要处理多种 Sarg 形态——`isPoints`→正向 IN；`isComplementedPoints`（补集点集，如 `c NOT IN (1,2,3)`→`Sarg[(-∞..1),(1..2),(2..3),(3..+∞)]`）→`UNARY(NOT, IN(原点集))`，原点集从 `rangeSet.complement().asRanges()` 的 `lowerEndpoint()` 提取（complement 全是 singleton，不崩）；空 Sarg(SYMMETRIC 不可达区间)→常量 FALSE；单段闭区间→BETWEEN；两段补集 `(-∞..low)∪(high..+∞)`(NOT BETWEEN)→`UNARY(NOT, BETWEEN(low,high))`；单段 `(-∞..+∞)`→常量 TRUE；半界/其他多段→暂不表示(INVALID)。用 `rangeSet.asRanges()` 的 `hasLowerBound/hasUpperBound/lowerEndpoint/upperEndpoint` 判别，别只取 `iterator().next()`（会漏 NOT BETWEEN 的第二段、SYMMETRIC 空 Sarg 会抛异常；补集 Sarg 无界区间 `lowerEndpoint()` 抛 `range unbounded on this side`）。⚠️ between-native + not-in-native 合覆盖主要形态但**均未合入 upstream <branch> 主线**，原版 SEARCH case 对补集/无界 Sarg 直接崩。
- **SEARCH 字面量点/端点必须经 `extractSargEndpoint`**：NlsString→string、TimestampString→millis（`import org.apache.calcite.util.TimestampString`）、Number/Boolean/String→原值。不统一则 TIMESTAMP 崩 `json.exception.type_error.302 type must be number, but is object`（原版 isPoints 只处理 NlsString，TimestampString 放对象→OmniTask init 崩）。isPoints（正向 IN）与 isComplementedPoints（NOT IN）两分支都要用。between gap① + not-in isPoints 重复踩第二次。
- **SEARCH/Sarg 形态源码推演不可靠，必 e2e 实证**：Flink vendor Calcite + SqlToRel/ReduceExpressions 多阶段变换 + unknownAs 上下文，源码推演 RexNode 形态常被打脸（NOT IN 推演 `NOT(SEARCH(points))` 实为补集 Sarg；NULL 列表推演 `sarg.containsNull` 丢失实为 `OR(SEARCH, null)` 自动正确）。改前单独跑 native 抓 sql-client `Current rexNode` 日志看实际 Sarg 形态。含 NULL 列表的 IN/NOT IN 走 `OR(SEARCH, null literal)` 路径（非 Sarg），三值自动正确，无需 containsNull 处理。

### 2.5 OmniAdaptor Java UT（非平凡翻译时写，可本地跑）

> 并非每次适配都要写。仅当 `RexNodeUtil` 翻译逻辑**非平凡**时写 Java UT；平凡翻译靠步骤 5 e2e 覆盖接线。

**何时写（满足任一即写）：**
- 新增 `exprType` 分支(如 `UNARY`/`IFNULL`/`COALESCE`/`SWITCH`),需验证 RexCall→JSON 结构。
- 翻译有**递归/嵌套构建**(如 `case COALESCE` 把 N 参展平成嵌套 COALESCE 节点)。
- **别名映射**须产出特定 JSON 形态(如 `IFNULL→COALESCE` 应产出 `exprType:COALESCE`,而非 IFNULL)。
- **特殊参数扩展**(如 `json_value` 2 参→6 参、ON EMPTY/ERROR 行为字段)。
- 步骤 1.3 判定需**加 CAST 子表达式**或类型矩阵有分叉决策。
- 新增 `unaryOperatorMap`/`specialOperatorMap` 映射 + 枚举:至少 1 用例断言映射存在 + 1 用例断言 `buildJsonMap` 产出。

**何时不用写:** 翻译是邻近 FUNCTION case 的平凡复制(仅 `function_name`/参数个数不同、无逻辑分叉)——步骤 5 e2e 覆盖接线(反例:LEFT/RIGHT 复制 LOWER,未写 Java UT)。

**怎么写（模式）:**
- **位置**:镜像主类路径,放 `omni-table-planner/src/test/java/.../RexNodeUtilXxxTest.java`。
- **框架**:JUnit 4(`org.junit.Test` + `static org.junit.Assert.*`)。
- **构造输入**:用 Calcite `RexBuilder` + `SqlTypeFactoryImpl(RelDataTypeSystem.DEFAULT)` 构造**真实 `RexCall`**(field ref / literal / 嵌套),**不 mock**。
- **直驱被测方法**:直接调 `RexNodeUtil.buildJsonMap(rexCall)`,隔离 Flink planner/集群。
- **断言 JSON `Map<String,Object>`**:`exprType`、`function_name`/`operator`、`returnType`(DataTypeId 整数)、嵌套 `expr`/`arguments` 的 `exprType`/`dataType`/`value`/`isNull`。
- **本地跑**:`cd omni-table-planner && mvn test -Dtest=RexNodeUtilXxxTest`(Java,**无需鲲鹏,Windows 本地即可**)——Java UT 相对 C++ UT 的优势:本地秒级反馈,不必等远端 e2e。

**标杆示例:** `RexNodeUtilNotTest.java`(commit `d920300c`,!254 NOT 运算)——4 用例:映射注册断言、field-ref 输入、true/false/null 字面量输入,逐个断言 UNARY JSON 结构。

**原则:** 每个仓库的 UT 只测本仓库的非平凡逻辑——OmniAdaptor Java UT 测 RexCall→JSON 翻译(是 OmniOperator `VectorFunction::Apply` 直驱 UT 的对偶);C++ 语义由 `omnioperator-expression-dev` UT 测;端到端接线 + native==vanilla 仍由步骤 5 e2e 覆盖。三者互补,Java UT 不替代 e2e。跨仓库场景矩阵见权威指南 §10.3。

---

## 步骤 3：SFTP 自动同步

本地改完保存，VSCode SFTP 插件自动同步到远端代码根(见 AGENTS.md §5)对应路径。**无需手动上传**。

> 确认 SFTP 已配置同步 `OmniAdaptor`/`OmniOperator`（及 `OmniStream`，若改了 C++）。若个别文件未自动同步，手动 scp 单文件兜底。

---

## 步骤 4：重新构建（委派 `omnistream-build-deploy`）

构建命令不在本 skill 内重复，按改动范围调用 [`omnistream-build-deploy`](../omnistream-build-deploy/SKILL.md) 的预定义任务：

| 改动范围 | 任务（omnistream-build-deploy） | 说明 |
|----------|-------------------------------|------|
| 仅 `RexNodeUtil.java` + 字典（主场景） | `adaptor_build` | 仅改 planner 可加 `-pl omni-table-planner -am` 加速 |
| 同时改 OmniStream C++ | `omnistream_incr` | 只编 libtnel.so,不编 test 不 install |
| 同时改 OmniOperator 向量化实现（已获用户确认） | `operator_build` | 全量(`--clean-first`) |

> 命令实现见 `omnistream-build-deploy/scripts/config.ini` `task_<name>`(不在此重复,避免漂移)。

构建后部署 jar/so 到部署目录(`<deploy_dir>/`,见 AGENTS.md §5)并重启集群(`deploy` / `conf_parent_first` / `cluster_stop` / `cluster_start` 任务,均见 `omnistream-build-deploy`)。

### 修复报错（循环）

1. 多数报错源于步骤 2 的 4 处不一致（枚举漏加、case 拼写、缺分号/import）。
2. 本地修改 → 保存（SFTP 同步）→ 重新构建（`omnistream-build-deploy`），直到 `BUILD SUCCESS`。

---

## 步骤 5：结果正确性对比（委派 `omnistream-expression-test`）

对比方法论不在本 skill 内重复，用 [`omnistream-expression-test`](../omnistream-expression-test/SKILL.md) 跑 **native（OmniStream）vs vanilla（Flink 原生）** 黄金对比：

1. 按步骤 1 调研的语义场景生成 csv+sql（正常/边界/NULL/越界/各类型/大数）——模板见 `omnistream-expression-test/templates/`；远端现成资产(见 AGENTS.md §5 `INSTALL_SCRIPT_DIR`)下 `verify_expr_fixed.csv` / `verify_expr_csv_selfcontained.sql` 可复用。
2. 本地驱动 `bash run_local.sh <函数名>`（自动 scp 上传用例+脚本 → ssh 跑 native+vanilla+compare → 取回结果；vanilla 切 `config.sh` 去 flink-tnel.jar + `config.sh.bak` 恢复在服务端 `run_test.sh` 内完成）→ `compare.sh` 归一化 diff → 报告本地 `flink-test/report/<函数名>/`。
3. 通过判据：native == vanilla 逐行一致 **且** `welcome to native` 计数 > 0。

> 步骤 1.4 的调研结论（Flink 期望语义）作为对比的预期基准。不一致时回步骤 1 复查 `function_name`/注册名、入参类型匹配、语义一致性；未打印 `welcome to native` 则查字典 `is_support_func`/类型、JSON 协议字段。
>
> ⚠️ `WRITE_TO_FILE`/`FLINK_PERFORMANCE` 必须在 `start-cluster.sh` **之前** export（由 TM 进程读取）；native 使能本身由 `omnistream-build-deploy` 保证。

---

## 步骤 6：生成总结报告

```markdown
# 向量化表达式适配总结报告

## 1. 调研结论
| 函数 | Flink 语义要点 | 向量化注册名 | 向量化支持类型 | 入参匹配结论 |
|------|----------------|--------------|----------------|--------------|
| ABS  | 返回绝对值；numeric | abs | BYTE/SHORT/INT/LONG/FLOAT/DOUBLE/DECIMAL | 直接适配 |

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

- **适配前必须先调研**（步骤 1），核对函数字典语义/类型与向量化注册类型；跳过调研属违规。
- **OmniOperator 不支持即报告**：入参类型未被向量化注册覆盖、或语义不一致、或需新增/修改 OmniOperator 向量化实现时，向用户说明不支持原因和差异，不再继续适配。
- **仅在 OmniAdaptor 侧加 CAST**：仅当目标类型已被向量化注册支持且 CAST 语义安全时才可。
- **测试以结果正确性为准**（步骤 5 委派 `omnistream-expression-test`），不能只看是否走 native；必须 native 与原生 Flink 输出逐行一致。
- **本地编辑 + SFTP 自动同步**：三仓库在本地工作目录，改完保存即同步远端，不在远端 `git clone`；只改实际涉及的文件。
- `function_name` 必须与 OmniOperator 向量化注册名严格一致。
- 步骤 4-5 委派的 skill（`omnistream-build-deploy`/`omnistream-expression-test`）远端命令前 `source /etc/profile`；`config.sh` 引擎切换与集群重启见 `omnistream-expression-test`（步骤 5）。

---

## 核心踩坑(提炼自记忆)

- **字典字符串函数 `is_supported_type` 须同时列 STRING+VARCHAR**:类型解析链把字符串参数归一为 VARCHAR(非 STRING),漏列 VARCHAR 会使 omnihelper 离线报表误判 unsupported(运行时不读字典,仅报表失真)。
- **三端类型 ID 系统性错位**:Java `RexTypeToIdMap` 与 C++ `DataTypeId` 在复合类型(ROW/ARRAY/MAP/MULTISET)及部分 TIMESTAMP 变体数值错位,Java 白名单放行 ≠ C++ 精确签名匹配能执行,复合类型静默回退优先怀疑此错位。
- **comparison/Sarg 族(IN/NOT IN/BETWEEN/NOT BETWEEN)常 OmniAdaptor-only**:底层 `InExpr`/`BetweenExpr`/`UnaryExpr(NOT)` 三值已正确,缺口全在 `RexNodeUtil` SEARCH case Sarg 翻译;适配前先查 OmniOperator 是否已有 Expr 类+向量化函数,有则勿多仓库铺开。
- **Type D 复用既有函数须两预检**:① 先查 adaptor `normalizeCharLiteralToVarchar` 是否已归一 CHAR 字面量→VARCHAR(常可免 OmniOperator 补 CHAR 注册,勿照搬 Type B 先例);② 源注释标 Spark 语义函数须预判 Spark-vs-Flink 分歧(escape/码点/大小写/NULL)。
- **LIKE 族 `\` escape 是引擎级分歧非适配 bug**:`LikeFunction` 2-arg 默认 `\` escape(Spark)vs Flink 无默认 escape,含 `\` 模式 native≠vanilla;e2e 黄金数据勿含 `\` 转义模式,审计勿误判为适配引入。
