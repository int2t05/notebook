# Velox Remote Test MCP Server

通过 SSH 在远端主机上编译 Velox / Gluten+Velox、执行正确性校验与性能测试的 MCP 服务。以 stdio 方式运行，配合 Claude Code / OpenCode 等 MCP 客户端使用。与 `spark-remote-mcp` 同源，工具面向 Velox / Gluten+Velox 后端。

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
    "velox-remote-test": {
      "type": "stdio",
      "command": "python",
      "args": ["-u", "/path/to/velox-remote-mcp/server.py"],
      "env": {
        "SSH_HOST": "远端主机地址",
        "SSH_USER": "root",
        "SSH_PASSWORD": "密码",
        "REMOTE_WORKDIR": "/path/to/incubator-gluten/dev",
        "E2E_VELOX_SCRIPT": "/path/to/run_exec_velox.sh"
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
    "velox-remote-test": {
      "type": "local",
      "command": ["python3", "-u", "/path/to/velox-remote-mcp/server.py"],
      "environment": {
        "SSH_HOST": "远端主机地址",
        "SSH_USER": "root",
        "SSH_PASSWORD": "密码",
        "REMOTE_WORKDIR": "/path/to/incubator-gluten/dev",
        "E2E_VELOX_SCRIPT": "/path/to/run_exec_velox.sh"
      },
      "enabled": true
    }
  }
}
```

> 连接信息一律从环境变量读取，**请勿在源码中硬编码服务器地址或密码**。`mcp_client.py` 也读取同一批环境变量（见下方「CLI 直接调用模式」）。

### 3. 目录结构

```
velox-remote-mcp/
├── server.py          # MCP 服务主文件
├── mcp_client.py      # CLI 客户端（绕过 MCP 协议直接调用，见下方说明）
├── compile_logs/      # 自动生成的运行日志（编译、UT、SQL、性能测试）
├── tpcds_results/     # run_tpcds_99_velox 按 run_label 落盘的逐 query 结果
└── flame_exports/     # 从远端拉取的火焰图 HTML（按时间戳建子目录）
```

## 工具总览

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `velox_ssh_check` | 验证 SSH 连通性 | 排查连接问题 |
| `compile_velox` | 在远端执行 `compile_velox.sh <url> <branch>`，仅编译 Velox | 验证 Velox 可编译 |
| `compile_gluten_velox` | 执行 `compile_gluten_velox.sh <url> <branch>`，编译 Velox + Gluten 集成版本 | 编译新版本供测试 |
| `run_velox_ut` | 在 `REMOTE_VELOX_HOME` 下跑 Velox CTest UT | 验证 UT 通过 |
| `run_e2e_sql_velox` | **正确性校验**：用 Gluten+Velox 后端执行 SQL，返回查询结果 | 验证优化后结果一致 |
| `run_tpcds_99_velox` | 跑 TPC-DS 99 条查询，逐 query 落盘到 `tpcds_results/<label>/` | 批量回归 |
| `diff_tpcds_results` | 字面对比两次 `run_tpcds_99_velox` 的结果 | 找出差异 query |
| `run_velox_perf_test` | **性能测试**：执行 SQL 返回端到端耗时 | Before/After 性能对比 |
| `fetch_velox_flame_graphs` | SFTP 拉取远端火焰图到本机 | 性能分析 |
| `run_velox_perf_and_fetch_flames` | 性能测试 + 自动拉取火焰图 | 一步出耗时与火焰图 |
| `get_compile_log` | 读取最新编译/测试日志末尾 | 查看进度或排错 |
| `read_remote_file` | 读取远端文件末尾 | 查看远端日志 |
| `drop_cluster_caches` | 清除 Driver + Worker 的 OS page cache | 确保冷跑是真正的冷启动 |

## 工具职责区分（重要）

```
性能计时 → run_velox_perf_test（返回端到端耗时）
正确性校验 → run_e2e_sql_velox（返回查询结果行）
```

- **不要用 `run_e2e_sql_velox` 做性能计时**——它的耗时不纯粹，不准确
- **不要用 `run_velox_perf_test` 做正确性校验**——它不返回查询结果内容

## 典型工作流

### 性能对比测试

```
1. compile_gluten_velox(git_repo_url, branch)     # 编译新版本
2. drop_cluster_caches()                           # 清缓存
3. run_velox_perf_test(query_id="q7")              # 冷跑（第 1 次）
4. run_velox_perf_test(query_id="q7") × 3          # 热跑（第 2-4 次，取均值）
5. run_velox_perf_and_fetch_flames(query_id="q7")  # 带火焰图跑一次并拉回本机
```

### 正确性校验

```
1. run_e2e_sql_velox(sql="SELECT ...", database="tpcds_sf1")   # Gluten+Velox 执行
2. 与基准结果对比是否一致
```

### TPC-DS 99 回归对比

```
1. run_tpcds_99_velox(run_label="baseline")    # 基线
2. （切换到新分支编译后）run_tpcds_99_velox(run_label="modified")
3. diff_tpcds_results("baseline", "modified")  # 字面对比差异
```

### 编译验证

```
1. compile_velox(git_repo_url, branch)   # 仅编译 Velox
2. get_compile_log()                      # 查看日志（编译进行中也可调用）
3. run_velox_ut()                         # 跑 CTest UT
```

## 环境变量参考

以下环境变量供 **server.py**（MCP 服务）使用，在 `.mcp.json` 的 `env` 中配置。`mcp_client.py` 同样读取这些环境变量。所有默认值均为 `/path/to/...` 占位符，**不含任何真实主机或密码**。

### SSH 连接

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SSH_HOST` | （空） | 远端主机地址 |
| `SSH_USER` | `root` | SSH 用户名 |
| `SSH_PASSWORD` | （空） | 密码，设置后走 Paramiko；否则走系统 ssh |
| `SSH_IDENTITY` | （空） | SSH 密钥文件路径（无密码时用此方式） |
| `SSH_PORT` | `22` | SSH 端口 |
| `SSH_TIMEOUT_SECONDS` | `3600` | SSH 命令超时（秒） |
| `SSH_CHECK_TIMEOUT` | `30` | `velox_ssh_check` 超时（秒） |

### 远端路径

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REMOTE_WORKDIR` | `/path/to/incubator-gluten/dev` | 远端编译脚本所在目录 |
| `COMPILE_VELOX_SCRIPT` | `compile_velox.sh` | Velox 编译脚本（相对 `REMOTE_WORKDIR`，也可绝对路径） |
| `COMPILE_GLUTEN_VELOX_SCRIPT` | `compile_gluten_velox.sh` | Velox+Gluten 编译脚本 |
| `REMOTE_VELOX_HOME` | `/path/to/incubator-gluten/ep/build-velox/build/velox_ep` | Velox 源码/构建根目录（跑 UT 用） |
| `VELOX_COMPILE_CONFIG` | `/path/to/incubator-gluten/dev/velox_compile_config.sh` | 编译配置脚本 |
| `VELOX_UT_BUILD_DIR` | `_build/release` | CTest 构建目录（相对 `REMOTE_VELOX_HOME`） |
| `E2E_VELOX_SCRIPT` | `/path/to/run_exec_velox.sh` | 远端 spark-sql 启动脚本（SQL 从 stdin 喂入） |
| `REMOTE_TPCDS_QUERY_DIR` | `/path/to/spark-queries-tpcds` | 远端 TPC-DS 标准查询集目录 |
| `REMOTE_PERF_SCRIPT_DIR` | `/path/to/spark-test-tool/script` | 性能测试脚本目录 |
| `REMOTE_PERF_SCRIPT` | `test-all-velox-1t.sh` | 性能测试脚本文件名 |
| `REMOTE_PERF_QUERY_SQL_DIR` | `/path/to/spark-test-tool/sql/query_sql` | 性能测试 SQL 目录 |
| `REMOTE_PERF_LOGS_DIR` | `/path/to/spark-test-tool/logs` | 远端性能测试日志目录 |
| `REMOTE_PERF_DB` | `tpcds` | 性能测试默认数据库 |
| `REMOTE_FLAME_DIR` | `/tmp/flame_graphs` | 远端火焰图 HTML 目录 |
| `HADOOP_WORKERS_FILE` | `/path/to/hadoop/etc/hadoop/workers` | Worker 节点列表文件 |

### 本机路径

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COMPILE_LOG_DIR` | `velox_remote_mcp/compile_logs` | 编译/测试日志本机目录 |
| `TPCDS_RESULTS_DIR` | `velox_remote_mcp/tpcds_results` | TPC-DS 99 结果本机目录 |
| `FLAME_LOCAL_DIR` | `velox_remote_mcp/flame_exports` | 火焰图本机保存根目录 |

### 超时（秒）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COMPILE_VELOX_TIMEOUT_SECONDS` | `max(7200, SSH_TIMEOUT)` | Velox 编译超时 |
| `COMPILE_GLUTEN_VELOX_TIMEOUT_SECONDS` | `max(7200, SSH_TIMEOUT)` | Velox+Gluten 编译超时 |
| `E2E_VELOX_TIMEOUT_SECONDS` | 由调用方决定，最低 `600` | E2E SQL 超时 |
| `TPCDS_99_TIMEOUT_SECONDS` | （由调用方/默认决定） | TPC-DS 99 超时 |
| `PERF_VELOX_TIMEOUT_SECONDS` | `SSH_TIMEOUT`（默认 3600） | 性能测试超时 |

## mcp_client.py：CLI 直接调用模式

部分 AI 编码工具对 MCP 工具调用有平台层超时限制，无法等待编译（可达 2 小时+）等长时任务完成。`mcp_client.py` 绕过 MCP stdio 协议，直接导入 `server.py` 的工具函数在本地执行，不受平台超时约束。

> 与 spark 版不同，本 `mcp_client.py` **不硬编码任何连接信息**，运行前需先在 shell / `.env` 中设置 `SSH_HOST`、`SSH_USER`、`SSH_PASSWORD`（或 `SSH_IDENTITY`）等环境变量；未设置 `SSH_HOST` 时会打印告警。

### 使用方式

```bash
cd velox-remote-mcp

# 设置连接信息（PowerShell 示例）
#   $env:SSH_HOST='<host>'; $env:SSH_USER='<user>'; $env:SSH_PASSWORD='<password>'

# 查看所有可用工具
python mcp_client.py

# SSH 连通性检查
python mcp_client.py velox_ssh_check

# 编译 Velox / Velox+Gluten（传入仓库 URL 和分支）
python mcp_client.py compile_velox <git_repo_url> <branch>
python mcp_client.py compile_gluten_velox <git_repo_url> <branch>

# 跑 Velox CTest UT
python mcp_client.py run_velox_ut [build_dir] [test_regex] [timeout_sec]

# 执行 E2E SQL（从文件读取，或用 '-' 从 stdin 读取）
python mcp_client.py run_e2e_sql_velox test.sql [database] [timeout_sec]

# TPC-DS 99 回归与对比
python mcp_client.py run_tpcds_99_velox <run_label> [database] [sql_dir] [timeout_sec]
python mcp_client.py diff_tpcds_results <label_a> <label_b>

# 性能测试 / 性能测试 + 拉火焰图
python mcp_client.py run_velox_perf_test [query_id] [query_sql]
python mcp_client.py run_velox_perf_and_fetch_flames [query_id] [query_sql]

# 拉取火焰图
python mcp_client.py fetch_velox_flame_graphs [remote_dir] [session_folder_name]

# 清集群缓存
python mcp_client.py drop_cluster_caches

# 查看编译日志 / 读取远端文件
python mcp_client.py get_compile_log [tail_lines]
python mcp_client.py read_remote_file <remote_path> [tail_lines]
```

## SSH 认证方式

两种方式二选一：

1. **密码认证**：设置 `SSH_PASSWORD`，内部使用 Paramiko 连接
2. **密钥认证**：设置 `SSH_IDENTITY` 指向私钥文件，不设置密码时走系统 `ssh` 命令

拉取火焰图（SFTP）始终使用 Paramiko，无密码时必须配置 `SSH_IDENTITY`。

## 日志说明

所有编译和测试操作的输出会实时写入 `compile_logs/` 目录，例如：

```
compile_logs/
├── compile_velox_20260529-180834.log          # Velox 编译日志
├── compile_gluten_velox_20260529-181908.log   # Velox+Gluten 编译日志
├── tpcds99_<label>_...log                      # TPC-DS 99 日志
├── e2e_sql_...log                              # E2E SQL 执行日志
└── latest.log                                  # 指向最新日志文件路径
```

- 编译进行中可随时调用 `get_compile_log` 查看当前进度
- `latest.log` 是一个文本指针文件，内容为最新日志的完整路径

## 火焰图说明

`fetch_velox_flame_graphs` / `run_velox_perf_and_fetch_flames` 通过 SFTP 将远端的 async-profiler HTML 文件下载到本机：

- 默认远端目录：`REMOTE_FLAME_DIR`（`/tmp/flame_graphs`）
- 如果目录下没有 HTML，会自动选择最近修改且包含 HTML 的子目录
- 本机按时间戳建子目录保存，返回 `file://` 链接可直接在浏览器打开
