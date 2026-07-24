# 补丁已合入差异报告

> **生成时间**: 2026-03-31 12:19:14
> **目标仓库**: `/home/xxd/velinux-kernel`
> **目标分支**: `auto-patch-20260331_114920`
> **模式**: `merged-diff`

---

## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | 15 |
| 本地补丁文件数 | 15 |
| 已匹配目标提交 | 15 |
| 未匹配目标提交 | 0 |
| 歧义目标提交 | 0 |
| 完全一致 | 13 |
| 存在差异 | 2 |
| 未匹配 | 0 |
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
| 目标提交 | `8b12daefa5d6d20180f38febd9ea23170acfd4b3` |
| 目标标题 | KVM: arm64: Only probe Hisi ncsnp feature on Hisi CPUs |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `b3fa9ed3eeea268f860816fe0fc79a3b708983cc` |
| 目标 patch-id | `f26111fea8fef0b5a5d524b6630e6bc716f33295` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/029e24e_KVM__arm64__Only_probe_Hisi_ncsnp_feature_on_Hisi_.patch`

**目标提交候选**:
- `8b12daefa5d6d20180f38febd9ea23170acfd4b3`

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

## 补丁 2: KVM: arm64: Add new HiSi CPU type to support DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0c2bca0_KVM__arm64__Add_new_HiSi_CPU_type_to_support_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0c2bca0_KVM__arm64__Add_new_HiSi_CPU_type_to_support_DVMBM.patch` |
| 本地提交 | `0c2bca09f8af` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `c84f17007c9aefbcade82ce1a60248ccf172e519` |
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
- `c84f17007c9aefbcade82ce1a60248ccf172e519`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 3: KVM: arm64: Add new HiSi CPU type for supporting DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `0fb85a6_KVM__arm64__Add_new_HiSi_CPU_type_for_supporting_D.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/0fb85a6_KVM__arm64__Add_new_HiSi_CPU_type_for_supporting_D.patch` |
| 本地提交 | `0fb85a6177b5` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `15caac0e0028d8dffd903f050cb9852f3c10ede6` |
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
- `15caac0e0028d8dffd903f050cb9852f3c10ede6`

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

## 补丁 4: KVM: arm64: fix memory leak in TLBI

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `18c863e_KVM__arm64__fix_memory_leak_in_TLBI.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/18c863e_KVM__arm64__fix_memory_leak_in_TLBI.patch` |
| 本地提交 | `18c863e22109` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `dd338449cf737a5d018b93ea31c845550703c091` |
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
- `dd338449cf737a5d018b93ea31c845550703c091`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 5: KVM: arm64: Add kvm_vcpu_arch::sched_cpus and pre_sched_cpus

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1c342c1_KVM__arm64__Add_kvm_vcpu_arch__sched_cpus_and_pre_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1c342c1_KVM__arm64__Add_kvm_vcpu_arch__sched_cpus_and_pre_.patch` |
| 本地提交 | `1c342c1a8d0a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `67e93154a375ac725a6eb0a8eb423d6a1c35e351` |
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
- `67e93154a375ac725a6eb0a8eb423d6a1c35e351`

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

## 补丁 6: kvm: hisi_virt: Update TLBI broadcast feature for hip12

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `2671ba2_kvm__hisi_virt__Update_TLBI_broadcast_feature_for_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/2671ba2_kvm__hisi_virt__Update_TLBI_broadcast_feature_for_.patch` |
| 本地提交 | `2671ba221968` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5d32d6d0de0fdddedd1da8c433ee07607e30bbcf` |
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
- `5d32d6d0de0fdddedd1da8c433ee07607e30bbcf`

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

## 补丁 7: KVM: arm64: Add support for probing Hisi ncsnp capability

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `625086f_KVM__arm64__Add_support_for_probing_Hisi_ncsnp_cap.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/625086f_KVM__arm64__Add_support_for_probing_Hisi_ncsnp_cap.patch` |
| 本地提交 | `625086f87673` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `c3083d4e2d6f6e35cbf3a7c2d2d8dc0ae802569d` |
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
- `c3083d4e2d6f6e35cbf3a7c2d2d8dc0ae802569d`

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

## 补丁 8: KVM: arm64: Support a new HiSi CPU type

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8dea2b6_KVM__arm64__Support_a_new_HiSi_CPU_type.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8dea2b6_KVM__arm64__Support_a_new_HiSi_CPU_type.patch` |
| 本地提交 | `8dea2b6c0541` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `49acaa49fd7c55bf4ea9fb3f9181609527e95071` |
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
- `49acaa49fd7c55bf4ea9fb3f9181609527e95071`

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

## 补丁 9: KVM: hisi_virt: tlbi: Fix wrong CPU aff3 conversion between MPIDR and SYS_LSUDVMBM_EL2

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b7334ad_KVM__hisi_virt__tlbi__Fix_wrong_CPU_aff3_conversio.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b7334ad_KVM__hisi_virt__tlbi__Fix_wrong_CPU_aff3_conversio.patch` |
| 本地提交 | `b7334ad8c897` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `3302d1e7c9c9a292d261a9f0c9b54b2e8a531c8c` |
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
- `3302d1e7c9c9a292d261a9f0c9b54b2e8a531c8c`

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

## 补丁 10: kvm: hisi_virt: fix kernel panic when enable DVMBM in nVHE

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `b7bcdd9_kvm__hisi_virt__fix_kernel_panic_when_enable_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/b7bcdd9_kvm__hisi_virt__fix_kernel_panic_when_enable_DVMBM.patch` |
| 本地提交 | `b7bcdd9e486e` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `679475856ff790036114496083b5cf6f612eb662` |
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
- `679475856ff790036114496083b5cf6f612eb662`

### 文件 1: `arch/arm64/kvm/hisilicon/hisi_virt.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 11: KVM: arm64: Add kvm_arch::sched_cpus and sched_lock

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `c4ed39b_KVM__arm64__Add_kvm_arch__sched_cpus_and_sched_loc.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/c4ed39b_KVM__arm64__Add_kvm_arch__sched_cpus_and_sched_loc.patch` |
| 本地提交 | `c4ed39bbe206` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `0bbb8f22a0c59b410dacc6ebe6303505ce2f740e` |
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
- `0bbb8f22a0c59b410dacc6ebe6303505ce2f740e`

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

## 补丁 12: KVM: arm64: Implement the capability of DVMBM

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `d47f814_KVM__arm64__Implement_the_capability_of_DVMBM.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/d47f814_KVM__arm64__Implement_the_capability_of_DVMBM.patch` |
| 本地提交 | `d47f8143fa03` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `326a6496aa4c78913df71a804bc13ec8f20b96a1` |
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
- `326a6496aa4c78913df71a804bc13ec8f20b96a1`

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

## 补丁 13: KVM: arm64: Translate logic cluster id to physical cluster id when updating lsudvmbm

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `da4dd06_KVM__arm64__Translate_logic_cluster_id_to_physical.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/da4dd06_KVM__arm64__Translate_logic_cluster_id_to_physical.patch` |
| 本地提交 | `da4dd0618a8a` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `3c08bbb3a453e6a013d54509021449a7f8d0bc41` |
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
- `3c08bbb3a453e6a013d54509021449a7f8d0bc41`

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

## 补丁 14: KVM: arm64: Probe Hisi CPU TYPE from ACPI/DTB

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `dab235e_KVM__arm64__Probe_Hisi_CPU_TYPE_from_ACPI_DTB.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/dab235e_KVM__arm64__Probe_Hisi_CPU_TYPE_from_ACPI_DTB.patch` |
| 本地提交 | `dab235e28e1c` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `475db2332d7b8f950352f4520f6136b1f95e695a` |
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
- `475db2332d7b8f950352f4520f6136b1f95e695a`

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

## 补丁 15: KVM: arm64: Probe and configure DVMBM capability on HiSi CPUs

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `e85b97c_KVM__arm64__Probe_and_configure_DVMBM_capability_o.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/e85b97c_KVM__arm64__Probe_and_configure_DVMBM_capability_o.patch` |
| 本地提交 | `e85b97c7e2b4` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `eb07accc25d294b3494dd0d340af635249be4bfd` |
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
- `eb07accc25d294b3494dd0d340af635249be4bfd`

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
