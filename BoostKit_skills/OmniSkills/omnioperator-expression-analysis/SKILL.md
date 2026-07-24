---
name: omnioperator-expression-analysis
description: Full-repo scan of Velox / Spark SQL / OmniOperator expression support status, generating an ecosystem benchmark report. Triggers: expression coverage research, competitive analysis, Omni missing expression inventory, type matrix analysis.
---

# Expression Ecosystem Status Analysis Skill

## Objective

Systematically scan three sources and produce `OmniOperator/docs/expression-analysis/expression_analysis_report_<yyyymmdd>.md` answering:
1. Which expressions has Omni implemented (both codegen and vectorization), and what types does each support?
2. Which Spark SQL expressions does Velox (industry reference) cover?
3. How many expressions does the Spark SQL standard expose, and in what categories?
4. What is the gap between Omni and Velox / Spark SQL standard, and how should it be prioritized?

---

## Expression Data Flow

An expression travels through these layers from Spark to Omni execution:

```
Spark SQL standard expression catalog
        ↓  (Gluten maps Spark → Substrait)
ExpressionMappings.scala          ← which expressions Gluten attempts to push down
ExpressionTransformer.scala      ← Omni-specific transformations (timezone, seed, etc.)
OmniExpressionAdaptor.scala      ← Scala-layer runtime validation (whitelist, type checks)
        ↓  (pass → generate Substrait plan)
SubstraitToOmniPlan.cpp           ← C++ bridge: Substrait expression → Omni plan
        ↓  (Omni execution)
OmniOperator execution layer
  ├── vectorization/              ← ExprEval visitor + VectorFunction dispatch (SIMD)
  └── codegen/                    ← LLVM JIT compilation (native machine code)
```

Upstream reference:
```
velox/velox/functions/sparksql/   ← Velox Spark SQL expressions (industry baseline)
```

---

## Key Methodology

**Do not estimate coverage by file count.** One `Register*.cpp` may register dozens of expression names (each with multiple type overloads), while one `.h` file may correspond to only one expression. The only reliable data source is the `registration/` directory — extract actual `RegisterFunction` calls.

**Type coverage is determined by registration helpers.** `RegistrationHelpers.h` defines template helpers that batch-register type combinations. Whether a helper like `RegisterUnaryDecimal` is called determines if DECIMAL is supported:

| Helper | Covered Types |
|--------|--------------|
| `RegisterUnaryIntegralNumeric<T>` | BYTE / SHORT / INT / LONG |
| `RegisterUnaryFloatingPoint<T>` | FLOAT / DOUBLE |
| `RegisterUnaryDecimal<T>` | DECIMAL64 / DECIMAL128 |
| `RegisterUnaryNumeric<T>` | All three above combined |
| `RegisterRoundNumericWithScale<T>` | BYTE/SHORT/INT/LONG/FLOAT/DOUBLE (excludes DECIMAL) |

**Use global grep to confirm registration.** To verify whether a specific expression is registered:
```bash
grep -r '"func_name"' OmniOperator/core/src/vectorization/registration/
```
No match = confirmed not registered.

---

## Step 1: Set Up Output Directory

```bash
mkdir -p OmniOperator/docs/expression-analysis
REPORT=OmniOperator/docs/expression-analysis/expression_analysis_report_$(date +%Y%m%d).md
```

---

## Step 2: Scan Omni Execution Layer

OmniOperator has two expression execution frameworks. Scan both to get complete coverage.

### 2a. Vectorization Framework (SIMD-based, ExprEval dispatch)

**Primary source**: `OmniOperator/core/src/vectorization/registration/`

This directory contains 18 `Register*.cpp` files, each binding a category of functions into the runtime registry.

```bash
ls OmniOperator/core/src/vectorization/registration/Register*.cpp
```

Read each `RegisterXxx.cpp` and extract `RegisterFunction<...>(prefix + "func_name", ...)` calls.

**To confirm whether a specific expression is registered, use global grep** (not file-by-file reading):
```bash
grep -r '"func_name"' OmniOperator/core/src/vectorization/registration/
```

**Check ExprEval dispatch completeness** — read `OmniOperator/core/src/vectorization/ExprEval.cpp` and find expression names in the `FuncExpr` dispatch block. This catches "registered but ExprEval has no dispatch entry" (incomplete wiring).

### 2b. Codegen Framework (LLVM JIT)

**Source**: `OmniOperator/core/src/codegen/func_registry_*.cpp`

The codegen framework has its own function registrations separate from vectorization. Scan these files to find expressions registered only in the JIT path:

```bash
ls OmniOperator/core/src/codegen/func_registry_*.cpp
```

Read each file and extract registered function names and type signatures. Note which expressions are:
- Only in codegen (not in vectorization)
- Only in vectorization (not in codegen)
- In both frameworks

### 2c. Aggregate Expressions

Read `OmniOperator/core/src/vectorization/aggregator_factory.cpp` (or similar path) for aggregate expression type variants. Aggregate expressions follow a separate dispatch path from scalar expressions.

---

## Step 3: Scan Gluten Mapping Layer

This layer determines which Spark expressions are mapped to Omni, and what runtime restrictions apply.

### 3a. Expression Pushdown Intent

**File**: `Gluten/gluten-substrait/src/main/scala/org/apache/gluten/expression/ExpressionMappings.scala`

This is the authoritative complete set of expressions Gluten attempts to push down. Three categories:

| Type | Variable | Content |
|------|----------|---------|
| Scalar | `SCALAR_SIGS` | ~270 entries |
| Aggregate | `AGGREGATE_SIGS` | ~35 entries |
| Window | `WINDOW_SIGS` | ~9 entries |

Extract: grep all `Sig[ClassName](FUNCTION_NAME)` lines, organize by category.

### 3b. Omni-Specific Expression Transforms

**File**: `Gluten/backends-omni/src/main/scala/org/apache/gluten/expression/ExpressionTransformer.scala`

Contains Omni-specific transformers that inject extra parameters (timezone, seed, etc.) into the Substrait output. Check what transformations are applied and to which expressions.

### 3c. Runtime Restrictions (Scala Layer)

**File**: `Gluten/backends-omni/src/main/scala/org/apache/gluten/expression/OmniExpressionAdaptor.scala`

This file validates expressions at runtime. Extract:
- Whitelist-based expression validation logic
- Type restrictions (e.g. `greatest` limited to 2 parameters, `concat` only STRING type)
- Timezone/format restrictions (e.g. `unix_timestamp`/`from_unixtime` limited to GMT+08:00/Asia/Shanghai)

These restrictions cause "expression is registered but falls back for specific types at runtime."

### 3d. Substrait → Omni Bridge

```bash
grep -n "scalar_function\|functionName\|\"spark:" \
  Gluten/cpp-omni/src/substrait/SubstraitToOmniPlan.cpp | head -100
```

Check which Substrait-level expressions are wired to Omni implementations.

---

## Step 4: Scan Velox Reference Baseline

Velox is Meta's vectorized execution engine and the industry reference for Spark SQL expression support.

**Path**: `velox/velox/functions/sparksql/registration/`

```bash
ls velox/velox/functions/sparksql/registration/Register*.cpp
```

Read each `Register*.cpp` and extract:
- `registerFunction<FuncName, ReturnType, ArgTypes...>({"func_name"})` — type signature
- `registerVectorFunction("func_name", signatures, ...)` — vector expression
- Template parameters indicate supported types

Key files: `RegisterMath.cpp`, `RegisterString.cpp`, `RegisterDateTime.cpp`, `RegisterArray.cpp`, `RegisterCollection.cpp`, `RegisterMap.cpp`, `RegisterHash.cpp`, `RegisterConversion.cpp`, `RegisterComparison.cpp`, `Register.cpp` (top-level entry).

---

## Step 5: Spark SQL Standard Expression Catalog

If `spark/` exists locally:
```bash
grep -r "class \w\+\s\+extends.*Expression\|FunctionRegistration" \
  spark/sql/catalyst/src/main/scala/ --include="*.scala" -l | head -20
```

Otherwise, use the known standard categories as a reference framework:

| Category | Representative Expressions | Approx. Count |
|----------|---------------------------|---------------|
| Math | abs, ceil, floor, sqrt, pow, log, round, rand... | ~40 |
| String | concat, substr, trim, replace, like, regexp_extract... | ~60 |
| Datetime | year, month, day, date_add, datediff, trunc, to_date... | ~50 |
| Conditional | if, case when, coalesce, nullif, nvl, greatest, least | ~10 |
| Aggregate | sum, avg, count, min, max, stddev, percentile... | ~30 |
| Window | rank, dense_rank, row_number, lead, lag, ntile... | ~10 |
| Collection | array_contains, size, sort_array, map_keys, explode... | ~60 |
| Hash / Crypto | md5, sha1, sha2, crc32, murmur3, xxhash64 | ~10 |
| JSON | get_json_object, from_json, to_json, json_tuple | ~6 |
| Type conversion | cast, try_cast | ~5 |
| Misc | version, spark_partition_id, stack, raise_error... | ~10 |

---

## Step 6: Build Comparison & Gap Analysis

### 6.1 Three-Way Expression Comparison

For each expression, mark its status across all sources:

| Expression | Spark SQL Std | Gluten Mapping | Velox Impl | Omni Impl | Notes |
|------------|:------------:|:--------------:|:----------:|:---------:|-------|

Fill-in rules:
- **Omni Impl**: Step 2 scan results (note codegen vs vectorization)
- **Gluten Mapping**: Step 3a results
- **Velox Impl**: Step 4 scan results

### 6.2 Type Coverage Matrix

For expressions with type coverage gaps, list explicitly:

| Expression | INT | LONG | FLOAT | DOUBLE | DECIMAL | STRING | DATE | TIMESTAMP | ARRAY | MAP |
|------------|-----|------|-------|--------|---------|--------|------|-----------|-------|-----|

### 6.3 Gap Priority Analysis

#### 🔴 High Priority — Gluten-mapped but Omni has no implementation
#### 🟡 Medium Priority — Implemented but specific conditions cause runtime fallback
#### 🟢 Low Priority — Not mapped by Gluten (Spark has it but doesn't attempt pushdown)

---

## Step 7: Generate Report

Write the report to `$REPORT` using the language the user communicates in. Follow this structure:

```markdown
# OmniOperator Expression Ecosystem Analysis Report
Generated: <date>
Scan branch: <branch> (OmniOperator / Gluten / Velox versions)
Commit: <short_commit_hash> (OmniOperator) / <short_commit_hash> (Gluten) / <short_commit_hash> (Velox)

## 1. Executive Summary
| Metric | Count | Data Source |
|--------|-------|-------------|
| Spark SQL standard expression count | ~XXX | Spark SQL standard |
| Expressions Gluten attempts to push down (scalar / aggregate / window) | XXX / XXX / XXX | ExpressionMappings.SCALAR/AGGREGATE/WINDOW_SIGS |
| Omni vectorized registered expressions (unique names) | XXX | vectorization/registration/*.cpp |
| Omni codegen registered expressions | XXX | codegen/func_registry_*.cpp |
| Omni vectorized total signatures (incl. type overloads) | XXX | Same |
| Omni aggregate expression type variants | XXX | aggregator_factory.cpp |
| Velox SparkSQL implemented expressions | XXX | velox/.../Register*.cpp |

Key conclusions (3-5 bullets highlighting the most important findings).

## 2. Scan Methodology
(Describe data sources — Omni execution layer, Gluten mapping layer, Velox reference layer)

## 3. Velox vs Omni Three-way Comparison
### 3.1 Velox Implemented Expressions (measured, by category)
### 3.2 Three-way Comparison Matrix (key difference expressions)

| Expression | Spark SQL | Gluten Mapping | Velox Impl | Omni Registered | Notes |
|------------|:---------:|:--------------:|:----------:|:---------------:|-------|

## 4. Gap Analysis
### 4.1 🔴 High Priority (Gluten-mapped but Omni has no implementation)
### 4.2 🟡 Medium Priority (implemented but specific conditions cause runtime fallback)
### 4.3 🟢 Low Priority (not mapped by Gluten — Spark has it but doesn't attempt pushdown)

## 5. Type Coverage Matrix
### 5.1 Scalar Expressions (vectorization framework, measured)
### 5.2 Aggregate Expressions (aggregator_factory, measured)

## 6. Priority Suggestions
### 6.1 High-value Fixes (impact production correctness)
### 6.2 Coverage Extensions (Velox has, Omni pending)
```

---

## Caveats

1. **File exists ≠ fully supported**: a `vectorization/functions/Foo.h` file does not mean the `ExprEval.cpp` dispatch chain is wired, nor that `SubstraitToOmniPlan.cpp` handles the corresponding Substrait function name
2. **Gluten mapping ≠ Omni implemented**: `ExpressionMappings.scala` maps expressions to Substrait, but the C++ layer may have no corresponding conversion, causing runtime fallback
3. **Type restrictions may be runtime**: type checks in `OmniExpressionAdaptor.scala` throw `UnsupportedOperationException` at runtime
4. **Two frameworks, different coverage**: codegen and vectorization register expressions independently — an expression may exist in one but not the other
5. **Helper function call chain determines type coverage**: whether helpers like `RegisterUnaryDecimal` in `RegistrationHelpers.h` are actually called decides whether an expression supports DECIMAL — trace the full call chain
