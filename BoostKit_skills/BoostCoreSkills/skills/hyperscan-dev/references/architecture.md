# Hyperscan 架构详解

## Hyperscan 简介

Hyperscan 是一个高性能正则表达式匹配库，专为网络数据包深度检测（DPI）场景设计。核心理念是 **编译一次，扫描多次** — 将正则规则集预编译为不可变的数据块（database），运行时用 SIMD 指令对输入数据做高速并行匹配。

### 输入 vs 输出

```
                          ┌─────────────┐
    正则规则集 (.literals)  │             │  匹配结果 (MatchResult)
    ──────────────────────►│  Hyperscan  │──────────────────────►
    待扫描数据 (corpus)     │             │  callback(id, from, to, ctx)
    ──────────────────────►│             │
                          └─────────────┘
```

**输入（两样东西）**：

| 输入 | 何时提供 | 说明 |
|------|---------|------|
| **规则集** (expressions) | 编译期 `hs_compile()` | 一组正则表达式或纯字面量，每条带唯一 ID，可选 flag（caseless, dotall, multiline 等） |
| **语料** (data/corpus) | 运行期 `hs_scan()` | 待匹配的原始字节流，可以是网络包、文件内容、日志行等任意二进制数据 |

**输出（回调驱动的匹配报告）**：

```
typedef int (*match_event_handler)(
    unsigned int id,           // 匹配到的规则 ID
    unsigned long long from,   // 匹配起始偏移 (字节)
    unsigned long long to,     // 匹配结束偏移 (字节, 不含)
    unsigned int flags,        // 标记位
    void *context              // 用户自定义上下文
);
```

### 两阶段架构

```
┌─────────────── 编译期 (离线, 一次性) ───────────────┐
│                                                      │
│  规则集 ──► parse ──► NFA 图 ──► 引擎分配 ──► 序列化 │
│                                          │           │
│                                     RoseEngine       │
│                                                      │
└──────────────────────────────────────────────────────┘
                        │
                        ▼  hs_database*
┌─────────────── 运行期 (在线, 每次扫描) ──────────────┐
│                                                      │
│  语料 ──► hs_scan(db, data, len, scratch, cb, ctx)   │
│              │                                       │
│              ├─ Lily scan (单字节短规则)               │
│              ├─ FDR/Teddy scan (字面量预过滤)          │
│              ├─ NFA confirm (正则确认)                 │
│              └─ callback(id, from, to, ctx)           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 三种扫描模式

| 模式 | API | 适用场景 |
|------|-----|---------|
| **Block** | `hs_scan()` | 完整数据块一次性扫描，跨包不保持状态 |
| **Streaming** | `hs_open_stream()` / `hs_scan_stream()` / `hs_close_stream()` | 连续数据流，跨包保持匹配状态，适合 TCP 流重组检测 |
| **Vectored** | `hs_scan_vector()` | 非连续内存块（如 scatter/gather IO），逻辑上视为一段连续数据 |

### 匹配语义

- **从左到右**：按输入字节顺序发现匹配
- **最早开始**：对于同一位置的多个匹配，优先报告起始位置最早的
- **最长匹配**：相同起始位置时，优先报告最长的匹配
- **非重叠**：默认不报告重叠匹配（可通过 flag 调整）
- **流式回调**：一旦匹配确认，立即触发回调，不等待扫描结束

## 编译期调用栈

### hs_compile (普通模式) — `src/hs.cpp` + `src/compiler/compiler.cpp`

```
hs_compile(expression, flags, mode, platform, db, error)           [src/hs.cpp:792]
  └─ hs_compile_multi_int(..., Grey())
       │                                                 [src/hs.cpp:510]
       ├─ validate: validModeFlags(), checkMode(), checkPlatform()
       │
       ├─ for each expression:
       │   └─ addExpression(ng, i, expr, flags, ext, id)     [src/compiler/compiler.cpp:280]
       │        │
       │        ├─ 如果是 HS_FLAG_COMBINATION:
       │        │    └─ ng.rm.pl.parseLogicalCombination()    → 逻辑组合解析
       │        │
       │        ├─ ParsedExpression(expr, flags)               [src/hs.cpp:254]
       │        │    └─ parse(expression, mode)                → PCRE→Component 语法树
       │        │
       │        ├─ prefilterTree()                [if HS_FLAG_PREFILTER]
       │        ├─ checkUnsupported()             → 检查不支持的 PCRE 结构
       │        ├─ optimise()                     → Component 树优化
       │        │
       │        ├─ shortcutLiteral()              → 如果是纯字面量:
       │        │    └─ 直接交给 Rose 的字面量表     → return (跳过 NFA 构建)
       │        │
       │        └─ buildGraph(rm, cc, pe)                     [src/compiler/compiler.cpp:719]
       │             ├─ makeNFABuilder()          → 创建 Glushkov NFA 构建器
       │             ├─ makeGlushkovBuildState()  → 创建构建状态
       │             ├─ component→notePositions() → 标记位置→字符映射
       │             ├─ connectInitialStates()    → 连线: start → firsts
       │             ├─ component→buildFollowSet()→ 构建 FOLLOW 关系
       │             ├─ connectFinalStates()      → 连线: lasts → accept
       │             ├─ bs→buildEdges()           → 生成 NFA 边
       │             └─ removeAssertVertices()    → 清理断言顶点
       │                  └─ 返回 BuiltExpression{unique_ptr<NGHolder> g}
       │
       │        └─ ng.addGraph(expr, move(g))     → 将 NFA 图注册到 NG
       │
       ├─ ng.rm.logicalKeyRenumber()              → 逻辑组合 key 重编号
       │
       └─ build(ng, &length, pureFlag)                        [src/compiler/compiler.cpp:578]
            │
            ├─ arm_generateRoseEngine(ng)                     [src/compiler/compiler.cpp:439]
            │    └─ ng.rose→arm_buildRose(minWidth)           [src/rose/rose_build_compile.cpp]
            │         │
            │         ├─ 收集所有字面量 → 角色分配 (role assignment)
            │         ├─ 前置过滤引擎构建:
            │         │   ├─ FDR/Teddy compile    → SIMD 多模字面量
            │         │   ├─ HWLM/Noodle compile   → 大字面量集
            │         │   └─ [ARM] Lily compile    → 单字节短规则
            │         │   └─ [ARM] LilyForTeddy compile → 2-4字节短规则
            │         ├─ NFA 引擎构建:
            │         │   ├─ Limex compile         → 大型 NFA (多 SIMD 宽度)
            │         │   ├─ McClellan compile     → DFA 限界重复
            │         │   ├─ Sheng compile         → 小型 NFA
            │         │   └─ Castle/Truffle/Shufti/Gough compile
            │         ├─ 构建 Rose 字节码程序        → rose_build_program.cpp
            │         ├─ 构建散列表 (scatter)        → rose_build_scatter.cpp
            │         └─ 序列化 → bytecode_ptr<RoseEngine>
            │
            └─ dbCreate(bytecode, len, platform)               [src/compiler/compiler.cpp:496]
                 ├─ hs_database_alloc()           → 分配内存
                 ├─ 64字节对齐放置 bytecode
                 ├─ memcpy(bytecode, RoseEngine)
                 ├─ Crc32c_ComputeBuf()           → CRC32 校验
                 └─ 返回 hs_database*
```

### fat_hs_compile (FAT Database 模式) — `src/hs.cpp` + `src/compiler/compiler.cpp`

```
fat_hs_compile(expression, flags, mode, platform, db, error)     [src/hs.cpp:811]
  └─ fat_hs_compile_multi_int(..., Grey())
       │                                                 [src/hs.cpp:213]
       ├─ === x86 路径 (Grey: allowLily=false, allowNeoFdr=false) ===
       │   ├─ addExpression(x86_ng, ...) × N   → 解析 + NFA 图构建
       │   └─ x86_generateRoseEngine(x86_ng)
       │        └─ x86_ng.rose→x86_buildRose() → RoseEngine_x86
       │                                          (不含 lily/lilyForTeddy/neoFDR 字段)
       │
       ├─ === ARM 路径 ===
       │   ├─ addExpression(arm_ng, ...) × N   → 解析 + NFA 图构建
       │   └─ arm_generateRoseEngine(arm_ng)
       │        └─ arm_ng.rose→arm_buildRose() → RoseEngine_arm
       │                                          (含 lily/lilyForTeddy/neoFDR 字段)
       │
       └─ fat_build(x86_ng, arm_ng, &length, pureFlag)          [src/compiler/compiler.cpp:606]
            └─ FatdbCreate(x86_bytecode, x86_len, arm_bytecode, arm_len, ...)
                 │                                        [src/compiler/compiler.cpp:531]
                 ├─ x86 字节码 → 64字节对齐
                 ├─ ARM 字节码 → 紧随 x86, 64字节对齐
                 ├─ Crc32c_ComputeBuf() × 2  → x86/arm 独立 CRC
                 └─ 返回 fat_hs_database*
```

## 运行期调用栈

### hs_scan (Block 模式) — `src/runtime.c`

```
hs_scan(db, data, length, flags, scratch, onEvent, ctx)           [src/runtime.c:319]
  │
  ├─ validDatabase(db)                        → 校验 magic/version
  ├─ hs_get_bytecode(db)                      → 获取 RoseEngine*
  ├─ validScratch(rose, scratch)              → 校验 scratch
  ├─ markScratchInUse(scratch)                → 标记 scratch 占用
  ├─ populateCoreInfo(scratch, rose, ...)     → 填充 data/len/offset/callback
  ├─ clearEvec() / clearLvec()                → 清空耗尽/逻辑向量
  │
  ├─ [HAVE_NEON] KHSEL_LilyRunExec(rose, scratch)          ← 单字节短规则
  ├─ [HAVE_NEON] KHSEL_LilyForTeddyRunExec(rose, scratch)  ← 2-4字节短规则
  │
  ├─ [smallWriteOffset] runSmallWriteEngine(smwr, scratch)
  │    └─ nfaExecMcClellan_B() or nfaExecSheng_B()         ← 短输入快速路径
  │
  ├─ switch(rose→runtimeImpl):
  │   │
  │   ├─ ROSE_RUNTIME_FULL_ROSE:
  │   │    └─ rawBlockExec(rose, scratch)
  │   │         └─ roseBlockExec(rose, scratch)            [src/rose/block.c]
  │   │              ├─ runAnchoredTableBlock()            ← 锚定匹配器
  │   │              ├─ runRoseProgram()                   ← ROSE 字节码解释器
  │   │              │    │                           [src/rose/program_runtime.c]
  │   │              │    ├─ literal scan callback
  │   │              │    │    └─ FDR/Teddy/HWLM scan    ← SIMD 字面量预过滤
  │   │              │    ├─ NFA dispatch
  │   │              │    │    └─ Limex/McClellan/Sheng/Castle  ← NFA 确认
  │   │              │    └─ match callback → onEvent()    ← 用户回调
  │   │              └─ flush matches
  │   │
  │   ├─ ROSE_RUNTIME_PURE_LITERAL:
  │   │    └─ pureLiteralBlockExec(rose, scratch)
  │   │         └─ hwlmExec(ftable, ...) → roseCallback()  ← 纯字面量路径
  │   │
  │   └─ ROSE_RUNTIME_SINGLE_OUTFIX:
  │        └─ soleOutfixBlockExec(rose, scratch)
  │             └─ nfaQueueExec(nfa, q, ...)               ← 单 NFA 路径
  │
  ├─ flushStoredLilyMatches()                → 上报缓存的 Lily 匹配项
  ├─ flushStoredSomMatches() [if SOM]        → 上报 SOM 匹配
  ├─ roseRunBoundaryProgram() [EOD]          → 运行 EOD 边界程序
  └─ unmarkScratchInUse(scratch)             → 释放 scratch
```

### hs_scan_stream (Streaming 模式) — `src/runtime.c`

```
hs_scan_stream(id, data, length, flags, scratch, onEvent, ctx)   [src/runtime.c:1054]
  └─ hs_scan_stream_internal()                                   [src/runtime.c:897]
       │
       ├─ getStreamStatus(state)                → 检查流是否已终止/耗尽
       ├─ populateCoreInfo(scratch, rose, ...)
       ├─ loadSomFromStream() [if SOM]          → 从流恢复 SOM 状态
       │
       ├─ [HAVE_NEON] KHSEL_LilyRunExec()       [block mode only]
       ├─ [HAVE_NEON] KHSEL_LilyForTeddyRunExec() [block mode only]
       │
       ├─ switch(rose→runtimeImpl):
       │   ├─ ROSE_RUNTIME_FULL_ROSE:
       │   │    └─ rawStreamExec(id, scratch)
       │   │         └─ roseStreamExec(rose, scratch)       [src/rose/stream.c]
       │   │              ├─ runAnchoredTableStream()       ← 锚定匹配(流)
       │   │              ├─ runRoseProgram()               ← ROSE 字节码解释器
       │   │              └─ 流状态更新
       │   │
       │   ├─ ROSE_RUNTIME_PURE_LITERAL:
       │   │    └─ pureLiteralStreamExec()
       │   │         └─ hwlmExecStreaming() → roseCallback()
       │   │
       │   └─ ROSE_RUNTIME_SINGLE_OUTFIX:
       │        └─ soleOutfixStreamExec()
       │             └─ nfaQueueExec() + nfaQueueCompressState()
       │
       ├─ flushStoredLilyMatches() [HAVE_NEON]
       ├─ flushStoredSomMatches() [if SOM]
       ├─ setStreamStatus(state, status)         → 保存流状态
       ├─ maintainHistoryBuffer()                → 维护历史缓冲
       ├─ storeSomToStream() [if SOM]            → SOM 状态写入流
       └─ unmarkScratchInUse(scratch)
```

### 三种 RuntimeImpl 路由

编译期在 `pickRuntimeImpl()` (`src/rose/rose_build_bytecode.cpp:334`) 中根据规则特征选择最快的运行时实现。路由优先级从上到下依次判断：

#### 1. ROSE_RUNTIME_PURE_LITERAL — 纯字面量

**判断条件** (`isPureFloating()`, `src/rose/rose_build_bytecode.cpp:262`)：全部满足以下条件才选中。

| 条件 | 含义 |
|------|------|
| `has_floating == true` | 至少有一个 floating 字面量 |
| `has_outfixes == false` | 无 NFA 引擎 |
| `has_suffixes == false` | 无后缀 NFA |
| `has_leftfixes == false` | 无左缀 NFA |
| `has_anchored == false` | 无锚定匹配器 |
| `has_eod == false` | 无 EOD 边界的规则 |
| `has_states == false` | 无状态追踪的角色 |
| `has_lit_delay == false` | 无延迟字面量 |
| `checks_groups == false` | 无组检查 |

**规则集样例**：

```text
hello
world
foobar
test123
apple
orange
```

所有规则都是纯字面量字符串，不含任何正则元字符。编译期直接将它们交给 HWLM 字面量匹配器，跳过整个 NFA 构建流程。运行时执行 `hwlmExec()` 函数。

#### 2. ROSE_RUNTIME_SINGLE_OUTFIX — 单 NFA

**判断条件** (`isSingleOutfix()`, `src/rose/rose_build_bytecode.cpp:310`)：

| 条件 | 含义 |
|------|------|
| Rose 图中不存在常规角色顶点（除 start 和 SMALL_BLOCK 字面量外） | 无复杂匹配逻辑 |
| `numSomSlots() == 0` | 无 SOM 槽位 |
| `boundary.report_at_eod` 为空 | 无 EOD 上报 |
| `outfixes.size() == 1` | 仅有 1 个 outfix NFA 引擎 |

**规则集样例**：

单条非字面量正则：
```text
/foo[a-z]+bar\d{2}/
```

或多条共享同一个 NFA 引擎的正则（编译器合并后只产生一个 outfix）。运行时直接执行 `nfaQueueExec()`，跳过 ROSE 字节码解释器。

#### 3. ROSE_RUNTIME_FULL_ROSE — 完整 ROSE

以上两种条件都不满足时走此路径。这是最常见的运行时模式，走完整的 `roseBlockExec()` / `roseStreamExec()` 字节码解释器。

**规则集样例**：

混合复杂度、带锚定、含逻辑组合的规则：
```text
1:/foo.*bar/s
2:/ba[rz]/i
3:hello
4:10001:/cat|dog|rabbit/
5:10002:/abc & def/  # 逻辑组合
```

这个规则集包含：1 条多态正则 + 1 条字符类 + 1 条纯字面量 + 1 条多选正则 + 1 条逻辑组合，编译器会分配多个引擎（FDR 字面量预过滤 + NFA 确认），必须走完整 ROSE 路径。

## 各引擎职责

| 引擎 | 类型 | 适用场景 |
|------|------|----------|
| **FDR** | 字面量预过滤 | 多模式字面量集合的 SIMD 扫描 |
| **Teddy** | 字面量预过滤 | FDR 的 SIMD 加速变体，flood fill 算法 |
| **HWLM** | 字面量预过滤 | 大字面量集的 Hyperscan-Wu-Manber 算法 |
| **Noodle** | 字面量预过滤 | 少量大字面量的快速扫描 |
| **Limex** | NFA 引擎 | 大型 NFA 图执行，支持多种 SIMD 宽度 |
| **McClellan** | DFA 引擎 | 带限界重复的确定性匹配 |
| **Sheng** | NFA 引擎 | 极小型 NFA (<64 状态) 的紧凑编码 |
| **Gough** | NFA 引擎 | 带辅助加速表的 NFA |
| **Castle** | 特化引擎 | 单字符重复模式 `.` 或 `[^x]` |
| **Truffle** | 特化引擎 | 单字符匹配 |
| **Shufti** | 特化引擎 | 字符类范围匹配 |
| **MPV** | 调度引擎 | 多模式向量化分发 |
| **Tamarama** | 调度引擎 | 多引擎组合调度 |

## ARM 鲲鹏增强层 (KHSEL)

`src/kunpeng-enhanced/` 是华为在鲲鹏平台上新增的优化模块：

### Lily — 单字节短规则匹配

- **编译期** (`lily.cpp`): `KHSEL_BuildLily()` — 将单字节规则（如 `a`, `b`, `[0-9]`）编译为 16 字节 SIMD mask
- **运行期** (`runtime_lily.c`): `KHSEL_LilyRunExec()` — 用 NEON 指令并行匹配单字节规则
- 特点：支持大小写不敏感匹配，通过 flags 控制

### LilyForTeddy — 2~4字节短规则匹配

- **编译期** (`lily.cpp`): `KHSEL_BuildLilyForTeddy()` — 将 2~4 字节规则编译为 `lilyTeddy` 结构体
- **运行期** (`runtime_lily.c`): `KHSEL_LilyForTeddyRunExec()` — 用 NEON 指令并行匹配
- 使用优先队列按规则长度排序，从长到短匹配

### NeoFDR — 增强 FDR 引擎

- `fdr_enhanced.c`: ARM NEON 优化的 FDR 实现

### KHSEL 类型系统

- `khsel_typebase.h` — 基础类型定义
- `khsel_type.h` — KhselResult, LilyMatchItem 等复合类型
- `khsel_core.h` — NEON intrinsics 封装和编译器兼容宏
- `khsel_ops.h` — SIMD 操作封装

### 配置控制

`config.txt` 中的 `allowLily` 和 `allowNeoFdr` 在编译期通过 `Grey` 对象读取，控制是否启用这些 ARM 专属优化路径。


## 关键数据结构

Hyperscan 的数据结构设计遵循两个核心原则：**(1) offset 间接寻址** — 所有子结构通过 `base + offset` 访问，绝不用裸指针，确保编译产物可序列化为 relocatable blob；**(2) 缓存行对齐** — 高频访问的热数据全部 `ROUNDUP_CL` 对齐到 64 字节边界。

### 数据流全景

```
hs_scan(db, data, len, scratch, callback, ctx)
│
├─ hs_get_bytecode(db) ───────────────────────► RoseEngine* (根结构体)
│     db + db->bytecode = RoseEngine
│
├─ RoseEngine.fmatcherOffset ─────────────────► HWLM → FDR/Teddy (字面量预过滤)
├─ RoseEngine.lilyOffset ─────────────────────► Lily masks (单字节NEON扫描)
├─ RoseEngine.lilyForTeddyOffset ─────────────► lilyTeddy (2~4字节NEON扫描)
├─ RoseEngine.amatcherOffset ─────────────────► anchored_matcher_info (锚定DFA)
├─ RoseEngine.nfaInfoOffset ──────────────────► NfaInfo[] (NFA引擎元数据)
│     └─ NfaInfo.nfaOffset ───────────────────► NFA bytecode (Limex/Sheng/...)
│
└─ RoseEngine.stateOffsets ───────────────────► RoseStateOffsets (流状态布局)
```

### RoseEngine — 编译期输出的根结构体

`src/rose/rose_internal.h:437` — 整个数据库字节码的根，70+ 字段的巨型结构体，是所有子引擎的索引入口。

**核心设计：offset 间接寻址**

```c
// 所有子结构都通过 offset 访问, 不用指针 — bytecode 需序列化到磁盘/网络
static really_inline
const struct HWLM *getFLiteralMatcher(const struct RoseEngine *t) {
    if (!t->fmatcherOffset) return NULL;             // offset=0 表示不存在
    return (const struct HWLM *)((const char *)t + t->fmatcherOffset);
}

static really_inline
const struct NFA *getNfaByQueue(const struct RoseEngine *t, u32 qi) {
    const struct NfaInfo *info = getNfaInfoByQueue(t, qi); // offset → NfaInfo
    return getNfaByInfo(t, info);                           // NfaInfo.nfaOffset → NFA
}
```

**x86 vs ARM 双版本**

```c
struct x86_RoseEngine {
    u32 lilyOffset;           // 防止报错 — x86 上永远为 0
    u32 lilyForTeddyOffset;   // 防止报错 — x86 上永远为 0
    ...
};

struct RoseEngine {           // ARM 版本
    u32 lilyOffset;           // 真实字段, 指向 Lily 单字节 mask 表
    u32 lilyForTeddyOffset;   // 真实字段, 指向 lilyTeddy 结构
    ...
};
```

关键字段分类：

| 类别 | 字段 | 含义 |
|------|------|------|
| **模式标识** | `runtimeImpl` | 0=FULL_ROSE, 1=PURE_LITERAL, 2=SINGLE_OUTFIX |
| | `pureLiteral`, `hasSom`, `canExhaust` | 特征 flag |
| **子引擎 offset** | `fmatcherOffset` | Floating HWLM (FDR/Teddy) |
| | `amatcherOffset` | Anchored matcher (DFA) |
| | `lilyOffset` | Lily 单字节 NEON 引擎 (ARM) |
| | `lilyForTeddyOffset` | Lily 2~4 字节引擎 (ARM) |
| | `longLitTableOffset` | 长字面量表 |
| **NFA 队列** | `outfixBeginQueue/EndQueue` | Outfix NFA 的队列范围 |
| | `leftfixBeginQueue` | Prefix/Infix NFA 的队列起点 |
| | `nfaInfoOffset` | NfaInfo 数组, 每个 NFA 的元数据 |
| **距离控制** | `floatingDistance/MinDistance` | Floating 表的有效扫描范围 |
| | `anchoredDistance/MinDistance` | Anchored 表的有效扫描范围 |
| | `maxBiAnchoredWidth` | 双向锚定最大宽度 |
| **流状态** | `stateOffsets` | `RoseStateOffsets` — 完整流状态内存布局 |
| | `historyRequired` | Streaming 模式所需的历史字节数 |

### hs_database — 对外暴露的数据库句柄

`src/database.h:50` — 轻量 header + 字节码 payload。

```
┌──────────────────────────────────────┐
│ hs_database (header)                 │
│  magic      = HS_DB_MAGIC            │  ← 校验: 是不是 Hyperscan 数据库
│  version    = HS_DB_VERSION          │  ← 校验: 版本兼容性
│  platform   = target 平台特征位       │  ← 校验: 是否在当前 CPU 上编译
│  crc32      = 字节码的 CRC32          │  ← 校验: 数据完整性
│  bytecode   = offset of RoseEngine   │  ← 核心: db + bytecode = RoseEngine*
├──────────────────────────────────────┤
│ bytes[] (实际 RoseEngine 字节码)      │
│  ├─ HWLM (FDR/Teddy) table          │
│  ├─ NFA bytecode[]                   │
│  ├─ Lily masks                       │
│  └─ Programs                         │
└──────────────────────────────────────┘
```

### fat_hs_database — 双平台字节码

`src/fat_database.h:49` — 一份数据库同时包含 x86 + ARM 两套 RoseEngine。

```
┌──────────────────────────────────────────┐
│ fat_hs_database header                   │
│  x86_length / arm_length                 │
│  x86_crc32 / arm_crc32                   │  ← 两份独立 CRC
│  x86_bytecode / arm_bytecode (offsets)   │
├──────────────────────────────────────────┤
│ x86 RoseEngine bytecode                  │  ← x86_ng→x86_buildRose()
│  x86_RoseEngine (lily 占位符)            │
├──────────────────────────────────────────┤
│ ARM RoseEngine bytecode                  │  ← arm_ng→arm_buildRose()
│  RoseEngine (lily 真实有效)              │
└──────────────────────────────────────────┘
```

运行时根据编译宏选择：
```c
#if defined(ARCH_X86_64)
    return db + db->x86_bytecode;   // x86 取 x86
#elif defined(ARCH_AARCH64)
    return db + db->arm_bytecode;   // ARM 取 ARM
#endif
```

### hs_scratch — 每线程临时工作空间

`src/scratch.h:191` — 匹配过程中的可变状态全在这里，编译期根据 RoseEngine 计算大小一次性分配，运行期复用。

| 字段 | 作用 |
|------|------|
| `core_info` | 当前扫描上下文：`buf`, `len`, `callback`, `userContext` |
| `tctxt` (`RoseContext`) | Rose 运行期状态：groups, 各类 match offset, 当前队列索引 |
| `lily_ctx` / `lily_for_teddy_ctx` | Lily 环形缓冲队列：items 数组, start/size/capacity |
| `fdr_conf` / `fdr_conf_offset` | FDR/Teddy confirm 的当前 conf 值和偏移 |
| `bstate` / `tstate` / `fullState` | NFA 状态存储：block / transient / full 三种 |
| `queues` + `aqa` | NFA 队列数组 + active queue fatbit |
| `deduper` | 匹配去重器：even/odd 双缓冲 log |
| `som_store` | SOM (Start of Match) 位置数组 |
| `delay_slots` | 延迟字面量的 fatbit 槽位 |

**状态标志位** (`core_info.status`):

| 标志 | 含义 |
|------|------|
| `STATUS_TERMINATED` | 用户回调返回非零, 提前终止扫描 |
| `STATUS_EXHAUSTED` | 所有 exhaustion key 耗尽, 不可能再匹配 |
| `STATUS_DELAY_DIRTY` | 延迟字面量命中历史区, 需要重建扫描 |
| `STATUS_ERROR` | Rose 程序执行异常 |

**LilyMatchItem — 8 字节位域压缩** (`src/scratch.h:71`):

```c
#define LILY_REPORT_INDEX_BITS    3U          // 低 3 bit: 最多 8 个 Report
#define LILY_TO_OFFSET_BITS       (64U - 3U) // 高 61 bit: toOffset
struct LilyMatchItem {
    unsigned long long onmatch_index : 3;     // Report 索引 (0~7)
    unsigned long long toOffset      : 61;    // 匹配结束偏移
};  // 8 字节 = 1 条缓存行 (64B) 可容纳 8 个 LilyMatchItem
```

### HWLM — 字面量匹配器包装层

`src/hwlm/hwlm_internal.h:48` — header 后紧跟引擎专属字节码，`type` 字段决定下层是 Noodle 还是 FDR/Teddy。

```
┌──────────────────────────────────────┐
│ HWLM header                          │
│  type = HWLM_ENGINE_NOOD (16)        │  ← 1 条字面量 → Noodle
│      or HWLM_ENGINE_FDR  (12)        │  ← 多条字面量 → FDR/Teddy
│  accel1_groups, accel1, accel0       │  ← 加速辅助
├──────────────────────────────────────┤
│ Engine-specific bytecode             │
│  Noodle → Noodle engine              │
│  FDR    → FDR 或 Teddy 或 NeoFDR     │
└──────────────────────────────────────┘
```

### RoseStateOffsets — 流状态内存布局

`src/rose/rose_internal.h:194` — 编译期计算好的各类状态在流状态中的偏移。Streaming 模式下所有需要跨 buffer 保持的状态都存储在这段连续内存中。

```
Stream State 内存布局 (相对于 state 基址):
┌──────────────────────┐ ← state
│ status_flags         │ ROSE_STATE_OFFSET_STATUS_FLAGS
│ role mmbit           │ ROSE_STATE_OFFSET_ROLE_MMBIT
├──────────────────────┤
│ [history]            │ ← history .. +historyRequired
│ [exhausted]          │ ← exhausted .. +exhausted_size
│ [logicalVec]         │ ← logicalVec .. +logicalVec_size
│ [combVec]            │
│ [activeLeafArray]    │ ← active NFA tracking
│ [activeLeftArray]    │
│ [leftfixLagTable]    │ ← 1 byte per leftfix engine
│ [anchorState]        │ ← McClellan DFA states
│ [groups]             │
│ [longLitState]       │
│ [somLocation]        │
├──────────────────────┤
│ [nfaStateBegin..end) │ ← Limex/Sheng/etc NFA engine states
└──────────────────────┘
```

### NfaInfo / LeftNfaInfo — NFA 引擎元数据

`src/rose/rose_internal.h:144,157` — 每个 NFA 队列对应一个 `NfaInfo`，每个 leftfix (prefix/infix) 额外对应一个 `LeftNfaInfo`。

```c
struct NfaInfo {
    u32 nfaOffset;        // NFA bytecode 在 RoseEngine 中的 offset
    u32 stateOffset;      // NFA 状态在流状态中的 offset
    u32 fullStateOffset;  // 未压缩状态在 scratch 中的 offset
    u32 ekeyListOffset;   // exhaustion key 列表
    u8  no_retrigger;     // 禁止重复触发
    u8  in_sbmatcher;     // 由 small-block matcher 处理
    u8  eod;              // 仅产生 EOD 匹配
};

struct LeftNfaInfo {
    u32 maxQueueLen;      // 最大队列长度
    u32 maxLag;           // 后继 role 的最大滞后
    u8  transient;        // 是否为 transient rose
    char eager;           // eager 模式: 积极运行到首次匹配或死亡
    u32 countingMiracleOffset; // RoseCountingMiracle offset
    rose_group squash_mask;    // NFA 死亡时应用的 squash mask
};
```

### 引擎专属结构一览

| 结构体 | 文件 | 关键字段 |
|--------|------|---------|
| `FDR` | `src/fdr/fdr_internal.h:69` | engineID, stride(1/2/4), domain(9-15), domainMask, tabSize, confOffset, floodOffset |
| `FDRConfirm` | `src/fdr/fdr_confirm.h:78` | andmsk (u64a), mult (u64a), nBits, groups — 8 字节 confirm hash |
| `Teddy` | `src/fdr/teddy_internal.h` | 继承 FDR + numMasks(1-4) — NEON flood fill 使用的 nibble masks |
| `lilyTeddy` | `src/fdr/teddy_internal.h:66` | engineID(19), lilyReport/Ekey/Len/QuietOffset — Lily 2~4 字节引擎 |
| `RoseLongLitTable` | `src/rose/rose_internal.h:631` | caseful/nocase sub-table (hash + bloom), streamStateBytes, maxLen |
| `RoseCountingMiracle` | `src/rose/rose_internal.h:134` | shufti flag, count, c, poison, lo(m128), hi(m128) — 计数字符触发器 |
