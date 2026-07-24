# OmniOperator Spark Test Runner

通过 SSH 连接池执行 pytest 测试脚本，用于 Spark OmniOperator 算子测试执行。

## 适用场景

- 执行已生成的 pytest 测试脚本
- 通过 SSH 连接池并行执行 Spark SQL 测试
- 运行 S1（Native vs Omni 结果对比）和 E2（执行计划关键词验证）测试模式

## 前置条件

工作目录根路径下需准备以下文件：

```
<workspace-root>/
├── test_cases.json                  ← 测试用例定义（必需）
├── config.json                      ← 服务器和 Spark 命令配置（必需）
├── tests/                           ← pytest 测试脚本目录（必需，由 test-script-generator 生成）
│   ├── test_spark_omni_runtime_operator_001.py
│   └── ...
└── .agents/
    └── skills/
        └── spark-omnioperator-test-runner/   ← 本技能
            ├── SKILL.md                       # Skill 主文件，执行流程指引
            ├── README.md                      # 本文件
            ├── scripts/
            │   ├── ssh_pool_template.py       # SSH 连接池模板
            │   ├── ssh_executor_template.py   # SSH 执行器模板
            │   ├── test_runner_template.py    # 测试运行器模板
            │   ├── config_loader_template.py  # 配置加载器模板
            │   ├── logger_template.py         # 日志模块模板
            │   └── setup_venv.sh              # 虚拟环境设置脚本
            └── references/
                ├── bash_timeout_calculation.md   # Bash 超时计算说明
                ├── timeout_configuration.md       # 超时配置详解
                ├── ssh_pool_architecture.md       # SSH 连接池架构
                ├── logging_color_strategy.md      # 日志颜色策略
                ├── performance_tips.md            # 性能优化建议
                ├── core_modules.md                 # 核心模块说明
                └── troubleshooting.md             # 故障排查指南
```

### tests/ 目录来源

由 `spark-omnioperator-test-script-generator` 根据 `test_cases.json` 自动生成。若未生成，请先执行测试脚本生成。

## 输出

执行测试后生成以下文件：

- `reports/test_results.json` — pytest-json-report 执行结果（用于报告生成）
- `logs/` — 测试执行日志目录

## 使用方法

直接告诉 AI，例如：

- "执行Spark OmniOperator测试"
- "运行Spark OmniOperator的 pytest 测试"
- "执行Spark OmniOperator S1 和 E2 测试模式"

AI 将自动：
1. 设置 Python 虚拟环境
2. 复制核心模块到工作目录
3. 计算合理的超时时间
4. 执行 pytest 测试
5. 验证输出文件

## 职责边界

本技能**仅负责执行测试**，不涉及：

- 测试脚本生成 → 使用 `spark-omnioperator-test-script-generator`
- 报告生成 → 使用 `spark-omnioperator-test-report-generator`