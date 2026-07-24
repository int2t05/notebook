# OmniOperator Expression Development

用于指导在 OmniOperator 向量化执行引擎中开发新表达式/函数的 skill。

## 适用场景

- 实现新的 SQL 函数（数学、字符串、位运算、数组等）
- 添加向量化表达式
- 编写或修改函数注册
- 编写函数的单元测试

## 前置条件

工作目录根路径下需存在以下代码仓：

```
<workspace-root>/
├── OmniOperator/             ← OmniOperator 仓库（必需）
├── Gluten/                   ← Gluten 仓库（必需）
├── velox/                    ← Velox 仓库（必需）
└── .agents/
    └── skills/
        └── omnioperator-expression-dev/   ← 本技能
            ├── SKILL.md                          # Skill 主文件，完整的开发流程指引
            ├── README.md                         # 本文件
            └── references/
                ├── function_template.h           # 头文件模板（一元/二元/三元函数）
                ├── function_template.cpp         # 实现文件模板
                ├── test_template.cpp             # 单元测试模板
                ├── design_document_template.md   # 设计文档模板
                └── project_structure.md          # 项目目录结构、注册文件映射、数据类型常量
```

## 开发流程

1. **需求分析** — 明确函数名、类型、输入输出、边界情况
2. **研究 Velox 参考实现** — 学习向量化逻辑和边界处理
3. **研究 OmniOperator 现有模式** — 熟悉注册方式和代码风格
4. **编写设计文档** — 输出到 `OmniOperator/docs/expression-design/`
5. **等待用户审批** — 强制检查点，审批通过后才进入实现
6. **实现函数** — 按模板编写 `.h` / `.cpp`
7. **注册函数** — 在对应 `Register*.cpp` 中注册
8. **编写单元测试** — 覆盖正常、NULL、边界情况
9. **验证完整性**

## 快速开始

直接告诉 AI 你要实现的函数，例如：

- "实现 `sqrt` 函数，输入 double 输出 double"
- "添加 `bit_count` 表达式"
- "实现 `concat` 字符串函数"

Skill 会自动引导完成上述全流程。

## 注意事项

- 开发环境无鲲鹏硬件，**不要尝试编译或运行测试**，专注于代码实现
- 实现前必须先阅读 `references/` 下对应的模板文件
