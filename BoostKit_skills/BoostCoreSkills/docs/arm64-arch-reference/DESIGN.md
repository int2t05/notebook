# arm64-arch-reference — 设计文档

> 本文档是该 skill 的完整分析与设计记录（内部维护用，不随 skill 分发）。
> 面向后续维护者：解释 skill 解决什么问题、数据从哪来、如何构建与再生成、如何验证。

---

## 1. 背景与目标

**使用者场景**：在编译器（如 LLVM/GCC/Go）上开发 ARM64（AArch64/A64）相关优化，需要频繁查阅
ARM 架构手册的**架构特性（Features）**与**指令（Instructions）**——特性的引入版本、可选/强制状态、
指令的汇编模板/编码、以及"某指令受哪个 `FEAT_*` 门控"。这些事实**极易记错**（典型如 LSE 的引入版本、
SME2 的版本、各扩展的可选强制），凭记忆作答风险高。

**目标**：一个可在任意会话触发、自包含、便于 Claude/人工快速查阅的 skill，含三类内容：

1. **Features.md** — 全量 A-profile 架构特性，按功能域分类，列：
   `特性名 / 英文标题 / 中文翻译 / 中文介绍 / 引入版本 / 执行状态 / 可选或强制`
2. **instructions/**（按分类拆多文件）— 全量 A64 指令，列：
   `指令名 / 英文简述 / 中文简介 / 汇编模板(Encoding) / 关联特性`
3. **总览/导航**（`SKILL.md` + `references/overview.md`）— 功能域映射、指令分类索引、检索指引。

---

## 2. 数据来源（官方，只读）

ARM 机器可读规范（AARCHMRS）A-profile，版本 **v9Ap6-A（Armv9.6）/ 2026-03_rel / schema 2.8 / build 750**。

| 数据 | 官方下载地址 | 内容 |
| --- | --- | --- |
| 架构特性 | `https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-Features/AARCHMRS/AARCHMRS_A_profile-2026-03_96.tar.gz` | `Features.json`：363 个 parameters，其中 346 个 `FEAT_*`，含 `title`/`description.before`(英文详述,92%覆盖)/`description.after`(版本/状态/可选性) |
| A64 指令 | `https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz` | 逐指令 XML + 4 个索引：`index`(Base)/`fpsimdindex`(SIMD&FP)/`sveindex`(SVE)/`mortlachindex`(SME) |
| 人类可读手册 | `https://developer.arm.com/documentation/ddi0487/mb` | Arm ARM (DDI 0487 M.b)，用于深读核对 |

**指令 XML 可抽取字段**（XPath）：
- 助记符 `docvars/docvar[@key="mnemonic"]/@value`
- 分类 `docvars/docvar[@key="instr-class"]/@value`（general/advsimd/sve/mortlach2…）
- 英文标题 `heading`，简述 `desc/brief/para`
- 汇编模板 `classes/iclass/encoding/asmtemplate`（拼接 `<text>`+`<a>` 内文还原，如 `ADD <Wd|WSP>, <Wn|WSP>, #<imm>{, <shift>}`）
- 关联特性 `classes/iclass/arch_variants/arch_variant/@feature`（如 `FEAT_SVE || FEAT_SME`，抽其中的 `FEAT_*` 词元）

顶层分类直接由 4 个索引文件决定，每个索引恰好一个 `<iforms>` 组，干净对应 Base / SIMD&FP / SVE / SME。

---

## 3. 关键设计决策

| 决策点 | 选择 | 理由 |
| --- | --- | --- |
| 中文介绍来源 | Features 逐条**详译**；instructions 仅译**一行 brief** | 平衡质量与成本：特性 346 条值得详译；指令 2258 条一行简介即够速查 |
| 指令文件组织 | 按 4 分类**拆多文件** + 总览索引（features 单文件） | 单文件塞 2258 条会 >1MB、查阅加载慢；拆分后按需读取 |
| Encoding 列 | **仅汇编模板** `asmtemplate` | 用户取舍：紧凑可读，不渲染 bit 位域图 |
| 指令集范围 | **仅 A64** | 贴合 ARM64 编译器优化场景；AArch32 关系不大 |
| 翻译存储 | 独立 `.py` 数据模块（`feat_desc.py`/`instr_desc.py`） | 与既有 `feat_meta.py` 一致；ARM 升级时只补译增量、翻译不丢失、可维护 |
| 汇编模板上限 | `cap=16`（实测最大 15，**零截断**） | 早期 cap=6 截断了 CAS(8编码) 等，破坏自包含；测得最大 15 后调到 16 保证全量内联 |
| 自包含 | skill 内**零本地路径依赖**，来源描述用下载地址 | skill 可独立分发/版本化，不依赖生成它的仓库 |

---

## 4. 架构

三层「可编辑数据 + 生成脚本 + 只读产物」，产物复制进 skill：

```
生成仓库（维护侧，不随 skill 分发）
  feat_meta.py        人工：META[name]=(中文翻译, 功能域) + GROUP_ORDER(11 域)
  feat_desc.py        生成：DESC[name]=中文介绍（346）
  gen_feat_table.py   读 Features.json → Features.md（+ 兼容产物 FEAT_列表.md）
  instr_meta.py       人工：分类配置 CATEGORY_LABELS / INDEX_TO_CATEGORY
  instr_desc.py       生成：INSTR_DESC[iform_id]=中文一行简介（2258）
  gen_instr_table.py  解析 A64 索引+单指令 XML → instructions/{base,simd-fp,sve,sme}.md + 00-index.md
  prep_translate.py / merge_translate.py   翻译流水线的切批与汇总
        │ 复制 skill_build/reference/ → skill/references/
        ▼
skill：~/.claude/skills/arm64-arch-reference/
  SKILL.md                 触发描述 + 导航 + 检索指引 + 下载地址
  references/
    Features.md            346 特性 / 11 域 / 7 列
    overview.md                总体介绍 + 检索建议 + 下载地址
    instructions/00-index.md + base.md/simd-fp.md/sve.md/sme.md   2258 指令 / 5 列

  （evals 与本设计文档已移出 skill，分别置于源码仓库
   tests/arm64-arch-reference/evals/（评测用例与结果）
   docs/arm64-arch-reference/（本 DESIGN.md + scripts/ 归档脚本））
```

> 上述全部脚本与数据模块的**归档副本**存于 `scripts/`（见其 `README.md`），用于记录与复现；
> 它们是副本不能就地运行，实际再生成需放回带官方数据的数据集仓库。

### 数据规模
- 特性：**346** 个 `FEAT_*`，11 功能域。
- 指令：**2258** 条 A64 —— base 507 / simd-fp 463 / sve 938 / sme 350。

### 11 个功能域（GROUP_ORDER）
内存管理与地址转换 / 内存模型与原子操作 / 浮点·SIMD·数据类型 / SVE / SME /
安全与内存标记 / 虚拟化 / 调试与追踪 / 性能监控与剖析 / RAS / 系统控制·异常·执行状态。

---

## 5. 构建流程

### 5.1 特性表
`gen_feat_table.py` 提取所有 `FEAT_*`，正则解析「引入版本(`from ArmvX.Y`)/执行状态/可选强制」，
套 `feat_meta.META`（翻译+域）与 `feat_desc.DESC`（中文介绍，缺则回退英文 before），按域分组排序，
写 `Features.md`。**严格校验**：META 与 `FEAT_*` 集合必须一一对齐，否则 `[错误]` 退出；DESC 只报覆盖率。

### 5.2 指令表
`gen_instr_table.py` 遍历 4 索引取 (heading, brief, iformfile, id, 分类)，逐个打开单指令 XML
抽取 mnemonic / asmtemplate(去重,cap=16) / `FEAT_*`，套 `instr_desc.INSTR_DESC`（缺则回退英文 brief），
按分类写 5 个 md。纯标准库（`xml.etree`+`glob`+`re`），自动定位 A64 的 `2026-03_rel` 快照。

### 5.3 翻译流水线（生成 feat_desc.py / instr_desc.py）
1. `prep_translate.py`：把待译项切批（feat 40/批=9 批，instr 120/批=19 批），写 `skill_build/desc/in_*.json` + `manifest.json`。
2. **翻译执行**：用 Workflow 起 **28 个 `sonnet` 子 agent**（9 feat + 19 instr），各读 `in_*.json`、
   产出中文写 `out_*.json`。实测消耗约 **702k token**。
3. `merge_translate.py`：汇总 `out_*.json` → 生成 `feat_desc.py` / `instr_desc.py`，报覆盖率。
   **安全护栏**：若无任何 `out_*.json`（中间件已清理）则中止、不以空字典覆盖既有翻译。

**已知坑**：翻译 agent 偶尔在 JSON 字符串里写裸 ASCII 双引号（如 `"公共"`）破坏该批 JSON，
merge 会报"跳过损坏文件"；把裸 `"` 改成中文引号 `“”` 后重 merge 即可（本次曾在 `FEAT_TTCNP` 命中并修复）。

最终覆盖率：**feat DESC 346/346，instr INSTR_DESC 2258/2258**。

---

## 6. Skill 触发设计

`SKILL.md` 的 `description` 是触发主开关，写得"主动"：覆盖 ARM64/AArch64/A64 关键词、`FEAT_*` 例子、
版本/可选强制、汇编模板/编码、门控、以及"做编译器/codegen 优化、即使没明说查手册也应主动查、不要凭记忆作答"。
正文用渐进式披露：参考文件**按需 grep**，不全量载入上下文。

**检索范式**（写入 SKILL.md）：查特性→搜 `Features.md` 特性名；查指令→按功能去对应 `instructions/*.md` 搜助记符；
由特性反查指令→在指令文件搜 `FEAT_xxx`；判断可用性→查到门控特性后回 `Features.md` 看版本/可选强制。

---

## 7. 验证与评测

### 7.1 输出正确性（功能评测）
4 个真实场景查询 × (with-skill / 无 skill 基线) 子代理对跑，断言程序化校验（归一化空白/反斜杠 + `must_not` 捕获错误声明）。

| 配置 | 通过率 | 耗时 | token |
| --- | --- | --- | --- |
| **with skill** | **100%** (14/14) | 49.5s | 20658 |
| 无 skill 基线 | 88% (12/14) | 43.9s | 16419 |
| Δ | **+12pp** | +5.5s | +4238 |

基线的失败/方差来自记忆错误：把 **FEAT_LSE 说成 Armv8.1 强制**（实为 Armv8.0 可选）、
**FEAT_SME2 说成 Armv9.4**（实为 Armv9.2）、给 BF16 编造"Armv8.6 起强制/支持 AArch32"。
skill 用 ~+5.5s/+4k token 换 100% 准确——对速查正是关键价值。

### 7.2 触发精度（直测真实 skill）
用 `claude -p` 直测已安装的真实 skill（比 skill-creator 的 `run_eval` 代理命令更准——
本机装了同名 skill 时 run_eval 会因名字不匹配测不准，曾误报 0%）：

| 查询 | 应触发 | 实测 | 首个工具 |
| --- | --- | --- | --- |
| FEAT_LSE128 版本/可选 | ✓ | 触发 ✓ | `Skill` |
| BFCVT encoding/扩展 | ✓ | 触发 ✓ | `Skill` |
| 用 NEON intrinsics 写 C 代码 | ✗ | 不触发 ✓ | AskUserQuestion |
| RISC-V RVV vs ARM SVE | ✗ | 不触发 ✓ | (直接回答) |

**4/4 正确**：召回（真查询触发并查表）与精度（近似请求不误触发）兼具，描述已良好校准。

---

## 8. 维护：升级 ARM 数据版本

1. 从第 2 节下载地址取新数据，替换仓库 `Features/`、`Instructions/`，并把新 `Features.json` 复制到仓库根。
2. **特性**：`python3 gen_feat_table.py`；若报 META 未覆盖/多余，在 `feat_meta.py` 增删条目后重跑。
3. **指令**：`python3 gen_instr_table.py`，核对指令总数 = 4 索引 iform 数之和。
4. **增量翻译**：`prep_translate.py`（可只切新增项）→ 翻译 Workflow → `merge_translate.py` 重生成 `*_desc.py`，覆盖率达标后重跑 2-3。
5. **更新 skill**：把 `skill_build/reference/` 复制进 `references/`；核对 `SKILL.md`/`overview.md` 的版本号与计数。
6. （可选）复跑 `tests/arm64-arch-reference/evals/` 下评测确认无回归。

---

## 9. 已知限制 / 未来增强
- 指令仅 A64，不含 AArch32（A32/T32）。如需扩展，AArch32 数据结构同构，可复用同一抽取策略。
- 指令"中文简介"为一行（brief 级），非逐条详译；详细语义请回 DDI 0487。
- 引入版本由正则解析官方描述，约 21 个特性官方未注明版本（显示 `—`）。
- Encoding 列只给汇编模板，不含逐 bit 位域图；如需精确编码请查源 XML 的 `regdiagram`。
- 触发自动化：受限于无 API key，未跑 skill-creator 的 `run_loop` 自动描述优化；改用 `claude -p` 直测验证（结论：描述已良好）。
