---
name: omnioperator-expression-dev
description: Use for OmniOperator expression development. Trigger when implementing new vectorized expressions, functions, or operators in OmniOperator framework. This includes scalar functions, aggregate functions, window functions, variadic functions, bitwise operations, math functions, string functions (like concat, split, substring), or any SQL function implementation. Also trigger when asked to "implement function", "add expression", "create vectorized function", "实现函数", "添加表达式", "编写函数", when working with Register*.cpp registration files, or when user mentions "OmniOperator" with "function/expression/implementation" or "函数/表达式/实现" and specifies function signature, arguments, return type, NULL handling, or vector encoding support.
---

# OmniOperator Expression Development

This skill guides the implementation of new vectorized expressions and functions in the OmniOperator framework. OmniOperator is a vectorized execution engine that follows patterns from Velox (Meta's vectorization framework).

## When This Skill Applies

This skill activates when you need to:
- Implement a new SQL function (math, string, bitwise, array, etc.)
- Add vectorized expression support for OmniOperator
- Create or modify function registration in `Register*.cpp` files
- Write unit tests for expression implementations

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
8. Write unit tests
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
`OmniOperator/docs/expression-design/<function_name>_design.md`

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

#### Step 8: Write Unit Tests

**Task:** "Write unit tests"

**Prerequisite:** Read the design document at `OmniOperator/docs/expression-design/<function_name>_design.md` and implement the test cases specified in the **Test Plan** and **Edge Cases** sections. The design document should have already identified specific test values, boundary conditions, and expected results during the analysis phase.

**Location:** `OmniOperator/core/test/vectorization/<FunctionName>Test.cpp`

**Template:** Use [`references/test_template.cpp`](references/test_template.cpp) as the structural template for includes, namespace declarations, and test patterns, then fill in the specific test cases from the design document:

- **ExprEval path** (most common): Create raw C-array inputs via `CreateVectorBatch()`, build expression tree with `FuncExpr` + `FieldExpr`, evaluate via `ExprEval::Visit()`, verify with `dynamic_cast<Vector<T>*>`.
- **VectorFunction::Apply path** (for precise control): Create vectors via `VectorHelper::CreateFlatVector()`, lookup via `VectorFunction::Find(signature)`, execute via `Apply()` with `std::stack<BaseVector*>`. Useful for NaN/Inf testing and custom vector construction.

**Test coverage should include:**
1. Basic functionality with typical inputs
2. Null input handling
3. Edge cases (min/max values, zero, negative numbers)
4. Type conversion behaviors
5. Invalid inputs (division by zero, negative sqrt, etc.)

#### Step 9: Verification

**Task:** "Verification and completeness check"

Use the Verification Checklist below to ensure completeness.

## Code Style Guidelines

### Naming Conventions
- Function struct: `<FunctionName>Function` (e.g., `SqrtFunction`, `BitCountFunction`)
- Test file: `<FunctionName>Test.cpp` (e.g., `MathFunctionTest.cpp`)
- Registration: `Register<FunctionCategory>Functions()`

### Common Data Types

> For the complete data type constants reference table, see the "Data Type Constants" section in [`references/project_structure.md`](references/project_structure.md).

### Helper Templates Available

> For the complete helper template list with descriptions, see the "Common Helper Templates" section in [`references/project_structure.md`](references/project_structure.md).

## Important Constraints

1. **No test execution:** The development environment lacks Kunpeng hardware. Do NOT attempt to run tests or compile commands. Focus on code implementation only.

2. **Follow existing patterns:** Study similar functions in the codebase before implementing. Consistency is critical.

3. **Header file dependencies:** When calling existing functions, check the function signature and how other functions invoke them to avoid compilation errors.

4. **Function signature compatibility:** Ensure your function signatures match what the registration helpers expect.

5. **Namespace:** Always use `namespace omniruntime::vectorization` for function implementations.

6. **ALWAYS use TaskCreate:** Display a task list at the start and update it as you progress.

7. **ALWAYS await approval at checkpoint:** Stop after design document creation and use AskUserQuestion to get explicit approval before coding.

## Verification Checklist

Before considering the implementation complete:

- [ ] Design document created and approved
- [ ] Function implementation follows template structure
- [ ] Registered in the correct `Register*.cpp` file
- [ ] Function called from `Register.cpp` if needed
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
