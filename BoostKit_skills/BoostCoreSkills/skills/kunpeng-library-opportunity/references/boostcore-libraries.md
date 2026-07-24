# BoostCore Library Matching Reference

Snapshot source: `https://gitcode.com/boostkit/boostcore`, commit `3ce36c410ab0ccedfc75f1c70b4f9d6fe70954dc`, inspected 2026-06-10.

Use this as a local matching guide, not as proof of the latest community state. Refresh the upstream repository when exact availability, version, support status, or installation paths matter.

## Core Candidates

| Area | Candidate | Runtime or build signals | Opportunity | Validation notes |
| --- | --- | --- | --- | --- |
| KAE Kunpeng Acceleration Engine | KAE | `libssl.so`, `libcrypto.so`, OpenSSL `EVP_*`, `SSL_*`, AES, SHA, RSA, zlib `deflate` or `inflate`, TLS or compression CPU hotspots | Hardware acceleration for SSL/TLS and compression through standard OpenSSL and zlib style interfaces | Confirm Kunpeng CPU and KAE availability. Compare baseline throughput, CPU cycles, latency, and error rate before and after enablement. |
| KUAF Kunpeng Unified Acceleration Framework | KUAF | Existing or planned hardware acceleration stack, multiple acceleration engines, scheduler or framework integration requirement | Hardware acceleration scheduling framework | Treat as an architecture-level opportunity. Do not recommend as a simple library swap without integration evidence. |
| KZL compression | zstd | `libzstd.so`, `ZSTD_*`, file formats or DB/table codecs using zstd | Optimized zstd patch repository for Kunpeng | Benchmark representative compression levels, decompression ratio, CPU cycles, and tail latency. |
| KZL compression | snappy | `libsnappy.so`, `snappy::`, block compression in DB or big data storage | Optimized snappy patch repository for Kunpeng | Validate on real block sizes used by the service. |
| KZL compression | lz4 | `liblz4.so`, `LZ4_*`, streaming or block compression paths | Optimized lz4 patch repository for Kunpeng | Benchmark compression and decompression separately. |
| KZL compression | zlib | `libz.so`, `deflate`, `inflate`, gzip, HTTP compression, storage compression | Optimized zlib patch repository and possible KAE path depending on workload | Distinguish software optimized zlib from KAE hardware acceleration. |
| KSL system library | kpglibc | Hot `memcpy`, `memmove`, `memcmp`, `memset`, `strlen`, `strcmp`, time functions, glibc-heavy profiles | Kunpeng optimized glibc related implementation, especially SVE optimized paths for suitable Kunpeng CPUs | This is high blast radius. Validate in staging with ABI, OS, and rollback plan. |
| KSL system library | protobuf | `libprotobuf.so`, `google::protobuf`, `ParseFrom*`, `SerializeTo*`, arena allocation, RPC serialization hotspots | Kunpeng optimized protobuf patch repository | Confirm version compatibility with the service framework. Benchmark parse and serialize under representative payloads. |
| KSL system library | sonic-cpp | JSON parsing or serialization hotspots, current use of JSON libraries that can be migrated | Optimized JSON library candidate | Recommend only if API migration is realistic and JSON is material in perf data. |
| KSL system library | KQMalloc | `malloc`, `free`, allocator locks, high allocation rate, page faults, RSS pressure, `libc` allocator only, no jemalloc or tcmalloc already loaded | Kunpeng memory allocator for single-threaded and multi-threaded scenarios, usable through `LD_PRELOAD` or link flags | Only for Kunpeng CPUs. Validate with workload time, average RSS, max RSS, latency, and allocator-sensitive correctness tests. |
| KSL migration | AVX2KI | x86 AVX intrinsic code, porting from x86 to Kunpeng, source symbols or build files mentioning AVX/AVX2 intrinsics | Migration library for AVX intrinsic code to Kunpeng instruction sets | This is a source-porting opportunity, not a runtime library detection. |
| KSAL storage | ISA-L | `libisal`, CRC, erasure coding, RAID, storage checksum, compression or data protection hotspots | Kunpeng optimized storage algorithm library using NEON or SVE oriented optimization | Validate checksum and erasure coding correctness before performance. |
| KSAL storage | KAE enabled SPDK | `spdk`, BDEV compression, BDEV crypto, storage service using SPDK | Enable compression and crypto in SPDK BDEV paths | Requires SPDK configuration and device path review. |

## Documentation-Only or Domain-Specific Leads

| Area | Candidate | Use when |
| --- | --- | --- |
| KMML media | HMPP | Image processing, color conversion, filtering, transforms, statistics, signal processing, or fixed precision vector operations dominate the workload. |
| KMML media | KVCL | Video encoding base operators or media codec pipelines dominate the workload. |
| KAIL AI | Kunpeng DNN library | DNN operator hotspots are visible and the service can use a Kunpeng AI operator library. |

## KQMalloc Details From BoostCore Docs

Known library files:

| Library | Meaning |
| --- | --- |
| `libkqmalloc.so` | Single-threaded dynamic library |
| `libkqmallocmt.so` | Multi-threaded dynamic library |
| `libkqmallocmt.debug.so` | Debug build with checks such as assertions and double free checking |
| `libkqmallocmt.profiler.so` | Profiling build that writes memory analysis files under `/tmp/kqmalloc_<process>CPU<cpu_id>.txt` |

Documented environment variables include:

| Variable | Purpose |
| --- | --- |
| `KQMALLOC_ALIGNMENT` | Memory alignment in bytes |
| `KQMALLOC_C11_COMPLIANT_PROCESSES` | Process list that should use C11 compatible alignment |
| `KQMALLOC_SINGLE_THREADED` | Threading mode selection |
| `KQMALLOC_SLAB_CACHE_RATIO` | Maximum cached slab ratio |
| `KQMALLOC_LOCAL_CACHE_RATIO` | Thread local cache ratio |
| `KQMALLOC_USE_THP` | Transparent huge page usage |
| `KQMALLOC_NUMA_AWARE` | NUMA awareness mode |
| `KQMALLOC_TINY_THRESHOLD` | Tiny object size threshold |
| `KQMALLOC_PROFILER_SECONDS` | Memory profiler interval |
| `KQMALLOC_PROFILER_EXPONENT` | Memory profiler interval growth |
| `KQMALLOC_HEAP_CACHE_SIZE` | Maximum cached heap remainder size |
| `KQMALLOC_HEAP_CACHE_RATIO` | Maximum cached heap remainder ratio |
| `KQMALLOC_DIRTY_THRESHOLD` | Dirty page threshold per heap |

Example activation shape from the docs:

```bash
export LD_PRELOAD=/<path-to-KQMalloc>/build/<HIPxx>/lib/libkqmallocmt.so
```

Example link shape from the docs:

```bash
-L/<KQMalloc-path>/build/<HIPxx>/lib/ -lkqmallocmt -Wl,-rpath=/<KQMalloc-path>/build/<HIPxx>/lib/
```

## Matching Heuristics

- RPC service: inspect TLS, compression, protobuf or JSON serialization, allocator, memcpy, event-loop networking, and system call profiles.
- Database: inspect storage compression, checksums, allocator, memcpy, sorting or encoding operators, plugin libraries, and page cache or NUMA behavior.
- Big data suite: inspect native codec libraries, shuffle compression, RPC serialization, JNI native libraries, vectorized operators, storage checksum, and allocator behavior.
- A loaded library without hotspot evidence is an enablement lead, not a recommendation.
- A hotspot without a compatible activation path is a research item, not an immediate optimization.
