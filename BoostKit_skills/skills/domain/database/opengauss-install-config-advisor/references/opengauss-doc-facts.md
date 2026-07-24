# openGauss Documented Facts

Use this reference when you need portable, distilled facts from the openGauss documentation. These are not a replacement for version-specific docs. If a user's target version differs, ask them to confirm against the official documentation or package/image notes for that version.

## Scope Of These Facts

These facts are intended for ordinary single-node or lightweight installation guidance. Treat production, primary-standby, CM, HA, distributed deployment, and deep performance tuning as outside the main path.

## Platform And Operating System Notes

Documented platform support includes:

- ARM servers.
- x86_64 general-purpose PC/server platforms.
- Local storage such as SATA, SAS, and SSD.
- Ethernet networking, including gigabit and 10GE environments.

Documented OS examples include:

- ARM: openEuler 20.03 LTS, openEuler 22.03 LTS, openEuler 24.03 LTS, Kylin V10, Asianux 7.5, UnionTech/UOS V20.
- x86: openEuler 20.03 LTS, openEuler 22.03 LTS, openEuler 24.03 LTS, CentOS 7.6, Asianux 7.6, Kylin V10.

The docs call out openEuler 20.03 LTS as a recommended OS in some installation-preparation material. Native package compatibility is version-specific, so always confirm the package matches the user's OS and CPU architecture.

Some package guidance notes that current installation packages may require an English OS environment. If a native install fails with locale or OS recognition issues, check the package documentation and OS compatibility notes before continuing.

## Lightweight Resource Baseline

For ordinary lightweight use, the docs mention:

- Minimum personal/developer configuration: about 2 CPU cores and 4 GB memory.
- Recommended personal/developer configuration: about 4 CPU cores and 8 GB memory.

The docs also describe much larger memory expectations for functional debugging, performance testing, and commercial deployment. Keep those out of the normal lightweight path unless the user explicitly asks for heavier scenarios.

## Disk, Storage, And Network Planning

Installation-preparation guidance includes these planning points:

- Reserve space for openGauss application files.
- Plan additional metadata storage per host.
- Keep substantial free disk capacity for database data rather than filling the target filesystem.
- SSD storage is supported for database primary storage.
- RAID planning and hardware cache policy are hardware-specific; do not invent RAID commands. Tell users to follow their hardware/vendor documentation.
- A remaining inode count greater than 1.5 billion is documented as recommended in some preparation guidance. For ordinary lightweight setups, treat inode shortage as a warning or troubleshooting signal rather than an automatic blocker unless the installer or workload needs it.
- Network guidance mentions Ethernet of at least hundreds of Mbps, with gigabit/10GE environments supported.

## Common Native Dependencies

For native package installation, documented dependency examples include:

- `bzip2`
- `libaio-devel`
- `readline-devel`
- `libedit-devel`
- `libxml2-devel`
- `lz4-devel`
- `numactl-devel`
- `unixODBC-devel`
- `java-1.8.0-openjdk-devel`
- `openblas-devel`

Do not blindly run package-manager commands for every OS. First identify the user's OS and package manager, then map missing dependency names appropriately.

## Installation Package Handling

Documented preparation guidance includes:

- Download the package matching the target platform.
- For ordinary non-enterprise or learning scenarios, a simplified package can be enough when OM components are not needed.
- Verify package integrity when checksum files are available.
- Extract the package and inspect the directory layout before giving package-specific commands.

If the extracted package includes `simpleInstall/`, inspect its scripts and help output before giving install commands. Do not invent installer flags.

## openGauss Check Tools

### `gs_checkos`

`gs_checkos` helps check operating system, control parameters, disk configuration, I/O configuration, network configuration, and THP-related information.

Important behavior:

- It can be executed by root or ordinary users.
- Ordinary users can check only; they cannot set parameters.
- `A1...A14` items are check-only.
- `B1...B8` items set system parameters to expected values.
- `A` and `B` item groups should not be mixed in one invocation.
- Root can check all `A1...A14` items and set `B1...B8`.
- Ordinary users can check only a subset documented by the tool and cannot set items.

Use `gs_checkos` conservatively:

```bash
gs_checkos -i A --detail
```

Ask users to paste output instead of automatically applying `B` settings.

### `gs_check`

`gs_check` unifies several check tools and can inspect openGauss runtime environment, OS environment, network environment, and database execution environment.

Documented scene examples include:

- `inspect`
- `upgrade`
- `binary_upgrade`
- `health`
- `install`

Use it after native installation or before major changes when available:

```bash
gs_check -e inspect
gs_check -e health
gs_check -e install
```

If the check needs root-only items, prefer explaining the permission requirement or using documented skip options rather than requesting broad credentials.

### `gs_perfconfig`

`gs_perfconfig` can provide or apply tuning across OS configuration, database setup, and database GUC parameters.

Important behavior:

- It may run as root or ordinary user, but some OS checks/adjustments require root.
- Some actions may restart the database.
- It asks for user consent before disruptive tuning operations.
- Main actions include `tune`, `recover`, `preset`, and `help`.
- `tune` supports targets such as `all`, `os`, `setup`, `guc`, and `suggest`.
- `--apply` performs changes. Without applying, use it as a planning/report mechanism when possible.

For this lightweight skill, prefer suggestion/report mode. Do not apply changes unless the user explicitly asks and understands restart risk.

## Connection And Safety Notes

Connection-related parameters can affect security:

- Listening on all addresses can expose the server. Prefer a specific address when remote access is required.
- Broad client authentication rules such as allowing all source IPs are risky.
- Port ranges below 1024 are usually OS-reserved and should not be used as normal openGauss service ports.
- Increasing connection-related settings can require more shared memory or semaphores, so do not raise connection counts blindly.

When remote access is requested, use the narrowest client IP/CIDR and explain the firewall and authentication implications.
