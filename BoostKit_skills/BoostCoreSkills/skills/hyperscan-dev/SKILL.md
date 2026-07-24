---
name: hyperscan-dev
description: Hyperscan ARM (Kunpeng) 平台的开发、编译和验证工作流。当你需要编译 Hyperscan、运行 hsbench 测试验证、修改代码架构、调试 ARM NEON 适配问题时使用此技能。覆盖 cmake/make 构建、hsbench 性能/功能验证、config.txt 配置组合测试、以及 Rose/Lily/ 等核心引擎的开发指导。
---

# Hyperscan ARM 平台开发工作流


## 核心工作流

### 编译

**ARM 平台:**
```bash
cd .claude/skills/hyperscan-dev/scripts
./build_arm.sh          # Release 编译 (默认 -j64)
./build_arm.sh debug    # Debug
./build_arm.sh release 32  # Release, -j32
```

**x86 平台:**
```bash
./build_x86.sh          # Release 编译
./build_x86.sh debug    # Debug 
```

### 验证

编译成功后运行 benchmark.sh:

```bash
cd .claude/skills/hyperscan-dev/scripts
# Streaming 模式 (默认), 2 次迭代
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db

# Block 模式, 10 次迭代
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db N 10

# Vectored 模式, 5 次迭代
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db V 5
```

实际执行命令: `hsbench -e <规则集> -c <语料库> -n <次数> [-N|-V]`

脚本自动定位 `build/bin/hsbench`，如果找不到会给出明确的编译指引。hsbench 是编译 Hyperscan 项目时一起生成的，路径为 `<项目根>/build/bin/hsbench`。

确认 Matches per iteration = **637380**，如果不匹配说明修改引入了 bug。

### 配置组合验证

修改 `config.txt`（项目根目录），验证不同 Lily/NeoFDR 开关组合：

```
allowLily:1;allowNeoFdr:1;   # 全开（默认）
allowLily:0;allowNeoFdr:1;   # 仅 NeoFDR
allowLily:1;allowNeoFdr:0;   # 仅 Lily
allowLily:0;allowNeoFdr:0;   # 全关
```


## 自动化脚本

`scripts/` 目录下提供三个非交互式脚本, 全部自动推算项目路径。

### build_arm.sh — ARM 平台编译

```bash
./build_arm.sh              # Release: cmake .. && make -j64
./build_arm.sh debug        # Debug:   cmake .. -DCMAKE_BUILD_TYPE=DEBUG && make -j64
./build_arm.sh release 32   # 指定 -j32
```

### build_x86.sh — x86 平台编译

```bash
./build_x86.sh              # Release
./build_x86.sh debug        # Debug 
```


### benchmark.sh — 性能测试

```bash
./benchmark.sh <规则集> <语料库> [mode] [迭代次数]

# 示例:
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db         # Stream
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db N       # Block
./benchmark.sh ../assets/fdr_100.literals /data/alexa200.db V       # Vectored
```

自动解析 hsbench 输出, 提取:
- 扫描耗时、语料大小
- 匹配数/迭代
- Mean throughput (Mbit/s)
- Max throughput (Mbit/s)

## 代码架构

详细架构说明见 `references/architecture.md`，包含 Hyperscan 输入/输出模型、完整编译/运行调用栈、三种运行时模式、所有引擎职责、ARM KHSEL 增强层、FAT-Bytecode 方案、以及全部关键数据结构（RoseEngine, hs_database, fat_hs_database, hs_scratch, HWLM, RoseStateOffsets 等）。


### 代码修改后的验证顺序

1. 本地修改代码
2. 同步到 openEuler 环境
3. `./build_arm.sh`（先确认编译通过）
4. `./benchmark.sh ...`（确认功能正确，结果 637380）
5. 切换 `config.txt` 中 allowLily/allowNeoFdr 组合，重复步骤 3-4
6. 如有单元测试失败，检查 `./bin/unit-hyperscan` 和 `./bin/unit-internal`

### 调试与问题排查

出现假阴性/假阳性时, 可按照如下方式排查 
- **hscollider** 正确性验证（`-t N` streaming、`-a` 对齐测试、错误输出解读）
- **hsdump** 数据库检查（查看编译产物走了哪个引擎）
- **引擎隔离**（config.txt 开关、修改 `teddy_engine_description.cpp` 禁用特定引擎、`fdr.c` funcs[] 替换）
- **ARM vs x86 交叉验证**（`-D__X86_64__` 模拟 x86 路径、最小对照实验）
- **常见故障模式**（SIMD 移位方向、有符号/无符号比较、pshufb 索引超范围、Lily 假阳性污染、char 符号不一致）
- **标准排查流程**（复现→缩小范围→对照验证→引擎隔离→SIMD 排查→最小复现）

## ARM vs x86 关键差异

| 模块 | 文件 | 作用 |
|------|------|------|
| **Lily** | `lily.cpp`, `runtime_lily.c` | 单字节短规则 NEON 并行匹配 (≤8条) |
| **LilyForTeddy** | `lily.cpp`, `runtime_lily.c` | 2~4 字节短规则 NEON 并行匹配 (≤8条) |
| **NeoFDR** | `fdr_enhanced.c` | FDR 引擎 NEON 加速: 紧凑查表 + 无 flood detect 主循环 |
| **NEON Shufti** | `shufti.c` | 字符类范围匹配 NEON 实现 (BATCH_SIZE=16) |
| **NEON Compare** | `compare.h` | `u64a` 粒度的字符串比较: 8 字节批量 caseful/nocase |
| **Teddy Common** | `lily_teddy_common.h` | NEON `pshufb`+`palignr` 做 Teddy nibble mask 展开 |
| **SIMD Ops** | `khsel_ops.h` | NEON intrinsic 封装 (+ `arm_neon.h`) |
| **Base Types** | `khsel_type.h`, `khsel_typebase.h` | 平台基础类型和错误码体系 |

### 编译期结构体差异

`src/rose/rose_internal.h` 中定义了两套 RoseEngine，通过 `fat_hs_compile` 分别编译

## 语料生成

### gen_corpus.py — 匹配比例可控的语料生成器

`assets/gen_corpus.py` 包装 Hyperscan 自带的 `CorpusBuilder.py`

```bash
cd .claude/skills/hyperscan-dev/assets

# 100MB 语料, 50% 命中率 (默认)
python gen_corpus.py -r fdr_100.literals -o test.db -s 100M -m 50

# 10MB 语料, 10% 命中率 (稀疏匹配)
python gen_corpus.py -r fdr_100.literals -o sparse.db -m 10

# 1GB 语料, 90% 命中率 (密集匹配), 指定种子
python gen_corpus.py -r full_rose_mixed.literals -o dense.db -s 1G -m 90 --seed 123
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `-r`, `--rules` | 必填 | `.literals` 规则集 |
| `-o`, `--output` | 必填 | 输出 `.db` 文件 |
| `-s`, `--size` | 10M | 语料大小, 支持 K/M/G |
| `-m`, `--match-ratio` | 50 | 匹配块百分比 (0-100) |
| `-c`, `--chunk-size` | 4096 | 每块字节数 |
| `--seed` | 42 | 随机种子 (相同参数+种子=相同语料) |

生成的 `.db` 是 SQLite 数据库, 表 `chunk(id, stream_id, data)`。匹配块在随机可打印字符中嵌入一条规则字面量, 噪音块为纯随机可见字符 (0x20~0x7E)。

### CorpusBuilder.py（底层库）

`tools/hsbench/scripts/CorpusBuilder.py` — Hyperscan 自带的语料构建模块。`gen_corpus.py` 是对它的封装。同一目录下还有 `gutenbergCorpus.py`（从 Project Gutenberg 图书生成）、`linebasedCorpus.py`（文本行→block）和 `pcapCorpus.py`（网络抓包→payload）。

## 规则集资产

`assets/` 下提供 19 个预置 `.literals` 文件 + `ENGINE_MAP.md`（完整的 proto ↔ literals 映射文档），覆盖 Hyperscan 全部引擎路径。

### arm_buildFinalEngine Proto 对应关系

`arm_buildFinalEngine()` (`src/rose/rose_build_bytecode.cpp:3703`) 中构建的各个 proto 与 assets 规则集的对应:

```
arm_buildFinalEngine
├─ KHSEL_BuildLily ─────────────────── Lily 单字节 [lily_8]
├─ KHSEL_BuildLilyForTeddy ─────────── Lily 2-4字节 [lily_forteddy_8]
├─ buildNfas ───────────────────────── Sheng/McClellan/Limex/... [NFA 引擎]
├─ buildFloatingMatcherProto ───────── Noodle/Teddy/NeoFDR/FDR [HWLM]
├─ buildDelayRebuildMatcherProto ───── Delay Rebuild HWLM
├─ buildEodAnchoredMatcherProto ────── EOD Anchored HWLM
├─ buildSmallBlockMatcherProto ─────── Small Block HWLM
├─ buildLongLiteralTable ───────────── 长字面量表
├─ buildAnchoredMatcher ────────────── Anchored DFA
└─ pickRuntimeImpl ─────────────────── PURE_LITERAL / SINGLE_OUTFIX / FULL_ROSE
```

详见 `assets/ENGINE_MAP.md`。

### 引擎触发规则集一览

#### 字面量引擎 (Floating HWLM)

| 文件 | 引擎 | 条数 | 规则特征 | 触发条件 |
|------|------|------|----------|----------|
| `noodle_1.literals` | Noodle | 1 | 单条字面量 | `lits.size()==1` |
| `teddy_12.literals` | Teddy | 12 | 6字节, 不同后缀 | ≤48条, `fdrAllowTeddy` |
| `fat_teddy_48.literals` | Fat Teddy | 48 | 8字节, 3组×16条 | AVX2 only, x86 Fat Teddy |
| `neofdr_50.literals` | NeoFDR | 50 | 8字节, 统一前缀 | >48条, `allowNeoFdr:1`, ARM |
| `fdr_100.literals` | FDR | 100 | 8字节, 统一前缀 | >48条, 标准兜底 |

#### ARM 短规则引擎 (Lily)

| 文件 | 引擎 | 条数 | 触发条件 |
|------|------|------|----------|
| `lily_8.literals` | Lily | 8 | 单字节字面量, `allowLily:1`, block 模式 |
| `lily_forteddy_8.literals` | LilyForTeddy | 8 | 2~4字节字面量, `allowLily:1`, block 模式 |
| `lily_and_forteddy_16.literals` | 两者同时 | 16 | 8条单字节 + 8条2~4字节 |

#### NFA 引擎

| 文件 | 引擎 | 条数 | 触发条件 |
|------|------|------|----------|
| `sheng_small.literals` | Sheng | 2 | 极小NFA (<64状态) |
| `mcclellan_repeat.literals` | McClellan | 2 | 限界重复 |
| `castle_dotstar.literals` | Castle | 3 | `.*` 前导模式 |
| `truffle_char.literals` | Truffle | 3 | 单字符匹配 |
| `shufti_range.literals` | Shufti | 3 | 字符类范围 |
| `limex_complex.literals` | Limex | 3 | 复杂大NFA |
| `gough_accel.literals` | Gough | 2 | 中等NFA+加速表 |

#### 运行时路由 / 特殊路径

| 文件 | RuntimeImpl / 说明 | 条数 |
|------|-------------------|------|
| `pure_literal_5.literals` | ROSE_RUNTIME_PURE_LITERAL | 5 |
| `single_outfix_1.literals` | ROSE_RUNTIME_SINGLE_OUTFIX | 1 |
| `full_rose_mixed.literals` | ROSE_RUNTIME_FULL_ROSE | 5 |
| `nofdr_single_regex.literals` | 纯正则, 不进 HWLM/字面量路径 | 1 |
