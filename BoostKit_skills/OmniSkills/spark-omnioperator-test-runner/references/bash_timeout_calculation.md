# Bash Tool Timeout Calculation (CRITICAL - Prevents Test Interruption)

## Critical Issue

pytest was interrupted by bash tool timeout, causing incomplete test execution. This is the #1 cause of test suite failures.

## Problem Analysis

When executing pytest via bash tool:
- **Default bash timeout**: 120s (2 minutes) - **INSUFFICIENT**
- **Actual pytest time**: 47 tests × ~2 min/test = ~94 minutes
- **Result**: pytest interrupted at ~10 min mark, tests skipped, incomplete HTML report

## Timeout Calculation Formula

**MUST calculate bash timeout BEFORE executing pytest:**

```python
# Step 1: Count test cases
import json
test_cases = json.load(open('test_cases.json'))
test_count = len(test_cases)  # Example: 47

# Step 2: Estimate per-test time
# S1 pattern: Native(400s) + Omni(400s) + E2(90s) + overhead(100s) = 990s
# Simplified: ~1000s per test (with safety buffer)
per_test_time_seconds = 1000

# Step 3: Account for parallel workers
workers = 8  # Default from pytest.ini
tests_per_worker = test_count / workers

# Step 4: Calculate total pytest time
total_pytest_time = tests_per_worker * per_test_time_seconds
# Example: (47/8) × 1000 = 5875s (~97 minutes)

# Step 5: Calculate bash timeout (with 50% safety buffer)
bash_timeout_ms = min(
    int(total_pytest_time * 1.5 * 1000),  # 50% buffer
    900000000  # Maximum: 15 minutes cap
)
# Example: 5875 × 1.5 × 1000 = 8812500ms (~147 minutes)
# Cap to 900000000ms (15 min) for extreme cases
```

## Concrete Timeout Values

| Test Count | Workers | Tests/Worker | Time/Worker | Bash Timeout |
|------------|---------|--------------|-------------|--------------|
| 10 tests | 8 | 1.25 | ~20 min | **1800000ms** (30 min) |
| 25 tests | 8 | 3.125 | ~50 min | **4500000ms** (75 min) |
| 47 tests | 8 | 5.875 | ~97 min | **8812500ms** (147 min) |
| 100+ tests | 8 | 12.5+ | ~200 min+ | **900000000ms** (15 min cap) |

## Execution Pattern (MANDATORY)

**When skill executes pytest via bash tool, MUST:**

1. **Read test_cases.json and count tests**
2. **Calculate bash timeout using formula above**
3. **Execute pytest with calculated timeout parameter**

**Example execution:**

```python
# User request: "Run pytest for Omni Spark tests"

# Step 1: Count test cases
import json
test_count = len(json.load(open('C:/bigdata_test/test_cases.json')))

# Step 2: Calculate timeout
workers = 8
per_test = 1000  # seconds
total_time = (test_count / workers) * per_test
bash_timeout_ms = min(int(total_time * 1.5 * 1000), 900000000)

# Step 3: Execute pytest with timeout
bash_command = f"""
cd C:/bigdata_test
python -m pytest tests/ -v --html=reports/test.html --self-contained-html -n 8 --maxfail=50
"""

# CRITICAL: Pass timeout parameter to bash tool
result = bash(
    command=bash_command,
    description="Execute pytest test suite",
    timeout=bash_timeout_ms  # Example: 8812500 for 47 tests
)
```

## Anti-Pattern (CAUSES FAILURE)

```python
# WRONG: No timeout calculation
bash(command="pytest tests/", description="Run tests")
# Result: Default timeout 120s → pytest interrupted → incomplete tests

# WRONG: Fixed timeout regardless of test count
bash(command="pytest tests/", timeout=600000)
# Result: 47 tests need ~97 min → interrupted at 10 min → 80% tests skipped

# WRONG: Assuming short tests
bash(command="pytest tests/", timeout=300000)
# Result: Spark SQL operations take ~2 min/test → catastrophic failure
```

## Timeout Safety Rules

1. **NEVER use default bash timeout (120s)** - guaranteed interruption
2. **ALWAYS calculate based on test_count** - different projects have different sizes
3. **ALWAYS add 50% buffer** - accounts for network delays, Spark startup, retries
4. **ALWAYS cap to 900000000ms max** - prevents extreme timeout values
5. **NEVER estimate without test_count** - "probably takes X minutes" = failure

## Why This Matters

- **pytest-html requires complete exit**: Interrupted pytest → empty "tests: {}" → no report
- **Test skipping = false negatives**: Passed tests skipped → looks like failed suite
- **User frustration**: Partial execution violates "complete test execution" requirement
- **Time waste**: Re-running takes 90+ minutes, interruption wastes partial work