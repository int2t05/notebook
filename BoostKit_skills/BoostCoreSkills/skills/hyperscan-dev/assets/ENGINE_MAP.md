# arm_buildFinalEngine Proto ↔ Literals 规则集映射

`rose_build_bytecode.cpp:3703` — `RoseBuildImpl::arm_buildFinalEngine()` 构建的各 proto 与 assets 下 `.literals` 文件的对应关系。

## 构建流程全景

```
arm_buildFinalEngine(minWidth)
│
├─ KHSEL_BuildLily          → Lily 单字节引擎
├─ KHSEL_BuildLilyForTeddy  → LilyForTeddy 2~4字节引擎
│
├─ buildNfas                → NFA 引擎分解 (Sheng/McClellan/Limex/...)
│
├─ prepOutfixes / prepMpv   → Outfix / MPV
│
├─ buildFloatingMatcherProto   → Floating HWLM (Noodle/Teddy/FDR/NeoFDR)
├─ buildDelayRebuildMatcherProto → Delay Rebuild HWLM
├─ buildEodAnchoredMatcherProto  → EOD Anchored HWLM
├─ buildSmallBlockMatcherProto   → Small Block HWLM
│
├─ buildLongLiteralTable    → 长字面量表 (≥longLitLengthThreshold)
├─ buildAnchoredMatcher     → 锚定匹配器 (Anchored DFA)
│
├─ addLily / addLilyForTeddy → 将 Lily 引擎附加到 RoseEngine
│
└─ pickRuntimeImpl          → ROSE_RUNTIME_PURE_LITERAL
                               ROSE_RUNTIME_SINGLE_OUTFIX
                               ROSE_RUNTIME_FULL_ROSE
```

## 一、Lily / LilyForTeddy 短规则引擎

触发路径: `shortcut_literal.cpp` → `rose_build_add.cpp::addChar/addShortLit`

| .literals 文件 | 引擎 | 触发条件 | 规则特征 |
|---------------|------|---------|---------|
| `lily_8.literals` | **Lily** | 单字节, allowLily:1, ≤8条 | `a~2` 8个不同单字符 |
| `lily_forteddy_8.literals` | **LilyForTeddy** | 2~4字节, allowLily:1, ≤8条 | abcd, ef, yz 等 |
| `lily_and_forteddy_16.literals` | **Lily + LilyForTeddy** | 8+8 同时触发 | 8个单字节 + 8个2~4字节 |

## 二、Floating HWLM 字面量匹配器

触发路径: `buildFloatingMatcherProto` → `hwlmBuildProto` → `fdrBuildProto`

```
fdrBuildProto(HWLM_ENGINE_FDR)
│
├─ Tedddy Build (fdrAllowTeddy)
│   ├─ ARM: 8bucket × 6load = 48 max
│   └─ x86: 16bucket × 6load = 96 max
│
├─ NeoFDR (allowNeoFdr, Teddy failed)
│   └─ chooseNeoFdrEngine → engineID=1 → KHSEL_NeoFdrEngineExec
│
└─ 标准 FDR (兜底)
    └─ chooseEngine → engineID=0 → fdr_engine_exec
```

| .literals 文件 | 引擎 | 触发条件 | 为什么 |
|---------------|------|---------|--------|
| `noodle_1.literals` | **Noodle** | 仅 1 条字面量 | `isNoodleable()` 直接走 Noodle |
| `teddy_12.literals` | **Teddy** | 12 ≤ ARM 48 上限 | `chooseTeddyEngine` 成功, `pack()` 可容纳 |
| `fat_teddy_48.literals` | **Fat Teddy** | AVX2 only (!ARM) | maskWidth=2, dup nibble mask, x86 Fat Teddy |
| `neofdr_50.literals` | **NeoFDR** | >48 条, allowNeoFdr:1 | Teddy 失败 → `chooseNeoFdrEngine` |
| `fdr_100.literals` | **FDR** | >48 条, 标准兜底 | Teddy 失败 → `chooseEngine` (engineID=0) |
| `nofdr_single_regex.literals` | **不进 HWLM** | 纯正则无纯字面量 | 直接走 NFA 图构建 |

### NeoFDR 零尾过滤 (编译期)

当 `allowNeoFdr:1` 且字面量 ≥8 字节时，多个 violet 路径检查末尾 8 字节是否全 `\0`，是则丢弃:

| 文件 | 行号 | 作用 |
|------|------|------|
| `ng.cpp` | 585-589 | addLiteral 拒绝零尾 |
| `ng_literal_component.cpp` | 182-186 | 字面量组件拒绝零尾 |
| `ng_violet.cpp` | 685-710 | 候选集移除零尾 |
| `ng_violet.cpp` | 996-1013 | 拒绝零尾 best_lit |
| `ng_violet.cpp` | 1469-1491 | Cut 分析时全零尾放弃切分 |
| `ng_violet.cpp` | 2475-2492 | Accept 边过滤 |
| `ng_violet.cpp` | 2519-2537 | 另一路径同样过滤 |

原因: FDR confirm hash 为 8 字节 (`CONF_TYPE = u64a`)，零尾字面量会导致洪水式假阳性。

## 三、NFA 引擎 (buildNfas)

`buildNfas()` 对 NFA 图进行分解/委托，每个子图匹配最合适的引擎。

| .literals 文件 | 引擎 | 触发条件 |
|---------------|------|---------|
| `sheng_small.literals` | **Sheng** | 状态数 < shengLimit (~64) |
| `mcclellan_repeat.literals` | **McClellan** | DFA 有界重复 |
| `castle_dotstar.literals` | **Castle** | `.*` 型模式 |
| `truffle_char.literals` | **Truffle** | 单字符类 |
| `shufti_range.literals` | **Shufti** | 字符范围 |
| `limex_complex.literals` | **Limex** | 大 NFA (多宽度 SIMD) |
| `gough_accel.literals` | **Gough** | 带辅助加速表的 NFA |

## 四、运行时模式 (pickRuntimeImpl)

`rose_build_bytecode.cpp:348-356` — 根据规则集特征选择最快执行路径:

| .literals 文件 | 运行时模式 | 条件 |
|---------------|----------|------|
| `pure_literal_5.literals` | **ROSE_RUNTIME_PURE_LITERAL** | 全部 floating literal, 无 NFA/锚定/EOD/state |
| `single_outfix_1.literals` | **ROSE_RUNTIME_SINGLE_OUTFIX** | outfixes==1, 无 Rose 角色/SOM/EOD |
| `full_rose_mixed.literals` | **ROSE_RUNTIME_FULL_ROSE** | 混合字面量+正则+锚定 → 完整 ROSE 解释器 |

### 各模式的执行路径

```
ROSE_RUNTIME_PURE_LITERAL  → pureLiteralBlockExec → hwlmExec (FDR scan)
                               (不启动 ROSE 解释器, 最快路径)

ROSE_RUNTIME_SINGLE_OUTFIX → soleOutfixBlockExec → nfaQueueExec
                               (不启动 ROSE 解释器)

ROSE_RUNTIME_FULL_ROSE     → roseBlockExec
                               ├─ runAnchoredTable     (锚定 DFA)
                               ├─ runSmallWriteEngine  (短写优化)
                               ├─ runLilyRunExec       (Lily 单字节)
                               ├─ runLilyForTeddyExec  (Lily 2~4字节)
                               └─ runRoseProgram       (ROSE 字节码解释器)
```