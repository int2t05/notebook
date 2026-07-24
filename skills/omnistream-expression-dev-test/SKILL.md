---
name: "omnistream-expression-dev-test"
description: "表达式开发+编译测试全周期 skill。从需求到 OmniOperator 实现 + OmniAdaptor 适配 + 三仓库编译 + 部署 + native vs vanilla 对比 + 报告。编排 omnioperator-expression-dev(实现)/omniadaptor-vectorized-expression(适配)/omnistream-build-deploy(编译部署)/omnistream-expression-test(测试)。触发:开发新表达式并编译验证/表达式全周期/实现函数并跑通测试/新增向量化函数端到端/Type A 标量函数开发测试/row JIT 函数开发/json_value/char_length 类函数实现验证。"
---

# 表达式开发 + 编译测试 全周期 skill

> 路径/host/user 取自 repo 根 AGENTS.md(omnistream-env-init 生成);本文件 <placeholder> 由 agent 运行时替换。

> 📖 **表达式开发权威指南**:全链路架构、Type A/B/C/D 分类、框架原理(Expr/Visitor/JSONParser/FunctionRegistry)、json_value 深度案例、C 函数规范与排错,见 [表达式开发指南.md](references/表达式开发指南.md)。本 skill 聚焦全周期编排(实现→适配→编译→部署→测试→报告),权威指南为总纲。

开发一个新的 native 表达式,完成**实现 → 适配 → 编译 → 部署 → 测试 → 报告**全周期。本 skill 是**编排层**:按流程调用四个现有 skill,补上 `omnioperator-expression-dev`(无硬件不跑)缺失的编译测试环节,覆盖 Type A/B/C/D 全分类。

## 定位(与现有 skill 分工,不重复)

| 环节 | 调用 skill | 本 skill 角色 |
|---|---|---|
| OmniOperator **向量化**函数实现(`vectorization/functions/*.{h,cpp}` + `Register*.cpp` + 单测) | `omnioperator-expression-dev` | 编排 + **补编译测试**(该 skill 仅覆盖向量化路径、声明无硬件不跑;row JIT/Type B/C/D 亦由本 skill 编排) |
| OmniAdaptor 适配(RexNodeUtil + 函数字典 + 调研) | `omniadaptor-vectorized-expression` | 编排(其步骤 1 调研 / 步骤 2 适配) |
| 三仓库编译 + 部署 + native 使能 | `omnistream-build-deploy` | 编排(operator_build/adaptor_build/deploy) |
| native vs vanilla 对比 + 报告 | `omnistream-expression-test` | 编排(run_local.sh) |

> 独特价值:`omniadaptor-vectorized-expression` 不实现 OmniOperator(不支持就结束)且仅向量化;`omnioperator-expression-dev` 不编译不跑。本 skill 串联**完整周期**(含 OmniOperator 实现 + row JIT/Type B/C/D + 实际编译测试)。

## 服务器与路径常量

服务器/路径/身份常量见 `AGENTS.md`(§5 真源),任务命令见 `omnistream-build-deploy/scripts/config.ini` `[exec]` 段,本 skill 不重复定义。本 skill 特有路径:
- OmniOperator 实现:`<remote_omnioperator>/core/src/{codegen/functions,vectorization/functions,expression}`
- OmniOperator 注册:`<remote_omnioperator>/core/src/{codegen/func_registry_*.cpp, vectorization/registration/Register*.cpp}`
- OmniAdaptor 协议:`<remote_omniadaptor>/.../nodes/exec/util/RexNodeUtil.java`
- 测试报告:本地 `flink-test/report/<expr>/`

## 全流程(6 阶段)

### 阶段 0:分类决策

判断表达式类型,决定改动范围:

| 类型 | 触发 | 改动 |
|---|---|---|
| **Type A** 标量函数 | `FUNCTION` | OmniAdaptor + OmniOperator |
| **Type B** 特殊语法 | 新 exprType | OmniAdaptor + OmniOperator(jsonparser + Expr 体系) |
| **Type C** 聚合 | 算子级 aggInfoList | OmniAdaptor + OmniStream + OmniOperator |
| **Type D** 改名/别名 | `FUNCTION` | 仅 OmniAdaptor(或 OmniOperator aliases) |

Type A 再分两条路径(最关键决策):
- **row JIT**:逐行复杂逻辑/外部上下文(JSON 缓存、正则)→ `codegen/functions/` + `func_registry_*.cpp`(样例 `json_value`)
- **向量化**:纯列式可向量化、追求吞吐 → `vectorization/functions/` + `Register*.cpp`(样例 `char_length`)

> 两条路径 JSON 侧(`RexNodeUtil`)完全一样(都发 `FUNCTION` + `function_name`),区别只在 OmniOperator 注册到哪张表。

### 阶段 1:开发

**先调研后开发**(omniadaptor-vectorized-expression 步骤 1,不可跳):核对 `OmniAdaptor/omnihelper/resources/` 函数字典(`flink_function_dictionary.json`/`flink_function_return_type.json`)语义/类型 + OmniOperator 注册类型 + 入参匹配。

按 Type 实现(文件级清单见下):

- **Type A 向量化**:用 `omnioperator-expression-dev` 模板实现 `vectorization/functions/<Func>.{h,cpp}` + 注册 `Register*.cpp`(Path A SimpleFunction)
- **Type A row JIT**:(以 `CountChar` 为模板)→ `codegen/functions/<domain>functions.{h,cpp}` 声明+实现 + `func_registry_<domain>.cpp` 加 `XxxFnStr()` + `Function` 注册(遵循 C 函数参数规范,见 `omnioperator-expression-dev` references)
- **Type B**:(`jsonparser.cpp:547` 加 exprType 分支 + `ParseJSONXxx` + 按需新 Expr 类 + 各 Visitor `Visit` + `expression_codegen`)
- **Type C**:(`operator/util/function_type.h` 的 `FunctionType` 枚举 + `aggregator.h` 新 `Aggregator` 子类 + `aggregator_factory.{h,cpp}`,按枚举分发)
- **Type D**:(`RexNodeUtil` 映射 `function_name` = 已注册名,或 `Function` 构造 `aliases`)

OmniAdaptor 侧(Type D 仅改名可跳过):
- `RexNodeUtil.java`:`specialOperatorMap` + `SpecialExprType` + `buildJsonMap()` case(生成 `FUNCTION` + `function_name`)
- `flink_function_dictionary.json`/`flink_function_return_type.json`:`is_support_func`/`is_supported_type`(正向列表)/`return_type`
- `ValidateCalcOPStrategy.java`:按需补校验

> ⚠️ **注册名 = function_name(大小写敏感)**。反例 `char_length`:`RegisterString.cpp:42` 注册名 `"length"` ≠ SQL `char_length` → native `jsonparser.cpp:511` not supported。开发前确认注册名与 SQL 函数名一致。

### 阶段 2:编译(按改动范围,omnistream-build-deploy)

只重编受影响仓库,直接 ssh 跑(命令取自 omnistream-build-deploy config.ini):

| 改动 | 任务 |
|---|---|
| OmniOperator | `operator_build` |
| OmniAdaptor | `adaptor_build` |
| OmniStream(仅头文件 ABI 破坏 / Type C 算子级) | `omnistream_incr` |

> 命令实现见 `omnistream-build-deploy/scripts/config.ini` `task_<name>`(不在此重复,避免漂移)。

> `omnioperator-expression-dev` 声明无硬件不编译;本阶段在服务器实际编译,补其缺失。
>
> OmniStream 经动态链接用 OmniOperator `.so`(非静态打包):OmniOperator `.cpp`-only 或 ABI 兼容头文件改(加已有 virtual 的 override)不必重编 OmniStream,`operator_build`+`deploy` 换 `.so` 即可;仅头文件 ABI 破坏(新成员/新 virtual 槽/Type B 新 Expr 类/Type C)才需 `omnistream_incr`。

### 阶段 3:部署(omnistream-build-deploy)

委派 `deploy` 任务(命令见 `omnistream-build-deploy/scripts/config.ini` `task_deploy`):
- `deploy`:拷全 so(含新编译的 boostkit/libtnel)+ flink-tnel.jar 到 `<deploy_dir>/`
- `conf_parent_first`:确保 `classloader.resolve-order: parent-first`(classpath 覆盖 Flink 同名类)

### 阶段 4:测试(omnistream-expression-test)

1. 在 `flink-test/test/<expr>/` 建用例 `<expr>.csv`(覆盖**正常值/边界值/NULL/越界**)+ `<expr>.sql`(csv path `/tmp/<expr>.csv`);可参考 `omnistream-expression-test/templates/`
2. 本地驱动跑对比:`bash run_local.sh <expr>`(自动 scp 上传 + ssh 跑 native+vanilla + 取回结果;切 config.sh 去 flink-tnel.jar + `config.sh.bak` 恢复在服务端 `run_test.sh` 内完成)
3. 归一化 diff(`compare.sh`,由 `run_local.sh` 内部经 `run_test.sh` 调用)

```bash
bash .claude/skills/omnistream-expression-test/scripts/run_local.sh <expr>
# 报告: flink-test/report/<expr>/<expr>.report.md
```

### 阶段 5:报告 + 排错

- **报告**:本地 `flink-test/report/<expr>/<expr>.report.md`(welcome 计数 + native/vanilla 输出 + diff + ✅PASS/❌FAIL)
- **通过判据**:native == vanilla 逐行一致 + `welcome to native` 计数 > 0
- **排错**:
  - 未走 native(无 welcome):查 `RexNodeUtil.specialOperatorMap` / 字典 `is_support_func`/`is_supported_type` / `ValidateCalcOPStrategy`
  - `Function not supported: <name>`:注册名 ≠ `function_name`(大小写)/ 签名不匹配 / `returnType` DataTypeId 错 / VARCHAR 漏 width
  - CodeGen/JIT 失败:C 函数签名与注册不一致 / VARCHAR 三元组 / CHAR 四元组 / 字符串返回 `const char*` + `(bool* outIsNull, int32_t* outLen)` / `setExecutionContext=true` 首参 `int64_t contextPtr`
  - 结果异常:`INPUT_DATA` NULL 短路(需感知 NULL 改 `INPUT_DATA_AND_NULL*`)/ `DLLEXPORT` 导出 / 字符串内存用 Arena
  - **welcome=0 且无 "not supported" 日志(静默回退)**:多半是 Sink 类型限制 —— 看 **sql-client 日志**(`<flink_home>/log/flink-<user>-sql-client-*.log`,非 TM .log)的 `is NOT SUITABLE` + `outputTypes`;Sink 输出类型须在 `SINK_SUPPORT_DATA_TYPE`(`OmniGraphOverride.java:215`,不含 DOUBLE/BOOLEAN/CHAR)内,否则 `isSinkSupportNative=false` → `useOmniFlag=false` 整链回退。Calc 层可能支持但 print Sink 不接受 → "Calc 支持 ≠ 端到端可测"。诊断脚本用 nohup 后台跑(避免 stop-cluster/pkill 的 ssh 抖动),详见 `omnistream-expression-test` 排错章节。
  - **三层不一致(需求表/字典标"已支持"但实测回退)**:离线字典 `is_support_func`、Java `specialOperatorMap`、OmniOperator native 注册三者未必一致,需求表标注更不可信;以 native vs vanilla 实测为准。**Type D 别名映射**可复用已支持函数通路(如 IFNULL 语义≡2 参 COALESCE → `specialOperatorMap` 加 `"IFNULL"→SpecialExprType.COALESCE` 一行,复用 CoalesceExpr + batch_coalesce),OmniOperator 零改动。

## 开发检查清单

**阶段一 设计**:函数语义(参数/返回/NULL)→ row JIT vs 向量化 → Type B?→ domain → 测试用例
**阶段二 OmniAdaptor**:`RexNodeUtil` 映射 + 字典 + `ValidateCalcOPStrategy` → JSON `function_name` 与注册名一致、`returnType` 正确
**阶段三 OmniOperator**:row(`<domain>functions.{h,cpp}` + `func_registry_*.cpp`)/ 向量化(`vectorization/functions/` + `Register*.cpp`)/ Type B(jsonparser + Expr + Visitor + codegen)/ Type C(Aggregator + factory)
**阶段四 测试**:单测(`*_test.cpp`,NULL/边界/溢出)+ Flink SQL 全链路(走 native + 行/批)+ native vs vanilla 一致。单测远端构建+跑:委派 `omnistream-build-deploy` 的 `operator_test` 任务(默认开测试,`--gtest_filter` 指定用例)

## 关键约束

- **先调研后开发**(omniadaptor-vectorized-expression 步骤 1):核对函数字典语义/类型 + OmniOperator 注册类型 + 入参匹配,跳过调研属违规。
- **注册名 = function_name**(大小写敏感,char_length 反例)。
- **OmniAdaptor 决策不校验函数名**(`ValidateCalcOPStrategy` 只校验表达式结构,FUNCTION 分支不查函数支持)→ **决策通过 ≠ native 运行时支持**,必跑 native vs vanilla 测试。
- **不自动 git push**;三仓库独立,提交前确认目标仓库与分支。**只提交源码,禁止提交构建相关文件**(CLAUDE.md §6):`CMakeLists.txt`/`build.sh`/`build_scripts`/`env_check.sh`/`scripts/*.sh`/`.gitignore` 保留本地未提交(SFTP 同步远端)。
- 每条远端命令前 `source /etc/profile`;`WRITE_TO_FILE`/`FLINK_PERFORMANCE` 在 `start-cluster.sh` **之前** export。
- C++ 编译在远端 aarch64(本地 Windows 不可);改 OmniOperator 后必须 `operator_build` + `deploy` 才生效。

## 数据类型映射

| Flink SQL | Omni DataTypeId | 常量 |
|---|:---:|---|
| INT/INTEGER | 1 | `OMNI_INT` |
| BIGINT | 2 | `OMNI_LONG` |
| DOUBLE | 3 | `OMNI_DOUBLE` |
| BOOLEAN | 4 | `OMNI_BOOLEAN` |
| DECIMAL(≤18/>18) | 6/7 | `OMNI_DECIMAL64/128` |
| VARCHAR/STRING | 15 | `OMNI_VARCHAR` |
| CHAR | 16 | `OMNI_CHAR` |

完整枚举见 `OmniOperator/core/src/type/data_type.h:46`。

## 核心踩坑(提炼自记忆)

- **冲突以权威指南为准**:Type A/B/C/D 分类与两路径(row JIT codegen vs 向量化 Register)细节冲突时,以 `references/表达式开发指南.md` 为单一权威源(5 skill 共享,勿凭记忆)。
- **e2e+UT 双验证分侧**:e2e native vs vanilla 黄金对比必跑;UT 按「非平凡逻辑落在哪个仓库」分侧——C++ `VectorFunction::Apply` 直驱 / Java `RexNodeUtil.buildJsonMap` 镜像(平凡翻译不写 Java UT,靠 e2e 覆盖)。
- **三端类型 ID 错位**:Java `RexTypeToIdMap` 与 C++ `DataTypeId` 基础类型一致,复合类型(ROW/ARRAY/MAP/MULTISET)及部分 TIMESTAMP 变体数值错位;复合类型走 native 静默回退优先怀疑此错位。
- **实证 > 源码推演**:Sarg 形态矩阵/Spark-vs-Flink 语义分歧多次推翻源码推演;关键行为必 e2e 实跑,stack trace + vanilla 基线是 ground truth。
