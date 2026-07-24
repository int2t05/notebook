# DevKit Top-Down Metrics Reference

Full reference for all metrics in the devkit top-down report. Based on ARM PMUv3 events.

## Level 1: Top-Level Categories

### Retiring
Percentage of pipeline slots that successfully retired uOps. High Retiring = good. The processor is spending its time doing useful work rather than being stalled.

- High (>50%): Excellent — compute or well-optimized code
- Medium (20-50%): Normal for memory-intensive workloads
- Low (<20%): Heavily stalled, check Backend/Frontend

### Bad Speculation
Pipeline slots wasted due to incorrect speculation (branch mispredicts, machine clears/nukes). This is pure waste — these uOps should never have been issued.

Sub-categories:
- **Branch Mispredicts**: Wrong branch direction prediction causes pipeline flush
  - `Other Branch`: Regular conditional/direct branches mispredicted
  - `Indirect Branch`: Indirect branch mispredict (function pointers, virtual calls, switch statements)
  - `Push/Pop Branch`: Return stack buffer mispredict
- **Machine Clears**: Pipeline cleared due to memory ordering violations or self-modifying code
  - `Nuke Flush`: Full pipeline nuke (typically from memory disambiguation failures)

High Bad Speculation → check for unpredictable branches, large switch statements, or inconsistent patterns in the hot loop.

### Frontend Bound
Frontend cannot deliver enough uOps to keep the backend busy. The instruction fetch / decode pipeline is the bottleneck.

Sub-categories:
- **Fetch Latency Bound**: Frontend waiting for instructions (ICache miss, ITLB miss, branch mispredict flush)
  - `ICache Miss`: Code footprint too large for L1 instruction cache
  - `ITLB Miss`: Code spread across too many pages
  - `BP_Misp_Flush`: Frontend bubbles after branch mispredict
  - `OoO Flush`: Out-of-order pipeline flush stalls
- **Fetch Bandwidth Bound**: Decode width limitation — the frontend is fetching but can't decode fast enough. Common with high-density of complex/long-latency instructions.

### Backend Bound
Backend cannot accept more uOps. This is where most performance problems live. Split into **Core Bound** and **Memory Bound**.

## Level 2: Backend Sub-Categories

### Core Bound
Backend stalled because execution units are saturated. The processor has enough data but can't process it fast enough.

- **FDIV Stall**: Pipeline stall due to floating-point divide (very slow operation)
- **DIV Stall**: Pipeline stall due to integer divide
- **FSU Stall**: Floating-point/Store Unit stall. FMA operations competing with store instructions for write ports. Common in DGEMM where results are written back to C matrix.
- **Resource Bound** (approximate): Microarchitectural resource constraints
  - `Rob_stall`: Reorder Buffer full — too many in-flight instructions
  - `Ptag_stall`: Physical register file tag shortage — too many live values. Common in unrolled loops with many temporaries.
  - `MapQ_stall`: Map queue (register rename queue) full
  - `PCBuf_stall`: PC buffer stall
- **Exe Ports Util**: Execution port utilization — the most important Core Bound metric
  - `0 ports serialize`: No ports available AND a serializing operation is in flight
  - `0 ports non serialize`: **No ports available** — all execution units busy. High value = compute-saturated.
  - `1 ports`: Exactly 1 port busy per cycle
  - `2 ports`, `3 ports`, ..., `6p ports`: Multiple ports busy — good utilization

**Port utilization interpretation:**
- High `0 ports non serialize` = compute limited (all FMA/ALU pipes full)
- High `1 ports` + low `0 ports` = limited ILP or load bandwidth limited (only 1 port doing load)
- High `2+ ports` = good parallel execution (loads + compute in parallel)

### Memory Bound
Backend stalled waiting for data from the memory hierarchy. This is the most common bottleneck for data-intensive workloads.

- **L1 Bound**: Stalls at L1 data cache level
  - `DTLB`: Data TLB miss (data spread across too many pages → use huge pages)
  - `Misalign`: Unaligned memory access penalty. Common with odd strides or packed data.
  - `Resource Full`: L1 load/store queue full — too many in-flight memory operations. Try reducing memory-level parallelism or using cache-blocking.
  - `Instruction Type`: Certain instruction types (load-pair, etc.) stalling
  - **Forward hazard**: Store-to-load forwarding stall. A load depends on a recent store that hasn't committed yet. Shows up in read-modify-write patterns like `C[i] += A[i]*B[i]`.
  - **Structure hazard**: L1 cache port contention. Multiple loads/stores competing for the same L1 access port. Critical for DGEMM where matrix A, B, C loads compete.
  - `Pipeline`: L1 pipeline stall (bank conflicts, etc.)

- **L2 Bound**: Stalls at L2 cache level
  - `buffer pending`: L2 request buffer full — too many outstanding L2 requests
  - **snoop pending**: Waiting for L2 snoop (cache coherence check from other cores). Even on single-core, hardware prefetcher may trigger snoops. High value → minimize cross-core sharing or pin to isolated cores.
  - `Arb idle`: L2 arbiter idle — waiting for L2 to respond. Common with L2 misses.
  - `Pipeline`: L2 pipeline stall

- **L3 or DRAM Bound**: Stalls waiting for L3 cache or main memory (DRAM). This is the most expensive stall — often 100+ cycles.
  - High value → improve cache blocking, use software prefetch, or restructure data layout

- **Store Bound**: Stalls related to store operations
  - `SCA`: Store commit area full — too many pending stores
  - `Head`: Store head of queue blocked
  - `Order`: Store ordering constraint (memory barriers, strongly-ordered memory)

## Practical Analysis Flow

1. Check **IPC** first — low IPC means something is wrong
2. Look at Level 1 breakdown: where is the biggest %?
3. If **Retiring > 40%**: you're in good shape, look at sub-components for fine-tuning
4. If **Backend Bound > 50%**: 
   - Drill into Core vs Memory split
   - If Memory dominates → cache/memory optimization needed
   - If Core dominates → check Exe Ports Util for execution unit saturation
5. If **Frontend Bound > 10%**: code layout or decode issues
6. If **Bad Speculation > 5%**: branch prediction problems

## ARM PMU Events (r-prefix)

The raw PMU event counts in the report section map to ARM PMUv3 events:
- `r0008` = INST_RETIRED
- `r0011` = CPU_CYCLES
- `r0027` = BR_MIS_PRED
- `r2004-r2012` = L1D/L2D cache events
- `r5090-r50a3` = Core Bound related
- `r7000-r7020` = Top-down specific events

These are informational; focus on the Top-down percentages, not raw event counts.
