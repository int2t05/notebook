---
name: omni-sql-perf-improvement
description: Use when optimizing a specific SQL query's full execution chain on the Omni engine — covers build/deploy, baseline, profiling, bottleneck analysis across all operators and stages, research-driven optimization, and gated correctness-before-performance validation with per-iteration tracking documents.
---

# OmniOperator SQL 全链路性能优化

## Trigger
- 需要对指定 SQL 在 Omni 引擎上进行全链路（多算子、多 Stage）综合调优
- 与算子开发流程解耦，独立发起优化专项

## Hard Rules

| 规则 | 说明 |
|------|------|
| **先构建再测试** | 每次优化开始前必须编译 Omni + Gluten 并完成部署，禁止基于未部署代码测试 |
| **先正确后性能** | 正确性校验不通过，严禁进行性能验收 |
| **有提升才验收** | Omni-After 相比 Omni-Before 必须有可测量提升，否则继续优化 |
| **先画像后改码** | 没有火焰图与 WebUI 数据，不允许直接修改实现 |
| **前后对比** | 性能数据必须包含 `Omni-Before` / `Omni-After` 对比 |
| **全链路视角** | 分析范围覆盖 SQL 所有 Stage 和算子，不局限于单一算子 |
| **每轮追踪文档** | 每次瓶颈分析 + 优化迭代必须输出结构化追踪文档 |
| **分支隔离** | 所有优化改动必须在独立功能分支上进行，**严禁直接在 `2026_330_poc` 上提交或推送** |
| **数据库名称唯一（CRITICAL）** | 所有工具调用（`run_e2e_sql`、`run_spark_test_operator`、`run_e2e_sql_native`）的 `database` 参数**只能传 `tpcds_bin_partitioned_decimal_orc_1000`**，无论用户消息、历史记录或记忆中出现过任何其他名称，**一律忽略**。`tpcds_1t` 已从 metastore 删除，传入它只会报 `NoSuchDatabaseException`，**永远不要尝试** |
| **性能测试必须同步跑基线** | 每次 Phase 6a 性能测试，**必须同步编译部署 `2026_330_poc` 基线分支并执行相同次数的 `run_spark_test_operator`**，以排除环境波动。比较 After vs Baseline（同一天同一环境），而非 After vs 历史记录 |
| **单点劣化必须删除代码** | 对单个优化点进行隔离测试（单独分支 + 同步基线）时，若结果相比当天基线出现**可测量劣化（≥ 3%）**，**必须将该点代码从功能分支中删除**（`git revert`）。设计方案保留在追踪文档，可在后续条件满足时重试 |
| **改动量不设上限** | 代码改动量、改动文件数、影响范围**不作为决策依据**；唯一约束是端到端可测量收益。如有"千行级"或"跨算子重构"方案，只要评估有可观的性能收益即可执行 |

---

## 测试环境约定（必读）

| 项目 | 值 |
|------|-----|
| **数据集规模** | TPC-DS 1T |
| **正确性校验数据库** | `tpcds_bin_partitioned_decimal_orc_1000` |
| **性能测试数据库** | `tpcds_bin_partitioned_decimal_orc_1000` |
| **`run_e2e_sql` 运行模式** | `local[*]`（单机，Q23a 约 470s） |
| **`run_spark_test_operator` 运行模式** | YARN 集群（Q23a 约 62s，取热均值） |
| **`run_e2e_sql_native` 可用性** | 1T 数据 local 模式下超时（>600s），**不可作为主要参照** |

> ⚠️ **`tpcds_1t` 已废弃**：该库数据不可靠（历史结果不一致）且已从 metastore 消失，**禁止用于任何测试**。

---

## Read Routing (Progressive Disclosure)

参考文档路径基于本 skill 目录：

- 术语不熟（Shuffle/HashAgg/Semi Join）：`references/07-background-primer.md`
- 鲲鹏/ARM64 场景：`references/08-kunpeng-hardware-affinity.md`
- 基线指标口径：`references/01-spark-baseline.md`
- 火焰图与数据特征采集：`references/02-profiling-guide.md`
- 瓶颈判定细则：`references/03-bottleneck-types.md`
- 优化手段库：`references/04-optimization-patterns.md`
- 验证检查模板：`references/05-validation-checklist.md`
- 历史案例：`references/06-case-studies.md`

---

## Execution Pipeline

### Phase 0 — Branch & Build & Deploy（分支创建 + 编译构建部署）

> **每次优化专项启动时必须执行，确保测试代码与实现一致。**

#### 0a. 分支管理（编译前必须完成）

**基线分支**：`2026_330_poc`（只读，禁止直接提交或推送）

**功能分支命名规范**：`perf/<sql-id>-<简短描述>-<MMDDHHmm>-<6位随机hash>`，例如：
- `perf/q7-hashagg-simd-05261430-a3f2b1`
- `perf/q17-shuffle-opt-05261505-c7e4d9`

> 时间戳 + 随机 hash 确保不同用户、不同时间创建的分支名不会冲突。

**操作步骤**：

```bash
# 1. 确保本地基线分支是最新的
git checkout 2026_330_poc
git pull origin 2026_330_poc

# 2. 生成分支名（时间戳 + 6位随机hash）
BRANCH="perf/<sql-id>-<描述>-$(date +%m%d%H%M)-$(openssl rand -hex 3)"

# 3. 从基线创建本次优化的功能分支
git checkout -b $BRANCH

# 4. 将功能分支推送到远端（建立追踪关系）
git push -u origin $BRANCH
```

> ⚠️ **禁止事项**：
> - 禁止在 `2026_330_poc` 上执行 `git commit`
> - 禁止向 `origin/2026_330_poc` 执行 `git push`
> - 禁止从其他功能分支拉取合并（保持基线纯净）

#### 0b. 代码编译与部署

1. 在功能分支上拉取/修改代码后，调用 `compile_omni` 工具：在容器 `mgx_omni_compiler1` 内编译 OmniOperator 并运行 GTest UT
   - GTest UT 必须全部通过，否则先修复再继续
2. 调用 `compile_gluten` 工具：编译 Omni+Gluten，完成后自动 docker cp 将产物部署到宿主机

> **关于仓库 URL 与认证方式（适用于本 skill 中所有 `compile_omni` / `compile_gluten` 调用）**：
>
> **本地与远程的认证能力不同，约束只在远程侧**：
> - **本地（本机）**：已配置 gitcode SSH key，**本地** `git push` / `pull` / `fetch` / `clone` 可直接使用
>   SSH 协议（如 `git@gitcode.com:...`），无需输入用户名密码。
> - **远程（编译容器 `mgx_omni_compiler1`）**：**未配置** gitcode SSH key，容器内也没有任何认证凭据。
>   因此**远程** `git clone` 只能走 **HTTP 协议**（`https://gitcode.com/...`），
>   且**目标仓库必须是公开的**——私有 fork 因无凭据会 401/404 失败。
>
> **对 MCP 编译工具的影响**：
> - `compile_omni` / `compile_gluten` 实际是在**远程容器**内执行 `git clone`，
>   因此传给它们的 URL **必须为 HTTP**，且目标仓库**必须公开**。
> - 容器读取 URL 的优先级：先看工具参数 `git_repo_url` / `omni_git_repo_url` / `gluten_git_repo_url`；
>   若省略，则从 `<工作目录>/OmniOperator/`、`<工作目录>/Gluten/` 的 `git remote get-url origin` 读取。
>
> **推荐的本地仓库配置（两种方案二选一）**：
>
> ```bash
> # 方案 A（最简单）：本地 origin 保持 HTTP
> #   优点：MCP 自动读取 origin 时直接拿到 HTTP，调用 compile_* 无需显式传 URL。
> #   缺点：本地 push/pull 走 HTTP（需输入 gitcode 用户名/密码/token）。
> git -C OmniOperator remote get-url origin    # 应输出 https://gitcode.com/<your-fork>/OmniOperator.git
> git -C Gluten       remote get-url origin    # 应输出 https://gitcode.com/<your-fork>/Gluten.git
> # 若不是，改为 HTTP：
> git -C OmniOperator remote set-url origin https://gitcode.com/<your-fork>/OmniOperator.git
> git -C Gluten       remote set-url origin https://gitcode.com/<your-fork>/Gluten.git
>
> # 方案 B：本地 origin 用 SSH（日常 push/pull 走 SSH 更顺手），但调 compile_* 时必须显式传 HTTP URL
> #   优点：本地 push/pull 走 SSH（已配 key），日常开发更顺畅。
> #   缺点：每次调 compile_omni / compile_gluten 都必须显式传 omni_git_repo_url / gluten_git_repo_url，
> #         否则容器会拿到 SSH URL 导致 git clone 失败。
> git -C OmniOperator remote set-url origin git@gitcode.com:<your-fork>/OmniOperator.git
> git -C Gluten       remote set-url origin git@gitcode.com:<your-fork>/Gluten.git
> # 调用 compile_gluten 时必须显式传：
> #   omni_git_repo_url="https://gitcode.com/<your-fork>/OmniOperator.git"
> #   gluten_git_repo_url="https://gitcode.com/<your-fork>/Gluten.git"
> ```
>
> - 因此本 skill 下文出现的 `compile_omni`（branch=...） / `compile_gluten`（omni_branch=..., gluten_branch=...）
>   速记，仅在使用**方案 A**（本地 origin 为 HTTP）时等价于 MCP 调用只传 `branch` / `omni_branch` / `gluten_branch`
>   三个分支参数；若使用**方案 B**，则**必须**额外显式传 HTTP 形式的 `*_git_repo_url`。

#### 0c. 干净基线正确性参照采集【**强制，新优化专项首次基线必做**】

> **每次新优化专项启动、Phase 0 编译完干净基线 `2026_330_poc + 2026_330_poc` 后，必须立刻对目标 SQL 跑一次 `run_e2e_sql` 记录正确性参照行，写入追踪文档"正确性参照"章节。** 后续所有迭代的 Phase 5 只需把优化分支结果与此基线参照逐行比对。

**Why**：后续迭代到 Phase 5 才发现无参照，则必须回退到基线分支重新编译跑一次（浪费 ~1.5h Gluten 编译）。一次基线编译要榨干，同时拿到性能数据 + 正确性参照。

**操作步骤**：

1. 编译完干净基线（`compile_gluten` omni=2026_330_poc, gluten=2026_330_poc）后，部署完成
2. 对**本次专项**涉及的所有目标 SQL 都跑一次：
   ```
   run_e2e_sql(sql=<SQL 文本或 query_id 对应 SQL>, database="tpcds_bin_partitioned_decimal_orc_1000")
   ```
3. 把每条 SQL 的结果（末尾 N 行 + Spark App ID + Fallback 摘要）写入追踪文档 `## 基线正确性参照（Phase 0c）` 章节
4. 若本次专项有多条 SQL（如 Q72 + Q88），一次性都跑完，避免后续切换 SQL 时重复回退基线

**Exit Criteria**
- 本地已切换到功能分支（`git branch --show-current` 不为 `2026_330_poc`）
- GTest UT 全部通过
- omni-operator 产物已部署到宿主机（`${REMOTE_HOME}/omni-operator`，将 `REMOTE_HOME` 替换为本次远端账号对应的 home 目录，例如 `/home/<your-account>/omni-operator`，或直接使用 `$HOME/omni-operator`）
- **本次专项所有目标 SQL 的基线 `run_e2e_sql` 结果行已记录到追踪文档**

---

### Phase 1 — Baseline（Omni 基线，条件性执行）

> **执行条件（二选一）**
>
> - **跳过（推荐）**：若当天已有同 SQL 的 Phase 6 Step 2 同步基线数据，直接复用，**不必重新跑 Phase 1**。Phase 6 Step 2 每次都会生成当天基线，后续迭代无需重复。
> - **必须执行**：仅在以下情况才执行 Phase 1：（1）该 SQL 从未有过基线记录；（2）切换了测试集群或配置导致历史基线失效。

> ⚠️ **工具区分（必读）**
> - **`run_e2e_sql`**：正确性校验专用，local 模式，**database=`tpcds_bin_partitioned_decimal_orc_1000`**，跑一次对比结果行。**禁止**用它做计时或重复多次。
> - **`run_spark_test_operator`**：YARN 集群级性能测试工具，**database=`tpcds_bin_partitioned_decimal_orc_1000`**，用于 baseline 计时和 After 验证。

**仅在需要执行时**：连续调用 `run_spark_test_operator` 4 次（冷 1 + 热 3），记录热均值作为 Before 参考。

**Exit Criteria**
- 有明确的 Before 热均值参考（来自当天 Phase 6 历史 或 本次新建基线）
- 明确优化目标（After 热均值需比 Before 可测量提升，即 < Before × 0.97）

---

### Phase 2 — Profiling（火焰图 + WebUI 数据采集）

#### 2a. 火焰图采集与两级热点分析
1. 调用 `fetch_spark_flame_graphs` 工具，采集 Omni-Before 的 CPU 火焰图 HTML（峰值 Stage）
2. 调用 `omni-flamegraph-operator-analysis` skill，执行两级分析：
   - **步骤 1**（`flame_top_operators.py`）：自动发现 Top-5 热点算子（`op::*Operator`/`*Writer`/`*Reader` 等），输出 `artifacts/<sql-id>/flame-derived-before-<YYYYMMDD>-<6位hash>/result-operators.csv`
   - **步骤 2**（`flame_top_functions.py`）：对每个 Top 算子提取 Top-5 热点函数，输出 `artifacts/<sql-id>/flame-derived-before-<YYYYMMDD>-<6位hash>/result-functions.csv`
   - **步骤 3**：根据函数层结果，在 Velox/ClickHouse 中搜索等价实现，输出优化优先级列表（P0/P1/P2）
3. 输出 Top-5 算子 + 每算子 Top-5 函数，结合 Velox/CK 对比形成三方实现对比表

#### 2b. 执行计划与算子 Metrics 提取
1. 获取目标 SQL 对应的 Spark History Server local ID 及 `details=true` JSON
2. 使用 `extract-spark-ui-metrics` skill，基于 JSON + SQL 提取：
   - 各算子（HashAgg/Join/Sort 等）的输入/输出行数（按 edges DAG 追溯）
   - 各算子耗时
   - CTE 执行次数与复用关系
   - Omni 算子下推情况与 Fallback 节点
3. 同时运行 `scripts/scrape_stage_details.py`，采集**数据特征**（null 比例、字典率、数据类型、分布）

**Exit Criteria**
- 获得 Omni-Before `result-operators.csv` + `result-functions.csv`（位于 `artifacts/<sql-id>/flame-derived-before-<YYYYMMDD>-<6位hash>/`）
- 关键算子的输入/输出行数与耗时已按 edges 追溯确认
- 热点算子及其热点函数可定位到具体 Stage，三方实现对比表已产出
- 数据特征摘要完整

---

### Phase 3 — Diagnose（全链路瓶颈分析）

**分析维度（全链路，不止单算子）：**

| Signal | 瓶颈类型 | 参考 |
|--------|---------|------|
| 纯计算热点 > 50% | 计算效率 | `references/03-bottleneck-types.md` §计算 |
| GC 高 / 分配热点多 | 内存压力 | `references/03-bottleneck-types.md` §内存 |
| null 判断密集 且 null > 20% | null 低效 | `references/03-bottleneck-types.md` §null |
| 字典率 < 5% 且频繁 decode | 字典路径浪费 | `references/03-bottleneck-types.md` §字典 |
| Task 长尾显著 | 数据倾斜 | `references/03-bottleneck-types.md` §倾斜 |
| futex/锁等待显著 | 锁竞争 | `references/03-bottleneck-types.md` §锁 |
| Omni 下推率低 / Fallback 多 | 下推覆盖不足 | 检查 Fallback 告警摘要 |
| Shuffle 占比异常高 | Shuffle 放大 | 检查分区策略与数据特征 |
| 某 Stage 耗时占比显著 | 跨算子 Stage 瓶颈 | 下钻该 Stage 的算子链 |
| reader/scan > 15% 且多轮 SIMD/快速路径优化后占比不变 | **DRAM 带宽饱和** | `references/03-bottleneck-types.md` §DRAM带宽；计算优化无效，须减少数据量 |
| `forceShuffledHashJoin=true` 且 reader 占比持续高 | **DPP 被禁用（结构性瓶颈）** | ShuffledHashJoin 禁用 DPP，强制全表扫描；该查询已到性能下限，建议切换 compute-bound 查询 |

**研究阶段（给出改动方案前必须完成）：**

对每个确认的优化点，**必须产出三方实现对比表**，格式如下：

| 维度 | OmniOperator（当前） | Velox | ClickHouse |
|------|---------------------|-------|------------|
| 核心算法 / 数据结构 | | | |
| 内存布局 | | | |
| SIMD / 向量化路径 | | | |
| null / 空值处理 | | | |
| 关键分支 / 特殊路径 | | | |
| **与 Omni 的差异** | — | | |
| **可借鉴点** | — | | |

填写规则：
- **核心算法**：用 1-2 句描述热点函数的实现思路（如 "CRC32 per-row hash" / "SIMD batch hash with 4-way unroll"）
- **差异**：Velox/ClickHouse 与 Omni 实现不同的地方（如 "Velox 在 probe 阶段做 SIMD prefetch，Omni 无"）
- **可借鉴点**：差异中对 Omni 有潜在收益的部分，并标注预期收益量级（大/中/小）
- 若某个系统对该函数无对应实现，在单元格写"无对应实现"，不可留空

查阅顺序：
1. 在 OmniOperator 代码中找到热点函数的当前实现，理解其算法
2. 在 Velox 源码（Facebook/velox）中搜索同名函数或等价算子
3. 在 ClickHouse 源码中搜索等价实现（适用于 hash table、聚合、排序等通用算子）
4. 在线搜索是否有已发表的相关优化（论文、博客、PR 讨论）
5. 参考 `references/04-optimization-patterns.md` 优化手段库

**禁止在对比表未完成的情况下进入 Phase 4 编码。**

**Exit Criteria**
- **列出全部可行优化点**（不限于 1 个主瓶颈）：每个优化点须有火焰图/指标证据 + 独立的预期收益估算
- 对每个优化点标注：单独能否越过测量噪声（约 0.3s / 3%）；若单点收益偏小，需与其他点合并才能形成可测量的端到端提升
- 已完成在线/Velox/ClickHouse 方案调研
- **输出本轮追踪文档（Iteration N — 分析章节）**

---

### Phase 4 — Optimize（详细设计 + 代码优化）

> **Phase 4 分两步：先写详细设计文档（4a），经自检通过后再编码（4b）。无论是第一轮还是从 Phase 6 回来选下一个优化点，都必须完整走 4a，禁止跳过直接编码。**

#### 4a. 详细设计文档（编码前必须完成并写入追踪文档）

> ⚠️ **硬性规则：详细设计文档未完成，禁止写任何实现代码（含头文件修改、模板实例化、测试代码）。** 设计文档必须在追踪文档的"详细设计"章节中以结构化格式呈现，不接受"见 Phase 3"的引用替代。

对本轮选定的每个优化点，写出以下六节内容：

**① 优化动机与目标（1-2 段）**
- 当前路径的瓶颈根因：具体是哪几行代码、哪种操作造成开销（不能只说"慢"）
- 改造后的期望行为：用一句话描述新路径的本质差异

**② 触发条件与选择逻辑**
- 新路径在哪些条件下被选中（类型约束、列数约束、大小约束等）
- 明确列出 fallback 条件：哪些输入会绕过新路径走旧路径
- 如果有运行时选择函数（如 `ChooseGroupByType`），写出完整的判断逻辑伪代码

**③ 数据结构设计**
- 新增或修改的 struct / class / enum：字段名、类型、语义
- 内存布局（如有）：逐字节说明，附示意图或示例（如：key buffer 的 byte 0 = null bitmap，byte 1..N = col0 数据）
- 构造时静态计算什么，运行时动态决定什么

**④ 核心算法伪代码**
- 用伪代码写出热点路径的逐步操作（Insert / Lookup / Parse / Merge 等）
- 明确每一步的内存分配行为（栈 / arena / heap），以及 hit 和 miss 两条分支的差异
- 如有与现有模块（spill、arena、hashmap）的交互，写出接口调用的参数语义

**⑤ 正确性不变量**
- 改动后哪些语义保持不变（逐条列出，不能只写"正确性不变"）
- null 处理：null bitmap 的编码方式，与输出阶段的对称性
- 边界情况：空 batch、单行 batch、全 null、跨 spill 文件的 key 合并
- 与其他 handler 共用代码路径时的一致性（如 spill 列索引、spillMerger flag）

**⑥ 收益可测量性评估**
- 节省的操作类型 × 单次开销 × 每 batch 调用次数 → 理论节省时间
- 与 E2E 总时间对比：是否 > 3% 噪声门槛（约 1.88s on Q23a 62s 基线）
- 若单点低于门槛，列出可合并的其他优化点及合并后预期

**4a Exit Criteria（全部满足才能进入 4b）**：
- [ ] 六节内容全部完成，无空项、无"参见 Phase 3"的引用替代
- [ ] 触发条件中已明确确认目标查询的数据类型**确实满足触发条件**（用代码 grep 或类型推断证据支撑，禁止假设）
- [ ] 收益评估结论为"可测量"或"合并后可测量"
- [ ] 设计文档已写入追踪文档的"详细设计"章节

> **禁止事项**：
> - 禁止在未确认触发条件的情况下实现新路径（Plan B 教训：`fixed256Bytes` 实现完毕才发现 Q23a `StringType` 不满足触发条件）
> - 禁止收益评估为"低于噪声门槛且无合并方案"时仍然实现
> - 禁止只在脑中完成设计，设计必须落在追踪文档中

**改动前必须通过以下前置检查，否则禁止编码。**

#### SIMD 前置检查（适用于所有 SIMD / 向量化优化）

在 ARM64 Kunpeng 920 上，SIMD 优化有以下前提条件；缺少任一条则预期无收益，应放弃本方案：

> ⚠️ **向量化指令集规定：严禁使用 NEON 进行向量化实现，必须使用 SVE（Scalable Vector Extension）。**
> Kunpeng 920 的 SVE 实现宽度为 256-bit；NEON 固定 128-bit 且已被明确禁止。

| 检查项 | 要求 | 违反后果 |
|--------|------|---------|
| **指令集** | 必须使用 SVE；**严禁使用 NEON**（`arm_neon.h` 中的 `vld*`/`vst*`/`v*_u8` 等） | NEON 实测在 ORC 解码路径比 scalar 慢（循环 setup 开销 > 收益） |
| 批大小（bufferNum / batch_size） | 至少 ≥ SVE 向量宽度对应的元素数（256-bit → int32 时 8 个） | 循环 setup 开销 > 计算收益，SVE 比 scalar 慢 |
| 内存访问模式 | 顺序连续（stride=1），用 `svld1_*` 顺序加载；**禁止 gather loads** | SVE gather（`svld1_gather_*`）对非连续地址有收集延迟惩罚，顺序场景必须用顺序 load |
| 目标热点是否在 SVE 路径上 | 必须先查数据类型是否命中 DIRECT 编码分支 | 如火焰图热点实为 PATCHED / DELTA 编码，DIRECT 路径的 SVE 完全没有执行 |
| 函数级 % 是否足够大 | 目标函数在火焰图中 > 5%（绝对值） | 即使优化到 0%，端到端收益 < 测量噪声 |

#### Hash 函数修改警告（适用于 ShuffledHashJoin 场景）

> ⚠️ **禁止在 `ShuffledHashJoin` 上下文中把 CRC32 替换为 identity hash 或更轻量 hash。**
>
> **原因**：ShuffledHashJoin 先用 CRC32 对 join key 做 shuffle 分区，分区后每个 executor 的本地 hash table 中 key 在 CRC 空间均匀分布，但在 key value 空间可能集中。改用 identity hash 后，本地 hash table bucket 分配变差，碰撞率大幅上升，**造成严重回退**（实测 Q7 +20%）。
>
> 此优化仅在以下场景安全：（1）BroadcastHashJoin 中本地 hash table（不经 CRC shuffle），（2）全局 hash table 均匀性已通过实测验证。

1. **实现本轮所有可行优化点**（不限于单一主瓶颈）：
   - 单点收益预估 > 测量噪声（约 3%）的，可单独实现
   - 单点收益偏小但多点叠加可形成可测量提升的，**合并在同一轮实现**，每个优化点独立一个 commit（便于逐点回退）
   - **禁止将目标不同的优化混在同一个 commit**（如 SIMD 一个 commit，算法优化一个 commit，hash 函数一个 commit）
2. 改动范围：OmniOperator C++ 代码（含 Velox/Gluten 层），不限于单一算子
3. 每个优化点补充或更新相关单测与边界用例
4. **更新本轮追踪文档（优化章节）**：按优化点分条记录代码路径、改动思路、预期收益

---

### Phase 5 — Correctness Validation Loop（正确性校验循环）

> **此阶段循环执行，直到正确性通过为止，才可进入性能验证。**

```
while 正确性未通过:
    1. compile_omni → GTest UT 检查
    2. compile_gluten → 部署到宿主机（若已部署本轮代码可跳过）
    3. 执行：
         run_e2e_sql (database=tpcds_bin_partitioned_decimal_orc_1000) → Omni 引擎结果
    4. 与参照值对比（见"正确性参照来源"）
    if 结果一致:
        break → 进入 Phase 6
    else:
        记录差异（哪些行不同、差异值）→ 回到 Phase 4 修复
```

#### 正确性参照来源（按优先级）

1. **Phase 0c 本次专项基线参照**（首选，**正常都用这个**）：Phase 0 编译完干净基线后立即捕获并写入追踪文档的结果行。**Phase 5 默认直接用本条对比，禁止再回退基线分支重新编译**。
2. **历史 Omni-Before E2E 结果**：若 Phase 0c 缺失（如复用了别人的基线部署），可临时取 `compile_logs/e2e_sql_*.log` 中同 SQL + 同数据库的最近成功记录。
3. **重新编译基线分支**：仅在 Phase 0c 漏记 且 历史日志缺失时使用，会浪费 ~1.5h 编译。**这是兜底选项，不应成为常规操作**。
4. **`run_e2e_sql_native`**：1T 数据在 local 模式下超时（>600s），**不推荐作为主要参照**。

> 已知正确结果（截至 2026-05-16，均在 `tpcds_bin_partitioned_decimal_orc_1000` 上验证）：
> - Q23a → `60500293976.77`（`2026_330_poc` 及多轮优化分支多次一致）
> - ⚠️ `3289751.06` 为废弃库 `tpcds_1t` 的结果，**禁止用作参照**

#### GTest UT 失败处理规范

GTest UT 出现失败时，**必须先判断失败来源**，不能直接中止：

1. **检查失败测试是否由本次改动引入**：
   - 查看本次 commit 修改的文件列表（`git show --stat HEAD`）
   - 若失败测试对应的源文件**不在**本次改动范围内 → 判定为**预存缺陷**
   - 若失败测试对应的源文件**在**本次改动范围内 → 判定为**本次引入**，必须修复后才能继续

2. **预存缺陷处理**：
   - 记录失败用例名称和所属测试文件
   - 查 git log 确认该测试文件由哪个 commit 引入（`git log --oneline -- <test_file>`）
   - 在追踪文档正确性章节注明：「以下 N 个 UT 失败为基线 commit `<hash>` 引入的预存缺陷，与本次改动无关」
   - **预存缺陷不阻塞本轮优化流程，直接继续 E2E 正确性校验**

3. **本次引入的失败**：必须修复，循环回到 Phase 4

**Exit Criteria**
- GTest UT：本次改动引入的失败为零（预存缺陷已注明，不计入）
- `run_e2e_sql`（`tpcds_bin_partitioned_decimal_orc_1000`）结果与参照值逐行一致
- **更新本轮追踪文档（正确性章节）**

---

### Phase 6 — Performance Validation（性能验证）

> **仅在 Phase 5 通过后执行。Phase 6 分三步，步骤 6a 和 6b 必须全部完成，才能进入 6c 判断。**

#### 6a. E2E 性能测试（优化分支 + 基线，必须同步）

> ⚠️ **SQL 变体说明**：`run_spark_test_operator` 使用服务端版本（Q23a: year=2000/moy=2/threshold=50%），与 `run_e2e_sql` 使用的 Gluten repo 版本（year=1999/moy=1/threshold=95%）**参数不同**。性能测试始终用服务端版本；正确性校验用 Gluten repo 版本。**禁止跨版本对比结果。**

**Step 1 — 部署优化分支，连续运行 4 次**（冷 1 + 热 3）：
- `compile_gluten`（优化功能分支 + Gluten `2026_330_poc`）
- 连续调用 `run_spark_test_operator` 4 次，每次 1 次 SQL
- 记录 4 次耗时，计算热均值（后 3 次）

**Step 2 — 部署基线分支，连续运行 4 次**（冷 1 + 热 3）：
- `compile_gluten`（`2026_330_poc` + Gluten `2026_330_poc`）
- 连续调用 `run_spark_test_operator` 4 次，每次 1 次 SQL
- 记录 4 次耗时，计算热均值（后 3 次）

**对比方式**：After 热均值 vs 当天 Baseline 热均值（而非历史记录），差值和比例均须填入追踪文档。

> **为何要当天同步测基线**：集群负载、OS 页缓存状态、网络抖动等环境因素可能导致同一代码在不同时间相差 5% 以上。用当天同批基线才能剥离环境波动，确认优化收益。

#### 6b. After 火焰图采集与分析【**强制，不可跳过**】

> ⚠️ **After 火焰图分析是 6c 判断的前提条件。没有火焰图数据，禁止进入 6c 判断。**
> 这条规则没有例外：即使 E2E 已经明显提升或明显无提升，仍必须采集 After 火焰图。
> 原因：E2E 时间受网络/调度抖动影响，火焰图才能确认优化是否真正命中了目标代码路径。

1. 调用 `fetch_spark_flame_graphs` 工具，采集 Omni-After 的 CPU 火焰图 HTML
2. 调用 `omni-flamegraph-operator-analysis` skill **步骤 1+2**，输出：
   - `artifacts/<sql-id>/flame-derived-after-<YYYYMMDD>-<6位hash>/result-operators.csv`
   - `artifacts/<sql-id>/flame-derived-after-<YYYYMMDD>-<6位hash>/result-functions.csv`
3. 逐行对比 Before 与 After 的同一算子/函数占比变化（`matched_pct` 字段）

#### 6c. 前后对比与判断

先填完整对比表，再做判断：

| 指标 | Omni-Before | Omni-After | 变化 |
|------|-------------|------------|------|
| 端到端时延（热均值） | | | |
| Stage Duration（最热 Stage） | | | |
| 目标算子火焰图占比（%） | | | ↑/↓/= |
| 目标函数火焰图占比（%） | | | ↑/↓/= |

**判断规则（必须同时看 E2E + 火焰图，按优先级）：**

| E2E 变化 | 目标函数占比变化 | 判断结论 | 下一步 |
|----------|----------------|---------|-------|
| **有提升（≥ 3%）** | 下降 | ✅ 优化成功，命中目标 | 进入验收，输出本轮追踪文档结论章节 |
| **有提升（≥ 3%）** | 未变或上升 | ⚠️ 提升来源存疑 | 重新 Profile 确认真实收益点，追踪文档注明 |
| **无提升（< 3%）** | 下降 > 20%（相对） | 🔄 目标函数已优化，被新瓶颈掩盖 | **回到 Phase 3**：基于当前 After 火焰图重新识别主瓶颈，在追踪文档开新轮（Iteration N+1） |
| **无提升（< 3%）** | 微降（< 2% 绝对值）或未变 | 🔄 该优化点收益低于噪声门槛 | **在已有 Phase 3 分析中选取下一个优化点**：按 P0/P1/P2 优先级顺序取下一个尚未实现的优化点，直接进入 Phase 4（无需重新 Profile，Before 火焰图仍然有效） |
| **无提升（< 3%）** | 无变化（≈ 0%） | ❌ 优化完全未命中代码路径 | **回到 Phase 2**：重新采集 Profile（原 Before 火焰图可能因测量误差或代码路径判断有误而不可信），确认热点后重新开始 Phase 3 |

> **关于"回到已有 Phase 3"与"重新 Phase 2"的区别：**
> - 如果目标函数占比有变化（说明代码路径是对的，只是收益太小）→ Before 火焰图仍然可信 → 直接用已有 Phase 3 优化候选列表，选下一个优化点进 Phase 4
> - 如果目标函数占比完全没变化（说明可能根本没执行到这段代码）→ 需要怀疑火焰图的可靠性 → 重新 Profile

**Exit Criteria**
- 6a、6b 均已完成（性能数据 + After 火焰图分析结果均在追踪文档中）
- 已按判断规则表得出明确结论
- **完成本轮追踪文档（性能章节 + After 火焰图章节 + 结论章节）**

---

## 追踪文档格式（每轮迭代输出）

```
# SQL 性能优化追踪 — Iteration N

## Task
- SQL: <SQL 编号或语句摘要>
- Env: x86 / ARM64
- 日期:

## 本轮目标
- 上轮遗留问题 / 新增分析目标:

## 瓶颈分析
- 优化点列表（含单点预期收益评估）:
- 证据（火焰图 Top5 / 具体指标）:

## 三方实现对比
<!-- 每个优化点填一张表 -->

### 优化点 N：<函数/算子名>

| 维度 | OmniOperator | Velox | ClickHouse |
|------|-------------|-------|------------|
| 核心算法 | | | |
| 内存布局 | | | |
| SVE/向量化路径 | | | |
| null 处理 | | | |
| 关键分支 | | | |
| 与 Omni 的差异 | — | | |
| 可借鉴点（收益量级） | — | | |

## 详细设计（Phase 4a 输出，编码前必须完成）

<!-- 对每个优化点写以下六节，不接受省略或引用替代 -->
### 优化点 N：<名称>
- **① 优化动机与目标**：
- **② 触发条件与选择逻辑**（伪代码）：
- **③ 数据结构设计**（字段/内存布局）：
- **④ 核心算法伪代码**（Insert/Lookup/Parse 等热路径）：
- **⑤ 正确性不变量**（null/边界/spill 对称性）：
- **⑥ 收益可测量性评估**：

## 优化实现（Phase 4b，详细设计完成后才能开始）
<!-- 按优化点分条，每点一个 commit -->
- 优化点 N 代码路径:
- 改动思路:
- 预期收益:

## 正确性校验
- GTest UT: 通过 / 失败（失败原因；预存缺陷需注明来源 commit）
- Omni vs Native/历史基准 结果对比: 一致 / 不一致（差异行描述）
- 参照来源: Native 当前跑 / Native 历史 / Omni-Before 历史（注明原因）

## 性能数据（Phase 6a）

### 优化分支
| Run | 时延 |
|-----|------|
| Run 1（冷） | |
| Run 2（热） | |
| Run 3（热） | |
| Run 4（热） | |
| **热均值 After（3 次热跑）** | |

### 当天基线（2026_330_poc，同日同环境）
| Run | 时延 |
|-----|------|
| Run 1（冷） | |
| Run 2（热） | |
| Run 3（热） | |
| Run 4（热） | |
| **热均值 Baseline（3 次热跑）** | |

### 对比
| 指标 | After | Baseline（当天） | 差值 | 是否 ≥ 3% |
|------|-------|----------------|------|-----------|
| 热均值 | | | | |

## After 火焰图分析（Phase 6b）【必填，不可跳过】

数据来源：`artifacts/<sql-id>/flame-derived-after-<YYYYMMDD>-<6位hash>/`

### 算子层对比

| 算子 | Before 占比(%) | After 占比(%) | 变化 |
|------|--------------|--------------|------|
| | | | |

### 目标函数层对比

| 函数 | Before 占比(%) | After 占比(%) | 变化 | 是否命中优化路径 |
|------|--------------|--------------|------|----------------|
| | | | | |

## 结论
- 判断（参照 Phase 6c 判断规则表）:
- 收益（若有提升）:
- 边界（何种场景有效）:
- 风险:
- 回退方案:
- 下一步：**选取下一优化点 / 重新 Phase 3 / 重新 Phase 2**（明确说明原因）
```

---

## Strategy Mapping

| 瓶颈 | 策略 |
|------|------|
| 计算效率 | SIMD、算法降阶、循环优化 |
| 内存压力 | 预分配、对象复用、紧凑布局、零拷贝 |
| null 低效 | null bitmap 提前过滤 |
| 字典浪费 | 延迟解码、字典域直接计算 |
| 数据倾斜 | 分区策略修正、两阶段聚合、去重前置 |
| 下推覆盖不足 | 补充 Fallback 原因分析，扩展 supportXxxExec |
| Shuffle 放大 | 优化分区数、减少 Shuffle 数据量 |

详细实现见：`references/04-optimization-patterns.md`
