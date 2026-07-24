# 部署流程(deploy)

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时从 AGENTS.md 替换。

把编译产物部署到 Flink,使 native 路径生效。4 个动作,缺一不可。

## 动作1:重建 `<deploy_dir>/`

集中部署目录,`config.sh` classpath 与 `LD_LIBRARY_PATH` 都指向它。任务 `deploy` 逐项 `cp -f`:

| 文件 | 源路径 |
|---|---|
| `libtnel.so` | `<remote_omnistream>/cpp/build/jni/libtnel.so` |
| `libboostkit-omniop-{codegen,operator,vector,reader}-2.2.0-aarch64.so` | `<omni_home>/lib/` |
| `libboundscheck.so` | `<remote_code_root>/libboundscheck/lib/` |
| `libLLVM-15.so` | `/usr/local/lib/` |
| `libxxhash.so.0` | `/usr/local/lib64/` |
| `librdkafka.so.1`、`librdkafka++.so.1` | `/usr/local/lib/` |
| `librocksdb.so.8` | `/usr/lib64/` |
| `libjemalloc.so.2` | `/usr/local/lib/` |
| `libsnappy.so.1`、`libre2.so.11` | `/usr/local/lib64/` |
| `flink-tnel-0.1-SNAPSHOT.jar` | `<remote_omniadaptor>/omnistream/omniop-flink-extension/java/target/` |
| `omni-table-planer-0.1-SNAPSHOT.jar` | `<remote_omniadaptor>/omnistream/omniop-flink-extension/omni-table-planner/target/` |

> 此目录被误删是 native 失效最常见原因。重建后必须重启集群(TM 进程启动时读 classpath/LD_LIBRARY_PATH)。

## 动作2:`LD_LIBRARY_PATH`

`/etc/profile` 已含 `export LD_LIBRARY_PATH=<deploy_dir>:$LD_LIBRARY_PATH`(以及 `omni_home/omni-operator/lib`、`/usr/local/lib` 等)。`source /etc/profile` 生效。TM 进程靠此找 `libtnel.so`(`System.loadLibrary("tnel")`)。

验证:`ssh <user>@<host> 'source /etc/profile && echo $LD_LIBRARY_PATH | tr ":" "\n" | grep Dependency'`

## 动作3:`config.sh` classpath 前置(native 使能核心,patch 前必备份)

`<flink_home>/bin/config.sh` 的 `constructFlinkClassPath` 函数末尾把 `flink-tnel.jar` 前置到 classpath 最前(类加载优先级,实现 classpath 覆盖 Flink 同名类)。

**首次 patch 前备份**(供 expression-test vanilla 切换恢复;`task_deploy` 末尾已自动 `cp -n config.sh config.sh.bak`):
```bash
ssh <user>@<host> 'cp -n <flink_home>/bin/config.sh <flink_home>/bin/config.sh.bak'
```

手动改 config.sh 的 `constructFlinkClassPath` 末尾(注释原 echo + 插入 PATCH):
```bash
# echo "$FLINK_CLASSPATH""$FLINK_DIST"        # 原行注释掉
PATCH="<deploy_dir>/flink-tnel-0.1-SNAPSHOT.jar"
echo "$PATCH":"$FLINK_CLASSPATH""$FLINK_DIST"
```
(远端 `vi <flink_home>/bin/config.sh` 改;或本地 SFTP 改后同步。sed 一键版引号较繁,建议手动)

验证:`ssh <user>@<host> 'grep -n "Dependency_library\|FLINK_CLASSPATH" <flink_home>/bin/config.sh | tail'`

## 动作4:`flink-conf.yaml` 加 `parent-first`

`classloader.resolve-order: parent-first`。Flink 默认 `child-first` 会先加载用户 jar 里的类——但 classpath 覆盖需要 `parent-first` 让前置的 flink-tnel.jar 优先。任务 `conf_parent_first` 幂等追加。

验证:`ssh <user>@<host> 'grep "^classloader.resolve-order" <flink_home>/conf/flink-conf.yaml'`

## native 加载机制(原理)

覆盖的 `org/apache/flink/runtime/taskexecutor/TaskManagerRunner.java:499` 在 TM 启动时调 `TNELLibrary.loadLibrary(args)`([A] `com/huawei/omniruntime/flink/TNELLibrary.java`):

1. 读配置 `omni.taskmanager.binaryfiles`(逗号分隔的绝对路径 so 列表)→ 逐个 `System.load`(未配或非绝对路径则跳过,log WARN)
2. `System.loadLibrary("tnel")` —— 从 `LD_LIBRARY_PATH` 找 `libtnel.so`
3. native `initialize()` —— JNI 初始化

使能标志:
- TM 启动 log `TNELLibrary - Loading Task Native Execution Library`(库加载成功)
- 提交 native 作业后 log `welcome to native`(`OmniTask.cpp:250/315`,native Task 实际运行)

## table-planner jar 加载确认

`omni-table-planer-0.1-SNAPSHOT.jar`(ExecNode 注入 native JSON 的关键)经 `PlannerModule` 加载到独立 classpath。验证是否生效:提交 SQL 后查算子描述是否含 `originDescription`(native 注入标志)。**若无**,说明 PlannerModule 未加载该 jar,需查 `OmniAdaptor/.../omni-table-planner/src/main/java/org/apache/flink/table/planner/loader/PlannerModule.java` 的 jar 定位逻辑并部署。

## 部署后一键验证

任务 `status` 查:libtnel/so/jar mtime + `<deploy_dir>/` 内容 + 集群进程 + parent-first 状态。

## 部署完整序列(改动后典型流程)
```
omnistream_incr(或对应仓库编译) → deploy → conf_parent_first → cluster_stop → cluster_start → test_native
```
