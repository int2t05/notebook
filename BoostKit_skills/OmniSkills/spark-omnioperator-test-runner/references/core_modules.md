# Core Modules Reference

## ssh_pool.py

Thread-safe singleton SSH connection pool with health checks. See `scripts/ssh_pool_template.py`.

Key methods:
- `_load_max_pool_size()`: Load pool size from env/pytest.ini
- `get_max_pool_size()`: Public accessor for configured pool size
- `SSHConnectionPool.acquire(timeout)`: Acquire connection from pool
- `SSHConnectionPool.release(client)`: Return connection to pool
- `SSHConnectionPool.get_stats()`: Get pool statistics

**Important**: Add `__test__ = False` to prevent pytest collection.

## ssh_executor.py

SSH-based remote execution with retry logic. See `scripts/ssh_executor_template.py`.

Key classes:
- `SSHExecutor`: Connection + background/direct execution + retry logic
- `ResultExtractor`: Filter logs, extract query results
- `ResultComparator`: Row-by-row comparison
- `ExecutionPlanChecker`: Omni keyword detection

Key methods:
- `connect()`: Establish SSH connection (pool or direct)
- `_retry_operation()`: Execute with exponential backoff retry
- `execute_spark_sql_background()`: Background execution
- `execute_native_spark()`: S1 execution on Native
- `execute_omni_spark()`: S1 execution on Omni
- `execute_explain()`: E2 execution

## test_runner.py

S1/E2 execution logic with pool statistics logging. See `scripts/test_runner_template.py`.

Key patterns:
- Step detection: E2 first (EXPLAIN keyword), then S1
- Per-step logging with command strings
- Pool statistics logging in test finalization
- Result aggregation

**Important**: Add `__test__ = False` to TestCaseRunner class to prevent pytest collection.

## config_loader.py

Singleton pattern for JSON config loading. See `scripts/config_loader_template.py`.

Key methods:
- `get_test_case(case_id)`: Get single test case by 用例_编号
- `get_native_spark_command()`: Get Native spark-sql command
- `get_omni_spark_command()`: Get Omni spark-sql command
- `get_server_config()`: Get SSH server info

## logger.py

Per-case logging with duplicate prevention. See `scripts/logger_template.py`.

Key methods:
- `sql()`: Log SQL/EXPLAIN commands (INFO level, green)
- `output()`: Log execution output (INFO level, green)
- `diff()`: Log comparison differences (WARNING level, yellow)
- `step_failure()`: Log step failures (ERROR level, red)
- `execution_result()`: Smart stderr handling (INFO/WARNING based on content)

Log file naming: `<case_id_lowercase>_<timestamp>.log`

**See `references/logging_color_strategy.md` for color mapping details.**