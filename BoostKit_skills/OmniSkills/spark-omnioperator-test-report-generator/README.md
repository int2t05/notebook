# OmniOperator Spark Test Report Generator

从 pytest-json-report 结果生成防崩溃的 HTML 测试报告，用于 Spark OmniOperator 算子测试结果可视化。

## 适用场景

- 从 `reports/test_results.json` 生成可视化 HTML 报告
- 展示所有用例的测试状态（passed / failed / not_tested）
- pytest 崩溃后仍可生成报告（JSON 已持久化）

## 前置条件

工作目录根路径下需准备以下文件：

```
<workspace-root>/
├── test_cases.json                  ← 测试用例定义（必需）
├── reports/
│   └── test_results.json            ← pytest-json-report 执行结果（必需，由 test-runner 生成）
└── .agents/
    └── skills/
        └── spark-omnioperator-test-report-generator/   ← 本技能
            ├── SKILL.md                          # Skill 主文件，生成流程指引
            ├── README.md                         # 本文件
            ├── scripts/
            │   ├── conftest_template.py          # pytest hook 模板（测试结束后自动生成报告）
            │   └── generate_html_template.py     # HTML 报告生成模板
            └── references/
                └── html_report_generation.md     # 报告生成设计文档
```

### reports/test_results.json 来源

由 `spark-omnioperator-test-runner` 执行 pytest 后自动生成（pytest.ini 中配置了 `--json-report`）。若未执行测试，此文件不存在。

## 输出

生成 `reports/test_report.html`，包含以下功能：

- **防崩溃**：pytest 崩溃也能生成报告
- **完整覆盖**：展示所有用例（已测试 + 未测试）
- **可展开/折叠**：点击行查看详细日志
- **筛选按钮**：全部 / Passed / Failed / Not Tested
- **正确耗时**：setup + call + teardown 三阶段求和
- **ERROR 高亮**：红色背景突出错误日志

> **为什么自定义 HTML 而不用 pytest-html？** pytest-html 在 pytest 崩溃时不生成报告，对 xdist 支持不佳，且无法展示未执行的用例。自定义方案通过 pytest-json-report 增量持久化 JSON，确保报告始终可用。

## 使用方法

### 自动生成（推荐）

由 Agent 在 pytest 执行完毕后自动触发：将 `scripts/conftest_template.py` 复制为项目根目录的 `conftest.py`，pytest 结束时会自动调用报告生成逻辑。

### Agent 触发生成

当 `reports/test_results.json` 已存在时，告诉 Agent "生成Spark OmniOperator 算子测试报告"，Agent 会：

1. 将 `scripts/generate_html_template.py` 复制到项目根目录
2. 执行 `python3 generate_html_from_json.py`
3. 输出 `reports/test_report.html`

无需用户手动操作脚本。

## 职责边界

本技能**仅负责生成 HTML 报告**，不涉及：

- 测试脚本生成 → 使用 `spark-omnioperator-test-script-generator`
- 测试执行 → 使用 `spark-omnioperator-test-runner`
