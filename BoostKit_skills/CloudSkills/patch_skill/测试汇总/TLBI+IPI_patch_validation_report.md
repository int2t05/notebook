# 补丁已合入差异报告

> **生成时间**: 2026-03-31 21:48:22
> **目标仓库**: `/home/xxd/velinux-kernel`
> **目标分支**: `auto-patch-20260331_204826`
> **模式**: `merged-diff`

---

## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | 37 |
| 本地补丁文件数 | 37 |
| 已匹配目标提交 | 35 |
| 未匹配目标提交 | 2 |
| 歧义目标提交 | 0 |
| 完全一致 | 27 |
| 存在差异 | 8 |
| 未匹配 | 2 |
| 匹配歧义 | 0 |

> **整体状态**: ❌ 已发现本地补丁与目标仓库已合入补丁存在差异

---

## 详细结果

## 补丁 1: KVM: arm64: Only probe Hisi ncsnp feature on Hisi CPUs

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `029e24e_KVM__arm64__Only_probe_Hisi_ncsnp_feature_on_Hisi_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/029e24e_KVM__arm64__Only_probe_Hisi_ncsnp_feature_on_Hisi_.patch` |
| 本地提交 | `029e24ef7b17` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `29f00427963bccd9223babbcbe8bbe6212c0ba6e` |
| 目标标题 | KVM: arm64: Only probe Hisi ncsnp feature on Hisi CPUs |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `b3fa9ed3eeea268f860816fe0fc79a3b708983cc` |
| 目标 patch-id | `8778629e75a8d2006069efc8a77636273f4ffc92` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/029e24e_KVM__arm64__Only_probe_Hisi_ncsnp_feature_on_Hisi_.patch`

**目标提交候选**:
- `29f00427963bccd9223babbcbe8bbe6212c0ba6e`

### 文件 1: `arch/arm64/configs/openeuler_defconfig`

**状态**: ❌ `missing-file`

*备注*: Merged commit does not contain this file diff

**本地补丁有、目标已合入补丁缺失的新增行**:
- `CONFIG_KVM_HISI_VIRT=y`


### 文件 2: `/dev/null`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kernel/image-vars.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `arch/arm64/kvm/Makefile`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 8: `/dev/null`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 9: `arch/arm64/kvm/hisilicon/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 10: `arch/arm64/kvm/hisilicon/Makefile`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 11: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 12: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 13: `config.aarch64`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_KVM_HISI_VIRT=y`


### 文件 14: `config.aarch64-64k`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_KVM_HISI_VIRT=y`


---

## 补丁 2: kvm: hisi: make sure vcpu_id and vcpu_idx have same value in IPIv

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0754497_kvm__hisi__make_sure_vcpu_id_and_vcpu_idx_have_sam.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0754497_kvm__hisi__make_sure_vcpu_id_and_vcpu_idx_have_sam.patch` |
| 本地提交 | `075449783bf2` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `0fd6973ba43dd416991184bd2acbf36323da69b0` |
| 目标标题 | kvm: hisi: make sure vcpu_id and vcpu_idx have same value in IPIv |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `1d5494bb56ca684f23d6c64e4b90e70f94ed8f4b` |
| 目标 patch-id | `1d5494bb56ca684f23d6c64e4b90e70f94ed8f4b` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/0754497_kvm__hisi__make_sure_vcpu_id_and_vcpu_idx_have_sam.patch`

**目标提交候选**:
- `0fd6973ba43dd416991184bd2acbf36323da69b0`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 3: irqchip/gic: Add HiSilicon PV SGI support

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `09d8e92_irqchip_gic__Add_HiSilicon_PV_SGI_support.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/09d8e92_irqchip_gic__Add_HiSilicon_PV_SGI_support.patch` |
| 本地提交 | `09d8e9218695` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `36cce6954b9fe0f71c500e19ded29f3c9bb956bf` |
| 目标标题 | irqchip/gic: Add HiSilicon PV SGI support |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `4a1821677234a0fc7b81c995d06ae720f9a3f351` |
| 目标 patch-id | `4a1821677234a0fc7b81c995d06ae720f9a3f351` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/09d8e92_irqchip_gic__Add_HiSilicon_PV_SGI_support.patch`

**目标提交候选**:
- `36cce6954b9fe0f71c500e19ded29f3c9bb956bf`

### 文件 1: `arch/arm64/kvm/sys_regs.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3.c`

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

## 补丁 4: KVM: arm64: ipiv: change declaration argument

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0a93f3e_KVM__arm64__ipiv__change_declaration_argument.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0a93f3e_KVM__arm64__ipiv__change_declaration_argument.patch` |
| 本地提交 | `0a93f3e2d545` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `10e53c2a1e17527201926db944a1400202058af6` |
| 目标标题 | KVM: arm64: ipiv: change declaration argument |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `b2c168a62b3648de9e0a3b8d7b083074464ac28c` |
| 目标 patch-id | `6d6e91dd9edb962e8892a8c42f15b4253433ea8f` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/0a93f3e_KVM__arm64__ipiv__change_declaration_argument.patch`

**目标提交候选**:
- `10e53c2a1e17527201926db944a1400202058af6`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `static inline bool hisi_ipiv_supported_per_vm(struct kvm *kvm)`
- `static inline void hisi_ipiv_enable_per_vm(struct kvm *kvm) {}`

**目标已合入补丁额外包含的新增行**:
- `static bool hisi_ipiv_supported_per_vm(struct kvm *kvm)`
- `static void hisi_ipiv_enable_per_vm(struct kvm *kvm) {}`

**删除行不一致**:
- `static inline bool hisi_ipiv_supported_per_vm(struct kvm_vcpu *vcpu)`
- `static inline void hisi_ipiv_enable_per_vm(struct kvm_vcpu *vcpu) {}`
- `static bool hisi_ipiv_supported_per_vm(struct kvm_vcpu *vcpu)`
- `static void hisi_ipiv_enable_per_vm(struct kvm_vcpu *vcpu) {}`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 96.8% | Hunk content differs |


---

## 补丁 5: KVM: arm64: Add new HiSi CPU type to support DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0c2bca0_KVM__arm64__Add_new_HiSi_CPU_type_to_support_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0c2bca0_KVM__arm64__Add_new_HiSi_CPU_type_to_support_DVMBM.patch` |
| 本地提交 | `0c2bca09f8af` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `32cc38af0f8f4db899c73c18ddc35ad715c74d11` |
| 目标标题 | KVM: arm64: Add new HiSi CPU type to support DVMBM |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `a3a7544fa06cf8b70d1b8a7ab0fc4a0072ad9cd1` |
| 目标 patch-id | `a3a7544fa06cf8b70d1b8a7ab0fc4a0072ad9cd1` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/0c2bca0_KVM__arm64__Add_new_HiSi_CPU_type_to_support_DVMBM.patch`

**目标提交候选**:
- `32cc38af0f8f4db899c73c18ddc35ad715c74d11`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 6: KVM: arm64: Add new HiSi CPU type for supporting DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0fb85a6_KVM__arm64__Add_new_HiSi_CPU_type_for_supporting_D.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0fb85a6_KVM__arm64__Add_new_HiSi_CPU_type_for_supporting_D.patch` |
| 本地提交 | `0fb85a6177b5` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `9b4cb0c62b2ce30baf78282b27e8f4a6d8227bde` |
| 目标标题 | KVM: arm64: Add new HiSi CPU type for supporting DVMBM |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `9fc1713c8905c3f870832240ab20022c6d44d6b9` |
| 目标 patch-id | `9fc1713c8905c3f870832240ab20022c6d44d6b9` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/0fb85a6_KVM__arm64__Add_new_HiSi_CPU_type_for_supporting_D.patch`

**目标提交候选**:
- `9b4cb0c62b2ce30baf78282b27e8f4a6d8227bde`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 7: KVM: arm64: Document PV-sgi interface

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `11c4602_KVM__arm64__Document_PV_sgi_interface.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/11c4602_KVM__arm64__Document_PV_sgi_interface.patch` |
| 本地提交 | `11c4602610dd` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `e59adc8e0a6c70e916b191304e8ef0ff2e549760` |
| 目标标题 | KVM: arm64: Document PV-sgi interface |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `0d9c49aee4c754c376ec2dc14654855837b98b25` |
| 目标 patch-id | `0d9c49aee4c754c376ec2dc14654855837b98b25` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/11c4602_KVM__arm64__Document_PV_sgi_interface.patch`

**目标提交候选**:
- `e59adc8e0a6c70e916b191304e8ef0ff2e549760`

### 文件 1: `Documentation/virt/kvm/arm/hypercalls.rst`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `Documentation/virt/kvm/arm/pvsgi.rst`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 8: KVM: arm64: fix memory leak in TLBI

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `18c863e_KVM__arm64__fix_memory_leak_in_TLBI.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/18c863e_KVM__arm64__fix_memory_leak_in_TLBI.patch` |
| 本地提交 | `18c863e22109` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `e782525ee85e2a63c13a2262311451652450f289` |
| 目标标题 | KVM: arm64: fix memory leak in TLBI |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `55afafe7bb3589d395ccebf9117cff8433f1f04c` |
| 目标 patch-id | `55afafe7bb3589d395ccebf9117cff8433f1f04c` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/18c863e_KVM__arm64__fix_memory_leak_in_TLBI.patch`

**目标提交候选**:
- `e782525ee85e2a63c13a2262311451652450f289`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 9: KVM: arm64: Add kvm_vcpu_arch::sched_cpus and pre_sched_cpus

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1c342c1_KVM__arm64__Add_kvm_vcpu_arch__sched_cpus_and_pre_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1c342c1_KVM__arm64__Add_kvm_vcpu_arch__sched_cpus_and_pre_.patch` |
| 本地提交 | `1c342c1a8d0a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `55fbc4564a467ed352428e2fb3c178222b9ed102` |
| 目标标题 | KVM: arm64: Add kvm_vcpu_arch::sched_cpus and pre_sched_cpus |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `ff2020063f472c9fc9c62dce2a1032177aa0e464` |
| 目标 patch-id | `11c9c36aa5335f8e725001e86838c5c9c82181fe` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/1c342c1_KVM__arm64__Add_kvm_vcpu_arch__sched_cpus_and_pre_.patch`

**目标提交候选**:
- `55fbc4564a467ed352428e2fb3c178222b9ed102`

### 文件 1: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 86.5% | Hunk content matches (layout differs) |
| 3 | 3 | `identical` | 92.2% | Hunk content matches (layout differs) |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |
| 6 | 6 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 10: KVM: arm64: ipiv: fix bug in live migration

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `22f1e3b_KVM__arm64__ipiv__fix_bug_in_live_migration.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/22f1e3b_KVM__arm64__ipiv__fix_bug_in_live_migration.patch` |
| 本地提交 | `22f1e3b38ca0` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `c08df2241790dcd8547dfb0657ebfdc6e156ff69` |
| 目标标题 | KVM: arm64: ipiv: fix bug in live migration |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `889fa6b60b619109437d9637c11278010f409ef4` |
| 目标 patch-id | `889fa6b60b619109437d9637c11278010f409ef4` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/22f1e3b_KVM__arm64__ipiv__fix_bug_in_live_migration.patch`

**目标提交候选**:
- `c08df2241790dcd8547dfb0657ebfdc6e156ff69`

### 文件 1: `arch/arm64/kvm/vgic/vgic-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 11: kvm: hisi_virt: Update TLBI broadcast feature for hip12

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `2671ba2_kvm__hisi_virt__Update_TLBI_broadcast_feature_for_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/2671ba2_kvm__hisi_virt__Update_TLBI_broadcast_feature_for_.patch` |
| 本地提交 | `2671ba221968` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5edb4f0450b5a0b8b1a1d56b5d1d59f399ef27f1` |
| 目标标题 | kvm: hisi_virt: Update TLBI broadcast feature for hip12 |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `73074758e10946bc675c4ba6e29cc53d690f82dc` |
| 目标 patch-id | `73074758e10946bc675c4ba6e29cc53d690f82dc` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/2671ba2_kvm__hisi_virt__Update_TLBI_broadcast_feature_for_.patch`

**目标提交候选**:
- `5edb4f0450b5a0b8b1a1d56b5d1d59f399ef27f1`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 12: kvm: hisi_virt: Register ipiv exception interrupt

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `292d513_kvm__hisi_virt__Register_ipiv_exception_interrupt.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/292d513_kvm__hisi_virt__Register_ipiv_exception_interrupt.patch` |
| 本地提交 | `292d513a1364` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `76ae48fdc260b7236c49e8897b8ab7617bd3ea7f` |
| 目标标题 | kvm: hisi_virt: Register ipiv exception interrupt |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `43c3b4f2ba4932f19602c8fae2a709fd77e95088` |
| 目标 patch-id | `43c3b4f2ba4932f19602c8fae2a709fd77e95088` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/292d513_kvm__hisi_virt__Register_ipiv_exception_interrupt.patch`

**目标提交候选**:
- `76ae48fdc260b7236c49e8897b8ab7617bd3ea7f`

### 文件 1: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 13: kvm: arm64: avoid sending multi-SGIs in IPIV

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `3b4266e_kvm__arm64__avoid_sending_multi_SGIs_in_IPIV.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/3b4266e_kvm__arm64__avoid_sending_multi_SGIs_in_IPIV.patch` |
| 本地提交 | `3b4266e88e78` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `91cbbad587df5fe96a3d6cb790e5e56147931b77` |
| 目标标题 | kvm: arm64: avoid sending multi-SGIs in IPIV |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `ecd1b326d6d90658043dcfaca3212fda5b9c4166` |
| 目标 patch-id | `ecd1b326d6d90658043dcfaca3212fda5b9c4166` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/3b4266e_kvm__arm64__avoid_sending_multi_SGIs_in_IPIV.patch`

**目标提交候选**:
- `91cbbad587df5fe96a3d6cb790e5e56147931b77`

### 文件 1: `arch/arm64/kvm/sys_regs.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 14: KVM: arm64: Introduce ipiv enable ioctl

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `47782a5_KVM__arm64__Introduce_ipiv_enable_ioctl.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/47782a5_KVM__arm64__Introduce_ipiv_enable_ioctl.patch` |
| 本地提交 | `47782a5586e0` |
| 状态 | ❓ 未匹配 |
| 目标提交匹配状态 | 未找到目标提交 |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| 本地 patch-id | `302aaf3cb46c6b5a4e1bfa42a767e28eb686b468` |
| 目标 patch-id | `302aaf3cb46c6b5a4e1bfa42a767e28eb686b468` |

*备注*: No target commit matched this local patch

**本地补丁候选**:
- `/home/xxd/AI/test/patches/47782a5_KVM__arm64__Introduce_ipiv_enable_ioctl.patch`

---

## 补丁 15: KVM: arm64: check if IPIV is enabled in BIOS

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `4c1b2c9_KVM__arm64__check_if_IPIV_is_enabled_in_BIOS.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/4c1b2c9_KVM__arm64__check_if_IPIV_is_enabled_in_BIOS.patch` |
| 本地提交 | `4c1b2c9b61b2` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `80a30f60ee3f5d1a4970c8e0b8b7f78a5be34a39` |
| 目标标题 | KVM: arm64: check if IPIV is enabled in BIOS |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `7a91e7cf05f6a13d956649825bbd300fae010d58` |
| 目标 patch-id | `7a91e7cf05f6a13d956649825bbd300fae010d58` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/4c1b2c9_KVM__arm64__check_if_IPIV_is_enabled_in_BIOS.patch`

**目标提交候选**:
- `80a30f60ee3f5d1a4970c8e0b8b7f78a5be34a39`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 16: kvm: arm64: Add interface KVM_CAP_ARM_IPIV_MODE

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `5242aef_kvm__arm64__Add_interface_KVM_CAP_ARM_IPIV_MODE.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/5242aef_kvm__arm64__Add_interface_KVM_CAP_ARM_IPIV_MODE.patch` |
| 本地提交 | `5242aefd5d2e` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `0a2102ace9c2d9e45130317ea7700b46b85b894d` |
| 目标标题 | kvm: arm64: Add interface KVM_CAP_ARM_IPIV_MODE |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `cef20eeb8ae81d1866e66f8de49980dae903e29b` |
| 目标 patch-id | `fbd77c620d6a7d98367a5dc2a29a034401254600` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/5242aef_kvm__arm64__Add_interface_KVM_CAP_ARM_IPIV_MODE.patch`

**目标提交候选**:
- `0a2102ace9c2d9e45130317ea7700b46b85b894d`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 88.5% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 79.1% | Hunk content matches (layout differs) |


### 文件 2: `include/uapi/linux/kvm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 32.4% | Hunk content matches (layout differs) |


---

## 补丁 17: kvm: hisi_virt: Probe and configure IPIV capacity on HIP12

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `5634a3d_kvm__hisi_virt__Probe_and_configure_IPIV_capacity_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/5634a3d_kvm__hisi_virt__Probe_and_configure_IPIV_capacity_.patch` |
| 本地提交 | `5634a3dfafb7` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `55de7430b022377a3d099d8604d8b1180dc86543` |
| 目标标题 | kvm: hisi_virt: Probe and configure IPIV capacity on HIP12 |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `5fe1cb52215afc8708fe98e0fa6f90afeeb1fe3e` |
| 目标 patch-id | `e028e911c98e4c5a47d1c40b4fd2db48117fe9b2` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/5634a3d_kvm__hisi_virt__Probe_and_configure_IPIV_capacity_.patch`

**目标提交候选**:
- `55de7430b022377a3d099d8604d8b1180dc86543`

### 文件 1: `Documentation/admin-guide/kernel-parameters.txt`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 91.1% | Hunk content matches (layout differs) |


### 文件 3: `arch/arm64/kvm/arm.c`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `	kvm_ipiv_support = hisi_ipiv_supported();`
- `	kvm_info("KVM ipiv %s\n", kvm_ipiv_support ? "enabled" : "disabled");`
- `	if (kvm_ipiv_support)`
- `		ipiv_gicd_init();`
- ``

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | None | `missing-hunk` | 0.0% | Local patch hunk not found in merged commit |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 18: arm64/kabi: use KABI_EXTEND to skip KABI check

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `5a25f12_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/5a25f12_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch` |
| 本地提交 | `5a25f1236bae` |
| 状态 | ❓ 未匹配 |
| 目标提交匹配状态 | 未找到目标提交 |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| 本地 patch-id | `cc2704526af17a41ee3a5343993b8077c18a7f7d` |
| 目标 patch-id | `cc2704526af17a41ee3a5343993b8077c18a7f7d` |

*备注*: No target commit matched this local patch

**本地补丁候选**:
- `/home/xxd/AI/test/patches/5a25f12_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch`

---

## 补丁 19: KVM: arm64: Add support for probing Hisi ncsnp capability

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `625086f_KVM__arm64__Add_support_for_probing_Hisi_ncsnp_cap.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/625086f_KVM__arm64__Add_support_for_probing_Hisi_ncsnp_cap.patch` |
| 本地提交 | `625086f87673` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `7fe255289bd619b8db6761a04eef096e5664a0d0` |
| 目标标题 | KVM: arm64: Add support for probing Hisi ncsnp capability |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `de8d2e8dde91f4e4b8a7085bb329c4b381ebedbf` |
| 目标 patch-id | `4a50ae40beae4774a8b8dc53a56c4a1a1939c1dc` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/625086f_KVM__arm64__Add_support_for_probing_Hisi_ncsnp_cap.patch`

**目标提交候选**:
- `7fe255289bd619b8db6761a04eef096e5664a0d0`

### 文件 1: `arch/arm64/include/asm/hisi_cpu_model.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/include/asm/kvm_mmu.h`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `	if (kvm_ncsnp_support || cpus_have_const_cap(ARM64_HAS_STAGE2_FWB))`

**目标已合入补丁额外包含的新增行**:
- `	if (kvm_ncsnp_support || cpus_have_final_cap(ARM64_HAS_STAGE2_FWB))`

**删除行不一致**:
- `	if (cpus_have_const_cap(ARM64_HAS_STAGE2_FWB))`
- `	if (cpus_have_final_cap(ARM64_HAS_STAGE2_FWB))`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 96.5% | Hunk content differs |


### 文件 3: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 87.4% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisi_cpu_model.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/hyp/pgtable.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 20: kabi: Use KABI_EXTEND to perform kabi repair for IPIV

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `68d4f5d_kabi__Use_KABI_EXTEND_to_perform_kabi_repair_for_I.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/68d4f5d_kabi__Use_KABI_EXTEND_to_perform_kabi_repair_for_I.patch` |
| 本地提交 | `68d4f5dfc875` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `246711290bccebf54e59acea9ef3f06ae1c4de69` |
| 目标标题 | kabi: Use KABI_EXTEND to perform kabi repair for IPIV |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `2734e26548858c7a8156a475b1b30102596733bd` |
| 目标 patch-id | `4f317d8883bb3c6cdad2bfc658e38241320c29d3` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/68d4f5d_kabi__Use_KABI_EXTEND_to_perform_kabi_repair_for_I.patch`

**目标提交候选**:
- `246711290bccebf54e59acea9ef3f06ae1c4de69`

### 文件 1: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `	KABI_EXTEND(struct page		*vpeid_page)`
- `	KABI_EXTEND(bool			nassgireq)`

**目标已合入补丁额外包含的新增行**:
- `	struct page		*vpeid_page;`

**删除行不一致**:
- `	bool			nassgireq;`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 73.0% | Hunk content differs |
| 2 | None | `missing-hunk` | 0.0% | Local patch hunk not found in merged commit |


---

## 补丁 21: KVM: arm64: using kvm_vgic_global_state for ipiv

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `730562d_KVM__arm64__using_kvm_vgic_global_state_for_ipiv.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/730562d_KVM__arm64__using_kvm_vgic_global_state_for_ipiv.patch` |
| 本地提交 | `730562db1d90` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `a9cbef1842707a58aa4e48b9742e74c2ffaa021b` |
| 目标标题 | KVM: arm64: using kvm_vgic_global_state for ipiv |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `a9a0cfe6ef3e35108a3a758fb8ad719f07c385b8` |
| 目标 patch-id | `8913c979757ff2f3ce19481af08d5a1a689850bf` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/730562d_KVM__arm64__using_kvm_vgic_global_state_for_ipiv.patch`

**目标提交候选**:
- `a9cbef1842707a58aa4e48b9742e74c2ffaa021b`

### 文件 1: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ❌ `different`

*备注*: File diff differs

**删除行不一致**:
- `#ifdef CONFIG_ARM64_HISI_IPIV`
- `	kvm_ipiv_support = hisi_ipiv_supported();`
- `#endif`
- `#ifdef CONFIG_ARM64_HISI_IPIV`
- `	kvm_info("KVM ipiv %s\n", kvm_ipiv_support ? "enabled" : "disabled");`
- `#endif`
- `#ifdef CONFIG_ARM64_HISI_IPIV`
- `	if (kvm_ipiv_support)`
- `		ipiv_gicd_init();`
- `#endif`
- ``

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | None | `missing-hunk` | 0.0% | Local patch hunk not found in merged commit |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 22: kvm: hisi: print error for IPIV

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8207b85_kvm__hisi__print_error_for_IPIV.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8207b85_kvm__hisi__print_error_for_IPIV.patch` |
| 本地提交 | `8207b85ea720` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `3074c28b11e7f706625707da2182e0ac6733641f` |
| 目标标题 | kvm: hisi: print error for IPIV |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `49e5c1eec5821af0cd60612f6d28982603176dac` |
| 目标 patch-id | `107d29b8a2cd1e052752635fd44325c8dba783bb` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/8207b85_kvm__hisi__print_error_for_IPIV.patch`

**目标提交候选**:
- `3074c28b11e7f706625707da2182e0ac6733641f`

### 文件 1: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 61.4% | Hunk content matches (layout differs) |


### 文件 3: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 23: KVM: arm64: Support a new HiSi CPU type

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8dea2b6_KVM__arm64__Support_a_new_HiSi_CPU_type.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8dea2b6_KVM__arm64__Support_a_new_HiSi_CPU_type.patch` |
| 本地提交 | `8dea2b6c0541` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `82a24c91dd043b10ad80b149d7e7652d29c11109` |
| 目标标题 | KVM: arm64: Support a new HiSi CPU type |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `c027bcb7c56301add16e7ad18e25c60b817f7972` |
| 目标 patch-id | `c027bcb7c56301add16e7ad18e25c60b817f7972` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/8dea2b6_KVM__arm64__Support_a_new_HiSi_CPU_type.patch`

**目标提交候选**:
- `82a24c91dd043b10ad80b149d7e7652d29c11109`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 24: kvm: hisi: Don't allow to change mpidr in IPIv

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `a68af58_kvm__hisi__Don_t_allow_to_change_mpidr_in_IPIv.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/a68af58_kvm__hisi__Don_t_allow_to_change_mpidr_in_IPIv.patch` |
| 本地提交 | `a68af58d270d` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5a350c27631b01a38fe8f8c439232b484d1a4c44` |
| 目标标题 | kvm: hisi: Don't allow to change mpidr in IPIv |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `a96df643a4a7e83a11d8e85e4d2735f3c94d70d6` |
| 目标 patch-id | `a96df643a4a7e83a11d8e85e4d2735f3c94d70d6` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/a68af58_kvm__hisi__Don_t_allow_to_change_mpidr_in_IPIv.patch`

**目标提交候选**:
- `5a350c27631b01a38fe8f8c439232b484d1a4c44`

### 文件 1: `arch/arm64/kvm/sys_regs.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 25: kvm: hisi_virt: Allocate VM table and save vpeid in it

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `ab4dbc6_kvm__hisi_virt__Allocate_VM_table_and_save_vpeid_i.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/ab4dbc6_kvm__hisi_virt__Allocate_VM_table_and_save_vpeid_i.patch` |
| 本地提交 | `ab4dbc657c10` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `9097e634e47d12db49aac76edd34c02f0ec50122` |
| 目标标题 | kvm: hisi_virt: Allocate VM table and save vpeid in it |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `2b42f38a6e88870917f365e99fb0a8ed9c56d9a6` |
| 目标 patch-id | `ee0797d1e4b2602f968f61c658643b6069c2e169` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/ab4dbc6_kvm__hisi_virt__Allocate_VM_table_and_save_vpeid_i.patch`

**目标提交候选**:
- `9097e634e47d12db49aac76edd34c02f0ec50122`

### 文件 1: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 71.3% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 94.1% | Hunk content matches (layout differs) |


### 文件 2: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 26: KVM: arm64: fix live migration bug of IPIv

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b599aaa_KVM__arm64__fix_live_migration_bug_of_IPIv.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b599aaa_KVM__arm64__fix_live_migration_bug_of_IPIv.patch` |
| 本地提交 | `b599aaac9ec7` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `ac9f85cfcf47d9a8a084967578b36c175804bd67` |
| 目标标题 | KVM: arm64: fix live migration bug of IPIv |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `0e024e67e5dd03cb78256c05b6a838de12832b5f` |
| 目标 patch-id | `0e024e67e5dd03cb78256c05b6a838de12832b5f` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/b599aaa_KVM__arm64__fix_live_migration_bug_of_IPIv.patch`

**目标提交候选**:
- `ac9f85cfcf47d9a8a084967578b36c175804bd67`

### 文件 1: `arch/arm64/kvm/vgic/vgic-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 27: KVM: hisi_virt: tlbi: Fix wrong CPU aff3 conversion between MPIDR and SYS_LSUDVMBM_EL2

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b7334ad_KVM__hisi_virt__tlbi__Fix_wrong_CPU_aff3_conversio.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b7334ad_KVM__hisi_virt__tlbi__Fix_wrong_CPU_aff3_conversio.patch` |
| 本地提交 | `b7334ad8c897` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `52c17b291d2fe40de613074a7b5ecf6911e80245` |
| 目标标题 | KVM: hisi_virt: tlbi: Fix wrong CPU aff3 conversion between MPIDR and SYS_LSUDVMBM_EL2 |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `7d84b17333efaf4afd990fdb20ebb692f3eb5d73` |
| 目标 patch-id | `7d84b17333efaf4afd990fdb20ebb692f3eb5d73` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/b7334ad_KVM__hisi_virt__tlbi__Fix_wrong_CPU_aff3_conversio.patch`

**目标提交候选**:
- `52c17b291d2fe40de613074a7b5ecf6911e80245`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 28: kvm: hisi_virt: fix kernel panic when enable DVMBM in nVHE

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b7bcdd9_kvm__hisi_virt__fix_kernel_panic_when_enable_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b7bcdd9_kvm__hisi_virt__fix_kernel_panic_when_enable_DVMBM.patch` |
| 本地提交 | `b7bcdd9e486e` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `c7700d75d5482eb4c37c8b870fd6401e378bb246` |
| 目标标题 | kvm: hisi_virt: fix kernel panic when enable DVMBM in nVHE |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `fd7943e91a5ca5ec8cac24adcf3d20cf50e0797b` |
| 目标 patch-id | `fd7943e91a5ca5ec8cac24adcf3d20cf50e0797b` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/b7bcdd9_kvm__hisi_virt__fix_kernel_panic_when_enable_DVMBM.patch`

**目标提交候选**:
- `c7700d75d5482eb4c37c8b870fd6401e378bb246`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 29: KVM: arm64: Add kvm_arch::sched_cpus and sched_lock

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `c4ed39b_KVM__arm64__Add_kvm_arch__sched_cpus_and_sched_loc.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/c4ed39b_KVM__arm64__Add_kvm_arch__sched_cpus_and_sched_loc.patch` |
| 本地提交 | `c4ed39bbe206` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `6b074bfbf4b0f06df2799d878423b8f078106de9` |
| 目标标题 | KVM: arm64: Add kvm_arch::sched_cpus and sched_lock |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `70da7c4d1b993901060ea5a67c050c6cde766cc3` |
| 目标 patch-id | `70da7c4d1b993901060ea5a67c050c6cde766cc3` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/c4ed39b_KVM__arm64__Add_kvm_arch__sched_cpus_and_sched_loc.patch`

**目标提交候选**:
- `6b074bfbf4b0f06df2799d878423b8f078106de9`

### 文件 1: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 30: irqchip: gicv3-its: Set base address of vm table and targe ITS when vpe schedule and deschedule

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `cb87b7e_irqchip__gicv3_its__Set_base_address_of_vm_table_a.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/cb87b7e_irqchip__gicv3_its__Set_base_address_of_vm_table_a.patch` |
| 本地提交 | `cb87b7ec77eb` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `511384f3ac531e9f53d4de0d5d8c3e84fd727819` |
| 目标标题 | irqchip: gicv3-its: Set base address of vm table and targe ITS when vpe schedule and deschedule |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `5e6dfe76b6577dbfb11d9810adb5b9e6832a7d3f` |
| 目标 patch-id | `a6570015b329d77b45e7c254e9e274ad1df2f784` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/cb87b7e_irqchip__gicv3_its__Set_base_address_of_vm_table_a.patch`

**目标提交候选**:
- `511384f3ac531e9f53d4de0d5d8c3e84fd727819`

### 文件 1: `arch/arm64/kvm/vgic/vgic-mmio-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 79.6% | Hunk content matches (layout differs) |


---

## 补丁 31: KVM: arm64: ipiv: Change parameter from vcpu to kvm

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `cbd165f_KVM__arm64__ipiv__Change_parameter_from_vcpu_to_kv.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/cbd165f_KVM__arm64__ipiv__Change_parameter_from_vcpu_to_kv.patch` |
| 本地提交 | `cbd165f529bd` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `2df8bbe0c7d4b91a608cda3f8c37733ab69d6633` |
| 目标标题 | KVM: arm64: ipiv: Change parameter from vcpu to kvm |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `16e953c2eecc2b7b10eabc10c8461c584ef55a16` |
| 目标 patch-id | `28f5064760268cf67c7ee18e3198c0c4855db52f` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/cbd165f_KVM__arm64__ipiv__Change_parameter_from_vcpu_to_kv.patch`

**目标提交候选**:
- `2df8bbe0c7d4b91a608cda3f8c37733ab69d6633`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hypercalls.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 96.3% | Hunk content matches (layout differs) |


---

## 补丁 32: KVM: arm64: Implement PV_SGI related calls

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `cd77c03_KVM__arm64__Implement_PV_SGI_related_calls.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/cd77c03_KVM__arm64__Implement_PV_SGI_related_calls.patch` |
| 本地提交 | `cd77c03a1ee1` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `e037e533326d3f1f11459696ec3272909e813de8` |
| 目标标题 | KVM: arm64: Implement PV_SGI related calls |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `8f9463ef63801f9e63b54580bc2495743534dcc8` |
| 目标 patch-id | `b024ae7e9cfbc4300d654df11e7d22134291b56a` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/cd77c03_KVM__arm64__Implement_PV_SGI_related_calls.patch`

**目标提交候选**:
- `e037e533326d3f1f11459696ec3272909e813de8`

### 文件 1: `arch/arm64/include/uapi/asm/kvm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hypercalls.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 31.4% | Hunk content matches (layout differs) |


### 文件 5: `arch/arm64/kvm/vgic/vgic-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `arch/arm64/kvm/vgic/vgic-mmio-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ❌ `different`

*备注*: File diff differs

**删除行不一致**:
- `#ifdef CONFIG_ARM64_HISI_IPIV`
- `extern struct static_key_false ipiv_enable;`
- `#endif`
- ``

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 4 | `different` | 19.2% | Hunk content differs |
| 2 | 1 | `identical` | 100.0% | Hunk content matches |
| 3 | 2 | `identical` | 100.0% | Hunk content matches |
| 4 | 3 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 49.2% | Hunk content matches (layout differs) |
| 6 | None | `missing-hunk` | 0.0% | Local patch hunk not found in merged commit |


### 文件 8: `include/linux/arm-smccc.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 94.7% | Hunk content matches (layout differs) |


### 文件 9: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ❌ `different`

*备注*: File diff differs

**目标已合入补丁额外包含的新增行**:
- `	bool			enable_ipiv_from_vmm;`

**删除行不一致**:
- `	KABI_EXTEND(bool			nassgireq)`
- `	bool			nassgireq;`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 92.6% | Hunk content differs |


### 文件 10: `tools/arch/arm64/include/uapi/asm/kvm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 11: `tools/testing/selftests/kvm/aarch64/hypercalls.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 33: KVM: arm64: Implement the capability of DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `d47f814_KVM__arm64__Implement_the_capability_of_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/d47f814_KVM__arm64__Implement_the_capability_of_DVMBM.patch` |
| 本地提交 | `d47f8143fa03` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `2673b163d40bc9c5773fae0c1af1fd965d54f398` |
| 目标标题 | KVM: arm64: Implement the capability of DVMBM |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `4089ea418bbddf12e444cc73e456778d6b4af4bb` |
| 目标 patch-id | `4089ea418bbddf12e444cc73e456778d6b4af4bb` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/d47f814_KVM__arm64__Implement_the_capability_of_DVMBM.patch`

**目标提交候选**:
- `2673b163d40bc9c5773fae0c1af1fd965d54f398`

### 文件 1: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 34: KVM: arm64: Translate logic cluster id to physical cluster id when updating lsudvmbm

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `da4dd06_KVM__arm64__Translate_logic_cluster_id_to_physical.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/da4dd06_KVM__arm64__Translate_logic_cluster_id_to_physical.patch` |
| 本地提交 | `da4dd0618a8a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `c2eeadca4d6f11c8a7e0d094d629e4eba761779d` |
| 目标标题 | KVM: arm64: Translate logic cluster id to physical cluster id when updating lsudvmbm |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `ddfc14d02ace2db0774d57ebe8d38c233f03c377` |
| 目标 patch-id | `ddfc14d02ace2db0774d57ebe8d38c233f03c377` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/da4dd06_KVM__arm64__Translate_logic_cluster_id_to_physical.patch`

**目标提交候选**:
- `c2eeadca4d6f11c8a7e0d094d629e4eba761779d`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 35: KVM: arm64: Probe Hisi CPU TYPE from ACPI/DTB

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `dab235e_KVM__arm64__Probe_Hisi_CPU_TYPE_from_ACPI_DTB.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/dab235e_KVM__arm64__Probe_Hisi_CPU_TYPE_from_ACPI_DTB.patch` |
| 本地提交 | `dab235e28e1c` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `0c9ba732b8e7015057cbb0ebd9d688ac0c8acad9` |
| 目标标题 | KVM: arm64: Probe Hisi CPU TYPE from ACPI/DTB |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `3cf5de520588a18211474c358c813f13f93df3b3` |
| 目标 patch-id | `84e64519ac5f11bd9283a7ccb72105c9d306dda2` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/dab235e_KVM__arm64__Probe_Hisi_CPU_TYPE_from_ACPI_DTB.patch`

**目标提交候选**:
- `0c9ba732b8e7015057cbb0ebd9d688ac0c8acad9`

### 文件 1: `arch/arm64/include/asm/hisi_cpu_model.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/Makefile`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 82.6% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/hisi_cpu_model.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 36: arm64/config: add config to control whether enable IPIV feature

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e318754_arm64_config__add_config_to_control_whether_enable.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e318754_arm64_config__add_config_to_control_whether_enable.patch` |
| 本地提交 | `e318754d42ce` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `c2ac60e2cf29725bf6ba0017a8b47e4a0e90decb` |
| 目标标题 | arm64/config: add config to control whether enable IPIV feature |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `53c14b66c2251290a86cae4b6301b64b5d753edb` |
| 目标 patch-id | `0db585bd665720eeeada2488e30c33d8e445590e` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/e318754_arm64_config__add_config_to_control_whether_enable.patch`

**目标提交候选**:
- `c2ac60e2cf29725bf6ba0017a8b47e4a0e90decb`

### 文件 1: `arch/arm64/Kconfig`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 95.7% | Hunk content matches (layout differs) |


### 文件 2: `arch/arm64/configs/openeuler_defconfig`

**状态**: ❌ `missing-file`

*备注*: Merged commit does not contain this file diff

**本地补丁有、目标已合入补丁缺失的新增行**:
- `CONFIG_ARM64_HISI_IPIV=y`


### 文件 3: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 93.1% | Hunk content matches (layout differs) |


### 文件 4: `arch/arm64/kvm/arm.c`

**状态**: ❌ `different`

*备注*: File diff differs

**目标已合入补丁额外包含的新增行**:
- `	kvm_ipiv_support = hisi_ipiv_supported();`
- `	kvm_info("KVM ipiv %s\n", kvm_ipiv_support ? "enabled" : "disabled");`
- `	if (kvm_ipiv_support)`
- `		ipiv_gicd_init();`

**删除行不一致**:
- `	if (kvm_dvmbm_support)`
- `		kvm_get_pg_cfg();`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 90.5% | Hunk content matches (layout differs) |
| 3 | 3 | `identical` | 82.2% | Hunk content matches (layout differs) |
| 4 | 4 | `different` | 91.5% | Hunk content differs |


### 文件 5: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `arch/arm64/kvm/hisilicon/hisi_virt.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `arch/arm64/kvm/sys_regs.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 8: `arch/arm64/kvm/vgic/vgic-init.c`

**状态**: ❌ `different`

*备注*: File diff differs

**目标已合入补丁额外包含的新增行**:
- `#endif`
- `#endif`
- `#endif`
- `#endif`
- `#endif`

**删除行不一致**:
- `#ifdef CONFIG_ACPI`
- `#ifdef CONFIG_ACPI`
- `#ifdef CONFIG_ACPI`
- `#ifdef CONFIG_ACPI`
- `#ifdef CONFIG_ACPI`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 2 | `different` | 29.9% | Hunk content differs |
| 2 | 1 | `different` | 22.9% | Hunk content differs |
| 3 | 3 | `different` | 15.5% | Hunk content differs |
| 4 | None | `missing-hunk` | 0.0% | Local patch hunk not found in merged commit |


### 文件 9: `arch/arm64/kvm/vgic/vgic-mmio-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 10: `drivers/irqchip/irq-gic-v3-its.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 82.1% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |
| 6 | 6 | `identical` | 100.0% | Hunk content matches |
| 7 | 7 | `identical` | 100.0% | Hunk content matches |
| 8 | 8 | `identical` | 100.0% | Hunk content matches |
| 9 | 9 | `identical` | 100.0% | Hunk content matches |
| 10 | 10 | `identical` | 100.0% | Hunk content matches |
| 11 | 11 | `identical` | 100.0% | Hunk content matches |
| 12 | 12 | `identical` | 100.0% | Hunk content matches |


### 文件 11: `drivers/irqchip/irq-gic-v3.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 12: `include/linux/irqchip/arm-gic-v3.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |
| 4 | 4 | `identical` | 100.0% | Hunk content matches |


### 文件 13: `include/linux/irqchip/arm-gic-v4.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 66.4% | Hunk content matches (layout differs) |


### 文件 14: `config.aarch64`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_ARM64_HISI_IPIV=y`


### 文件 15: `config.aarch64-64k`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `CONFIG_ARM64_HISI_IPIV=y`


---

## 补丁 37: KVM: arm64: Probe and configure DVMBM capability on HiSi CPUs

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e85b97c_KVM__arm64__Probe_and_configure_DVMBM_capability_o.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e85b97c_KVM__arm64__Probe_and_configure_DVMBM_capability_o.patch` |
| 本地提交 | `e85b97c7e2b4` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `03142b25e10e7c8753f5ccaad4502ff7170ff7fa` |
| 目标标题 | KVM: arm64: Probe and configure DVMBM capability on HiSi CPUs |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `d683c989b9e9be270358e3a415d9586b30c28029` |
| 目标 patch-id | `68411ba1a7d0ed2cfc4507ec3e7f973c03a235b7` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/e85b97c_KVM__arm64__Probe_and_configure_DVMBM_capability_o.patch`

**目标提交候选**:
- `03142b25e10e7c8753f5ccaad4502ff7170ff7fa`

### 文件 1: `Documentation/admin-guide/kernel-parameters.txt`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/include/asm/kvm_host.h`

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
| 1 | 1 | `identical` | 82.2% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/hisilicon/hisi_virt.h`

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
