# Performance Optimization Tips

## Pool Size Tuning

Set pool_size >= worker_count * 3:
- 8 workers → pool_size=30 (default)
- 16 workers → pool_size=50
- 32 workers → pool_size=100

## Worker Count

- `-n 8` good for most cases
- Increase for large test suites (e.g., `-n 16`)
- Decrease for slow networks (e.g., `-n 4`)

## Timeout Tuning

Increase `timeout = 1200` in pytest.ini for long SQL queries:
- Normal: 1200s (20 min)
- Heavy queries: 1800s (30 min)
- Very slow network: 2400s (40 min)

## Retry Logic

3 retries with exponential backoff handles transient failures:
- Retry 1: 1s delay
- Retry 2: 2s delay  
- Retry 3: 4s delay

## Load Distribution

`--dist=loadscope` groups tests by file for efficiency:
- Tests in same file execute on same worker
- Reduces config loading overhead
- Improves cache locality

## Bash Timeout Calculation

**CRITICAL**: Always calculate bash timeout before pytest execution.
See `references/bash_timeout_calculation.md` for formula.