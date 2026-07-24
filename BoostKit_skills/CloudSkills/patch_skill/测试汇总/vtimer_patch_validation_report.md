# 补丁已合入差异报告

> **生成时间**: 2026-03-31 15:35:40
> **目标仓库**: `/home/xxd/velinux-kernel`
> **目标分支**: `auto-patch-20260331_144625`
> **模式**: `merged-diff`

---

## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | 22 |
| 本地补丁文件数 | 22 |
| 已匹配目标提交 | 22 |
| 未匹配目标提交 | 0 |
| 歧义目标提交 | 0 |
| 完全一致 | 20 |
| 存在差异 | 2 |
| 未匹配 | 0 |
| 匹配歧义 | 0 |

> **整体状态**: ❌ 已发现本地补丁与目标仓库已合入补丁存在差异

---

## 详细结果

## 补丁 1: KVM: arm64: GICv4.1: Allow non-trapping WFI when using direct vtimer interrupt

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1582ce5_KVM__arm64__GICv4_1__Allow_non_trapping_WFI_when_u.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1582ce5_KVM__arm64__GICv4_1__Allow_non_trapping_WFI_when_u.patch` |
| 本地提交 | `1582ce57947c` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `1bf9d12ea131ac366e13c561fc0f4345f0113c06` |
| 目标标题 | KVM: arm64: GICv4.1: Allow non-trapping WFI when using direct vtimer interrupt |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `d62c38a753e79214f3856ae6ab772fc95143ec66` |
| 目标 patch-id | `d62c38a753e79214f3856ae6ab772fc95143ec66` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/1582ce5_KVM__arm64__GICv4_1__Allow_non_trapping_WFI_when_u.patch`

**目标提交候选**:
- `1bf9d12ea131ac366e13c561fc0f4345f0113c06`

### 文件 1: `arch/arm64/include/asm/kvm_emulate.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 2: mbigen: vtimer: isolate mbigen vtimer funcs with macro

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1f51042_mbigen__vtimer__isolate_mbigen_vtimer_funcs_with_m.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1f51042_mbigen__vtimer__isolate_mbigen_vtimer_funcs_with_m.patch` |
| 本地提交 | `1f510421c1c8` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `b1aa9023a467fa7664b6f334d1e5d8831b28bc93` |
| 目标标题 | mbigen: vtimer: isolate mbigen vtimer funcs with macro |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `fe68d6ecb60f483e738b57938c4bab7cc6deb6e5` |
| 目标 patch-id | `4e6e18ba8007617f946dbc76b5791bc38d254830` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/1f51042_mbigen__vtimer__isolate_mbigen_vtimer_funcs_with_m.patch`

**目标提交候选**:
- `b1aa9023a467fa7664b6f334d1e5d8831b28bc93`

### 文件 1: `arch/arm64/configs/openeuler_defconfig`

**状态**: ❌ `missing-file`

*备注*: Merged commit does not contain this file diff

**本地补丁有、目标已合入补丁缺失的新增行**:
- `CONFIG_VIRT_VTIMER_IRQ_BYPASS=y`


### 文件 2: `arch/arm64/kvm/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 91.8% | Hunk content matches (layout differs) |


### 文件 3: `config.aarch64`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_VIRT_VTIMER_IRQ_BYPASS=y`


### 文件 4: `config.aarch64-64k`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_VIRT_VTIMER_IRQ_BYPASS=y`


---

## 补丁 3: irqchip/gic-v4.1: Rework get/set_irqchip_state callbacks of GICv4.1-sgi chip

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `33fb8a2_irqchip_gic_v4_1__Rework_get_set_irqchip_state_cal.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/33fb8a2_irqchip_gic_v4_1__Rework_get_set_irqchip_state_cal.patch` |
| 本地提交 | `33fb8a258e00` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `764710b8cb4b4a395da30d1ced9425d9ee56d49d` |
| 目标标题 | irqchip/gic-v4.1: Rework get/set_irqchip_state callbacks of GICv4.1-sgi chip |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `480a7ba941120f6236d4682b67a785623cdc51bb` |
| 目标 patch-id | `480a7ba941120f6236d4682b67a785623cdc51bb` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/33fb8a2_irqchip_gic_v4_1__Rework_get_set_irqchip_state_cal.patch`

**目标提交候选**:
- `764710b8cb4b4a395da30d1ced9425d9ee56d49d`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 4: KVM: arm64: arch_timer: Rework vcpu init/reset logic

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `377d438_KVM__arm64__arch_timer__Rework_vcpu_init_reset_log.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/377d438_KVM__arm64__arch_timer__Rework_vcpu_init_reset_log.patch` |
| 本地提交 | `377d438f90c9` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `586f343150f822d53b199b285d7890dde61f6929` |
| 目标标题 | KVM: arm64: arch_timer: Rework vcpu init/reset logic |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `4d489ba75af59a37f90247af3b4bd877aabb3f44` |
| 目标 patch-id | `4d489ba75af59a37f90247af3b4bd877aabb3f44` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/377d438_KVM__arm64__arch_timer__Rework_vcpu_init_reset_log.patch`

**目标提交候选**:
- `586f343150f822d53b199b285d7890dde61f6929`

### 文件 1: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/kvm/arm_arch_timer.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 5: irqchip/gic-v4.1: Detect ITS vtimer interrupt bypass capability

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `37bd072_irqchip_gic_v4_1__Detect_ITS_vtimer_interrupt_bypa.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/37bd072_irqchip_gic_v4_1__Detect_ITS_vtimer_interrupt_bypa.patch` |
| 本地提交 | `37bd0722b681` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `0336971924a126096ea40331d940847f90a5dabc` |
| 目标标题 | irqchip/gic-v4.1: Detect ITS vtimer interrupt bypass capability |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `6180fb9c42a6436a286228f6de4bd5db66f001f5` |
| 目标 patch-id | `6180fb9c42a6436a286228f6de4bd5db66f001f5` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/37bd072_irqchip_gic_v4_1__Detect_ITS_vtimer_interrupt_bypa.patch`

**目标提交候选**:
- `0336971924a126096ea40331d940847f90a5dabc`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 6: KVM: arm64: vtimer: Expose HW-based vtimer interrupt in debugfs

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `3baae1d_KVM__arm64__vtimer__Expose_HW_based_vtimer_interru.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/3baae1d_KVM__arm64__vtimer__Expose_HW_based_vtimer_interru.patch` |
| 本地提交 | `3baae1d5ed54` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `cef22d5e95b28317fd21bd4eeca062f6b706338d` |
| 目标标题 | KVM: arm64: vtimer: Expose HW-based vtimer interrupt in debugfs |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `4def1c8506db7683100bce663387076dc2c85f8d` |
| 目标 patch-id | `4def1c8506db7683100bce663387076dc2c85f8d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/3baae1d_KVM__arm64__vtimer__Expose_HW_based_vtimer_interru.patch`

**目标提交候选**:
- `cef22d5e95b28317fd21bd4eeca062f6b706338d`

### 文件 1: `arch/arm64/kvm/vgic/vgic-debug.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 7: mbigen: vtimer mbigen driver support

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `3ce0ad7_mbigen__vtimer_mbigen_driver_support.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/3ce0ad7_mbigen__vtimer_mbigen_driver_support.patch` |
| 本地提交 | `3ce0ad7d0b4c` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `06231d3c58a5cb720f2ed778d647ab12fa456291` |
| 目标标题 | mbigen: vtimer mbigen driver support |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `d4927aa0eb7e57aaf0e7acc60bda7a7c838285b9` |
| 目标 patch-id | `2750b0a9567c409d337552e011216acd7e8bbba0` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/3ce0ad7_mbigen__vtimer_mbigen_driver_support.patch`

**目标提交候选**:
- `06231d3c58a5cb720f2ed778d647ab12fa456291`

### 文件 1: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-mbigen.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 99.4% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 98.8% | Hunk content matches (layout differs) |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/clocksource/arm_arch_timer.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 8: KVM: arm64: GICv4.1: Enable vtimer vPPI irqbypass config

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `513b107_KVM__arm64__GICv4_1__Enable_vtimer_vPPI_irqbypass_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/513b107_KVM__arm64__GICv4_1__Enable_vtimer_vPPI_irqbypass_.patch` |
| 本地提交 | `513b107ef8b7` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `3358213741f6d9d0c55639116a1f2ed62d029855` |
| 目标标题 | KVM: arm64: GICv4.1: Enable vtimer vPPI irqbypass config |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `ba44b42735a543e784b7b74db0a4d6df08d73e9d` |
| 目标 patch-id | `0c17fdfbb6705e2de25b56adbd766d340ce1554d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/513b107_KVM__arm64__GICv4_1__Enable_vtimer_vPPI_irqbypass_.patch`

**目标提交候选**:
- `3358213741f6d9d0c55639116a1f2ed62d029855`

### 文件 1: `arch/arm64/kvm/vgic/vgic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/vgic/vgic-v4.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/vgic/vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 90.4% | Hunk content matches (layout differs) |


---

## 补丁 9: KVM: arm64: GICv4.1: Add direct injection capability to PPI registers

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `59b9f94_KVM__arm64__GICv4_1__Add_direct_injection_capabili.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/59b9f94_KVM__arm64__GICv4_1__Add_direct_injection_capabili.patch` |
| 本地提交 | `59b9f9490de6` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5b381d1968d97267d9b9fd9657eb76ce0404161f` |
| 目标标题 | KVM: arm64: GICv4.1: Add direct injection capability to PPI registers |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `4a54a5e7a8e5d52013701d566d14db6066dc502b` |
| 目标 patch-id | `6ca60a468bc4a0d34a5572277b185c5f4c305661` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/59b9f94_KVM__arm64__GICv4_1__Add_direct_injection_capabili.patch`

**目标提交候选**:
- `5b381d1968d97267d9b9fd9657eb76ce0404161f`

### 文件 1: `arch/arm64/kvm/vgic/vgic-mmio.c`

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
| 7 | 7 | `identical` | 100.0% | Hunk content matches |
| 8 | 8 | `identical` | 100.0% | Hunk content matches |
| 9 | 9 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/vgic/vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 95.0% | Hunk content matches (layout differs) |


---

## 补丁 10: KVM: arm64: vgic: Add helper for vtimer vppi info register

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `5c691ec_KVM__arm64__vgic__Add_helper_for_vtimer_vppi_info_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/5c691ec_KVM__arm64__vgic__Add_helper_for_vtimer_vppi_info_.patch` |
| 本地提交 | `5c691ec3c74a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `c156a5cd70d507e70d8be640a296393d1779c3c4` |
| 目标标题 | KVM: arm64: vgic: Add helper for vtimer vppi info register |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `a4cb424ee1095bc22c662fc7bf8eb7e04e71b1a4` |
| 目标 patch-id | `5f052022ebae0cfd403c93bd34fcc41f3e443392` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/5c691ec_KVM__arm64__vgic__Add_helper_for_vtimer_vppi_info_.patch`

**目标提交候选**:
- `c156a5cd70d507e70d8be640a296393d1779c3c4`

### 文件 1: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/vgic/vgic.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 89.6% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 11: KVM: arm64: arch_timer: Make vtimer_irqbypass a Distributor attr

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `747c447_KVM__arm64__arch_timer__Make_vtimer_irqbypass_a_Di.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/747c447_KVM__arm64__arch_timer__Make_vtimer_irqbypass_a_Di.patch` |
| 本地提交 | `747c447574f3` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `f38d4e4d37101b37bfe20f3ca54a01850fa1bb6c` |
| 目标标题 | KVM: arm64: arch_timer: Make vtimer_irqbypass a Distributor attr |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `194f09dc1921b5670192657dc358ad4e379ebfba` |
| 目标 patch-id | `194f09dc1921b5670192657dc358ad4e379ebfba` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/747c447_KVM__arm64__arch_timer__Make_vtimer_irqbypass_a_Di.patch`

**目标提交候选**:
- `f38d4e4d37101b37bfe20f3ca54a01850fa1bb6c`

### 文件 1: `arch/arm64/include/asm/kvm_emulate.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/vgic/vgic-v4.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/vgic/vgic.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `include/kvm/arm_arch_timer.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 12: KVM: arm64: GICv4.1: Add support for MBIGEN save/restore

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `78feb45_KVM__arm64__GICv4_1__Add_support_for_MBIGEN_save_r.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/78feb45_KVM__arm64__GICv4_1__Add_support_for_MBIGEN_save_r.patch` |
| 本地提交 | `78feb450c1fb` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `a094212916b3946adb1b4cc65435629be47408d1` |
| 目标标题 | KVM: arm64: GICv4.1: Add support for MBIGEN save/restore |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `b9eb17ede9d127a6c7d2528415e0ba8c999031be` |
| 目标 patch-id | `b9eb17ede9d127a6c7d2528415e0ba8c999031be` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/78feb45_KVM__arm64__GICv4_1__Add_support_for_MBIGEN_save_r.patch`

**目标提交候选**:
- `a094212916b3946adb1b4cc65435629be47408d1`

### 文件 1: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/vgic/vgic-v4.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/kvm/arm_arch_timer.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `include/kvm/arm_vgic.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 13: mbigen: probe mbigen driver with arch_initcall

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `7e3e12f_mbigen__probe_mbigen_driver_with_arch_initcall.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/7e3e12f_mbigen__probe_mbigen_driver_with_arch_initcall.patch` |
| 本地提交 | `7e3e12fd43da` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `6822b1dd56db2fb2b4635cfbf60d2cfa572be82d` |
| 目标标题 | mbigen: probe mbigen driver with arch_initcall |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `5ee0bb6a95b09d562f44a2d21bf2b4f4116ffe9b` |
| 目标 patch-id | `5ee0bb6a95b09d562f44a2d21bf2b4f4116ffe9b` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/7e3e12f_mbigen__probe_mbigen_driver_with_arch_initcall.patch`

**目标提交候选**:
- `6822b1dd56db2fb2b4635cfbf60d2cfa572be82d`

### 文件 1: `drivers/irqchip/irq-mbigen.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 14: irqchip/gic-v4.1: Extend VSGI command to support the new vPPI

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `89929a9_irqchip_gic_v4_1__Extend_VSGI_command_to_support_t.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/89929a9_irqchip_gic_v4_1__Extend_VSGI_command_to_support_t.patch` |
| 本地提交 | `89929a9b4cdf` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `349a05cba5377a2ac1634113e63a25af7cc466e7` |
| 目标标题 | irqchip/gic-v4.1: Extend VSGI command to support the new vPPI |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `e4f69abc16d1da37098d4d66e6a456753195f438` |
| 目标 patch-id | `f5e7098b9d8737c4e2e2844887ba3016f60f6d1a` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/89929a9_irqchip_gic_v4_1__Extend_VSGI_command_to_support_t.patch`

**目标提交候选**:
- `349a05cba5377a2ac1634113e63a25af7cc466e7`

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


### 文件 2: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 47.9% | Hunk content is covered by another aligned hunk |
| 2 | None | `identical` | 0.0% | Hunk content is covered by another aligned hunk |


### 文件 3: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 15: irqchip/gic-v4.1: Probe vtimer irqbypass capability at RD level

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `9b916d2_irqchip_gic_v4_1__Probe_vtimer_irqbypass_capabilit.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/9b916d2_irqchip_gic_v4_1__Probe_vtimer_irqbypass_capabilit.patch` |
| 本地提交 | `9b916d2aa2a9` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `46008bd3c4cafba0bbd19ab21976807658e94f98` |
| 目标标题 | irqchip/gic-v4.1: Probe vtimer irqbypass capability at RD level |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `230c28b99538c035ebc9cccfd1c29aaa5c99729e` |
| 目标 patch-id | `230c28b99538c035ebc9cccfd1c29aaa5c99729e` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/9b916d2_irqchip_gic_v4_1__Probe_vtimer_irqbypass_capabilit.patch`

**目标提交候选**:
- `46008bd3c4cafba0bbd19ab21976807658e94f98`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `include/linux/irqchip/arm-vgic-info.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 16: KVM: arm64: vgic-v3: Clearing pending status of vtimer on guest reset

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `9e9b442_KVM__arm64__vgic_v3__Clearing_pending_status_of_vt.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/9e9b442_KVM__arm64__vgic_v3__Clearing_pending_status_of_vt.patch` |
| 本地提交 | `9e9b44275df8` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `f862f66cb10234e80bf544c05d17fe28a0036409` |
| 目标标题 | KVM: arm64: vgic-v3: Clearing pending status of vtimer on guest reset |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `7b4f727310b86c6633efe97e98d685d89bf06c5a` |
| 目标 patch-id | `29f1369fad9fca21a8e6d6e47904496aede558bd` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/9e9b442_KVM__arm64__vgic_v3__Clearing_pending_status_of_vt.patch`

**目标提交候选**:
- `f862f66cb10234e80bf544c05d17fe28a0036409`

### 文件 1: `arch/arm64/kvm/vgic/vgic-mmio-v3.c`

**状态**: ❌ `different`

*备注*: File diff differs

**目标已合入补丁额外包含的新增行**:
- `		if (irq->pending_latch) {`
- `		} else {`
- `		}`

**删除行不一致**:
- `		if (irq->pending_latch)`
- `		else`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 89.1% | Hunk content differs |


---

## 补丁 17: mbigen: Sets the regs related to vtimer irqbypass

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b8b70fe_mbigen__Sets_the_regs_related_to_vtimer_irqbypass.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b8b70fe_mbigen__Sets_the_regs_related_to_vtimer_irqbypass.patch` |
| 本地提交 | `b8b70fe6bcf0` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `74d895f760a98334876e487f230175c85d692a31` |
| 目标标题 | mbigen: Sets the regs related to vtimer irqbypass |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `e60dc1f74ad710cecee683b145ab376ce79810d0` |
| 目标 patch-id | `e60dc1f74ad710cecee683b145ab376ce79810d0` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/b8b70fe_mbigen__Sets_the_regs_related_to_vtimer_irqbypass.patch`

**目标提交候选**:
- `74d895f760a98334876e487f230175c85d692a31`

### 文件 1: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-mbigen.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 18: KVM: arm64: arch_timer: Probe vtimer irqbypass capability

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `d306753_KVM__arm64__arch_timer__Probe_vtimer_irqbypass_cap.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/d306753_KVM__arm64__arch_timer__Probe_vtimer_irqbypass_cap.patch` |
| 本地提交 | `d306753c582d` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `76e7235ca0003def21236457963540020ee01372` |
| 目标标题 | KVM: arm64: arch_timer: Probe vtimer irqbypass capability |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `9a5ed61f4cdfdb0d59e9df7bc605ebe8d8b8e6d6` |
| 目标 patch-id | `9a5ed61f4cdfdb0d59e9df7bc605ebe8d8b8e6d6` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/d306753_KVM__arm64__arch_timer__Probe_vtimer_irqbypass_cap.patch`

**目标提交候选**:
- `76e7235ca0003def21236457963540020ee01372`

### 文件 1: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 19: irqchip/gic-v4.1: Rework its_alloc_vcpu_sgis() to support vPPI allocation

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `d766e9d_irqchip_gic_v4_1__Rework_its_alloc_vcpu_sgis___to_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/d766e9d_irqchip_gic_v4_1__Rework_its_alloc_vcpu_sgis___to_.patch` |
| 本地提交 | `d766e9d99817` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `868ef2e27f5a8170db653f0879c2a7cdc8249eed` |
| 目标标题 | irqchip/gic-v4.1: Rework its_alloc_vcpu_sgis() to support vPPI allocation |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `073f673b672f081245ce5a231b89c19bfdc32a6b` |
| 目标 patch-id | `9792c9857dcc1933235e8340b0bf74d85590c8ff` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/d766e9d_irqchip_gic_v4_1__Rework_its_alloc_vcpu_sgis___to_.patch`

**目标提交候选**:
- `868ef2e27f5a8170db653f0879c2a7cdc8249eed`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v4.c`

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


### 文件 3: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 94.2% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 20: mbigen: vtimer: disable vtimer mbigen probe when vtimer_irqbypass disabled

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `db01928_mbigen__vtimer__disable_vtimer_mbigen_probe_when_v.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/db01928_mbigen__vtimer__disable_vtimer_mbigen_probe_when_v.patch` |
| 本地提交 | `db019283fc0e` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `bd69d4ef7efcc4c2a1fce9410929b40f2ee88aa8` |
| 目标标题 | mbigen: vtimer: disable vtimer mbigen probe when vtimer_irqbypass disabled |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `0cf1b96e35baf3199d6bec0c10dc741d8cb2ee5f` |
| 目标 patch-id | `0cf1b96e35baf3199d6bec0c10dc741d8cb2ee5f` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/db01928_mbigen__vtimer__disable_vtimer_mbigen_probe_when_v.patch`

**目标提交候选**:
- `bd69d4ef7efcc4c2a1fce9410929b40f2ee88aa8`

### 文件 1: `drivers/irqchip/irq-mbigen.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 21: KVM: arm64: GICv4.1: Inform the HiSilicon vtimer irqbypass capability

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e035284_KVM__arm64__GICv4_1__Inform_the_HiSilicon_vtimer_i.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e035284_KVM__arm64__GICv4_1__Inform_the_HiSilicon_vtimer_i.patch` |
| 本地提交 | `e0352844a73e` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `133a4d197a9bbdc39ad371aa661eb790072d1eb5` |
| 目标标题 | KVM: arm64: GICv4.1: Inform the HiSilicon vtimer irqbypass capability |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `fa9d84e9c7a5044a33ae271d217121b894421db4` |
| 目标 patch-id | `fa9d84e9c7a5044a33ae271d217121b894421db4` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/e035284_KVM__arm64__GICv4_1__Inform_the_HiSilicon_vtimer_i.patch`

**目标提交候选**:
- `133a4d197a9bbdc39ad371aa661eb790072d1eb5`

### 文件 1: `arch/arm64/kvm/vgic/vgic-v3.c`

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
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 22: mbigen: vtimer: add support for MBIX1_CPPI_NEGEDGE_CLR_EN_SETR(CLRR)

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e981deb_mbigen__vtimer__add_support_for_MBIX1_CPPI_NEGEDGE.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e981deb_mbigen__vtimer__add_support_for_MBIX1_CPPI_NEGEDGE.patch` |
| 本地提交 | `e981deb1790c` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `7b2a8234c3bea9001b27282f88bf6e74ceff2ee0` |
| 目标标题 | mbigen: vtimer: add support for MBIX1_CPPI_NEGEDGE_CLR_EN_SETR(CLRR) |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `672f39d977a78d1933a0e9c4a4cc698aeb1e204d` |
| 目标 patch-id | `672f39d977a78d1933a0e9c4a4cc698aeb1e204d` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/e981deb_mbigen__vtimer__add_support_for_MBIX1_CPPI_NEGEDGE.patch`

**目标提交候选**:
- `7b2a8234c3bea9001b27282f88bf6e74ceff2ee0`

### 文件 1: `arch/arm64/kvm/arch_timer.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-mbigen.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/clocksource/arm_arch_timer.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


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
