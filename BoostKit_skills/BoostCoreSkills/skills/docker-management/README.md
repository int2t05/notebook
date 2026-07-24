# docker-management Docker 管理

`docker-management` 覆盖 Docker 容器、镜像、卷、网络和 Compose 栈的完整管理——生命周期操作、调试、清理和 Dockerfile 优化。

`docker-management` covers Docker containers, images, volumes, networks, and Compose stacks — lifecycle ops, debugging, cleanup, and Dockerfile optimization.

## 核心能力

- **容器生命周期**：运行、停止、启动、重启、删除、暂停/恢复，以及 exec/logs/inspect/stats/top 等交互操作
- **镜像管理**：构建（含 BuildKit）、拉取、推送、标签、历史查看、清理
- **Docker Compose**：多服务栈的启动/停止/日志/执行/配置验证，含 healthcheck 模板
- **卷和网络**：创建、查看、删除、清理，容器间网络连接管理
- **磁盘诊断与清理**：`docker system df` 诊断 + 分级清理（dangling → unused → aggressive）
- **Dockerfile 优化**：多阶段构建、层排序、.dockerignore、slim/alpine 基础镜像、非 root 用户等最佳实践
- **故障排查**：常见问题速查表（端口冲突、权限问题、磁盘满、构建缓存失效等）

## 快速开始

### 安装

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill docker-management -g -y
```

### 前置检查

```bash
docker --version && docker compose version
```

## 常用命令速查

| 任务 | 命令 |
|------|------|
| 后台运行容器 | `docker run -d --name NAME IMAGE` |
| 停止并删除 | `docker stop NAME && docker rm NAME` |
| 查看日志（跟踪） | `docker logs --tail 50 -f NAME` |
| 进入容器 | `docker exec -it NAME /bin/sh` |
| 列出所有容器 | `docker ps -a` |
| 构建镜像 | `docker build -t TAG .` |
| Compose 启动 | `docker compose up -d` |
| Compose 停止 | `docker compose down` |
| 磁盘用量 | `docker system df` |
| 清理悬挂资源 | `docker image prune && docker container prune` |

## 在 AI Agent 工具中使用

### Claude Code

当你提到 Docker 操作、容器管理、镜像构建、Compose、Dockerfile 优化时，Skill 会自动激活：

```
帮我运行一个 nginx 容器，端口映射到 8080
构建当前目录的 Dockerfile，打上 my-app:latest 标签
检查 Docker 磁盘占用，清理无用资源
审查这个 Dockerfile 有没有优化空间
用 docker compose 启动项目
```

### CodeBuddy / 通用 Agent 框架

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill docker-management -a <agent-name> -g -y
```

### 常用提示语

| 任务 | 提示语 |
|------|--------|
| 运行容器 | "运行一个 postgres 16 容器，持久化数据，端口 5432" |
| 调试容器 | "进入 web 容器查看环境变量和日志" |
| 构建镜像 | "用 BuildKit 构建当前目录的 Dockerfile" |
| 清理空间 | "检查 Docker 磁盘占用，清理 7 天前的未使用镜像" |
| Compose | "用 docker compose 启动项目，跟踪 api 服务日志" |
| 审查优化 | "审查这个 Dockerfile，给出优化建议" |

## 故障排查速查

| 问题 | 原因 | 解决 |
|------|------|------|
| 容器立即退出 | 主进程结束或崩溃 | `docker logs NAME`，尝试 `docker run -it --entrypoint /bin/sh IMAGE` |
| 端口已被占用 | 其他进程使用该端口 | `docker ps` 或 `lsof -i :PORT` 查找 |
| 磁盘空间不足 | Docker 磁盘满 | `docker system df` 后按需清理 |
| 无法连接容器 | 应用绑定到 127.0.0.1 | 应用需绑定 `0.0.0.0`，检查 `-p` 映射 |
| 卷权限拒绝 | UID/GID 不匹配 | 使用 `--user $(id -u):$(id -g)` 或修复权限 |
| Compose 服务互不可达 | 网络或服务名错误 | 服务名即主机名，检查 `docker compose config` |
| 构建缓存失效 | Dockerfile 层顺序不对 | 将变化少的层放前面（依赖先于源码） |
| 镜像过大 | 无多阶段构建/无 .dockerignore | 使用多阶段构建，添加 `.dockerignore` |

## Dockerfile 优化要点

1. **多阶段构建** — 分离构建环境和运行环境，减小最终镜像
2. **层顺序** — 依赖安装在前，源码复制在后
3. **合并 RUN** — 减少层数，缩小镜像
4. **.dockerignore** — 排除 `node_modules`、`.git`、`__pycache__` 等
5. **固定版本** — `node:20-alpine` 而非 `node:latest`
6. **非 root 运行** — 添加 `USER` 指令
7. **轻量基础镜像** — `python:3.12-slim` 而非 `python:3.12`

## 与其他 Skill 的关系

| Skill | 职责 | 与本 Skill 关系 |
|-------|------|---------------|
| `docker-management`（本 Skill） | 本地 Docker 全功能管理 | — |
| `dev-container-manager` | 远程开发容器生命周期管理 | 互补：本 Skill 面向本地通用 Docker 操作，dev-container-manager 面向远程服务器上的隔离开发环境 |

## 当前限制

- 需要 Docker Engine 已安装并运行
- 部分操作需要 `docker` 组成员资格或 `sudo`
- 仅支持 Docker Compose v2（现代 Docker 已内置）
- 不涉及 Kubernetes/容器编排
- 不涉及 Docker Swarm 模式
