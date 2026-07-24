---
name: omnioperator-expression-dev
description: Use for OmniOperator expression development. Trigger when implementing new vectorized expressions, functions, or operators in OmniOperator framework. This includes scalar functions, variadic functions, bitwise operations, math functions, string functions (like concat, split, substring), or any vectorized SQL function implementation via the vectorization SimpleFunction/VectorFunction path (Register*.cpp under core/src/vectorization/). Aggregate/window functions and the row-JIT codegen path (codegen/functions/ + func_registry_*.cpp) are out of scope. Also trigger when asked to "implement function", "add expression", "create vectorized function", "实现函数", "添加表达式", "编写函数", when working with Register*.cpp registration files, or when user mentions "OmniOperator" with "function/expression/implementation" or "函数/表达式/实现" and specifies function signature, arguments, return type, NULL handling, or vector encoding support.
---

# OmniOperator Expression Development

> 📖 **表达式开发权威指南**:全链路架构、Type A/B/C/D 分类、框架原理(Expr/Visitor/JSONParser/FunctionRegistry)、json_value 深度案例、C 函数规范与排错,见 [表达式开发指南.md](../omnistream-expression-dev-test/references/表达式开发指南.md)。本 skill 聚焦 OmniOperator 向量化函数实现(vectorization 路径),权威指南为总纲。

This skill guides the implementation of new vectorized expressions and functions in the OmniOperator framework. OmniOperator is a vectorized execution engine that follows patterns from Velox (Meta's vectorization framework).

## When This Skill Applies

This skill activates when you need to:
- Implement a new SQL function (math, string, bitwise, array, etc.)
- Add vectorized expression support for OmniOperator
- Create or modify function registration in `Register*.cpp` files
- Write unit tests for expression implementations

> **范围边界**:本 skill 仅覆盖**向量化路径**(`core/src/vectorization/` 下的 SimpleFunction/VectorFunction + `Register*.cpp`)。**不覆盖** row JIT(`core/src/codegen/functions/` + `func_registry_*.cpp`)、聚合(`core/src/operator/aggregation/`)、窗口(`core/src/operator/window/`)——这些由 `omnistream-expression-dev-test` 编排。
>
> **特殊语法操作符**(BETWEEN/LIKE/SIMILAR TO/IN,需自定义 `exprType` + 新 Expr 节点):除写向量化函数外,**还需建 Expr 节点 + jsonparser + ExprEval + codegen stub**,否则漏建脚手架导致 native 不通。且此时要决定"借原语走 codegen"还是"造函数走解释器"——见 `../omnistream-expression-dev-test/references/表达式开发路径选择-向量化函数vs-codegen.md`。

## Reference Files

The `references/` directory provides template files that MUST be consulted during implementation:

| File | Purpose |
|------|---------|
| [`references/function_template.h`](references/function_template.h) | Header file templates (unary/binary/ternary, all call() return type patterns) — use when implementing `.h` files |
| [`references/function_template.cpp`](references/function_template.cpp) | Implementation file template — use when implementing `.cpp` files |
| [`references/test_template.cpp`](references/test_template.cpp) | Unit test template (ExprEval path, VectorFunction::Apply path, string path) — use when writing tests |
| [`references/design_document_template.md`](references/design_document_template.md) | Design document template — use in Step 4 |
| [`references/project_structure.md`](references/project_structure.md) | Project directory layout, registration file mapping, helper templates, data type constants, search commands |

**Important:** When executing Step 6 (implement function) and Step 8 (write tests), you MUST read the corresponding reference template files first and follow their structure exactly.

## Execution Protocol (CRITICAL)

**You MUST use the TaskCreate tool at the start of every task to create and display a visible task list.** This allows the user to track progress through the development workflow.

When this skill is triggered, immediately create tasks using this structure:

```
1. Analyze requirements and understand function specification
2. Research Velox reference implementation
3. Research OmniOperator existing patterns
4. Create design document
5. ⏸️ AWAIT USER APPROVAL (Design Review)
6. Implement function (.h and .cpp)
7. Register function in appropriate Register*.cpp
8. Write unit tests (MANDATORY deliverable — see Constraint #1; not optional)
9. Verification and completeness check
```

Update task status as you progress:
- Set status to `in_progress` when starting a task
- Set status to `completed` when finishing a task
- The ⏸️ emoji indicates a user approval checkpoint

## Project Structure Overview

> For the complete project directory layout, registration file mapping, data type constants, and search commands, see [`references/project_structure.md`](references/project_structure.md).

## Development Workflow

### Phase 1: Analysis and Design

#### Step 1: Understand the Requirement

**Task:** "Analyze requirements and understand function specification"

Clarify the function to be implemented:
- **Function name** (e.g., `sqrt`, `bit_count`, `date_add`)
- **Function category** (scalar/aggregate/window/math/string/bitwise/etc.)
- **Input/output types** (e.g., `double -> double`, `int -> bigint`)
- **Edge cases** (null handling, overflow, invalid inputs)

#### Step 2: Research Reference Implementations

**Task:** "Research Velox reference implementation"

Study Velox first (the reference implementation):
```bash
# Search Velox for similar functions
find velox/velox/functions -name "*<function_name>*"
grep -r "function_name" velox/velox/functions --include="*.cpp"
```

**Key learning objectives:**
1. How does Velox implement the vectorized logic?
2. What edge cases does Velox handle?
3. What are the function signatures used?

#### Step 3: Research OmniOperator Patterns

**Task:** "Research OmniOperator existing patterns"

Study existing OmniOperator patterns:
```bash
# Find related registration file
ls OmniOperator/core/src/vectorization/registration/Register*.cpp

# Find similar function implementations
grep -r "SimilarFunction" OmniOperator/core/src/vectorization/functions/
```

**Key learning objectives:**
1. How does OmniOperator register similar functions?
2. What helper functions are available?
3. What is the existing code style and structure?

#### Step 4: Create Design Document

**Task:** "Create design document"

Before coding, create a detailed design document at:
`OmniOperator/docs/expression-design/<function_name>_design.md`(目录不存在时先 `mkdir -p OmniOperator/docs/expression-design`)

**Template:** Refer to [`references/design_document_template.md`](references/design_document_template.md) for the design document structure.

#### Step 5: Design Review - AWAIT USER APPROVAL

**Task:** "⏸️ AWAIT USER APPROVAL (Design Review)"

**MANDATORY CHECKPOINT:** After creating the design document, you MUST stop and request user approval before proceeding.

**Use the AskUserQuestion tool with this exact structure:**

```markdown
## Design Document Ready for Review

I've created the design document at: `OmniOperator/docs/expression-design/<function_name>_design.md`

**Summary:**
- Function: <function_name>
- Category: <category>
- Input/Output: <types>
- Registration file: <Register*.cpp>

**Next steps after approval:**
1. Implement function header
2. Add registration entries
3. Write unit tests

Do you approve this design and want me to proceed with implementation?
```

Options:
- "Yes, proceed with implementation"
- "No, I need changes (will specify)"
- "Let me review the document first"

**DO NOT proceed to Phase 2 until user explicitly approves.**

### Phase 2: Implementation

**Only begin Phase 2 after receiving explicit user approval in Step 5.**

#### Step 6: Implement the Function

**Task:** "Implement function (.h and .cpp)"

**Prerequisite:** Read the design document at `OmniOperator/docs/expression-design/<function_name>_design.md` and implement according to the **Implementation Plan** section. Specifically follow the decisions made in the design document for:
- Function class structure (struct name, call() signature, return type convention)
- Type specializations needed
- Edge case handling strategy

**Location:**
- Header: `OmniOperator/core/src/vectorization/functions/<FunctionName>.h`
- Implementation: `OmniOperator/core/src/vectorization/functions/<FunctionName>.cpp` (needed for complex logic, date/array/string functions with helpers, etc.)

**Templates:** Use the following reference files as structural guides, filling in the specifics from the design document:
- [`references/function_template.h`](references/function_template.h) — header file templates for unary, binary, and ternary functions, covering all call() return type patterns
- [`references/function_template.cpp`](references/function_template.cpp) — implementation file template for `.cpp` files

**Key patterns:**
- Use `ALWAYS_INLINE` for performance
- The `call()` method supports three return type conventions:
  - `Status` — for arithmetic/math/bitwise (return `Status::OK()` on success, `Status::UserError(...)` on error). Null handling is done by the vector framework.
  - `bool` — for string/comparison functions (`true` = valid result, `false` = NULL output). The bool becomes the null flag in the output vector.
  - `void` — always produces non-NULL result (`notNull = true`).
- Some functions use `callNullable()` instead of `call()` when they need to inspect null inputs directly (input pointers are `const T*`, nullable).
- Use template specialization for different types

#### Step 7: Register the Function

**Task:** "Register function in appropriate Register*.cpp"

**Prerequisite:** Read the design document at `OmniOperator/docs/expression-design/<function_name>_design.md` and follow the **Registration entries** specified in the **Implementation Plan** section. The design document should have already determined which registration file and which registration pattern (helper template vs explicit `RegisterFunction<>`) to use.

**Find the correct registration file:**

> For the complete function category → registration file mapping, see the "Registration File Mapping" section in [`references/project_structure.md`](references/project_structure.md). If no appropriate file exists, create a new one following the pattern.

**Registration patterns:**

There are two registration paths:

**Path A — SimpleFunction (most functions):** Uses `RegisterFunction<>()` which inserts into `simpleFunctionFactoryMap_`. The function struct is wrapped by `FunctionHolder` -> `SimpleFunctionAdapterFactory` -> `SimpleFunction`.

```cpp
// Unary function - single type specialization
RegisterFunction<FunctionName, double, double>(
    prefix + "function_name",
    {OMNI_DOUBLE},
    OMNI_DOUBLE
);

// Multiple type specializations
RegisterFunction<FunctionName, int32_t, int32_t>(prefix + "func", {OMNI_INT}, OMNI_INT);
RegisterFunction<FunctionName, int64_t, int64_t>(prefix + "func", {OMNI_LONG}, OMNI_LONG);
RegisterFunction<FunctionName, double, double>(prefix + "func", {OMNI_DOUBLE}, OMNI_DOUBLE);

// Binary function
RegisterFunction<FunctionName, double, double, double>(
    prefix + "binary_func",
    {OMNI_DOUBLE, OMNI_DOUBLE},
    OMNI_DOUBLE
);

// Using helper templates (when available)
RegisterUnaryNumeric<UnaryFunction>({prefix + "unary_func"});
RegisterBinaryNumeric<BinaryFunction>({prefix + "binary_func"});
RegisterBinaryIntegral<BinaryIntegralFunction>({prefix + "binary_int_func"});
```

Note: `RegisterFunction<Func, TReturn, TArgs...>` instantiates `Func<TReturn>` — `TReturn` fills the dummy template parameter `T`.

**Path B — VectorFunction (complex functions like concat, split, LIKE):** Uses `VectorFunction::RegisterVectorFunction()` which inserts a pre-built shared_ptr into `functionMap_`. Use this when a function needs custom batch-level processing logic.

**Important:** After adding registration, ensure the function is called from `Register.cpp`:
```cpp
void RegisterFunctions::RegisterAllFunctions(const std::string &prefix) {
    // ...
    Register<FunctionCategory>Functions(prefix);
}
```

#### Step 8: Write Unit Tests (MANDATORY)

**Task:** "Write unit tests"

> **MANDATORY deliverable, not optional.** The unit test file is a required part of every function implementation. Lack of Kunpeng hardware only prevents *running* tests locally (gtest execution delegated to the `operator_test` task in `omnistream-build-deploy`; end-to-end Flink SQL validation uses `omnistream-expression-test`); it never excuses *writing* them. See Constraint #1.

**Prerequisite:** Read the design document at `OmniOperator/docs/expression-design/<function_name>_design.md` and implement the test cases specified in the **Test Plan** and **Edge Cases** sections. The design document should have already identified specific test values, boundary conditions, and expected results during the analysis phase.

**Location:** `OmniOperator/core/test/vectorization/<FunctionName>Test.cpp`

**Template:** Use [`references/test_template.cpp`](references/test_template.cpp) as the structural template for includes, namespace declarations, and test patterns, then fill in the specific test cases from the design document:

- **ExprEval path** (end-to-end,经 ExprEval::Visit + 决策链;UT 逻辑测试优先 VectorFunction::Apply 直驱,见下方 UT 设计原则): Create raw C-array inputs via `CreateVectorBatch()`, build expression tree with `FuncExpr` + `FieldExpr`, evaluate via `ExprEval::Visit()`, verify with `dynamic_cast<Vector<T>*>`.
- **VectorFunction::Apply path** (for precise control): Create vectors via `VectorHelper::CreateFlatVector()`, lookup via `VectorFunction::Find(signature)`, execute via `Apply()` with `std::stack<BaseVector*>`. Useful for NaN/Inf testing and custom vector construction.

**Test coverage should include:**
1. Basic functionality with typical inputs
2. Null input handling
3. Edge cases (min/max values, zero, negative numbers)
4. Type conversion behaviors
5. Invalid inputs (division by zero, negative sqrt, etc.)

**UT 设计原则(2026-07-20 BETWEEN 经验):**
- **优先 VectorFunction::Apply 直驱路径**(非 ExprEval 路径)测逻辑:用 helper 构造函数对象 + `std::stack<BaseVector*>` 直接调 `Apply`,隔离 ExprEval/决策链,聚焦函数自身语义。ExprEval::Visit + supportVectorized 决策 + vectorFunction 查找由 e2e(native vs vanilla)覆盖,UT 不重复。
- **UT 与 e2e 互补**:UT = VectorFunction::Apply 逻辑(精确控向量,含 NaN/NULL/边界);e2e = ExprEval::Visit + 决策 + native==vanilla 逐行一致。两者都需要,UT 不能替代 e2e(UT 不验证接线)。
- **三值逻辑函数(AND/OR/BETWEEN/比较)必测决定性用例**:`FALSE AND UNKNOWN = FALSE`(非 UNKNOWN)、`NULL value → UNKNOWN`、`NULL 操作数 → UNKNOWN 或 FALSE`(按 SQL 三值)。反例:BETWEEN 早期只测"任一 NULL→UNKNOWN"会漏 `12 BETWEEN NULL AND 10 → FALSE`。
- **类型覆盖**:主数值类型(INT)+ 字符串(VARCHAR,走 string 路径)即可;其余数值(BYTE/SHORT/LONG/FLOAT/DOUBLE/DECIMAL)共享同一模板,一个代表够。不追求每类型都测。
- **测试文件自动发现**:`core/test/vectorization/CMakeLists.txt` 用 `aux_source_directory` 自动收 .cpp,**新增 Test.cpp 无需改 CMakeLists**(构建配置不进 commit,见 CLAUDE.md §6)。
- **BOOLEAN 返回的函数 e2e 测法**:测**向量化**路径用 FILTER(`WHERE bool_expr`,输出非 bool 列);测 **codegen 回退**用 `CAST(bool_expr AS INT)` 投影(1/0/null)。⚠️ `CAST(BOOLEAN AS INT)` 被 planner 改写成 CASE→SWITCH_GENERAL→**codegen**(非向量化),两条路径都要测。详见 `omnistream-expression-test` skill 前提 5。勿用 CASE/IF/CAST AS VARCHAR。
- **UT 覆盖 e2e 不可达的类型**:某些类型 e2e 测不了(jsonparser 字面量界 gap 如 BETWEEN 的 VARCHAR/TIMESTAMP;SOURCE/SINK_SUPPORT 限制如 DOUBLE/BOOLEAN/CHAR)。这些类型的 VectorFunction 分派只能靠 UT(Apply 直驱),UT 类型覆盖要比 e2e 广(INT/LONG/DOUBLE/VARCHAR/DECIMAL 各测一个代表,覆盖 Apply 的 type dispatch 各分支)。
- **OmniAdaptor 翻译非平凡时另写 Java UT**(`omni-table-planner/src/test/java/.../RexNodeUtilXxxTest.java`,直驱 `buildJsonMap`,本地 `mvn test` 无需鲲鹏)——测 RexCall→JSON 翻译,是本侧 Apply 直驱 UT 的对偶;何时写见 `omniadaptor-vectorized-expression` skill §2.5 / 权威指南 §10.3。本 skill 的 C++ UT 只测向量化函数语义,不测翻译接线。

#### Step 9: Verification

**Task:** "Verification and completeness check"

Use the Verification Checklist below to ensure completeness.

## Code Style Guidelines

### Naming Conventions
- Function struct: `<FunctionName>Function` (e.g., `SqrtFunction`, `BitCountFunction`)
- Test file: `<FunctionName>Test.cpp` (e.g., `MathFunctionTest.cpp`)
- Registration: `Register<FunctionCategory>Functions()`

### Comments
- **Strict English only** — no Chinese in any comment (file header, function, TODO). Brief; prefer `//` line comments explaining intent over `/** @param */` blocks; obvious code needs no comment.
- **Hard cap: `//` comments max 2 lines** (default 1 line of concise "why"; rarely 2). More than 2 lines = restating code — trim or delete. File-header `Description:` one line.
- **Follow the comment style of existing files in the same directory** — see `core/src/expression/expressions.cpp`, `vectorization/functions/ConcatFunction.h`, and the `references/function_template.*` templates.
- See CLAUDE.md §7 for the project-wide rule.

### Common Data Types

> For the complete data type constants reference table, see the "Data Type Constants" section in [`references/project_structure.md`](references/project_structure.md).

### Helper Templates Available

> For the complete helper template list with descriptions, see the "Common Helper Templates" section in [`references/project_structure.md`](references/project_structure.md).

## Important Constraints

1. **Test code is MANDATORY; only test *execution* is non-local:** Writing the unit test file `OmniOperator/core/test/vectorization/<FunctionName>Test.cpp` is a REQUIRED deliverable of every function implementation — NOT optional, NOT deferred. "No Kunpeng hardware" means you cannot compile or run tests locally (gtest execution delegated to the `operator_test` task in `omnistream-build-deploy` on the remote aarch64 server; end-to-end Flink SQL validation uses `omnistream-expression-test`); it does NOT excuse skipping test code. Always model the test on an existing test in `OmniOperator/core/test/vectorization/` (e.g. `MathFunctionTest.cpp`, `BitCountTest.cpp`, `ConcatTest.cpp`, `CharLengthTest.cpp`, `LeftRightTest.cpp`) or on [`references/test_template.cpp`](references/test_template.cpp). Do NOT attempt to compile or run tests locally.

2. **Follow existing patterns:** Study similar functions in the codebase before implementing. Consistency is critical.

3. **Header file dependencies:** When calling existing functions, check the function signature and how other functions invoke them to avoid compilation errors.

4. **Function signature compatibility:** Ensure your function signatures match what the registration helpers expect.

5. **Namespace:** Always use `namespace omniruntime::vectorization` for function implementations.

6. **ALWAYS use TaskCreate:** Display a task list at the start and update it as you progress.

7. **ALWAYS await approval at checkpoint:** Stop after design document creation and use AskUserQuestion to get explicit approval before coding.
8. **注册名 = function_name(大小写敏感):** `RegisterFunction(prefix + "name", ...)` 的注册名必须与 OmniAdaptor `RexNodeUtil` 生成的 `function_name` 完全一致(大小写敏感),否则 native 运行时 `jsonparser.cpp:511` 报 `Function not supported`。反例 `char_length`:`RegisterString.cpp` 注册名 `"length"` ≠ SQL `char_length` → not supported(虽有 `CharLengthFunction` 实现,见 `String.h:651`)。

## Verification Checklist

Before considering the implementation complete:

- [ ] Design document created and approved
- [ ] Function implementation follows template structure
- [ ] Registered in the correct `Register*.cpp` file
- [ ] Function called from `Register.cpp` if needed
- [ ] Unit test file exists at `core/test/vectorization/<FunctionName>Test.cpp` (MANDATORY — implementation is incomplete without it; see Constraint #1)
- [ ] Unit tests cover basic cases
- [ ] Unit tests cover edge cases
- [ ] Code follows OmniOperator naming conventions
- [ ] Required headers included

## Troubleshooting

**Issue:** Function not found during registration
- Check that the registration function is called from `Register.cpp`
- Verify namespace is correct

**Issue:** Template compilation errors
- Verify type parameters match the function signature
- Check that data type constants are correct

**Issue:** Missing headers
- Review similar function files for required includes
- Common headers: `util/compiler_util.h`, `vectorization/Status.h`, `type/data_type.h`

## 核心踩坑(提炼自记忆)

- **Type B Expr(自定义 Expr 类)带字符串字面量须注册 VARCHAR+CHAR 全组合**:`VectorFunction::Find` 精确匹配无 CHAR/VARCHAR 转换,`col OP 'literal'` 签名是 `{VARCHAR,CHAR}`,只注册 `{VARCHAR,VARCHAR}` → Find 返回 nullptr → codegen SIGSEGV pc=0x0;Type A FuncExpr 有 row-JIT 兜底不踩此坑。
- **native 字符串按 Unicode 码点计,Flink 按 UTF-16 码元计**:仅增补平面字符(emoji)分歧,BMP 无分歧;引擎级设计非 bug,审计字符串函数勿误判,e2e 黄金数据避免 emoji。
- **LIKE 2-arg 默认 `\` escape 是 Spark 语义,Flink 2-arg 无默认 escape**:预存引擎分歧(非适配 bug),LIKE/NOT LIKE e2e 黄金数据勿含 `\` 转义模式,只测 `%`/`_`/exact/NULL。
