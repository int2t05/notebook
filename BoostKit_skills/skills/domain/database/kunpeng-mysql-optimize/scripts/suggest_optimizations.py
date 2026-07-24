#!/usr/bin/env python3
"""Recommend Kunpeng MySQL optimization strategies from perf hotspot text."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PATCH_ROOT = SKILL_DIR / "assets" / "patches"


Strategy = Dict[str, object]


STRATEGIES: Dict[str, Strategy] = {
    "compute_path": {
        "name": "Compute-path optimization",
        "keywords": [
            "cmp_dtuple",
            "dtuple",
            "rem0cmp",
            "page_cur_search",
            "rec_get_offsets",
            "row_sel_field_store",
            "my_convert",
            "ctype",
            "utf8",
            "utf8mb4",
            "collation",
            "my_strnncoll",
            "my_well_formed",
            "item_func_like",
            "like",
            "skip_trailing_space",
            "space",
            "memcmp",
        ],
        "signals": "Record comparison, charset conversion, LIKE, space skipping, collation, or InnoDB search/row-select work dominates CPU.",
        "patches": {
            "5.7": [
                "PS-57-patch/0001-fast-tuple-comparing.patch",
                "PS-57-patch/0001-optimize-character-with-neon.patch",
                "PS-57-patch/0001-optimize-my_convert-for-aarch64.patch",
                "PS-57-patch/0001-optimize-mysqld-s-branch-alignment-in-kunpeng-platfo.patch",
                "PS-57-patch/0001-optimize-space-skipping-with-neon.patch",
                "PS-57-patch/0001-optimize-Item_func_like-with-neon.patch",
                "PS-57-patch/0001-optimize-utf8-utf8mb4-charset-handler.patch",
                "PS-57-patch/0001-non-aligned-memory-access-optimize-for-aarch64.patch",
                "PS-57-patch/0001-rec_get_offsets-optimize.patch",
                "PS-57-patch/0001-speedup-collation-lookup.patch",
                "PS-57-patch/0001-inline-row_sel_field_store_in_mysql_format_func.patch",
            ],
            "8.0": [
                "PS-8043-patch/0001-fast-tuple-record-comparing.patch",
                "PS-8043-patch/0001-optimize-Item_func_like-with-neon.patch",
                "PS-8043-patch/0001-optimize-utf8-utf8mb4-charset-handler.patch",
                "PS-8043-patch/0002-optimize-space-skipping-with-neon.patch",
                "PS-8043-patch/0003-non-aligned-memory-access-optimize-for-aarch64.patch",
                "PS-8043-patch/0005-rec_get_offsets-optimize.patch",
                "PS-8043-patch/0008-remove-some-release-assert-and-add-some-branch-predi.patch",
            ],
        },
        "verify": "Run sysbench read_only/point_select plus charset, LIKE, collation, and InnoDB row-search MTR coverage.",
    },
    "binlog": {
        "name": "Binlog optimization",
        "keywords": [
            "binlog",
            "mysql_bin_log",
            "ordered_commit",
            "commit_stage",
            "group_commit",
            "sync_binlog",
            "flush",
            "fsync",
            "pwrite",
            "writeset",
            "dense_hash",
            "rpl_commit_stage_manager",
        ],
        "signals": "With binlog enabled, ordered commit, flush/sync, writeset history, or binlog file growth dominates.",
        "patches": {
            "5.7": [
                "PS-57-patch/0001-binlog-replace-std-map-with-dense_hash_map.patch",
                "PS-57-patch/0001-improving-binlog-s-flushing-with-preallocated-binlog.patch",
                "PS-57-patch/0001-optimize-binlog-order-commit.patch",
            ],
            "8.0": [
                "PS-8043-patch/0001-optimize-binlog-write-performance-preallocated-binlo.patch",
                "PS-8043-patch/0004-optimize-binlog-ordered-commit.patch",
            ],
        },
        "verify": "Run binlog/replication MTR, write stress, GTID/writeset, sync_binlog, and crash-safe cases.",
    },
    "network_multipath": {
        "name": "Network multipath optimization",
        "keywords": [
            "vio_read",
            "vio_write",
            "net_read_packet",
            "thd_wait_net",
            "recv",
            "send",
            "epoll",
            "poll",
            "tcp",
            "softirq",
            "rss",
        ],
        "signals": "Network send/receive, softirq, single queue, or THD_WAIT_NET limits throughput.",
        "patches": {"5.7": [], "8.0": []},
        "verify": "Collect sar, ethtool, IRQ, RSS/RPS/XPS, and client connection distribution. No clear bundled source patch exists.",
    },
    "fine_grained_lock": {
        "name": "Fine-grained lock optimization",
        "keywords": [
            "lock_sys",
            "lock0lock",
            "lock_table",
            "lock_rec",
            "deadlock",
            "sync_array",
            "row0ins",
            "mutex_enter",
            "rw_lock",
        ],
        "signals": "InnoDB lock_sys, table/record lock queues, deadlock detection, or mutex/rwlock contention is high.",
        "patches": {
            "5.7": [
                "PS-57-patch/lock_sys_opt/0001-LOCK_TABLE-CAN-BE-OPTIMIZED-IF-UPDATING-THE-SAME-TAB.patch",
                "PS-57-patch/lock_sys_opt/0001-WL-10314-InnoDB-Lock-sys-optimization-sharded-lock_s.patch",
            ],
            "8.0": [],
        },
        "verify": "Run InnoDB lock/deadlock/monitor MTR plus concurrent DML, DDL+DML, AUTO_INC, and foreign-key regression.",
    },
    "readview_lockfree": {
        "name": "Lock-free / ReadView optimization",
        "keywords": [
            "readview",
            "read view",
            "mvcc::view_open",
            "changes_visible",
            "trx_sys",
            "trx_sys_mutex",
            "rw_trx_ids",
            "read0read",
            "view_close",
        ],
        "signals": "Read view create/close/reuse or trx_sys contention is high in short snapshot-read transactions.",
        "patches": {
            "5.7": [
                "PS-57-patch/0001-innodb-enhance-read-view-management-with-version-tra.patch",
                "PS-57-patch/0001-optimize-mvcc-readview-data-structure.patch",
            ],
            "8.0": [
                "PS-8043-patch/readview-opt/0001-innodb-enhance-read-view-management-with-version-tra.patch",
                "PS-8043-patch/readview-opt/0002-Bug-37628911-Crash-caused-by-race-condition-between-.patch",
            ],
        },
        "verify": "Run RC/RR snapshot reads, autocommit selects, long transaction plus purge, crash, and race regression.",
    },
    "numa": {
        "name": "NUMA scheduling optimization",
        "keywords": [
            "numa",
            "remote",
            "numastat",
            "hccs",
            "hha",
            "memory bandwidth",
            "cpuset",
            "memset",
        ],
        "signals": "Remote NUMA access, cross-socket bandwidth, or thread/memory/IRQ node mismatch is visible.",
        "patches": {"5.7": [], "8.0": []},
        "verify": "Compare numactl binding/interleave, IRQ affinity, and buffer pool warmup. No standalone bundled source patch exists.",
    },
    "crc32": {
        "name": "CRC32 instruction optimization",
        "keywords": [
            "ut_crc32",
            "crc32",
            "crc32c",
            "checksum",
            "buf_page_is_corrupted",
            "arm_acle",
            "__crc32",
        ],
        "signals": "InnoDB page/redo checksum or CRC32 calculation dominates CPU.",
        "patches": {
            "5.7": ["PS-57-patch/0001-add-ut_crc32_hw-for-arm-platform.patch"],
            "8.0": [],
        },
        "verify": "Confirm CMake detects ARMv8 CRC32 intrinsics, then run checksum and crash-recovery regression.",
    },
    "text_huge_pages": {
        "name": "Text huge pages",
        "keywords": [
            "itlb",
            "i-tlb",
            "instruction tlb",
            "l1i",
            "icache",
            "dsb",
            "text_huge_pages",
            "hugepage_text",
            "large_page",
            "front-end",
            "frontend",
        ],
        "signals": "iTLB/L1I/frontend metrics are high and CPU-bound hotspots are spread across mysqld .text.",
        "patches": {
            "5.7": ["PS-57-patch/0001-add-text-remapping-to-huge-pages.patch.gz"],
            "8.0": ["PS-8043-patch/0007-add-text-huge-pages-for-aarch64-platform.patch.gz"],
        },
        "verify": "Compare perf stat frontend metrics. Watch perf symbols because huge-page text mapping may need a perf map.",
    },
    "thread_pool": {
        "name": "Thread pool optimization",
        "keywords": [
            "thread_pool",
            "threadpool",
            "active_threads_quota",
            "threadpool_statistics_detail",
            "nvcsw",
            "nivcsw",
            "context switch",
            "group_commit_pending",
            "order_commit_flush",
        ],
        "signals": "With thread pool enabled, active workers, CPU usage, context switches, or group commit waits limit throughput.",
        "patches": {
            "5.7": ["PS-57-patch/tp-opt/0001-threadpool-adjust-concurrency-using-scheduler-statis.patch"],
            "8.0": ["PS-8043-patch/tp-opt/0001-adjust-threadpool-concurrency-using-scheduler-statis.patch"],
        },
        "verify": "Run pool_of_threads, new sys_vars tests, Threadpool_statistics_detail checks, and TPS/P99/context-switch comparisons.",
    },
    "plan_cache": {
        "name": "Plan cache",
        "keywords": [
            "plan_cache",
            "join::optimize",
            "sql_optimizer",
            "range_optimizer",
            "test_quick_select",
            "repeated select",
            "point select",
            "optimizer",
        ],
        "signals": "On 8.0+, repeated simple SELECT statements spend significant CPU in optimizer or plan construction.",
        "patches": {
            "5.7": [],
            "8.0": ["PS-8043-patch/0001-Add-plan-cache-to-improve-select-performance.patch"],
        },
        "verify": "Run repeated SELECT, ANALYZE/DDL invalidation, optimizer trace, prepared statement, and sys_vars regression.",
    },
    "arm_foundation": {
        "name": "ARM foundation micro-optimizations",
        "keywords": [
            "lse",
            "aarch64",
            "arm64",
            "memory barrier",
            "sync0rw",
            "os_atomic",
            "cacheline",
            "unaligned",
            "non-aligned",
            "branch prediction",
            "ut_delay",
        ],
        "signals": "Low-level hotspots appear in atomics, memory barriers, unaligned access, cacheline behavior, or branch prediction.",
        "patches": {"5.7": [], "8.0": []},
        "verify": "This skill no longer bundles ARM foundation micro-optimization patches; evaluate external patch porting or deployment/build tuning instead.",
    },
    "container_aware": {
        "name": "Container-aware optimization",
        "keywords": [
            "container",
            "cgroup",
            "docker",
            "kubernetes",
            "cpuset",
            "memory.limit",
            "resource group",
            "log write",
        ],
        "signals": "In 8.0+ container environments, CPU/memory limit detection, resource groups, or log writer behavior is abnormal.",
        "patches": {
            "5.7": [],
            "8.0": [
                "PS-8043-patch/container_aware/0001-WL-16484-Make-InnoDB-container-aware.patch",
                "PS-8043-patch/container_aware/0002-Bug-37993516-Handle-cgroup-v1-default-memory-limit.patch",
                "PS-8043-patch/container_aware/0003-Bug-37993516-Handle-cgroup-v1-default-memory-limit-p.patch",
                "PS-8043-patch/container_aware/0004-Enhance-log-write-conditions-to-prevent-CPU-overutil.patch",
            ],
        },
        "verify": "Run cgroup v1/v2, Docker/Kubernetes, resource group, and log writer stress tests.",
    },
}


def normalize_version(version: str) -> str:
    v = version.lower().strip()
    if v.startswith("5.7") or v in {"57", "ps57", "mysql57"}:
        return "5.7"
    if v.startswith("8.") or v in {"80", "8.0", "8043", "ps8043"}:
        return "8.0"
    return "unknown"


def display_version(version: str) -> str:
    return "8.0+" if version == "8.0" else version


def read_input(args: argparse.Namespace) -> str:
    parts: List[str] = []
    if args.hotspots:
        parts.extend(args.hotspots)
    if args.perf_report:
        parts.append(Path(args.perf_report).read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts).lower()


def score_strategy(text: str, strategy: Strategy) -> int:
    return sum(text.count(keyword.lower()) for keyword in strategy["keywords"])  # type: ignore[index]


def patch_lines(patches: Iterable[str], patch_root: Path) -> List[str]:
    lines = []
    for rel in patches:
        full = patch_root / rel
        suffix = "" if full.exists() else "  (not found; verify the patch root)"
        lines.append(f"  - `{full}`{suffix}")
    return lines


def print_strategy(key: str, score: int, version: str, patch_root: Path) -> None:
    strategy = STRATEGIES[key]
    patches_by_version = strategy["patches"]  # type: ignore[index]
    patches = patches_by_version.get(version, []) if isinstance(patches_by_version, dict) else []

    print(f"## {strategy['name']} (match score: {score})")
    print()
    print(f"- Evidence: {strategy['signals']}")
    print(f"- Validation focus: {strategy['verify']}")
    if version == "unknown":
        print("- Patches: version not recognized. Use `--mysql-version 5.7`, `--mysql-version 8.0`, or a specific 8.0.x version.")
    elif patches:
        print("- Recommended patches:")
        print("\n".join(patch_lines(patches, patch_root)))
    else:
        print("- Recommended patches: no clear bundled source patch for this MySQL version; treat as deployment tuning or a porting task.")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend Kunpeng MySQL optimization strategies from hotspots")
    parser.add_argument("--mysql-version", default="unknown", help="Example: 5.7, 8.0, 8.0.30, PS-8043")
    parser.add_argument("--perf-report", help="Text file containing perf report/top/flamegraph output")
    parser.add_argument("--hotspots", nargs="*", help="Hotspot functions or symptom text passed directly")
    parser.add_argument(
        "--patch-root",
        default=str(DEFAULT_PATCH_ROOT),
        help="Patch root directory; defaults to the skill-bundled assets/patches",
    )
    parser.add_argument("--top", type=int, default=5, help="Maximum number of candidate strategies to print")
    parser.add_argument("--list", action="store_true", help="List all strategies")
    parser.add_argument("--all-if-unknown", action="store_true", help="Print all strategies when no match is found")
    args = parser.parse_args()

    version = normalize_version(args.mysql_version)
    patch_root = Path(args.patch_root)

    if args.list:
        for key, strategy in STRATEGIES.items():
            print(f"{key}: {strategy['name']}")
        return 0

    text = read_input(args)
    if not text:
        parser.error("Provide --perf-report or --hotspots")

    scored = [
        (key, score_strategy(text, strategy))
        for key, strategy in STRATEGIES.items()
    ]
    scored = [(key, score) for key, score in scored if score > 0]
    scored.sort(key=lambda item: item[1], reverse=True)

    print(f"# Kunpeng MySQL Optimization Candidates (version: {args.mysql_version} -> {display_version(version)})")
    print()

    if not scored:
        print("No clear strategy matched the input. Provide perf top/flamegraph data, wait events, or system metrics.")
        if args.all_if_unknown:
            print()
            scored = [(key, 0) for key in STRATEGIES]
        else:
            return 0

    for key, score in scored[: max(args.top, 1)]:
        print_strategy(key, score, version, patch_root)

    print("Note: script output is only a candidate list. Verify with references/optimization-map.md and references/patch-inventory.md before making final recommendations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
