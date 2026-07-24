---
name: remote-vm-builder
description: Create and manage Linux cloud-image virtual machines on remote SSH-accessible libvirt/KVM hosts. Use when users ask to list supported OS images, inspect remote VM host capabilities, create remote VMs with configurable CPU/memory/disk/network/storage, use custom cloud image URLs, SSH/exec into VMs, or start/stop/destroy remote VMs.
metadata:
  short-description: Build remote libvirt/KVM VMs
---

# Remote VM Builder

## 目标

这个 skill 用于在远程 Linux 服务器上创建和管理虚拟机。当前实现使用
`SSH + libvirt/KVM`，镜像类型限定为 Linux cloud image。它适合开发者在
指定服务器上快速创建 Ubuntu、Debian、CentOS Stream、openEuler 等系统的
测试 VM、构建 VM 或兼容性验证 VM。

核心能力：

- 查询当前内置支持的 OS 镜像。
- 查询远程宿主机的 KVM/libvirt 能力、架构、网络和存储池。
- 通过内置 OS ID 创建 VM。
- 通过 `--os custom --image-url <url>` 使用自定义 Linux cloud image。
- 通过命令行参数或 YAML spec 调整 CPU、内存、磁盘、架构、网络、存储池和 VM 用户。
- 管理 VM 生命周期：`status`、`ssh`、`exec`、`start`、`stop`、`destroy`。

不支持：

- ISO 交互式安装。
- Windows VM。
- Proxmox、OpenStack、VMware、公有云实例 API。
- 非 SSH 可达的远程宿主机。

## 文件结构

- `scripts/remote-vm`：推荐 CLI 入口，调用 Python 脚本。
- `scripts/remote_vm.py`：核心实现。
- `references/os-images.yaml`：内置 OS catalog，脚本读取它作为唯一镜像来源。
- `references/troubleshooting.md`：常见问题处理。
- `README.md`：面向人类用户的中文完整手册。
- `tests/remote-vm-builder/test_remote_vm.py`：离线测试，覆盖 catalog、dry-run、自定义镜像和 spec。

在本 skill 目录中运行示例时，先设置：

```bash
REMOTE_VM_SCRIPT="./scripts/remote-vm"
```

如果从 skills 集合仓库根目录运行，使用：

```bash
REMOTE_VM_SCRIPT="./skills/remote-vm-builder/scripts/remote-vm"
```

如果作为 Codex skill 安装到其他位置，按 skill 目录解析 `scripts/remote-vm`。

## 工作模型

创建 VM 的真实流程是：

1. 用户提供远程宿主机：`--host build01` 或 spec 顶层 `host`。
2. 脚本通过 SSH 到远程服务器执行检查和创建逻辑。
3. 如果使用内置 OS，脚本从 `references/os-images.yaml` 选择匹配架构的 cloud image URL。
4. 如果使用 custom OS，脚本使用用户传入的 `--image-url`。
5. 远程宿主机下载镜像，必要时解压 `.xz` 或 `.gz`。
6. 远程宿主机创建 qcow2 overlay，不修改 base image。
7. 脚本生成 cloud-init seed ISO，注入用户、SSH 公钥、hostname 和 sudo 权限。
8. 脚本执行 `virt-install --import` 创建 VM。
9. 创建后等待 libvirt DHCP lease，返回 VM IP 和 SSH ProxyJump 命令。

## 远程宿主机要求

远程服务器必须是 Linux KVM/libvirt 宿主机，并满足：

- 能从当前机器通过 SSH 登录。
- 远程用户能执行 `sudo -n true`。
- 存在 `/dev/kvm`。
- 已安装并可用：`virsh`、`virt-install`、`qemu-img`、`curl`。
- 如下载 `.xz` 镜像，需要 `xz`。
- 如下载 `.gz` 镜像，需要 `gzip`。
- 至少有一个 cloud-init seed 工具：`cloud-localds`、`genisoimage` 或 `mkisofs`。
- 至少有一个 libvirt 网络，默认使用 `default`。
- 至少有一个 libvirt storage pool，默认使用 `default`。

检查新宿主机时先运行：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
```

`doctor` 会检查 SSH、sudo、libvirt、KVM、`qemu-img`、`virt-install`、cloud-init seed
工具、默认网络、默认存储池和宿主机架构。

## 远程服务器指定方式

所有远程命令都用 `--host` 指定宿主机。`--host` 可以是 SSH config alias，
也可以是直接的 `user@host`。

推荐写入 `~/.ssh/config`：

```sshconfig
Host build01
  HostName 192.168.1.20
  User root
  IdentityFile ~/.ssh/id_ed25519
```

然后使用：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404
```

也可以直接写：

```bash
"$REMOTE_VM_SCRIPT" doctor --host root@192.168.1.20
"$REMOTE_VM_SCRIPT" create --host root@192.168.1.20 --os debian-12 --name debian-test
```

YAML spec 中，远程宿主机写在顶层：

```yaml
host: build01
```

CLI 的 `--host` 会覆盖 spec 中的 `host`。

不要混淆两个用户：

- `--host build01` 中的 SSH 用户：登录远程宿主机并运行 libvirt/KVM 的用户。
- `--vm-user builder` 或 `ssh.user`：创建在新 VM 里面的登录用户。

## 推荐工作流

第一次使用某台服务器时，按“检查宿主机 -> 选择镜像 -> dry-run -> 创建 -> 访问 -> 清理”的顺序：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
"$REMOTE_VM_SCRIPT" list-vm-types --host build01
"$REMOTE_VM_SCRIPT" list-networks --host build01
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
"$REMOTE_VM_SCRIPT" list-os --host build01
"$REMOTE_VM_SCRIPT" image-info --os ubuntu-24.04
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404 --arch x86_64 --dry-run
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404
```

## 命令总览

查询内置 OS：

```bash
"$REMOTE_VM_SCRIPT" list-os
"$REMOTE_VM_SCRIPT" list-os --family openeuler
"$REMOTE_VM_SCRIPT" list-os --arch aarch64
"$REMOTE_VM_SCRIPT" list-os --host build01
"$REMOTE_VM_SCRIPT" list-os --available-only
"$REMOTE_VM_SCRIPT" list-os --json
"$REMOTE_VM_SCRIPT" image-info --os openeuler-24.03-lts-sp4
```

查询远程宿主机能力：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
"$REMOTE_VM_SCRIPT" host-info --host build01
"$REMOTE_VM_SCRIPT" list-vm-types --host build01
"$REMOTE_VM_SCRIPT" list-networks --host build01
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
```

创建 VM：

```bash
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404
"$REMOTE_VM_SCRIPT" create --spec vm.yaml
"$REMOTE_VM_SCRIPT" create --host build01 --os custom --image-url https://example.com/image.qcow2 --name custom-vm --arch x86_64
```

生命周期：

```bash
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" exec --host build01 --name dev-u2404 -- uname -a
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404 --force
"$REMOTE_VM_SCRIPT" start --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404 --force
```

## 内置 OS Catalog

当前内置 OS ID：

```text
ubuntu-24.04
ubuntu-22.04
debian-12
centos-stream-9

openeuler-22.03-lts-sp1
openeuler-22.03-lts-sp2
openeuler-22.03-lts-sp3
openeuler-22.03-lts-sp4

openeuler-24.03-lts-sp1
openeuler-24.03-lts-sp2
openeuler-24.03-lts-sp3
openeuler-24.03-lts-sp4
```

每个 OS 条目包含名称、family、版本、默认用户、是否支持 cloud-init、架构列表、
镜像 URL、压缩格式和可用状态。详细数据在 `references/os-images.yaml`。

Rocky Linux 和 AlmaLinux 不在当前内置 catalog 中。需要其他发行版时使用：

```bash
"$REMOTE_VM_SCRIPT" create --host build01 --os custom --image-url https://example.com/image.qcow2 --name custom-vm --arch x86_64
```

注意：`openeuler-24.03-lts-sp4` 的 OS ID 已保留，但 catalog 当前将它标记为
`unavailable`。如果官方或镜像站已有可用镜像，使用 `--os custom --image-url <url>`。

## 创建 VM

最小命令：

```bash
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404
```

指定资源和宿主机能力：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os openeuler-24.03-lts-sp3 \
  --name oe2403-test \
  --arch aarch64 \
  --vcpus 8 \
  --memory-mb 16384 \
  --disk-gb 120 \
  --network default \
  --storage-pool fast-ssd \
  --cpu-mode host-passthrough \
  --vm-user builder
```

默认配置：

```text
vcpus: 4
memory_mb: 8192
disk_gb: 80
network: default
storage_pool: default
vm_user: builder
arch: auto
cpu_mode: host-passthrough
wait_timeout: 180
```

重要参数：

- `--name`：VM 名称。
- `--os`：内置 OS ID，或 `custom`。
- `--arch`：`x86_64`、`aarch64` 或 `auto`。默认 `auto` 会 SSH 到远程宿主机检测架构。
- `--vcpus`：vCPU 数量。
- `--memory-mb`：内存，单位 MB。
- `--disk-gb`：overlay 磁盘大小，单位 GB。
- `--network`：libvirt 网络名、`network:<name>` 或 `bridge:<name>`。
- `--storage-pool`：用于推导远程 artifact 根目录的 libvirt storage pool。
- `--cpu-mode`：libvirt CPU mode，默认 `host-passthrough`。
- `--vm-user`：VM 内部创建的 SSH 用户。
- `--public-key`：SSH 公钥文件路径或公钥文本。不传时尝试读取 `~/.ssh/id_ed25519.pub` 和 `~/.ssh/id_rsa.pub`。
- `--root-dir`：远程 artifact 根目录；默认从 storage pool 路径推导。
- `--wait-timeout`：创建后等待 DHCP lease 的秒数，默认 180。
- `--dry-run`：只打印配置和远程脚本，不真正创建 VM。

## YAML Spec

适合团队共享、CI 或可复现环境。

```yaml
host: build01
name: oe2403-test
os: openeuler-24.03-lts-sp3
arch: aarch64
resources:
  vcpus: 8
  memory_mb: 16384
  disk_gb: 120
libvirt:
  network: default
  storage_pool: fast-ssd
  cpu_mode: host-passthrough
ssh:
  user: builder
  public_key: ~/.ssh/id_ed25519.pub
```

执行：

```bash
"$REMOTE_VM_SCRIPT" create --spec vm.yaml
```

CLI 参数会覆盖 spec 同名配置，例如：

```bash
"$REMOTE_VM_SCRIPT" create --spec vm.yaml --host build02 --name temp-test
```

## 自定义 Cloud Image

自定义镜像入口是正式支持能力。镜像必须是 Linux cloud image，不支持 ISO。

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/company-ubuntu-24.04.qcow2 \
  --name company-test \
  --arch x86_64
```

支持 `.qcow2`、`.img`、`.raw`、`.qcow2.xz`、`.img.xz`、`.raw.xz`、`.qcow2.gz`、
`.img.gz`、`.raw.gz`。如果 URL 后缀不能判断格式，传：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url "https://example.com/download?id=123" \
  --image-format qcow2 \
  --name custom-image \
  --arch x86_64
```

推荐为自定义镜像提供 checksum：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/company.qcow2 \
  --image-checksum sha256:0123456789abcdef... \
  --name checked-image \
  --arch x86_64
```

查看推断结果：

```bash
"$REMOTE_VM_SCRIPT" image-info --os custom --image-url https://example.com/company.qcow2
```

## Dry Run

`--dry-run` 会打印合并后的配置和将通过 SSH 发到远程宿主机执行的脚本。

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name dry-run-test \
  --arch x86_64 \
  --dry-run
```

如果希望 dry-run 完全不连接远程服务器，显式传 `--arch x86_64` 或 `--arch aarch64`。
如果保持 `arch=auto`，脚本需要 SSH 到远程服务器检测 `uname -m`。

## 网络和存储

默认网络是 `default`，默认 storage pool 是 `default`。常用命令：

```bash
"$REMOTE_VM_SCRIPT" list-networks --host build01
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name net-test --network default
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name bridge-test --network bridge:br0
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name storage-test --storage-pool fast-ssd
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name rootdir-test --root-dir /var/lib/remote-vm-builder
```

## 生命周期和访问

状态：

```bash
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404 --json
```

SSH：

```bash
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404 --vm-user builder
```

在 VM 内执行命令：

```bash
"$REMOTE_VM_SCRIPT" exec --host build01 --name dev-u2404 -- uname -a
"$REMOTE_VM_SCRIPT" exec --host build01 --name dev-u2404 -- cloud-init status
```

停止、启动、销毁：

```bash
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404 --force
"$REMOTE_VM_SCRIPT" start --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404
```

`destroy` 默认只删除带有 `managed-by=remote-vm-builder` 描述标记的 VM。
如果确实要删除非本 skill 创建的 VM，必须显式传 `--force`。

## 输出格式

这些命令支持 `--json`：

- `list-os`
- `image-info`
- `doctor`
- `host-info`
- `list-vm-types`
- `list-networks`
- `list-storage-pools`
- `status`

给自动化、CI 或上层 agent 使用时优先选择 `--json`。

## 安全规则

- 不要把远程服务器密码写进 spec。
- 不要把私钥内容写进 spec。
- 推荐使用 `~/.ssh/config` 管理宿主机登录信息。
- 默认通过 SSH key 注入 VM 登录权限。
- 自定义镜像建议搭配 `--image-checksum sha256:<digest>`。
- 生产环境使用前先跑 `--dry-run` 审计远程脚本。
- `destroy` 默认拒绝删除没有 `managed-by=remote-vm-builder` 标记的 VM。

## 故障处理

常见问题见 `references/troubleshooting.md`。

快速定位：

- SSH 失败：先运行 `ssh build01 true`。
- sudo 失败：远程运行 `sudo -n true`。
- 无 KVM：检查 `/dev/kvm` 和宿主机虚拟化能力。
- 无 libvirt：检查 `virsh -c qemu:///system list --all`。
- 无 DHCP IP：检查 libvirt 网络是否 active，运行 `list-networks` 和 `status`。
- 镜像不可用：运行 `image-info --os <id>`，必要时使用 `--os custom --image-url <mirror-url>`。

## Agent 使用原则

当 Codex 使用这个 skill 时：

1. 优先读取 `references/os-images.yaml` 确认 OS ID、架构和可用性。
2. 新宿主机先运行 `doctor --host <host>`，再创建 VM。
3. 用户只说发行版名称时，把自然语言映射为稳定 OS ID；不确定时先用 `list-os`。
4. 用户没有指定架构时，使用默认 `arch=auto`；如果 dry-run 不应连接远端，显式指定架构。
5. 创建前如果风险较高，先用 `create --dry-run` 展示将执行的配置和远程脚本。
6. 不替用户写入密码、私钥或其他敏感信息。
7. 对 unavailable catalog 条目，不强行创建；提示用户使用 custom image URL。

## 开发和验证

离线验证：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -o cache_dir=/tmp/qemu-skill-pytest-cache
python3 /Users/yuzhihuan/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

真实集成验证需要一台可 SSH 访问、具备 libvirt/KVM 的远程 Linux 宿主机。
