# Spark Remote Test MCP Server

通过 SSH 在远端集群上执行 Spark 性能测试、编译部署、正确性校验的 MCP 服务。以 stdio 方式运行，配合 Claude Code / Opencode 等 MCP 客户端使用。

## 快速开始

### 1. 安装依赖

```bash
pip install paramiko mcp
```

### 2. 配置 .mcp.json

#### Claude Code

在项目根目录的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "spark-remote-test": {
      "type": "stdio",
      "command": "python",
      "args": ["-u", "/path/to/spark-remote-mcp/server.py"],
      "env": {
        "SSH_HOST": "远端主机地址",
        "SSH_USER": "root",
        "SSH_PASSWORD": "密码",
        "REMOTE_SCRIPT": "/usr/local/Spark-Test-Tool/script/test-all.sh",
        "COMPILE_OMNI_SCRIPT": "/home/omni/compile_omni.sh",
        "COMPILE_GLUTEN_SCRIPT": "/home/omni/compile_gluten.sh"
      }
    }
  }
}
```

#### OpenCode

在项目根目录的 `opencode.json` 中添加：

```json
{
  "mcp": {
    "spark-remote-test": {
      "type": "local",
      "command": ["python3", "-u", "/path/to/spark-remote-mcp/server.py"],
      "environment": {
        "SSH_HOST": "远端主机地址",
        "SSH_USER": "root",
        "SSH_PASSWORD": "密码",
        "REMOTE_SCRIPT": "/usr/local/Spark-Test-Tool/script/test-all.sh",
        "COMPILE_OMNI_SCRIPT": "/home/omni/compile_omni.sh",
        "COMPILE_GLUTEN_SCRIPT": "/home/omni/compile_gluten.sh"
      },
      "enabled": true
    }
  }
}
```

### 3. 目录结构

```
spark-remote-mcp/
├── server.py          # MCP 服务主文件
├── mcp_client.py      # CLI 客户端（绕过 MCP 协议直接调用，见下方说明）
├── compile_logs/      # 自动生成的运行日志（编译、测试、SQL 执行）
└── flame_exports/     # 从远端拉取的火焰图 HTML（按时间戳建子目录）
```

## 工具总览

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `spark_ssh_check` | 验证 SSH 连通性 | 排查连接问题 |
| `run_spark_test_operator` | **性能测试**：执行 SQL 一次，返回端到端耗时 | Omni Before/After 性能对比 |
| `run_spark_test_all` | 执行 Native Spark 全量测试 | 原生 Spark 基准 |
| `run_e2e_sql` | **正确性校验**：用 Omni 引擎执行 SQL，返回查询结果 + 算子下推信息 | 验证优化后结果是否一致 |
| `run_e2e_sql_native` | 用原生 Spark（无 Omni/Gluten）执行 SQL | 与 Omni 结果对比 |
| `debug_e2e_sql_columnar` | **正确性调试**：逐个关闭列式算子配置并对比 Native 基线 | 定位哪个 columnar 开关让结果恢复一致或异常消失 |
| `compile_omni` | 在 Docker 容器内编译 OmniOperator + 运行 GTest UT | 验证代码可编译、UT 通过 |
| `compile_gluten` | 编译 Omni + Gluten 并部署到宿主机 | 编译新版本供性能测试 |
| `get_compile_log` | 读取最新编译/测试日志 | 查看进度或排错 |
| `fetch_spark_flame_graphs` | SFTP 拉取远端火焰图到本机 | 性能分析 |
| `read_remote_file` | 读取远端文件末尾 | 查看远端 Spark 日志 |
| `drop_cluster_caches` | 清除 Driver + Worker 的 OS page cache | 确保冷跑是真正的冷启动 |

## 工具职责区分（重要）

```
性能计时 → run_spark_test_operator（每次只跑 1 次，返回耗时）
正确性校验 → run_e2e_sql（返回查询结果行 + Omni 算子 + Fallback 告警）
列式算子定位 → debug_e2e_sql_columnar（多轮执行，逐个 SET <columnar-key>=false）
```

- **不要用 `run_e2e_sql` 做性能计时**——它的耗时包含 SHS 查询和截图，不准确
- **不要用 `run_spark_test_operator` 做正确性校验**——它不返回查询结果内容
- **不要用 `debug_e2e_sql_columnar` 做性能判断**——它是多轮调试编排，耗时只用于排错参考

## 典型工作流

### 性能对比测试

```
1. compile_gluten(omni_branch, gluten_branch)    # 编译新版本
2. drop_cluster_caches()                          # 清缓存
3. run_spark_test_operator(query_id="q7")          # 冷跑（第 1 次）
4. run_spark_test_operator(query_id="q7") × 3      # 热跑（第 2-4 次，取均值）
5. run_spark_test_operator(query_id="q7", flame_enabled=true)  # 带火焰图跑一次
6. fetch_spark_flame_graphs()                      # 拉取火焰图到本机
```

### 正确性校验

```
1. run_e2e_sql(sql="SELECT ...", database="tpcds_sf1")   # Omni 引擎执行
2. run_e2e_sql_native(sql="SELECT ...", database="tpcds_sf1")  # 原生 Spark 执行
3. 对比两者结果是否一致
```

### 列式算子定位

```
1. debug_e2e_sql_columnar(
     sql="SELECT ...",
     database="tpcds_sf1",
     toggles=[
       "spark.gluten.sql.columnar.project",
       "spark.gluten.sql.columnar.filter",
       "spark.gluten.sql.columnar.broadcastJoin"
     ],
     timeout_sec=300,
     stop_on_match=true,
     include_native_baseline=true
   )
2. 查看报告中首个 match_native=yes 或 error_recovered=yes 的配置
3. 围绕该配置对应算子继续分析物理计划和日志
```

### 编译验证

```
1. compile_omni(branch="feature_x")     # 编译 + UT，产物留在容器内
2. get_compile_log()                     # 查看日志（编译进行中也可调用）
```

### 容器内功能调试

当前统一使用 `compile_gluten` 编译 Omni + Gluten。

```
1. compile_gluten(omni_branch, gluten_branch)
2. run_e2e_sql(sql="SELECT ...", database="tpcds_sf1")
3. debug_e2e_sql_columnar(sql="SELECT ...", database="tpcds_sf1")
```

## 环境变量参考

以下环境变量供 **server.py**（MCP 服务）使用，在 `.mcp.json` 的 `env` 中配置。`mcp_client.py` 在第 10-13 行会硬编码 SSH 连接信息，不依赖这些环境变量。

### SSH 连接

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SSH_HOST` | （空） | 远端主机地址 |
| `SSH_USER` | （空） | SSH 用户名 |
| `SSH_PASSWORD` | （空） | 密码，设置后走 Paramiko；否则走系统 ssh |
| `SSH_IDENTITY` | （空） | SSH 密钥文件路径（无密码时用此方式） |
| `SSH_PORT` | （空） | SSH 端口 |
| `SSH_TIMEOUT_SECONDS` | `3600` | SSH 命令超时（秒） |

### 远端路径

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REMOTE_SCRIPT` | `/usr/local/Spark-Test-Tool/script/test-all.sh` | Native Spark 测试脚本 |
| `REMOTE_OPERATOR_DIR` | `/usr/local/Spark-Test-Tool/script` | Omni 性能测试脚本目录 |
| `REMOTE_OPERATOR_SCRIPT` | `test-all-operator.sh` | Omni 性能测试脚本文件名 |
| `REMOTE_QUERY_SQL_DIR` | `/usr/local/Spark-Test-Tool/sql/query_sql` | 远端 SQL 文件目录 |
| `REMOTE_TPCDS_QUERY_SOURCE_DIR` | `/opt/hive-testbench-hdp3/spark-queries-tpcds` | TPC-DS 标准查询集源目录 |
| `REMOTE_FLAME_DIR` | `/opt/async` | 远端火焰图 HTML 目录 |
| `HADOOP_WORKERS_FILE` | `/usr/local/hadoop/etc/hadoop/workers` | Worker 节点列表文件 |

### 本机路径

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FLAME_LOCAL_DIR` | `spark_remote_mcp/flame_exports` | 火焰图本机保存根目录 |
| `COMPILE_LOG_DIR` | `spark_remote_mcp/compile_logs` | 编译/测试日志本机目录 |
| `PROJECT_ROOT` | server.py 上两级目录 | 本地项目根目录（用于自动读取 git remote URL） |

### 编译相关

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COMPILE_OMNI_SCRIPT` | `/home/omni/compile_omni.sh` | Omni 编译脚本（接受 $1=URL $2=branch） |
| `COMPILE_GLUTEN_SCRIPT` | `/home/omni/compile_gluten.sh` | Gluten 编译脚本（接受 $1-4） |
| `COMPILE_OMNI_TIMEOUT_SECONDS` | `max(7200, SSH_TIMEOUT)` | Omni 编译超时 |
| `COMPILE_GLUTEN_TIMEOUT_SECONDS` | `max(7200, SSH_TIMEOUT)` | Gluten 编译超时 |

### E2E SQL

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `E2E_SQL_SCRIPT` | `/home/omni/run_e2e_sql.sh` | Omni E2E SQL 执行脚本 |
| `E2E_SQL_NATIVE_SCRIPT` | `/home/omni/run_e2e_sql_native.sh` | 原生 Spark SQL 执行脚本 |
| `E2E_SQL_TIMEOUT_SECONDS` | `300` | E2E SQL 超时（秒） |

### Spark History Server

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SHS_BASE_URL` | `http://<host>:18080` | Spark History Server 地址 |
| `SHS_INIT_WAIT_SECONDS` | `12` | 查 SHS 前等待秒数（SHS 每 10s 刷新 event log） |

## mcp_client.py：CLI 直接调用模式

部分 AI 编码工具对 MCP 工具调用有平台层超时限制，无法等待编译（可达 2 小时+）等长时任务完成。`mcp_client.py` 绕过 MCP stdio 协议，直接导入 `server.py` 的工具函数在本地执行，不受平台超时约束。

### 使用方式

```bash
cd spark-remote-mcp

# 查看所有可用工具
python mcp_client.py

# SSH 连通性检查
python mcp_client.py spark_ssh_check

# 编译 Omni（传入仓库 URL 和分支）
python mcp_client.py compile_omni <git_repo_url> <branch>

# 编译 Gluten
python mcp_client.py compile_gluten <omni_url> <omni_branch> <gluten_url> <gluten_branch>

# 执行 E2E SQL（从文件读取 SQL）
python mcp_client.py run_e2e_sql test.sql [database] [timeout_sec]
python mcp_client.py run_e2e_sql_native test.sql [database] [timeout_sec]

# 调试列式算子开关（toggles 为空时使用默认列表）
python mcp_client.py debug_e2e_sql_columnar test.sql [database] [timeout_sec] [toggle1,toggle2,...] [stop_on_match] [include_native_baseline]

# 性能测试（传 query_id 或 SQL 文件路径）
python mcp_client.py run_spark_test_operator q7           # 用 TPC-DS q7
python mcp_client.py run_spark_test_operator q7 true      # 开启火焰图

# Native Spark 全量测试
python mcp_client.py run_spark_test_all [sql_file]

# 拉取火焰图
python mcp_client.py fetch_spark_flame_graphs [remote_dir] [session_folder] [max_files]

# 清集群缓存
python mcp_client.py drop_cluster_caches

# 查看编译日志
python mcp_client.py get_compile_log [tail_lines]

# 读取远端文件
python mcp_client.py read_remote_file <remote_path> [tail_lines]
```

### 注意事项

- `mcp_client.py` 内部硬编码了 SSH 连接信息（第 10-13 行），使用前需确认指向正确的服务器

## 关于 PROJECT_ROOT

`compile_omni` 和 `compile_gluten` 支持省略 `git_repo_url` 参数，此时会自动从 `PROJECT_ROOT` 下的本地仓库读取 git remote URL：

```
PROJECT_ROOT/
├── OmniOperator/   ← git remote get-url origin → Omni 仓库 URL
├── Gluten/         ← git remote get-url origin → Gluten 仓库 URL
└── spark-remote-mcp/
    └── server.py
```

如果目录布局不符合上述结构，可设置 `PROJECT_ROOT` 环境变量，或在调用时显式传入 `git_repo_url`。

## SSH 认证方式

两种方式二选一：

1. **密码认证**：设置 `SSH_PASSWORD`，内部使用 Paramiko 连接
2. **密钥认证**：设置 `SSH_IDENTITY` 指向私钥文件，不设置密码时走系统 `ssh` 命令

拉取火焰图（SFTP）始终使用 Paramiko，无密码时必须配置 `SSH_IDENTITY`。

## 日志说明

所有编译和测试操作的输出会实时写入 `compile_logs/` 目录，例如：

```
compile_logs/
├── compile_omni_20260529-180834.log    # Omni 编译日志
├── compile_gluten_20260529-181908.log  # Gluten 编译日志
├── perf_omni_20260529-182933.log       # Omni 性能测试日志
├── perf_native_20260529-183000.log     # Native Spark 测试日志
├── e2e_sql_20260529-182403.log         # E2E SQL 执行日志
└── latest.log                          # 指向最新日志文件路径
```

- 编译进行中可随时调用 `get_compile_log` 查看当前进度
- `latest.log` 是一个文本指针文件，内容为最新日志的完整路径

## 火焰图说明

`fetch_spark_flame_graphs` 通过 SFTP 将远端的 async-profiler HTML 文件下载到本机：

- 默认远端目录：`REMOTE_FLAME_DIR`（`/opt/async`）
- 如果目录下没有 HTML，会自动选择最近修改且包含 HTML 的子目录
- 本机按时间戳建子目录保存，返回 `file://` 链接可直接在浏览器打开
