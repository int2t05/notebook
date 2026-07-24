# 编译流程(build)

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时从 AGENTS.md 替换。

三仓库编译均在远端 `<host>`(aarch64 鲲鹏)。本地 Windows 不可编译 C++,只能改 Java/Python/文档。

## 编译顺序与依赖

完整首次构建顺序见 `<install_script_dir>/install_step.sh`:基础依赖 → OmniOperator → OmniAdaptor → OmniStream。**OmniOperator 和 OmniStream 须同为 release 或 debug**。日常改码只重编改动的仓库,不必全编。**OmniStream↔OmniOperator 动态链接 `.so`**(libtnel.so 运行时加载 boostkit `.so`,非静态打包;`jni/CMakeLists.txt:41-45` 静态分支因无 `.a` 未触发):只改 OmniOperator `.cpp` 或 ABI 兼容头文件(加 override)不必重编 OmniStream,`operator_build`+`deploy` 换 `.so` 即可;头文件 ABI 破坏(新成员/新 virtual/Type B 新 Expr 类/Type C)才需 `omnistream_incr`。

## OmniStream

### 产物

- `cpp/build/jni/libtnel.so`(~82MB,ARM aarch64,stripped)—— 9 个静态库 `--whole-archive` 打包
- deploy 直接从 `cpp/build/jni/libtnel.so` 拷(不依赖 make install);若 `make install`(可选,需 install bulk 优化)→ `/usr/local/lib/libtnel.so` + 头文件装 `/usr/local/include/`
- 静态库:`cpp/build/{core,table,runtime,streaming,connector,datagen}/*.a` + `cpp/build/translate/{basictypes,functions,thirdlibrary}/*.a`

### 三种编译方式

| 方式                 | 命令                                                                    | 何时用                                  | 耗时                                                                                    |
| -------------------- | ----------------------------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------- |
| **增量(推荐)** | `export HOME=<remote_code_root> && cd cpp/build && make tnel -j$(nproc)` | 改了 .cpp/.h,日常重编                   | 改动少 1-3 分钟;重文件(如 StreamOperatorFactory.cpp)首次冷编 ~20 分钟,ccache 缓存后秒级 |
| 全量                 | `bash install_script/OmniStream/rebuild_omnistream_vec.sh Release`    | cmake 配置变更/彻底清理                 | 10-20 分钟                                                                              |
| PGO 生产             | `bash scripts/build_gcc.sh omnistream`                                | 出包/性能基准(PGO+LTO,ENABLE_TESTS=off) | 20-40 分钟                                                                              |

### 增量编译原理(通用化,不依赖本地 CMakeLists 优化)

保留 `cpp/build/` 目录,`make tnel` 据文件 mtime 增量重编改动文件的 `.o` + 重新链接 libtnel.so。**`make tnel` 只编 libtnel.so 目标,不编 tneltest(绕过 upstream vector_helper 重构链接失败)、不 `make install`(deploy 直接从 `cpp/build/jni/libtnel.so` 拷,避免无 install bulk 时逐文件 cp 卡死)**。`export HOME=<remote_code_root>` 修 reconfigure 路径(CMakeLists `if(EXISTS /repo)` 不成立走 else → `OMNIRUNTIME_SRC_DIR=$HOME`,源码在 `<remote_omnioperator>`)。**仅改 cmake 配置(CMakeLists.txt / 选项)才需重跑 `cmake ..`**,否则直接 `make tnel -j` 即可。日志:`rebuild_omnistream_vec.sh` 写 `/tmp/omnistream_build.log`。

### ccache 加速 + 编译慢根因(可选优化,由 init skill 应用到 CMakeLists;build-deploy 不依赖)

> 以下 ccache/install bulk 是**本地 CMakeLists 优化**(非 upstream 原版),由 `omnistream-env-init` skill 可选应用。build-deploy 的 `make tnel` 通用化后**不依赖**它们(upstream 原版 CMakeLists 也能编译部署)。

- **ccache(可选加速)**:`cpp/CMakeLists.txt` 顶部 `find_program(CCACHE)` 自动探测,已 `yum install ccache`(openEuler)。`make` 时 `HOME=<remote_code_root>` → 缓存目录 `<remote_code_root>/.ccache/`(5GB)。**首次冷编不加速**,后续改同一文件秒级命中。查缓存:`HOME=<remote_code_root> ccache -s`。
- **编译慢根因 = 激进内联**(upstream CMakeLists 自带,非本地优化):Release 的 `-O3 -finline-limit=6000 --param inline-unit-growth=300` → `StreamOperatorFactory.cpp`(含 LLVM + OmniOperator 重模板)单文件 20+ 分钟。ccache 缓存后跳过;**reconfigure 致 ccache miss 时会重编(全量约 40min)**。
- **⚠️ 禁止并发 make**:同一 `cpp/build/` 跑两个 `make` 会抢同一 `.o`、互相 `Terminated`,产物可能残缺。**一次只跑一个 make**。
- **make install 卡死(可选 install bulk 优化)**:upstream 原版 `install_headers()` 逐文件 cp 上千头文件卡死。本地优化改 1 条 bulk `install(DIRECTORY)`。**通用化后 `make tnel` 不 install、deploy 从 build/jni 拷,绕过此问题**(无需 install bulk 也能部署)。
- **tneltest 链接失败(upstream 2026_930_poc 已知,非本地引入)**:`vector_helper.h` header/source 分离重构(commit 7c78194a)致 tneltest 静态链接 `VectorHelper::PrintVecBatch/CreateVector` 等 undefined reference。**libtnel.so 不受影响**(动态链接 omni so,符号运行时解析)。`make tnel` 只编 libtnel.so 绕过;若需 C++ 单测,待 upstream 修复 vector_helper header-only 适配后 `cmake -DENABLE_TESTS=ON`。

### CMakeCache 关键配置(已验证)

- `CMAKE_BUILD_TYPE=Release`
- `CMAKE_INSTALL_PREFIX`:/usr/local(无 OMNI_HOME 时)或 $OMNI_HOME(设了 OMNI_HOME 走 if 分支);**deploy 不依赖 install prefix**(从 build/jni 拷)
- `ENABLE_TESTS`:默认 ON,但 upstream 2026_930_poc vector_helper 重构致 tneltest 链接失败 → **建议 `cmake -DENABLE_TESTS=OFF`**(或 `make tnel` 不编 test 绕过)
- `WITH_OMNISTATESTORE=OFF`(`install_step.sh` sed 关闭 BSS 状态后端)
- `LLVM_DIR=/usr/local/lib/cmake/llvm`
- 首次 configure:`cd cpp/build && cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_TESTS=OFF -DLLVM_DIR=/usr/local/lib/cmake/llvm`(ENABLE_TESTS=OFF 避免 tneltest 链接失败;HOME=<remote_code_root>)

### C++ 单测(可选)

```bash
ssh <user>@<host> 'source /etc/profile && cd <remote_omnistream>/cpp/build && ctest -j$(nproc) --output-on-failure'
```

测试在 `cpp/test/`(真实数据,禁止 mock)。

## OmniAdaptor(Java/Maven)

| 方式                 | 命令                                                            | 耗时                                                                                  |
| -------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **增量(推荐)** | `cd omni-flink-bundle && mvn package -DskipTests`(不带 clean) | 无改动 ~2s(Maven 增量 compile,日志 "Nothing to compile - all classes are up to date") |
| 全量                 | `mvn clean package -DskipTests`(清 target)                    | 数分钟                                                                                |

- 目录:`omnistream/omniop-flink-extension/omni-flink-bundle`
- 产物:`java/target/flink-tnel-0.1-SNAPSHOT.jar`(运行时扩展:Task/StreamTask/IO 覆盖 + JNI 入口)+ `omni-table-planner/target/omni-table-planer-0.1-SNAPSHOT.jar`(ExecNode 覆盖,注入 native JSON)
- 本地 Windows 装 JDK8 + Maven 也可编译;远端产物直接可用于部署。

## OmniOperator(C++ + Java JNI)

| 方式                 | 命令                                                                                                                                 | 耗时                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **增量(推荐)** | `HOME=<remote_code_root> cmake --build build -j$(nproc) && cmake --install build`(build/ 为 Ninja,`build.sh -G Ninja`+lld;不 clean) | 无改动 0s "no work to do";单文件改动 ~15s(ccache 直命中 .o + 重链 4 目标);**需 build 目录已存在** |
| 全量                 | `bash build_scripts/build.sh release:java`(`--clean-first` + 删 CMakeCache)                                                      | 20-40 分钟                                                                                              |

- 目录:`OmniOperatorJIT`;产物:`<omni_home>/lib/libboostkit-omniop-{codegen,operator,vector,reader}-2.2.0-aarch64.so`
- `OMNI_HOME=<omni_home>`。**首次需全量建 build 目录,之后日常用增量**(`build.sh` 的 `--clean-first` 是人为强制全量,非必需)。
- **ccache + 单测默认开**:`CMAKE_CXX_COMPILER_LAUNCHER` 启用(旧 `RULE_LAUNCH_*` 对 Ninja 无效已替换;Make/Ninja 通用,`HOME=<remote_code_root>` 共享 `<remote_code_root>/.ccache`,warm rebuild 100% hit);`option(EXCLUDE_TEST OFF)` → release 默认构建 `omtest`(不再 `--exclude-test`)。跑单测:`operator_test` 任务(全量)或 `build/core/test/omtest --gtest_filter='XxxTest.*'`(指定用例)。
- **⚠️ ccache 目录必须 `HOME=<remote_code_root>`**:ssh 默认 HOME=/root → ccache 写 `/root/.ccache` → 与 skill 任务的 `<remote_code_root>/.ccache` 分裂(查错目录看似 0 命中,实为冷缓存)。手动 ssh 构建务必前缀 `HOME=<remote_code_root>`;skill 的 `operator_*` 任务已带。

## 常见编译问题

| 现象                                                                                     | 原因                                                                                                                                                                                                                                                                                                      | 处理                                                                                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cmake 找不到 LLVM                                                                        | 未`source /etc/profile`                                                                                                                                                                                                                                                                                 | 每条命令前`source /etc/profile`                                                                                                                                                                                                                                                      |
| 链接 undefined reference                                                                 | OmniOperator so 未编译/部署                                                                                                                                                                                                                                                                               | 先`operator_build`,确认 `omni_home/omni-operator/lib/` 有 boostkit so                                                                                                                                                                                                              |
| make install 权限错误                                                                    | 非 root                                                                                                                                                                                                                                                                                                   | 服务器即 root,无问题                                                                                                                                                                                                                                                                   |
| 增量没重编改动文件                                                                       | build 目录 mtime 异常                                                                                                                                                                                                                                                                                     | 用`omnistream_rebuild` 全量重建                                                                                                                                                                                                                                                      |
| `make: *** Terminated` + `Deleting file ...o`                                        | **并发 make 互踩**(同 build 目录两个 make)                                                                                                                                                                                                                                                          | 禁止并发;等现有 make 结束或杀干净再跑                                                                                                                                                                                                                                                  |
| `make install` 末尾卡死(拷头文件)                                                      | upstream 原版`install_headers()` 逐文件 install                                                                                                                                                                                                                                                         | 用`make tnel` 不 install(deploy 从 build/jni 拷);或应用 install bulk 优化(init)                                                                                                                                                                                                      |
| 单文件编译 20+ 分钟                                                                      | 激进内联`-finline-limit=6000` + 重模板文件                                                                                                                                                                                                                                                              | 正常;ccache 缓存后后续秒级。首次冷编只能等                                                                                                                                                                                                                                             |
| `operator_incr` 报 "build 目录不存在"                                                  | 首次未全量建 build                                                                                                                                                                                                                                                                                        | 先跑一次`operator_build` 全量建 build 目录,之后日常用 `operator_incr`                                                                                                                                                                                                              |
| OmniOperator 改 core 头文件(`expressions.h`/`VectorFunction.h` 等)后增量编译 17+ min | 被`.h` 级联:所有 `#include` 它的 `.cpp` 全重编(`expressions.h` 被 expr/vectorization/codegen/test 几乎全 include)                                                                                                                                                                                 | 尽量把逻辑放`.cpp`(如 BetweenExpr 的 `vectorFunction` 设置放 `expressions.cpp` 构造函数,仅 `supportVectorized()` override 必须 inline 在 `.h`);ccache warm 后同文件秒级,但头文件改触发的是**下游 `.cpp`** 重编,ccache 命中率低,只能等。属必要代价,别中途 Ctrl-C 重跑 |
| 想跑单测是否要再编译一次?                                                                | `EXCLUDE_TEST` 默认 OFF → release build **已含 `omtest`**(单测二进制)                                                                                                                                                                                                                          | **不需再 build**。直接 `build/core/test/omtest --gtest_filter='XxxTest.*'` 跑指定用例(operator_test 任务即此);或 `bash build.sh test` 一步 build+test。**1 次编译带测试即可**,别 release build + test build 跑两遍                                                     |
| 只改了注释,增量编译耗时                                                                  | **build/ 已切 ninja + ccache(`HOME=<remote_code_root>`)→ 注释改动 ~15s**(ccache 直命中 .o 秒级 + 重链 4 目标:libexpression.a + codegen/operator .so + omtest),不再是 make 时代的 5-10 min。原 make 慢根因:make 重编该 .cpp + 重链 85MB .so(link 不缓存)且 make 无 restat,注释 mtime 变必触发 relink | ninja+ccache 已是日常增量基线(15s 可接受)。仍想零等待:①**不同步纯注释到远端**(注释本地保留,与下次逻辑改动一起 sync;纯注释行为不变,旧 .so 仍有效,无需重编验证)。② `touch -r <.o> <source>` 恢复 mtime(仅注释安全,逻辑改动禁用)                                                |
