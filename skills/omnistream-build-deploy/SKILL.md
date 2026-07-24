---
name: "omnistream-build-deploy"
description: "OmniStream/OmniAdaptor/OmniOperator 三仓库在鲲鹏远端服务器的增量编译、部署到 Flink、native 使能测试。触发场景:OmniStream 编译/增量编译/远程编译/全量重编,部署到 Flink/native 使能/重建 Dependency_library/parent-first,跑通 native 测试/welcome to native/enable_test。本地 Windows 无法编译 C++,所有 C++ 编译在远端 aarch64 服务器进行。"
---

# OmniStream 三仓库编译·部署·测试 skill

本 skill 覆盖 **OmniStream / OmniAdaptor / OmniOperator** 三仓库在鲲鹏远端服务器上的**增量编译 → 部署到 Flink → native 使能测试**全流程。本地(Windows)仅能改 Java/Python/文档,C++ 编译必须在远端 aarch64 服务器进行。

> 三仓库边界:流式算子/状态/调度 → OmniStream;向量化内核/表达式/codegen/函数库 → OmniOperator;Flink 桥接/算子替换决策 → OmniAdaptor。改了哪个仓库就重编哪个,不必每次全编。

> **skill 边界**:三仓库编译 + 部署 + native 使能。**不做**:本地→远端代码同步(VSCode SFTP 自动)、表达式正确性对比(用 `omnistream-expression-test`;本 skill `test_native` 仅 A 类使能验证)。

## 服务器与路径常量(真源 = AGENTS.md)

> host / user / 所有路径取自 repo 根 `AGENTS.md`(§2 服务器 / §4 远端路径 / §5 Shell 变量块),由 `omnistream-env-init` 生成。本文件用 `<placeholder>` 表示,agent 运行时从 AGENTS.md 取值。关键变量:`$OMNI_CODE_ROOT`、`$OMNISTREAM_DIR`、`$OMNIADAPTOR_DIR`、`$OMNIOPERATOR_DIR`、`$FLINK_HOME`、`$OMNI_HOME`、`$DEPLOY_DIR`、`$INSTALL_SCRIPT_DIR`。

| 项 | AGENTS.md 字段 | 说明 |
|---|---|---|
| host/user/port | host / user / port | SSH 密钥免密 |
| 代码仓 | remote_omnistream/omniadaptor/omnioperator | OmniOperator 远端带 JIT 后缀 |
| OmniStream 产物 | `$OMNISTREAM_DIR`/cpp/build/jni/libtnel.so | deploy 从此拷,不依赖 make install |
| OmniOperator so | `$OMNI_HOME`/lib/libboostkit-omniop-{codegen,operator,vector,reader}-2.2.0-aarch64.so | |
| OmniAdaptor jar | `$OMNIADAPTOR_DIR`/.../java/target/flink-tnel-0.1-SNAPSHOT.jar + omni-table-planner/target/omni-table-planer-0.1-SNAPSHOT.jar | |
| 部署目录 | deploy_dir(`$DEPLOY_DIR`) | so + jar 集中部署,供 Flink 加载 |
| Flink | flink_home(`$FLINK_HOME`) | → flink-1.16.3;conf `$FLINK_HOME/conf/flink-conf.yaml`;脚本 `$FLINK_HOME/bin/{start,stop}-cluster.sh`、`sql-client.sh` |
| JAVA_HOME / LLVM | java_home / llvm | /etc/profile 已含 |
| install 脚本 | install_script_dir(`$INSTALL_SCRIPT_DIR`) | install_omni_*.sh、rebuild_omnistream_vec.sh 等 |
| 测试资产 | 本地 `<local_flink_test>`/test/enable_test/enable_test.{csv,sql}(A 类使能测试)+ test/<expr>/(表达式用例);服务器 `$INSTALL_SCRIPT_DIR`/verify_expr_fixed.csv | |

## 三段流程总览

### 一、编译 → 详见 [build.md](scripts/build.md)

| 仓库 | 增量(推荐日常,无改动秒级) | 全量 |
|---|---|---|
| OmniStream | `export HOME=$OMNI_CODE_ROOT && cd cpp/build && make tnel -j$(nproc)`(只编 libtnel.so,不 install/test) | `rebuild_omnistream_vec.sh Release`(`rm -rf build`) |
| OmniAdaptor | `omni-flink-bundle/` 下 `mvn package -DskipTests`(不带 clean,~2s) | `mvn clean package`(清 target) |
| OmniOperator | `cd build && cmake --build . -j$(nproc) && cmake --install .`(不 clean,~0.4s;需 build 已存在) | `bash build_scripts/build.sh release:java`(`--clean-first`,20-40min) |

> ⚠️ **三仓库都支持增量**;全量仅用于首次/cmake 配置变更/彻底清理。`build.sh` 的 `--clean-first` 与 `mvn clean` 是人为强制全量,日常改码用增量任务(`*_incr`)。OmniStream 另有 `scripts/build_gcc.sh omnistream`(PGO+LTO 生产构建,出包/基准用)。
> OmniOperator 已启用 ccache(`CMAKE_CXX_COMPILER_LAUNCHER`,Make/Ninja 通用,`HOME=$OMNI_CODE_ROOT` 共享 `$OMNI_CODE_ROOT/.ccache`)+ 默认开单测(`EXCLUDE_TEST=OFF`);单测经 `operator_test` 任务。

### 二、部署 → 详见 [deploy.md](scripts/deploy.md)

4 个动作:① 重建 `$DEPLOY_DIR`(拷全 so + flink-tnel.jar + omni-table-planer.jar);② `/etc/profile` 的 `LD_LIBRARY_PATH` 已含该目录,`source` 生效;③ `config.sh` 把 flink-tnel.jar 前置 classpath(已改,验证);④ `flink-conf.yaml` 加 `classloader.resolve-order: parent-first`(classpath 覆盖 Flink 同名类的必要条件)。⚠️ **planner 覆盖 jar(`omni-table-planer.jar`,含 `StreamExecJoin` 等 ExecNode 的 native JSON 注入)必须随 `flink-tnel.jar` 一起部署**;`task_deploy` 已含两者。改 OmniAdaptor 后两 jar 都要重部署,否则算子描述缺 `originDescription` → native 不触发。

native 加载链:覆盖的 `TaskManagerRunner.java:499` → `TNELLibrary.loadLibrary()` → 读 `omni.taskmanager.binaryfiles`(未配则跳过)→ `System.loadLibrary("tnel")` 从 LD_LIBRARY_PATH 找 libtnel.so → native `initialize()`。使能标志 = 提交 native 作业后 `OmniTask.cpp:250/315` 打印 `welcome to native`。

### 三、测试 → 详见 [test.md](scripts/test.md)

A 类固定使能测试 `flink-test/test/enable_test/enable_test.{csv,sql}`(纯投影 `SELECT channel, price`,无函数,规避 `char_length` 式 not supported)。**完整对比 + 本地报告(推荐)**:委派 `omnistream-expression-test` 的 `run_local.sh enable_test` → native vs vanilla 黄金对比 + 富报告 `flink-test/report/enable_test/enable_test.report.md`。**快速 native-only 检查(迭代用,无报告)**:scp csv+sql 到 `/tmp/` → `cluster_start`(带 `WRITE_TO_FILE=TRUE`)→ `test_native` 任务 → 验证 `welcome to native` 计数增加 + `/tmp/flink_output.txt` 输出 8 行。测具体表达式用 `omnistream-expression-test` skill(在 `flink-test/test/<expr>/` 建用例 → `run_local.sh <expr>`)。

## 预定义任务(scripts/config.ini `[exec]` 段)

| 任务 | 说明 |
|---|---|
| `omnistream_incr` | OmniStream 增量 `make tnel -j`(只编 libtnel.so,不 install/test),打印产物 mtime |
| `omnistream_rebuild` | OmniStream 全量(`rebuild_omnistream_vec.sh`),日志 `/tmp/omnistream_build.log` |
| `adaptor_incr` | OmniAdaptor 增量(`mvn package` 不 clean,~2s),打印 jar mtime |
| `adaptor_build` | OmniAdaptor 全量(`mvn clean package`) |
| `operator_incr` | OmniOperator 增量(`cmake --build build` 不 clean,~0.4s;需 build 已存在),打印 so mtime |
| `operator_build` | OmniOperator 全量(`build.sh release:java`,`--clean-first`,20-40min) |
| `operator_test` | OmniOperator 单测:构建 omtest(默认开测试)+ 跑全量 gtest;指定用例 `--gtest_filter='XxxTest.*'` |
| `deploy` | 重建 `$DEPLOY_DIR`(拷全 so + jar) |
| `conf_parent_first` | 幂等追加 `classloader.resolve-order: parent-first` 到 flink-conf |
| `cluster_stop` | 停集群(stop-cluster + pkill 残留) |
| `cluster_start` | 启集群(start-cluster + 进程计数) |
| `test_native` | 提交 `/tmp/enable_test.sql`(A 类纯投影)+ 抓 welcome to native + 读 native 输出(快速 native-only,无服务端报告;完整对比+本地报告用 `omnistream-expression-test` 的 `run_local.sh enable_test`) |
| `status` | 查产物/部署目录/集群进程/parent-first 状态 |

## 执行方式

服务器免密(ssh 取自 AGENTS.md §2)。`scripts/config.ini` 的 `[exec]` 段集中定义各任务命令(`task_<name>=<命令>`,多行用 `\` 续行),命令内用 `$VAR` 引用路径(路径无关)。**执行前 agent 从 AGENTS.md §5 取变量值,先 export 再跑 task**(export 在 `source /etc/profile` 前;自定义变量不被 /etc/profile 覆盖):

```bash
ssh <user>@<host> 'export OMNI_CODE_ROOT=<v> OMNISTREAM_DIR=<v> OMNIADAPTOR_DIR=<v> OMNIOPERATOR_DIR=<v> FLINK_HOME=<v> OMNI_HOME=<v> DEPLOY_DIR=<v> INSTALL_SCRIPT_DIR=<v>; source /etc/profile; <task_命令>'
```

> `<user>@<host>` 与各 `<v>` 取自 AGENTS.md。用单引号包裹整条 ssh(内部双引号/`$()`/管道在单引号下正常传递)。前提:本地代码已由 VSCode SFTP 同步到 `<remote_code_root>`(本 skill 不含同步)。

## 注意事项

- **每条远端命令前 `source /etc/profile`**(加载 JAVA_HOME/LLVM/LD_LIBRARY_PATH/FLINK_HOME)。
- `WRITE_TO_FILE=TRUE` 必须在 `start-cluster.sh` **之前** export(由 TM 进程读取)。
- **绝不自动 git push**;三仓库独立,提交前确认目标仓库与分支。**只提交源码,禁止提交构建相关文件**(CLAUDE.md §6):`CMakeLists.txt`/`build.sh`/`build_scripts`/`env_check.sh`/`scripts/*.sh`/`.gitignore` 保留本地未提交(SFTP 同步远端)。
- native 使能失败常见原因:① `$DEPLOY_DIR` 缺 so/jar;② flink-conf 缺 `parent-first`;③ libtnel.so 不在 LD_LIBRARY_PATH;④ table-planner jar 未注入(算子描述无 `originDescription`)。
- 日常改码用增量任务(`*_incr`);全量(`*_build`/`omnistream_rebuild`)仅首次/清理用。

## 核心踩坑(提炼自记忆)

- **operator_incr 装位 ≠ deploy 读位**:`cmake --install` 装到 `/opt/lib`,deploy 从 `$OMNI_HOME/lib` 拷;中间须跑 `install_omni_operator_vec.sh` 或手动 `cp`,否则 deploy 拷旧 so 致 e2e 加载不到新代码。
- **git restore/checkout 后 SFTP 不自动同步**:外部改动绕过 uploadOnSave,服务器仍旧版;commit 远程 + 切分支触发重传,或提醒用户 IDE 保存(Claude 不手动 scp)。
- **reset --hard 前备份构建文件**:`CMakeLists.txt`/`build.sh`/`pom.xml` 等本地未提交优化会被 reset 丢弃,先 cp 备份事后恢复。
- **reset/切分支后文件集变需重跑 cmake**:CMakeLists 用 `file(GLOB_RECURSE)` 无 `CONFIGURE_DEPENDS`,新增/删除 `.cpp` 不自动进 build,须手动 `cmake ..` 重 GLOB(仅改 `.cpp`/`.h` 不必)。
- **CRLF 假脏识别**:Windows checkout CRLF 致 `git diff` 满屏整文件增删;用 `git diff -w --stat` 验真实改动,纯 CRLF reset 安全。
