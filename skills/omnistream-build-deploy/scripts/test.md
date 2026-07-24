# 测试流程(test):native 使能验证(A 类固定使能测试)

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时从 AGENTS.md 替换。

编译部署后验证 OmniStream native 使能。用 **A 类固定使能测试** `enable_test`(纯投影,无函数,规避 `char_length` 式 not supported),测试用例在本地 `flink-test/test/enable_test/enable_test.{csv,sql}`。

> 测试用例与报告都在本地 `flink-test/` 工作区(不走 SFTP,`run_local.sh` 负责 scp 上传)。**服务器不留报告**。

## 用例说明
- 输入:`enable_test.csv`(8 行:`auction,bidder,price,channel`,`csv.null-literal='null'`)
- SQL:`SELECT channel, price FROM src`(纯投影,Calc FIELD_REFERENCE 直接 SUITABLE 走 native)
- sink:`print`;但 **native 侧 SinkOperator 为桩实现,不写 print stdout** —— native 结果经 `WRITE_TO_FILE=TRUE` 落盘 `/tmp/flink_output.txt`(格式 `+I,v1,v2`);vanilla 侧 print 正常写 TM `.out`(`+I[v1, v2]`)
- 本地源:`flink-test/test/enable_test/enable_test.{csv,sql}`
- 原理:纯投影无函数 codegen,native 必成功
- ⚠️ `WRITE_TO_FILE` 必须 `=TRUE`(native `StreamOperatorFactory.cpp:365` 判 `=="TRUE"`,路径硬编码 `/tmp/flink_output.txt`);`cluster_start` 任务已带此 export

## 方式一:完整对比 + 本地报告(推荐)

委派 `omnistream-expression-test` 的本地驱动(native vs vanilla 黄金对比 + 富报告):
```bash
bash .claude/skills/omnistream-expression-test/scripts/run_local.sh enable_test
```
- 自动:scp `flink-test/test/enable_test/enable_test.{csv,sql}` → `/tmp/` → ssh 跑 native+vanilla+compare → 本地组装报告
- 报告:`flink-test/report/enable_test/enable_test.report.md`(测试内容 + native/vanilla 输出 + 归一化 diff + ✅PASS/❌FAIL)
- 全程约 2-3 分钟(native + vanilla 各重启一次集群);结束自动恢复 native 集群

## 方式二:快速 native-only 检查(无报告,迭代用)

只验证 native 使能(welcome + native 输出),不跑 vanilla,不开报告。适合 build→deploy→test 快速循环。

### 1. 上传测试资产(本地 → 服务器)
```bash
scp flink-test/test/enable_test/enable_test.csv flink-test/test/enable_test/enable_test.sql <user>@<host>:/tmp/
```

### 2. 重启集群(使部署生效 + 带 WRITE_TO_FILE=TRUE)
部署改动后必须重启。任务 `cluster_stop` + `cluster_start`(`cluster_start` 已 `export WRITE_TO_FILE=TRUE`),或手动:
```bash
ssh <user>@<host> 'source /etc/profile && stop-cluster.sh; sleep 2; pkill -9 -f taskexecutor; pkill -9 -f standalonesession; sleep 2; export WRITE_TO_FILE=TRUE; start-cluster.sh; sleep 8'
```

### 3. 提交 + 验证
任务 `test_native`(抓 welcome + 读 `/tmp/flink_output.txt`,**不生成报告**),或手动:
```bash
ssh <user>@<host> 'source /etc/profile && export FLINK_HOME=<flink_home> && export PATH=$FLINK_HOME/bin:$PATH && LOG=$(ls -t <flink_home>/log/flink-*-taskexecutor-0-*.out|head -1) && B=$(grep -c "welcome to native" "$LOG") && rm -f /tmp/flink_output.txt && timeout 120 sql-client.sh -f /tmp/enable_test.sql 2>&1 | grep -iE "Job ID|submitted|error" | head && sleep 12 && A=$(grep -c "welcome to native" "$LOG") && echo "welcome: $B -> $A" && echo "=== native output ===" && cat /tmp/flink_output.txt'
```

## 预期输出(native 落盘 `/tmp/flink_output.txt`,格式 `+I,channel,price`,parallelism=1 保序)
| 输入行 (auction,bidder,price,channel) | 预期 |
|---|---|
| 100,5,200,Google | `+I,Google,200` |
| 5,100,3,Facebook | `+I,Facebook,3` |
| 12345,234,12345,Baidu | `+I,Baidu,12345` |
| 999,99,1,Apple | `+I,Apple,1` |
| 0,0,0,AB | `+I,AB,0` |
| 7,7,7,null | `+I,null,7`(`csv.null-literal='null'` → NULL) |
| 88,8,42,HelloWorld | `+I,HelloWorld,42` |
| 2147483648,123,9999999999,Channel_X | `+I,Channel_X,9999999999` |

## 通过判据
- ✅ TM log `welcome to native` 计数增加(native Task 运行,`OmniTask.cpp:315`)
- ✅ `/tmp/flink_output.txt` 输出 8 行与上表逐行一致(native 结果正确)
- ✅(方式一)报告显示 `RESULT: IDENTICAL`(native == vanilla)

## 失败排查
| 现象 | 原因 | 处理 |
|---|---|---|
| 无 `welcome to native` | native 未使能 | 查 `parent-first` / `<deploy_dir>/` / `libtnel.so` |
| TM 启动即崩 | libtnel.so 加载失败 | `ldd <deploy_dir>/libtnel.so` 查缺失依赖 |
| 算子描述无 `originDescription` | table-planner jar 未注入 | 查 `PlannerModule.java` 加载逻辑(见 deploy.md) |
| `/tmp/flink_output.txt` 不存在/为空 | `WRITE_TO_FILE` 未 `=TRUE` 或未在 `start-cluster` 前 export | 重启集群前 `export WRITE_TO_FILE=TRUE`(=`cluster_start` 任务) |
| 输出与预期不符 | native bug | 切 vanilla 对比定位(`run_local.sh` 报告里的 diff) |
| `Job ID` 未出现 | SQL 提交失败 | 看 sql-client 完整 stderr |

## 进阶:表达式 native vs vanilla 对比
测具体表达式(非纯投影)同样用 [`omnistream-expression-test`](../../omnistream-expression-test/SKILL.md) skill 的 `run_local.sh`(在 `flink-test/test/<expr>/` 建用例 → 本地报告 `flink-test/report/<expr>/`)。
