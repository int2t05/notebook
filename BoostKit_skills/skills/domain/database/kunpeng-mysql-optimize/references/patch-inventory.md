# Patch Inventory

The default patch root is the skill-bundled `assets/patches/` directory, which contains:

- `assets/patches/PS-57-patch/`
- `assets/patches/PS-8043-patch/`

When using this skill on any machine, prefer the bundled patches. Use an external patch root only when the user explicitly provides a newer external patch repository.

## Version Selection Rules

- MySQL/Percona 5.7: prefer `PS-57-patch/`.
- MySQL/Percona 8.0+: prefer `PS-8043-patch/`. The directory name comes from the PS-8043 patch baseline, but these patches are recommended for the 8.0+ series.
- Before applying to a specific 8.0.x target, still check conflicts and run MTR plus stress regression.
- If no same-version or same-series patch exists, say "no bundled patch found" and explain whether the hikunpeng item is still usable as deployment tuning guidance.

## MySQL 5.7

### Compute Path

- `PS-57-patch/0001-fast-tuple-comparing.patch`: InnoDB tuple/record compare.
- `PS-57-patch/0001-optimize-character-with-neon.patch`: NEON character handling.
- `PS-57-patch/0001-optimize-my_convert-for-aarch64.patch`: AArch64 `my_convert` optimization.
- `PS-57-patch/0001-optimize-mysqld-s-branch-alignment-in-kunpeng-platfo.patch`: Kunpeng branch alignment.
- `PS-57-patch/0001-optimize-space-skipping-with-neon.patch`: NEON space skipping.
- `PS-57-patch/0001-optimize-Item_func_like-with-neon.patch`: NEON LIKE optimization.
- `PS-57-patch/0001-optimize-utf8-utf8mb4-charset-handler.patch`: UTF8/UTF8MB4 handler.
- `PS-57-patch/0001-non-aligned-memory-access-optimize-for-aarch64.patch`: Unaligned access.
- `PS-57-patch/0001-rec_get_offsets-optimize.patch`: `rec_get_offsets`.
- `PS-57-patch/0001-speedup-collation-lookup.patch`: collation lookup.
- `PS-57-patch/0001-inline-row_sel_field_store_in_mysql_format_func.patch`: inline row-select field conversion.

### Binlog

- `PS-57-patch/0001-binlog-replace-std-map-with-dense_hash_map.patch`: replaces writeset history `std::map` with `google::dense_hash_map`.
- `PS-57-patch/0001-improving-binlog-s-flushing-with-preallocated-binlog.patch`: preallocates binlog files to reduce flush/growth cost; adds `enable_binlog_preallocate`.
- `PS-57-patch/0001-optimize-binlog-order-commit.patch`: shards ordered-commit pending lock/condition to reduce wakeup contention.
- `PS-57-patch/0001-binlog-order-commit-optimize-generally.patch`: related ordered-commit candidate. Do not blindly stack it with the previous patch; compare diffs and conflicts first.

### Fine-Grained Locking

- `PS-57-patch/lock_sys_opt/0001-LOCK_TABLE-CAN-BE-OPTIMIZED-IF-UPDATING-THE-SAME-TAB.patch`: tracks lock counts by mode and optimizes intention-lock grants for concurrent same-table DML.
- `PS-57-patch/lock_sys_opt/0001-WL-10314-InnoDB-Lock-sys-optimization-sharded-lock_s.patch`: backports lock_sys sharding; large code-change surface.
- `PS-57-patch/0001-LOCK_TABLE-CAN-BE-OPTIMIZED-IF-UPDATING-THE-SAME-TAB.patch`: duplicate root-level candidate; prefer the `lock_sys_opt/` copy.

### Lock-Free / ReadView

- `PS-57-patch/0001-innodb-enhance-read-view-management-with-version-tra.patch`: read view version tracking to reduce read view close/reuse lock cost.
- `PS-57-patch/0001-optimize-mvcc-readview-data-structure.patch`: MVCC readview data-structure candidate. It touches the same read view path, so check conflicts before combining.

### CRC32

- `PS-57-patch/0001-add-ut_crc32_hw-for-arm-platform.patch`: AArch64 ARMv8 CRC32 intrinsic path with runtime `HWCAP_CRC32/PMULL` checks.

### Text Huge Pages

- `PS-57-patch/0001-add-text-remapping-to-huge-pages.patch.gz`: maps `.text` to huge pages; adds `text_huge_pages`. Distributed as gzip because of the GitCode single-file size limit; decompress before applying.

### Thread Pool

- `PS-57-patch/tp-opt/0001-threadpool-adjust-concurrency-using-scheduler-statis.patch`: adaptive thread-pool concurrency control.
- Added or related variables: `thread_pool_enable_extra_threads`, `thread_pool_cpu_usage_threshold`, `thread_pool_nvcsw_freq_threshold`, `thread_pool_nivcsw_freq_threshold`.
- Touched areas: `threadpool_unix.cc`, `threadpool_common.cc`, `sys_vars.cc`, `binlog.cc`, `service_thd_wait.h`.

## MySQL 8.0+

### Compute Path

- `PS-8043-patch/0001-fast-tuple-record-comparing.patch`: InnoDB tuple/record compare.
- `PS-8043-patch/0001-optimize-Item_func_like-with-neon.patch`: NEON LIKE optimization.
- `PS-8043-patch/0001-optimize-utf8-utf8mb4-charset-handler.patch`: UTF8/UTF8MB4 handler.
- `PS-8043-patch/0002-optimize-space-skipping-with-neon.patch`: NEON space skipping.
- `PS-8043-patch/0003-non-aligned-memory-access-optimize-for-aarch64.patch`: unaligned access.
- `PS-8043-patch/0005-rec_get_offsets-optimize.patch`: `rec_get_offsets`.
- `PS-8043-patch/0008-remove-some-release-assert-and-add-some-branch-predi.patch`: release assert and branch prediction.

### Binlog

- `PS-8043-patch/0001-optimize-binlog-write-performance-preallocated-binlo.patch`: preallocated binlog; adds `enable_binlog_preallocate`.
- `PS-8043-patch/0004-optimize-binlog-ordered-commit.patch`: ordered-commit pending lock/condition optimization.
- No bundled 8.0 dense_hash_map writeset patch was found.

### Lock-Free / ReadView

- `PS-8043-patch/readview-opt/0001-innodb-enhance-read-view-management-with-version-tra.patch`: read view version tracking.
- `PS-8043-patch/readview-opt/0002-Bug-37628911-Crash-caused-by-race-condition-between-.patch`: read view race-crash fix. Usually evaluate it together with `0001`.

### Text Huge Pages

- `PS-8043-patch/0007-add-text-huge-pages-for-aarch64-platform.patch.gz`: `.text` huge pages; adds `text_huge_pages`. Distributed as gzip because of the GitCode single-file size limit; decompress before applying.

### Thread Pool

- `PS-8043-patch/tp-opt/0001-adjust-threadpool-concurrency-using-scheduler-statis.patch`: adaptive thread-pool concurrency using CPU and context-switch statistics.
- Added or related variables: `thread_pool_commit_burst_threads`, `thread_pool_cpu_usage_threshold`, `thread_pool_nvcsw_freq_threshold`, `thread_pool_nivcsw_freq_threshold`.
- Added status output: `Threadpool_statistics_detail`, including `n_cpu`, `cpu_pct`, `nivcsw_freq`, `nvcsw_freq`, and `active_threads_quota`.

### Plan Cache

- `PS-8043-patch/0001-Add-plan-cache-to-improve-select-performance.patch`: SQL-layer plan cache.
- Added variables: `plan_cache`, `plan_cache_allow_change_ratio`.
- Added files: `sql/sql_plan_cache.cc`, `sql/sql_plan_cache.h`.
- Recommend as a bundled 8.0+ patch. Check conflicts and run regression before applying to a specific 8.0.x target.

### Container-Aware

- `PS-8043-patch/container_aware/0001-WL-16484-Make-InnoDB-container-aware.patch`: InnoDB/container-aware foundation.
- `PS-8043-patch/container_aware/0002-Bug-37993516-Handle-cgroup-v1-default-memory-limit.patch`: cgroup v1 memory limit.
- `PS-8043-patch/container_aware/0003-Bug-37993516-Handle-cgroup-v1-default-memory-limit-p.patch`: follow-up cgroup v1 memory-limit fix.
- `PS-8043-patch/container_aware/0004-Enhance-log-write-conditions-to-prevent-CPU-overutil.patch`: log write CPU-overutilization prevention under containers.

## hikunpeng Items Without Clear Bundled Source Patches

- Network multipath optimization: no clear bundled MySQL source patch was found; treat it as system/deployment tuning.
- NUMA scheduling optimization: no standalone bundled MySQL source patch was found; treat it as deployment, affinity, and memory-policy tuning.
- 8.0+ fine-grained lock_sys: no bundled counterpart was found; check whether the target version already has upstream support.
- 8.0+ standalone CRC32: no bundled counterpart like the 5.7 CRC32 patch was found; confirm upstream and compiler-flag support first.
