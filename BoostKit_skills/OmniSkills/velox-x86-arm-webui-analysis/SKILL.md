---
name: velox-x86-arm-webui-analysis
description: 对比分析 Gluten+Velox 在 x86 和 ARM(鲲鹏) 上的 Spark WebUI 性能差异，识别 ARM 落后的算子和计算过程,定位可能缺失 NEON/SVE 向量化的代码路径,并生成可视化 HTML 对比报告。使用场景:用户提供 x86 和 ARM 的 Spark Application ID 或 WebUI URL,要求对比性能、找出 ARM 慢的原因、分析 Gluten 代码中架构特定优化缺失点,并生成可视化 HTML 报告.
---

# Velox x86 vs ARM WebUI 性能对比分析技能

本技能对比 Velox 在 x86 和 ARM（鲲鹏）平台上的 Spark WebUI 性能指标，识别 ARM 落后的算子和计算瓶颈,定位 Gluten/Velox 代码中缺失的 NEON/SVE 向量化实现,并生成带 WebUI 快捷链接的可交互 HTML 对比报告。

## 何时使用

- 用户提供 x86 和 ARM 的 Spark Application ID 或 WebUI URL,要求跨架构性能对比
- 用户问为什么 ARM(鲲鹏)比 x86 慢 — Gluten+Velox Spark 查询
- 用户想识别 Gluten/Velox 中缺失的 NEON/SVE 向量化代码路径
- 用户要求生成可视化性能对比 HTML 报告
- 用户指定任务名 + Stage ID 做精细粒度的单 Stage 对比

## 4-Phase 分析工作流

用户提供两个 Application ID(x86 + ARM)时,使用 **4-Phase 完整分析工作流**(详见 [code-hotspots.md](code-hotspots.md)):

| Phase | 目标 | 输出 |
|-------|------|------|
| **Phase 1** | 整体性能对比总览 | 全 Stage 耗时对比表,标记差异 > 20% 的 Stage |
| **Phase 2** | 慢 Stage 算子级精细分析 | 每个慢 Stage 的算子指标对比 + 瓶颈排序 |
| **Phase 3**(可选)| 代码热点分析 | 结合仓库代码定位 NEON/SVE 缺失点和优化建议 |
| **Phase 4** | 生成可视化 HTML 报告 | 基于 webui-template.html 填充数据,`open` 在浏览器打开 |

> 如果用户指定了任务名 + 具体 Stage ID,直接跳到 **Step 13**(单 Stage 精细对比流程),无需从 Step 1 逐步走完。

## 逐步分析详细步骤

### Step 1: 准确识别架构(关键)

**不要**依赖 Application ID 前缀来判断架构,必须通过 WebUI Environment 页面确认。

访问 Environment 页面:
```
http://spark35-his.data.sankuai.com/history/<appId>/1/environment/
```

在 "Spark Properties" 或 "Gluten Build Information" 中查找:
- `Component Velox Branch` 含 `huawei_kunpeng` → **ARM (鲲鹏)**
- `Component Velox Branch` 含 `mt-1.` / `develop/mt-` → **x86**
- `Gluten Repo URL` 含 `kunpeng` → **ARM**

History Server 地址: `http://spark35-his.data.sankuai.com`

### Step 2: 获取关键 WebUI 页面

对每个 Application,**并行**获取以下页面(用 `web_fetch` 工具):

| 页面 | URL 模板 | 核心信息 |
|------|----------|--------|
| SQL Execution | `/history/<appId>/1/SQL/execution/?id=<queryId>` | 总耗时、算子树 |
| Stages | `/history/<appId>/1/stages/` | 各 Stage 耗时 |
| Gluten 指标 | `/history/<appId>/1/gluten/` | 算子级细粒度指标 |
| Environment | `/history/<appId>/1/environment/` | 架构识别、编译信息 |

默认 queryId=119,如无则从 SQL 列表页获取实际 ID。

### Step 3: 提取对比指标

**总体指标**: Query Duration、Job 数量、Stage 数量

**WholeStageCodegenTransformer (WSCT) 指标**: `duration`、`time to split`、`time to deserialize`、`time to shuffle sort`

**ColumnarExchange 指标**: `shuffle write time`、`shuffle wall time`、`fetch wait time`

**HashJoin 指标**: `time of hash build`、`time of hash probe`

**Project/Convert 指标**: `time of project`、`time to convert`

### Step 4: 定位落后最多的 Executor(通过 WebUI 日志)

使用 YARN History Server(`http://rz-data-hdp-hisha01.sankuai.com:19888`)获取容器日志。
从 Spark WebUI Executors 页面提取 `container_` ID。
从 Stage 详情页识别耗时最长的前 3 个 Task 及其 Executor ID。

### Step 5: 获取 Executor 日志(syslog + stderr)

创建提取脚本:
- `/tmp/extract_log.py` — 提取 `<pre>` 标签内容
- `/tmp/extract_html.py` — 全文提取去除标签

下载并提取:
```bash
curl -s "<URL>" -o /tmp/exec_raw.html
python3 /tmp/extract_log.py /tmp/exec_raw.html > /tmp/exec.log
```

对 syslog 用 `extract_html.py`,对 stderr 用 `extract_log.py`。

### Step 6: 分析 syslog(Java 层)

提取关键时间节点: 进程启动、task 分配、task 完成、关闭。
分析 Shuffle Fetch: remote blocks 数量、建连耗时。
分析 Broadcast 读取和 GC 模式。
检查 Executor 被 Kill 事件(`Driver commanded a shutdown` = 正常的 Dynamic Allocation 回收,**不是**异常)。

### Step 7: 分析 stderr(Native C++ 层)

提取 native 初始化时间线(MimallocAllocator → VeloxBackend → UdfLoader → DumpStatsThread)。
提取 Task 级别执行时间(`Terminating task ... running for N.NNs`)。
提取算子级统计(WholeStageResultIterator 输出)。

**关键诊断指标**: ValueStream `Wall time / CPU time` 比率:
- ≈ 1.0 → 数据本地/内存缓存,无 IO 等待
- >> 1.0 → 大量网络/磁盘 IO 等待(shuffle fetch 延迟,ARM 冷 executor 常见)

### Step 8: 对比分析模板

生成结构化对比表:
- Executor 生命周期对比
- Native 初始化对比
- 算子执行对比(同 Stage 同 Task 类型)
- JVM GC 对比

**根因诊断决策树**:
```
ValueStream Wall >> CPU (比率 > 3x)?
├── Yes → 主要瓶颈是 Shuffle Fetch IO 等待
│          ├── 冷 executor(首个 task) → 建连开销,连接复用率低
│          └── 跨机架 shuffle → 网络延迟,检查 remote blocks 比例
└── No  → 主要瓶颈是 CPU 计算
            ├── ValueStream CPU 差距大 → shuffle 解压/反序列化慢
            │    └── 对应代码: VeloxShuffleReader.cc(readFlatVectorStringView)
            ├── HashProbe CPU 差距大 → hash 计算或内存访问慢
            │    └── 对应代码: 哈希函数(xxHash),缺少 AES-NI 加速
            └── Project CPU 差距大 → 列计算/类型转换慢
                 └── 对应代码: VeloxColumnarToRowConverter.cc(fastCopy/memcpy)
```

### Step 9: 结构化对比输出(WebUI 指标层)

每对 Application 输出对比表,带 ARM/x86 比值和显著度标记:
- 🔴 ARM/x86 > 1.5(ARM 显著慢)
- 🟡 1.2 ~ 1.5(ARM 轻微慢)
- 🟢 < 1.2(无显著差异或 ARM 更快)

### Step 10: 结合代码定位热点

根据慢的指标,对照以下代码热点(详见 code-hotspots.md):

**`time to split` 慢 → Shuffle 分片路径**:
- `cpp/velox/shuffle/VeloxHashShuffleWriter.h` — `splitFixedType<T>`: scatter-gather 循环,x86 自动 `VPGATHERDD`,ARM 缺乏等价 NEON gather
- `cpp/velox/shuffle/VeloxHashShuffleWriter.cc` — `splitBoolType`: x86 `__rolb` 硬件字节旋转,ARM 软件 `rotateLeft`
- `cpp/core/shuffle/HashPartitioner.cc` — `computePid`: x86 内联 `CMOVS`(无分支),ARM `if` 分支

**`time to convert` / `time of project` 慢 → 列式转换路径**:
- `cpp/velox/utils/Common.h` — `fastCopy` → `simd::memcpy`: x86 AVX2 256-bit,ARM NEON 128-bit
- `cpp/velox/operators/serializer/VeloxColumnarToRowConverter.cc` — `UnsafeRowFast::serialize`

**`time of hash probe` 慢 → HashJoin 路径**:
- `velox/common/base/SimdUtil-inl.h` — `Gather` 结构体: x86 `_mm256_i32gather_epi32` 单指令 gather,ARM `xsimd::generic` 逐元素 load

**`time to deserialize` 慢 → Shuffle 读取路径**:
- `cpp/velox/shuffle/VeloxShuffleReader.cc` — `readFlatVectorStringView`: 前缀和累加循环

### Step 11: 输出最终汇总

多对 Application 时,输出汇总表:
```
| 配对 | 任务名 | x86 AppId | ARM AppId | ARM总耗时/x86 | 主要慢点 | 可能原因 |
```

一句话总结格式:
> **[算子名]** 慢 [N]x,主要在 **[计算过程]**,推测原因:[架构差异]

### Step 12: 生成可视化 HTML 报告

使用本技能目录下的 `webui-template.html` 模板文件。
填入每对任务的数据:
- AppIDs、耗时、Velox branch 名称
- ARM/x86 比值(保留2位小数)
- 主要慢算子和根因

保存为 `analysis/<日期>_perf_report.html`,然后用 `open` 在默认浏览器打开。

比值徽章样式:
- ratio >= 3.0 → `ratio-severe`(深红)
- 1.5 <= ratio < 3.0 → `ratio-critical`(红)
- 1.2 <= ratio < 1.5 → `ratio-warn`(橙)
- ratio < 1.2 → `ratio-ok`(绿)

### Step 13: 指定任务 + 指定 Stage 的精细对比分析

当用户提供任务名 + 目标 Stage ID:
1. 确定 AppID 对(匹配已知数据或 Environment 页面验证)
2. 并行获取两个 AppID 的 Stage 详情页
3. 提取 Stage 级指标(Total Time、GC Time、Task 数量、Input/Output、KILLED tasks)
4. 定位对应 SQL Query 并提取算子级耗时
5. 瓶颈排序:按绝对耗时差值(ARM - x86)降序,同等差值时倍差更大排前
6. 参照 Step 8 的根因诊断决策树给出推测原因
7. 标准输出格式:

---
**📌 任务背景表**(任务名、AppID、Stage ID、Query ID、逻辑语义、DAG 结构)

**🕐 Stage 级别总耗时对比表**(总耗时、GC Time、Task 数、输入/输出)

**🔍 算子级别逐一对比**(按算子逐项展开,每算子小表格 + 结论一句话)

**📊 性能瓶颈排序表**(排名 | 算子/阶段 | x86耗时 | ARM耗时 | 倍差 | 根因推断)

**🎯 一句话总结**(格式:`Stage <N> ARM 比 x86 慢 Nx,核心瓶颈是 <算子>(慢 Nx,占 Stage X%)...`)

---

## 抴资源文件

- **code-hotspots.md**: 完整的 4-Phase 工作流规范,含详细逐步指令、代码热点映射表、架构差异速查表、实测性能数据参考
- **webui-template.html**: 完整的 HTML 模板(含 CSS 样式和卡片结构),用于生成可视化性能对比报告。内含预构建的 ratio badge、柱状图、stage detail card、code hotspot section、WebUI link grid 等 CSS 组件

## 分析完成后

- 告知用户 HTML 报告文件路径
- 用纯文本总结 3-5 个关键发现
- 突出最关键的 ARM 特定瓶颈
- 为每个慢 Stage 提供一句话总结
- 提醒报告中 WebUI 链接可点击,直接打开原始 Spark History Server 页面