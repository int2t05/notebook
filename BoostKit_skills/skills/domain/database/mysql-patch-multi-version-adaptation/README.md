# mysql-patch-multi-version-adaptation

用于 MySQL / Percona Server 补丁跨版本移植的 Codex skill。它面向“真实完成适配”的场景，不止做静态分析，还要求尽可能把补丁移植、编译、安装、启动、验证和 patch 产出整条链路走完。

## 适用场景

- 将一个 `8.0.x` 版本上的 patch 移植到另一个 `8.0.y`
- 将 Percona Server patch 适配到官方 MySQL
- 处理 MySQL 内核 patch 的 API / ABI / 生命周期差异
- 需要把移植结果沉淀为可审计 patch、案例记录和规则库，而不是只给口头建议

## 核心目标

- 在真正改代码前先选择最合适的参考 patch
- 保留原 patch 语义，不靠删逻辑规避编译问题
- 尽量完成编译、安装、启动和功能验证
- 产出可直接复用的新 patch
- 把本次适配经验追加回案例库，形成闭环

## 仓库结构

```text
.
├── README.md
├── SKILL.md
├── references/
│   ├── adaptation-cases.jsonl
│   ├── case-plan-cache-8.0.43-to-8.0.36.md
│   ├── checklists.md
│   ├── continuous-improvement.md
│   ├── prompt-template.md
│   └── reference-patch-selection.md
└── scripts/
    ├── mysql_patch_adapt_snapshot.sh
    ├── record_adaptation_case.py
    └── select_reference_patch.sh
```

## 使用方式

这个仓库本质上是一个 Codex skill。触发条件：

- 用户明确提到 `mysql-patch-multi-version-adaptation`
- 任务本身就是 MySQL / Percona Server 补丁跨版本移植，并要求实际落地

执行入口是 [SKILL.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/SKILL.md)，其中定义了标准流程、强制约束、输出模板和完成标准。

## 推荐提示词

这个 skill 已经在 [SKILL.md](/home/l30039266/.codex/skills/mysql-patch-multi-version-adaptation/SKILL.md) 和 [references/prompt-template.md](/home/l30039266/.codex/skills/mysql-patch-multi-version-adaptation/references/prompt-template.md) 里定义了通用约束。实际使用时，提示词优先补充“本次任务输入”和“本次特有要求”，不必重复整份规则。

以 plan cache 为例，可以直接使用下面这段：

```text
请使用 mysql-patch-multi-version-adaptation skill，处理一个 plan cache patch 的跨版本移植任务。

输入：
- 原 patch 路径：<参考仓库中的 patch 绝对路径>
- 源版本源码目录：<源版本源码绝对路径，例如 /path/to/percona-server-8.0.43-34>
- 目标版本源码目录：<目标版本源码绝对路径，例如 /path/to/mysql-8.0.36>
- 编译命令：
  mkdir -p <target_repo>/build
  cd <target_repo>/build

  CC=<gcc_path>/gcc \
  CXX=<gcc_path>/g++ \
  cmake .. \
    -DBUILD_CONFIG=mysql_release \
    -DWITH_COREDUMPER=OFF \
    -DCMAKE_INSTALL_PREFIX=<install_dir> \
    -DWITH_BOOST=<boost_dir> \
    -DENABLE_DOWNLOADS=0 \
    -DWITH_ROCKSDB=0

  export LD_LIBRARY_PATH=<gcc_lib64>:$LD_LIBRARY_PATH

  make -sj
  make -sj install
- 安装目录：<install_dir>
- 功能验证方式：
  - 验证 `mysqld --version`
  - 使用独立 datadir 初始化并启动 `mysqld`
  - 验证 `mysqladmin ping`
  - 验证 `SHOW VARIABLES LIKE 'plan_cache%'`
  - 验证 `SHOW STATUS LIKE 'plan_cache%'`
  - 验证 prepared statement 相关 SQL 路径
  - 如具备条件，补充 sysbench 验证，重点关注 `order_ranges=1`、`distinct_ranges=1` 一类场景
- 参考仓库或候选 patch：
  - 本地优先检查 `<reference_repo>` 中各分支的 `boostdb-patches/`
  - 如本地信息不足，再参考远程仓库：https://gitcode.com/boostkit/mysql

补充要求：
- 优先从与目标版本更接近、且已包含 plan cache 能力的候选 patch 中选择主参考
- 除功能正确性验证外，如条件允许，请对比优化前后版本的 sysbench 只读、读写、只写性能差异
- 最终请输出新 patch 路径、主要冲突点、编译结果、启动结果和功能验证结果
```

## 标准工作流

1. 先选参考 patch，而不是默认拿手边版本直接移植
2. 分析 patch 设计：修改文件、模块、hook 点、系统变量、测试
3. 对目标版本做逐文件差异分析，定位接口和生命周期差异
4. 先执行 `git apply --check`，再区分自动应用与人工修复
5. 按 build、声明、成员、生命周期、PSI / sysvar、测试的顺序修复
6. 用用户给定命令真实完成编译、安装、启动和功能验证
7. 生成新 patch，并按需提交
8. 把结果追加到案例库，更新规则文档

## 关键约束

- 先读 patch，再读目标源码，不凭记忆改代码
- 必须区分自动应用成功的 hunk 和人工冲突修复
- 不允许通过删除核心逻辑绕过编译
- 做不到完整验证时，要明确写出阻塞点
- 进度输出统一采用 `[阶段] [分析] [修改] [问题] [解决] [验证]`

## 参考资料

- [references/reference-patch-selection.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/references/reference-patch-selection.md)：参考 patch 选择规则和打分维度
- [references/checklists.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/references/checklists.md)：patch 分析、差异检查、编译和验证清单
- [references/prompt-template.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/references/prompt-template.md)：推荐提示词模板
- [references/continuous-improvement.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/references/continuous-improvement.md)：案例沉淀和规则回写要求
- [references/case-plan-cache-8.0.43-to-8.0.36.md](/home/xxxxxxx/.codex/skills/mysql-patch-multi-version-adaptation/references/case-plan-cache-8.0.43-to-8.0.36.md)：plan cache 跨版本移植案例

## 辅助脚本

### `scripts/select_reference_patch.sh`

用于在候选仓库里快速列出远程分支中的相关 patch，辅助做主参考 / 辅助参考选择。

```bash
scripts/select_reference_patch.sh <repo_dir> <keyword> [branch-pattern]
```

示例：

```bash
scripts/select_reference_patch.sh ~/boostkit/mysql plan-cache 'origin/'
```

### `scripts/mysql_patch_adapt_snapshot.sh`

用于在真实移植前做一次快照式检查，输出工作树状态、patch 改动概览和 `git apply --check` 结果。

```bash
scripts/mysql_patch_adapt_snapshot.sh <repo_dir> <patch_file>
```

### `scripts/record_adaptation_case.py`

用于把一次适配结果追加到 JSONL 案例库。脚本会校验必填字段：

- `date`
- `topic`
- `target_version`
- `selected_reference_branch`
- `compile_pass`
- `startup_pass`
- `functional_pass`

```bash
scripts/record_adaptation_case.py <json_file> <jsonl_output>
```

## 输入要求

理想输入至少包括：

- 原 patch 路径
- 原始适配版本源码目录
- 目标版本源码目录
- 编译命令
- 安装目录
- 功能验证方式

若用户没有一次性提供完整信息，约定是先从本地仓库、已有目录和历史命令中补齐，再继续推进。

## 完成标准

只有同时满足以下条件，才能称为“移植完成”：

- patch 已适配到目标源码
- 编译成功
- 安装成功
- `mysqld` 成功启动
- 至少一条核心功能路径验证成功
- 已输出或生成目标 patch

任意一项未完成，都应标记为“部分完成”，并明确剩余阻塞。
