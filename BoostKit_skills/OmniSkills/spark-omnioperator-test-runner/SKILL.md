---
name: spark-omnioperator-test-runner
description: "Execute pytest test scripts via SSH with connection pool. Runs S1 (Native vs Omni comparison) and E2 (execution plan verification) patterns. Sets up core modules, SSH pool, logger, and handles timeout calculation. Use this skill when user mentions 'run tests', 'execute pytest', 'SSH test execution', 'S1 comparison', 'E2 verification'. Trigger ONLY for execution phase, NOT for script generation or reporting."
---

# Omni Spark Test Executor

Execute pytest test scripts via SSH with connection pool.

## Sole Responsibility

**Execute tests and set up execution environment.**

- Set up: `core/` modules, `config/config_loader.py`, virtual environment
- Execute: `pytest tests/ -v` with calculated timeout
- Output: `logs/*.log`, `reports/test_results.json`

**NOT responsible for:**
- Test script generation → use `spark-omnioperator-test-script-generator`
- HTML report generation → use `spark-omnioperator-test-report-generator`

## When to Use

Trigger when user wants to:
- Run/execute pytest tests
- Set up SSH execution environment
- Perform S1/E2 pattern testing

**NOT triggered for:**
- Script generation → use `spark-omnioperator-test-script-generator`
- Report generation → use `spark-omnioperator-test-report-generator`

## Prerequisites

From `spark-omnioperator-test-script-generator`:
- `tests/test_*.py`
- `pytest.ini`
- `test_cases.json`
- `config.json`

## Output Files

Creates:
```
core/
├── ssh_pool.py
├── ssh_executor.py
├── test_runner.py
└── logger.py

config/
└── config_loader.py

logs/
└── test_<case_id>_<timestamp>.log

reports/
└── test_results.json

omni_test_env/
```

## Execution Process

### Setup Environment

```bash
./scripts/setup_venv.sh
source omni_test_env/bin/activate
```

### Copy Core Modules

```bash
cp scripts/ssh_pool_template.py core/ssh_pool.py
cp scripts/ssh_executor_template.py core/ssh_executor.py
cp scripts/test_runner_template.py core/test_runner.py
cp scripts/config_loader_template.py config/config_loader.py
cp scripts/logger_template.py core/logger.py
```

### Calculate Timeout (CRITICAL)

```python
import json
test_count = len(json.load(open('test_cases.json')))
workers = 8
per_test = 1000  # seconds
total_time = (test_count / workers) * per_test
bash_timeout_ms = min(int(total_time * 1.5 * 1000), 900000000)
```

See `references/bash_timeout_calculation.md`.

### Execute

```python
bash(command="pytest tests/ -v", timeout=bash_timeout_ms)
```

## Bash Timeout (CRITICAL)

**NEVER use default 120s timeout.**

| Test Count | Timeout |
|------------|---------|
| 10 | 1800000ms (30 min) |
| 25 | 4500000ms (75 min) |
| 47 | 8812500ms (147 min) |
| 100+ | 900000000ms (cap) |

## Test Patterns

### S1: Native vs Omni Comparison

- Execute SQL on Native Spark
- Execute SQL on Omni Spark
- Compare results row-by-row

Detection: "S1" or "原生和Omni执行"

### E2: Execution Plan Verification

- Execute EXPLAIN
- Check for Omni keywords

Detection: "E2" or "执行计划"

## SSH Connection Pool

Configurable size:
- Env: `export SSH_POOL_SIZE=30`
- pytest.ini: `[ssh] pool_size=30`
- Default: 30

See `references/ssh_pool_architecture.md`.

## Omni Keywords

- `OmniInsertIntoHadoopFsRelationCommand`
- `OmniFilter`, `OmniProject`, `OmniSort`
- `OmniAggregate`, `OmniScan`, `OmniJoin`
- `ColumnarShuffle`, `Gluten`

