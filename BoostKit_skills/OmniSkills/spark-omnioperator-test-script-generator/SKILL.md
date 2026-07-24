---
name: spark-omnioperator-test-script-generator
description: "Generate pytest test scripts for Spark OmniOperator testing. Reads test_cases.json and creates tests/test_*.py files with 1:1 mapping for pytest-xdist parallel execution. Trigger when user mentions '生成测试脚本', 'generate test scripts', 'create test files' in the context of Spark OmniOperator. Do NOT trigger for other business scenarios or for test execution/reporting."
---

# OmniOperator Spark Test Script Generator

Generate pytest test scripts from JSON configuration for Spark OmniOperator. Each test case maps to a separate file to support pytest-xdist parallel execution.

## Sole Responsibility

**Only generate test script files.**

- Input: `test_cases.json`
- Output: `tests/test_*.py` files
- NOT responsible for: execution, environment setup, core modules, reporting

## When to Use

Trigger when user wants to:
- Generate test scripts from JSON
- Create pytest files
- Set up test structure

**NOT triggered for:**
- Test execution → use `spark-omnioperator-test-runner`
- Report generation → use `spark-omnioperator-test-report-generator`

## Input Files

Required:
- **Test cases JSON file**: contains test case definitions. Resolved by priority:
  1. **User-specified filename**: e.g. `BigData_Spark_Operator_Test_TableWrite_Test_Cases.json` — use directly
  2. **Auto-discovery** (when user doesn't specify): search in order:
     - `{OperatorName}_Test_Design/*_Test_Cases.json` in the working directory
     - `*_Test_Cases.json` in the working directory
     - Fallback: `test_cases.json`
  3. **Not found**: prompt user to provide a filename or generate test cases first
- `config.json`: Server connection + Spark commands (copied from template if missing)

See `references/test_cases_schema.json` for JSON structure.

## Output Files

Creates:
```
tests/
├── test_spark_omni_runtime_tablewrite_001.py
├── test_spark_omni_runtime_tablewrite_002.py
└── test_<case_id>.py  # 1:1 from test_cases.json
```

Also creates:
- `pytest.ini` from `references/pytest_ini_template.ini` if not exists.
- `config.json` from `references/config_schema.json` if not exists (user must fill in server credentials before execution).

**Why 1:1 file mapping?** Each test case gets its own file so that `pytest-xdist` (`-n 8` in pytest.ini) can distribute files across worker processes for parallel execution.

## Generation Logic

1. Resolve test cases JSON file (see Input Files priority above)
2. Copy `references/config_schema.json` → `config.json` (if not exists), then **remind user to fill in server IP, user, password**
3. Create `pytest.ini` from `references/pytest_ini_template.ini` (if not exists)
4. Create `tests/` directory (if not exists)
5. For each test case:
   - Extract `用例_编号` → filename: `tests/test_<case_id_lowercase>.py`
   - Extract `用例_名称` → class docstring
   - Extract `用例_测试步骤` → test method content
6. Use template from `scripts/test_script_template.py`
7. After generation, **remind user**: "请修改项目根目录下的 config.json，填写正确的服务器 IP、用户名和密码后再执行测试"

## Template

See `scripts/test_script_template.py`.

Replace placeholders:
- `{CASE_ID}` → test case ID, e.g. `Spark_OmniRuntime_Tablewrite_001`
- `{CASE_NAME}` → test case name, e.g. `TableWrite算子_开关开启场景测试`
- `{N}` → numeric suffix from case ID, e.g. `001` (used in class name `TestCase{N}`)
- `{method_name}` → case ID lowercased, e.g. `spark_omni_runtime_tablewrite_001`

## Naming Convention

Input: `用例_编号 = "Spark_OmniRuntime_Tablewrite_001"`
Output: `tests/test_spark_omni_runtime_tablewrite_001.py`

Rules: lowercase, preserve underscores, no special characters.

