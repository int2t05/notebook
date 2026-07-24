---
name: "omnioperator-debugger"
description: "OmniOperator 列式算子调试专家。Use when Codex needs to 做 Omni 与 Spark 结果对比、关闭或开启列式算子定位问题、分析物理计划、处理 Coredump、排查数据不一致、或阅读 Omni 调试工作流。"
---

# OmniOperator Debugger

将此 skill 作为调试层使用。SQL 执行与列式算子开关定位优先使用 `mcp-servers/spark-remote-mcp`；需要编译或重编译可运行产物时，使用 `compile_gluten`。服务器连接、文件同步等手工远端操作规则由 `omnioperator-remote-build` 提供。

## 目录结构

当前 skill 目录结构如下：

```text
omnioperator-debugger/
├── SKILL.md
├── README.md
├── cases/
│   ├── README.md
│   ├── q45-existence-join.md
│   └── q62-const-vector-null.md
├── knowledge/
│   ├── README.md
│   ├── operators/
│   │   ├── broadcast-hash-join.md
│   │   ├── existence-join.md
│   │   └── scan-orc.md
│   ├── patterns/
│   │   ├── cross-batch-copy.md
│   │   ├── encoding-compatibility.md
│   │   ├── nested-field-indexing.md
│   │   ├── null-flag-propagation.md
│   │   ├── output-window-mismatch.md
│   │   └── state-lifecycle-race.md
│   └── vectors/
│       ├── const-vector.md
│       └── dictionary-vector.md
├── config.yaml
├── omnioperator-debugger-params.md
├── omnioperator-debugger-coredump.md
└── omnioperator-debugger-workflow.md
```

各文件职责如下：

- `SKILL.md`：skill 入口、适用场景、调用顺序、目录边界规则
- `README.md`：用户侧提示词模板，说明如何触发调试与总结归档流程
- `cases/README.md`：case 索引，说明哪些 issue 被保留为主案例，哪些只沉淀到 knowledge
- `cases/q45-existence-join.md`：代表性案例，示范如何使用本 skill 定位 `BroadcastHashJoin + ExistenceJoin` 问题
- `cases/q62-const-vector-null.md`：代表性案例，示范如何从结果差异定位到 const vector NULL 标记丢失
- `knowledge/README.md`：knowledge 目录索引与组织原则
- `knowledge/patterns/`：跨 operator、跨模块复用的问题模式与根因模式
- `knowledge/operators/`：按算子入口组织常见问题与对应 pattern
- `knowledge/vectors/`：按向量语义与 encoding 组织调试知识
- `config.yaml`：skill 依赖关系与 MCP 工具映射
- `omnioperator-debugger-params.md`：列式算子参数表、物理计划标识、常用 `SET` 语句
- `omnioperator-debugger-coredump.md`：Coredump / GDB / native 栈问题定位方法
- `omnioperator-debugger-workflow.md`：数据不一致调试流程、表达式排查、案例化经验

## 内容边界

本 skill 用于沉淀可复用的调试方法，不作为 issue 全量归档目录。

- 通用调试流程、算子规律、排查方法、常用命令，应保留在 skill 文档中
- 代表性的案例可以保留，但应服务于“示范这个 skill 怎么使用”，而不是堆积完整 issue 历史
- 聊天整理稿、完整日志、patch 文件、一次性实验记录，不应直接放入 skill 目录
- 如果后续新增 `cases/`，每个问题类型默认只保留 1 个主案例；新的相似 issue 优先抽取到知识库而不是重复建案例
- 如果后续新增 `knowledge/`，其中内容应是跨 issue 可复用的经验，而不是绑定某次提交或某次环境的临时结论
- 新增案例时，应同步补充或链接至少 1 条对应的通用经验，避免 skill 目录逐渐演变成纯案例堆积

## 调试原则

- 证据驱动：每个结论都要有日志、数据、结果文件或代码证据。
- Spark 是基准：Omni 与 Spark 不一致时，默认先以 Spark 结果为正确基线。
- 可复现优先：先把问题稳定复现，再继续缩小根因。
- 最小化验证：优先用最小 SQL、最小数据集、最少算子组合验证假设。
- 渐进式排查：从结果差异到物理计划，再到表达式、算子、native 栈逐步收敛。

## 前置依赖

1. 运行 Omni SQL 正确性校验时，优先调用 `mcp-servers/spark-remote-mcp` 的 `run_e2e_sql`
2. 运行 Spark Native 基线时，调用 `mcp-servers/spark-remote-mcp` 的 `run_e2e_sql_native`
3. 需要自动逐个关闭列式算子开关时，调用 `mcp-servers/spark-remote-mcp` 的 `debug_e2e_sql_columnar`
4. 需要编译或重编译可运行产物时，调用 `compile_gluten`
5. 需要手工 ssh/scp、同步文件、远端命令时，读取 `omnioperator-remote-build`
6. 文档中的 `{{server.*}}`、`{{project.*}}` 仅作为手工远端命令占位符，不代表真实值

## 调试入口

优先使用 `mcp-servers/spark-remote-mcp/mcp_client.py` 调用 MCP 工具。这样可以绕过客户端对长时间 MCP 调用的等待限制，也能把编译与 SQL 执行日志统一落到 `compile_logs/`。

### 示例：复现并定位 q45_1.sql

本示例对应 `cases/q45-existence-join.md`，适合用来校验 MCP 配置、编译链路和 SQL 调试链路是否可用。

1. 使用指定分支编译 Omni + Gluten：

```bash
cd mcp-servers/spark-remote-mcp
python mcp_client.py compile_gluten \
  https://gitcode.com/helloxteen_/OmniOperator.git issue/q45_1 \
  https://gitcode.com/helloxteen_/Gluten.git issue/q45_1
```

2. 使用 Native Spark 获取基线结果：

```bash
python mcp_client.py run_e2e_sql_native q45_1.sql tpcds_bin_partitioned_varchar_orc_5 300
```

3. 使用 Omni 执行同一 SQL：

```bash
python mcp_client.py run_e2e_sql q45_1.sql tpcds_bin_partitioned_varchar_orc_5 300
```

4. 如果 Omni 与 Native 不一致，执行列式算子开关定位：

```bash
python mcp_client.py debug_e2e_sql_columnar q45_1.sql tpcds_bin_partitioned_varchar_orc_5 300 "" true true
```

5. 根据结果继续收敛：

- 如果关闭某个 columnar toggle 后结果恢复一致，优先检查该 toggle 对应的物理计划算子
- 如果结果行数不同，先看 `match_exact`、`match_sorted`、结果行数、缺失/多出的行
- 如果出现 coredump，转到 `omnioperator-debugger-coredump.md`
- 如果问题集中在 NULL、encoding、STRUCT、ORC 或 batch 边界，优先查 `knowledge/`

## 总结与归档

定位完成后，参照 `cases/q45-existence-join.md` 对当前 issue 做一次结构化总结。总结不要求长，但必须包含足够证据，方便后续判断是否值得进入 `cases/` 或 `knowledge/`。

建议记录以下内容：

- 问题现象：SQL、数据库、Native 结果、Omni 结果、错误日志或 coredump
- 版本信息：OmniOperator / Gluten 的 repo、branch、commit
- 定位步骤：使用了哪些 MCP 命令、关闭了哪些 columnar toggle、观察到什么变化
- 关键证据：物理计划、输出行数、关键日志、native 变量、栈信息
- 根因：具体代码路径和错误语义
- 修复：修改点和为什么能修复
- 验证：Native/Omni 是否一致，`match_exact` / `match_sorted` 是否通过

归档判断：

- 适合作为 `cases/`：能代表一条完整、清晰、可复用的调试路径，并且与已有 case 类型不同
- 适合进入 `knowledge/`：能抽象成跨 issue 可复用的 pattern、operator 经验或 vector 语义
- 不建议进入 skill：完整日志、聊天记录、一次性实验过程、只对单次环境有效的临时结论

## 列式算子调试

排查列式算子问题时，必须与 Spark 结果对比。

### 关闭特定算子进行问题排查

优先使用 `debug_e2e_sql_columnar`，传入怀疑的列式算子配置 key。工具会自动逐个追加 `SET <key>=false;`，并与 Native Spark 基线对比。

```python
debug_e2e_sql_columnar(
    sql="<SQL text>",
    database="<database>",
    toggles=[
        "spark.gluten.sql.columnar.project",
        "spark.gluten.sql.columnar.filter",
        "spark.gluten.sql.columnar.broadcastJoin",
        "spark.gluten.sql.columnar.hashagg",
    ],
    timeout_sec=300,
    stop_on_match=True,
    include_native_baseline=True,
)
```

### 生成简化 SQL 来复现问题

当定位到问题后，生成简化的 SQL 进一步隔离。**必须同时运行 Omni 和 Spark 测试并对比**。

```bash
run_e2e_sql_native(sql="<simplified SQL>", database="<database>", timeout_sec=300)
run_e2e_sql(sql="<simplified SQL>", database="<database>", timeout_sec=300)
```

---

## 参考文档

- [cases/q45-existence-join.md](cases/q45-existence-join.md)：`BroadcastHashJoin + ExistenceJoin` 代表性案例，展示如何按本 skill 完成定位与修复验证
- [cases/q62-const-vector-null.md](cases/q62-const-vector-null.md)：`ConstVector NULL` 代表性案例，展示 NULL 标记传播类问题的定位方式
- [knowledge/README.md](knowledge/README.md)：knowledge 目录结构、组织原则与使用规则
- [knowledge/operators/existence-join.md](knowledge/operators/existence-join.md)：`ExistenceJoin` 的常见问题模式与关键链路
- [knowledge/patterns/output-window-mismatch.md](knowledge/patterns/output-window-mismatch.md)：分批输出窗口错位类问题的通用判断方式
- [knowledge/patterns/null-flag-propagation.md](knowledge/patterns/null-flag-propagation.md)：NULL 标记在 slice/copy/read/rebuild 中丢失的通用判断方式
- [omnioperator-debugger-params.md](omnioperator-debugger-params.md)：列式算子 Enable 参数表、物理计划算子标识、常用 SET 语句
- [omnioperator-debugger-coredump.md](omnioperator-debugger-coredump.md)：Coredump 问题定位、GDB 使用指南、分析结果解读
- [omnioperator-debugger-workflow.md](omnioperator-debugger-workflow.md)：数据不一致调试流程、表达式排查、案例与最佳实践

## 注意事项

- 涉及 NULL 值计算时优先检查数据质量与边界条件
- 只同步必要文件，避免上传整个目录
- 需要重编译并跑 Spark SQL 时，优先使用 `compile_gluten`
