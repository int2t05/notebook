---
name: "omnistream-dev-audit"
description: "OmniStream/OmniAdaptor/OmniOperator 改源码后声称完成/commit/push 前必跑的项目特有踩坑审计 checklist。触发:开发任务声称完成前、push 前、PR 提交/re-request review 前。症状:构建成功但改动没生效、welcome=0 native 没使能、new 不 delete、catch 丢 e.what、switch default 缺 throw 静默吞异常、误改 sibling、误提交构建文件。2026-07-24 由 EXISTS review 修复复盘提炼,三仓库源码规范逐仓库核对。"
---

# OmniStream 开发完成审计 skill

每次改源码后**声称完成 / commit / push 前**强制过一遍本项目特有踩坑 checklist。构建成功 ≠ 改动生效 ≠ 部署正确 ≠ 行为正确——本 skill 是"我觉得搞定了"前的最后一道闸。

> 这些点都是**真实踩过/源码实证的**(非臆想),逐条核对,任一不过则未完成。

## 触发场景

- 改了 C++/Java 源码,准备声称"完成"/"已修复"。
- commit / push 前;PR 提交 / re-request review 前。

## 审计 checklist

### A. 资源所有权 & 内存安全

- [ ] 每个 `new` 有对应 `delete`。**OmniStream**:open()/ctor 里 `new` 的 state-view/keySelector 裸指针成员,派生析构负责 delete+`=nullptr`(仿 `StreamingSemiAntiJoinOperator` 析构,**不仿** `StreamingJoinOperator` 只 LOG 不 delete=泄漏);base ptr delete 派生对象前确认基类 `virtual ~`。**OmniOperator**:Expr 树 raw `Expr*`,新 Expr 子类析构必须 delete 子节点(仿 `IsNullExpr::~IsNullExpr{delete value;}`、`BinaryExpr{delete left;delete right;}`、`FuncExpr{DeleteExprs(arguments);}`);`LiteralExpr::stringVal` 等成员析构 delete。
- [ ] 裸指针成员 `= nullptr` 初始化(open()/ctor 中途抛异常时析构 delete 未初始化 = UB)。
- [ ] **leak-on-throw**:allocation 后有 throw 路径(`default: throw`、catch/rethrow、下游调用抛异常)→ `unique_ptr`/RAII 或 try-catch+delete(OmniStream `buildOutput*`/`processBatch*` 用 unique_ptr;OmniOperator `AlignedBuffer` 用 unique_ptr)。
- [ ] 优先 `unique_ptr`/`make_unique`(局部拥有态)、`shared_ptr`(OmniOperator `VectorFunction`/`DataTypePtr`/`FunctionSignature`)。**sibling 同款技术债仅修本任务算子,不扩范围**(surgical),PR 描述/memory mention。

### B. 异常诊断 & 类型

- [ ] catch + rethrow **保 `e.what()`**:`throw std::runtime_error(std::string("...") + e.what())`。OmniStream `StreamingJoinOperator`/`AbstractStreamingJoinOperator::open` 既有 catch 丢 e.what() 技术债,新代码勿复刻。
- [ ] **switch default 必须有 `throw`**:`default: throw std::runtime_error("DataType not supported yet!");`——**`default: std::runtime_error("...");`(无 `throw`)= 临时对象丢弃、静默吞异常**(OmniStream `StreamingJoinOperator.cpp` 4 处既有 bug,勿引入新例)。
- [ ] 异常类型按仓库:**OmniStream** `throw std::runtime_error`(校验)/`NOT_IMPL_EXCEPTION`(未实现)/`THROW_LOGIC_EXCEPTION("...")`(type dispatch default);**OmniOperator** `throw OmniException("OPERATOR_RUNTIME_ERROR","msg")`(表达式层)/`OMNI_THROW("cat","msg")`(函数层);**OmniAdaptor Java** `LOG.warn` 后回退(勿抛 checked 异常破坏 Flink 签名)。
- [ ] **OmniAdaptor 回退语义陷阱**:`validateNodeForOmniTask` 返回 `true`=不支持→回退、`false`=OK(反直觉);回退时 `validateVertexForOmniTask` 调 `setUseOmniEnabled(false)` 保留 Flink 原生 invokable class。

### C. 构建产物是否真正含改动(构建成功 ≠ 改动生效)

- [ ] **strings 验证**(definitive):`strings <build>/jni/libtnel.so | grep <我的独有串>`(如新异常消息)——改动是否真链进 .so。
- [ ] **.o mtime**:我的源文件对应 .o mtime 是否刷新(不是几天前)= 是否真重编。
- [ ] **`make -n` dry run**:`make -n tnel | grep <我的文件>` —— make 是否当它是 build target。
- [ ] **cmake GLOB 陷阱**:`table/CMakeLists.txt` 等用 `file(GLOB_RECURSE)` **无 `CONFIGURE_DEPENDS`** → `git reset`/切分支/增删源文件后,`make` 触发的 reconfigure **不重扫 GLOB**,文件可能从 build targets 掉落(`build.make` 0 refs、.o 旧 mtime、strings 无我的串)。修:手动 `cmake ..` 重 GLOB + `make tnel`。
- [ ] **禁止并发 make**:kill 本地 ssh **不杀远端 make**;重构建前 `ps -ef | grep -E "make tnel|cc1plus"` 查残留,等结束或杀干净再跑。

### D. 部署产物是否 stale(部署 ≠ 源码)

- [ ] 改源码后,部署的 jar/.so 是否从**最新源码**重编?源码有未提交改动时尤其警惕。
- [ ] **jar 内容验证**:`unzip -p <jar> <class-path> | strings | grep <预期串>`(如 `ValidateJoinOPStrategy.class` 里 `LeftSemiJoin`)。
- [ ] 知道类在哪个 jar:`ValidateJoinOPStrategy`/`OmniGraphOverride` 在 **flink-tnel.jar**(java 模块);`StreamExecJoin` 在 **omni-table-planer.jar**。改 OmniAdaptor 后两 jar 都 `adaptor_incr` 重编 + redeploy。
- [ ] **stale 部署症状**:native 静默回退——`welcome 0->0`(`TNELLibrary_initialize` 已调=lib 加载,但无 OmniTask=决策 NOT SUITABLE),无异常。先查部署 jar 是否含白名单/决策类。

### E. e2e 回归(native vs vanilla)

- [ ] 改算子/表达式后跑 e2e 黄金对比(`omnistream-expression-test` 或专用 harness,如 `test/exists/run_exists.sh`+`run_batch.sh`)。
- [ ] **welcome 0→N** 确认 native 真使能;welcome 0 = 没使能(查 D 节)。
- [ ] **operator close 路径**:e2e 作业跑完会 close+析构算子——catch double-free/crash(查 TM .out:Segmentation/core dumped/exception)。
- [ ] 归一化逐行一致(native==vanilla)才 PASS。

### F. 代码规范(三仓库实际惯例,逐仓库核对)

**只改本任务相关**,不顺手重构 sibling/相邻代码(CLAUDE.md §3);既有 dead code mention 不删。**只提交源码**:CMakeLists.txt/build.sh/build_scripts/.gitignore 等构建配置不进 commit。

| 仓库 | 文件头 | 注释 | 命名 | 关键惯例/陷阱 |
|---|---|---|---|---|
| **OmniStream C++** | 全 Mulan PSL v2 块;新文件块后加 `// Description: <一句>` | **仅英文**、`//`、≤2 行、稀疏、解释 why 不复述字面 | CamelCase 类、`this->` 前缀、无 `_` 后缀;新文件 `#pragma once`(旧 `#ifndef`) | `.cpp` 顶部 `template class Foo<RowData*>; template class Foo<long>;` 显式实例化;`override` + `virtual ~`;`nullptr` over NULL;SVE intrinsics 内联在算子内不抽象 |
| **OmniAdaptor Java** | 自有代码 Mulan PSL v2;**Flink 覆盖类(`org/apache/flink/`)保留 Apache 2.0 头 + 追加 Huawei 修改行** `* We modify this part...based on Apache Flink...` | **中英混合允许**(中文 OK,非英文强制);Javadoc 稀疏 | PascalCase 类(缩写大写如 `OP`)、camelCase 方法、`UPPER_SNAKE_CASE` static final | **Flink 覆盖类保持 `@Internal` + public 签名 verbatim**(回退兼容,只加 private 方法 + `// omnistream used` 块);**禁止直 `import com.google.common.*`**(Flink shaded,用 `commons-lang3` Pair 或 `org.apache.flink.shaded.guava30.*`);新算子→`SUPPORT_OP_NAME` + `ValidateOperatorStrategyFactory` map **双注册**;新 join 类型→`SUPPORT_JOIN_TYPE`;`ReflectionUtils.retrievePrivateField` 读 Flink 私有字段;SLF4J `LOG.info` trace / `LOG.warn` 回退前 / `LOG.error` 不可能态 |
| **OmniOperator C++** | **两版**:表达式层(`expressions.*`)全 Mulan 块;函数/测试/注册(`*Function.{h,cpp}`、`*Test.cpp`、`Register*.cpp`)短版 `Copyright + Description: <一句>`(**勿 copy-paste 占位**,如 `Description: visitor class for expressions` 实非 visitor) | 英文、`//`;**`Register*.cpp` 多行 `//` 语义说明块常见**(超 2 行可接受) | Expr 类后缀 `Expr`、VectorFunction/SimpleFunction 后缀 `Function`;`supportVectorized()`(非 supportVectorization);`class ... final` | **SimpleFunction**(`RegisterFunction<F,Ret,Args...>(name,{types},ret)`,struct `ALWAYS_INLINE call`)vs **VectorFunction**(`RegisterVectorFunction(name,{types},ret,make_shared<...>())`,override `Apply`);`supportVectorized()` inline in .h、`compute/Apply` in .cpp;**字符串函数注册 VARCHAR+CHAR 两组合**(无 OMNI_STRING,C++ 侧 STRING 归一为 VARCHAR);测试 `TEST`(非 TEST_F)、真实数据(禁 mock)、末尾手动 `delete`、必测 NULL;函数注册名大小写敏感混合(`lower`/`LIKE`/`Md5`,跟 Spark/Flink 原名不归一) |

### G. git 卫生

- [ ] push 到 fork(origin),**不 push upstream**(除非用户明确确认)。
- [ ] review 修复折叠用 `commit --amend` + `push --force-with-lease`(干净单 commit PR;--force-with-lease 比 --force 安全)。
- [ ] `git add` 显式选源码文件,**不 `git add .`/`-A`**。
- [ ] commit 前确认目标仓库 + 分支(三仓库独立)。

## 红旗(STOP,未完成)

- "构建成功了" → 没 strings 验证改动是否链进 .so(C)。
- "e2e 跑通了" 但 welcome=0 → 跑的是 vanilla,native 没使能(D/E)。
- "我改了 .cpp" 但 .o mtime 没变 → cmake GLOB 掉了 / make 没重编(C)。
- `default: std::runtime_error("...");`(无 throw)→ 静默吞异常,改回 `throw std::runtime_error(...)`(B)。
- "catch 改成跟 sibling 一样(固定字符串丢 e.what())" → 诊断丢失,改回保 e.what()(B)。
- OmniAdaptor 直 `import com.google.common.*` → Flink shaded,换 commons-lang3 / shaded 路径(F)。
- OmniAdaptor 覆盖类改了 public 签名 → 回退兼容破坏,还原 verbatim(F)。
- OmniOperator 字符串函数只注册 VARCHAR 没注册 CHAR → 带 CHAR 字面量 vectorFunction=NULL→SIGSEGV(F)。
- OmniOperator `Description:` copy-paste 占位(与文件实际内容不符)→ 改成真实描述(F)。
- "sibling 也有这问题,一起修了" → 超范围,回退(A/F)。
- `git add .` → 可能误提交 CMakeLists.txt/.gitignore(G)。

## 真实踩坑(本 skill 来源,2026-07-24 EXISTS review 修复)

- **review 5 findings**:析构泄漏 state view 裸指针 + catch 丢 e.what() + leak-on-throw。全修(unique_ptr RAII + nullptr init + delete + e.what());sibling `StreamingJoinOperator` 同款技术债未动(超范围)。
- **构建假成功**:`make tnel` 后 libtnel.so 重链但 strings 无我的串——cmake GLOB 无 CONFIGURE_DEPENDS,`git reset` 后文件从 build.make 掉落。手动 `cmake ..` 重 GLOB 才真编进去。
- **部署 stale**:`welcome 0->0`——部署的 flink-tnel.jar 旧版无 LeftSemiJoin 白名单,源码有白名单但 jar 没重编。`adaptor_incr` 重编 + redeploy 才使能。
- **远端 make 残留**:kill 本地 ssh 后远端 make 还在跑,差点并发 make 互踩。

## 关联

- 构建部署:[[omnistream-build-deploy]] skill;表达式 e2e:[[omnistream-expression-test]] skill;表达式开发权威指南:[[expression-dev-guide-authoritative]] memory。
- 任务收尾清理+复盘:[[task-cleanup-retrospective-convention]] memory(CLAUDE.md §6)——本 skill 是"声称完成前"代码审计,与"任务结束后"清理复盘互补。
- 外科手术式改动:CLAUDE.md §3;注释规范:CLAUDE.md §7。
