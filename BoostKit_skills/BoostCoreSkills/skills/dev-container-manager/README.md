# dev-container-manager 远程开发容器管理

`dev-container-manager` 用于在远程 Linux 服务器上创建、查询和删除 Docker 开发容器，支持 NUMA 感知资源分配和多用户共存。

`dev-container-manager` manages the full lifecycle of Docker-based dev containers on remote Linux servers, with NUMA-aware resource allocation and multi-user coexistence support.

## 核心能力

- **远程资源检测**：自动采集服务器 CPU 拓扑（NUMA 节点、核心列表、空闲核心）、内存、已有容器和端口占用
- **NUMA 感知分配**：确保分配连续 CPU 核心在同一 NUMA 节点内，避免跨 socket 延迟
- **环境预检**：自动检测 Docker Hub 可达性、registry mirror 配置、磁盘空间（阈值 128GB），必要时自动配置镜像加速器或建议数据目录迁移
- **完整容器生命周期**：拉取镜像 → 创建容器 → 安装 openssh-server + 开发工具 → 注入 SSH 公钥 → 提交镜像 → 重建（含 sshd 自启动）
- **多用户安全共存**：按用户名命名容器/镜像/密钥文件，CPU 范围不重叠，端口自动分配
- **密钥管理**：本地生成 ed25519 密钥对，密码认证禁用，仅密钥登录

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill dev-container-manager -g -y
```

### 创建开发容器

在 AI Agent 中直接描述需求：

```
帮我在 192.168.1.100 上创建一个 16 核 32G 内存的开发容器
查看 192.168.1.100 上的所有开发容器
删除 zhangsan 的开发容器
```

Skill 会自动完成环境预检 → 资源检测 → 分配 → 创建全流程。

### 连接容器

创建完成后会输出连接信息：

```
ssh -i "$(pwd)/dev_container_<username>_key" -p <port> root@<server>
```

## 工作流程

```
用户需求 → 环境预检 (Docker Hub / 磁盘 / Mirror)
         → 资源检测 (CPU/NUMA/内存/端口/已有容器)
         → NUMA 感知资源分配
         → 生成 SSH 密钥
         → 创建容器 (拉取镜像/安装工具/注入公钥/提交/重建)
         → 输出连接信息
```

## 脚本清单

| 脚本 | 用途 | 运行位置 |
|------|------|----------|
| `env_precheck.sh` | Docker Hub 可达性、mirror 配置、磁盘空间检查 | 远程 |
| `check_resources.sh` | CPU/NUMA/内存/端口/已有容器信息采集 | 远程 |
| `create_container.sh` | 完整创建流程（拉取、安装、配置、提交、重建） | 远程 |
| `list_containers.sh` | 列出所有 dev_container 及资源总览 | 远程 |

## 在 AI Agent 工具中使用

### Claude Code

当你提到远程开发容器、NUMA、服务器资源分配时，Skill 会自动激活：

```
在 10.0.0.5 上创建一个 32 核 64G 的开发容器
查看我的开发容器
删除 dev_container_zhangsan
服务器还有多少空闲资源？
```

### CodeBuddy / 通用 Agent 框架

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill dev-container-manager -a <agent-name> -g -y
```

### 常用提示语

| 任务 | 提示语 |
|------|--------|
| 创建容器 | "在 IP X 上创建 N 核 M G 内存的开发容器" |
| 查看容器 | "列出服务器上的所有开发容器" |
| 查看资源 | "服务器还有多少空闲 CPU 和内存？" |
| 删除容器 | "删除 zhangsan 的开发容器" |
| 连接容器 | "给我 zhangsan 容器的 SSH 连接命令" |

## 前置条件

- 远程 Linux 服务器已安装 Docker
- 当前用户有远程服务器的 SSH 访问权限（默认 root）
- 远程服务器安装 `numactl`（用于 NUMA 拓扑检测，缺失时退化为单节点）

## 与其他 Skill 的关系

| Skill | 职责 | 与本 Skill 关系 |
|-------|------|---------------|
| `dev-container-manager`（本 Skill） | 远程开发容器生命周期管理 | — |
| `docker-management` | 本地 Docker 操作（容器/镜像/网络/Compose） | 互补：本 Skill 专注于远程服务器上的开发容器场景 |
| `ssh-remote` | SSH 连接与远程系统信息获取 | 本 Skill 依赖 SSH 执行所有远程操作 |

## 当前限制

- 仅支持 Linux 远程服务器
- 依赖 Docker Engine（不支持 Podman/containerd）
- 容器镜像默认使用 OpenEuler（可自定义）
- 不支持容器动态扩缩容（需重建）
- 不支持 GPU 直通分配
