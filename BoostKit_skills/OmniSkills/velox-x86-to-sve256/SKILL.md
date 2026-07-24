---
name: velox-x86-to-sve256
description: Use when modifying velox or gluten-velox C++ files containing x86 SIMD intrinsics (_mm_*, _mm256_*, __m128i, __m256i, immintrin headers) to port them to ARM SVE with fixed 256-bit vector length (AWS Graviton3 or similar). Performs closed-loop verification via remote MCP build + e2e SQL diff against baseline, with up to 5 auto-fix iterations.
---

# velox x86 → SVE256 移植（x86/SVE 双架构共存，带远端 MCP 闭环验证）

## 核心原则

- **双架构共存**：**保留**原有 x86 路径，**额外新增**功能等价的 SVE 路径，用预处理守卫按目标架构分流。**不删 x86、不是原地替换**。
  - 守卫形式：原 `#if XSIMD_WITH_AVX2 ... #endif` 块改成
    ```cpp
    #if XSIMD_WITH_AVX2
      ... 原 AVX2 代码（原样保留）...
    #elif defined(__ARM_FEATURE_SVE)
      ... 新增 SVE 代码 ...
    #else
      ... 原有 scalar 兜底（若有，保留）...
    #endif
    ```
    x86 编译走 `XSIMD_WITH_AVX2`（ARM 上恒 0），ARM 编译走 `__ARM_FEATURE_SVE`。
- **VL 固定 256-bit**：SVE 路径编译开关 `-march=armv8-a+sve -msve-vector-bits=256`，元素数按 256 硬编码。
- 元素数对应关系：
  - `__m256i` = 8×i32 = 4×i64 = 16×i16 = 32×i8
  - `__m128i` = 4×i32 = 2×i64 = 8×i16 = 16×i8
- 头文件：**保留** `<immintrin.h>` 等（x86 块仍需要）；SVE 块新增 `#include <arm_sve.h>`（放文件顶部条件包含或无条件包含均可，arm_sve.h 在 x86 上不会被用到但要确保 ARM 编译能找到）。
- **闭环验证靠 MCP，不靠 grep 自检**。语法过 ≠ 语义对。

## 必须遵守

| 错误想法 | 现实 |
|---|---|
| "build 过了就没事" | build 只验证语法，**必须**跑 baseline vs modified SQL 对比 |
| "shuffle / pack / permute / blend 我会写" | 高风险类必须先 `lookup.py` 查表，不允许凭直觉 |
| "迭代到第 5 次还差一点，再来一次" | 严格停在第 5 次，把所有失败日志交给用户 |
| "删掉 x86 代码、原地换成 SVE" | **违反用户决策**：x86 必须保留，SVE 是 `#elif __ARM_FEATURE_SVE` 新增分支 |
| "VL-agnostic 更通用" | 违反用户决策：硬编码 VL=256 |
| "没基准结果就跳过对比" | 不允许，baseline build 必须先跑 |
| "结果和 native Spark 不一样 = SVE 翻错了" | **错**。判定标准是 `modified == baseline`，不是 `== native Spark`。先比 baseline，相同就是 pre-existing Velox bug，记台账延后，**别去关 SVE 路径"修"它**（见下节铁律） |

## 正确性判定铁律（2026-05-23 血泪教训）

> 上个 agent 把一条 **pre-existing Velox bug（q14a）误判为 SVE 引入**，连续提交多个 commit 关闭 SVE 路径去"修"，结果把本项目要交付的 SVE 工作白白禁用，且根本没修好。

1. **本项目的过线标准是 `modified == baseline`（Velox 对 Velox），不是 `modified == native Spark`。** 某条 query 只要和 **Velox baseline** 字面一致，对这个移植就是绿的——哪怕它和 native Spark 不同。那个不同是 **pre-existing Velox bug**，不是 SIMD 移植造成的，**不在本任务范围**。
2. **任何 query 报 DIFF，第一步永远是 `diff modified baseline`，不是 `diff modified native-oracle`。**
   - `modified == baseline` → **pre-existing**，记录bug**延后**处理，继续移植。**严禁**为它关闭/gating 任何 SVE 路径。
   - `modified != baseline` → 可能是 SVE 引入，才进 [迭代修复](#迭代修复)。
3. **baseline metadata 里的 `fallback=true` 不可信。** 标了 fallback 的 query 结果**仍可能是带 bug 的 Velox 输出**（q14a 实测：fallback=true 却是错的 `1001001 1001001`）。不要拿它当 native oracle，也不要因为"它 fallback 了所以一定对"而下结论。
4. **存疑 baseline 来源时，用 git 提交时间核验。** 把 baseline 结果文件的 mtime 和最早的 SVE commit 时间对比：baseline 早于 SVE 工作 → 它是干净的 pre-SVE 基准，`modified==baseline` 即证明 SVE 没改变行为。
5. **native Spark oracle 的正确用法**（仅用于给"已确认 `modified != baseline` 的差异"定责）：先确认 modified 和 baseline 真的不同，再用 oracle 判断是 baseline 错还是 modified 错。**不要跳过 baseline 直接对 oracle。**

## MCP 工具

| 工具 | 签名 | 用途 |
|---|---|---|
| `mcp__velox_remote__velox_ssh_check` | `()` | 冒烟测 SSH 连通性，stdout 含 `VELOX_MCP_OK` 即通 |
| `mcp__velox_remote__compile_velox` | `(git_repo_url, branch)` | 仅编译 velox。**两个参数必填**，baseline 也要显式传（见下方默认值） |
| `mcp__velox_remote__compile_gluten_velox` | `(git_repo_url, branch)` | 编译 velox + gluten 集成版本，同样两参必填 |
| `mcp__velox_remote__run_e2e_sql_velox` | `(sql, database="", timeout_sec=600)` | 跑**单条/少量** SQL（快速冒烟用），返回查询结果 + App ID + Time taken + Fallback 摘要 |
| `mcp__velox_remote__run_tpcds_99_velox` | `(run_label, database="tpcds_bin_partitioned_decimal_orc_10", sql_dir="", timeout_sec=3600)` | **正确性回归主力**：一次 spark session 跑完 TPC-DS 99 条，按 query 切分结果落盘到 `tpcds_results/<run_label>/` |
| `mcp__velox_remote__diff_tpcds_results` | `(label_a, label_b)` | 字面对比两次 99 条结果，列 `[OK]/[DIFF]/[MISSING]` + unified diff 预览 |
| `mcp__velox_remote__get_compile_log` | `(tail_lines=80)` | 读最新一次编译/e2e 实时日志末尾若干行 |
| `mcp__velox_remote__read_remote_file` | `(remote_path, tail_lines=100)` | 读远端文件末尾若干行，或对目录做 `ls -la` |

### 正确性验证用 99 条全量 TPC-DS

本项目正确性回归的硬要求是 **TPC-DS 全 99 条 query 跑通且结果与 baseline 字面一致**，不再为每个文件单独设计触发 SQL。

- SQL 来源：**远端运行**（103 个 .sql = 99 query + q14a/b、q23a/b、q24a/b、q39a/b）。本机 `tpcds-99/` 是镜像但不再使用——`run_tpcds_99_velox` 直接用远端目录。
- `run_tpcds_99_velox` 内部：在**远端** for 循环遍历 q*.sql 拼成一个文件（每条前后插 `SELECT 'MCP_TPCDS_BANNER_...'` banner，SQL 全程不离开远端 → 天然避开 ARG_MAX），开头注入兼容 SET（见下），同一个 spark-sql session 跑完，输出按 banner 切分（**剔除 Time taken / log / banner 行**，只留数据行）落盘 `tpcds_results/<run_label>/qN.txt` + `metadata.json`
- **兼容 SET（批量开头自动注入）**：`forceShuffledHashJoin=true` + `preferSortMergeJoin=false` 规避 Velox 1.3 MergeJoin `transposeIndices` NOT_IMPLEMENTED（baseline 固有，q1 等会崩）；只换 join 算法不改结果，baseline/modified 同配置 diff 仍有效。还注入 `hive.cli.errors.ignore=true` 尝试让单条失败不中断整批（spark-sql -f 默认遇错 abort）。
- 一轮 99 条约 **15–60 分钟**，所以**单个守卫块改完只 build 验语法，不跑 99 条**；一个文件所有块改完才跑一轮 99 条对比（见 Phase 1 节奏）
- **baseline 跨文件复用**：baseline 99 条结果只在 baseline 代码变化时重跑一次，多个修改文件共用同一份 baseline 结果对比

### baseline 默认参数（必须显式传）

- `git_repo_url` = `默认本地仓库的remote链接`
- `branch` = `与用户确认基线分支`

用任何其他分支跑走非 baseline 路径。

### run_exec_velox.sh / SQL 传递机制（曾踩过两个坑）

`run_exec_velox.sh` 已照 omni 的 `run_e2e_sql.sh` 改成**接受文件参数**：开头 `SQL_FILE=$1` / `DATABASE=$2` / `DB_ARGS`，末尾 `$DB_ARGS -f "$SQL_FILE"`。所以 MCP 直接 `bash run_exec_velox.sh <sqlfile> <database>` 即可，**不再有 wrapper/sed hack**。database 走 `--database $2`，不在 SQL 里加 `USE`。

- `run_e2e_sql_velox`（单条/少量）：`_sftp_put_text` 把 SQL 上传到 `/tmp/mcp_velox_e2e_<uuid>.sql`，再 `_build_run_cmd` 跑。
- `run_tpcds_99_velox`（99 条）：`_build_99_remote_cmd` 在远端拼接，SQL 不离开远端。

## Phase 推进路径（项目层面）

> 本节决定**何时翻什么文件**；下一节「标准闭环工作流」决定**单个文件怎么翻**。两者配合用。

### 颗粒度与节奏

- **颗粒度** = 一个 `#if XSIMD_WITH_AVX2 ... #endif` 守卫块。
- **一次最大 diff** = 3 个块 或 100 行 SIMD 代码，谁先到谁停 → build → SQL → 字面对比 → commit。
- **方向** = 自底向上（L1 → L2 → L3 工具/算子），热路径优先。
- **高风险类**（scan_file.py 标 `[HIGH-RISK]` 的 shuffle / pack / permute / blend / movemask / gather / scatter）必须**每块单独**走完整 build + SQL，不允许批量。

### Phase 0 — 工具链冒烟（0 行代码改动）

| 步 | 调用 | 通过判据 |
|---|---|---|
| 0.1 | `velox_ssh_check()` | stdout 含 `VELOX_MCP_OK` |
| 0.2 | `compile_velox("仓库链接", "分支名")` | 退出码 0 + 末尾日志含 `Successfully built Velox from Source.` |
| 0.3 | `compile_gluten_velox(同 URL, 同分支)` | 退出码 0 |
| 0.4 | `run_e2e_sql_velox("SELECT 1 AS a, 2 AS b;")` | 查询结果含 `1\t2` 行 + `Time taken: X seconds, Fetched 1 row(s)` |

四步全绿才进入 Phase 1。任一步红 → 先解决工具/环境，**不开始翻译**。

### Phase 1 — 首发模块：BitPackDecoder.{h,cpp}（6 个守卫块）

选它做首发的理由（不要换）：
- 模块隔离清晰（bit-pack 列解码），跨块耦合弱
- SQL 触发简单：任何 ORC/Parquet INT 列读取都进
- 块少且独立（.h 4 块 + .cpp 2 块）
- 不依赖 `SimdUtil-inl.h` 内部细节（直接调 intrinsic），主干没改完也能验

正确性基准：**TPC-DS 99 条**（不是单条 SQL）。BitPackDecoder 是 ORC/Parquet 整数列解码，TPC-DS 任何整数列扫描都触发，99 条足以覆盖回归。

节奏（**单块只 build，文件级才跑 99 条**）：
1. `scan_file.py BitPackDecoder.h` → 看每块的 intrinsic
2. 跑一次 baseline（若本会话还没有）：
   `run_tpcds_99_velox(run_label="baseline_<base_sha>")` —— 结果跨文件复用
3. 改第 1 块 → `compile_velox(repo, sve256-port)` 验语法绿 → 进第 2 块（**这一步不跑 SQL**）
4. .h 所有块改完 → push `sve256-port` → `compile_velox` + `compile_gluten_velox` → `run_tpcds_99_velox(run_label="sve256_BitPackDecoder_h_<sha>")`
5. `diff_tpcds_results("baseline_<base_sha>", "sve256_BitPackDecoder_h_<sha>")` → 0 DIFF 才 commit
6. 同样节奏处理 .cpp（.h + .cpp 也可合并成一个文件批次一起跑 99 条，省一轮）

> 有 DIFF：看是哪条 qN 差异 → 该 query 涉及的列类型反推哪个守卫块的 intrinsic 翻错 → 回 [迭代修复](#迭代修复)。

Phase 1 结束后：把翻译过程中**速查表外**、`lookup.py` 也较冷门的 intrinsic 追加到 SKILL.md 的速查表（这一步**等用户确认**后再做）。

### Phase 2 — 主干：SimdUtil-inl.h（约 38 个守卫块）

按**类别**批次推进（不按行号顺序）：

| 批次 | 类别 | 估算块数 | 验证 SQL 思路 |
|---|---|---|---|
| 2.1 | load/store + broadcast | 6~8 | 任何列读取 |
| 2.2 | arithmetic + logical + shift | 6~8 | `SELECT a+b, a&b, a<<2 FROM t` |
| 2.3 | compare + select | 4~6 | `SELECT * FROM t WHERE a=1 AND b<3` |
| 2.4 | gather / scatter ⚠️高风险 | 4~6 | hash join 探测 / 索引列读取 |
| 2.5 | movemask / 谓词归约 ⚠️高风险 | 4~6 | `SELECT COUNT(*) WHERE …` |
| 2.6 | shuffle / pack / permute ⚠️高风险 | 余下 | 字符串列、字典编码列 |

约束：
- 2.1 – 2.3 每批结束后 build + 该类别 SQL，绿才进下一批
- 2.4 / 2.5 / 2.6 **每个块都单独** build + SQL（高风险类不准批量）

### Phase 3 — L2 / L3 剩余（~8 文件，~15 块）

按依赖序：`IntDecoder` → `ColumnVisitors` → `SelectiveStructColumnReader.{h,cpp}` → `SelectiveStringDirectColumnReader.cpp` → `HashTable.h` → `FlatVector-inl.h` / `BaseVector.cpp` → `StringCore.h` / `StringView.cpp`。

### Phase 4 — 测试代码 + ByteStreamSplitInternal.h（待用户确认特殊处理）

- `tests/Lemire/bmipacking32.h`、`experimental/wave/tests/CpuTable.h`：只在跑 velox UT 时编。先用 `read_remote_file` 看 baseline 脚本带不带 UT；带就翻，不带就跳过并报告给用户。
- `ByteStreamSplitInternal.h`（98 个裸 intrinsic，**无 `#if XSIMD_WITH_AVX2` 守卫**）是特例：先 grep 该文件在 ARM 上的实际编译条件。如果 ARM codepath 走不到 → **唯一允许整文件加 `#ifdef __x86_64__` 包起来**（上游 Arrow 代码例外）；走得到才真翻 SVE。这一处**必须停下来问用户**，不允许自行决策。

---

## 标准闭环工作流

每个待改文件，按顺序执行。任一步失败 → 跳到 [迭代修复](#迭代修复)。

### 0. 扫描

```bash
python ./.claude/skills/velox-x86-to-sve256/scripts/scan_file.py <abs_file_path>
```

- 输出 unique intrinsic 列表、行号、**高风险标注**（shuffle/pack/permute/blend/movemask）。
- 用 `TaskCreate` 建一条 todo per unique intrinsic。

### 1. 确认正确性基准（不用每文件写 SQL）

正确性基准固定为 **TPC-DS 99 条**（本机 `tpcds-99/`）。不再为每个文件设计针对性 SQL。
只需确认 baseline 99 条结果是否已存在于 `tpcds_results/baseline_<sha>/`：有 → 复用；无 → 第 2 步生成。

### 2. 跑 baseline 拿基线结果（跨文件复用）

baseline 仓库与分支两个参数都**必填**（见上方「baseline 默认参数」一节）：

```
mcp__velox_remote__compile_velox(
    git_repo_url="代码仓链接",
    branch="代码仓分支",
)
mcp__velox_remote__compile_gluten_velox(
    git_repo_url="代码仓链接",
    branch="代码仓分支",
)
mcp__velox_remote__run_tpcds_99_velox(run_label="baseline_<base_sha>")
```

baseline 99 条结果落盘 `tpcds_results/baseline_<base_sha>/`。**只要 baseline 代码没变、远端产物未被修改分支覆盖，就跨多个修改文件复用这份结果，不重跑。** 一旦远端编译被覆盖（你 build 了修改分支），下次要回 baseline 必须重新 compile baseline 分支再跑 99 条。

### 3. 翻译

每条 intrinsic 按以下三级查找：

1. 先查本文件 [高频速查表](#高频速查表-30-条) → 命中即用
2. 未命中 → `python ./.claude/skills/velox-x86-to-sve256/scripts/lookup.py <intrinsic_name>` → 读输出
3. 仍不确定 → Read `templates/conversion_patterns.md` 对应类别段（不要全文 Read）
4. 高风险类（scan_file.py 标 `[HIGH-RISK]`）必须执行第 2 步，不允许跳到模板

写 SVE 分支时（**新增 `#elif defined(__ARM_FEATURE_SVE)` 块，不动原 AVX2 块**）：
- 把原 AVX2 块的逻辑用 SVE 等价重写在 `#elif` 分支里；原 `#if XSIMD_WITH_AVX2` 块**原样保留**
- `__m256i` / `__m128i` 在 SVE 块里用 `svint32_t`/`svint64_t`/...（按上下文判断元素类型）
- 在循环外定义一次谓词：`svbool_t pg = svptrue_b32();`（按元素宽度选 `_b8`/`_b16`/`_b32`/`_b64`）
- 头文件：保留 `#include <immintrin.h>` 等；确保 `#include <arm_sve.h>` 对 ARM 编译可见（条件包含或顶部无条件包含）
- 守卫结构见[核心原则](#核心原则)的 `#if XSIMD_WITH_AVX2 / #elif __ARM_FEATURE_SVE / #else` 模板

### 4. 编译 velox（用修改分支）

```
mcp__velox_remote__compile_velox(git_repo_url=<repo>, branch=<modified_branch>)
```

非 ok → 迭代修复。

### 5. 集成编译

```
mcp__velox_remote__compile_gluten_velox(git_repo_url=<repo>, branch=<modified_branch>)
```

> `compile_gluten_velox` 内部脚本会用同一个 `<repo>` / `<modified_branch>` 同时处理 velox 子模块和 gluten 集成层（脚本调 `buildbundle-veloxbe.sh --velox_repo=$1 --velox_branch=$2 --run_setup_script=OFF`）。它**不接受单独的 gluten repo/branch 参数** —— gluten 代码用远端已 clone 的版本，velox 才是 $1/$2 控制的部分。

非 ok → 迭代修复。

### 6. 跑修改版 99 条

```
mcp__velox_remote__run_tpcds_99_velox(run_label="sve256_<file>_<sha>")
```

结果落盘 `tpcds_results/sve256_<file>_<sha>/`。

### 7. 对比

```
mcp__velox_remote__diff_tpcds_results("baseline_<base_sha>", "sve256_<file>_<sha>")
```

`✅ 一致 = 99 且 ❌ 差异 = 0` 才算过。任一 `[DIFF]` → 迭代修复（看差异 qN 反推哪个守卫块翻错）。
注意 `[MISSING]` 也要查：若 baseline 某 qN 本就失败而 modified 也失败，两边都没结果行属正常；但若 modified 新增失败（baseline 有结果 modified 没有）即回归。

### 8. 交付

报告给用户：
- 替换文件 / 替换条数 / unique intrinsic 数
- 用于验证的 baseline run_label 与 modified run_label
- `diff_tpcds_results` 结论：一致 99 / 差异 0 / 缺失情况

## 迭代修复

发生 build 失败、SQL 跑错、结果不对时：

1. **计数器 +1**（全局一个计数，初始 0）
2. **如果计数 ≥ 5**：立即停止。把所有失败日志和当前修改清单交给用户，**不再尝试**。
3. 否则：
   - build 失败 → 调 `get_compile_log(tail_lines=200)` 拉日志
   - 结果不对 → 把 baseline vs modified 的 diff 列出
   - 定位出错的源文件行 → 反查是哪条 intrinsic 翻译错了
   - 重新走 [翻译](#3-翻译) 的三级查找（这次直接到第 2 步 lookup.py，不再用速查表）
   - 修改后回到 [4. 编译 velox](#4-编译-velox)

## 高频速查表-30-条

> 速查表只覆盖常见模式。任何带 `[查表]` 后缀或在表外的 intrinsic 必须走 `lookup.py`。

### Load / Store（8）

| AVX2 / SSE | SVE (VL=256) |
|---|---|
| `_mm256_loadu_si256((__m256i*)p)` | `svld1_s32(pg, (int32_t*)p)`（按元素类型换 `_s8/_s16/_s64/_u*`） |
| `_mm256_load_si256((__m256i*)p)`  | `svld1_s32(pg, (int32_t*)p)` |
| `_mm256_storeu_si256((__m256i*)p, v)` | `svst1_s32(pg, (int32_t*)p, v)` |
| `_mm256_store_si256((__m256i*)p, v)`  | `svst1_s32(pg, (int32_t*)p, v)` |
| `_mm_loadu_si128((__m128i*)p)` | `svld1_s32(svptrue_pat_b32(SV_VL4), (int32_t*)p)` — 半向量 |
| `_mm_storeu_si128((__m128i*)p, v)` | `svst1_s32(svptrue_pat_b32(SV_VL4), (int32_t*)p, v)` |
| `_mm256_maskload_epi32(p, mask)` | `svld1_s32(<mask_to_svbool>, (int32_t*)p)` `[查表]` mask 转换 |
| `_mm256_maskstore_epi32(p, mask, v)` | `svst1_s32(<mask_to_svbool>, (int32_t*)p, v)` `[查表]` |

### Arithmetic（8）

| AVX2 | SVE (VL=256) |
|---|---|
| `_mm256_add_epi32(a, b)` | `svadd_s32_x(pg, a, b)` |
| `_mm256_sub_epi32(a, b)` | `svsub_s32_x(pg, a, b)` |
| `_mm256_mullo_epi32(a, b)` | `svmul_s32_x(pg, a, b)` |
| `_mm256_add_epi64(a, b)` | `svadd_s64_x(pg64, a, b)` |
| `_mm256_add_epi16(a, b)` | `svadd_s16_x(pg16, a, b)` |
| `_mm256_add_epi8(a, b)`  | `svadd_s8_x(pg8, a, b)` |
| `_mm256_min_epi32(a, b)` | `svmin_s32_x(pg, a, b)` |
| `_mm256_max_epi32(a, b)` | `svmax_s32_x(pg, a, b)` |

### Compare（4）

| AVX2 | SVE (返回 svbool_t，不是向量！) |
|---|---|
| `_mm256_cmpeq_epi32(a, b)` | `svcmpeq_s32(pg, a, b)` → `svbool_t` |
| `_mm256_cmpgt_epi32(a, b)` | `svcmpgt_s32(pg, a, b)` → `svbool_t` |
| `_mm256_cmpeq_epi8(a, b)`  | `svcmpeq_s8(pg8, a, b)`  → `svbool_t` |
| `_mm256_cmpeq_epi64(a, b)` | `svcmpeq_s64(pg64, a, b)` → `svbool_t` |

> ⚠️ x86 cmp 返回向量（-1/0），SVE cmp 返回 `svbool_t` 谓词。下游若把比较结果当向量用（如 `_mm256_and_si256(cmp, other)`），必须改成 `svsel_*(cmp_pg, other, svdup_*(0))`。`[查表必查]`

### Logical（4）

| AVX2 | SVE (VL=256) |
|---|---|
| `_mm256_and_si256(a, b)`    | `svand_s32_x(pg, a, b)` |
| `_mm256_or_si256(a, b)`     | `svorr_s32_x(pg, a, b)` |
| `_mm256_xor_si256(a, b)`    | `sveor_s32_x(pg, a, b)` |
| `_mm256_andnot_si256(a, b)` | `svbic_s32_x(pg, b, a)` — **注意操作数顺序反了**：AVX2 是 `~a & b`，SVE bic 是 `b & ~a` |

### Broadcast / Set（3）

| AVX2 | SVE (VL=256) |
|---|---|
| `_mm256_set1_epi32(x)`   | `svdup_s32(x)` |
| `_mm256_setzero_si256()` | `svdup_s32(0)` |
| `_mm256_set_epi32(...)`  | 写入栈数组再 `svld1_s32(pg, arr)`，无单指令对应 |

### Shift（2）

| AVX2 | SVE (VL=256) |
|---|---|
| `_mm256_slli_epi32(a, n)` | `svlsl_n_s32_x(pg, a, n)` |
| `_mm256_srli_epi32(a, n)` | `svlsr_n_u32_x(pg, svreinterpret_u32_s32(a), n)` — 注意 logical shift 要先转 unsigned |

### Mask / Movemask（1，高风险）

| AVX2 | SVE — `[查表必查]` |
|---|---|
| `_mm256_movemask_epi8(v)` | 无直接对应。常用模式：`svbool_t b = svcmpne_s8(pg8, v, svdup_s8(0));` 然后用 `svaddv` 类归约或 `svcntp_b8(pg8, b)` 取计数。具体翻译看上下文用途，必须 lookup.py 并改造控制流。 |

## 何时停下来问用户

- 找不到 baseline 分支默认值（脚本提示需要参数）→ 问
- 5 次迭代仍失败 → 停，列日志
- 高风险类需要重构控制流（如 movemask 在 `if` 条件里）→ 先把当前理解给用户确认再改

## 不要做的事

- 不要 Read 整个 `references/avx2_to_sve.md`（170KB，token 浪费）
- 不要 Read 整个 `references/sve_intrinsics.md`（3MB，必爆上下文）
- 不要 Read `references/intel_intrinsics.xml` 或 `arm_intrinsics.json`（仅供 `regen_mapping.py` 用）
- 不要本地用 cmake/gcc 试编译——本机是 x86，只有远端 ARM 才能验证
- 不要跳过 baseline 跑 SQL 这一步
<!--
TPC-DS 99 validation cadence override

Use this cadence for the migration work unless the user explicitly changes it.
The goal is to keep correctness coverage useful without spending a full TPC-DS
99 run after every single guard block.

- Run the baseline TPC-DS 99 only once per unchanged baseline commit and reuse
  that result across files.
- For every translated guard block, run lightweight validation: Velox compile
  plus the most relevant UT or focused SQL probe.
- Run full TPC-DS 99 at file or category boundaries, not at every guard block.
- For BitPackDecoder.{h,cpp}, one full TPC-DS 99 after the file pair is enough
  unless focused validation exposes a risk.
- For SimdUtil-inl.h, batch by semantic category and run full TPC-DS 99 after
  each completed category batch: load/store+broadcast, arithmetic+logical+shift,
  compare+select, gather/scatter, movemask/predicate reduction, and
  shuffle/pack/permute.
- For the remaining Phase 3 files, batch one file at a time by default. Small
  adjacent low-risk files may share one full TPC-DS 99 batch if each guard block
  already passed compile and focused validation.
- High-risk guard blocks still get isolated focused validation. Add a full
  TPC-DS 99 immediately only when focused validation cannot cover the changed
  behavior or when the block changes movemask, shuffle, gather/scatter, null
  bitmap, dictionary index, or row selection semantics.
- Always run one final full TPC-DS 99 after the whole migration batch.
- If a full TPC-DS 99 diff appears, investigate only the files/categories in
  the most recent full-validation batch before changing unrelated code.

Expected total full TPC-DS 99 runs for the whole migration is roughly 11-15:
one reusable baseline, about one for BitPackDecoder, about 4-6 for
SimdUtil-inl.h, about 4-6 for remaining Phase 3 files, and one final run.

TPC-DS run artifact retention

For every full TPC-DS run and every failed-query retry, preserve intermediate
artifacts in a timestamped run directory. Do not rely only on terminal output.
Each run directory must contain:

- `query.list`: exact SQL files that were attempted, in execution order.
- `meta.txt`: branch/commit, database, SQL source, Spark/Gluten runtime paths,
  and relevant shared-library timestamps.
- `status.txt`: current state while the run is active and final totals when it
  ends.
- `summary.tsv`: one row per query with query name, status, duration, start
  time, and end time.
- `log/<query>.log`: stderr/Spark log for each query.
- `result/<query>.result`: stdout/query result for each query, even when empty.

Do not extract result files with broad `grep` or by dropping only `Time taken`
lines. spark-sql logs and query rows are mixed in this environment. Use
`scripts/tpcds_extract_result.py` from the Velox checkout to create each
`result/<query>.result` from `log/<query>.log`; it reads the final
`Time taken: ..., Fetched N row(s)` trailer and keeps only the preceding N
non-empty rows. If the trailer is missing, mark the query failed and keep the
raw log.

When retrying failed queries after changing runtime parameters, create a new
timestamped retry directory instead of overwriting the full-run directory. The
retry summary must be comparable to the full-run summary.

TPC-DS result comparison

After every full TPC-DS validation run, compare the preserved result files
against the reusable baseline before continuing migration work.

- Use `scripts/tpcds_compare_results.py` from the Velox checkout.
- Before comparing, ensure every result file was created by
  `scripts/tpcds_extract_result.py`; compare output must not contain Spark,
  Hive, YARN, or Gluten warning lines.
- Supply the full run result directory first, then any retry result directories
  in chronological order as repeated `--current` arguments. Later directories
  override earlier results for the same query.
- Supply the baseline result directory as `--baseline`. If the baseline is
  incomplete, keep the comparison output and report `MISSING_BASELINE`
  separately; do not call the whole run fully validated until a complete
  baseline exists.
- Always pass the full run `query.list` with `--query-list` so missing current
  query results are detected.
- Write comparison artifacts into a timestamped directory under
  `<远端结果目录>/tpcds99_runs/compare-*`.
- Preserve `summary.tsv` and every file under `diffs/`. A non-empty `diffs/`
  directory means correctness must be investigated before translating the next
  batch.
- Treat `ORDER_ONLY` as a separate classification from `DIFF`. It means the
  result rows are identical as a multiset but the output order differs. Keep
  the diff artifact, but prioritize numeric/key `DIFF` entries first.
- If a query differs from an old Velox baseline, run a focused native Spark
  oracle for that query before changing SVE code. Historical partial baselines
  may contain stale, incomplete, or parameter-specific results.

Example:

`python3 scripts/tpcds_extract_result.py --log <run>/log/q16.sql.log --out <run>/result/q16.sql.result`

`python3 scripts/tpcds_compare_results.py --query-list <run>/query.list --baseline <baseline-result-dir> --current <run>/result --current <retry>/result --out <compare-dir>`
-->
