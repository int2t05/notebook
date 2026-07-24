# Troubleshooting Guide

## Common Issues

### "hadoop: command not found"

SSH non-interactive sessions don't load environment. Fix by:
- Adding `source ~/.bashrc;` prefix to spark commands in config.json
- OR ensuring ~/.bashrc sets Hadoop PATH for non-interactive shells

### SSH pool exhaustion

If pool full error occurs:
- Increase pool size: `export SSH_POOL_SIZE=50` or edit pytest.ini `[ssh] pool_size=50`
- Reduce parallelism: `pytest tests/ -n 4` (fewer workers)

### Pytest collection warnings for TestCaseRunner

Add `__test__ = False` attribute to the class:
```python
class TestCaseRunner:
    __test__ = False  # Prevent pytest collection
```

### Duplicate test execution

Use class-based tests with `setup_method/teardown_method`, NOT standalone wrapper functions. Pytest auto-discovery handles setup/teardown.

### Virtual environment not activated

Check activation:
```bash
which python  # Should point to omni_test_env/bin/python
pip list      # Should show pytest, paramiko, etc.
```

If not activated:
```bash
source omni_test_env/bin/activate
# OR
./activate_env.sh
```

### Tests being skipped (timeout)

**Check pytest timeout in pytest.ini:**
```bash
grep timeout pytest.ini
# Should show: timeout = 1200
```

**Check bash timeout calculation:**
- See `references/bash_timeout_calculation.md` for timeout formula
- MUST calculate bash timeout before executing pytest
- NEVER use default bash timeout (120s)

### Incomplete HTML report

**Check pytest-json-report:**
```bash
ls reports/test_results.json
# Should exist even if pytest crashed
```

**Check custom HTML generation:**
```bash
python generate_html_from_json.py
# Should generate HTML from JSON results
```

**See `references/html_report_generation.md` for custom HTML workflow.**

### Pool Statistics Missing

Verify pool integration:
```python
# In ssh_executor.py, check pool initialization
if self.use_pool:
    self.ssh_pool = get_ssh_pool({...})
```

### Virtual Environment Issues

Recreate venv:
```bash
rm -rf omni_test_env
./scripts/setup_venv.sh
source omni_test_env/bin/activate
```