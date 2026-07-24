# OmniOperator Remote Build

OmniOperator 远程构建与单元测试技能 —— 将本地代码同步到远程服务器，执行编译并运行单元测试。

## 功能

通过 SSH + rsync 在本地与远程服务器之间完成 OmniOperator 项目的代码同步、编译、单元测试与系统状态检查，核心能力：

- 使用 `rsync` 将本地代码增量同步到远程服务器
- 通过 SSH 在远程服务器上执行任意命令
- 一键触发 OmniOperator + Gluten 编译任务
- 一键触发 OmniOperator 全量单元测试（GTest）
- 预置系统信息查看任务（磁盘、内存、进程、网络等）
- 支持 SSH 密钥免密登录，避免明文存储密码

## 前置条件

工作目录根路径下需准备以下内容：

```
<workspace-root>/
├── OmniOperator/             ← 待同步的 OmniOperator 仓库
├── Gluten/                   ← 待同步的 Gluten 仓库（如需）
└── .agents/
    └── skills/
        └── omnioperator-remote-build/    ← 本技能
            ├── SKILL.md                  # Skill 主文件
            ├── README.md                 # 本文件
            └── scripts/
                ├── rsync_sync.sh         # 代码同步脚本
                ├── remote_exec.sh        # 远程命令执行脚本
                ├── ssh_connect.sh        # SSH 连接脚本
                ├── common.sh             # 公共函数库
                ├── config.ini            # 远程服务器配置（必填）
                ├── exclude.txt           # rsync 排除规则
                ├── compile.md            # 编译任务说明
                └── ut_test.md            # 单元测试任务说明
```

> 目录名可与 `OmniOperator`/`Gluten` 不同，但需在同步前确认 `config.ini` 中的 `source_path` 配置正确。

## 首次使用配置

`scripts/config.ini` 需要填写实际的远程服务器信息才能使用。运行任何命令前，请先引导用户完成配置。

**重要**：`config.ini` 包含密码等敏感信息，务必将其加入 `.gitignore`，避免提交到代码仓库。

```ini
[remote]
host=实际远程主机地址
user=实际用户名
password=实际密码（推荐使用 SSH 密钥代替）
port=实际SSH端口
```

推荐使用 SSH 密钥免密登录，避免在配置文件中明文存储密码：

```bash
cd scripts
./ssh_connect.sh --setup-key
```

## 可用脚本

所有脚本均位于本技能的 `scripts/` 子目录中：

| 脚本 | 说明 |
|------|------|
| [rsync_sync.sh](scripts/rsync_sync.sh) | 使用 rsync 将本地代码同步到远程服务器 |
| [remote_exec.sh](scripts/remote_exec.sh) | 通过 SSH 在远程服务器上执行命令或预定义任务 |
| [ssh_connect.sh](scripts/ssh_connect.sh) | 建立到远程服务器的 SSH 连接，支持密钥配置 |
| [common.sh](scripts/common.sh) | 公共函数库，被上述脚本共享加载 |
| [config.ini](scripts/config.ini) | 所有脚本的配置文件（首次使用前必须配置） |
| [exclude.txt](scripts/exclude.txt) | rsync 排除规则（如 `.git/`、`build/`、`*.o` 等） |
| [compile.md](scripts/compile.md) | 编译任务的具体内容与远程环境要求 |
| [ut_test.md](scripts/ut_test.md) | 单元测试任务的具体内容与远程环境要求 |

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

详细编译内容见 [compile.md](scripts/compile.md)。

### 3. 运行单元测试

```bash
cd scripts
./remote_exec.sh -t ut             # 运行预定义的单元测试任务
```

详细测试内容见 [ut_test.md](scripts/ut_test.md)。

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

以下任务定义在 `config.ini` 中，可通过 `remote_exec.sh -t <task>` 调用：

| 任务 | 说明 |
|------|------|
| `compile` | 编译 OmniOperator 和 Gluten |
| `ut` | 运行 OmniOperator 单元测试 |
| `sysinfo` | 显示系统信息（主机名、用户、时间、运行时长） |
| `diskinfo` | 显示磁盘使用情况 |
| `meminfo` | 显示内存使用情况 |
| `procinfo` | 显示进程信息（CPU 占用 Top 10） |
| `netinfo` | 显示网络监听端口 |
| `logcheck` | 查看系统日志 |
| `fullreport` | 完整系统报告（汇总所有信息） |

## 完整工作流示例

同步代码、编译并运行单元测试的端到端流程：

```bash
cd scripts

# 第一步：同步代码
./rsync_sync.sh

# 第二步：编译
./remote_exec.sh -t compile

# 第三步：运行单元测试
./remote_exec.sh -t ut
```

## 错误处理

当脚本执行失败时：
1. 检查 `config.ini` 中的连接信息是否正确
2. 使用 `./ssh_connect.sh` 测试 SSH 连接是否正常
3. 编译/测试失败时，查看输出中的错误信息并报告给用户
4. 如果是连接超时，建议用户检查网络和防火墙设置
5. 如果提示 `sshpass` 未安装，`common.sh` 会尝试自动安装（需要 `apt`/`yum`/`dnf`/`brew`）

## 注意事项

- 编译与单元测试均依赖远程服务器的硬件环境（建议鲲鹏/aarch64），本地 macOS 主机仅做调度
- 远程编译时间较长，请耐心等待
- 远程环境需提前安装 CMake、GCC、Maven 等依赖
- 单元测试二进制默认路径：`/home/omni/OmniOperator/build/core/test/omtest`
- 动态库需部署到 `$OMNI_HOME/lib`
