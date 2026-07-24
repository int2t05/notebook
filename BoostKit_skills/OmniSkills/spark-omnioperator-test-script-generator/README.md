# OmniOperator Spark Test Script Generator

从 JSON 测试用例配置自动生成 pytest 测试脚本，用于 Omni Spark 算子测试。

## 适用场景

- 从 `test_cases.json` 批量生成 pytest 测试文件
- 初始化测试目录结构和 `pytest.ini`
- 将中文测试用例定义转换为可执行的 Python 测试脚本

## 前置条件

工作目录根路径下需准备以下文件：

```
<workspace-root>/
├── test_cases.json                  ← 测试用例定义（必需）
├── config.json                      ← 服务器和 Spark 命令配置（必需，若不存在会从模板自动生成）
└── .agents/
    └── skills/
        └── spark-omnioperator-test-script-generator/   ← 本技能
            ├── SKILL.md                          # Skill 主文件，生成流程指引
            ├── README.md                         # 本文件
            ├── scripts/
            │   └── test_script_template.py       # 测试脚本模板
            └── references/
                ├── test_cases_schema.json        # 测试用例 JSON 结构定义
                ├── config_schema.json            # 配置文件 JSON 结构定义
                └── pytest_ini_template.ini       # pytest.ini 模板
```

### test_cases.json 结构

```json
[
  {
    "用例_编号": "Spark_OmniRuntime_Operator_001",
    "用例_名称": "Operator test case name",
    "用例_级别": "Level1",
    "用例_测试步骤": {
      "step1": {
        "description": "S1.原生和Omni执行SQL语句",
        "sql_statement": "SELECT * FROM test_table ORDER BY id;",
        "expected_result": "E1.原生和Omni执行结果一致"
      }
    }
  }
]
```

## 输出

在 `tests/` 目录下为每个测试用例生成对应的 pytest 脚本文件，同时创建 `pytest.ini` 和 `config.json`（如不存在）：

```
tests/
├── test_spark_omni_runtime_operator_001.py
├── test_spark_omni_runtime_operator_002.py
└── ...                               # 与 test_cases.json 一一对应
```

> **为什么每个用例单独生成一个文件？** 为了支持 pytest-xdist 并行执行（pytest.ini 中配置了 `-n 8`，即 8 个 worker 进程），每个文件作为独立调度单元分配到不同 worker 上并行跑。

> **注意：** 生成后请修改项目根目录下的 `config.json`，填写正确的服务器 IP、用户名和密码后再执行测试。

## 使用方法

直接告诉 AI，例如：

- "根据 test_cases.json 生成Spark OmniOperator测试脚本"
- "生成Spark OmniOperator的 pytest 测试文件"
- "初始化Spark OmniOperator测试目录结构"

## 职责边界

本技能**仅负责生成测试脚本**，不涉及：

- 测试执行 → 使用 `spark-omnioperator-test-runner`
- 报告生成 → 使用 `spark-omnioperator-test-report-generator`