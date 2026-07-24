# 补丁已合入差异报告

> **生成时间**: 2026-03-31 11:36:55
> **目标仓库**: `/home/xxd/velinux-kernel`
> **目标分支**: `auto-patch-20260331_110559`
> **模式**: `merged-diff`

---

## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | 13 |
| 本地补丁文件数 | 13 |
| 已匹配目标提交 | 13 |
| 未匹配目标提交 | 0 |
| 歧义目标提交 | 0 |
| 完全一致 | 9 |
| 存在差异 | 4 |
| 未匹配 | 0 |
| 匹配歧义 | 0 |

> **整体状态**: ❌ 已发现本地补丁与目标仓库已合入补丁存在差异

---

## 详细结果

## 补丁 1: KVM: arm64: Introduce shadow device

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `013f589_KVM__arm64__Introduce_shadow_device.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/013f589_KVM__arm64__Introduce_shadow_device.patch` |
| 本地提交 | `013f589495b7` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5aa1cfbd251f3bf78576ddeb98dd35302d25d52c` |
| 目标标题 | KVM: arm64: Introduce shadow device |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `bdb44829c856582e9da4750a9fdfcd0917d7c3f3` |
| 目标 patch-id | `e31e0ce53e4f3400c3fef1d3296f916ad4de513d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/013f589_KVM__arm64__Introduce_shadow_device.patch`

**目标提交候选**:
- `5aa1cfbd251f3bf78576ddeb98dd35302d25d52c`

### 文件 1: `arch/arm64/kvm/Makefile`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 82.1% | Hunk content matches (layout differs) |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/vgic/shadow_dev.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `include/uapi/linux/kvm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 2: KVM: arm64: update arm64 openeuler_defconfig for CONFIG_VIRT_PLAT_DEV

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0bd8805_KVM__arm64__update_arm64_openeuler_defconfig_for_C.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0bd8805_KVM__arm64__update_arm64_openeuler_defconfig_for_C.patch` |
| 本地提交 | `0bd88058ec52` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `91fa350bba87c4676957d054bd7f9d4548e9f3d2` |
| 目标标题 | KVM: arm64: update arm64 openeuler_defconfig for CONFIG_VIRT_PLAT_DEV |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `a5cd2fe0d7b62404d432d03c64b5dc494855fcb4` |
| 目标 patch-id | `3a816d67be223c9a0ea50bb8db94f245c3c43def` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/0bd8805_KVM__arm64__update_arm64_openeuler_defconfig_for_C.patch`

**目标提交候选**:
- `91fa350bba87c4676957d054bd7f9d4548e9f3d2`

### 文件 1: `arch/arm64/configs/openeuler_defconfig`

**状态**: ❌ `missing-file`

*备注*: Merged commit does not contain this file diff

**本地补丁有、目标已合入补丁缺失的新增行**:
- `CONFIG_VIRT_PLAT_DEV=y`


### 文件 2: `config.aarch64`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_VIRT_PLAT_DEV=y`


### 文件 3: `config.aarch64-64k`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_VIRT_PLAT_DEV=y`


---

## 补丁 3: irqchip/gic-v3-its: Init reserved rsv_devid_pools use pci bus info

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1572bef_irqchip_gic_v3_its__Init_reserved_rsv_devid_pools_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1572bef_irqchip_gic_v3_its__Init_reserved_rsv_devid_pools_.patch` |
| 本地提交 | `1572bef21a3e` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `b69a2eeb8637b08dddd8441c21ec36dd5ea88d43` |
| 目标标题 | irqchip/gic-v3-its: Init reserved rsv_devid_pools use pci bus info |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `abec598d90231868fa598d4948a2cadd933bb0e6` |
| 目标 patch-id | `24c5894b6c735b5ff92d29e3fd958269e87c6d5d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/1572bef_irqchip_gic_v3_its__Init_reserved_rsv_devid_pools_.patch`

**目标提交候选**:
- `b69a2eeb8637b08dddd8441c21ec36dd5ea88d43`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `#endif`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `different` | 98.4% | Hunk content differs |


---

## 补丁 4: irqchip/gic-v3-its: Remove DevID Pool's restriction

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `2dfa84d_irqchip_gic_v3_its__Remove_DevID_Pool_s_restrictio.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/2dfa84d_irqchip_gic_v3_its__Remove_DevID_Pool_s_restrictio.patch` |
| 本地提交 | `2dfa84d06b8a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `afbe84d6e40abbedd4d5064f89684c3d38db8dbd` |
| 目标标题 | irqchip/gic-v3-its: Remove DevID Pool's restriction |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `6b8685678945da42eae63613dacec4efc27f9a77` |
| 目标 patch-id | `6b8685678945da42eae63613dacec4efc27f9a77` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/2dfa84d_irqchip_gic_v3_its__Remove_DevID_Pool_s_restrictio.patch`

**目标提交候选**:
- `afbe84d6e40abbedd4d5064f89684c3d38db8dbd`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 5: KVM: arm64: sdev: Support virq bypass by INT/VSYNC command

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `3a95fc6_KVM__arm64__sdev__Support_virq_bypass_by_INT_VSYNC.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/3a95fc6_KVM__arm64__sdev__Support_virq_bypass_by_INT_VSYNC.patch` |
| 本地提交 | `3a95fc619fa4` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `56c13fc15191fc7d73aadceead6fc9ef335d2fcc` |
| 目标标题 | KVM: arm64: sdev: Support virq bypass by INT/VSYNC command |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `c36ccd6a17bccf1e7db532cefaced68ecb25a2da` |
| 目标 patch-id | `c36ccd6a17bccf1e7db532cefaced68ecb25a2da` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/3a95fc6_KVM__arm64__sdev__Support_virq_bypass_by_INT_VSYNC.patch`

**目标提交候选**:
- `56c13fc15191fc7d73aadceead6fc9ef335d2fcc`

### 文件 1: `arch/arm64/kvm/vgic/vgic-irqfd.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 6: irqchip/gic-v3-its: Add virt platform devices MSI support

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `4cc6850_irqchip_gic_v3_its__Add_virt_platform_devices_MSI_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/4cc6850_irqchip_gic_v3_its__Add_virt_platform_devices_MSI_.patch` |
| 本地提交 | `4cc685056a00` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `b8b6abe071ae40d5409a134d41b53c10927705d1` |
| 目标标题 | irqchip/gic-v3-its: Add virt platform devices MSI support |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `323520a477725f855e31cf1bad5b57098f499915` |
| 目标 patch-id | `323520a477725f855e31cf1bad5b57098f499915` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/4cc6850_irqchip_gic_v3_its__Add_virt_platform_devices_MSI_.patch`

**目标提交候选**:
- `b8b6abe071ae40d5409a134d41b53c10927705d1`

### 文件 1: `drivers/irqchip/irq-gic-v3-its-platform-msi.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/linux/msi.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 7: irqchip/gic-v3-its: Alloc/Free device id from pools for virtual devices

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `7b39fd0_irqchip_gic_v3_its__Alloc_Free_device_id_from_pool.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/7b39fd0_irqchip_gic_v3_its__Alloc_Free_device_id_from_pool.patch` |
| 本地提交 | `7b39fd06a391` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `34f326c838ba156c8ec12bdddfb58f21e33105c0` |
| 目标标题 | irqchip/gic-v3-its: Alloc/Free device id from pools for virtual devices |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `7b1fd8b462c10170edb762ef6ace105a722af3ae` |
| 目标 patch-id | `7b1fd8b462c10170edb762ef6ace105a722af3ae` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/7b39fd0_irqchip_gic_v3_its__Alloc_Free_device_id_from_pool.patch`

**目标提交候选**:
- `34f326c838ba156c8ec12bdddfb58f21e33105c0`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |
| 6 | 6 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 8: virt_plat_dev: Register the virt platform device driver

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8597aa4_virt_plat_dev__Register_the_virt_platform_device_d.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8597aa4_virt_plat_dev__Register_the_virt_platform_device_d.patch` |
| 本地提交 | `8597aa420851` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `61707226ce3028c519839567d721090ea996e18e` |
| 目标标题 | virt_plat_dev: Register the virt platform device driver |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `8838c1112b38fa6b737e01d653d76f9ffd493731` |
| 目标 patch-id | `8838c1112b38fa6b737e01d653d76f9ffd493731` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/8597aa4_virt_plat_dev__Register_the_virt_platform_device_d.patch`

**目标提交候选**:
- `61707226ce3028c519839567d721090ea996e18e`

### 文件 1: `drivers/misc/Makefile`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/misc/virt_plat_dev.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 9: irqchip/gic-v3-its: Introduce the reserved device ID pools

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `87f09e4_irqchip_gic_v3_its__Introduce_the_reserved_device_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/87f09e4_irqchip_gic_v3_its__Introduce_the_reserved_device_.patch` |
| 本地提交 | `87f09e449b65` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `19cee9a7eb6de31030fd3b8aa13d132b3c40ee0d` |
| 目标标题 | irqchip/gic-v3-its: Introduce the reserved device ID pools |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `9e272d09e085eb31776617badac36f2fd85fa190` |
| 目标 patch-id | `9e272d09e085eb31776617badac36f2fd85fa190` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/87f09e4_irqchip_gic_v3_its__Introduce_the_reserved_device_.patch`

**目标提交候选**:
- `19cee9a7eb6de31030fd3b8aa13d132b3c40ee0d`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/misc/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 10: irqchip/gic-v3-its: Add ACPI_IORT as VIRT_PLAT_DEV's dependency

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8bc36d3_irqchip_gic_v3_its__Add_ACPI_IORT_as_VIRT_PLAT_DEV.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8bc36d3_irqchip_gic_v3_its__Add_ACPI_IORT_as_VIRT_PLAT_DEV.patch` |
| 本地提交 | `8bc36d370007` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `af35d669190fc0217256009a48f6910469c1a4fd` |
| 目标标题 | irqchip/gic-v3-its: Add ACPI_IORT as VIRT_PLAT_DEV's dependency |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `783515aa6a6457c651cfdefaae00228c56fed5d4` |
| 目标 patch-id | `3444fdd052672f602296f36722b68092d6d3453e` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/8bc36d3_irqchip_gic_v3_its__Add_ACPI_IORT_as_VIRT_PLAT_DEV.patch`

**目标提交候选**:
- `af35d669190fc0217256009a48f6910469c1a4fd`

### 文件 1: `drivers/misc/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 63.9% | Hunk content matches (layout differs) |


---

## 补丁 11: irqchip/gic-v3-its: Move build_devid_pools from its to acpi iort init

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `af552f9_irqchip_gic_v3_its__Move_build_devid_pools_from_it.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/af552f9_irqchip_gic_v3_its__Move_build_devid_pools_from_it.patch` |
| 本地提交 | `af552f9d957d` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `831632dfd25b87ed7fba8b716b2cdd4da0e75a9e` |
| 目标标题 | irqchip/gic-v3-its: Move build_devid_pools from its to acpi iort init |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `79af01c60c7c6c7ee0caff4183b66ffbe2776dc3` |
| 目标 patch-id | `1ad4e7c6b445e8e3f4fe41eb182ea636f3a4d41d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/af552f9_irqchip_gic_v3_its__Move_build_devid_pools_from_it.patch`

**目标提交候选**:
- `831632dfd25b87ed7fba8b716b2cdd4da0e75a9e`

### 文件 1: `drivers/acpi/arm64/iort.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ❌ `different`

*备注*: File diff differs

**删除行不一致**:
- `#ifdef CONFIG_VIRT_PLAT_DEV`
- ``

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 85.9% | Hunk content matches (layout differs) |
| 3 | 3 | `different` | 77.4% | Hunk content differs |


---

## 补丁 12: KVM: arm64: kire: irq routing entry cached the relevant cache data

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e25e2fd_KVM__arm64__kire__irq_routing_entry_cached_the_rel.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e25e2fd_KVM__arm64__kire__irq_routing_entry_cached_the_rel.patch` |
| 本地提交 | `e25e2fd49400` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `1cdf9bea7dd424565e19a185d4736028b07c523f` |
| 目标标题 | KVM: arm64: kire: irq routing entry cached the relevant cache data |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `73647feb5704a4b85a399ed7113cba64d8920c57` |
| 目标 patch-id | `73647feb5704a4b85a399ed7113cba64d8920c57` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/e25e2fd_KVM__arm64__kire__irq_routing_entry_cached_the_rel.patch`

**目标提交候选**:
- `1cdf9bea7dd424565e19a185d4736028b07c523f`

### 文件 1: `arch/arm64/kvm/vgic/vgic-irqfd.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/linux/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `virt/kvm/eventfd.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 13: acpi/iort: Add func to get used deviceid bitmap

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `f234395_acpi_iort__Add_func_to_get_used_deviceid_bitmap.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/f234395_acpi_iort__Add_func_to_get_used_deviceid_bitmap.patch` |
| 本地提交 | `f234395f459d` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `8ef2d8af21d4bbea1b1b83c743ff3aa85969a51a` |
| 目标标题 | acpi/iort: Add func to get used deviceid bitmap |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `866fbf807b554d6d90a137359509db8f441f145a` |
| 目标 patch-id | `e6466732719c129f2e46157a94be828bb8a275c3` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/f234395_acpi_iort__Add_func_to_get_used_deviceid_bitmap.patch`

**目标提交候选**:
- `8ef2d8af21d4bbea1b1b83c743ff3aa85969a51a`

### 文件 1: `drivers/acpi/arm64/iort.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `#ifdef CONFIG_VIRT_PLAT_DEV`
- `#include <linux/pci.h>`
- `#endif`
- ``

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 84.4% | Hunk content differs |


### 文件 3: `include/linux/acpi_iort.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 80.3% | Hunk content matches (layout differs) |


---

## 术语说明

| 状态 | 含义 |
|------|------|
| ✅ 完全一致 (IDENTICAL) | 本地补丁与目标仓库已合入提交的 diff 完全一致 |
| ❌ 存在差异 (DIFFERENT) | 已找到对应提交，但 diff 内容存在缺失行、额外行或删除侧不一致 |
| ❓ 未匹配 (UNMATCHED) | 未找到对应本地补丁，或本地补丁未找到对应目标提交 |
| ⚠️ 匹配歧义 (AMBIGUOUS) | 本地补丁映射存在多个候选，无法安全自动判断 |

---

*报告由 patch-validator 自动生成*
