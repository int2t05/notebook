---
name: kunpeng-mysql-optimize
description: Select Kunpeng ARM/AArch64 MySQL, Percona Server, or mysqld performance tuning strategies. Use when an AI agent, coding agent, or automated tuning assistant needs to analyze perf top output, flamegraphs, POC benchmark symptoms, MySQL 5.7 or 8.0+ version differences, hikunpeng MySQL optimization docs, and bundled Kunpeng patches, then recommend compute-path, binlog, network multipath, fine-grained locking, lock-free/ReadView, NUMA, CRC32, text huge page, thread pool, plan cache, ARM build, or container-aware optimizations.
---

# Kunpeng MySQL Optimization

## Workflow

1. Confirm the inputs first: MySQL/Percona version, CPU platform, workload, perf top/flamegraph hotspots, key wait events, and whether the deployment uses containers, NUMA, or multiple NICs.
2. If the user provides perf text or hotspot names, run `scripts/suggest_optimizations.py` first to generate candidate strategies:

```bash
python3 <skill-dir>/scripts/suggest_optimizations.py \
  --mysql-version 8.0.30 \
  --perf-report perf.txt
```

3. The default patch root is `<skill-dir>/assets/patches`. Only pass `--patch-root <external-dir>` when the user explicitly provides a newer external patch repository.
4. Read `references/optimization-map.md` to verify the script suggestions against hotspot functions, wait events, and system metrics.
5. Read `references/patch-inventory.md` to select patch paths by MySQL version. Do not recommend 5.7 patches directly for 8.0+, and do not assume 8.0+ has every 5.7 counterpart.
6. If hikunpeng docs conflict with bundled patch contents, use this priority order: bundled same-version or same-series patch > bundled near-version patch code facts > hikunpeng doc description. When no bundled patch exists, label the item as a deployment/configuration direction and do not invent a patch.
7. In the final recommendation include: evidence, recommended strategy, version-matched patches, likely conflicts, validation commands or regression scope, and rollout risks.

## Resource Routing

- Read `references/optimization-map.md` when choosing strategies from hotspots.
- Read `references/patch-inventory.md` when listing or verifying patch paths.
- Read `references/hikunpeng-notes.md` when explaining hikunpeng docs or items with no bundled patch.
- Copy or apply patches from `assets/patches/`; do not reference absolute paths from the machine that created this skill.
- If a patch path ends with `.patch.gz`, decompress it to `.patch` before applying it with `git apply` or `patch`; keep the compressed file for distribution.
- Use the script for fast screening only. Treat script output as candidates and verify against the references and the user's environment before final advice.

## Output Requirements

- Do not force English or Chinese output. Follow the language explicitly requested by the user or calling agent; if none is specified, match the main language of the current conversation.
- Clearly distinguish directly usable bundled patches, patches that require porting, and deployment/configuration-only optimizations.
- For concurrency-sensitive patches such as lock, binlog, thread pool, and plan cache changes, tell the user to apply them on an isolated branch and run MTR plus stress regression before rollout.
- Do not apply patches automatically unless the user explicitly asks.
- If hotspot evidence is insufficient, ask for concrete data such as `perf top -g`, flamegraphs, `perf stat`, Performance Schema waits, `SHOW ENGINE INNODB STATUS`, NUMA counters, or NIC metrics.
