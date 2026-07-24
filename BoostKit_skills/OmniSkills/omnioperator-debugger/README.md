# OmniOperator Debugger

这个 README 面向使用者，帮助你用提示词触发 `omnioperator-debugger` skill。
具体执行规则、目录边界和调试流程以 `SKILL.md` 为准。

## 什么时候用

当你需要 Codex 帮你做下面这些事情时，可以明确提到 `omnioperator-debugger`：

- 编译指定 OmniOperator / Gluten 分支并跑 SQL 验证
- 对比 Native Spark 与 Omni 结果
- 使用 `debug_e2e_sql_columnar` 逐个关闭列式算子定位问题
- 分析物理计划、native 日志、coredump 或数据不一致
- 定位完成后，把 issue 总结成 case 或 knowledge

## 调试提示词模板

```text
使用 omnioperator-debugger。

1、调试
使用 mcp_client.py 进行 MCP 服务调用，先按下面的分支编译，然后调试 q45_1.sql 的问题。

Omni repo: https://gitcode.com/helloxteen_/OmniOperator.git
Omni branch: issue/q45_1
Gluten repo: https://gitcode.com/helloxteen_/Gluten.git
Gluten branch: issue/q45_1

要求：
- 先用 compile_gluten 编译
- 再跑 Native Spark 基线
- 再跑 Omni 结果
- 如果结果不一致，使用 debug_e2e_sql_columnar 定位可疑 columnar toggle
- 继续根据物理计划、日志和代码定位根因
```

## 总结归档提示词模板

```text
使用 omnioperator-debugger。

2、总结
参照 cases/q45-existence-join.md，对当前 issue 进行总结，看是否值得归档到 cases 和 knowledge。

要求：
- 总结问题现象、版本信息、定位步骤、关键证据、根因、修复和验证结果
- 判断是否值得新增 cases
- 如果不适合新增 cases，抽象到 knowledge 的 patterns/operators/vectors 中
- 不要把完整日志、聊天记录、一次性实验过程放进 skill
```

## 更通用的提示词

```text
使用 omnioperator-debugger，帮我调试这个 Omni 与 Native Spark 结果不一致的问题。
SQL 文件是 <sql file>，数据库是 <database>。
请先跑 Native 和 Omni 对比，再用 debug_e2e_sql_columnar 缩小到可疑算子，
最后给出根因、修复建议和是否需要归档到 cases/knowledge。
```

## 归档边界

- `cases/`：只放代表性的完整调试样板，例如 q45、q62
- `knowledge/`：放跨 issue 可复用的规律，例如 NULL 传播、encoding 兼容、输出窗口错位
- 不放入 skill：完整日志、聊天记录、临时实验文件、只对某次环境有效的结论
