---
name: omnistream-env-init
description: OmniStream 开发环境端到端 bootstrap(本地 Windows + 鲲鹏服务器)。交互问参数生成 AGENTS.md 单一真源,自动拉全源(3 omni fork 官方 + 4 调研源)→ 配 SFTP/flink-test → 测服务器连接 → 应用 ccache 加速 + 编译三仓库 → 部署 + native 使能测试。触发:新环境搭建/初始化开发环境/环境清单/路径确认/fork 配置/一键 bootstrap。
---
# OmniStream 开发环境初始化 skill(端到端 bootstrap)

从任意 cwd 一键搭建:交互问参数 → 生成 `AGENTS.md` → 拉全源(3 omni fork 官方 + 4 调研源)→ 配 SFTP/flink-test → 测服务器连接 → 应用 ccache 加速 + 编译三仓库 → 部署 + native 使能测试。**不硬编码任何用户路径/身份**。

> 真源 = `AGENTS.md`(本 skill 写到 OmniStream 仓库根 `omni_repo_root`,本地 gitignore)。其他 skill 读它,不硬编码。`omni_repo_root` = 本 skill 所在目录上溯 3 级(`omnistream-env-init/` → `skills/` → `.claude/` → 仓库根)。

## 步骤 0:交互式收集参数 → 写 AGENTS.md

用 AskUserQuestion 逐项收集(项目约定默认值已给,fork_owner/host/user/local_work **必问**):

| 参数 | 默认 | 说明 |
|---|---|---|
| git_host | gitcode.com | 代码托管平台 |
| fork_owner | (必问) | 你 fork 后的账号,不假设任何特定账号 |
| official_org | openeuler | 官方 upstream 组织 |
| branch | 2026_930_poc | 三仓库统一开发分支 |
| host / user / port | (必问) | 鲲鹏服务器 SSH |
| local_work | (必问,默认=`omni_repo_root` 父目录) | 本地工作根目录 |
| remote_code_root | /opt/buildtools | install_step.sh 约定,可改 |
| flink_home | /opt/flink | |
| omni_home | `<remote_code_root>`/omni_home/omni-operator | |
| deploy_dir | /home/Dependency_library | |
| install_script_dir | `<remote_code_root>`/install_script/OmniStream | |

收集完写 `AGENTS.md` 到 `omni_repo_root/AGENTS.md`,加 `omni_repo_root/.git/info/exclude` 忽略。结构:§核心原则[手维护,init 不覆盖] / §1 Git 身份 / §2 服务器 / §3 本地 / §4 远端 / §5 Shell 变量块 / §6 注意[手维护]。**重跑 init 只刷新 §1-§5,保留 §核心原则 与 §6**。

## 步骤 1:拉全源(idempotent,已存在则 skip)

### 1a. 3 omni 仓库(fork 官方,**不 clone 别人 fork**)
- **OmniStream**:已存在(skill 在此),仅 ensure `upstream` remote(`git remote add upstream https://<git_host>/<official_org>/OmniStream.git` + fetch,若无)。
- **OmniAdaptor / OmniOperator**:若 `<local_work>/<repo>` 不存在 → 用户先在 `git_host` 网页把 `official_org/<repo>` fork 到 `fork_owner` 账号 → `git clone https://<git_host>/<fork_owner>/<repo>.git -b <branch>` → `git -C <repo> remote add upstream https://<git_host>/<official_org>/<repo>.git`;若存在 → 仅 ensure upstream。

### 1b. 4 调研源(shallow,调研优先本地)
```bash
cd <local_work>
[ -d flink-1.16.3 ]   || git clone --depth 1 --branch release-1.16.3 https://github.com/apache/flink.git flink-1.16.3
[ -d calcite-1.26.0 ] || git clone --depth 1 --branch calcite-1.26.0 https://github.com/apache/calcite.git calcite-1.26.0
[ -d velox ]          || git clone --depth 1 https://github.com/facebookincubator/velox.git velox
[ -d Gluten ]         || git clone --depth 1 https://github.com/apache/incubator-gluten.git Gluten
```
> Flink 已 vendor Calcite 在 `flink-1.16.3/.../org/apache/calcite/`;未 vendor 的查 `calcite-1.26.0/`。Velox/Gluten 为 Spark 生态向量化基准。

## 步骤 2:本地配置
- **SFTP**:每仓库 `.vscode/sftp.json`(host/user/port 取自 AGENTS.md,uploadOnSave true,watcher autoUpload/autoDelete true)。remotePath:OmniStream→`<remote_code_root>/OmniStream`、OmniAdaptor→`<remote_code_root>/OmniAdaptor`、OmniOperator→`<remote_code_root>/OmniOperatorJIT`(**远端带 JIT 后缀**)、install_script→`<remote_code_root>/install_script`。ignore:`**/.git/**`、`**/build/**`、`**/*.so`、`**/.claude/**`、`**/target/**`、`**/flink-test/**` 等。
- **flink-test**:`mkdir -p <local_flink_test>/{test,report}`;`run_local.sh` 在 `omnistream-expression-test/scripts/`;enable_test 用例在 `omnistream-expression-test/templates/`。
- **workspace**:用 `omni_repo_root/.vscode/OmniStream.code-workspace`(多根)。

## 步骤 3:测服务器连接(必须先过,失败则停)
```bash
ssh <user>@<host> 'source /etc/profile && echo CONNECT_OK && ls <install_script_dir>/install_step.sh && which java cmake'
```
失败→提示用户配 SSH 免密(`~/.ssh/id_ed25519`)+ 服务器装好环境(install_step.sh),**不继续后续步骤**。

## 步骤 4:服务器 bootstrap(首建)
- 若 `<remote_code_root>/OmniStream` 不存在(服务器未建):`ssh <user>@<host> 'source /etc/profile && cd <install_script_dir> && bash install_step.sh'`(主序 base→patch→jdk→boostkit_ksl→...→install_omni_operator_vec→install_omni_adaptor→install_omni_stream)。
- **Flink 配置(native 使能核心)**:装 Flink 1.16.3→`<flink_home>` 软链 + `rest.bind-address: 0.0.0.0` + `FLINK_HOME` 写 /etc/profile;**config.sh patch**(flink-tnel jar 前置 classpath,patch 前备份 `config.sh.bak`,见 build-deploy deploy.md 动作3);**parent-first**(`conf_parent_first` 任务);LD_LIBRARY_PATH(/etc/profile 含 `<deploy_dir>` + `<omni_home>/lib`)。

## 步骤 5:加速构建(ccache 优化 + 编译三仓库)

### 5a. 应用 CMakeLists ccache 优化(本地未提交 SFTP 同步;upstream 原版也能编,此为加速)
- **OmniStream `omni_repo_root/cpp/CMakeLists.txt`**:ccache launcher(`find_program(CCACHE_PROGRAM ccache)` + `set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})`)+ install bulk(1 条 `install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/ DESTINATION include FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp" PATTERN "build" EXCLUDE)` 替代 `install_headers()`)+ 移除 `install_headers()`。
- **OmniOperator `<local_work>/OmniOperator/CMakeLists.txt`**:ccache 改 `CMAKE_CXX_COMPILER_LAUNCHER`(原 `RULE_LAUNCH_*` 对 Ninja 无效)+ `option(EXCLUDE_TEST "Exclude unit tests" OFF)`。
> 应用后 `HOME=<remote_code_root>` 共享 `<remote_code_root>/.ccache`(warm rebuild 秒级)。**改完提醒用户在 IDE 保存(Ctrl+S)触发 SFTP 同步到远端**。

### 5b. 编译三仓库(委派 `omnistream-build-deploy`;agent 从 AGENTS.md §5 export $VARS 后 ssh 跑 task)
```
omnistream_incr(make tnel) → operator_incr → adaptor_incr
```
验证:libtnel.so + boostkit-omniop-*.so + flink-tnel.jar + omni-table-planer.jar 产物 mtime 更新(用 build-deploy `status` 任务)。

## 步骤 6:部署 + native 使能测试
```
deploy → conf_parent_first → cluster_stop → cluster_start(WRITE_TO_FILE=TRUE) → test_native
```
通过判据:`welcome to native` 0→1 + `/tmp/flink_output.txt` 8 行(详见 build-deploy test.md)。
完整 native vs vanilla 对比 + 本地富报告:`bash <omni_repo_root>/.claude/skills/omnistream-expression-test/scripts/run_local.sh enable_test`。

## 产物:init_env.md
按 `templates/init_env.md` 模板填(值取自 AGENTS.md),落 `<local_flink_test>/init_env.md` 或 `omni_repo_root/`。记录环境清单(本地+服务器路径)+ remote/SFTP + native 验证结果 + 注意。新成员接手时 AGENTS.md + 此文档即环境入口。

## 关键注意
- **AGENTS.md 唯一真源**:所有 skill 读路径从此,不硬编码用户身份/路径。
- **fork 官方不 clone 别人 fork**:fork `official_org/<repo>` 到 `fork_owner` 自己账号。
- **AGENTS.md 本地忽略**(`.git/info/exclude`),不进 commit(per-user)。
- **idempotent**:重跑 init skip 已存在的仓库/源,只刷新 AGENTS.md §1-§5 + 补缺失配置。
- **构建文件不进 commit**:CMakeLists 优化本地未提交,SFTP 同步(§6)。
