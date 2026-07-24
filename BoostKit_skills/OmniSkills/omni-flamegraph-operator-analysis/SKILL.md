---
name: omni-flamegraph-operator-analysis
description: >
  Two-level async-profiler flame graph analysis for OmniOperator: first discovers
  the hottest operators (op::*Operator / *Writer / *Reader naming), then drills
  into each operator's hottest functions. Outputs structured CSVs to a
  per-run artifact directory.
---

# OmniOperator 火焰图两级热点分析

## 何时使用

- 拿到 async-profiler 导出的 `.html` 火焰图后需要确定优化目标

---

## 脚本位置

| 步骤 | 脚本 | 说明 |
|------|------|------|
| 1 | `scripts/flame_top_operators.py` | 自动发现 Top-N 算子，输出 `result-operators.csv` |
| 2 | `scripts/flame_top_functions.py` | 对每个 Top 算子提取 Top-N 函数，输出 `result-functions.csv` |

---

## 输出目录约定（与 omni-sql-perf-improvement 共同遵守）

```
<workspace-root>/artifacts/<sql-id>/flame-derived-<run>/
    result-operators.csv    ← 步骤 1 输出
    result-functions.csv    ← 步骤 2 输出
```

- `<sql-id>` 示例：`q23a`、`q7`
- `<run>` 格式：`YYYY-MM-DDTHH:mm:ss`（如 `2026-05-30T15:33:36`），由 `date +%Y-%m-%dT%H:%M:%S` 生成
- **禁止**覆盖已有 run 目录（每次分析自动使用新时间戳）

---

## 步骤 1 — 算子层热点提取

```bash
RUN=$(date +%Y-%m-%dT%H:%M:%S)
python "<SKILL_DIR>/scripts/flame_top_operators.py" \
  --dir "LOCAL_FLAME_HTML_DIR" \
  --out "<WORKSPACE_ROOT>/artifacts/<sql-id>/flame-derived-${RUN}/result-operators.csv" \
  --top 5 \
  --min-pct 0.5
```

> **路径约定**：
> - `<SKILL_DIR>` = 本 skill 所在目录（即 `.agents/skills/omni-flamegraph-operator-analysis`）
> - `<WORKSPACE_ROOT>` = 当前工作区根目录（即 `git rev-parse --show-toplevel` 或当前目录）

**算子识别规则**（内置于脚本，无需手动指定 pattern）：
- 匹配帧名包含 `op::*Operator`、`*Writer`、`*Reader`、`*Splitter`、`*Deserializer` 的帧
- 自动合并同名算子的所有帧宽度，计算占比（与浏览器 Search 一致）
- 输出列：`file, query, rank, operator, matched_pct`

**解读算子结果**（以下为示例，实际以火焰图中发现的算子为准）：

| 算子 | 对应代码路径 |
|------|------------|
| `ColumnarShuffleWriter` | `splitter.cpp` — 序列化 + 压缩写入 |
| `ShuffleReaderDeserializer` | `Decompression.cc` — 解压 + 反序列化 |
| `HashAggOperator` | 聚合核心路径 |
| `SortOperator` | 排序路径 |
| `FilterOperator` / `ProjectOperator` | 过滤与列计算 |
| `TableScanOperator` / `SplitReader` | ORC 读取路径 |

拿到 Top-5 算子后，在 Velox 和 ClickHouse 中搜索等价实现，对比：
- 核心数据结构与算法
- 序列化格式（Protobuf vs flat binary vs arrow）
- SIMD / 向量化路径（OmniOperator 必须用 SVE，禁止 NEON）
- null 处理策略

---

## 步骤 2 — 函数层热点提取

```bash
python "<SKILL_DIR>/scripts/flame_top_functions.py" \
  --dir "LOCAL_FLAME_HTML_DIR" \
  --operators-csv "<WORKSPACE_ROOT>/artifacts/<sql-id>/flame-derived-${RUN}/result-operators.csv" \
  --out "<WORKSPACE_ROOT>/artifacts/<sql-id>/flame-derived-${RUN}/result-functions.csv" \
  --top 5 \
  --min-pct 0.1
```

输出列：`file, query, operator, operator_pct, rank, function, function_pct`

**解读函数结果**：

对每个 Top-5 函数：
1. 在 OmniOperator 代码中定位该函数的实现，理解当前算法
2. 在 Velox / ClickHouse 中搜索等价函数（或同名函数）
3. 在线搜索是否有已知优化方案（论文、PR、博客）
4. 判断是否满足 SIMD 前置条件（见 `omni-sql-perf-improvement` Phase 4 检查表）

**典型热点函数举例**（Q23a 经验）：

| 函数 | 来源算子 | 优化方向 |
|------|---------|---------|
| `SerializeToZeroCopyStream` | `ColumnarShuffleWriter` | 序列化格式替换（flat binary） |
| `snappy_compress` / `lz4_compress` | `ColumnarShuffleWriter` | 压缩算法选择 |
| `ParseFromArray` | `ShuffleReaderDeserializer` | 反序列化路径 |
| `memcpy` / `memmove` | 多个算子 | 零拷贝 / 内存对齐 |

---

## 步骤 3 — 优化点汇总与优先级排序

整合步骤 1（算子层）和步骤 2（函数层）的分析结果，按以下维度打分：

| 维度 | 说明 |
|------|------|
| **火焰图占比** | 函数 `matched_pct` 越高，优化收益上限越大 |
| **实现可行性** | 是否有 Velox/CK 可借鉴方案，改动复杂度 |
| **正确性风险** | 改动是否涉及序列化协议（高风险）、纯算法（低风险） |
| **测量噪声门槛** | 单点预期收益需 > 3%（约 0.3s on Q23a 62s 基线）才能单独验证 |

输出格式（提交到迭代追踪文档）：

```markdown
### 优化优先级列表（基于火焰图 ${RUN}）

| 优先级 | 算子 | 函数 | 火焰图占比 | 可借鉴方案 | 预期收益 | 风险 |
|--------|------|------|-----------|-----------|---------|------|
| P0 | ColumnarShuffleWriter | SerializeToZeroCopyStream | 9.4% | flat binary | ~5-10% | 高（协议改动） |
| P1 | ShuffleReaderDeserializer | ParseFromArray | 3.2% | flat binary deserialize | ~3-5% | 高（与 P0 联动） |
| P2 | HashAggOperator | buildHashTable | 2.1% | Velox SIMD hash | ~2-3% | 中 |
```

---

## 方法论说明

1. **算子发现是自动的**：脚本内置正则，不依赖用户指定 pattern，避免分析偏差
2. **函数占比是近似的**：`flame_top_functions.py` 使用全文件帧宽度比（非精确子树统计），适合发现热点方向，不适合精确计时
3. **OmniOperator 特有约束**：
   - SIMD 优化必须用 SVE（ARM64 Kunpeng 920，256-bit）；严禁 NEON
   - ShuffleReaderDeserializer 改动必须同步修改 splitter.cpp 的写端（读写格式必须一致）
4. **与 Velox/CK 对比是手动的**：脚本只产出 CSV，对比分析由 Agent 根据步骤 3 指引完成

---

## 交付物检查清单

- [ ] `result-operators.csv` — Top-5 算子，含 `matched_pct`
- [ ] `result-functions.csv` — 每个 Top 算子的 Top-5 函数，含 `function_pct`
- [ ] 三方实现对比表（每个优化点一张，填入迭代追踪文档）
- [ ] 优化优先级列表（P0/P1/P2，含预期收益与风险评估）
