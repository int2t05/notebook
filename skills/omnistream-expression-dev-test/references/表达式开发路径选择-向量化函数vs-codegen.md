# 表达式开发路径选择:向量化函数 vs codegen

> 配套:[表达式开发指南.md](表达式开发指南.md)、[表达式开发文件清单.md](表达式开发文件清单.md)。
>
> 解决一个具体困惑:**开发一个表达式,到底要不要写 `vectorization/functions/*.h/.cpp`?要不要改 `codegen/*.cpp`?** 用两个真实案例对照——`BETWEEN`(借原语)vs `SIMILAR TO`(完整链路)。
>
> 调研基线:OmniAdaptor/OmniOperator(分支/提交状态见 git log;文中行号为核实时点,代码改动后会漂移,以函数名/类名为准)。

---

## 0. 一句话回答你的困惑

你纠结的"functions 下 cpp/h vs codegen 文件",其实是**两个独立的问题**,不是二选一:

| 问题                                    | 由什么决定                                     | 写哪里                                                   |
| --------------------------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| 要不要**新建一个向量化函数**?     | 语义能否**复用已有原语**拼出来           | `vectorization/functions/*.h/.cpp` + `Register*.cpp` |
| 要不要**为某个 Expr 节点写 JIT**? | 是不是**特殊语法**(需要自定义 Expr 节点) | `codegen/*.cpp` 的 `Visit(const XxxExpr&)`           |

`BETWEEN` 和 `SIMILAR TO` 都是特殊语法(都要新建 Expr 节点),但一个**没写函数**(语义能拆成 `<= AND <=`,借原语),一个**写了函数**(正则没法拆,必须自己实现)。这就是核心区别。

---

## 1. 先认清:四个"写代码"的位置

OmniOperator 表达式引擎有四类你会动代码的地方,职责不同(**注意 `codegen/` 下有两类,别混**):

```
① vectorization/functions/<Name>.{h,cpp} + Register*.cpp
   写一个「可复用的向量化函数」(VectorFunction/SimpleFunction),列式批量执行
   注册后按名字被调用,是一等公民,可被多处复用

② expression/expressions.{h,cpp} + jsonparser.cpp + expr_visitor/verifier/printer
   新建一个「Expr AST 节点」(如 BetweenExpr / SimilarExpr)
   只在表达式是特殊语法、不能走通用 FuncExpr 时才需要

③ codegen/functions/<domain>functions.{h,cpp} + func_registry_<domain>.cpp
   写一个「row JIT 函数」(extern "C",逐行调用,可用 ExecutionContext)
   给复杂逐行逻辑/需外部上下文(JSON 缓存、正则)的普通函数用(见指南 §2.1/§8)

④ codegen/batch_expression_codegen.cpp + expression_codegen.cpp
   为某个 Expr 节点写「LLVM JIT 编译逻辑」(Visit 方法)
   决定这个节点在 codegen 路径下怎么编译成机器码
```

- ①③ 都是"造零件"(造函数):① 列式向量化,③ 逐行 row JIT——**普通函数(Type A)二选一**(判据:能整列批量→①;需逐行外部上下文→③,见指南 §2.1)。
- ②④ 是"接专线"(为特殊语法 Expr 节点接线):② 建节点,④ 写节点 JIT 逻辑。
- 普通函数(Type A)动 ① 或 ③;特殊语法(Type B)动 ②,然后视情况动 ①(造 VectorFunction,B-②)或 ④(_codegen-lower,B-①)。

---

## 2. 三种范式(决策矩阵)

| 范式                                 | 何时用                                             | 新 Expr 节点?          | 新向量化函数? | codegen Visit?          | 实际执行路径                           | 标杆                  |
| ------------------------------------ | -------------------------------------------------- | ---------------------- | ------------- | ----------------------- | -------------------------------------- | --------------------- |
| **A 纯向量化函数**             | 普通函数调用(`LEFT`/`char_length`/`concat`) | ❌(用通用`FuncExpr`) | ✅            | ❌                      | ExprEval→`Apply`(或 codegen 调函数) | LEFT/RIGHT、DATE 系列 |
| **B 专用 Expr + codegen 下放** | 特殊语法 + 语义**能拆成已有原语**            | ✅                     | ❌            | ✅(lower 到原语)        | **codegen**                      | **BETWEEN**     |
| **C 专用 Expr + 专用函数**     | 特殊语法 + 语义**需专属逻辑**                | ✅                     | ✅            | ⚠️ stub(返回 invalid) | **ExprEval→`Apply`**          | **SIMILAR TO**  |

> 注意:本篇「范式 A/B/C」是决策矩阵本地编号,**勿与指南 Type A/B/C/D 混淆**:范式 A=Type A(普通函数),范式 B=Type B-①(BETWEEN,拆得开→codegen 借原语),范式 C=Type B-②(SIMILAR TO,拆不开→写专用函数);指南 Type C 是聚合,与此无关。

---

## 3. 决策树

```
                  开发一个表达式
                       │
              ┌────────▼────────┐
              │ 是普通函数调用? │   (SQL 里像 func(a,b),Calcite 当 SqlFunction)
              └────────┬────────┘
                 是    │         否(是操作符:BETWEEN/LIKE/SIMILAR TO/IN...)
        ┌──────────────┘         │
        │                        ▼
   【范式 A】              需要自定义 exprType + 新 Expr 节点
   只写 functions/*.h/.cpp        + jsonparser + visitor/verifier/printer
   + Register*.cpp                       │
   不碰 codegen,不建 Expr 节点           │
                                         ▼
                              语义能拆成已有向量化原语?
                              (如 BETWEEN = lower<=val AND val<=upper)
                                   │
                    ┌──────────────┴──────────────┐
                   是                              否
                    │                              │
               【范式 B】                      【范式 C】
               不写函数                        写 functions/*.h/.cpp
               codegen Visit lower 到原语       + Register*.cpp 注册
               ExprEval Visit 留空 stub         ExprEval Visit 调 Apply
               执行走 codegen                   codegen Visit 返回 invalid
                                               执行走 ExprEval(解释器)
```

---

## 4. 案例 A:BETWEEN —— 范式 B(借原语,不写函数)

### 为什么选 B

`x BETWEEN a AND b` ≡ `a <= x AND x <= b`。语义**完全能拆成已有的向量化比较原语** `batch_lessThanEqual` 和逻辑原语 `batch_and`——没必要造新函数,在 codegen 里把这些原语拼起来即可。

### 改了哪些文件

| 仓库         | 文件                                                                  | 做了什么                                                                                                                      |
| ------------ | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| OmniAdaptor  | `RexNodeUtil.java` `case SEARCH`(:577)                            | Calcite 把 BETWEEN 优化成`SEARCH(x, Sarg[a..b])`,在此识别闭区间→产出 `exprType:"BETWEEN"`(value/lower_bound/upper_bound) |
| OmniOperator | `expressions.h:333` `BetweenExpr`                                 | 新 Expr 节点(value/lowerBound/upperBound)                                                                                     |
| OmniOperator | `jsonparser.cpp:560/239`                                            | 解析`BETWEEN`→`BetweenExpr`                                                                                              |
| OmniOperator | `ExprEval.cpp:486`                                                  | **空 stub**:`void Visit(const BetweenExpr &e) {}` —— 解释器路径**不实现**                                     |
| OmniOperator | `batch_expression_codegen.cpp:1741` `BatchVisitBetweenExprHelper` | **codegen lower**:`batch_lessThanEqual`×2(:1793-1794)+ `batch_and`(:1803)+ `batch_or` 处理 null                  |
| OmniOperator | `expr_verifier.cpp:221`                                             | `vectorFunction==nullptr`→`isSupportVectorization_=false`(禁用解释器,走 codegen)                                         |

### 关键特征

- ❌ **没有** `functions/Between.h/.cpp`,**没有** 在 `Register*.cpp` 注册 `between` 函数。
- ✅ codegen 是活的(lower 到原语),ExprEval 是死的(空)。
- 执行:**codegen 路径**。借了 `batch_lessThanEqual` + `batch_and` 两个已有原语。

---

## 5. 案例 B:SIMILAR TO —— 范式 C(完整链路,写专用函数)

### 为什么选 C

`x SIMILAR TO pattern` 是 SQL 正则全匹配。**正则语义没法拆成已有比较/逻辑原语**(没有现成的 `batch_regex_match`),必须自己实现 re2 全匹配 → 造一个专用函数 `SimilarFunction`。又因为 `SimilarFunction` 是 `VectorFunction`(自带批级循环 + re2 编译缓存),不适合被 row-JIT codegen 内联,所以 codegen **返回 invalid 回退到解释器**执行。

### 为什么 VectorFunction 而非 SimpleFunction

- **re2 编译昂贵,需批级缓存**:`MatchSimilar` 用 `thread_local` 缓存编译后的 `RE2`(`Similar.cpp:94`),不能每行重编译。SimpleFunction 的 `call(标量)` 是无状态逐元素,没干净的批级缓存位置。
- **ConstVector 快路径**:`ApplySimilar` 判 `patternVec->GetEncoding()==OMNI_ENCODING_CONST`(`Similar.cpp:36`)→ 常量 pattern 整批只编译一次。SimpleFunction 的 `call()` 只拿解码后标量,**看不到向量 encoding**,做不了这个优化。
- **架构硬接**:`SimilarExpr` 构造 `VectorFunction::Find`(`expressions.cpp:1020`)只查 `functionMap_`(VectorFunction),不查 SimpleFunction。要 SimpleFunction 就得 ditch `SimilarExpr` 走 `FuncExpr`,但 SIMILAR TO 是操作符必须建 `SimilarExpr`。
- **同类佐证**:LIKE/RLike 也都是 VectorFunction——pattern 匹配类一律 VectorFunction。**判据:每行算要不要"整批共享昂贵 setup"(如编译正则)?要→VectorFunction;不要→SimpleFunction。**

### 改了哪些文件(基本是未提交 WIP)

| 仓库         | 文件                                                                  | 做了什么                                                                                                                                                                                              |
| ------------ | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OmniAdaptor  | `RexNodeUtil.java:109/246/674`                                      | `specialOperatorMap.put("SIMILAR TO",...)` + 枚举 + `case SIMILAR_TO`→`exprType:"SIMILAR_TO"`(value/pattern);3 参带 ESCAPE→INVALID 回退                                                       |
| OmniAdaptor  | `ValidateCalcOPStrategy.java:422`                                   | `case "SIMILAR_TO":` 校验                                                                                                                                                                           |
| OmniAdaptor  | `flink_function_dictionary.json:61`                                 | `SIMILAR TO`/`NOT SIMILAR TO`→`is_support_func:true`                                                                                                                                           |
| OmniOperator | `expressions.h:485` `SimilarExpr`                                 | 新 Expr 节点(value/pattern);**构造函数 `expressions.cpp:1016-1024` 用 `FunctionSignature("similar_to",...)`+`VectorFunction::Find` 查找已注册的 SimilarFunction 存入 `vectorFunction`** |
| OmniOperator | `jsonparser.cpp:590/424`                                            | 解析`SIMILAR_TO`→`SimilarExpr`                                                                                                                                                                   |
| OmniOperator | **`functions/Similar.h`+`Similar.cpp`(新文件)**             | **`class SimilarFunction : public VectorFunction`**:`Apply()` 把 SQL SIMILAR 模式翻译成 POSIX 正则(re2)逐行全匹配,线程级编译缓存(`SimilarPatternToRegex`/`MatchSimilar`)                |
| OmniOperator | `RegisterRegexp.cpp:17-18`                                          | `RegisterVectorFunction("similar_to", {OMNI_VARCHAR,OMNI_VARCHAR}, OMNI_BOOLEAN, similarFunction)` 注册进 `functionMap_`                                                                          |
| OmniOperator | `ExprEval.cpp:527-537`                                              | **`Visit(const SimilarExpr&)` 调 `e.vectorFunction->Apply(...)`** —— 解释器路径**是活的**(对比 BETWEEN 的空 stub)                                                                   |
| OmniOperator | `expression_codegen.cpp:804` + `batch_expression_codegen.cpp:481` | **codegen `Visit` 返回 `CreateInvalidCodeGenValue()`** —— codegen 不实现,回退解释器                                                                                                       |
| OmniOperator | `expr_verifier.cpp:300`                                             | `vectorFunction` 非空(SimilarFunction 已注册)→`isSupportVectorization_=true`(走解释器)                                                                                                           |
| OmniOperator | `SimilarTest.cpp`(新文件)                                           | 单测                                                                                                                                                                                                  |

### 关键特征

- ✅ **有** `functions/Similar.h/.cpp`(专用函数),✅ **有** `RegisterRegexp.cpp` 注册 `similar_to`。
- ✅ ExprEval 是活的(调 Apply),⚠️ codegen 是 stub(返回 invalid)。
- 执行:**解释器路径**(ExprEval→SimilarFunction::Apply)。**没借任何已有原语**,自己写了 re2 全匹配。

---

## 6. BETWEEN vs SIMILAR TO 逐项对照

| 维度                 | BETWEEN(范式 B)                               | SIMILAR TO(范式 C)                                                    |
| -------------------- | --------------------------------------------- | --------------------------------------------------------------------- |
| 特殊语法?            | 是(Type B)                                    | 是(Type B)                                                            |
| 新 Expr 节点         | `BetweenExpr`                               | `SimilarExpr`                                                       |
| OmniAdaptor 入口     | `case SEARCH`(Sarg)→`exprType:"BETWEEN"` | `specialOperatorMap`+`case SIMILAR_TO`→`exprType:"SIMILAR_TO"` |
| 新向量化函数         | ❌ 无                                         | ✅`SimilarFunction`(re2)                                            |
| 注册到 Register*.cpp | ❌ 无                                         | ✅`similar_to`                                                      |
| ExprEval`Visit`    | **空** stub                             | **调 `Apply`**(活)                                            |
| codegen`Visit`     | **lower 到原语**(活)                    | **返回 invalid**(stub)                                          |
| 执行路径             | codegen                                       | 解释器(ExprEval)                                                      |
| 借了已有原语?        | ✅`batch_lessThanEqual`+`batch_and`       | ❌ 零,自写 re2                                                        |
| 选择依据             | 语义可拆成`<= AND <=`                       | 正则不可拆,需专属逻辑                                                 |

> 一句话:**两者都是 Type B(特殊语法,建 Expr 节点),但 BETWEEN 的语义能拆→借原语走 codegen;SIMILAR TO 的语义拆不开→自写函数走解释器。**

---

## 7. 回到你的问题:到底写哪个?

按这个顺序自问:

1. **是普通函数调用吗?**(SQL 里 `func(a,b)`,Calcite 当 `SqlFunction`)
   → **范式 A**:只写 `functions/*.h/.cpp` + `Register*.cpp`。不建 Expr 节点,不碰 codegen。**(最常见,90%+ 的标量函数都是这个)**
2. **是特殊语法操作符吗?**(BETWEEN/LIKE/SIMILAR TO/IN/IS NULL…)
   → 必须建 Expr 节点 + jsonparser + visitor/verifier/printer。然后:

   - **语义能拆成已有向量化原语?**(像 `<=`/`AND`/`OR` 这种比较/逻辑)
     → **范式 B**:不写函数,codegen `Visit` 里 lower 到原语,ExprEval 留空。执行走 codegen。
   - **语义需要专属逻辑?**(正则、JSON 解析、加密…没有现成原语)
     → **范式 C**:写 `functions/*.h/.cpp` + `Register*.cpp`,ExprEval `Visit` 调 `Apply`,codegen `Visit` 返回 invalid。执行走解释器。

### 判据速记

- **能拆成已有原语 → 借原语(范式 B,改 codegen)**:省一个函数,但 codegen 要写 lower 逻辑。
- **拆不开 → 造函数(范式 C,写 functions/)**:多一个函数文件 + 注册,但 codegen 只需 stub。
- **普通函数 → 造函数(范式 A)**:只造函数,连 Expr 节点都不用建。

### 为什么 SIMILAR TO 不能像 BETWEEN 那样借原语?

BETWEEN 的 `<=`/`AND` 是引擎里**已有的一等向量化原语**(`batch_lessThanEqual`/`batch_and`),codegen 直接调用即可。SIMILAR TO 的"正则全匹配"引擎里**没有现成原语**,且 re2 带编译缓存、不适合 row-JIT 内联——所以只能造一个 `SimilarFunction`(VectorFunction),让解释器批量调它的 `Apply`。

---

## 8. 速查:三种范式要改的文件清单

### 范式 A(纯向量化函数,普通函数调用)

```
OmniAdaptor:  RexNodeUtil.java(specialOperatorMap + enum + buildJsonMap case → exprType:"FUNCTION")
              flink_function_dictionary.json(使能)
OmniOperator: vectorization/functions/<Name>.{h,cpp}     ← 造函数
              vectorization/registration/Register<Category>.cpp  ← 注册
              test/vectorization/<Name>Test.cpp          ← 单测
```

### 范式 B(专用 Expr + codegen 下放,特殊语法可拆)

```
OmniAdaptor:  RexNodeUtil.java(产出自定义 exprType,如 BETWEEN 走 SEARCH)
              ValidateCalcOPStrategy.java(新 exprType 校验) + 字典
OmniOperator: expression/expressions.{h,cpp}             ← 新 Expr 节点
              expression/jsonparser/jsonparser.{h,cpp}   ← 解析新 exprType
              expression/expr_visitor.{h,cpp} + expr_verifier.{h,cpp} + expr_printer.{h,cpp}
              codegen/batch_expression_codegen.cpp       ← Visit lower 到原语(活)
              codegen/expression_codegen.cpp             ← Visit lower(活)
              vectorization/ExprEval.cpp                 ← Visit 留空 stub
              ❌ 不写 functions/,不碰 Register*.cpp
```

### 范式 C(专用 Expr + 专用函数,特殊语法不可拆)

```
OmniAdaptor:  RexNodeUtil.java(specialOperatorMap + enum + buildJsonMap case → 自定义 exprType)
              ValidateCalcOPStrategy.java(校验) + 字典
OmniOperator: expression/expressions.{h,cpp}             ← 新 Expr 节点(ctor 里 Find 函数)
              expression/jsonparser/jsonparser.{h,cpp}   ← 解析新 exprType
              expression/expr_visitor.{h,cpp} + expr_verifier.{h,cpp} + expr_printer.{h,cpp}
              vectorization/functions/<Name>.{h,cpp}     ← 造专用函数(SimilarFunction)
              vectorization/registration/Register<Category>.cpp  ← 注册(VectorFunction)
              vectorization/ExprEval.cpp                 ← Visit 调 Apply(活)
              codegen/batch_expression_codegen.cpp       ← Visit 返回 invalid(stub)
              codegen/expression_codegen.cpp             ← Visit 返回 invalid(stub)
              test/vectorization/<Name>Test.cpp          ← 单测
```

---

## 9. 部署提醒(范式 B/C)

范式 B/C 都新建 Expr 类(头文件加成员/新 virtual 槽)= **ABI 破坏**,部署前**必须 `omnistream_incr` 重编 OmniStream**,否则 ODR/崩溃。范式 A(只造函数,`.cpp`-only)则只需 `operator_build`+`deploy`,不必重编 OmniStream。见 OmniStream CLAUDE.md §6。

> SIMILAR TO 等特性的实现/提交状态见 git log,不在此固定记录(易过时)。

---

> **参考**:Type A/B/C/D 分类与框架原理见 [表达式开发指南.md](表达式开发指南.md);每范式完整文件清单见 [表达式开发文件清单.md](表达式开发文件清单.md)。本篇聚焦"Type B 内部的 B/C 分叉"——即何时写函数、何时改 codegen。
