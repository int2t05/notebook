# Optimization Strategy Map

## Table of Contents

- Diagnostic entry point
- Compute-path optimization
- Binlog optimization
- Network multipath optimization
- Fine-grained lock optimization
- Lock-free / ReadView optimization
- NUMA scheduling optimization
- CRC32 instruction optimization
- Text huge pages
- Thread pool optimization
- Plan cache
- ARM foundation micro-optimizations
- Container-aware optimization

## Diagnostic Entry Point

Normalize user input into four evidence types first:

- CPU hotspots: `perf top -g`, flamegraphs, `perf report --stdio`.
- Waits and lock contention: Performance Schema waits, `SHOW ENGINE INNODB STATUS`, mutex/rwlock sampling, context switches.
- IO, network, and NUMA: `perf stat`, `numastat`, NIC queues/RSS/IRQ, binlog fsync/write metrics.
- SQL shape: point select, range query, LIKE/charset, write transactions, whether binlog is enabled, and whether thread pool is enabled.

Make strong recommendations only when the evidence maps to a strategy. If the evidence is weak, ask for more hotspot data first.

## Compute-Path Optimization

Applicable signals:

- High cost in `cmp_dtuple_rec_with_match`, `rem0cmp`, `page_cur_search_with_match`, `rec_get_offsets`, or `row_sel_field_store_in_mysql_format`.
- High cost in `strings/ctype*`, `my_convert`, `my_strnncoll`, `my_well_formed_len`, UTF8/UTF8MB4, collation, `Item_func_like`, or LIKE.
- CPU-bound OLTP or read-only workloads where hotspots cluster around record comparison, charset conversion, space skipping, LIKE matching, or branch prediction.

Preferred strategy:

- For 5.7, consider the fast tuple, NEON character/LIKE/space skipping, `my_convert`, UTF8 handler, and `rec_get_offsets` patch group.
- For 8.0+, consider `fast-tuple-record-comparing`, NEON LIKE/space skipping, UTF8 handler, unaligned access, and `rec_get_offsets`.
- If the hotspot is instruction cache or branch alignment, consider branch alignment or text huge pages instead. Do not group that with charset hotspots.

Validation focus:

- Run sysbench point_select, read_only, and read_write workloads, including UTF8/UTF8MB4, LIKE, sort, and comparison cases.
- Run relevant MTR coverage for charset, collation, InnoDB row/search, and basic optimizer behavior.

## Binlog Optimization

Applicable signals:

- Hot `MYSQL_BIN_LOG::ordered_commit`, `Commit_stage_manager`, `process_commit_stage_queue`, `sync_binlog_file`, `binlog_cache_data::flush`, `fsync`, or `pwrite`.
- Binlog, GTID, or writeset is enabled and write transaction throughput is limited by group commit or binlog file growth.
- Waits show commit-stage congestion, ordered-commit condition-variable wakeup cost, or binlog flush/sync cost.

Preferred strategy:

- Preallocated binlog reduces file growth and flush cost. Watch the added `enable_binlog_preallocate` variable.
- Ordered commit optimization assigns pending commit locks/conditions to reduce herd wakeups and single-lock contention.
- The 5.7 dense_hash_map patch only replaces `std::map` in writeset history. No bundled 8.0+ dense_hash_map counterpart is present.

Validation focus:

- Keep `sync_binlog`, `innodb_flush_log_at_trx_commit`, GTID, and writeset settings identical across comparisons.
- Run replication/binlog MTR, crash-safe binlog coverage, relay log cases, and mysqlbinlog readback regression.

## Network Multipath Optimization

Applicable signals:

- Hot `vio_read`, `vio_write`, `net_read_packet`, `send`, `recv`, `poll`, `epoll_wait`, or `THD_WAIT_NET`.
- Multi-NIC or multiqueue environments show single-queue or single-NUMA-node bottlenecks.
- CPU is not saturated, but TPS is limited by network throughput, IRQ handling, or softirq load.

Bundled patch status:

- No clear MySQL source patch for network multipath exists in the bundled 5.7 or 8.0+ patch set.
- Treat the hikunpeng network multipath document as deployment and system-tuning guidance.

Suggested direction:

- Check RSS/RPS/XPS, IRQ affinity, multiqueue, bond/team configuration, multi-IP or multi-connection distribution, and client connection distribution.
- Do not inspect mysqld hotspots alone. Also collect `sar -n DEV/TCP/ETCP`, `ethtool -S`, and softirq CPU distribution.

## Fine-Grained Lock Optimization

Applicable signals:

- High cost in `lock_sys`, `lock0lock.cc`, `lock_rec_lock`, `lock_table`, `sync_array`, or InnoDB mutex/rwlock paths.
- Heavy concurrent DML, hot tables, row/table intention-lock queue scans, deadlock detection, or lock_sys mutex contention.

Preferred strategy:

- For 5.7, use `LOCK_TABLE ... same table` to reduce intention-lock queue scanning.
- For 5.7, use `WL#10314 sharded lock_sys mutex` to shard lock_sys protection. This has a larger risk and code-change surface.
- No bundled 8.0+ fine-grained lock_sys patch is present. If the target version already includes upstream sharded lock_sys support, do not port it again.

Validation focus:

- Concurrent update/select for update/insert, deadlock detection, foreign keys, AUTO_INC, and mixed DDL+DML.
- Run InnoDB lock/deadlock/monitor and Performance Schema lock instrumentation MTR coverage.

## Lock-Free / ReadView Optimization

Applicable signals:

- Hot `MVCC::view_open`, `ReadView::prepare`, `ReadView::changes_visible`, `trx_sys->mutex`, `rw_trx_ids`, or read view list operations.
- Read-heavy or read-mostly workloads, RC/RR snapshot reads, and short-transaction point selects where read view create/close cost is high.

Preferred strategy:

- For 5.7, use the read view version tracking patch. The MVCC readview data-structure optimization in the same directory is a related candidate; check conflicts before applying both.
- For 8.0+, apply `readview-opt/0001`, then evaluate `readview-opt/0002` for the race-crash fix.

Validation focus:

- Short transactions under RC/RR, autocommit non-locking selects, long transaction plus purge, clone read view, and crash/race regression.

## NUMA Scheduling Optimization

Applicable signals:

- `numastat` remote accesses are high, cross-socket memory access is high, HCCS/interconnect bandwidth is high, or mysqld threads and memory are imbalanced.
- Large buffer pool instances, connection threads, IO, or IRQ placement does not match memory nodes.

Bundled patch status:

- No standalone NUMA scheduling source patch is present in the bundled patch directories. 8.0+ has adjacent container-aware capabilities, but they do not replace NUMA strategy.

Suggested direction:

- Identify the NUMA nodes for mysqld, clients, IRQs, and storage interrupts.
- Compare `numactl --interleave=all`, per-socket binding, buffer pool warmup, and IRQ/RSS affinity.
- In containers, confirm cpuset/memset constraints match what MySQL observes for CPU and memory limits.

## CRC32 Instruction Optimization

Applicable signals:

- Hot `ut_crc32`, `ut_crc32_sw`, page checksum, redo/checksum, or `buf_page_is_corrupted`.
- On AArch64, the compiler did not enable CRC intrinsics or runtime dispatch is not using hardware CRC32.

Preferred strategy:

- For 5.7, use `0001-add-ut_crc32_hw-for-arm-platform.patch`. It checks `arm_acle.h` and `HWCAP_CRC32/PMULL`, then implements the ARM CRC32 path.
- No standalone 8.0+ CRC32 patch exists in the bundled directory. First confirm whether the target 8.0+ already has hardware CRC32 support and correct compiler flags.

Validation focus:

- Confirm CMake reports ARMv8 CRC32 intrinsic support.
- Stress checksum/redo paths and run InnoDB checksum plus crash recovery regression.

## Text Huge Pages

Applicable signals:

- High iTLB miss, instruction TLB stalls, L1I/DSB/ICache metrics, with hotspots spread across mysqld `.text`.
- CPU-bound workload where perf points to frontend instruction-fetch pressure instead of data locks or IO.

Preferred strategy:

- For 5.7, use the text remapping to huge pages patch.
- For 8.0+, use the text huge pages for AArch64 patch.
- Check the added `text_huge_pages` variable and the THP/explicit hugepage environment.

Validation focus:

- Compare `perf stat` frontend metrics such as iTLB, L1I, and branch/frontend stalls.
- Watch perf symbols: once code text is mapped to huge pages, perf may need a generated perf map.

## Thread Pool Optimization

Applicable signals:

- With thread pool enabled, CPU usage and context-switch rates oscillate, or active worker count is too high or too low.
- `Threadpool_statistics_detail`, `ru_nvcsw`, `ru_nivcsw`, group commit pending wait, or order commit flush wait is relevant.
- Thread pool scheduling limits throughput in high-concurrency short-transaction workloads.

Preferred strategy:

- The 5.7 patch backports adaptive threadpool concurrency from 8.0 and adds `thread_pool_enable_extra_threads`, `thread_pool_cpu_usage_threshold`, `thread_pool_nvcsw_freq_threshold`, and `thread_pool_nivcsw_freq_threshold`.
- The 8.0+ patch adds or adjusts `thread_pool_commit_burst_threads`, CPU/context-switch thresholds, and `Threadpool_statistics_detail`.

Validation focus:

- Compare `pool_of_threads`, new sys_vars tests, and binlog group commit stress tests.
- Watch TPS, P99, context switches, and whether `active_threads_quota` behaves as expected.

## Plan Cache

Applicable signals:

- On 8.0+, many repeated simple SELECT statements are hot in `JOIN::optimize`, `sql_optimizer.cc`, range optimizer, or plan construction.
- SQL text or query shape is stable, table row-count change is controlled, and optimizer cost is high relative to execution cost.

Preferred strategy:

- Recommend the bundled 8.0+ `0001-Add-plan-cache-to-improve-select-performance.patch`.
- Adds `plan_cache` and `plan_cache_allow_change_ratio`. Default `plan_cache=ON`; cached plans are invalidated when row-count change exceeds the ratio, while 0 means always valid.
- Do not recommend this for 5.7 unless the user explicitly asks for porting and accepts substantial SQL-layer risk.

Validation focus:

- Repeated point select, range select, prepared/non-prepared execution, statistics change, ANALYZE TABLE, DDL, and optimizer trace.
- Run optimizer, range optimizer, prepared statement, sys_vars, and Performance Schema memory-key regression.

## ARM Foundation Micro-Optimizations

Applicable signals:

- Hot atomic operations, rw-locks, memory barriers, unaligned access, cacheline behavior, branch prediction, or AArch64 compile flags.
- perf points to `sync0rw`, `os_atomic`, `ut_delay`, unaligned load/store, or low-level utility functions.

Preferred strategy:

- This skill no longer bundles ARM foundation micro-optimization patches.
- For these hotspots, first check whether a more specific strategy such as compute path, locking, or CRC32 already covers the case. If not, treat it as external patch porting, build-flag tuning, or deployment tuning.
- These changes often intersect with lock and compute-path work. Classify by hotspot first, then check conflicts.

Validation focus:

- CMake flags, target CPU features, debug/release differences, and concurrency lock regression.

## Container-Aware Optimization

Applicable signals:

- MySQL 8.0+ runs in cgroup/container environments and the CPU/memory limits seen by mysqld do not match container limits.
- Log write or resource group behavior causes CPU overuse or scheduling anomalies under container constraints.

Preferred strategy:

- For 8.0+, reference `container_aware/` patches for cgroup v1/v2, InnoDB container awareness, and log write conditions.
- No bundled 5.7 counterpart exists.

Validation focus:

- cgroup v1/v2, Docker/Kubernetes, cpuset/memory.limit, resource group, and log writer stress tests.
