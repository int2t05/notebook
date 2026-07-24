# Velox Flame Graph Analyzer Skill

Analyze async-profiler flame graph HTML files to identify Java/C++(Velox)/kernel bottlenecks, map hotspots to Velox business code modules, provide ARM/aarch64-specific optimization insights for the Velox engine, and generate an interactive HTML summary report with direct links to original flame graphs.

## When to Use

- User provides a directory of async-profiler flame graph HTML files and asks for bottleneck analysis
- User asks about performance optimization on ARM/Kunpeng/aarch64 platforms
- User wants a visual summary of flame graph findings with clickable links
- User needs to cross-reference flame graph hotspots with source code

## How to Invoke

```bash
python scripts/analyze.py \
  --input <path_to_flame_graph_html_directory> \
  --output <path_to_output_directory> \
  --arch aarch64 \
  --engine "Gluten 1.3.0 + Velox" \
  --flame-rel-path <relative_path_from_report_to_flamegraphs>
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--input` | Yes | - | Directory containing async-profiler flame graph HTML files |
| `--output` | No | `.` | Output directory for the HTML report |
| `--arch` | No | `aarch64` | Target architecture: `x86`, `arm`, or `aarch64` |
| `--engine` | No | `Gluten + Velox` | Engine name shown in report header |
| `--sample-size` | No | `60` | Number of files to sample for analysis (for large collections) |
| `--flame-rel-path` | No | `""` | Relative path prefix for flame graph links in the report |
| `--report-name` | No | `flamegraph_analysis_report.html` | Output report filename |
| `--biz-keywords` | No | Gluten+Velox set | Comma-separated keywords to identify business logic frames (vs runtime frames like libjvm.so) |

## What the Tool Does

1. **Samples** flame graph files from the input directory (stratified by time batch)
2. **Stream-parses** each HTML file, extracting `f()` call data from async-profiler JS
3. **Builds hotspots**: computes self-time percentage for each stack frame relative to root
4. **Classifies** frames into Java, C++/native, kernel, or other categories
5. **Identifies business code** using configurable keyword matching (default: Velox/Gluten)
6. **Matches ARM rules**: checks each business hotspot against known ARM performance patterns
7. **Builds conclusions** grouped by functional area (Scan/IO, Join, Aggregate, Expression, Shuffle, Sort, Memory, JNI) with severity ratings
8. **Generates HTML report** with:
   - Summary dashboard (Java%, C++%, Kernel%, Business Code%)
   - Java bottleneck analysis with per-area breakdown and optimization tips
   - C++/native bottleneck analysis with ARM-specific notes and tags
   - Business code top 30 hotspot table with module classification
   - Kernel bottleneck table
   - Representative flame graph file listings
   - Overall ranked bottleneck summary table
   - ARM/aarch64 platform-specific notes section (when arch=arm/aarch64)
   - Every hotspot row includes a direct link to open the corresponding flame graph

## ARM-Specific Analysis Rules

The tool recognizes these ARM/aarch64 performance patterns and provides targeted advice:

| Pattern | ARM Issue | Suggestion |
|---------|-----------|------------|
| `RleDecoderV2` | RLE/BIT_PACK lacks NEON vectorization | Add NEON decode paths; -march=armv8.2-a+dotprod |
| `HashStringAllocator` | Frequent small malloc/free penalized by ARM cache | Switch to jemalloc+large pages; pre-allocate in bulk |
| `hashBytes/Murmur3Hash` | Hash may not use ARM CRC32/crypto extensions | -march=armv8.2-a+crypto for CRC32 instructions |
| `HashTable/groupProbe` | Hash probe suffers higher ARM memory latency | Use prefetch hints; larger initial allocation |
| `simdjson/GetJsonObject` | get_json_object is scalar per-row; no vectorization | Cache JSON results; use batch Velox UDF |
| `CollectList/deserializeToValueList` | UnsafeRow deserialization heavy on ARM string copy | Optimize with bulk memcpy; NEON string copy |

## Custom Business Keywords

The default keyword set covers Gluten + Velox. For other engines, pass custom keywords:

```bash
# For Spark + ClickHouse backend
python scripts/analyze.py --input ./flames --biz-keywords "ClickHouse,CH,clickhouse,NativeExecutor"

# For Flink + Velox
python scripts/analyze.py --input ./flames --biz-keywords "velox,flink,Arrow,substrait"
```

## Output

A single HTML file (default: `flamegraph_analysis_report.html`) that can be opened in any browser. The report is self-contained (no external dependencies) and includes clickable links to open original flame graphs directly.

## After Generating the Report

- Tell the user the report file path
- Summarize the top 3-5 key findings in plain text
- Highlight the most critical ARM-specific bottleneck if arch=aarch64
- Mention that flame graph links in the report are clickable and open the original async-profiler interactive visualization