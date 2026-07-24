# 补丁已合入差异报告

> **生成时间**: 2026-03-31 14:37:47
> **目标仓库**: `/home/xxd/velinux-kernel`
> **目标分支**: `auto-patch-20260331_141354`
> **模式**: `merged-diff`

---

## 执行摘要

| 指标 | 数量 |
|------|------|
| 本地补丁数 | 8 |
| 本地补丁文件数 | 8 |
| 已匹配目标提交 | 8 |
| 未匹配目标提交 | 0 |
| 歧义目标提交 | 0 |
| 完全一致 | 7 |
| 存在差异 | 1 |
| 未匹配 | 0 |
| 匹配歧义 | 0 |

> **整体状态**: ❌ 已发现本地补丁与目标仓库已合入补丁存在差异

---

## 详细结果

## 补丁 1: KVM: arm64: fix memory leak in HDBSS

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `00c9310_KVM__arm64__fix_memory_leak_in_HDBSS.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/00c9310_KVM__arm64__fix_memory_leak_in_HDBSS.patch` |
| 本地提交 | `00c93102b328` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `5808b45d49f23a724059d275f3fbced1d75ba2be` |
| 目标标题 | KVM: arm64: fix memory leak in HDBSS |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `1083638cdc5412473dc31a3364feb6b2f671a107` |
| 目标 patch-id | `1083638cdc5412473dc31a3364feb6b2f671a107` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/00c9310_KVM__arm64__fix_memory_leak_in_HDBSS.patch`

**目标提交候选**:
- `5808b45d49f23a724059d275f3fbced1d75ba2be`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 2: arm64/sysreg: add HDBSS related register information

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `16ab2a2_arm64_sysreg__add_HDBSS_related_register_informati.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/16ab2a2_arm64_sysreg__add_HDBSS_related_register_informati.patch` |
| 本地提交 | `16ab2a2fee8b` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `f6af513f440fa2c6912a4c0c3afcfb0454a8e982` |
| 目标标题 | arm64/sysreg: add HDBSS related register information |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `722c92ec1efef62732ab1161157c9cb4e156079b` |
| 目标 patch-id | `0247e9998b4992ce5e42dad7cd047f4eadf63b29` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/16ab2a2_arm64_sysreg__add_HDBSS_related_register_informati.patch`

**目标提交候选**:
- `f6af513f440fa2c6912a4c0c3afcfb0454a8e982`

### 文件 1: `arch/arm64/include/asm/esr.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/include/asm/kvm_arm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 78.0% | Hunk content matches (layout differs) |


### 文件 3: `arch/arm64/tools/sysreg`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 3: arm64/kabi: use KABI_EXTEND to skip KABI check

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `1d334a2_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/1d334a2_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch` |
| 本地提交 | `1d334a25caf9` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `67344644ab216930e508c93ebd50270dbfbc41f0` |
| 目标标题 | arm64/kabi: use KABI_EXTEND to skip KABI check |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `077307fc39ee645cdb398b6422544e32ee299b1a` |
| 目标 patch-id | `077307fc39ee645cdb398b6422544e32ee299b1a` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/1d334a2_arm64_kabi__use_KABI_EXTEND_to_skip_KABI_check.patch`

**目标提交候选**:
- `67344644ab216930e508c93ebd50270dbfbc41f0`

### 文件 1: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `include/linux/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 4: arm64/kvm: support to handle the HDBSSF event

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `6d60015_arm64_kvm__support_to_handle_the_HDBSSF_event.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/6d60015_arm64_kvm__support_to_handle_the_HDBSSF_event.patch` |
| 本地提交 | `6d60015590c3` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `b89a50db30f40edff37904c2cade85789b4b31b9` |
| 目标标题 | arm64/kvm: support to handle the HDBSSF event |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `3aa43aed98a33cca462b108b423b6983e5c94c17` |
| 目标 patch-id | `3aa43aed98a33cca462b108b423b6983e5c94c17` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/6d60015_arm64_kvm__support_to_handle_the_HDBSSF_event.patch`

**目标提交候选**:
- `b89a50db30f40edff37904c2cade85789b4b31b9`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/handle_exit.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 3: `arch/arm64/kvm/mmu.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 5: arm64/kvm: support set the DBM attr during memory abort

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `74a1397_arm64_kvm__support_set_the_DBM_attr_during_memory_.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/74a1397_arm64_kvm__support_set_the_DBM_attr_during_memory_.patch` |
| 本地提交 | `74a1397438e0` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `a83779d8bbc209b9dd7737542aea804470c7a4e2` |
| 目标标题 | arm64/kvm: support set the DBM attr during memory abort |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `0be84bc69de7ba6377300f480dd201dd1df62cde` |
| 目标 patch-id | `d1ea531a2b1bebc6357d9aa8bb3d4dc935f3fca1` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/74a1397_arm64_kvm__support_set_the_DBM_attr_during_memory_.patch`

**目标提交候选**:
- `a83779d8bbc209b9dd7737542aea804470c7a4e2`

### 文件 1: `arch/arm64/include/asm/kvm_pgtable.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 2: `arch/arm64/kvm/hyp/pgtable.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 79.8% | Hunk content matches (layout differs) |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 6: arm64/config: add config to control whether enable HDBSS feature

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `8d2e1e3_arm64_config__add_config_to_control_whether_enable.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/8d2e1e3_arm64_config__add_config_to_control_whether_enable.patch` |
| 本地提交 | `8d2e1e3b26a9` |
| 状态 | ❌ 存在差异 |
| 目标提交 | `981f82cf6bb7bef7fdd05055124cc39715a0466e` |
| 目标标题 | arm64/config: add config to control whether enable HDBSS feature |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `1d705ea7b15c821cdea3e8713e8f5b57ad00fa57` |
| 目标 patch-id | `a462268c61991427eade9f90d049ff7f5cb88f3b` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/8d2e1e3_arm64_config__add_config_to_control_whether_enable.patch`

**目标提交候选**:
- `981f82cf6bb7bef7fdd05055124cc39715a0466e`

### 文件 1: `arch/arm64/Kconfig`

**状态**: ❌ `different`

*备注*: File diff differs

**本地补丁有、目标已合入补丁缺失的新增行**:
- `	  translation table descriptors’ dirty state to reduce the cost of`

**目标已合入补丁额外包含的新增行**:
- `	  translation table descriptors' dirty state to reduce the cost of`

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `different` | 95.6% | Hunk content differs |


### 文件 2: `arch/arm64/configs/openeuler_defconfig`

**状态**: ❌ `missing-file`

*备注*: Merged commit does not contain this file diff

**本地补丁有、目标已合入补丁缺失的新增行**:
- `#`
- `# ARMv9.5 architectural features`
- `#`
- `CONFIG_ARM64_HDBSS=y`
- `# end of ARMv9.5 architectural features`
- ``


### 文件 3: `arch/arm64/include/asm/cpufeature.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 89.2% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 75.4% | Hunk content matches (layout differs) |


### 文件 5: `arch/arm64/include/asm/kvm_mmu.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 6: `arch/arm64/include/asm/sysreg.h`

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
| 3 | 3 | `identical` | 84.3% | Hunk content matches (layout differs) |
| 4 | 4 | `identical` | 74.3% | Hunk content matches (layout differs) |
| 5 | 5 | `identical` | 100.0% | Hunk content matches |
| 6 | 6 | `identical` | 100.0% | Hunk content matches |


### 文件 8: `arch/arm64/kvm/handle_exit.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 9: `arch/arm64/kvm/hyp/pgtable.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 87.8% | Hunk content matches (layout differs) |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |


### 文件 10: `arch/arm64/kvm/hyp/vhe/switch.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 11: `arch/arm64/kvm/hyp/vhe/sysreg-sr.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 81.8% | Hunk content matches (layout differs) |


### 文件 12: `arch/arm64/kvm/mmu.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 100.0% | Hunk content matches |
| 3 | 3 | `identical` | 100.0% | Hunk content matches |


### 文件 13: `arch/arm64/kvm/reset.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 90.2% | Hunk content matches (layout differs) |


### 文件 14: `include/linux/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 15: `config.aarch64`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `#`
- `# ARMv9.5 architectural features`
- `#`
- `CONFIG_ARM64_HDBSS=y`
- `# end of ARMv9.5 architectural features`
- ``


### 文件 16: `config.aarch64-64k`

**状态**: ❌ `extra-file`

*备注*: Merged commit contains an extra file diff not present in local patch

**目标已合入补丁额外包含的新增行**:
- `#`
- `# ARMv9.5 architectural features`
- `#`
- `CONFIG_ARM64_HDBSS=y`
- `# end of ARMv9.5 architectural features`
- ``


---

## 补丁 7: KVM: arm64: do not support hdbss in nvhe

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `a5e3c93_KVM__arm64__do_not_support_hdbss_in_nvhe.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/a5e3c93_KVM__arm64__do_not_support_hdbss_in_nvhe.patch` |
| 本地提交 | `a5e3c939fbb1` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `8e6c97d005a8a5e1d505f843bdd4f2bf27482a88` |
| 目标标题 | KVM: arm64: do not support hdbss in nvhe |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `c3b878b1bfe2b0adbf2fa159f8ae694452a5222f` |
| 目标 patch-id | `c3b878b1bfe2b0adbf2fa159f8ae694452a5222f` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/a5e3c93_KVM__arm64__do_not_support_hdbss_in_nvhe.patch`

**目标提交候选**:
- `8e6c97d005a8a5e1d505f843bdd4f2bf27482a88`

### 文件 1: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


---

## 补丁 8: arm64/kvm: using ioctl to enable/disable the HDBSS feature

| 属性 | 值 |
|------|-----|
| 本地补丁文件 | `bd6106e_arm64_kvm__using_ioctl_to_enable_disable_the_HDBSS.patch` |
| 本地补丁路径 | `/home/xxd/AI/test/patches/bd6106e_arm64_kvm__using_ioctl_to_enable_disable_the_HDBSS.patch` |
| 本地提交 | `bd6106e348d7` |
| 状态 | ✅ 完全一致 |
| 目标提交 | `4e4bb7aea813dceca4ac8e1b6e60697e6d68fbf3` |
| 目标标题 | arm64/kvm: using ioctl to enable/disable the HDBSS feature |
| 目标提交匹配状态 | 已匹配目标提交 |
| 目标提交匹配方式 | `subject` |
| 本地补丁匹配状态 | 已匹配本地补丁 |
| 本地补丁匹配方式 | `indexed` |
| Diff 比较匹配方式 | `subject` |
| 本地 patch-id | `0032d2200ff0125f9cb2dd96774805abdd41ff08` |
| 目标 patch-id | `bc28926268c4173e4ddedd1d5fc2d3cfe3545364` |

**本地补丁候选**:
- `/home/xxd/AI/test/patches/bd6106e_arm64_kvm__using_ioctl_to_enable_disable_the_HDBSS.patch`

**目标提交候选**:
- `4e4bb7aea813dceca4ac8e1b6e60697e6d68fbf3`

### 文件 1: `arch/arm64/include/asm/cpufeature.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 86.7% | Hunk content matches (layout differs) |


### 文件 2: `arch/arm64/include/asm/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 69.2% | Hunk content matches (layout differs) |


### 文件 3: `arch/arm64/include/asm/kvm_mmu.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 4: `arch/arm64/include/asm/sysreg.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 5: `arch/arm64/kvm/arm.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 83.3% | Hunk content matches (layout differs) |
| 3 | 3 | `identical` | 71.8% | Hunk content matches (layout differs) |


### 文件 6: `arch/arm64/kvm/hyp/vhe/switch.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 7: `arch/arm64/kvm/hyp/vhe/sysreg-sr.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 81.4% | Hunk content matches (layout differs) |


### 文件 8: `arch/arm64/kvm/mmu.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 9: `arch/arm64/kvm/reset.c`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |
| 2 | 2 | `identical` | 76.2% | Hunk content matches (layout differs) |


### 文件 10: `include/linux/kvm_host.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 100.0% | Hunk content matches |


### 文件 11: `include/uapi/linux/kvm.h`

**状态**: ✅ `identical`

*备注*: File diff matches

| Local Hunk | Merged Hunk | 状态 | 相似度 | 说明 |
|------------|-------------|------|--------|------|
| 1 | 1 | `identical` | 3.5% | Hunk content matches (layout differs) |


### 文件 12: `tools/include/uapi/linux/kvm.h`

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
