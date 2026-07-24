# spark-omnioperator-test-design-generator

为 Spark OMNI 优化算子生成标准化黑盒测试设计文档。

## 功能

- 根据算子名称自动定位分类（数据流向 × 功能语义）
- 基于输入因子和场景速查卡生成测试设计
- 支持四大测试类型（功能/性能/可靠性/兼容性）规划
- 生成后自动检视覆盖度（数据类型/算子场景/测试模块）
- 按标准模板输出 Markdown 测试设计文档

## 使用方式

向 AI 提供算子名称即可触发，例如：

- "帮我生成 TableWrite 算子的测试设计文档"
- "HashJoin 算子测试设计"
- "Sort 算子的黑盒测试设计文档"

## 前置条件

工作目录根路径下需存在以下代码仓库：

```
<workspace-root>/
├── spark/                    ← Spark 源码仓库（用于扫描原生算子实现）
│   └── sql/core/src/main/scala/org/apache/spark/sql/execution/
├── Gluten/                   ← Gluten 仓库（Omni 算子 Scala 集成层在此）
│   └── backends-omni/src/main/scala/org/apache/gluten/execution/    ← Omni 算子 Transformer
│   └── backends-omni/src/main/scala/org/apache/spark/sql/execution/ ← Spark 执行集成
├── {算子开发详设文档}.md        ← 开发设计文档（必需输入）
└── .agents/
    └── skills/
        └── spark-omnioperator-test-designgen/   ← 本技能
            ├── SKILL.md                          # Skill 主文件，生成流程指引
            ├── README.md                         # 本文件
            ├── references/                       # 参考文档
            │   ├── data-type-reference.md        # 数据类型参考资料（矩阵/边界值/插入规则）
            │   ├── data-type-checklist.md        # 数据类型检视清单
            │   ├── test-type-reference.md        # 测试类型参考资料（设计方法/四大类型规范）
            │   └── test-type-checklist.md        # 测试类型检视清单
            ├── templates/                           # 文档模板
            │   └── test_design_document_template.md  # 设计文档模板
            └── operators/                           # 算子速查卡（按需加载）
                ├── write_operator.md
                ├── scan_operator.md
                ├── filter_project_operator.md
                ├── aggregate_operator.md
                ├── sort_operator.md
                ├── join_operator.md
                └── window_operator.md
```

## 核心规范

### 测试设计方法（6种）

| 方法 | 缩写 | 用途 |
|:---|:---|:---|
| 等价类划分法 | EC/IE | 按输入因子可选值生成有效/无效等价类 |
| 边界值分析法 | BV | 按数据类型生成边界值用例 |
| 场景法 | SC | 按算子场景清单展开独立测试点 |
| 判定表法 | DT | 多条件组合场景 |
| 正交试验法 | OA | 2-wise/3-wise 因子组合 |
| 错误推测法 | EG | 补充易错场景 |

### 用例命名规范

- 格式：`{算子名}_{功能/场景描述}_{数据类型/变体}`
- 自检：去掉类型/模式标记后，步骤仍能与其他用例区分

## 输出

| 文件 | 格式 | 描述 |
|:---|:---|:---|
| {OperatorName}_Test_Design_Document.md | Markdown | 完整测试设计文档（按模板生成，逐条穷举所有测试点） |
