# Timeout Configuration (Critical for Complete Test Execution)

## Problem Statement

Before optimization:
- pytest.ini timeout=600s (10 min per test)
- S1 pattern requires Native(300s) + Omni(300s) = 600s minimum
- **pytest timeout equals S1 minimum → any delay causes timeout → tests skipped**

## Timeout Hierarchy

```
pytest.ini timeout (全局test timeout)
    ↓ 必须覆盖 (must cover)
config.json timeout_seconds (单次SQL timeout)
    ↓ 必须覆盖 (must cover)
test_runner per-step timeout (步骤级)
    ↓ 必须覆盖 (must cover)
ssh_executor timeout (命令级)
```

## Optimized Timeout Values

| Layer | Setting | Value | Rationale |
|-------|---------|-------|-----------|
| pytest.ini | `timeout` | **1200s (20 min)** | Covers S1(800s) + E2(90s) + buffer(310s) |
| config.json | `timeout_seconds` | **400s** | Per SQL execution (increased from 300s) |
| test_runner S1 | per execution | **400s** | Native + Omni = 800s total per step |
| test_runner E2 | EXPLAIN timeout | **90s** | EXPLAIN operations faster than data queries |
| test_runner Generic | per execution | **400s** | Single SQL execution |
| ssh_executor | default timeout | **400s** | Background execution timeout |

## Timeout Calculation

**S1 step time calculation:**
```
Native Spark execution: 400s
Omni Spark execution: 400s
Total S1 minimum: 800s
```

**pytest timeout calculation:**
```
S1 step: 800s
E2 step: 90s
Buffer (Spark startup + network + retry): 310s
pytest timeout = 800s + 90s + 310s = 1200s
```

## Timeout Configuration Files

**pytest.ini:**
```ini
[pytest]
timeout = 1200  # 20 min to cover S1+ E2 + buffer
```

**config.json:**
```json
{
  "test_config": {
    "timeout_seconds": 400  # Increased from 300s
  }
}
```

**test_runner.py:**
```python
# S1 timeout: 400s per execution (Native + Omni = 800s)
timeout = 400

# E2 timeout: 90s for EXPLAIN
timeout = 90

# Generic timeout: 400s for single SQL
timeout = 400
```

## Timeout Best Practices

1. **pytest timeout ≥ max test time + buffer**: Ensure pytest timeout covers worst-case test
2. **Per-step timeout strategy**: Different timeout values for S1/E2/Generic steps
3. **Buffer for delays**: Include Spark startup time, network delay, retry time
4. **Monitor actual execution time**: Check logs/ to verify timeout values are appropriate
5. **Adjust per environment**: Increase timeout for slow networks or heavy cluster load

## Timeout Troubleshooting

**Symptom: Tests being skipped**

Check pytest timeout in pytest.ini:
```bash
grep timeout pytest.ini
# Should show: timeout = 1200
```

**Symptom: SQL execution timeout**

Check config.json timeout_seconds:
```bash
grep timeout_seconds config.json
# Should show: "timeout_seconds": 400
```

**Symptom: E2 EXPLAIN timeout**

Check test_runner.py E2 timeout:
```python
# Should show: timeout=90 in _execute_e2_step
```

**Symptom: Still seeing timeouts**

Increase timeout values further:
- pytest.ini: `timeout = 1800` (30 min)
- config.json: `"timeout_seconds": 600` (10 min per SQL)
- test_runner: S1 timeout=600s per execution