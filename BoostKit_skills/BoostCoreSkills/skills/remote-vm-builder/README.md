# Remote VM Builder Skill 使用手册

这个 skill 用于在远程 Linux 服务器上创建和管理虚拟机。当前实现采用 `SSH + libvirt/KVM`，通过 Linux cloud image、cloud-init 和 `virt-install` 自动创建可 SSH 登录的 VM。

如果已经通过 skills 管理工具安装，直接在 AI Agent 中描述需求即可，例如：

```text
在 build01 上创建一台 Ubuntu 24.04 虚拟机，4 核 8G，磁盘 80G
查询 build01 支持哪些 VM 类型和 OS 镜像
```

从本 skill 目录手动运行时，主脚本为：

```bash
REMOTE_VM_SCRIPT="./scripts/remote-vm"
```

从 skills 集合仓库根目录运行时，使用：

```bash
REMOTE_VM_SCRIPT="./skills/remote-vm-builder/scripts/remote-vm"
```

也可以直接调用 Python 入口：

```bash
REMOTE_VM_SCRIPT="./scripts/remote_vm.py"
```

安装示例：

```bash
npx skills add https://gitcode.com/boostkit/skills.git --full-depth --skill remote-vm-builder -g -y
```

## 1. 适用场景

适合这些需求：

- 在指定远程服务器上创建 Ubuntu、Debian、CentOS Stream、openEuler VM。
- 查询当前 skill 内置支持哪些 OS 镜像。
- 检查远程宿主机是否支持 KVM/libvirt 创建 VM。
- 指定 VM 的 CPU、内存、磁盘、网络、存储池、架构等配置。
- 使用公司内部或自定义 Linux cloud image URL 创建 VM。
- 启动、停止、查询、SSH 登录、执行命令、销毁 VM。

当前实现不支持：

- ISO 交互式安装。
- Windows VM。
- Proxmox、OpenStack、VMware、公有云实例 API。

## 2. Linux Cloud Image 是什么

Linux cloud image 是已经安装好系统的虚拟机磁盘模板，常见格式包括 `.qcow2`、`.img`、`.raw`，也可能带 `.xz` 或 `.gz` 压缩。

它不是 ISO 安装盘。创建 VM 时，脚本会：

1. 在远程宿主机下载 cloud image。
2. 创建一个 qcow2 overlay 磁盘。
3. 生成 cloud-init seed ISO。
4. 通过 cloud-init 注入 hostname、用户、SSH key、sudo 权限。
5. 用 `virt-install --import` 启动 VM。

## 3. 远程服务器要求

远程服务器需要是 Linux 宿主机，并具备：

- 可通过 SSH 登录。
- 当前 SSH 用户可以执行 `sudo -n true`。
- 有 `/dev/kvm`。
- 已安装并可用 `libvirt`、`virsh`、`virt-install`、`qemu-img`。
- 已安装 `curl`。
- 如需解压 `.xz` 镜像，需要 `xz`。
- 如需解压 `.gz` 镜像，需要 `gzip`。
- 有 cloud-init seed 工具之一：`cloud-localds`、`genisoimage` 或 `mkisofs`。
- 至少有一个 libvirt 网络，默认使用 `default`。
- 至少有一个 libvirt storage pool，默认使用 `default`。

首次使用一台服务器时，先运行：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
```

## 4. 如何指定远程服务器

所有远程操作都通过 `--host` 指定宿主机。`--host` 可以是 SSH config alias，也可以是直接的 `user@host`。

推荐写入 `~/.ssh/config`：

```sshconfig
Host build01
  HostName 192.168.1.20
  User root
  IdentityFile ~/.ssh/id_ed25519
```

然后在命令里使用：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
"$REMOTE_VM_SCRIPT" create --host build01 --os ubuntu-24.04 --name dev-u2404
```

也可以直接指定：

```bash
"$REMOTE_VM_SCRIPT" doctor --host root@192.168.1.20
"$REMOTE_VM_SCRIPT" create --host root@192.168.1.20 --os debian-12 --name debian-test
```

不要把密码或私钥内容写进 spec。这个 skill 默认依赖系统 SSH 配置和 SSH key 登录。

注意区分两个用户：

- `--host build01` 里的 SSH 用户，是登录远程宿主机、运行 libvirt/KVM 的用户。
- `--vm-user builder` 是创建在 VM 内部的登录用户。

## 5. 查询支持的 OS 镜像

列出所有内置 OS：

```bash
"$REMOTE_VM_SCRIPT" list-os
```

只看 openEuler：

```bash
"$REMOTE_VM_SCRIPT" list-os --family openeuler
```

只看某个架构：

```bash
"$REMOTE_VM_SCRIPT" list-os --arch aarch64
"$REMOTE_VM_SCRIPT" list-os --arch x86_64
```

根据远程宿主机架构过滤：

```bash
"$REMOTE_VM_SCRIPT" list-os --host build01
```

JSON 输出：

```bash
"$REMOTE_VM_SCRIPT" list-os --json
```

查看单个镜像详情：

```bash
"$REMOTE_VM_SCRIPT" image-info --os ubuntu-24.04
"$REMOTE_VM_SCRIPT" image-info --os openeuler-24.03-lts-sp4
"$REMOTE_VM_SCRIPT" image-info --os openeuler-22.03-lts-sp4 --arch aarch64
```

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

Rocky Linux 和 AlmaLinux 不在当前内置列表中。如需使用其他发行版，使用 `--os custom --image-url <url>`。

openEuler `24.03 LTS SP4` 的 OS ID 已保留，但当前 catalog 将它标记为 `unavailable`，因为官方仓库 URL 在校验时返回 404。如果你有可用镜像源，请用自定义镜像 URL。

## 6. 查询远程宿主机能力

检查远程环境是否具备创建 VM 的条件：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
```

输出远程宿主机能力摘要：

```bash
"$REMOTE_VM_SCRIPT" host-info --host build01
```

查询支持的虚拟机类型、架构、machine type、CPU mode、网络和存储池：

```bash
"$REMOTE_VM_SCRIPT" list-vm-types --host build01
```

查询 libvirt 网络：

```bash
"$REMOTE_VM_SCRIPT" list-networks --host build01
```

查询 libvirt storage pool：

```bash
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
```

这些命令也支持 JSON 输出：

```bash
"$REMOTE_VM_SCRIPT" host-info --host build01 --json
"$REMOTE_VM_SCRIPT" list-vm-types --host build01 --json
"$REMOTE_VM_SCRIPT" list-networks --host build01 --json
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01 --json
```

## 7. 使用内置 OS 创建 VM

最小创建命令：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name dev-u2404
```

创建 Debian 12：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os debian-12 \
  --name debian12-dev
```

创建 openEuler：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os openeuler-22.03-lts-sp4 \
  --name oe2203-sp4
```

指定架构：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os openeuler-24.03-lts-sp3 \
  --arch aarch64 \
  --name oe2403-arm
```

如果不指定 `--arch`，默认是 `auto`，脚本会通过 SSH 检测远程宿主机架构，并选择匹配的镜像。

## 8. 调整虚拟机配置

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
```

通过命令行调整：

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

参数说明：

| 参数 | 作用 |
|---|---|
| `--name` | VM 名称 |
| `--os` | 内置 OS ID，或 `custom` |
| `--arch` | 镜像架构，支持 `x86_64`、`aarch64`、`auto` |
| `--vcpus` | VM CPU 数量 |
| `--memory-mb` | VM 内存，单位 MB |
| `--disk-gb` | VM overlay 磁盘大小，单位 GB |
| `--network` | libvirt 网络名，默认 `default` |
| `--storage-pool` | libvirt 存储池，默认 `default` |
| `--cpu-mode` | libvirt CPU mode，默认 `host-passthrough` |
| `--vm-user` | VM 内部创建的 SSH 用户 |
| `--public-key` | SSH 公钥文件路径，或直接传入公钥文本 |
| `--root-dir` | 远程 artifact 根目录，默认从 storage pool 路径推导 |
| `--wait-timeout` | 创建后等待 DHCP lease 的秒数，默认 180 |

如果不传 `--public-key`，脚本会尝试读取本机：

```text
~/.ssh/id_ed25519.pub
~/.ssh/id_rsa.pub
```

## 9. 使用 YAML spec 创建 VM

适合团队共享、CI 或可复现环境。

示例 `vm.yaml`：

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

创建：

```bash
"$REMOTE_VM_SCRIPT" create --spec vm.yaml
```

命令行参数会覆盖 spec 中的同名配置。例如临时换宿主机：

```bash
"$REMOTE_VM_SCRIPT" create --spec vm.yaml --host build02
```

## 10. 使用自定义 Cloud Image

自定义镜像必须是 Linux cloud image，不支持 ISO。

基本用法：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/company-ubuntu-24.04.qcow2 \
  --name company-test \
  --arch x86_64
```

压缩镜像：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/openeuler-custom.qcow2.xz \
  --name custom-oe \
  --arch aarch64
```

带 checksum：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/company.qcow2 \
  --image-checksum sha256:0123456789abcdef... \
  --name checked-image \
  --arch x86_64
```

如果 URL 后缀无法判断格式，显式指定：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://example.com/download?id=123 \
  --image-format qcow2 \
  --name custom-image \
  --arch x86_64
```

查看自定义镜像推断信息：

```bash
"$REMOTE_VM_SCRIPT" image-info \
  --os custom \
  --image-url https://example.com/company-ubuntu-24.04.qcow2
```

## 11. Dry Run 审计

`--dry-run` 会打印配置和将发送到远程宿主机执行的脚本，不真正创建 VM。

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name dry-run-test \
  --arch x86_64 \
  --dry-run
```

如果你希望 dry-run 完全不连接远程服务器，请显式传 `--arch x86_64` 或 `--arch aarch64`。如果使用默认 `arch=auto`，脚本需要 SSH 到远程宿主机检测架构。

## 12. VM 生命周期管理

查询状态：

```bash
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404 --json
```

SSH 登录 VM：

```bash
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404
```

指定 VM 内部用户：

```bash
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404 --vm-user builder
```

在 VM 内执行命令：

```bash
"$REMOTE_VM_SCRIPT" exec --host build01 --name dev-u2404 -- uname -a
"$REMOTE_VM_SCRIPT" exec --host build01 --name dev-u2404 -- cloud-init status
```

停止 VM：

```bash
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404
```

强制停止：

```bash
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404 --force
```

启动 VM：

```bash
"$REMOTE_VM_SCRIPT" start --host build01 --name dev-u2404
```

销毁 VM：

```bash
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404
```

默认情况下，`destroy` 只会销毁带有 `managed-by=remote-vm-builder` 标记的 VM。强制销毁非本 skill 管理的 VM：

```bash
"$REMOTE_VM_SCRIPT" destroy --host build01 --name old-vm --force
```

## 13. 网络和存储

默认使用 libvirt 网络：

```text
default
```

查看可用网络：

```bash
"$REMOTE_VM_SCRIPT" list-networks --host build01
```

使用指定 libvirt 网络：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name net-test \
  --network default
```

使用 bridge：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name bridge-test \
  --network bridge:br0
```

默认使用 storage pool：

```text
default
```

查看可用 storage pool：

```bash
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
```

使用指定 storage pool：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name storage-test \
  --storage-pool fast-ssd
```

指定远程 artifact 根目录：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name rootdir-test \
  --root-dir /var/lib/remote-vm-builder
```

## 14. 推荐工作流

第一次使用某台服务器：

```bash
"$REMOTE_VM_SCRIPT" doctor --host build01
"$REMOTE_VM_SCRIPT" list-vm-types --host build01
"$REMOTE_VM_SCRIPT" list-networks --host build01
"$REMOTE_VM_SCRIPT" list-storage-pools --host build01
```

选择 OS：

```bash
"$REMOTE_VM_SCRIPT" list-os --host build01
"$REMOTE_VM_SCRIPT" image-info --os ubuntu-24.04
```

审计创建脚本：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name dev-u2404 \
  --arch x86_64 \
  --dry-run
```

正式创建：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os ubuntu-24.04 \
  --name dev-u2404
```

进入 VM：

```bash
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" ssh --host build01 --name dev-u2404
```

完成后清理：

```bash
"$REMOTE_VM_SCRIPT" stop --host build01 --name dev-u2404
"$REMOTE_VM_SCRIPT" destroy --host build01 --name dev-u2404
```

## 15. 常见问题

### SSH 失败

先确认：

```bash
ssh build01 true
```

如果失败，检查 `~/.ssh/config`、用户名、私钥和网络连通性。

### sudo 失败

`doctor` 要求远程用户可以运行：

```bash
sudo -n true
```

如果这个命令失败，需要给远程用户配置免交互 sudo，或使用 root 登录。

### 没有 KVM

如果 `/dev/kvm` 不存在，当前实现不适合在这台服务器上创建 VM。请换一台支持硬件虚拟化的宿主机，或检查 BIOS/云服务器虚拟化能力。

### 没有 DHCP IP

`status` 和 `ssh` 依赖 libvirt DHCP lease 获取 VM IP。如果获取不到：

```bash
"$REMOTE_VM_SCRIPT" list-networks --host build01
"$REMOTE_VM_SCRIPT" status --host build01 --name dev-u2404
```

确认 VM 使用的网络处于 active 状态，并且该网络能提供 DHCP lease。

### 内置镜像不可用

先查看：

```bash
"$REMOTE_VM_SCRIPT" image-info --os openeuler-24.03-lts-sp4
```

如果 catalog 标记为 unavailable，使用自定义镜像：

```bash
"$REMOTE_VM_SCRIPT" create \
  --host build01 \
  --os custom \
  --image-url https://mirror.example.com/openEuler-24.03-LTS-SP4-x86_64.qcow2.xz \
  --name oe2403-sp4 \
  --arch x86_64
```

## 16. 安全约定

- 不在 spec 中保存密码。
- 不在 spec 中保存私钥内容。
- 优先使用 `~/.ssh/config` 管理远程宿主机登录信息。
- `destroy` 默认只删除本 skill 标记过的 VM。
- 自定义镜像建议配合 `--image-checksum sha256:<digest>` 使用。
- 生产服务器上先用 `--dry-run` 审计远程脚本。
