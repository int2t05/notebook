---
name: omnioperator-status-analysis
description: Full-repo scan of Spark SQL / Gluten / OmniOperator / Velox physical operator support status, generating an ecosystem benchmark report. Triggers: operator coverage research, Omni missing operator inventory, Spark physical operator pushdown status, Gluten fallback analysis, Substrait Rel to Omni PlanNode mapping matrix, operator type/config support matrix, competitive analysis vs Velox. Use this skill when the user asks "which operators are currently supported", "which operators are missing", "operator status analysis", "operator coverage", "fallback inventory".
---

# Operator Ecosystem Status Analysis Skill

## Objective

Systematically scan four code repositories and produce `OmniOperator/docs/operator-status/operator_status_report_<yyyymmdd>.md` answering:

1. Which Spark physical operators does Omni currently support?
2. Which operators are declared supported in Gluten but incomplete on the Omni execution side?
3. Which operators have Omni backend implementations but Gluten does not push down?
4. What are the main sources of fallback — which operators or type restrictions?
5. Compared to Velox, what operator capabilities is Omni missing?
6. Which operators should be prioritized for the next development phase?

This skill does status analysis only. If the user requests development or testing of a specific operator, switch to the corresponding operator development / design skill after analysis is complete.

---

## Key Methodology

**Do not estimate coverage by file count.** Only when the full chain exists and there is no evidence of fallback / unsupported can an operator be judged as fully supported. Every significant conclusion must include file paths and brief evidence showing which layer supports or is missing.

**Mark uncertain conclusions as "pending verification".** List the E2E SQL or source locations needed to confirm. If a layer's source is missing or unverified, use "pending verification" — never assume "supported".

**Expression gaps are not operator gaps.** If an operator is fully supported but a specific expression within it causes fallback, classify that under the omnioperator-expression-analysis skill, not here.

**Prefer `rg` for scanning.** Use `rg` / `rg --files` as the primary tool. Fall back to `grep` or PowerShell equivalents only if `rg` is unavailable.

---

## Step 1: Set Up Output Directory

```bash
mkdir -p OmniOperator/docs/operator-status
REPORT=OmniOperator/docs/operator-status/operator_status_report_$(date +%Y%m%d).md
```

---

## Step 2: Build Spark Physical Operator Candidate Set

Identify the full set of Spark physical operators that could potentially be pushed down.

**Path**: `spark/sql/core/src/main/scala/org/apache/spark/sql/execution/`

```bash
find spark/sql/core/src/main/scala/org/apache/spark/sql/execution/ -name "*Exec*.scala" | sort
```

Extract operator names from class definitions (e.g. `SortExec`, `HashAggregateExec`, `BroadcastHashJoinExec`). This forms the target universe — every other layer is measured against this set.

For each operator, also record:
- Minimal SQL that triggers the physical node
- Whether it is affected by Spark config (e.g. AQE, broadcast threshold, join preference, aggregate strategy)

If `spark/` is not available locally, reconstruct the candidate set from Gluten Transformer files (next step) and note "local Spark repo missing, candidate set inferred from Gluten".

---

## Step 3: Scan Gluten Layer

This layer determines which operators Gluten attempts to push down to Omni, and what runtime restrictions apply.

### 3.1 Backend Support Declaration

**File**: Search for `OmniBackend.scala` in the Gluten repo.

```bash
rg -l "OmniBackend" Gluten/ --type scala
rg -n "support.*Exec" Gluten/ --type scala
```

Extract: which Spark physical operators are declared as supported by the Omni backend. Operators not listed here will never reach Omni even if Omni has an implementation.

### 3.2 Plan Transformer

**File**: Search for `OmniSparkPlanExecApi.scala` and related transformer files.

```bash
rg -l "SparkPlanExecApi\|transform.*Exec" Gluten/ --type scala
rg -n "gen.*ExecTransformer" Gluten/ --type scala
rg -n "ExecTransformer" Gluten/ --type scala
```

Extract: which operators have Substrait transformation logic. Check for:
- Operators that have a dedicated transformer (full Substrait conversion)
- Operators that are only partially transformed (some variants handled, others fall back)
- Operators with no transformer (Gluten never generates Substrait for them)

For each operator, also record:
- Whether `supportXxxExec()` explicitly returns `true`
- Whether `genXxxExecTransformer()` returns a non-null Transformer
- Whether the Transformer class exists and inherits `TransformSupport` / `ValidatablePlan`
- Whether there are config switches (default enabled? `.internal()` preventing runtime override?)
- Whether there are explicit fallbacks, type filters, join type filters, or aggregate mode filters

Also identify Gluten's generic Substrait operator converters in `Gluten/gluten-substrait/src/main/scala/org/apache/gluten/execution/`. Cross-reference with Omni-specific transformers to find operators that rely on generic conversion vs custom Omni paths.

---

## Step 4: Scan cpp-omni Validator and Converter

These C++ files are the bridge between Substrait and Omni execution. They determine whether a Substrait plan is accepted and how it maps to Omni PlanNodes.

Record all findings in the Summary Table at the end of this step.

### 4.1 Validator

**File**: `Gluten/cpp-omni/src/substrait/SubstraitToOmniPlanValidator.cpp`

```bash
rg "validateRel|case.*Rel|::validate" Gluten/cpp-omni/src/substrait/SubstraitToOmniPlanValidator.cpp -n
```

For each Rel type, extract:
1. **Accept/reject logic**: `return true`/`false`, `GLUTEN_CHECK`, `throw`, error messages
2. **Type restrictions**: allowed/rejected data types
3. **Join type restrictions**: accepted join types for JoinRel/CrossRel
4. **Aggregate mode restrictions**: accepted phases for AggregateRel
5. **Window frame restrictions**: accepted frame types for WindowRel
6. **Sort direction/null ordering**: for SortRel
7. **Emit fields**: does the validator check `emit` or `outputMapping`?

**Critical check**: Validator rejects but Gluten still generates the Rel → runtime fallback.

### 4.2 Converter

**File**: `Gluten/cpp-omni/src/substrait/SubstraitToOmniPlan.cpp`

```bash
rg "case.*Rel|make.*Node|PlanNode" Gluten/cpp-omni/src/substrait/SubstraitToOmniPlan.cpp -n
```

For each Rel type, extract:
1. **Target PlanNode**: which Omni PlanNode is created?
2. **Conversion logic**: fields mapped from Rel to PlanNode properties
3. **Missing mappings**: Rel fields ignored or not mapped
4. **Error handling**: does converter throw or return null for certain variants?

### 4.3 Cross-reference

After scanning both files, check for contradictions:
- **Validator accepts but Converter missing** → fails at conversion time
- **Converter supports but Validator rejects** → potential unnecessary fallbacks
- **Inconsistent restrictions** → runtime error risk

### 4.4 Summary Table

Produce a summary table for all Rel types:

```
| Substrait Rel | Validator | Converter | Omni PlanNode | Status | Notes |
```

Status: ✅ Both pass | ⚠️ Partial (with restrictions) | ❌ Blocked | ❓ Unverified

---

## Step 5: Scan Omni Execution Layer

This is the primary source of truth for what Omni can actually execute.

### 5.1 PlanNode Definitions

**Path**: Search for `plannode/` in OmniOperator.

```bash
find OmniOperator/ -path "*/plannode/*.h" -o -path "*/plannode/*.cpp"
```

Extract: the set of defined PlanNode types. Each PlanNode represents an operator that Omni's plan layer recognizes.

### 5.2 Local Planner Dispatch

**File**: `OmniOperator/core/src/compute/local_planner.cpp` (or similar path)

```bash
rg "case.*Node|registerOperator|createOperator" OmniOperator/ --type cpp -g "*planner*"
```

Extract: which PlanNodes are wired to actual Operator factories. A PlanNode without a dispatch entry means it is defined but not executable.

### 5.3 Operator Implementations

**Path**: Search for `operator/` in OmniOperator.

```bash
find OmniOperator/ -path "*/operator/*.h" -o -path "*/operator/*.cpp"
```

Extract: concrete operator implementations. Cross-reference with local planner to confirm which operators have both plan dispatch and runtime implementation.

For each operator, also record:
- Whether the Operator has real execution logic (not empty implementation, `throw`, or TODO)
- Whether type dispatch is complete: key type, payload type, decimal, date/timestamp, string, complex types
- Potential runtime risks: memory limits, spill, sort stability, multi-batch, empty input, NULL behavior

### 5.4 Aggregate and Window Function Support

**File**: `OmniOperator/core/src/operator/util/function_type.h`

```bash
rg "OMNI_AGGREGATION_TYPE|OMNI_WINDOW_TYPE" OmniOperator/core/src/operator/util/function_type.h -n
```

Extract all supported aggregate function types and window function types. These define what functions the Omni execution layer can handle within Aggregate/Window operators.

**File**: `OmniOperator/core/src/operator/aggregation/aggregator/aggregator_factory.cpp`

```bash
rg "AggregatorFactory|case.*AGGREGATION_TYPE" OmniOperator/core/src/operator/aggregation/aggregator/aggregator_factory.cpp -n
```

Extract: which aggregate functions have actual factory implementations. A function type defined in `function_type.h` without a corresponding factory is not executable.

Record findings:

```
| Function Type | Category | Factory Implemented | Evidence |
|---------------|----------|---------------------|----------|
| OMNI_AGGREGATION_TYPE_SUM | Aggregate | ✅ | SumAggregatorFactory |
| OMNI_WINDOW_TYPE_ROW_NUMBER | Window | ✅ | ... |
```

---

## Step 6: Scan Velox Reference Baseline

Velox is Meta's vectorized execution engine and the industry reference for operator support. Note: Velox itself has no Substrait layer — the Substrait-to-Velox conversion lives in Gluten.

**Substrait conversion**: `Gluten/cpp/velox/substrait/SubstraitToVeloxPlan.cc`

```bash
rg "Rel|PlanNode|make.*Node" Gluten/cpp/velox/substrait/SubstraitToVeloxPlan.cc
```

**Velox PlanNode definitions**: `velox/velox/core/PlanNode.h`

```bash
rg "class.*Node\b" velox/velox/core/PlanNode.h
```

**Velox Operator implementations**: `velox/velox/exec/`

```bash
rg "class.*Operator\b" velox/velox/exec/ --type cpp -l
```

Extract: which operator types Velox supports via Substrait. This is the competitive baseline — operators Velox has but Omni doesn't represent capability gaps.

For each operator, also record:
- Velox limitations on join type, aggregate function, window frame, sort null ordering, limit/fetch, set operation
- Which gaps Velox covers but Omni does not

---

## Step 7: Determine Status and Generate Report

### Quality Gates (MANDATORY)

Read `references/pitfalls-and-boundaries.md` before classifying status:

```bash
cat references/pitfalls-and-boundaries.md
```

**During classification** — apply "常见误判" as a filter:
- Do NOT mark "fully supported" just because a Transformer class exists
- Do NOT mark "fully supported" just because `supportXxxExec = true`
- Do NOT mark "fully supported" just because OmniOperator has an Operator
- Do NOT classify expression gaps as operator gaps

**Before writing report** — verify "交付前自检":
1. Every "fully supported" conclusion traces to complete chain evidence
2. Every "partially supported" states restriction dimension (type, join type, aggregate mode, window frame, etc.)
3. Unscanned repos or remote verification gaps are noted in "扫描范围"
4. All Top Gaps include severity, fix complexity, and suggested follow-up skill
5. No expression gaps are classified as operator gaps

### Status Classification

For each operator, classify into one of these states based on evidence collected across all layers:

| Status | Meaning | Evidence Required |
|--------|---------|-------------------|
| **Fully supported** | Complete chain from Gluten to Omni execution | All layers present, no fallback evidence |
| **Partially supported** | Main path works but specific variants/types fall back | Some sub-cases show unsupported/fallback |
| **Frontend only** | Gluten declares support but Omni execution is incomplete | Gluten layer present, Omni execution missing or incomplete |
| **Backend only** | Omni has implementation but Gluten does not push down | Omni execution present, Gluten mapping missing |
| **Not supported** | No support at any layer | No evidence in any layer |
| **Pending verification** | Evidence is ambiguous or source is missing | Cannot confirm from static scan alone |

Only write "fully supported" when the complete chain exists with no fallback/unsupported evidence.

### E2E Sampling (Optional)

If static conclusions are disputed or critical operators claim full support, perform E2E SQL sampling:
1. Use Spark side to confirm the SQL physical plan shows the target `XxxExec` (via `EXPLAIN`).
2. Use Omni side to confirm the plan shows `XxxExecTransformer` and `fallback_warnings` is empty.
3. SQL must trigger the target physical node — do not substitute semantically similar SQL that takes a different physical path.

If no remote test environment is available, the report can be based on static scan only, but must note "E2E verification not performed".

### Report Output

Write the report to `$REPORT`. Read `references/report-template.md` before writing for the standard report structure.
