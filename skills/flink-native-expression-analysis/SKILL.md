---
name: flink-native-expression-analysis
description: 扫描 Flink SQL 表达式在 OmniStream native 的三层支持现状(OmniOperator native 注册 / OmniAdaptor Java 决策 / 离线字典),产出三层一致性 + 缺口报告。触发:Flink 表达式 native 支持分析、表达式缺口排查、声明支持但 not supported(如 char_length)、三层一致性、native 表达式覆盖度、表达式生态现状。
---

# Flink SQL 表达式 native 支持分析

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时替换。

> 📖 **表达式开发权威指南**:全链路架构、Type A/B/C/D 分类、框架原理(Expr/Visitor/JSONParser/FunctionRegistry)、json_value 深度案例、C 函数规范与排错,见 [表达式开发指南.md](../omnistream-expression-dev-test/references/表达式开发指南.md)。本 skill 聚焦三层支持现状扫描与缺口报告,权威指南为总纲。

## Objective

扫描 Flink SQL 表达式在 OmniStream native 路径的**三层**支持现状,产出 `OmniOperator/docs/expression-analysis/expression_analysis_report_<yyyymmdd>.md`,回答:
1. OmniOperator native 实际注册了哪些表达式(Layer A,各支持哪些类型)?
2. OmniAdaptor Java 运行时放行哪些表达式(Layer B,硬编码 Map + 白名单)?
3. OmniAdaptor 离线字典声称支持哪些表达式(Layer C,`is_support_func`)?
4. 三层一致性如何?哪些"声称支持但 native 未实现"(如 `CHAR_LENGTH`)?优先级?

> **关键认知**:运行时支持集 = Layer A(native 注册)∩ Layer B(Java 放行);Layer C(离线字典)与运行时**无耦合**,只是 omnihelper Python 离线工具的声称清单,可能与运行时不一致 —— 缺口分析的重点就是这种不一致。

## Expression Data Flow(Flink → native)

```
Flink SQL RexNode
  │  CommonExecCalc 调 RexNodeUtil.buildJsonMap()
  ▼
RexNodeUtil.java            ← 硬编码 4 Map(special/binary/unary/udfOperatorMap),不认识标 INVALID
  ▼
OmniGraphOverride.java      ← SUPPORT_OP_NAME 白名单 + 检测 INVALID → 回退
  │  + ValidateCalcOPStrategy(SUPPORT_BINARYOP/UNARYOP_NAME 二级白名单)
  ▼  setUseOmniEnabled(true/false)
StreamCalcBatch.{h,cpp}     ← JSONParser.ParseJSON → ExpressionEvaluator(preferVectorization=true 硬编码)→ codegen + Evaluate
  ▼
OmniOperator native(Layer A)
  ├── vectorization/registration/   ← ExprEval + VectorFunction dispatch(SIMD)
  ├── codegen/func_registry_*.cpp   ← LLVM JIT(独立注册)
  └── operator/aggregation/aggregator/  ← 聚合 dispatch

旁路(与运行时无耦合):omnihelper 字典(Layer C)仅 Python 离线分析用
```

> 完整源码路径见 [`references/source_paths.md`](references/source_paths.md)。

## Key Methodology

**不用文件数估覆盖度。** 一个 `Register*.cpp` 可注册几十个函数名(每个多类型重载),一个 `.h` 只对应一个函数。唯一可靠数据源是 `registration/` 目录的 `RegisterFunction` 调用。

**类型覆盖 = RegistrationHelpers.h 的 helper 调用。** 是否调用 `RegisterUnaryDecimal` 等 helper 决定 DECIMAL 是否支持(追完整调用链)。helper → 类型映射见 [`references/source_paths.md`](references/source_paths.md)。

**用全局 grep 确认注册:**
```bash
grep -r '"func_name"' <OmniOperator>/core/src/vectorization/registration/
```
无匹配 = 确认未注册。

**三层独立扫描,再交叉。** Layer A/B/C 是三个独立数据源,分别扫描后做一致性缺口分析。

---

## Step 1: 建输出目录

```bash
mkdir -p <OmniOperator>/docs/expression-analysis
REPORT=<OmniOperator>/docs/expression-analysis/expression_analysis_report_$(date +%Y%m%d).md
```

---

## Step 2: Layer A — OmniOperator native 注册层(主要真相源)

OmniOperator 有两套表达式执行框架 + 聚合,都扫。源码路径见 [`references/source_paths.md`](references/source_paths.md) §Layer A。

### 2a. 向量化框架(SIMD,ExprEval dispatch)
主源:`<OmniOperator>/core/src/vectorization/registration/Register*.cpp`(17 个文件,含 Register.cpp 主入口,16 个类别)。逐个提取 `RegisterFunction<...>(prefix + "func_name", ...)` 与 `RegisterVectorFunction("func_name", ...)`。
确认某函数是否注册:
```bash
grep -r '"func_name"' <OmniOperator>/core/src/vectorization/registration/
```
检查 ExprEval dispatch 完整性:读 `<OmniOperator>/core/src/vectorization/ExprEval.cpp`,找 `FuncExpr` dispatch 块(抓"已注册但 ExprEval 无 dispatch"的断链)。

### 2b. Codegen 框架(LLVM JIT)
源:`<OmniOperator>/core/src/codegen/func_registry_*.cpp`(11 个)。codegen 有独立于 vectorization 的注册。标注:仅 codegen / 仅 vectorization / 两者都有。

### 2c. 聚合表达式
读 `<OmniOperator>/core/src/operator/aggregation/aggregator/aggregator_factory.cpp`,提取聚合类型变体(独立 dispatch 路径)。

---

## Step 3: Layer B — OmniAdaptor Java 决策层(运行时放行集)

运行时实际放行哪些表达式 = Java 硬编码 Map + 白名单。源码路径见 [`references/source_paths.md`](references/source_paths.md) §Layer B。

### 3a. RexNodeUtil 硬编码 Map
读 `<OmniAdaptor>/.../RexNodeUtil.java` 的 `buildJsonMap()`,提取 4 个 Map 的 key 集:`specialOperatorMap`(CASE/CAST/JSON_VALUE/DATE_FORMAT/CHAR_LENGTH/LOWER/HASH_CODE/EXTRACT/COALESCE/AND/OR/IF/DATE_ADD/CURRENT_TIMESTAMP/JSON_QUERY/JSON_SPLIT/SEARCH/PROCTIME/...)、`binaryOperatorMap`、`unaryOperatorMap`、`udfOperatorMap`。不在 Map 的算子走 `default` 标 `exprType=INVALID`。
```bash
grep -nE 'specialOperatorMap|binaryOperatorMap|unaryOperatorMap|udfOperatorMap' <OmniAdaptor>/.../RexNodeUtil.java
```

### 3b. OmniGraphOverride INVALID 回退
读 `<OmniAdaptor>/.../OmniGraphOverride.java` 的 `validateOperatorByNameForOmniTask()`(line 712):`SUPPORT_OP_NAME` 白名单 + `operatorDescription.contains("INVALID")` → 回退(733-736)。

### 3c. ValidateCalcOPStrategy 二级白名单
读 `<OmniAdaptor>/.../ValidateCalcOPStrategy.java`:提取 `SUPPORT_BINARYOP_NAME`(OR/AND/ADD/SUBTRACT/MULTIPLY/DIVIDE/MODULUS/六比较/DATE_FORMAT/count_char)、`SUPPORT_UNARYOP_NAME`(CAST/NEGATION/NOT),及 `json_split`/`json_query`/`current_timestamp`/`date_add_days`/`to_timestamp_ltz` 签名校验。

> Layer B 放行集 = RexNodeUtil 4 Map 能翻译(非 INVALID) ∧ ValidateCalcOPStrategy 白名单通过。

---

## Step 4: Layer C — OmniAdaptor 离线字典层(声称支持,与运行时无耦合)

omnihelper Python 离线工具的声称清单。源码路径见 [`references/source_paths.md`](references/source_paths.md) §Layer C。

### 4a. flink 字典
`<OmniAdaptor>/omnihelper/resources/flink_function_dictionary.json`:231 项,`is_support_func=true` 40 项。提取 supported 函数名 + `is_supported_type` 类型列表。
```bash
py -c "import json;d=json.load(open(r'<OmniAdaptor>/omnihelper/resources/flink_function_dictionary.json',encoding='utf-8'));print([x['func_name'] for x in d if x.get('is_support_func')])"
```

### 4b. omni 字典
`<OmniAdaptor>/omnihelper/resources/omni_function_dictionary.json`:464 项,`is_support_func=true` 105 项。

### 4c. 消费链(可选,理解字典用途)
`omnihelper/flink/function/{dictionary_loader,support_checker,function_parse,pattern_matcher}.py` + `omnihelper/parser/function/function_checker.py`。全是 Python 离线静态分析,**Java 运行时不读**。

> ⚠️ Layer C 是"声称清单",用于离线报表/校验,与运行时放行集(Layer B)可能不一致。缺口分析的重点就是这种不一致。

---

## Step 5: 三层一致性 + 缺口分析

### 5.1 三层对比矩阵
| 表达式 | Layer A native 注册 | Layer B Java 放行 | Layer C 字典声称 | 状态 |
|---|:---:|:---:|:---:|---|

### 5.2 类型覆盖矩阵(Layer A)
| 表达式 | INT | LONG | FLOAT | DOUBLE | DECIMAL | STRING | TIMESTAMP | ARRAY | MAP |
|---|---|---|---|---|---|---|---|---|---|

### 5.3 缺口优先级
- 🔴 **高优先(影响正确性)**:Layer C 字典 `is_support_func=true` 但 Layer A native 未注册 / 注册名不匹配 / Layer B 不放行 —— 声称支持实际 not supported(如 `CHAR_LENGTH`:实现 `CharLengthFunction` 存在但注册名 `length` ≠ SQL 名,见 memory `native-test-char-length-unsupported`)。字典误导,应修字典/改注册名/补实现。
- 🟡 **中优先**:Layer B 放行但 Layer A native 未注册 —— 决策放行却 native 崩/回退。
- 🟢 **低优先**:Layer A 注册但 Layer B 不放行 —— native 死代码(Java 不触发)。
- 兜底:`StreamCalcBatch.collectUnsupportedExprImpl`(line 246)对 `regex_extract_null`/`PROCTIME→TIMESTAMP_LTZ`/`int64*decimal64→decimal128` 临时改写 FIELD_REFERENCE。

---

## Step 6: 生成报告

写到 `$REPORT`,用用户沟通语言。结构:
```markdown
# Flink SQL 表达式 native 支持分析报告
Generated: <date>
Scan: <OmniStream/OmniAdaptor/OmniOperator 分支 + commit>

## 1. 执行摘要
| 指标 | 数量 | 数据源 |
|---|---|---|
| Layer A native 注册(unique) | XXX | vectorization registration + codegen func_registry |
| Layer A 向量化签名(含类型重载) | XXX | 同上 |
| Layer A 聚合类型变体 | XXX | aggregator_factory.cpp |
| Layer B Java 放行集 | XXX | RexNodeUtil 4 Map + ValidateCalcOPStrategy 白名单 |
| Layer C flink 字典声称支持 | 40 | flink_function_dictionary.json |
| Layer C omni 字典声称支持 | 105 | omni_function_dictionary.json |
| 🔴 声称支持但 native 未实现 | XXX | 三层交叉 |

关键结论(3-5 条,突出 CHAR_LENGTH 类缺口)

## 2. 扫描方法论(三层独立 + 交叉)

## 3. 三层对比矩阵
### 3.1 Layer A native 注册(按类)
### 3.2 三层对比表(关键差异表达式)

## 4. 缺口分析
### 4.1 🔴 高优先(声称支持但 native 未实现)
### 4.2 🟡 中优先(放行但 native 未注册)
### 4.3 🟢 低优先(native 死代码)

## 5. 类型覆盖矩阵
### 5.1 标量(vectorization)
### 5.2 聚合(aggregator_factory)

## 6. 优先级建议
### 6.1 修字典/补实现(高价值)
### 6.2 覆盖扩展
```

---

## Step 7(可选):Velox/Gluten 业界基准对比

本地已拉取 `<workspace-root>/velox` + `<workspace-root>/Gluten`(shallow main;`<workspace-root>`=`<local_work>` 本地工作区根,见 omnistream-env-init skill)。作 Flink 三层之外的业界基准附录(非 Flink 主线,Spark 生态,仅参考)。

### 7a. Velox sparksql 函数
`<workspace-root>/velox/velox/functions/sparksql/registration/Register*.cpp`(14 个)。提取双引号函数名字面量(`registerStatefulVectorFunction`/`registerFunction` 等,~237 unique)。**Velox 含 `char_length`(`String.h`)** —— 对比 OmniOperator 注册名不匹配(`CharLengthFunction` 注册为 `length`,覆盖扩展参考)。
```bash
grep -rhoE '"[a-z_][a-z_0-9]*"' <workspace-root>/velox/velox/functions/sparksql/registration/*.cpp | tr -d '"' | sort -u
```

### 7b. Gluten 表达式映射
`<workspace-root>/Gluten/gluten-substrait/src/main/scala/org/apache/gluten/expression/ExpressionMappings.scala`:303 Sig(`SCALAR_SIGS`/`AGGREGATE_SIGS`/`WINDOW_SIGS`),Spark→Substrait 下推意图全集。
```bash
grep -cE 'Sig\[' <workspace-root>/Gluten/gluten-substrait/src/main/scala/org/apache/gluten/expression/ExpressionMappings.scala   # 303
```

> 对比:OmniOperator(192)vs Velox(237)vs Gluten(303)。Velox 有而 Omni 无的(如 `char_length`)= 潜在覆盖扩展。注意 Gluten/Velox 是 Spark 生态,与本项目 Flink 路径不同,仅作业界基准。

---

## Caveats

1. **文件存在 ≠ 完全支持**:`vectorization/functions/Foo.h` 存在不代表 `ExprEval.cpp` dispatch 已接 / Java 侧已放行。
2. **字典声称 ≠ 运行时支持**:Layer C `is_support_func=true` 只是离线工具清单,Java 运行时不读;运行时放行靠 Layer B 硬编码 Map,native 执行靠 Layer A 注册。
3. **两层框架覆盖不同**:codegen 与 vectorization 独立注册,可能只在其中一个。
4. **helper 调用链定类型覆盖**:是否调用 `RegisterUnaryDecimal` 等 helper 决定 DECIMAL 支持 —— 追完整调用链。
5. **Layer B 是硬编码**:RexNodeUtil/ValidateCalcOPStrategy 的 Map/白名单是 Java 硬编码,新增函数需改 Java(不是配置)。
6. **Velox/Gluten 业界基准(已拉取)**:`<workspace-root>/velox` + `<workspace-root>/Gluten`(shallow main)。Step 7 可选对比,非 Flink 主线(Spark 生态)。Velox 注册名 `char_length` 而 OmniOperator 注册为 `length`(名不匹配)→ 覆盖扩展参考。
7. **外部依赖源码本地优先(强制)**:调研 Flink/Calcite/Velox/Gluten 的 RexNode 表示 / SqlOperator / convertlet 展开 / 函数实现时,**必须先查本地 `<workspace-root>/` 已拉取源码**(`flink-1.16.3`、`calcite-1.26.0`、`velox`、`Gluten`),本地找不到再联网/context7——保证可复现 + 离线可查,避免网络内容漂移。Flink 未 vendor 的 Calcite 文件(如 `SqlBetweenOperator`、`StandardConvertletTable`)在 `calcite-1.26.0/core/src/main/java/org/apache/calcite/` 下;Flink 已 vendor 的文件(如 `RexSimplify`、`SqlToRelConverter`、`RexNodeJsonSerializer`)在 `flink-1.16.3/flink-table/flink-table-planner/src/main/java/org/apache/calcite/` 下。例:`BETWEEN` RexNode 表示 → `calcite-1.26.0/.../sql/fun/SqlBetweenOperator.java:114`(`validRexOperands` 永远 fail,BETWEEN 不进 RexNode)+ `sql2rel/StandardConvertletTable.java:946 convertBetween`(展开为 `AND(>=, <=)` / SYMMETRIC 的 `OR(AND,AND)` / NOT 外层包 `NOT`)。联网查到的关键外部源码应补 `git clone --branch <tag> --depth 1` 到 `<workspace-root>/` 以便复现。

## 核心踩坑(提炼自记忆)

- **Java 放行 ≠ native 能执行**:Layer B `ValidateCalcOPStrategy` 只用 `containsValue()` 宽松校验类型认识,Layer A C++ `jsonparser` 用 `FunctionSignature::operator==` 逐位精确匹配无隐式转换;两层断层是缺口分析盲区(决策通过 ≠ 运行时支持)。
- **三端类型 ID 系统性错位**:Java `RexTypeToIdMap` 与 C++ `DataTypeId` 基础类型一致,复合类型(ROW/ARRAY/MAP/MULTISET)及部分 TIMESTAMP 变体数值错位;分析复合类型 native 支持时须核对两端 ID,勿只看基础类型。
