# Flink SQL 表达式三层支持分析 — 源码路径速查

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时替换。

> 本文件是 `flink-native-expression-analysis` skill 的源码路径参考。分析 Flink SQL 表达式在 OmniStream native 的支持现状,扫描三层(运行时支持集 = Layer A ∩ Layer B;Layer C 为离线声称清单,与运行时无耦合)。
>
> 仓库根(本地):设 `<workspace-root>` = `<local_work>`(本地工作区根,见 omnistream-env-init skill);`<OmniOperator>` = `<workspace-root>/OmniOperator`、`<OmniAdaptor>` = `<workspace-root>/OmniAdaptor`、`<OmniStream>` = `<workspace-root>/OmniStream`。运行前用 `glob`/`ls` 校验目录存在。

## 表达式数据流(Flink → native)

```
Flink SQL RexNode
  │  CommonExecCalc.translateToPlanInternal() 调 RexNodeUtil.buildJsonMap()
  ▼
RexNodeUtil.java                    ← 硬编码 4 Map(special/binary/unary/udfOperatorMap),不认识标 INVALID
  │  组装 {originDescription, inputTypes, outputTypes, condition} JSON
  ▼
OmniGraphOverride.java              ← validateOperatorByNameForOmniTask():SUPPORT_OP_NAME 白名单 + 检测 INVALID → 回退
  │  + ValidateCalcOPStrategy.executeValidateOperator():SUPPORT_BINARYOP/UNARYOP_NAME 二级白名单递归校验
  ▼  setUseOmniEnabled(true/false)
native: StreamCalcBatch.{h,cpp}     ← JSONParser.ParseJSON → ExpressionEvaluator(preferVectorization=true 硬编码)→ codegen + Evaluate
  │
  ▼
OmniOperator native(实际实现)
  ├── vectorization/registration/   ← ExprEval visitor + VectorFunction dispatch(SIMD)—— Layer A 主真相源
  ├── codegen/func_registry_*.cpp   ← LLVM JIT 注册(独立于 vectorization)
  └── operator/aggregation/aggregator/  ← 聚合 dispatch 工厂

旁路(离线工具,与运行时无耦合):
omnihelper/resources/*.json + omnihelper/{flink,parser}/  ← Layer C 离线字典,仅 Python 静态分析用
```

> ⚠️ **关键**:运行时决策**不读任何字典 JSON**。`is_support_func` 只在 omnihelper Python 离线工具里。运行时放行集 = RexNodeUtil 硬编码 Map + ValidateCalcOPStrategy 白名单;实际能否执行 = 放行后 OmniOperator native 是否注册。Layer C 字典是"声称清单",可能与运行时不一致(如 `CHAR_LENGTH`:字典 `is_support_func=true` 但 native 未注册 → 声称支持实际 not supported)。

---

## Layer A — OmniOperator native 注册层(主要真相源,实际实现)

### 目录布局

```
<OmniOperator>/core/
├── src/vectorization/
│   ├── functions/                  # 函数实现(.h/.cpp,107+ 文件)
│   ├── registration/               # 函数注册(Layer A 主数据源)
│   │   ├── Register.h/.cpp         # 主入口:RegisterAllFunctions() 调 16 类注册
│   │   ├── RegisterMath.cpp        # 算术/数学(+,-,*,/,abs,sin,cos,sqrt...)
│   │   ├── RegisterBitwise.cpp     # 位运算
│   │   ├── RegisterString.cpp      # 字符串
│   │   ├── RegisterArray.cpp       # 数组
│   │   ├── RegisterMap.cpp         # Map
│   │   ├── RegisterComparison.cpp  # 比较
│   │   ├── RegisterConditional.cpp # 条件(coalesce,if,isnull,in)
│   │   ├── RegisterConversion.cpp  # Cast/转换
│   │   ├── RegisterDateTime.cpp    # 日期时间(30+)
│   │   ├── RegisterHash.cpp        # 哈希(sha1,sha2,md5,crc32)
│   │   ├── RegisterJson.cpp        # JSON
│   │   ├── RegisterLambda.cpp      # Lambda
│   │   ├── RegisterMisc.cpp        # 杂项(nanvl,isnan)
│   │   ├── RegisterPredicate.cpp   # 谓词(and,or,not)
│   │   ├── RegisterRegexp.cpp      # 正则(like,rlike,regexp_extract)
│   │   ├── RegisterCollection.cpp  # 集合(size,cardinality,slice,sort_array)
│   │   ├── RegistrationHelpers.h   # 类型批量注册 helper 模板
│   │   └── SimpleFunctionRegistry.h/.cpp
│   ├── ExprEval.h/.cpp             # 表达式求值器(FuncExpr dispatch)
│   └── VectorFunction.h/.cpp       # VectorFunction 基类
├── src/codegen/
│   └── func_registry_*.cpp         # LLVM JIT 注册(11 个,独立于 vectorization)
├── src/operator/aggregation/aggregator/
│   └── aggregator_factory.cpp      # 聚合表达式 dispatch 工厂
└── test/vectorization/             # 单测(120+)
```

### 注册文件映射(函数类 → Register*.cpp)

| 函数类 | 注册文件 |
|---|---|
| 加减乘除、模、abs/sign/正负、round/ceil/floor、三角/对数/幂 | `RegisterMath.cpp` |
| 位运算 AND/OR/XOR/NOT、ShiftLeft/Right、BitCount/BitGet | `RegisterBitwise.cpp` |
| 字符串(concat,substr,...) | `RegisterString.cpp` |
| 数组(append,sort,...) | `RegisterArray.cpp` |
| Map | `RegisterMap.cpp` |
| 比较(<,>,=,!=,...) | `RegisterComparison.cpp` |
| 条件(coalesce,if,isnull,in) | `RegisterConditional.cpp` |
| Cast/转换 | `RegisterConversion.cpp` |
| 日期时间(30+) | `RegisterDateTime.cpp` |
| 哈希(sha1,sha2,md5,crc32) | `RegisterHash.cpp` |
| JSON | `RegisterJson.cpp` |
| Lambda(transform,filter,exists) | `RegisterLambda.cpp` |
| 谓词(and,or,not) | `RegisterPredicate.cpp` |
| 正则(like,rlike,regexp_extract) | `RegisterRegexp.cpp` |
| 集合(size,cardinality,slice,sort_array) | `RegisterCollection.cpp` |

### 两条注册路径

- **Path A — SimpleFunction**(多数函数):`RegisterFunction<Func, TReturn, TArgs...>(prefix+"name", {paramTypes}, returnType)` → `simpleFunctionFactoryMap_`。注意 `Func<TReturn>` 实例化(TReturn 填占位模板参数 T)。
- **Path B — VectorFunction**(concat/split/LIKE 等复杂函数):`VectorFunction::RegisterVectorFunction("name", {paramTypes}, returnType, shared_ptr)` → `functionMap_`。

### 类型覆盖 = RegistrationHelpers.h 的 helper 调用

| Helper | 覆盖类型 |
|---|---|
| `RegisterBinaryIntegral<T>` | int8/int16/int32/int64(同入出) |
| `RegisterBinaryFloatingPoint<T>` | float/double |
| `RegisterBinaryNumeric<T>` | integral + floating |
| `RegisterUnaryIntegral<T>` | bool |
| `RegisterUnaryIntegralSameType<T>` | int8..int64(同入出) |
| `RegisterUnaryNumeric<T>` | integral + floating + decimal |
| `RegisterRoundNumericWithScale<T>` | BYTE/SHORT/INT/LONG/FLOAT/DOUBLE(不含 DECIMAL) |
| `RegisterFunction<Func, Return, Input...>` | 通用(完全控制) |

> 是否调用 `RegisterUnaryDecimal` 等 helper 决定 DECIMAL 是否支持 —— 追完整调用链。

### 数据类型常量

`OMNI_BOOLEAN`(bool)、`OMNI_BYTE`(int8)、`OMNI_SHORT`(int16)、`OMNI_INT`(int32)、`OMNI_LONG`(int64)、`OMNI_FLOAT`、`OMNI_DOUBLE`、`OMNI_VARCHAR`/`OMNI_CHAR`(string_view)、`OMNI_VARBINARY`、`OMNI_DECIMAL64`(int64)、`OMNI_DECIMAL128`、`OMNI_ARRAY`、`OMNI_MAP`。

---

## Layer B — OmniAdaptor Java 决策层(运行时放行集)

| 文件 | 关键点 |
|---|---|
| `<OmniAdaptor>/omnistream/omniop-flink-extension/omni-table-planner/src/main/java/org/apache/flink/table/planner/plan/nodes/exec/util/RexNodeUtil.java` | `buildJsonMap(RexNode)`:Calcite RexNode → OmniOperator JSON。**4 个硬编码 Map**:`specialOperatorMap`(CASE/CAST/JSON_VALUE/DATE_FORMAT/CHAR_LENGTH/LOWER/HASH_CODE/EXTRACT/COALESCE/AND/OR/IF/DATE_ADD/CURRENT_TIMESTAMP/JSON_QUERY/JSON_SPLIT/SEARCH/PROCTIME/...)、`binaryOperatorMap`、`unaryOperatorMap`、`udfOperatorMap`。不在 Map 的算子走 `default` 标 `exprType=INVALID`。另维护 `RexTypeToIdMap`(SqlTypeName→Omni typeId)。 |
| `<OmniAdaptor>/omnistream/omniop-flink-extension/omni-table-planner/.../common/CommonExecCalc.java` | `getExtraDescription()`/`translateToPlanInternal()`:调 `RexNodeUtil.buildJsonMap(projection)` + `buildJsonMap(condition)`,组装 JSON 写回 `transformation.setDescription(...)`。native 侧 StreamCalcBatch 拿到的 description 来源。 |
| `<OmniAdaptor>/omnistream/omniop-flink-extension/java/src/main/java/com/huawei/omniruntime/flink/streaming/api/graph/OmniGraphOverride.java` | `validateOperatorByNameForOmniTask()`(line 712):① 算子名在 `SUPPORT_OP_NAME` 白名单(performanceMode 含 `Calc`);② `operatorDescription.contains("INVALID")` → return false 回退(733-736,**表达式级决策关键**);③ 否则交 `ValidateOperatorStrategyFactory.getStrategy(name).executeValidateOperator(jsonMap)`。设 `vertexConfig.setUseOmniEnabled(true/false)`。 |
| `<OmniAdaptor>/.../validate/strategy/ValidateCalcOPStrategy.java` | `executeValidateOperator()`/`validateCalcExpr()`:递归校验 JSON expr 树。二级硬编码白名单 `SUPPORT_BINARYOP_NAME`(OR/AND/ADD/SUBTRACT/MULTIPLY/DIVIDE/MODULUS/六比较/DATE_FORMAT/count_char)、`SUPPORT_UNARYOP_NAME`(CAST/NEGATION/NOT),并对 `json_split`/`json_query`/`current_timestamp`/`date_add_days`/`to_timestamp_ltz` 做签名校验。default 返回 false。 |

> **提取放行集**:grep `RexNodeUtil.java` 的 4 个 Map 的 key + `ValidateCalcOPStrategy.java` 的 `SUPPORT_*_NAME` 数组。`preferVectorization` 不在 Java 侧(是 StreamCalcBatch.cpp:135 局部变量,硬编码 true)。

---

## Layer C — OmniAdaptor 离线字典层(声称支持,与运行时无耦合)

| 文件 | 内容 |
|---|---|
| `<OmniAdaptor>/omnihelper/resources/flink_function_dictionary.json` | 231 项 Flink 函数;`is_support_func=true` **40 项**。字段:`func_name`/`func_type`/`is_support_func`/`is_supported_type`/`cast_is_support_type`/`param_count`/`param_type_limit` |
| `<OmniAdaptor>/omnihelper/resources/omni_function_dictionary.json` | 464 项 Omni 侧函数;`is_support_func=true` 105 项。字段:`func_name`/`is_support_func` |
| `<OmniAdaptor>/omnihelper/flink/function/dictionary_loader.py` | `FunctionDictionaryLoader.load()`:读 flink 字典,构建 `func_support_map`/`func_is_supported_types`/`cast_is_support_type` + 三类正则。**不读 omni 字典** |
| `<OmniAdaptor>/omnihelper/flink/function/support_checker.py` | `FunctionSupportChecker.is_func_type_supported()`/`check_cast_function()`:判 is_support_func + CAST 白名单 |
| `<OmniAdaptor>/omnihelper/flink/function/function_parse.py` | 入口编排:Loader → Checker → pattern_matcher |
| `<OmniAdaptor>/omnihelper/flink/function/pattern_matcher.py` | `FunctionPatternMatcher`:正则匹配函数调 support_checker |
| `<OmniAdaptor>/omnihelper/parser/function/function_checker.py` | `FunctionChecker.check_support_status()`(另一套 `parser/` 链):判 `is_support_func`/`param_count`/`param_type_limit`/`no_support_type`,CAST/时间/LIKE 专项校验 |

> **关键**:Layer C 全是 omnihelper Python 离线静态分析工具,Java 运行时**不读**。grep `omnistream/` Java 目录 `is_support_func`/`function_dictionary` = 0 命中。Layer C 是"声称清单",用于离线报表/校验,与运行时放行集可能不一致。

---

## OmniStream 算子调用点

| 文件 | 关键点 |
|---|---|
| `<OmniStream>/cpp/streaming/api/operators/StreamCalcBatch.h` | include OmniOperatorJIT 的 `expression/expressions.h`、`expression/jsonparser/jsonparser.h`、`codegen/expr_evaluator.h`、`codegen/simple_filter_codegen.h`、`operator/execution_context.h` |
| `<OmniStream>/cpp/streaming/api/operators/StreamCalcBatch.cpp` | `open()`(106):`JSONParser.ParseJSON` 解析 projExprs/filterCondition → `new ExpressionEvaluator(filterCondition, projExprs, inputTypes_, ofConfig, preferVectorization)`,`preferVectorization=true` 硬编码(135);`processBatch()`(54):`Evaluate()`;`collectUnsupportedExprImpl()`(246):对 `regex_extract_null`/`PROCTIME→TIMESTAMP_LTZ`/`int64*decimal64→decimal128` 兜底改写 FIELD_REFERENCE |

OmniStream 自身无 expression/codegen 目录(`<OmniStream>/cpp/CMakeLists.txt` line 220-222 注释,`include_directories` 引 OmniOperatorJIT)。

---

## 搜索命令

```bash
# Layer A:OmniOperator native 是否注册某函数
grep -r '"func_name"' <OmniOperator>/core/src/vectorization/registration/
grep -rh 'prefix \+ "[a-z_0-9]+"' <OmniOperator>/core/src/vectorization/registration/ | grep -oE '"[a-z_0-9]+"' | tr -d '"' | sort -u   # 全部 vectorization 函数名
grep -rhoE '"[a-z_][a-z_0-9]+"' <OmniOperator>/core/src/codegen/func_registry_*.cpp | tr -d '"' | sort -u                                   # codegen 函数名

# Layer B:OmniAdaptor Java 放行集
grep -nE 'specialOperatorMap|binaryOperatorMap|unaryOperatorMap|udfOperatorMap' <OmniAdaptor>/.../RexNodeUtil.java
grep -nE 'SUPPORT_BINARYOP_NAME|SUPPORT_UNARYOP_NAME' <OmniAdaptor>/.../ValidateCalcOPStrategy.java

# Layer C:离线字典 supported
py -c "import json;d=json.load(open(r'<OmniAdaptor>/omnihelper/resources/flink_function_dictionary.json',encoding='utf-8'));print([x['func_name'] for x in d if x.get('is_support_func')])"

# ExprEval dispatch 完整性(注册但未 dispatch)
grep -n 'FuncExpr' <OmniOperator>/core/src/vectorization/ExprEval.cpp
```

## Velox/Gluten 业界基准(Step 7 可选,已拉取)

| 仓库 | 路径 | 用途 |
|---|---|---|
| Velox | `<workspace-root>/velox/velox/functions/sparksql/registration/Register*.cpp`(14 个) | Spark SQL 函数业界基准(~237 unique,含 `char_length` in `String.h`) |
| Gluten | `<workspace-root>/Gluten/gluten-substrait/src/main/scala/org/apache/gluten/expression/ExpressionMappings.scala` | Spark→Substrait 下推意图全集(303 Sig:`SCALAR_SIGS`/`AGGREGATE_SIGS`/`WINDOW_SIGS`) |

> Spark 生态,非本项目 Flink 主线,仅作业界基准对比。Velox 有 `char_length` 而 OmniOperator 无 → 覆盖扩展参考。

```bash
# Velox sparksql 函数名
grep -rhoE '"[a-z_][a-z_0-9]*"' <workspace-root>/velox/velox/functions/sparksql/registration/*.cpp | tr -d '"' | sort -u
# Gluten Sig 计数
grep -cE 'Sig\[' <workspace-root>/Gluten/gluten-substrait/src/main/scala/org/apache/gluten/expression/ExpressionMappings.scala
```

---

## 测试入口

`<OmniStream>/.claude/skills/omnistream-expression-test/scripts/run_local.sh <name>`:native(OmniStream)vs vanilla(Flink 原生)黄金对比 + 本地富报告 `flink-test/report/<name>/`。用例 `flink-test/test/<name>/<name>.{csv,sql}`。