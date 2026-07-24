# OmniOperator SQL 全链路性能优化

针对单条目标 SQL 在 Omni 引擎上进行端到端性能调优的技能 —— 覆盖分支管理、编译部署、基线采集、火焰图与 WebUI profiling、全链路瓶颈分析、研究驱动的优化设计、严格门控的正确性→性能验收与每轮追踪文档。

## 适用场景

- 需要对某条 TPC-DS / 自定义 SQL 在 Omni（Gluten 插件）上做综合调优
- 瓶颈横跨多个算子 / 多个 Stage，不能靠单算子 patch 解决
- 希望在「全链路视角」下识别热点并量化优化收益

## 前置条件

### 本地仓 + 远端集群

工作目录根路径下需存在以下代码仓 + 远端集群：

```
<workspace-root>/
├── OmniOperator/             ← OmniOperator 仓库（必需，基线分支 2026_330_poc）
├── Gluten/                   ← Gluten 仓库（必需，基线分支 2026_330_poc）
├── velox/                    ← Velox 仓库（可选，方案调研用）
├── mcp-servers/                                       # MCP 服务（必需，见下节）
│   └── spark-remote-mcp/                              # 提供本 skill 全部工具
└── .agents/
    └── skills/
        └── omni-sql-perf-improvement/   ← 本技能
            ├── SKILL.md                          # 完整 6 阶段流水线指引
            ├── README.md                         # 本文件
            ├── references/                       # 主题参考（基线、画像、瓶颈、优化、检查、案例）
            │   ├── 01-spark-baseline.md
            │   ├── 02-profiling-guide.md
            │   ├── 03-bottleneck-types.md
            │   ├── 04-optimization-patterns.md
            │   ├── 05-validation-checklist.md
            │   ├── 06-case-studies.md
            │   ├── 07-background-primer.md
            │   ├── 08-kunpeng-hardware-affinity.md
            │   └── 09-tpcds-operator-coverage.md
            └── scripts/
                ├── scrape_spark_execution.py
                └── scrape_stage_details.py
```

> 远端依赖：已配置好的 Spark YARN 集群 + `mgx_omni_compiler1` 编译容器 + 远端 `~/.omnioperator` 部署目录（详见 `SKILL.md` Phase 0）。

### MCP 服务依赖（必需）

本 skill 6 个 Phase 全部依赖 [mcp-servers/spark-remote-mcp/](../mcp-servers/spark-remote-mcp/) 提供的 11 个工具，**未配置 MCP 时整个流水线无法启动**：

## 测试环境约定

| 项目 | 值 |
|------|-----|
| 数据集 | TPC-DS 1T，库名 `tpcds_bin_partitioned_decimal_orc_1000` |
| `run_e2e_sql`（正确性） | `local[*]`，单次执行，Q23a 约 470s |
| `run_spark_test_operator`（性能） | YARN 集群，**冷 1 + 热 3** 连续调用取热均值，Q23a 约 62s |
| `run_e2e_sql_native` | 1T 数据 local 模式超时（>600s），**不可作为主要参照** |

## 流水线概览

```
Phase 0  ──► Phase 1  ──► Phase 2  ──► Phase 3  ──► Phase 4  ──► Phase 5  ──► Phase 6
分支/编译/  Baseline   Profiling   Diagnose    设计 +    正确性    性能
部署+基线   (热均值)   火焰图+WebUI  全链路瓶颈  编码     校验     验收
正确性参照
```

每阶段产物与退出标准详见 `SKILL.md` 主体。Phase 0c 必须先采集干净基线的 `run_e2e_sql` 结果行作为后续 Phase 5 的对照基准，避免后续迭代需要回退基线重新编译。

## 使用方法

直接告诉 AI 目标 SQL 与上下文，例如：

- "我要优化 Q23a 性能，跑完整流程"
- "Q7 跑出来 HashAgg 占比 60%，帮我做全链路分析"
- "这次专项的追踪文档我建在 `artifacts/q23a/`，请按 Phase 3/4 继续"

Skill 会按 Phase 0 → 6 顺序引导；如需跳到指定阶段（已有当日基线、复用历史 `result-operators.csv` 等），请明确说明。

## 职责边界

本技能是**端到端优化专项**，与下列技能协作而非替代：

- `omni-flamegraph-operator-analysis` — Phase 2a 调用，提供两级热点算子/函数 CSV
- `extract-spark-ui-metrics` — Phase 2b 调用，提供 HashAgg/Join/Sort 等算子的 edges 行数追溯

追踪文档默认位于 `<workspace-root>/artifacts/<sql-id>/iteration-<N>-<描述>.md`，火焰图产物位于同一根的 `flame-derived-<run>/` 子目录。详细目录约定见 `omni-flamegraph-operator-analysis/SKILL.md`。
