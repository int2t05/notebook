# SSH Connection Pool Architecture

## Pool Configuration

SSH pool size is configurable through multiple sources:

1. **Environment variable** (highest priority):
   ```bash
   export SSH_POOL_SIZE=30
   pytest tests/
   ```

2. **pytest.ini configuration**:
   ```ini
   [ssh]
   pool_size = 30
   ```

3. **Default fallback**: 30 connections

## Pool Features

- **Singleton pattern**: Only one pool instance per worker process
- **Thread-safe**: Lock-based synchronization for concurrent access
- **Health checks**: Automatic validation before reuse
- **Connection reuse**: Healthy connections returned to pool
- **Pool statistics**: Logged per test case

## Pool Statistics Logging

Each test case logs pool statistics:
```
SSH Pool Stats: {'pool_size': 5, 'active_connections': 8, 'max_pool_size': 30}
```

## Pool Implementation

Read `scripts/ssh_pool_template.py` for exact implementation.

Key classes:
- `SSHConnectionPool`: Singleton pool with health checks
- `get_ssh_pool()`: Global pool instance getter
- `_load_max_pool_size()`: Configuration loader (env → pytest.ini → default)
- `get_max_pool_size()`: Public accessor for configured pool size

## SSH Background Execution Pattern

For long-running Spark SQL commands, use background execution:

```python
# 1. Generate unique log file
log_file = f"/tmp/omni_test_{uuid.uuid4().hex[:8]}.log"

# 2. Create background command
bg_command = f"source /etc/profile &>/dev/null; nohup {spark_command} -e \"{sql_statements}\" > {log_file} 2>&1 & echo $! > {pid_file}"

# 3. Execute via SSH pool (with retry logic)
stdin, stdout, stderr = self._retry_operation(
    lambda: self.client.exec_command(bg_command, timeout=30),
    max_retries=2,
    operation_name="Background command execution"
)

# 4. Poll for completion (check process + read log)
# 5. Get return code and output
# 6. Cleanup temp files
```

## Pool Configuration Examples

### Example 1: Environment Variable

```bash
export SSH_POOL_SIZE=50
pytest tests/ -n 16  # 16 workers, pool size 50
```

### Example 2: pytest.ini

```ini
[pytest]
addopts = -v --json-report --json-report-file=reports/test_results.json -n 16 --dist=loadscope --maxfail=50

[ssh]
pool_size = 50
```

### Example 3: Custom Pool Size in Code

```python
from core.ssh_pool import get_ssh_pool

# Override pool size
pool = get_ssh_pool(server_config, max_pool_size=50)
```

## Troubleshooting

### SSH Pool Not Working

Check pool configuration:
```bash
# Check environment variable
echo $SSH_POOL_SIZE

# Check pytest.ini
cat pytest.ini | grep pool_size

# Check Python logs
grep "SSH_POOL" logs/*.log
```

### Pool Statistics Missing

Verify pool integration:
```python
# In ssh_executor.py, check pool initialization
if self.use_pool:
    self.ssh_pool = get_ssh_pool({...})
```

### SSH pool exhaustion

If pool full error occurs:
- Increase pool size: `export SSH_POOL_SIZE=50` or edit pytest.ini `[ssh] pool_size=50`
- Reduce parallelism: `pytest tests/ -n 4` (fewer workers)