---
name: "omnistream-expression-test"
description: "开发好的向量化表达式的 native vs vanilla 黄金对比测试。本地 csv+sql 用例(每个测试一个文件夹),本地驱动 run_local.sh 跑 native(OmniStream)与 vanilla(Flink 原生)对比,富报告生成到本地 flink-test/report/<name>/。触发:测试表达式/表达式黄金对比/native vs vanilla/verify_expr/csv_test/表达式开发后验证/CONCAT_WS/MD5/ACOS 等函数 native 验证。"
---
# OmniStream 表达式测试 skill

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);env.sh 由 init 从 AGENTS.md §5 派生。本文件 <placeholder> 由 agent 运行时替换。

> 📖 **表达式开发权威指南**:全链路架构、Type A/B/C/D 分类、框架原理(Expr/Visitor/JSONParser/FunctionRegistry)、json_value 深度案例、C 函数规范与排错,见 [表达式开发指南.md](../omnistream-expression-dev-test/references/表达式开发指南.md)。本 skill 聚焦 native vs vanilla 黄金对比测试,权威指南为总纲。

开发完一个 OmniOperator 向量化函数后,用 **csv + sql** 用例跑 **native(OmniStream)vs vanilla(Flink 原生)** 黄金对比,验证 native 与原生语义一致。测试用例与报告都在**本地** `flink-test/` 工作区,服务器不留报告。

## 测试布局(本地 `flink-test/`)

```
flink-test/
├── test/                       # 测试用例(每个测试一个文件夹; 不走 SFTP, 需手动 scp 上传)
│   └── <name>/
│       ├── <name>.csv          # 输入(正常/边界/NULL/越界)
│       └── <name>.sql          # SQL(csv path 须为 /tmp/<name>.csv)
└── report/                     # 测试报告(本地生成, 不上服务器)
    └── <name>/
        └── <name>.report.md    # 富报告: 测试内容 + native/vanilla 输出 + 归一化 diff + 结论
```

> SFTP 约定:`flink-test/test/` 与 `flink-test/report/` 都在 sftp.json ignore 中(**不上传**)。`run_local.sh` 负责 scp 上传 test 到 `/tmp/`,报告纯本地。

## 适用场景

- 开发完一个向量化函数(`OmniOperator/core/src/vectorization/registration/Register*.cpp` 注册),验证其 native 执行结果与 Flink 原生一致
- 也可跑使能测试 `enable_test`(纯投影,验证 native 使能端到端,见 `omnistream-build-deploy`)
- 已有 40+ 表达式用例可参考:`<install_script_dir>/queries/csv_test/<expr>/verify_expr_<expr>.{csv,sql}`(acos/floor/hex/md5/round/substring/...)

## 关键前提(源码核对,必读)

**1. 函数注册名必须与 SQL 函数名匹配**,否则 native 运行时 `jsonparser.cpp:511` 报 `Function not supported`:

- OmniOperator 注册名:`Register*.cpp` 的 `RegisterFunction(prefix + "name", ...)`
- OmniAdaptor `RexNodeUtil` 把 SQL 函数转成 `function_name`
- 两者必须一致,native 才能查表命中
- ⚠️ **反例 `char_length`**:`RegisterString.cpp:42` 注册名是 `"length"`,SQL 用 `char_length` → 名字不匹配 → not supported(虽有 `CharLengthFunction` 实现,见 `String.h:651`)。测试前先确认注册名。

**2. OmniAdaptor 决策白名单**(`ValidateCalcOPStrategy`):

- BINARY:`OR/AND/ADD/SUBTRACT/MULTIPLY/DIVIDE/MODULUS/GREATER_THAN/.../EQUAL/NOT_EQUAL/DATE_FORMAT/count_char`
- UNARY:`CAST/NEGATION`(注:CAST 是 fake,WARNING might not be supported)
- FUNCTION:决策**不校验函数名**(只校验 exprType/operator/returnType 结构)→ **决策通过 ≠ native 运行时支持**。所以必须实际跑 native 验证。

**3. native 已使能**:由 `omnistream-build-deploy` 保证(deploy + parent-first + cluster_start 带 `WRITE_TO_FILE=TRUE`)。`<flink_home>/bin/config.sh.bak` 存在(vanilla 切换后恢复用)。

**4. Sink 输出类型须在 `SINK_SUPPORT_DATA_TYPE` 内**(`OmniGraphOverride.java:215`):仅 BIGINT/INTEGER/VARCHAR(各宽度)/STRING/TIMESTAMP(0-3,9)/TIMESTAMP_LTZ(3)/DECIMAL64/DECIMAL128,**不含 DOUBLE/BOOLEAN/CHAR**。超出则 `isSinkSupportNative=false` → Sink 判 NOT SUITABLE → 整链 `useOmniFlag=false` 静默回退 vanilla(welcome=0、native 0 行,且无 `Current rexNode is`/`not supported` 日志,因决策在 buildJsonMap 注入前就否决)。注意:Calc 层(batch_coalesce 等)可能支持 DOUBLE/BOOLEAN,但 native print Sink 不接受 → **"Calc 支持 ≠ Sink 支持 ≠ 端到端可测"**;`'def'` 等 CHAR 字面量也会让 `IFNULL(STRING,'def')` 被推导为 CHAR 触发此问题,用 STRING 列或 `CAST(... AS STRING)` 避免。

**5. BOOLEAN 返回表达式(BETWEEN/比较/逻辑)的 e2e 测法——两条路径,测的不同**:

- **测 VECTORIZED 路径(你的 VectorFunction)→ 用 FILTER,不要 CAST**:`SELECT row_id, c FROM src WHERE bool_expr`(bool_expr 是过滤条件)。无 CAST → 无 SWITCH_GENERAL → Calc 向量化 → `ExprEval::Visit` → 你的 VectorFunction。输出非 bool 列(row_id/c,sink 支持)。**这是唯一能 e2e 验证向量化函数的方式**。例:`WHERE c BETWEEN 10 AND 20`(见 between_types 用例)。
- **测 CODEGEN 回退路径 → 用 `CAST(bool_expr AS INT)` 投影**(TRUE→1/FALSE→0/UNKNOWN→null):⚠️ **`CAST(BOOLEAN AS INT)` 被 Flink planner 改写成 `CASE(IS NOT NULL(b), CASE(b,1,0), null)` → `SWITCH_GENERAL` → `SwitchExpr` 不设 vectorFunction/不 override supportVectorized → 整树 `isSupportVectorization=false` → 走 codegen**(2026-07-20 TM 日志 + RexNode 诊断实证)。即 CAST AS INT 投影**测的是 codegen,不是你的向量化函数**。输出 1/0/null(数值无大小写 diff,三值保留)。
- 两条路径都要测(向量化 + codegen 回退,因不支持类型生产环境会回退 codegen)。
- ⚠️ **勿用 `CAST AS VARCHAR`**:BOOLEAN→VARCHAR 输出大小写("true"/"TRUE")与 vanilla 可能不一致 → 假 diff。
- ⚠️ **勿用 `CASE WHEN` / `IF` 包裹**:同 CAST AS INT,都映射 SWITCH_GENERAL → codegen(测 codegen 可用,测向量化不行)。
- ⚠️ **字面量界类型限制(FILTER 也受影响)**:BETWEEN/比较的字面量界(literal bound)只支持 INT/BIGINT(数字 value);VARCHAR/TIMESTAMP 字面量界 OmniAdaptor 序列化为对象 value(`{charsetName,value}`/`{millisSinceEpoch}`),OmniStream jsonparser 读字面量期望 number → `json.exception.type_error.302 "type must be number, but is object"` → OmniTask init 崩 → `StreamCalcBatch::close` crash → welcome 0→0。列界(`c BETWEEN c_lo AND c_hi`,FIELD_REFERENCE)无字面量,任意类型正常。VARCHAR/TIMESTAMP 的向量化分派只能 UT 测(Apply 直驱)。

## 测试设计完整性(2026-07-21 复盘,必读)

一个向量化表达式的 e2e 测试必须覆盖**完整矩阵**:语义变体 × 执行路径 × 类型。只测一条路径或只测基础语义 = 不完全(易漏 bug,且向量化函数可能根本没被端到端执行)。

**1. 语义变体全覆盖**:不只测基础形态,要测该表达式的所有 SQL 变体。BETWEEN 例:ASYMMETRIC / point(low==high)/ NOT BETWEEN / NULL 界三值(`FALSE AND UNKNOWN=FALSE`)/ SYMMETRIC(low≠high 会崩 Flink planner,只测 low==high)。反例:首轮 between_types 只测基础 ASYMMETRIC,漏了 NOT/SYMMETRIC/NULL 的向量化路径。

**2. 两条执行路径都测**(见前提 5):

- **codegen 路径**:`CAST(bool_expr AS INT)` 投影(CAST→CASE→SWITCH_GENERAL→codegen)。
- **向量化路径**:`WHERE bool_expr` FILTER(无 CAST→向量化→你的 VectorFunction)。
- ⚠️ 两条路径结果可能不同(codegen 的简化 NULL 逻辑 vs 向量化的严格三值),必须分别验证 native==vanilla。只测 codegen(投影)≠ 验证了你的向量化函数。

**3. 类型覆盖按可达性分层**:

- e2e 可达(字面量界):INT/BIGINT(数字 value,jsonparser 可解析)。
- e2e 可达(列界 FIELD_REFERENCE):任意类型(无字面量)。
- e2e 不可达:VARCHAR/TIMESTAMP 字面量界(jsonparser gap,见前提 5)、DOUBLE/BOOLEAN/CHAR(SOURCE/SINK_SUPPORT 限制)。
- 不可达类型只能 UT 测(Apply 直驱),UT 类型覆盖要比 e2e 广。

**4. 每个组合都跑 + 记 pass/fail**:在 `flink-test/test/<name>/` 下写一个 matrix md(如 `README.md`),列出 语义×路径×类型 每个组合的 native/vanilla pass/fail + 失败根因。别只跑一个用例就声称覆盖完整。

## 流程(3 步)

1. **准备用例**:`flink-test/test/<name>/<name>.{csv,sql}`(csv path `/tmp/<name>.csv`)。**设计原则参考 `install_script/queries/csv_test/<expr>/verify_expr_<expr>.{csv,sql}`**(40+ 现成用例):
   - csv:第一列 `row_id`(diff 行对照)+ 输入值,`null`=NULL,无 header
   - sql 头注释:语义(引 `flink/docs/data/sql_functions.yml`)+ 语法 + 返回类型 + NULL 处理 + 实现注册名 + 跑法
   - `SET 'parallelism.default'='1'; SET 'table.local-time-zone'='UTC';`
   - `CREATE TABLE src`(filesystem csv,`csv.null-literal='null'`)+ `CREATE TABLE sink`(`'connector'='print'`)+ `INSERT INTO sink SELECT ...`
   - sql 尾注释:期望输出(按 row_id 对照)+ 场景覆盖(正常/边界/NULL/越界)
   - **sink 输出类型须落在 `SINK_SUPPORT_DATA_TYPE` 内**(见关键前提 4),否则静默回退
   - 可参考 [templates/](templates/) 模板
2. **本地驱动跑对比**:`bash run_local.sh <name>` —— 自动 scp 上传 test+脚本 → ssh 跑 native+vanilla+compare → 取回结果。
3. **看报告**:`flink-test/report/<name>/<name>.report.md`(本地富报告)。

## 脚本

| 文件                                                                | 说明                                                                                     |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [scripts/run_local.sh](scripts/run_local.sh)                         | **本地驱动**(Git Bash 运行):scp 上传 + ssh 跑 run_test.sh + 本地组装富报告。入口。 |
| [scripts/run_test.sh](scripts/run_test.sh)                           | 服务端:跑 native+vanilla+compare,结构化结果输出 stdout(不生成报告文件)。                 |
| [scripts/compare.sh](scripts/compare.sh)                             | 归一化对比(基于 csv_test/compare_native_vanilla.sh)。                                    |
| [templates/expr_test.csv.template](templates/expr_test.csv.template) | csv 输入模板(占位符,创建新用例时参考)。                                                  |
| [templates/expr_test.sql.template](templates/expr_test.sql.template) | sql 查询模板(占位符 + 期望输出注释,csv path`/tmp/<EXPR_NAME>.csv`)。                   |

## 报告(本地 `flink-test/report/<name>/<name>.report.md`)

`run_local.sh` 自动生成(`mkdir -p` 创建目录),覆盖写(最新一次)。含:

- 测试内容(测试名 + 时间 + 服务器 + CSV 行数 + SQL 全文)
- Native 输出(welcome 计数 before→after + `/tmp/flink_output.txt` 内容,格式 `+I,v1,v2`)
- Vanilla 输出(print sink `.out` 内容,格式 `+I[v1, v2]`)
- 正确性对比(归一化后 diff + `RESULT: IDENTICAL/DIFFERENCES`)
- 结论(✅ PASS / ❌ FAIL)

## 执行方式

本地(Git Bash,ssh 免密;连接信息见 `scripts/env.sh`):

```bash
# 假设已建好 flink-test/test/concat_ws/concat_ws.{csv,sql}
bash .claude/skills/omnistream-expression-test/scripts/run_local.sh concat_ws
# 报告: flink-test/report/concat_ws/concat_ws.report.md
```

> 全程约 2-3 分钟(native + vanilla 各重启一次集群)。ssh 偶因 stop-cluster 抖动退出码非 0,重跑即可。

## 排错(welcome=0 / native 0 行)

报告 FAIL 且 `welcome 0→0`、native 0 行时,**先按链路逐一排查,勿臆测根因**(2026-07-21 复盘:首轮 BETWEEN 失败臆测"codegen 不支持 VARCHAR",实为 jsonparser 字面量解析,浪费一轮)。

**⚠️ 归因原则(必读,避免误判)**:

- **vanilla 是正确性基线**。一个失败判为「Flink 原生问题」**当且仅当 vanilla 也失败**(pure Flink 复现)。**若 vanilla 产出正确结果而 native 失败 → 是 Omni 模块 bug(OmniAdaptor/OmniStream/OmniOperator),不是 Flink**。绝不能只凭源码分析就把 native 失败归给 Flink —— 必须实跑 vanilla 验证。
- **分清阶段**:planner 期失败(translateToPlan / SearchOperatorGen / RexSimplify)在 native 与 vanilla 共享同一 planner 时两边都崩;若 vanilla 不崩只 native 崩 → 是 OmniAdaptor planner 覆盖或 OmniStream 运行期问题。runtime 期失败(native OmniTask vs vanilla codegen)只影响一边。
- **反例(2026-07-20)**:low>high BETWEEN 我凭源码分析归为"Flink vanilla bug"(Sarg.isComplementedPoints),**未实跑 vanilla 验证**。若 vanilla 实际能正确返回 FALSE/空(不崩),则实为 Omni 问题, attribution 错。

**链路排查框架(逐层定位)**:
0. **先读 TM .out 异常**:`LOG=$(ls -t <flink_home>/log/flink-*-taskexecutor-0-*.out|head -1); grep -iE "exception|error|fatal|core dumped|welcome to native|OmniTask|json\.exception" "$LOG" | tail -30`。异常信息直接指根因(jsonparser `type must be number, but is object` / codegen 段错误 / `find OmniTask still uninitialzed` 等)。**看到具体异常再定位,不要先猜**。

1. **测试用例本身**:vanilla 是否产出正确结果?vanilla 对=SQL/CSV 语义对;vanilla 错=用例写错。
2. **数据类型**:value/bound 类型是否 e2e 可达?(前提 5:字面量界只 INT/BIGINT;SOURCE/SINK_SUPPORT 限制)。
3. **Flink 原生(vanilla)**:作为基线,确认 vanilla 正确(native 对齐对象)。
4. **OmniAdaptor(决策+JSON)**:graph 是否 SUITABLE?JSON 序列化对不对?(sql-client 日志 `Current rexNode`/`SUITABLE`/`inputTypes`)。
5. **OmniStream(解析+执行)**:jsonparser 能解析 JSON 吗?OmniTask init 成功吗?(TM .out `json.exception`/`OmniTask still uninitialzed`)。
6. **OmniOperator(函数+codegen)**:向量化函数 dispatch 对吗?codegen 回退对吗?(UT 验证函数;codegen 看 codegen 路径)。

**诊断操作步骤:**

1. **看 sql-client 日志(不是 TM .log)**:算子替换决策在 Client 端(OmniGraphOverride + buildJsonMap),日志在 `<flink_home>/log/flink-*-sql-client-*.log`。⚠️ `run_test.sh` 的 vanilla 阶段会覆盖它 → 需单独跑 native 诊断(见下脚本)。
2. **grep 决策链路**:`grep -iE "Current rexNode|not supported|SUITABLE|useOmni|inputTypes|outputTypes" flink-*-sql-client-*.log`
   - `Current rexNode is <FN>(...)` → buildJsonMap 被调,Flink 保留该 RexCall(确认 operator name 是否被展开)
   - `The operator <FN> is not supported` → `specialOperatorMap` 无映射(走 INVALID)
   - `is NOT SUITABLE for OmniTask` + `outputTypes` → Sink/算子类型不支持(见前提 4:DOUBLE/BOOLEAN/CHAR)
3. **ssh 长命令抖动(exit 255)**:stop-cluster/pkill 会断开 ssh 连接 → 诊断脚本用 **nohup 后台**:`scp diag.sh <user>@<host>:/tmp/` → `ssh <user>@<host> 'nohup bash /tmp/diag.sh > /tmp/diag.out 2>&1 < /dev/null & disown'` → `sleep 180; ssh <user>@<host> 'cat /tmp/diag.out'`。
4. 根因定位后改用例/映射/实现 → 重跑 `run_local.sh <name>`。

诊断脚本模板(清旧 sql-client 日志 + 单跑 native + 抓决策链):

```bash
#!/bin/bash
source /etc/profile; export FLINK_HOME=<flink_home>; export PATH=$FLINK_HOME/bin:$PATH
stop-cluster.sh >/dev/null 2>&1; sleep 2; pkill -9 -f taskexecutor 2>/dev/null; pkill -9 -f standalonesession 2>/dev/null; sleep 2
export FLINK_PERFORMANCE=1 WRITE_TO_FILE=TRUE
rm -f <flink_home>/log/flink-*-sql-client-*.log*
start-cluster.sh >/dev/null 2>&1; sleep 12; rm -f /tmp/flink_output.txt
timeout 120 sql-client.sh -f /tmp/<name>.sql > /tmp/native_sql.log 2>&1; echo "sql-rc=$?"; sleep 8
SLOG=$(ls -t <flink_home>/log/flink-*-sql-client-*.log | head -1)
grep -iE "Current rexNode|not supported|SUITABLE|useOmni|inputTypes|outputTypes" "$SLOG" | tail -40
cat /tmp/flink_output.txt
```

## 核心踩坑(提炼自记忆)

- **pc=0x0 SIGSEGV = 空函数指针**:native 段错误地址为 0x0 多为解引用未解析的 vectorFunction(常 Type B Expr 漏注册 CHAR 组合),看 JSON arg dataType 对 `Register*.cpp` 签名补齐。
- **字符串函数 e2e 勿含 emoji/增补平面字符**:native 按 Unicode 码点计、Flink 按 UTF-16 码元,仅增补平面分歧(BMP 无),含 emoji 会假 diff。
- **LIKE e2e 勿含 `\` 转义模式**:OmniOperator 2-arg LIKE 默认 `\` escape(Spark 语义)、Flink 无默认 escape(`\` 字面、`%` 通配),含 `\` 模式 native≠vanilla,只测 `%`/`_`/exact/NULL。
- **`WRITE_TO_FILE=TRUE` 须在 `start-cluster.sh` 之前 export**:由 TM 进程启动时读取,先启动再 export 不生效、native 不落盘(`/tmp/flink_output.txt` 为空)。
- **SFTP 未同步兜底**:本地改源码远端核查未生效时,commit 后切换分支触发 SFTP 重传(工作树 mtime 变化触发全量重检),日常 Ctrl+S 即同步。

## 与其他 skill 关系

- 编译/部署/native 使能 → `omnistream-build-deploy`(本 skill 假设 native 已使能;enable_test 也用本 skill 的 `run_local.sh`)
- 表达式开发(实现新函数)→ `omnioperator-expression-dev`
- 表达式支持现状分析 → `flink-native-expression-analysis`
- 结果不一致根因定位 → `omnistream-expression-dev-test` 排错
