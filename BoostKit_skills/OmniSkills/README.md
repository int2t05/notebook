# OmniSkill

OmniSkill 是一套面向 OmniOperator 向量化执行引擎的 AI 辅助技能集合，覆盖表达式/算子生态分析、表达式/算子开发、远程构建与基础设施、性能优化、测试 SQL 生成以及算子端到端测试全流程。

## 技能列表

### 一、表达式 / 算子生态分析

#### omnioperator-expression-analysis

表达式生态分析技能 —— 系统扫描 OmniOperator / Velox / Spark SQL 三方表达式支持现状，生成覆盖度 Gap 分析报告。

- OmniOperator 向量化框架已注册哪些表达式？各支持哪些类型？
- Velox 覆盖了哪些 Spark SQL 表达式？
- Omni 与 Velox / Spark SQL 标准之间的差距是什么？优先级如何？

详见 [omnioperator-expression-analysis/README.md](omnioperator-expression-analysis/README.md)

#### omnioperator-status-analysis

算子生态分析技能 —— 全链路扫描 Spark / Gluten / OmniOperator / Velox 物理算子支持现状，生成覆盖度 Gap 分析报告。

- 当前 Omni 支持哪些 Spark 物理算子？
- 哪些算子只在 Gluten 侧声明了支持但执行侧还不完整？
- fallback 主要来自哪些算子或类型限制？
- 与 Velox 相比，Omni 缺哪些算子能力？

详见 [omnioperator-status-analysis/README.md](omnioperator-status-analysis/README.md)

### 二、表达式 / 算子开发

#### omnioperator-expression-dev

表达式开发技能 —— 指导在 OmniOperator 向量化执行引擎中开发新表达式/函数的完整流程。

- 需求分析 → 研究 Velox 参考实现 → 研究 OmniOperator 现有模式
- 编写设计文档 → 用户审批 → 实现函数 → 注册函数 → 编写单元测试
- 提供头文件、实现文件、测试文件模板

详见 [omnioperator-expression-dev/README.md](omnioperator-expression-dev/README.md)

### 三、远程构建与基础设施

#### omnioperator-remote-build

OmniOperator 远程构建与单元测试技能 —— 通过 SSH + rsync 在本地与远端服务器之间完成代码同步、编译、UT 与系统状态检查。

- rsync 增量同步本地代码到远端
- 远程一键执行编译、单元测试、系统信息查看等预定义任务
- 支持 SSH 密钥免密登录

详见 [omnioperator-remote-build/README.md](omnioperator-remote-build/README.md)

#### omnioperator-debugger

OmniOperator 列式算子调试技能 —— 用于 Omni 与 Spark 结果对比、列式算子开关定位、物理计划分析、Coredump 排查和数据不一致调试。

- 以 Spark 结果作为正确性基线，对比 Omni 结果
- 通过关闭或开启列式算子逐步缩小问题范围
- 提供常用 Gluten / Omni 参数表、物理计划标识和 SET 语句
- 提供数据不一致、表达式排查、Coredump 与 GDB 调试流程

详见 [omnioperator-debugger/SKILL.md](omnioperator-debugger/SKILL.md)

#### mcp-servers/spark-remote-mcp

Spark Remote Test MCP Server —— 通过 SSH 在远端集群上执行 Spark 性能测试、编译部署、正确性校验的 MCP 服务。

- 提供 11 个 MCP 工具：`run_spark_test_operator`（性能计时）、`run_e2e_sql`（正确性校验）、`compile_omni` / `compile_gluten`（编译部署）、`fetch_spark_flame_graphs`（拉取火焰图）、`drop_cluster_caches`（冷启动）等
- 以 stdio 方式运行，配合 Claude Code / OpenCode 等 MCP 客户端使用
- 配套 `mcp_client.py` 绕过 MCP 协议，可直接 CLI 调用长时任务

详见 [mcp-servers/spark-remote-mcp/README.md](mcp-servers/spark-remote-mcp/README.md)

### 四、性能优化

#### omni-sql-perf-improvement

SQL 全链路性能优化技能 —— 对单条目标 SQL 在 Omni 引擎上做端到端调优，覆盖 6 个阶段：分支/编译/部署 → Baseline → Profiling → Diagnose → 设计+编码 → 正确性校验 → 性能验收。

- 强制规则：先构建再测试、先正确后性能、每轮追踪文档、全链路视角
- 配套参考文档：基线指标口径、画像指南、瓶颈判定、优化手段库、验证检查、鲲鹏硬件亲和性、TPC-DS 算子覆盖
- 默认基线分支 `2026_330_poc`，所有改动必须在独立功能分支上进行

详见 [omni-sql-perf-improvement/README.md](omni-sql-perf-improvement/README.md)

#### omni-flamegraph-operator-analysis

火焰图两级热点分析技能 —— 基于 async-profiler 火焰图，自动发现 Top-N 热点算子，并对每个算子下钻到 Top-N 热点函数，输出结构化 CSV。

- 步骤 1：`flame_top_operators.py` 自动识别 `op::*Operator` / `*Writer` / `*Reader` 等帧
- 步骤 2：`flame_top_functions.py` 对每个 Top 算子提取子树下热点函数
- 步骤 3：与 Velox / ClickHouse 对比实现，输出 P0/P1/P2 优化优先级列表

详见 [omni-flamegraph-operator-analysis/SKILL.md](omni-flamegraph-operator-analysis/SKILL.md)

#### velox-flamegraph-analyzer-skill

Velox 火焰图全链路瓶颈分析技能 —— 解析 async-profiler 火焰图 HTML 文件，自动识别 Java/C++(Velox)/Kernel 热点帧，映射到 Velox 业务代码模块，按功能域（Scan/Join/Aggregate/Shuffle 等）聚类生成结论，输出带可点击火焰图链接的交互式 HTML 报告，并针对 ARM/aarch64 平台提供专属优化建议。

- 流式解析支持 1000+ 火焰图文件，分层抽样保证代表性
- 6 条 ARM 性能规则自动匹配（RLE 解码、哈希分配器、哈希计算、哈希表探测、JSON 解析、CollectList）
- 可配置业务关键词（默认 Gluten+Velox，可切换 ClickHouse / 纯 Java 等）

详见 [velox-flamegraph-analyzer-skill/README.md](velox-flamegraph-analyzer-skill/README.md)

#### velox-x86-arm-webui-analysis

Velox x86 vs ARM WebUI 性能对比分析技能 —— 对比分析 Velox 在 x86 和 ARM(鲲鹏) 上的 Spark WebUI 性能差异，识别 ARM 落后的算子和计算过程，定位缺失的 NEON/SVE 向量化代码路径，并生成带 WebUI 快捷链接的可交互 HTML 对比报告。

- 4-Phase 分析工作流：整体 Stage 对比总览 → 慢 Stage 算子级精细分析 → 代码热点定位 NEON/SVE 缺失点 → 生成可视化 HTML 报告
- 支持单 Stage 精细对比(用户指定任务名 + Stage ID 时直接跳到精细分析)
- 根因诊断决策树：ValueStream Wall/CPU 比率判定 IO 等待 vs CPU 计算，逐算子给出架构差异推测
- 代码热点映射表：splitFixedType(gather)、simd::memcpy(256-bit vs 128-bit)、HashProbe(gather)、readFlatVectorStringView(前缀和) 等 9 项架构差异速查
- 含完整 HTML 报告模板(CSS 柱状图、ratio badge、stage detail card、WebUI link grid)

详见 [velox-x86-arm-webui-analysis/SKILL.md](velox-x86-arm-webui-analysis/SKILL.md)

#### extract-spark-ui-metrics

Spark UI / API 算子级 Metrics 提取技能 —— 从 Spark History Server 的 `details=true` JSON 中提取 HashAgg / Join / Sort 等算子的输入输出行数、CTE 执行次数与复用关系，并按强制结构输出 Markdown 文档。

- 主查询 + 子查询 HashAgg 明细表（按 nodeId 与 edges 双向追溯）
- 汇总表（语义顺序：CTE 按 WITH 书写顺序 → 最后主查询）
- CTE 执行次数与复用判断（Subquery 节点 / stage 划分）
- 嵌套子查询必须逐层追溯，禁止漏内层 HashAgg

详见 [extract-spark-ui-metrics/SKILL.md](extract-spark-ui-metrics/SKILL.md)

### 五、Spark 表达式测试 SQL 生成

#### generate-sql-testcases

Spark 表达式测试 SQL 生成技能 —— 读取包含 Spark 函数信息的 CSV 文件，为每个函数批量生成 19 种数据类型的测试 SQL，并输出到新 CSV。

- 维护 ~170 个已知函数的 SQL 模板，按白名单匹配合理的数据类型组合
- 支持单/多参数函数、聚合函数、窗口函数、运算符
- 默认白名单模式（如 `abs` 只生成数值类型，`upper` 只生成字符串类型），`--all` 可退回到全类型模式
- 已有"已完成"状态的函数会被跳过，支持断点续跑

详见 [generate-sql-testcases/SKILL.md](generate-sql-testcases/SKILL.md)

### 六、OMNI 算子端到端测试全流程

> 这六个技能按"检视 → 设计 → 用例 → 脚本 → 执行 → 报告"流水线依次串联，可独立使用，也可组成完整测试流水线。

#### spark-omnioperator-test-devdoc-review

算子开发设计文档检视技能 —— 审查 Spark OMNI 优化算子的开发设计文档，验证其是否为下游 agent 自动生成测试设计提供足够的信息密度。

- 9 个功能完整性维度（F1~F9）：测试约束、数据类型覆盖、开关配置、观测算子、设计流程、SQL 用例示例、兼容性、行为可测试性、SQL 示例多样性
- 逐项给出"通过/不通过"判定 + 文档依据 + 修复建议
- 强制规则：F1~F9 任一 ❌ → 最终结论不通过
- 输出报告与原设计文档放在同一目录，便于开发、测试人员直接修改
- 推荐作为 `test-design-generator` 的前置步骤

详见 [spark-omnioperator-test-devdoc-review/README.md](spark-omnioperator-test-devdoc-review/README.md)

#### spark-omnioperator-test-design-generator

算子测试设计文档生成技能 —— 为指定算子生成标准化黑盒测试设计文档。

- 强制前置：需先扫描 Spark 源码 + 提取详设文档
- 按 6 种测试设计方法（等价类 / 边界值 / 场景法 / 判定表 / 正交试验 / 错误推测）展开
- 提供 7 类算子速查卡（写入 / 扫描 / 过滤投影 / 聚合 / 排序 / 关联 / 窗口）

详见 [spark-omnioperator-test-design-generator/README.md](spark-omnioperator-test-design-generator/README.md)

#### spark-omnioperator-test-case-generator

算子测试用例生成技能 —— 基于测试设计文档，为指定算子批量生成 4 字段标准 JSON 测试用例文件。

- 强制前置依赖：必须先存在 `spark-omnioperator-test-design-generator` 产出的测试设计文档
- 用例按「基础验证 → 功能深化 → 质量保障」三层结构排列
- 生成前展示用例标题预览等待确认；用例数 > 30 时分批交付
- 完成后执行六项强制自检（格式完整性、异常用例格式、名称-实现一致性、数据类型、功能模式、预期结果）

详见 [spark-omnioperator-test-case-generator/README.md](spark-omnioperator-test-case-generator/README.md)

#### spark-omnioperator-test-script-generator

算子测试脚本生成技能 —— 从 `test_cases.json` 批量生成 pytest 测试脚本文件。

- 每个测试用例生成一个独立文件，支持 pytest-xdist 并行执行（`pytest -n 8`）
- 自动生成 `pytest.ini` 和 `config.json`（服务器连接 + Spark 命令配置）模板
- 不涉及测试执行与报告生成

详见 [spark-omnioperator-test-script-generator/README.md](spark-omnioperator-test-script-generator/README.md)

#### spark-omnioperator-test-runner

算子测试执行技能 —— 通过 SSH 连接池执行 pytest 测试脚本，运行 S1（Native vs Omni 结果对比）和 E2（执行计划关键词验证）测试模式。

- 负责：核心模块拷贝（SSH pool / executor / runner / logger / config loader）、虚拟环境搭建、`pytest tests/ -v` 执行
- 按用例数量动态计算 bash 超时（避免默认 120s 误杀）
- 不涉及脚本生成与报告生成

详见 [spark-omnioperator-test-runner/README.md](spark-omnioperator-test-runner/README.md)

#### spark-omnioperator-test-report-generator

算子测试报告生成技能 —— 从 pytest-json-report 结果生成防崩溃的 HTML 测试报告。

- pytest 崩溃也能生成报告（基于持久化 JSON 增量恢复）
- 展示所有用例（已测试 + 未测试），可展开/折叠、按状态筛选
- ERROR 红色高亮、localStorage 记忆筛选状态
- 不涉及脚本生成与执行

详见 [spark-omnioperator-test-report-generator/README.md](spark-omnioperator-test-report-generator/README.md)

## 目录结构

```
OmniSkill/
├── README.md
│
├── omnioperator-expression-analysis/   ← 表达式生态分析
│   ├── SKILL.md
│   └── README.md
│
├── omnioperator-status-analysis/       ← 算子生态分析
│   ├── SKILL.md
│   ├── README.md
│   └── references/
│
├── omnioperator-expression-dev/        ← 表达式开发
│   ├── SKILL.md
│   ├── README.md
│   └── references/
│
├── omnioperator-remote-build/          ← 远程构建与单元测试
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│
├── omnioperator-debugger/              ← 列式算子调试
│   ├── SKILL.md
│   ├── config.yaml
│   ├── omniop-debugger-params.md
│   ├── omniop-debugger-coredump.md
│   └── omniop-debugger-workflow.md
│
├── mcp-servers/
│   └── spark-remote-mcp/               ← Spark Remote Test MCP Server
│       ├── server.py
│       ├── mcp_client.py
│       └── README.md
│
├── omni-sql-perf-improvement/          ← SQL 全链路性能优化
│   ├── SKILL.md
│   ├── README.md
│   ├── references/
│   └── scripts/
│
├── omni-flamegraph-operator-analysis/  ← 火焰图两级热点分析
│   ├── SKILL.md
│   └── scripts/
│
│── velox-flamegraph-analyzer-skill/    ← Velox 火焰图全链路瓶颈分析
 │   ├── SKILL.md
 │   ├── README.md
 │   ├── scripts/
 │   └── examples/
 │
 │── velox-x86-arm-webui-analysis/          ← Velox x86 vs ARM WebUI 性能对比分析
 │   ├── SKILL.md
 │   ├── code-hotspots.md
 │   └── webui-template.html
 │
  ├── extract-spark-ui-metrics/           ← Spark UI / API 算子级 Metrics 提取
│   └── SKILL.md
│
├── generate-sql-testcases/             ← Spark 表达式测试 SQL 生成
│   ├── SKILL.md
│   ├── scripts/
│   ├── examples/
│   └── references/
│
├── spark-omnioperator-test-devdoc-review/   ← 算子开发设计文档检视
│   ├── SKILL.md
│   ├── README.md
│   ├── references/
│   └── template/
│
├── spark-omnioperator-test-design-generator/   ← 算子测试设计文档生成
│   ├── SKILL.md
│   ├── README.md
│   ├── references/
│   ├── templates/
│   └── operators/
│
├── spark-omnioperator-test-case-generator/      ← 算子测试用例生成
│   ├── SKILL.md
│   ├── README.md
│   └── references/
│
├── spark-omnioperator-test-script-generator/    ← 算子测试脚本生成
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   └── references/
│
├── spark-omnioperator-test-runner/              ← 算子测试执行
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   └── references/
│
├── spark-omnioperator-test-report-generator/    ← 算子测试报告生成
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   └── references/
│
└── .gitignore
```

## 端到端测试流水线（OMNI 算子）

`spark-omnioperator-test-*` 系列六个技能按"检视 → 设计 → 用例 → 脚本 → 执行 → 报告"形成完整流水线：

```
[详设文档]
   │
   ▼
test-devdoc-review    ──► {Operator}_Design_Document_Review_Report.md
                                    │  (检视通过后再进入下一步)
                                    ▼
test-design-generator ──► {Operator}_Test_Design_Document.md
                                    │
                                    ▼
test-case-generator    ──► {Operator}_Test_Cases.json
                                    │
                                    ▼
test-script-generator  ──► tests/test_*.py  +  pytest.ini  +  config.json
                                    │
                                    ▼
test-runner            ──► reports/test_results.json  +  logs/*.log
                                    │
                                    ▼
test-report-generator  ──► reports/test_report.html
```

## 性能优化流水线

`omni-sql-perf-improvement` 依赖 `mcp-servers/spark-remote-mcp` 提供的工具，并按需调度两个子技能：

```
Phase 0c (基线正确性参照) ─► run_e2e_sql           [mcp-servers/spark-remote-mcp]
        │
        ▼
Phase 2a (Profiling)        ─► omni-flamegraph-operator-analysis
        │
        ▼
Phase 2b (Metrics 提取)     ─► extract-spark-ui-metrics
        │
        ▼
Phase 5 (正确性) / Phase 6 (性能)  ─► run_e2e_sql / run_spark_test_operator
```

### 目标用户

- 鲲鹏社区开发者
- 场景化应用开发者
- 内外部合作伙伴

## 免责声明

1. 本仓库中的 Agent Skills 内容、代码、配置及示例仅供技术参考和学习使用，不代表其适用于任何生产环境、商业场景或关键业务系统。
2. 开发者在使用本仓库内容时，应自行评估其安全性、兼容性和适用性。作者及贡献者不对因使用本仓库内容导致的任何直接或间接损失承担责任，包括但不限于数据丢失、系统故障、业务中断、经济损失等。
3. 本仓库内容可能涉及第三方依赖或接口调用示例，相关权限及合规性需由开发者自行核实。作者及贡献者不承担与第三方服务相关的任何责任。
4. 本仓库中的 Agent Skills 示例仅为功能演示，不保证其完整性、准确性、时效性。作者及贡献者有权随时修改或删除内容，无需另行通知。
5. 除非另有明确约定，本仓库所有内容均基于开源协议发布，不提供任何形式的技术支持、维护承诺或担保。
