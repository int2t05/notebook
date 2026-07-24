---
name: mysql-patch-multi-version-adaptation
description: 当用户要求将 MySQL 或 Percona Server 补丁从一个版本移植到另一个版本，并要求实际完成 patch 分析、版本差异比对、代码适配、编译、安装、启动验证、功能验证、patch 生成或提交时使用。适用于多版本 MySQL 内核补丁适配、兼容性修复、MTR 或 sysbench 验证，以及将补丁移植过程标准化为低人工参与流水线。
---

# MySQL 补丁多版本适配

用于 MySQL / Percona Server 补丁跨版本移植。目标不是只做静态分析，而是尽量完成：

- 参考 patch 选择
- patch 设计分析
- 源码差异定位
- 实际移植
- 编译与安装
- 启动与功能验证
- 产出新 patch
- 必要时提交到目标仓库

## 适用场景

- 将 `8.0.x` 的优化补丁移植到另一个 `8.0.y`
- 将 Percona Server patch 适配到官方 MySQL
- 已知 patch 大部分可用，但存在少量 API / ABI / 生命周期差异
- 需要把移植结果固化为可审计 patch，而不是只给口头建议

## 强制工作方式

1. 先读 patch，再读目标版本源码，不要先凭记忆改代码。
2. 必须区分“自动应用的 hunks”和“人工冲突修复”。
3. 优先保留原 patch 语义，不允许通过删除核心逻辑绕过编译。
4. 编译、安装、启动、功能验证尽量全走完；做不到时明确指出阻塞点。
5. 每个阶段都输出结构化进度：
   `[阶段] [分析] [修改] [问题] [解决] [验证]`
6. 在真正移植前，必须先判断“哪个分支上的 patch 最适合作为参考 patch”，不要默认拿最老版本或手边最近的版本直接移植。
7. 适配完成后，必须记录本次微调点、失败点和验证结果，用于后续更新规则库。

## 标准输入

至少确认以下信息：

- 原 patch 路径
- 原始适配版本源码目录
- 目标版本源码目录
- 目标编译命令
- 目标安装目录
- 功能验证方式
  优先级：MTR > SQL 回归 > sysbench > 启动可用性

如果用户没有给全，先从本地仓库和历史命令补齐，不要立刻停下提问。

## 主流程

### 0. 参考 patch 选择

如果用户只说“把某个能力移植到目标版本”，而仓库多个分支都存在相近 patch，必须先做参考 patch 选择。

默认先查看 `boostkit/mysql` 代码仓各分支中的 `boostdb-patches/`，优先从本地对应镜像仓库读取分支和 patch；如果本地镜像缺失，再看用户提供的源码树。

选择规则按优先级从高到低：

1. 功能最接近
2. 版本距离目标版本最近
3. 产品线最接近
4. 验证覆盖最完整
5. 历史通过率最高

具体解释：

- 功能最接近：
  要先确认 patch 真的是同一能力、同一实现路线，而不是同类优化的旧版本原型。
- 版本距离目标版本最近：
  对 `8.0.36` 这种目标版本，通常优先参考 `8.0.43` 一类近版本，而不是 `8.0.25`。
- 产品线最接近：
  官方 MySQL 目标版本，优先参考官方 MySQL 近版本；若官方近版本缺少该 patch，而 Percona 近版本有同实现，再优先参考 Percona 近版本。
- 验证覆盖最完整：
  优先选择自带更多 MTR、sys_vars、debug case、性能或回归验证的 patch。
- 历史通过率最高：
  如果团队已有多次移植记录，优先选择“少改动、高通过率”的参考来源。

对于 plan cache 这类功能，`8.0.36` 目标版本更适合参考 `MySQL-Percona-Server-8.0.43-34` 的 patch，而不是 `MySQL-8.0.25`。原因是：

- `8.0.25` 分支里根本没有同能力 patch
- `8.0.43-34` 与 `8.0.36` 生命周期、optimizer、prepared statement 结构更接近
- `8.0.43-34` patch 自带更完整的测试和修复历史

做完选择后，必须在进度输出里明确说明：

- 候选参考 patch 有哪些
- 为什么排除不合适版本
- 最终采用哪个版本作为主参考
- 是否需要同时参考第二来源做差异补洞

参考规则见：

- `references/reference-patch-selection.md`

辅助脚本见：

- `scripts/select_reference_patch.sh`

### 1. patch 设计分析

先回答四个问题：

- 修改了哪些文件和模块
- 新增了哪些类、结构、函数、系统变量、状态变量、测试
- hook 点在哪些生命周期节点
- patch 的核心语义是什么

如果 patch 很大，先用命令抽取修改面：

- `git apply --stat`
- `git apply --summary`
- `rg`
- `sed -n`

模块归类优先按以下维度整理：

- optimizer / executor / prepare / parser / metadata
- sys_vars / status_vars / PSI / memory key
- mysql-test / MTR / benchmark
- build system

### 2. 版本差异分析

对 patch 修改过的文件逐个比对目标版本：

- 文件是否存在
- 函数签名是否变化
- 类成员是否变化
- 枚举、宏、helper 是否重命名
- 生命周期逻辑是否迁移
- 同名逻辑是否已在旧版本中以别的形式存在

冲突原因必须归类，不要只说“apply 失败”：

- 上下文行漂移
- 接口缺失
- helper 名称变化
- 成员未下沉
- 生命周期清理点不同
- 测试基线不同
- 运行时依赖差异

详细检查清单见：

- `references/checklists.md`

### 3. 低风险自动应用

先做非破坏性检查：

- `git apply --check`

如果大部分 hunk 可用，再在可接受的工作树上做：

- `git apply --reject --whitespace=nowarn`

要求：

- 记录哪些文件自动应用成功
- 列出 `.rej` 文件
- 人工修复前先阅读自动应用后的目标文件，确认是否已有部分逻辑被合入

辅助脚本见：

- `scripts/mysql_patch_adapt_snapshot.sh`

### 4. 人工适配策略

人工修复按以下顺序处理：

1. build / include / forward declaration
2. 类型和成员缺口
3. 生命周期 hook
4. 系统变量、状态变量、PSI 注册
5. 测试和结果文件
6. 编译期 API 差异
7. 运行时依赖问题

常见原则：

- 旧版本无新接口时，找语义等价 helper
- 如果 patch 假设新生命周期存在，要回退到旧版本对应清理路径
- 若目标版本已有相同逻辑的一部分，不重复引入第二套实现
- 测试结果文件要基于目标版本基线做最小调整

### 5. 编译与安装

必须真实执行用户给定编译命令。不要自己换一套构建系统，除非原命令不可用且已证明阻塞。

遇到编译错误时：

- 记录精确报错文件和符号
- 判断是声明缺失、签名变化、命名变化还是运行库差异
- 修复后重新完整编译

### 6. 启动与功能验证

至少验证：

- `mysqld --version`
- 独立 datadir 初始化
- `mysqladmin ping`
- patch 相关系统变量或状态变量存在
- patch 核心 SQL 路径可执行

如果 patch 与 prepared statement / optimizer / range / filesort / tmp table 有关，必须优先设计针对性 SQL。

如果用户给过故障复现命令，例如 sysbench，要尽量复现同路径验证。

### 7. patch 产出

生成的新 patch 要满足：

- 可直接 apply 到目标版本原始源码
- 不包含 build 目录
- 不包含二进制
- 不包含临时文件

优先用：

- `git format-patch`

### 8. 仓库提交

如果用户要求提交到远程仓库：

- 先确认目标分支是否最新
- 避免在脏工作树直接提交
- 优先单独 worktree
- 只提交目标 patch 文件或目标源码变更
- push 前检查 fast-forward 风险

提交前还必须检查“本次改动边界”：

- 明确列出将要提交的文件
- 明确列出刻意不提交的文件
- 如果工作树里混有其他优化、构建脚本调整、日志、临时 patch、验证产物，必须保持未提交状态
- 如需拆分提交，优先用 `git add <file>` 精确暂存；不要把无关改动一起打包进一次提交

提交信息必须专业化，不允许使用临时标题，例如：

- `fix`
- `wip`
- `port patch`
- `update`

默认提交标题格式：

- `[optimization] ...`
- `[bugfix] ...`
- `[compatibility] ...`
- `[refactor] ...`
- `[test] ...`

选择规则：

- 性能优化、SIMD、热点路径提速，优先用 `[optimization]`
- 兼容性适配、版本 API 差异修复，优先用 `[compatibility]`
- 明确修复错误行为、越界、崩溃、回归，优先用 `[bugfix]`
- 纯结构整理且不改语义，优先用 `[refactor]`
- 仅补测试或测试基线，优先用 `[test]`

默认提交正文格式：

- 第一行是专业化标题，直接说明“做了什么 + 作用范围 + 平台/版本限定”
- 空一行后，用 4-8 个 bullet 描述关键改动
- 每个 bullet 用动词开头，描述代码、构建、测试三类变化
- 优先覆盖：
  - 新增/修改的核心实现
  - runtime dispatch 或 capability check
  - 关键接线点
  - 构建系统变更
  - 测试覆盖和验证范围

推荐风格示例：

- `[optimization] Accelerate UTF-8/UTF-8MB4 charset handling on AArch64 with NEON/SVE`
- `[compatibility] Adapt plan cache patch to MySQL 8.0.30 lifecycle and PSI interfaces`
- `[bugfix] Fix odd-length destination handling in utf8mb4 strxfrm path`

推荐正文写法示例：

- `Add AArch64 SIMD implementations for ...`
- `Update strings/CMakeLists.txt to probe ...`
- `Wire optimized paths into ... while preserving generic fallbacks`
- `Extend gunit and mysql-test coverage for ...`

如果用户指定“参考某个 commit 的提交信息风格”，必须先读取该 commit，再复用它的结构和措辞粒度，不要只模仿标题前缀。

如果需要 amend 或重写提交信息，必须保持代码内容边界不变；只修改提交元数据，不顺手混入额外源码调整。

### 9. 持续优化闭环

每次适配结束后，都要沉淀一条案例记录，最少包含：

- 任务编号或主题
- 目标版本
- 参考 patch 来源分支
- 实际主参考 patch
- 是否存在第二参考 patch
- 自动 apply 成功率
- 人工修复点
- 编译是否通过
- 启动是否通过
- 功能验证是否通过
- sysbench / MTR / SQL 验证覆盖情况
- 最终结论
- 本次新增规则

建议记录到 skill 目录下的案例数据文件：

- `references/adaptation-cases.jsonl`

新增案例时，优先追加，不要覆盖历史。

每完成一批适配后，要从案例中反推规则库更新：

1. 哪类 patch 最适合从哪个版本起步
2. 哪些 API 差异反复出现
3. 哪些验证动作应默认启用
4. 哪些补丁族存在固定冲突点
5. 哪些提示词约束能减少返工

如果同类任务连续出现失败或高人工修复占比，必须更新：

- `references/reference-patch-selection.md`
- `references/checklists.md`
- `references/case-*.md`

闭环说明见：

- `references/continuous-improvement.md`

记录脚本见：

- `scripts/record_adaptation_case.py`

## 输出模板

默认用下面结构持续汇报：

```text
[阶段]
正在做什么

[分析]
发现了什么

[修改]
改了哪些文件

[问题]
遇到了什么错误

[解决]
如何修复

[验证]
验证结果
```

最终总结至少覆盖：

- patch 设计概述
- 主要冲突点与解决方式
- 编译问题与修复
- 启动与功能验证结果
- 新 patch 路径
- 是否已提交远程

## 分级提示词

调用本 skill 时，优先采用三层提示结构：

1. 基础指令：任务目标、源 patch、目标版本、必须真实执行
2. 补充约束：保留语义、不得绕过、必须编译启动验证
3. 自检清单：冲突点、编译、运行、功能、patch 产出、提交

模板见：

- `references/prompt-template.md`
- `references/reference-patch-selection.md`

## 案例经验

本 skill 内置了一份实际案例：

- `references/case-plan-cache-8.0.43-to-8.0.36.md`

当用户做的是 MySQL 8.0.x 之间的 patch 迁移，尤其是 optimizer / prepared statement / plan cache 相关 patch，优先参考这份案例。

## 完成定义

只有同时满足以下条件，才能称为“移植完成”：

- patch 已适配到目标源码
- 编译成功
- 安装成功
- `mysqld` 成功启动
- 至少一条核心功能路径验证成功
- 已输出或生成目标 patch

如果其中任意一项未完成，结论必须写成“部分完成”，并明确剩余阻塞。
