---
name: extract-spark-ui-metrics
description: Extracts Spark History Server JSON (details=true) into the mandatory metrics document structure—HashAgg input/output rows via edges, CTE execution count/reuse, full SQL appendix. Use for "根据 xxx.sql 和 xxx.json 提取文档", q23a-zx.json-style API, HashAgg tables, or CTE reuse. Do not substitute a narrative-only physical plan for this structured output.
---

# 从 Spark UI / API 提取 Metrics 的技能

## 如何使用

- **触发方式**：在对话中提到"从 Spark UI / API 提取 metrics""解析 q23a-zx.json""整理 HashAgg 行数""写执行计划文档""CTE 执行次数"等，或提供 JSON/SQL 路径并让 Agent 提取、校对、写文档时，会按本技能执行。
- **简短指令等价于本技能（重要）**：用户只说 **「根据 `path/xxx.sql` 和 `path/xxx.json` 提取文档」**（或「整理成 metrics 文档」「按技能写 q4 文档」）且两处路径指向**本次执行**的 SQL + `details=true` JSON 时，**必须**按下文 **「文档必须结构（强制）」** 完整产出；**禁止**仅用「物理计划要点 / 算子叙述 / 热点定性」代替第 2–5 节表格与 **附录完整 SQL**。若用户**另行**只要计划树解读，应明确要求「不要按 metrics 技能结构，只要 plan 说明」以免混淆。
- **使用前准备**：  
  1）有 Spark History Server 某次 SQL 执行的 **JSON**（`details=true`），建议已保存为项目内文件（如 `sql/xxx.json`）；  
  2）有与该执行对应的 **SQL** 文件（如 `sql/xxx.sql`）。  
  两者齐备后，请 Agent 基于 JSON + SQL 做提取与文档即可。
- **典型请求示例**：  
  - "根据 `examples/q23a-zx.json` 和 `examples/q23a-zx.sql`，提取所有 HashAgg 的输入输出行数，写成文档。"  
  - "根据 `examples/q4.sql` 和 `examples/q4.json` 提取文档。"（与上条等价，输出须为技能结构，非仅计划叙述。）  
  - "校对/补充文档里的 max_store_sales 对应的 HashAgg 信息，结合 JSON 和 SQL。"  
  - "解释为什么 frequent_ss_items 执行 3 次、best_ss_customer 执行 2 次。"

## 何时使用

- 需要从 Spark History Server 的 API 或 UI 提取算子级 metrics（如输入/输出行数）
- 解析 `details=true` 返回的 JSON，整理成表格或文档
- 区分子查询/CTE 的执行次数与复用关系
- 将物理计划节点与 SQL（含 WITH/CTE）逐段对应

## 与本仓库批量脚本的关系

- **技能（本文件）**定义的是**文档结构、metrics 含义与归属原则**；不依赖特定目录布局。
- **批量实现**在仓库内单独维护：**`subop-knowledge/benchmarks/tpcds/results/20260313-cluster/extract_metrics_docs.py`**（位于该 **cluster 目录根下**，与 `spark-queries-tpcds/`、`tpcds-sparkui-json/`、`spark-metrics-derived/` 等同级）。用于按同名 `qxx.sql` + `qxx.json` 成批生成与上文**同一类**的 `qxx-metrics.md`，须显式传入 `--sql-dir`、`--json-dir`；可选 `--out-dir`，默认目录名为 `spark-metrics-derived`，**若已存在则依次尝试** `spark-metrics-derived-2`、`-3`… 直至可用（详见 cluster **`README.md`**）。**勿在 `.cursor/skills/` 下重复存放** `extract_metrics_docs.py`，以 cluster 下文件为唯一真源；**运行方式与参数**见 **`subop-knowledge/benchmarks/tpcds/results/20260313-cluster/README.md`** 中 **「Spark UI / metrics（计划与算子级文档）」** 小节（示例命令及 `--sql-dir` / `--out-dir` 等）。
- **启发式与预期**：批量脚本是 **启发式**工具，**不能替代** 基于 **`edges`/`nodes`** 的结构化追溯或 **按本 skill 的手工核对**；生成的 `qxx-metrics.md` 宜视为 **初稿**，歧义或敏感题（如 **q23a** 类）须复核。
- **Agent 行为建议**：用户要整批 TPC-DS metrics 或路径落在上述 cluster 布局时，**优先建议或执行**该 Python，而非手搓数十个文件；单题、任意路径的 SQL+JSON 仍可按本技能手写/校对。

## 数据来源

提取与文档依赖**两处**：

- **JSON（计划与 metrics）**：来自 Spark History Server API，`http://<host>:18080/api/v1/applications/<appId>/sql/<executionId>?details=true`。例如：`http://<host>:18080/api/v1/applications/application_1765972724156_1813/sql/0?details=true`。返回中：
  - `nodes[]`：每项含 `nodeId`、`nodeName`、`metrics[]`（如 `name` / `value`）
  - `edges[]`：`fromId`、`toId`，表示计划 DAG 的边  
  建议将响应保存为项目内 JSON 文件（如 `sql/q23a-zx.json`），便于重复解析与版本对应。
- **SQL（语义与对应关系）**：与本次执行对应的查询文件（如 `sql/q23a-zx.sql`）。用于把节点对应到具体 CTE/片段、写"对应 SQL 逻辑"和说明、区分子查询与主查询；子查询小节与附录中贴的 SQL 也来自该文件。

## JSON 与 SQL 的分工

- **仅以 JSON 为准**：所有行数（input/output）、nodeId、stageId、DAG 边（edges）。谁连谁、在哪个 stage、读入/写出多少行，一律从 `nodes[].metrics` 与 `edges` 得到。
- **必须结合 SQL**：某 nodeId 对应**哪一段 SQL**（哪个 CTE、内层还是外层、FROM 哪些表、GROUP BY 什么）。否则只能列出"节点 83：入 2,685,588,011、出 12,000,000"，无法判断是 max_store_sales 内层还是 best_ss_customer；表格中的"对应 SQL 逻辑""说明"列也依赖对 SQL 的阅读与标注。
- **总结**：数值与计划结构信 JSON；语义对应与文档表述结合 SQL 一起分析。

## 输入行数 / 输出行数

- **输出行数**：直接从该节点的 metrics 中取 `"name" : "number of output rows"` 的 `value`。
- **输入行数**：由**上游节点**得到：
  - 在 **edges** 中找 `toId == 当前 nodeId` 的边，其 `fromId` 即直接上游；
  - **必须**到 `nodes[]` 中定位该 `fromId` 对应节点，取其 `number of output rows`；
  - 同一 stage 内：上游多为 Project/Join 等；跨 stage：看 shuffle 的 `shuffle records written`（写端）或 `records read`（读端）。
- **禁止的 shortcuts**：
  - 禁止用**当前节点**的 output 当作 input（聚合节点 input ≠ output）；
  - 禁止用**下游节点**的 input 当作当前节点 input（如 merge 的 input 来自 shuffle，不等于 partial 的 input）；
  - 禁止用同 CTE 中「看起来合理」的数值（如 partial 与 merge 输出相近就混用）。
- **强制校验**：对任意聚合节点，`input ≥ output`；若 `input < output` 或 `input == output` 但上游 output 明显更大，必错。
- **特例**：若当前节点是 shuffle 后的消费者（如最终聚合），metrics 中的输入行数可能是**单任务**读入行数；**全局输入**需看该 stage 的 shuffle 总写入行数（其他节点的 `shuffle records written` 或上游聚合的 `number of output rows` 汇总）。
- **耗时（必提取）**：耗时对分析很重要，**必须**从同一节点的 metrics 中提取。HashAgg 节点取 **`time of aggregation`**，WholeStageCodegen 等取 **`duration`**；值常为 `total (min, med, max (stageId: taskId)) ...` 或单值（如 `5 ms`）。文档表格**须包含**"耗时"列。

## 用边还原管线

- 用 **edges** 还原一条完整管线：例如 `84→83→82→81→79→78→77`，即可确认 83 是 82 的上游、81 的上游是 82 等。
- **partial vs merge**：典型管线 `Project → FlushableHashAgg → Project → Exchange → InputIterator → RegularHashAgg`。FlushableHashAgg 的 input = 上游 Project 的 output；RegularHashAgg 的 input = shuffle 的 records read = FlushableHashAgg 的 output。两者**不可混用**。
- 据此判断某 nodeId 对应 SQL 的哪一段（例如 83 对应 max_store_sales 内层 GROUP BY，而不是 best_ss_customer），避免按"输出行数相同"误归类。

## 嵌套子查询：必须逐层追溯（禁止漏内层）

**典型结构**：`SELECT max(...) FROM (SELECT ... GROUP BY x) sub` —— 内层 GROUP BY 与外层 max 都是 HashAgg，**都要记录**。

**错误做法**：只写外层（如 max 的 81、77），漏掉内层（GROUP BY 的 83）。导致 max_store_sales 表格不完整、执行次数统计失真。

**正确做法（强制）**：
1. 从标量子查询/CTE 的**根节点**（如 Subquery 或最终输出）沿 edges **反推**，直到该子查询的 Scan/Join 边界。
2. 该路径上的**所有 HashAgg**（内层 partial、外层 partial、final）全部纳入该 CTE 的表格。
3. 示例：max_store_sales 管线 `84→83→82→81→79→78→77`，83 是内层 GROUP BY c_customer_sk，81/77 是外层 max；三者都属 max_store_sales。

**原则**：嵌套子查询的 HashAgg 文档必须**完整覆盖**内层与外层，禁止只写"最终输出"那一层。

## 算子→CTE 归属：必须按边追溯（禁止凭相似度猜测）

**错误做法（会导致错归 CTE）：**

- 凭"和某张表相关""在同一管线/stage"就推断属于某个 CTE。同一张表（如 store_sales）会参与多个 CTE，仅凭表名或管线位置会误把 max_store_sales / best_ss_customer 的节点归到 frequent_ss_items。
- **凭算子类型 + 输出行数相似就归到同一 CTE**：例如 58、83、150 都是 RegularHashAggregateExecTransformer、输出 12M，就误判为"best_ss_customer 执行 3 次"。实际 83 的边 `83→82→81` 指向 Subquery（max_store_sales），58→57、150→149 指向 HAVING Filter（best_ss_customer）。**相似 metrics 的节点可能属于不同 CTE，必须用 DAG 区分**。
- 忽略**输出行数**：例如"按 8 键 GROUP BY"的 partial 应产出大量组（如 272M），而"按 c_customer_sk"应产出约 12M；若某节点输出 12M 却归到"按 8 键"的 CTE，即矛盾。

**正确做法（强制）：**

1. **按 edges 双向追溯**：从该 nodeId 沿 edges **反推上游**（输入来源）和**顺推下游**（数据去向）。归属由"下游流向"决定：83→82→81→…→Subquery(73) → max_store_sales；58→57、150→149 → HAVING → best_ss_customer。
2. **按 edges 追溯每个 HashAgg 的输入来源**：从该 nodeId 沿 edges 反推上游，直到 Scan/Join，得到"输入是哪些表的 join"。例如：58←store_sales ⋈ customer → best_ss_customer；83←store_sales ⋈ customer ⋈ date_dim → max_store_sales 内层。
3. **用输入行数区分相似算子**：当多个 HashAgg 输出相同（如 12M）时，输入行数可区分 join 组合。83 输入 2.68B（3 表 join，date_dim 过滤后更少）vs 58/150 输入 2.75B（2 表 join）→ 83 属 max_store_sales，58/150 属 best_ss_customer。
4. **用输出行数做交叉验证**：输出行数须与 GROUP BY 维度一致（如 272M↔8 键，12M↔c_customer_sk）；若不一致，需重新用 edges 核对归属。
5. **归属唯一由"谁供给数据"决定**：同一张表可参与多个 CTE，归属只看**和谁 join**（join 组合 → 对应哪条 SQL/哪个 CTE），不猜、不按"像哪个 CTE"推断。

**原则**：做算子→CTE 归属时，**必须**按计划 DAG（edges）追溯上下游，再用输入/输出行数做 sanity check；**禁止**仅凭算子类型、输出行数相似或表名猜测。

## CTE 执行次数与复用

- **执行次数**：统计物理计划中实现同一逻辑 CTE 的**节点个数**（如 3 个 RegularHashAggregate 对应 frequent_ss_items → 执行 3 次）。
- **前置条件**：统计前**必须先完成归属**。每个 HashAgg 节点必须通过 edges 追溯上下游，确认属于哪个 CTE 后，再按 CTE 分组计数。禁止先按"算子类型 + 输出相似"聚类再计数，否则会误把不同 CTE 的节点算在一起（如 83 误入 best_ss_customer）。
- **是否复用**：
  - 若计划中有 **Subquery** 节点且其输出（edges 的 fromId 为该 Subquery）指向多处（多个 toId），则该子查询**执行 1 次、结果复用**；Subquery 的 metrics 常见 `data size`、`time to collect`。
  - 若无 Subquery 且同一逻辑对应多个节点，则**未复用**，每个节点各执行一次。
- **为何同一 SQL 中两处引用有的是 3 次、有的是 2 次**：由 **stage 划分**决定。看各节点 metrics 里的 `stageId`（如 `stage 15.0`、`stage 37.0`）：若多个节点分属不同 stage，则每个 stage 内各有一份物化；若多个节点在同一 stage 内不同管线，则按管线数执行。与 SQL 中"引用次数"不必一致。

## 文档必须结构（强制）

提取文档**必须**按以下目录结构组织，禁止随意增删或调序章节：

**有 CTE 时（含 WITH 子句）：**
```
1. 数据来源说明
2. 主查询 HashAgg          ← 仅当主查询含 GROUP BY/聚合时保留；若无则写「主查询无 HashAgg」或省略
3. 子查询 HashAgg          ← 仅列出含 HashAgg 的 CTE（3.1、3.2… 按 SQL 中 CTE 顺序）
4. 汇总表（按语义顺序）
5. CTE 执行次数与复用
6. 说明
---
7. 附录：完整 SQL
```

**无 CTE 时（单条 SELECT，无 WITH）：**
```
1. 数据来源说明
2. 主查询 HashAgg
3. 汇总表（按语义顺序）
4. 说明
---
5. 附录：完整 SQL
```

**主查询无 HashAgg、仅 CTE 有 HashAgg 时**：保留「主查询 HashAgg」小节，内容写「主查询无 HashAgg（如 `SELECT * FROM cte` 等）」，或直接省略该小节；汇总表仅含子查询的 HashAgg。

- **文件命名**：与 JSON/SQL 同基名，如 `q23a-zx-metrics.md`、`q23a-zx_测试结果提取.md`；若项目已有约定，沿用约定。
- **存放位置**：与 JSON/SQL 同目录，或项目指定的文档目录（如 `docs/`、`测试结果/`）。
- **参考模板**：`examples/q23a-zx-metrics.md`（相对本 skill 所在目录）。

## 表格格式规范（补充，与「文档必须结构」配合）

除章节目录外，建议将表格写到**可机器/人工核对**的粒度，避免「只有叙述、没有稳定列」的半成品。

### 两类表格

| 类型 | 位置 | 用途 |
|------|------|------|
| **汇总表** | §3 或 §4「汇总表（按语义顺序）」 | 全篇 HashAgg **一张表**收束；便于跨 CTE 对照行数与顺序（见「常见错误 §5」）。 |
| **CTE 内明细表** | §3.x 各子查询小节 | 仅该 CTE 的 HashAgg；列可含 **说明**（join、stage、与 Subquery 关系等），与汇总表分工明确。 |

### 汇总表：固定列与单元格规则

- **列名（固定）**：`序号` | `角色/算子（nodeId）` | `对应 SQL` | `输入行数` | `输出行数` | `耗时`。  
  - 若需额外文字，优先写入 **§6 说明** 或 **§3.x 明细表的「说明」列**，避免把汇总表加成「宽窄不一」的多列表。
- **角色/算子（nodeId）**：
  - 必须带 **`nodeId`**，且与 JSON `nodes[].nodeId` 一致；**禁止**与 `planDescription` 里括号 `(N)` 混用。
  - 算子名可缩写以贴近 UI，例如 `FlushableHashAggregateExecTransformer` → **`FlushableHashAgg (24)`**，`RegularHashAggregateExecTransformer` → **`RegularHashAgg (19)`**；全文缩写规则宜一致。
- **对应 SQL**：
  - 写 **SQL 语义**（CTE 名、主查询/子查询、GROUP BY 角色、UNION 腿、partial/final 等），**不要**用整段 `planDescription` 或 `Arguments:` 长文本代替。
  - CTE 名用反引号：`` `year_total` 门店 2001 partial ``、`` `frequent_ss_items` 内层 GROUP BY（partial）`` 等；与 `examples/q4-metrics.md`、`examples/q23a-zx-metrics.md` 对齐。
- **输入行数 / 输出行数**：
  - **仅整数 + 千分位逗号**（如 `2,750,387,156`）；特例（全局 vs 单任务读入）已在「文档约定」说明，仍避免在数字列写 join 表达式。
- **耗时**：
  - 优先 **摘录 JSON metrics 原文**（如含 `total (min, med, max (stageId: taskId))`）；不要改写为无出处的「约 x s」。
- **行顺序**：
  - **语义顺序**：**按 WITH 中 CTE 书写顺序，最后主查询**；同一 CTE 或主查询段内再按 UNION 腿与 **partial → final**（多腿 UNION 如 q4 见 `examples/q4-metrics.md`）。**禁止**按输出行数从大到小排序。

### CTE 内明细表（§3.x）

- 列建议：`序号` | `角色/算子` | `nodeId` | `对应 SQL 逻辑` | `输入行数` | `输出行数` | `耗时` | **`说明`**（必填用于承接 join、stage、复用、LIMIT 等）。
- **行顺序**：与**本 CTE 内数据流 / 管线**一致（常见为每条腿 **partial → final**，多子查询则**由内到外**或按 edges 叙述顺序）；**避免**无说明地改为纯 `nodeId` 升序（易与语义阅读顺序脱节）。
- 小节内顺序：**先**贴本 CTE 的 SQL 片段（注明源文件路径），**再**表格。

## 文档约定（可选）

- **主查询**：仅指最外层 SELECT（如 `FROM ... GROUP BY ROLLUP(...) LIMIT N`）。
- **子查询**：指 WITH 中的 CTE（如 frequent_ss_items、max_store_sales、best_ss_customer）。
- **汇总表 / 明细表列名与单元格规则**：见上文 **「表格格式规范（补充）」**；子查询明细表另含 **说明** 列时，与「输入/输出仅数字」规则不冲突。
- **汇总表**：按**语义顺序**（**CTE 按 WITH 书写顺序 → 最后主查询**），不按输出行数排序。行数一律写**精确值**（如 2,750,387,156），不用"2.75B 级"。若 final 聚合有"全局输入 + 单任务实际读入"，在输入列同时写出（如 `1,344,953,416（全局）；单任务实际读入 27,447,846`）。
- **LIMIT 无 ORDER BY**：在 final 聚合（如 RegularHashAggregate 最终 merge）的说明中注明：final 阶段可能提前终止，未必对全局行做完整 merge；在数据来源说明中可单独一条简述。
- **子查询章节**：每个 CTE 小节内先贴出**对应 SQL 片段**（注明来源如 `sql/q23a-zx.sql`，仅该 CTE 定义），再放该 CTE 的 HashAgg 表格。
- **文档末尾**：增加**附录：完整 SQL**，贴出 `sql/xxx.sql` 全文（不修改、不加注释）。
- 可单独设一节"CTE 执行次数与复用"，用表格列出执行次数、是否复用，并简述原因（标量子查询 + Subquery → 1 次复用；stage/管线数 → N 次执行）。

## 常见错误与规避（必读）

以下错误曾导致文档需返工，**必须**在提取与校对时规避。

### 1. 列混用：输入行数必须是数字

**错误**：在「输入行数」列写 `store_sales ⋈ date_dim ⋈ item` 等语义描述。**规避**：输入行数、输出行数列**仅数字**；表 join 表达式、stage、分支说明**放在「说明」列**。

### 2. 误把非目标算子纳入表格

**错误**：在「frequent_ss_items 的 HashAgg」表格中纳入 node 95、126，而 95 是 InputIteratorTransformer、126 是 ProjectExecTransformer。**规避**：凡写入某类算子表格，必须确认 `nodeName` 匹配；禁止仅凭 stage 或管线位置纳入；用输出行数交叉验证（272M↔8 键，12M↔c_customer_sk）。

### 3. 混淆 CTE 消费者与 CTE 定义

**错误**：best_ss_customer 的 HashAgg 说明写「catalog_sales 分支」，但该 CTE 定义是 `FROM store_sales, customer`。**规避**：说明列写该节点**实际读取的表/join**（由 edges 追溯），不写「被哪个分支使用」。

### 4. 输入行数取错上游

**错误**：主查询 partial 写输入 `316,109,739`，实际应为 `1,896,658,434`（316M 是 ColumnarUnion，1.9B 是 Expand）。**规避**：输入行数 = edges 中**直接上游**（fromId）的 `number of output rows`；禁止用中间节点代替直接上游。

### 4b. 输入行数误用同管线下游值（partial/merge 混淆）

**错误**：FlushableHashAgg (33) 输入行数写 `286,562,278`，实际应为 `286,562,330`。286,562,278 是 33 的**输出**、也是下游 RegularHashAgg (28) 的**输入**，被误当成 33 的输入。**规避**：
- 每个 HashAgg 的输入**必须**从 edges 中 `toId == 当前 nodeId` 的 `fromId` 对应节点取 `number of output rows`；
- **禁止**用当前节点的 output、下游节点的 input、同 CTE 中 merge 侧的 shuffle 行数来推断 partial 的 input；
- **强制校验**：对任意聚合节点，`input ≥ output`；若出现 `input < output` 或 `input == output` 但上游 output 更大，必错。

### 5. 汇总表格式不符合预期

**错误**：拆成「4.1 主查询」「4.2 子查询」两个表。**规避**：汇总表为**单一表格**，标题 `## 汇总表（按语义顺序）`，列：序号 | 角色/算子 | 对应 SQL | 输入行数 | 输出行数 | 耗时。

### 6. 凭相似 metrics 误把不同 CTE 的节点归到一起

**错误**：58、83、150 都是 RegularHashAggregateExecTransformer、输出 12M，就归到 best_ss_customer 并写"执行 3 次"。实际 83 属于 max_store_sales 内层（边 83→82→81 指向 Subquery），58/150 属于 best_ss_customer（边 58→57、150→149 指向 HAVING）。**规避**：归属**唯一**依据 edges 追溯上下游；输出相同、算子类型相同**不能**作为归属依据。用输入行数交叉验证：83 输入 2.68B（3 表 join）≠ 58/150 输入 2.75B（2 表 join）→ 必属不同 CTE。

### 7. 嵌套子查询漏记内层 HashAgg

**错误**：max_store_sales 只写外层 max（81、77），漏掉内层 GROUP BY c_customer_sk 的 83。**规避**：从子查询根沿 edges 反推，该路径上**所有** HashAgg 都要记录；标量子查询常见"内层 GROUP BY + 外层 aggregate"，两层都要纳入。

## 输入行数提取的强制步骤（每个 HashAgg 必执行）

对**每个** HashAgg 节点，按以下顺序操作，禁止跳过：

1. **查 edges**：`edges[]` 中找 `toId == 当前 nodeId`，得到 `fromId`（直接上游）。
2. **查上游 metrics**：在 `nodes[]` 中找 `nodeId == fromId` 的节点，取其 `number of output rows`。
3. **写入文档**：该值即当前节点的输入行数。
4. **自检**：当前节点 output ≤ 刚取的 input？若否，说明取错或上游找错。

**禁止**：不查 edges/上游，直接写「和下游一样」「和同 CTE 另一个 HashAgg 相近」等。

## 校验要点（提交前必做）

- **列格式**：输入行数、输出行数仅数字；语义描述在说明列。
- **算子类型**：表格中每个 nodeId 的 nodeName 与表格主题一致。
- **输入行数**：等于 edges 中直接上游的 `number of output rows`；**每个** HashAgg 必须按「强制步骤」显式查 edges → 上游 nodeId → 上游 metrics。
- **输出行数**：与 GROUP BY 维度一致。
- **聚合一致性**：对每个 HashAgg，`input ≥ output`；若违反，必错。
- **说明列**：写该节点实际读取的表/join（由 edges 追溯），不写「被某分支使用」。
- **归属验证**：每个 HashAgg 的 CTE 归属必须能用 edges 追溯上下游证明；相似输出/算子类型不能作为归属依据。
- **嵌套子查询**：标量子查询若有内层 GROUP BY + 外层 aggregate，两层 HashAgg 都须在文档中。
- 同一管线内相邻节点：上游的 `number of output rows` = 下游的输入行数。
- 子查询小节内可单独贴 CTE 片段，附录可贴完整 SQL 全文；若用户明确要求不改动文档中已有 SQL 章节，则只改表格与说明文字。
- 行数、nodeId、stage 信息均以 JSON 为准；若与 SQL 逻辑对应，注明 SQL 行号或片段（如 L26–41）。
- 写完一版之后，**逐行**追溯 JSON 中的 edges 与数据流，对每个 HashAgg 的 input 做「edges → 上游 nodeId → 上游 output」复核。

## 根因与反思：为何会误用下游值作为输入

**典型错误**：FlushableHashAgg (33) 输入写 286,562,278，实际应为 286,562,330。286,562,278 是 33 的 output，也是下游 RegularHashAgg (28) 的 input。

**根因**：
1. **认知捷径**：同一 CTE 内 partial 与 merge 紧邻，易把「merge 的 input」误当成「partial 的 input」，而 merge 的 input 来自 shuffle，等于 partial 的 output。
2. **未显式查上游**：未按 edges 找到 34 (Project)，再取 34 的 `number of output rows`，而是凭「和 28 的 input 一样」写数。
3. **缺少强制校验**：未做 `input ≥ output` 检查；33 的 input 若为 286,562,278 则 input == output，与「partial 去重」语义矛盾（应有少量去重）。

**教训**：输入行数**唯一**来源是 edges 指向的**直接上游**的 output；禁止用同管线其他节点的值推断。
