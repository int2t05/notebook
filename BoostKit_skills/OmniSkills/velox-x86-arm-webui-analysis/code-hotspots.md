# Gluten+Velox x86 vs ARM WebUI 对比分析工作流（4-Phase）

## 概述

输入两个不同架构（x86 / ARM）的 Spark Application ID 或 WebUI 地址，按以下 4 个阶段自动执行分析：

| Phase | 目标 | 输出 |
|-------|------|------|
| **Phase 1** | 整体性能对比总览 | 全 Stage 耗时对比表，标记差异 > 20% 的 Stage |
| **Phase 2** | 慢 Stage 算子级精细分析 | 每个慢 Stage 的算子指标对比 + 瓶颈排序 |
| **Phase 3**（可选）| 代码热点分析 | 结合仓库代码定位 NEON/SVE 缺失点和优化建议 |
| **Phase 4** | 生成可视化 HTML 报告 | 可直接在浏览器打开的完整报告 |

---

## 前置：输入格式与架构识别

### 输入格式

用户提供两个 Application ID 或 WebUI 地址：
- x86 应用：`http://spark35-his.data.sankuai.com/history/<x86_appId>/1/`
- ARM 应用：`http://spark35-his.data.sankuai.com/history/<arm_appId>/1/`

也可只提供 Application ID，History Server 地址固定为：`http://spark35-his.data.sankuai.com`

### 架构识别

用 `web_fetch` 获取 Environment 页面，查找 "Gluten Build Information"：
- `Component Velox Branch` 含 `huawei_kunpeng` → **ARM (鲲鹏)**
- `Component Velox Branch` 含 `mt-1.` 或 `develop/mt-` → **x86**
- `Gluten Repo URL` 含 `kunpeng` → **ARM**

---

## Phase 1：整体性能对比总览

### 1.1 并行获取数据

用 `web_fetch` **同时**获取以下 4 个页面：

```
http://spark35-his.data.sankuai.com/history/<x86_appId>/1/stages/
http://spark35-his.data.sankuai.com/history/<arm_appId>/1/stages/
http://spark35-his.data.sankuai.com/history/<x86_appId>/1/environment/
http://spark35-his.data.sankuai.com/history/<arm_appId>/1/environment/
```

从 Stages 页面提取每个 Stage 的：Stage ID、Description、Status、Duration、Input/Output Size、GC Time、Tasks Succeeded/Total

### 1.2 Stage 对齐策略

- **首选**：按 Description 文字匹配（如 `WholeStageCodegen (3)`、`Exchange hashing`）
- **次选**：按 Stage 序号对齐（x86 Stage N ↔ ARM Stage N）
- **注意**：两个 Application 的 Stage 总数可能不同，未匹配的 Stage 标注 `—`

### 1.3 Phase 1 标准输出

```
=== Phase 1: 📊 整体性能对比总览 ===

■ 应用基本信息
| 指标              | x86 (Baseline)        | ARM 鲲鹏 (New)        |
|-----------------|----------------------|----------------------|
| Application ID  | {x86_appId}          | {arm_appId}          |
| 总查询时间        | {x86_total}          | {arm_total}          |
| Stages 总数      | {x86_stages}         | {arm_stages}         |
| ARM/x86 总耗时比 | —                    | {ratio}x {badge}     |
| Velox Branch    | {x86_branch}         | {arm_branch}         |

■ Stage 逐一对比
| Stage | 描述（简）           | x86 耗时 | ARM 耗时 | ARM/x86 | 差异 | 精细分析? |
|-------|---------------------|---------|---------|---------|------|----------|
|   0   | Exchange hashing    |  1.2min |  2.3min |  1.92x  |  🔴  |    ✅     |
|   1   | WholeStageCodegen 3 |  0.8min |  0.9min |  1.12x  |  🟢  |    ❌     |

差异标记: 🔴 > 1.5x | 🟡 1.2~1.5x | 🟢 < 1.2x | ⚡ ARM更快(< 0.8x)

■ 需精细分析的 Stage: {slow_stage_ids}（共 {slow_count} 个）
```

---

## Phase 2：慢 Stage 算子级精细分析

对 Phase 1 中标记 🔴 或 🟡 的每个 Stage 执行以下流程。

### 2.1 获取 Stage 详情

```
http://spark35-his.data.sankuai.com/history/<appId>/1/stages/stage/?id=<stageId>&attempt=0
```

提取：Total Time Across All Tasks、Median/Max Task Duration、GC Time、Input/Output Size、Shuffle Read/Write Size、KILLED tasks 数量（推测执行）

### 2.2 定位对应 SQL Query

Stage 详情页 DAG 会显示 `WholeStageCodegenTransformer (N)`，据此找对应 Query ID：

```
http://spark35-his.data.sankuai.com/history/<appId>/1/SQL/
http://spark35-his.data.sankuai.com/history/<appId>/1/SQL/execution/?id=<queryId>
http://spark35-his.data.sankuai.com/history/<appId>/1/gluten/
```

优先提取以下算子的细粒度指标：

| 算子类型 | 关键指标 |
|---------|---------|
| `WholeStageCodegenTransformer` | `duration` |
| `ColumnarExchange` | `time to split`、`shuffle write time`、`fetch wait time`、`time to deserialize` |
| `BroadcastHashJoin` / `ShuffleHashJoin` | `time of hash build`、`time of hash probe`、`time of postProjection` |
| `VeloxColumnarToRow` | `time to convert` |
| `ProjectExecTransformer` | `time of project` |
| `ScanTransformer` | `time of scan and filter` |
| `ColumnarBroadcastExchange` | `time to collect`、`time to broadcast` |
| `SortExecTransformer` | `time to sort` |
| `WindowExecTransformer` | `time to compute window` |
| `VeloxResizeBatches` | `time to resize` |
| `FilterExecTransformer` | `time of filter` |

### 2.3 Phase 2 标准输出（每个慢 Stage 一份）

```
=== Phase 2: 🔍 Stage {stageId} 精细分析 ===

📌 Stage 背景
| 字段        | x86            | ARM            |
|------------|----------------|----------------|
| Stage ID   | {stageId}      | {stageId}      |
| Query ID   | {queryId}      | {queryId}      |
| Stage 描述 | {description}  | {description}  |
| 主要算子   | {op_list}      | {op_list}      |

🕐 Stage 级总耗时
| 指标                        | x86          | ARM          | ARM/x86 | 差异  |
|----------------------------|--------------|--------------|---------|-------|
| Total Time Across All Tasks | {x86}       | {arm}        | {ratio} | {🔴}  |
| GC Time                     | {x86}       | {arm}        | {ratio} | {🟡}  |
| Median Task Duration        | {x86}       | {arm}        | {ratio} | {🔴}  |
| KILLED Tasks (speculation)  | {x86}       | {arm}        | —       | {⚠️?} |
| Input Size                  | {x86}       | {arm}        | —       | —     |
| Shuffle Write Size          | {x86}       | {arm}        | —       | —     |

🔬 算子级别逐一对比
| 算子 / 指标                                | x86 耗时 | ARM 耗时 | ARM/x86 | 差异 |
|------------------------------------------|---------|---------|---------|------|
| BroadcastHashJoin - time of hash probe   | {x86}   | {arm}   | {ratio} | {🔴} |
| BroadcastHashJoin - time of hash build   | {x86}   | {arm}   | {ratio} | {🟢} |
| VeloxColumnarToRow - time to convert     | {x86}   | {arm}   | {ratio} | {🔴} |
| ProjectExecTransformer - time of project | {x86}   | {arm}   | {ratio} | {🟡} |
| ColumnarExchange - time to split         | {x86}   | {arm}   | {ratio} | {🔴} |
| ScanTransformer - scan and filter        | {x86}   | {arm}   | {ratio} | {🟢} |

📊 性能瓶颈排序（按绝对耗时差降序）
| 排名 | 算子 / 阶段                    | x86 耗时 | ARM 耗时 | 差值   | ARM/x86 | 根因推断                     |
|-----|------------------------------|---------|---------|--------|---------|------------------------------|
| #1  | BroadcastHashJoin hash probe  | 10.3s  | 42.8s   | +32.5s | 4.2x    | 散射访问缺 AVX2 gather 等效  |
| #2  | VeloxColumnarToRow convert    | 24.9s  | 51.4s   | +26.5s | 2.1x    | 列序列化路径 NEON 未充分优化  |

🎯 一句话总结
> Stage {stageId} ARM 比 x86 慢 {Nx}，核心瓶颈是 {算子1}（{ratio1}x）和 {算子2}（{ratio2}x），
> 根本原因是 {架构差异描述}。
```

---

## Phase 3：（可选）代码实现分析

**触发条件**：当前工作区存在 Gluten/Velox 代码仓库（`huawei_kunpeng_gluten/` 或 `huawei_kunpeng_velox/`）时自动执行。

根据 Phase 2 慢算子，对照以下代码路径分析：

### 3.1 各慢算子对应代码热点

#### `time to split` 慢 → Shuffle 分片路径

| 文件 | 函数 | 差异描述 |
|------|------|---------|
| `cpp/velox/shuffle/VeloxHashShuffleWriter.h` | `splitFixedType<T>` | scatter-gather 循环：x86 自动 `VPGATHERDD`，ARM 无等价 NEON gather |
| `cpp/velox/shuffle/VeloxHashShuffleWriter.cc` | `splitBoolType` | x86 `__rolb` 硬件字节旋转，ARM 软件 `rotateLeft` |
| `cpp/velox/shuffle/VeloxHashShuffleWriter.cc` | `PREFETCHT0` 宏 | x86 `_mm_prefetch` 直接 L1 预取，ARM `__builtin_prefetch` |
| `cpp/core/shuffle/HashPartitioner.cc` | `computePid` | x86 内联 `CMOVS`（无分支），ARM 依赖 `if` 分支编译器优化 |

#### `time to convert` / `time of project` 慢 → 列式转换路径

| 文件 | 函数 | 差异描述 |
|------|------|---------|
| `cpp/velox/utils/Common.h` | `fastCopy` | 调用 `simd::memcpy`，SIMD 宽度差异直接影响吞吐 |
| `velox/common/base/SimdUtil-inl.h` | `simd::memcpy` | x86 AVX2 256-bit 每次32字节；ARM NEON 128-bit 每次16字节，理论2x差距 |
| `cpp/velox/operators/serializer/VeloxColumnarToRowConverter.cc` | `UnsafeRowFast::serialize` | 大量 memcpy，底层调 fastCopy |

#### `time of hash probe` 慢 → HashJoin 路径

| 文件 | 函数 | 差异描述 |
|------|------|---------|
| `velox/common/base/SimdUtil-inl.h` | `Gather` 结构体 | x86 `_mm256_i32gather_epi32` 单指令 gather 8个值；ARM `xsimd::generic` 逐元素 load |
| `velox/exec/HashTable.cpp` | `arrayGroupProbe`、`listJoinResultsFastPath` | 哈希表探测大量随机访存，依赖 gather 加速 |
| `velox/exec/HashProbe.cpp` | `joinProbe`、`arrayJoinProbe` | probe 循环依赖 SIMD gather 和比较 |

#### `time to deserialize` 慢 → Shuffle 读取路径

文件 `cpp/velox/shuffle/VeloxShuffleReader.cc`，函数 `readFlatVectorStringView`：
串行前缀和累加（`offset += rawLength[i]`），x86 编译器可向量化，ARM 需手动 NEON `vaddq_s32`。

#### `WindowExecTransformer` / `VeloxResizeBatches` 慢

| 文件 | 函数 | 差异描述 |
|------|------|---------|
| `velox/exec/SortWindowBuild.cpp` | `addInput` | 行数据存储，底层 `simd::memcpy` |
| `velox/exec/PrefixSort.cpp` | `compareAllNormalizedKeys`、`bitsSwapByWord` | x86 字节旋转优化，ARM 无等价指令 |
| `velox/vector/FlatVector-inl.h` | `FlatVector::resizeValues` | `AlignedBuffer::reallocate + memcpy`，ARM 内存分配效率较低 |
| `cpp/velox/utils/VeloxBatchResizer.cc` | `VeloxBatchResizer::next` | 调用 `buffer->append`，频繁触发 resize + copy |

### 3.2 架构差异速查表

| 代码路径 | 对应算子指标 | ARM 预计劣势 | 优先级 |
|---------|------------|------------|--------|
| `splitFixedType<T>` — scatter-gather | `time to split` | 1.5~3x | 🔴 高 |
| `simd::memcpy` — 256-bit vs 128-bit | `time to convert`、`time of project` | 1.2~2x | 🔴 高 |
| `simd::gather` — AVX2 vs 逐元素 | `time of hash probe` | 1.5~4x（大表 join）| 🔴 高 |
| `computePid` — CMOVS vs if 分支 | `time to split` | 1.1~1.3x | 🟡 中 |
| `splitBoolType` — `__rolb` vs 软件旋转 | `time to split`（Bool 列多时）| 1.1~1.5x | 🟡 中 |
| `readFlatVectorStringView` — 前缀和 | `time to deserialize` | 1.2~1.8x | 🟡 中 |
| `CopyBitmap` — AVX2 256-bit vs NEON 128-bit | `time to split` | 1.1~1.5x | 🟡 中 |
| `FlatVector::resizeValues` — AlignedBuffer realloc | Window/VeloxResizeBatches | 1.2~2x | 🟡 中 |
| `PREFETCHT0` — `_mm_prefetch` vs `__builtin_prefetch` | 整体 cache miss | 难量化 | 🟢 低 |

### 3.3 Phase 3 标准输出

```
=== Phase 3: 🔧 代码级热点分析 ===

🔴 热点 #1：{算子名}（ARM 慢 {ratio}x）
   📁 文件：{文件路径}  |  函数：{函数名}
   ⚡ x86 优势：{x86 使用的指令/实现}
   🦾 ARM 现状：{缺失的 NEON/SVE 实现}
   💡 优化建议：{具体优化方向，1-2句}
   预计劣势：{ratio}x  |  优先级：{🔴高 / 🟡中 / 🟢低}

🔴 热点 #2：...
```

---

## Phase 4：生成可视化 HTML 报告

分析完成后生成 HTML 文件：`analysis/<日期>_perf_report.html`

生成后执行：`open analysis/<日期>_perf_report.html`

### 4.1 HTML 报告结构

| 区块 | 内容描述 |
|------|---------|
| ① 页面头部 | 标题、生成时间、x86/ARM AppID |
| ② 总览卡片 | x86（蓝色）/ARM（橙色）双栏对比 + 总耗时比值徽章 |
| ③ Stage 总览表 | 全部 Stage 带颜色差异标记，点击 Stage ID 跳转详细分析 |
| ④ 慢 Stage 分析卡片 | 每个慢 Stage 独立卡片：总耗时表 + 算子柱状图（CSS 实现）+ 瓶颈排序表 + 一句话总结 |
| ⑤ 代码热点分析 | 折叠展示代码差异和优化建议（`<details>/<summary>`） |
| ⑥ WebUI 快捷链接 | x86/ARM 各5类链接，全部 `target="_blank"` |

### 4.2 HTML 生成规则

1. **柱状图宽度**：以同 Stage 内最大算子耗时为 100%，等比例计算各算子宽度
   - `x86_pct = (x86_val / max_val) * 100`
   - `arm_pct = (arm_val / max_val) * 100`
2. **比值徽章颜色类**：
   - `ratio >= 3.0` → `ratio-severe`（深红）
   - `1.5 <= ratio < 3.0` → `ratio-critical`（红）
   - `1.2 <= ratio < 1.5` → `ratio-warn`（橙）
   - `ratio < 1.2` → `ratio-ok`（绿）
3. **Stage 表格行背景**：差异 > 1.5x 的行加 `class="slow-row"`
4. **WebUI 链接格式**：`http://spark35-his.data.sankuai.com/history/{appId}/1/{page}/`
5. 所有链接加 `target="_blank"`

### 4.3 HTML 骨架（填充数据后输出完整文件）

完整的 HTML 模板文件：见同目录 `webui-template.html`（可直接复制并替换 `{占位符}`）。

以下为 HTML 骨架结构说明（含关键 CSS 类名）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Gluten+Velox 性能对比报告</title>
<style>/* 见 4.4 节 */</style>
</head>
<body>
<div class="container">

  <!-- 区块1: 页面头部 -->
  <div class="page-header">
    <h1>⚡ Gluten+Velox x86 vs ARM 性能对比报告</h1>
    <div class="meta">生成时间: {时间} | x86: {x86_appId} | ARM: {arm_appId}</div>
  </div>

  <!-- 区块2: 应用总览（双栏卡片）-->
  <div class="card">
    <h2>📊 应用总览</h2>
    <div class="arch-row">
      <div class="arch-block x86">  <!-- 蓝色区块 -->
        <div class="arch-label">x86 Baseline</div>
        <div class="arch-appid">{x86_appId}</div>
        <div class="arch-time">⏱ {x86_total} | Velox: {x86_branch}</div>
      </div>
      <div class="arch-block arm">  <!-- 橙色区块 -->
        <div class="arch-label">ARM 鲲鹏 (New)</div>
        <div class="arch-appid">{arm_appId}</div>
        <div class="arch-time">⏱ {arm_total} | Velox: {arm_branch}</div>
      </div>
    </div>
    <div style="text-align:center;padding:10px 0">
      ARM/x86 = <span class="ratio-badge {ratio_class}">{total_ratio}x {emoji}</span>
    </div>
  </div>

  <!-- 导航栏（慢 Stage 快速跳转）-->
  <div class="nav-bar">
    <span>🔗 快速跳转:</span>
    <a class="nav-link slow" href="#stage-{S}">Stage {S} ({R}x 🔴)</a>
    <a class="nav-link" href="#code-hotspots">🔧 代码热点</a>
    <a class="nav-link" href="#webui-links">🔗 WebUI 链接</a>
  </div>

  <!-- 区块3: Stage 总览表 -->
  <div class="card">
    <h2>📋 Stage 总览 ({total_stages} 个, {slow_count} 个需精细分析)</h2>
    <table>
      <thead>
        <tr><th>Stage</th><th>描述</th><th>x86 耗时</th><th>ARM 耗时</th>
            <th>ARM/x86</th><th>差异</th><th>精细分析</th></tr>
      </thead>
      <tbody>
        <tr class="slow-row">  <!-- 差异 > 1.5x: class="slow-row" -->
          <td><a href="#stage-{S}" class="needs-detail">Stage {S}</a></td>
          <td>{desc}</td><td>{x86}</td><td><strong>{arm}</strong></td>
          <td><strong>{ratio}x</strong></td>
          <td><span class="badge badge-red">🔴 显著慢</span></td><td>✅</td>
        </tr>
        <tr>  <!-- 差异 1.2~1.5x -->
          <td>Stage {S}</td><td>{desc}</td><td>{x86}</td><td>{arm}</td>
          <td>{ratio}x</td>
          <td><span class="badge badge-orange">🟡 轻微慢</span></td><td>⚠️</td>
        </tr>
        <tr>  <!-- 正常 < 1.2x -->
          <td>Stage {S}</td><td>{desc}</td><td>{x86}</td><td>{arm}</td>
          <td>{ratio}x</td>
          <td><span class="badge badge-green">🟢 正常</span></td><td>—</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- 区块4: 慢 Stage 详细分析卡片（每个慢 Stage 一份）-->
  <div class="stage-detail" id="stage-{S}">
    <div class="stage-header">
      <span class="stage-id-badge">Stage {S}</span>
      <span class="stage-title">{desc}</span>
      <span class="ratio-badge ratio-critical">{ratio}x 🔴</span>
    </div>

    <!-- Stage 总耗时表 -->
    <h3>🕐 Stage 总耗时</h3>
    <table style="margin-bottom:16px">
      <thead><tr><th>指标</th><th>x86</th><th>ARM</th><th>ARM/x86</th></tr></thead>
      <tbody>
        <tr><td>Total Time Across All Tasks</td>
            <td>{x86}</td><td>{arm}</td>
            <td><span class="badge badge-red">{ratio}x</span></td></tr>
        <tr><td>GC Time</td><td>{x86}</td><td>{arm}</td>
            <td><span class="badge badge-orange">{ratio}x</span></td></tr>
        <tr><td>Median Task Duration</td><td>{x86}</td><td>{arm}</td>
            <td><span class="badge badge-red">{ratio}x</span></td></tr>
        <tr><td>KILLED Tasks</td><td>{x86}</td><td>{arm}</td><td>—</td></tr>
        <tr><td>Input Size</td><td>{x86}</td><td>{arm}</td><td>—</td></tr>
      </tbody>
    </table>

    <!-- 算子柱状图（CSS 实现）-->
    <h3>🔬 算子级耗时对比</h3>
    <div class="bar-legend">
      <span><span class="legend-dot" style="background:#1976d2"></span>x86</span>
      <span><span class="legend-dot" style="background:#e65100"></span>ARM</span>
    </div>
    <!-- 每个算子一行，x86 bar（蓝）和 ARM bar（橙）上下排列 -->
    <!-- bar-wrap 内 bar-track 高度 18px，宽度按比例（以最大耗时为100%）-->
    <div class="bar-row">
      <div class="bar-label">{算子名缩写}</div>
      <div class="bar-wrap">
        <div class="bar-track"><div class="bar-x86" style="width:{x86_pct}%"></div></div>
        <div class="bar-track"><div class="bar-arm" style="width:{arm_pct}%"></div></div>
      </div>
      <div class="bar-values">x86:{x86_val} ARM:{arm_val} <strong>({ratio}x)</strong></div>
    </div>
    <!-- 更多算子行 ... -->

    <!-- 瓶颈排序表 -->
    <h3 style="margin-top:18px">📊 瓶颈排序</h3>
    <table>
      <thead>
        <tr><th>#</th><th>算子/阶段</th><th>x86</th><th>ARM</th>
            <th>差值</th><th>倍差</th><th>根因</th></tr>
      </thead>
      <tbody>
        <tr><td><strong style="color:#f44336">#1 🥇</strong></td>
            <td>{算子}</td><td>{x86}</td><td>{arm}</td>
            <td>{+diff}</td><td><strong>{ratio}x</strong></td><td>{根因}</td></tr>
      </tbody>
    </table>

    <!-- 一句话总结 -->
    <div class="summary-box">
      🎯 <strong>总结</strong>: Stage {S} ARM 比 x86 慢 <strong>{ratio}x</strong>，
      核心瓶颈是 <strong>{算子1} ({r1}x)</strong> 和 <strong>{算子2} ({r2}x)</strong>，
      根本原因是 {根因描述}。
    </div>
  </div>
  <!-- 更多慢 Stage 卡片依此类推... -->

  <!-- 区块5: 代码热点分析（可选）-->
  <div class="code-section" id="code-hotspots">
    <h2>🔧 代码级热点分析</h2>
    <details>
      <summary>
        <span>🔴 高优 | {算子} — {差异描述}</span>
        <span style="font-size:12px;color:#888">预计劣势: {ratio}x</span>
      </summary>
      <div class="detail-content">
        <p><strong>文件</strong>: <code>{文件路径}</code>（函数: <code>{函数名}</code>）</p>
        <p style="color:#555;margin:8px 0">⚡ x86 实现:</p>
        <div class="code-block x86">{x86代码片段}</div>
        <p style="color:#555;margin:8px 0">🦾 ARM 现状:</p>
        <div class="code-block arm">{arm代码片段}</div>
        <div class="hotspot-tags">
          <span class="tag tag-high">🔴 高优先级</span>
          <span class="tag tag-file">{文件名}</span>
          <span class="tag">预计劣势: {ratio}x</span>
        </div>
        <p style="color:#2e7d32;margin-top:10px">💡 优化建议: {建议}</p>
      </div>
    </details>
    <!-- 更多热点... -->
  </div>

  <!-- 区块6: WebUI 快捷链接 -->
  <div class="card" id="webui-links">
    <h2>🔗 WebUI 快捷链接</h2>
    <div class="links-grid">
      <div class="link-item"><span class="link-arch x86">x86</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{x86_appId}/1/SQL/" target="_blank">🗂 SQL 列表</a></div>
      <div class="link-item"><span class="link-arch arm">ARM</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{arm_appId}/1/SQL/" target="_blank">🗂 SQL 列表</a></div>
      <div class="link-item"><span class="link-arch x86">x86</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{x86_appId}/1/gluten/" target="_blank">⚡ Gluten 指标</a></div>
      <div class="link-item"><span class="link-arch arm">ARM</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{arm_appId}/1/gluten/" target="_blank">⚡ Gluten 指标</a></div>
      <div class="link-item"><span class="link-arch x86">x86</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{x86_appId}/1/stages/" target="_blank">📊 Stages</a></div>
      <div class="link-item"><span class="link-arch arm">ARM</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{arm_appId}/1/stages/" target="_blank">📊 Stages</a></div>
      <div class="link-item"><span class="link-arch x86">x86</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{x86_appId}/1/jobs/" target="_blank">🔧 Jobs</a></div>
      <div class="link-item"><span class="link-arch arm">ARM</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{arm_appId}/1/jobs/" target="_blank">🔧 Jobs</a></div>
      <div class="link-item"><span class="link-arch x86">x86</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{x86_appId}/1/environment/" target="_blank">🔍 Environment</a></div>
      <div class="link-item"><span class="link-arch arm">ARM</span>
        <a class="link-btn" href="http://spark35-his.data.sankuai.com/history/{arm_appId}/1/environment/" target="_blank">🔍 Environment</a></div>
    </div>
  </div>

</div>
</body>
</html>
```

### 4.4 关键 CSS 类速查

| CSS 类 | 用途 |
|--------|------|
| `.page-header` | 深色渐变页眉 |
| `.card` | 白色圆角卡片 + 阴影 |
| `.arch-block.x86` | 蓝色双栏（x86 区块）|
| `.arch-block.arm` | 橙色双栏（ARM 区块）|
| `.ratio-ok/.warn/.critical/.severe` | 绿/橙/红/深红比值徽章 |
| `.nav-bar` | 顶部导航栏 |
| `.slow-row` | 慢 Stage 行背景浅红 |
| `.stage-detail` | 左侧红色竖线分析卡片 |
| `.bar-row/.bar-wrap/.bar-track/.bar-x86/.bar-arm` | CSS 纯实现柱状图 |
| `.summary-box` | 黄色总结框 |
| `.code-block.x86/.arm` | 深色代码块，左侧蓝/橙竖线 |
| `details` / `summary` | 折叠展开的代码热点 |

完整 CSS 参见同目录 `webui-template.html`，直接复制修改即可。

---

## 实测性能数据参考（2026-06-09）

数据来自 `dpapp_technician_hairdresser_skill_tag_score_d`，Stage 14（SQL Query 127）：

| 算子 | x86 耗时 | ARM 耗时 | 倍差 |
|------|---------|---------|------|
| BroadcastHashJoin hash probe | 10.3s | 42.8s | **4.2x** 🔴 |
| VeloxColumnarToRow convert | 24.9s | 51.4s | **2.1x** 🔴 |
| ColumnarBroadcastExchange collect | 205ms | 2.1s | **10.2x** 🔴 |
| ProjectExecTransformer project | 334ms | 1.5s | **4.5x** 🟡 |
| GC Time | 4s | 17s | **4.3x** 🟡 |

**一句话总结**：Stage 14 ARM 比 x86 慢 2.5×，核心瓶颈是 BroadcastHashJoin hash probe（4.2×）和 VeloxColumnarToRow 列转行（2.1×），根本原因是大规模 LeftOuter Join 的散射访问和列序列化路径缺乏 NEON/SVE 向量化优化。

---

## 附录：URL 模板速查

- 架构识别：`http://spark35-his.data.sankuai.com/history/<appId>/1/environment/`
- Stages 列表：`http://spark35-his.data.sankuai.com/history/<appId>/1/stages/`
- Stage 详情：`http://spark35-his.data.sankuai.com/history/<appId>/1/stages/stage/?id=<stageId>&attempt=0`
- SQL 执行：`http://spark35-his.data.sankuai.com/history/<appId>/1/SQL/execution/?id=<queryId>`
- Gluten 指标：`http://spark35-his.data.sankuai.com/history/<appId>/1/gluten/`
- Executor 列表：`http://spark35-his.data.sankuai.com/history/<appId>/1/executors/`
- YARN syslog：`http://rz-data-hdp-hisha01.sankuai.com:19888/jobhistory/logs/<node>:<port>/<cid>/<cid>/<user>/syslog/?start=0`
- YARN stderr：`http://rz-data-hdp-hisha01.sankuai.com:19888/jobhistory/logs/<node>:<port>/<cid>/<cid>/<user>/stderr/?start=0`
