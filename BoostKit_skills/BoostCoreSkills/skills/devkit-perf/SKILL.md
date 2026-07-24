---
name: devkit-perf
description: Use the devkit tuner tool to run top-down performance analysis on benchmarks, identify CPU microarchitectural bottlenecks, and compare performance between implementations. Use this skill whenever the user mentions devkit, top-down analysis, CPU performance profiling, microarchitectural bottlenecks, or wants to understand where a program is stalling (Frontend/Core/Memory bound).
---

# DevKit Top-Down Performance Analysis

Use the `devkit tuner top-down` command to run CPU microarchitectural performance analysis based on the Intel Top-Down methodology adapted for ARM AArch64.

## Quick start

```bash
devkit tuner top-down -L 0 ./benchmark [args...]
```

- `-L 0` : collect ALL metrics (levels 0–6)
- The tool spawns the workload, collects PMU counters, and prints a report
- A `.tar` file is generated for later review with `devkit report`

## Important options

| Option | Description |
|--------|-------------|
| `-L {0..6}`| Detail level: 0=ALL, 1=summary, 2=Core, 3=Memory, 5=BadSpec, 6=Frontend |
| `-d <sec>` | Collection duration in seconds |
| `-D <sec>` | Delay before starting collection |
| `-i <sec>` | Sampling interval for sub-reports |

## Understanding the Top-Down Report

The report breaks CPU pipeline slots into 4 level-1 categories that sum to 100%:

### Level 1: The Four Buckets

| Category | Meaning | High % indicates |
|----------|---------|-----------------|
| **Retiring** | uOps that successfully retired | Efficient execution, good IPC |
| **Bad Speculation** | Wasted work from mispredicted branches | Branch predictor struggles, unpredictable code paths |
| **Frontend Bound** | Frontend can't feed backend fast enough | I-cache misses, ITLB misses, fetch bandwidth limit |
| **Backend Bound** | Backend can't accept more uOps | Data stalls (Memory) or execution port saturation (Core) |

### Level 2: Backend Break-down

Backend Bound splits into two sub-categories:

| Sub-category | Meaning | Key sub-metrics |
|-------------|---------|-----------------|
| **Core Bound** | Execution units overloaded | `Exe Ports Util` — how many ports are busy/cycle |
| **Memory Bound** | Waiting for data from cache/memory | `L1 Bound`, `L2 Bound`, `L3 or DRAM Bound` |

### Core Bound detail

| Metric | Meaning |
|--------|---------|
| `0 ports non serialize` | % of cycles with ZERO execution ports available — all busy |
| `1 ports` | % of cycles with 1 port busy |
| `2+ ports` | % of cycles with 2+ ports busy |
| `FSU Stall` | Floating-point / Store Unit pipeline stall |
| `Ptag_stall` | Physical register file / rename buffer pressure |

**Rule of thumb:** High `0 ports non serialize` = compute-saturated. Low `0 ports` + high Memory Bound = memory-limited.

### Memory Bound detail

| Metric | Meaning |
|--------|---------|
| `L1 Bound → Structure hazard` | L1 cache port contention (load/store conflicts with compute) |
| `L1 Bound → Forward hazard` | Load-hit-store / store-to-load forwarding stalls |
| `L2 Bound → snoop pending` | Waiting for L2 snoop (cache coherence from other cores) |
| `L2 Bound → Arb idle` | L2 arbiter idle (waiting for L2 response) |
| `L3 or DRAM Bound` | L3 miss waiting for DRAM |

### Frontend Bound detail

| Metric | Meaning |
|--------|---------|
| `Fetch Bandwidth Bound` | Decode width cannot keep up — complex/long instructions |
| `ICache Miss` | Instruction cache miss |
| `ITLB Miss` | Instruction TLB miss |

## Comparison Workflow

When comparing two benchmarks (e.g., pure compute kernel vs. full application), run both with the same `-L 0` level and create a comparison table:

```bash
# Run both benchmarks
devkit tuner top-down -L 0 ./bench1 2>&1 | tee bench1.log
devkit tuner top-down -L 0 ./bench2 2>&1 | tee bench2.log
```

Then compare these key dimensions:

1. **IPC** — Higher is better; which one has better utilization?
2. **Retiring %** — Higher = more useful work per cycle
3. **Memory Bound %** — Higher = more time waiting for data
4. **Core Bound / 0 ports busy** — Higher = more compute-saturated
5. **Frontend Bound %** — Higher = instruction fetch issues (complex code paths)
6. **FSU Stall / Ptag stall** — Indicates register/execution resource pressure
7. **L1 Structure Hazard** — L1 port contention (load vs. compute)

Create a side-by-side table of level-1 metrics and drill into the biggest deltas. Focus on the *change* between benchmarks — the absolute numbers matter less than the difference.

## Example: Compute-bound vs Memory-bound

A pure FMLA loop (all data in registers) vs DGEMM (matrix multiply from memory):

| Metric | Pure FMLA | DGEMM | Diagnosis |
|--------|-----------|-------|-----------|
| Memory Bound | <1% | ~6% | DGEMM waits for cache/memory |
| 0 ports busy | ~60% | ~25% | FMLA saturates execution; DGEMM ports idle waiting for loads |
| L1 Structure Hazard | 0% | ~2% | Load/store port contention in L1 |
| Frontend Bound | 0% | ~10% | DGEMM has complex multi-level tiling code |

For detailed explanation of all metrics, read `references/metrics.md`.

## Troubleshooting devkit

- **"no such process"** — The workload exited too quickly. Lengthen the benchmark (more iterations, larger data). devkit needs at least a few hundred milliseconds of runtime.
- **"Options -c/--cpu, workload cannot be used together"** — Use `taskset` inside the workload or set CPU affinity in-code instead of `-c`.
