---
name: "omnioperator-remote-build"
description: "将本地代码同步到远程服务器，编译并运行单元测试。当用户想要同步代码、编译或运行远程服务器上的单元测试时调用。Triggers on: sync, build, compile, run tests, remote execute, deploy to server, push code to remote, rsync, 远程编译, 同步代码, 单元测试, UT, 编译. Also use when the user mentions running commands on a remote machine or asks about the status of a remote build."
---

# 远程构建技能

本技能帮助你将本地代码同步到远程服务器、编译项目并运行单元测试。

## 首次使用配置

`scripts/config.ini` 需要填写实际的远程服务器信息才能使用。运行任何命令前，请先引导用户完成配置：

**重要**：`config.ini` 包含密码等敏感信息，务必将其添加到 `.gitignore`，避免提交到代码仓库。

```ini
[remote]
host=实际远程主机地址
user=实际用户名
password=实际密码（推荐使用SSH密钥代替）
port=实际SSH端口
```

推荐使用 SSH 密钥免密登录，避免在配置文件中明文存储密码：

```bash
cd scripts
./ssh_connect.sh --setup-key
```

## 适用场景

在以下情况下调用本技能：
- 用户想要将本地代码同步到远程服务器
- 用户想要在远程服务器上编译代码
- 用户想要在远程服务器上运行单元测试
- 用户提到与远程服务器相关的"同步"、"编译"、"UT"、"单元测试"、"sync"、"build"、"compile"、"deploy" 等操作
- 用户想要检查远程服务器的系统状态（磁盘、内存、进程等）

## 可用脚本

所有脚本均位于本技能的 `scripts/` 子目录中：

| 脚本 | 说明 |
|------|------|
| [rsync_sync.sh](scripts/rsync_sync.sh) | 使用 rsync 将本地代码同步到远程服务器 |
| [remote_exec.sh](scripts/remote_exec.sh) | 通过 SSH 在远程服务器上执行命令 |
| [ssh_connect.sh](scripts/ssh_connect.sh) | 建立到远程服务器的 SSH 连接 |
| [config.ini](scripts/config.ini) | 所有脚本的配置文件（首次使用前必须配置） |

## 常用工作流

### 1. 同步代码到远程服务器

```bash
cd scripts
./rsync_sync.sh                    # 使用默认配置
./rsync_sync.sh -n -v              # 试运行并显示详细信息
./rsync_sync.sh -d                 # 删除远程端多余文件
```

### 2. 在远程服务器上编译

```bash
cd scripts
./remote_exec.sh -t compile        # 运行预定义的编译任务
```

### 3. 运行单元测试

```bash
cd scripts
./remote_exec.sh -t ut             # 运行预定义的单元测试任务
```

### 4. 执行自定义命令

```bash
cd scripts
./remote_exec.sh 'ls -la /home/omni'
./remote_exec.sh -t sysinfo        # 运行预定义任务
./remote_exec.sh --list-tasks      # 列出所有可用任务
```

### 5. SSH 连接

```bash
cd scripts
./ssh_connect.sh                   # 使用默认配置连接
./ssh_connect.sh --setup-key       # 配置 SSH 密钥以实现免密登录
```

## 预定义任务

以下任务定义在 `config.ini` 中：

| 任务 | 说明 |
|------|------|
| `compile` | 编译 OmniOperator 和 Gluten |
| `ut` | 运行 OmniOperator 单元测试 |
| `sysinfo` | 显示系统信息 |
| `diskinfo` | 显示磁盘使用情况 |
| `meminfo` | 显示内存使用情况 |
| `procinfo` | 显示进程信息 |
| `netinfo` | 显示网络信息 |
| `logcheck` | 查看系统日志 |
| `fullreport` | 完整系统报告（汇总所有信息） |

## 错误处理

当脚本执行失败时：
1. 检查 `config.ini` 中的连接信息是否正确
2. 使用 `./ssh_connect.sh` 测试 SSH 连接是否正常
3. 编译/测试失败时，查看输出中的错误信息并报告给用户
4. 如果是连接超时，建议用户检查网络和防火墙设置

## 完整工作流示例

同步代码、编译并运行单元测试的完整流程：

```bash
cd scripts

# 第一步：同步代码
./rsync_sync.sh

# 第二步：编译
./remote_exec.sh -t compile

# 第三步：运行单元测试
./remote_exec.sh -t ut
```
