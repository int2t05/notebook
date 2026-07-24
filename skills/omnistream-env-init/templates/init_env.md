# OmniStream 开发环境初始化文档

> 生成时间:________  |  生成者:________  |  路径真源:AGENTS.md(本文件值取自该文件)

> 所有 `<placeholder>` 取自 `AGENTS.md` 对应字段。AGENTS.md 是唯一真源,本文件为人类可读快照。

## 1. 本地环境(Windows)

| 项 | 路径/值 |
|---|---|
| 主工作目录 | `<local_work>`/OmniStream |
| 三仓库 | `<local_work>`/{OmniStream, OmniAdaptor, OmniOperator} |
| 外部源码 | `<local_work>`/{flink-1.16.3, calcite-1.26.0, velox, Gluten} |
| flink-test | `<local_flink_test>`/{test, report} |
| Python | `py` launcher |
| workspace | OmniStream/.vscode/OmniStream.code-workspace |

### git remote

| 仓库 | origin(fork) | upstream |
|---|---|---|
| OmniStream | `https://<git_host>/<fork_owner>/OmniStream.git` | `https://<git_host>/<official_org>/OmniStream.git` |
| OmniAdaptor | `https://<git_host>/<fork_owner>/OmniAdaptor.git` | `https://<git_host>/<official_org>/OmniAdaptor.git` |
| OmniOperator | `https://<git_host>/<fork_owner>/OmniOperator.git` | `https://<git_host>/<official_org>/OmniOperator.git` |
| 开发分支 | `<branch>`(三仓库统一) | |

### SFTP 配置(.vscode/sftp.json,host=`<host>`)

| 本地仓库 | remotePath | 说明 |
|---|---|---|
| OmniStream | `<remote_code_root>/OmniStream` | C++ 源码同步 |
| OmniAdaptor | `<remote_code_root>/OmniAdaptor` | Java 源码同步 |
| OmniOperator | `<remote_code_root>/OmniOperatorJIT` | **远端带 JIT 后缀** |
| install_script | `<remote_code_root>/install_script` | 安装脚本同步 |

## 2. 服务器环境(鲲鹏)

| 项 | 值 |
|---|---|
| 主机/用户/端口 | `<host>` / `<user>` / `<port>`(SSH 密钥免密) |
| 远端命令前缀 | `ssh <user>@<host> 'source /etc/profile && <cmd>'` |
| 远端代码根 | `<remote_code_root>` |
| 三仓库 | `<remote_code_root>`/{OmniStream, OmniAdaptor, OmniOperatorJIT} |
| Flink | `<flink_home>` |
| 部署目录 | `<deploy_dir>` |
| install 脚本 | `<install_script_dir>/` |
| JAVA_HOME | `<java_home>` |
| LLVM | `<llvm>` |
| OMNI_HOME | `<omni_home>`(**未持久化**,session export) |
| 集群启停 | start-cluster.sh / stop-cluster.sh(`<flink_home>/bin/`) |

## 3. native 使能验证结果

- [ ] `make tnel` 编译 libtnel.so(exit 0,不编 tneltest 不 install)
- [ ] `operator_incr` + `adaptor_incr` 编译 omni so + jar
- [ ] `deploy` 重建 `<deploy_dir>`(so + jar + config.sh.bak 备份)
- [ ] config.sh patch(flink-tnel jar 前置)+ parent-first
- [ ] cluster restart(`export WRITE_TO_FILE=TRUE` 在 start-cluster 前)
- [ ] `test_native`: `welcome to native` 0→1 + `/tmp/flink_output.txt` 8 行

验证时间:________  结果:________

## 4. 注意事项

- **AGENTS.md 是唯一真源**:所有 skill 从 AGENTS.md 读路径,不在 skill 内硬编码。
- **两套克隆源**:远端首建用 install_step.sh(镜像),本地开发用 fork fork + SFTP 覆盖(日常以本地源为准)。
- **OMNI_HOME/LLVM_DIR 未持久化**:/etc/profile 无,手动 cmake 需 session `export OMNI_HOME=<omni_home>`。
- **OmniOperator 远端名 `OmniOperatorJIT`**(带 JIT 后缀,SFTP 已映射,文档引用易混)。
- **flink-test 不走 SFTP**(run_local.sh 手动 scp 用例到 /tmp)。
- **config.sh patch + parent-first 是 native 使能核心**(patch 前必备份 config.sh.bak)。
- **构建文件不进 commit**(`CMakeLists.txt`/`build.sh`/`build_scripts`/`env_check.sh`/`scripts/*.sh`/`.gitignore` 本地未提交 SFTP 同步)。
- **新需求分支**:从 `upstream/<branch>` 切出,不带基础分支前缀,切出后 `git push -u origin <branch>` 远程化。

## 5. 常用 skill(开发流程)

| skill | 用途 |
|---|---|
| omnistream-env-init(本 skill) | 环境搭建(生成 AGENTS.md) |
| omnistream-build-deploy | 三仓库编译 + 部署 + native 使能 |
| omnistream-expression-test | 表达式 native vs vanilla 黄金对比 + 报告 |
| omnistream-expression-dev-test | 表达式开发+测试全周期编排 |
| omnioperator-expression-dev | OmniOperator 实现新向量化函数 |
| omniadaptor-vectorized-expression | OmniAdaptor 适配表达式走 native |
| flink-native-expression-analysis | Flink 表达式 native 三层支持分析 |
