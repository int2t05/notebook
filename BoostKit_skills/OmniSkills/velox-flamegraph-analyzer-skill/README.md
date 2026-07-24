# Velox Flame Graph Analyzer Skill

Velox 火焰图全链路瓶颈分析技能 —— 解析 async-profiler 火焰图 HTML 文件，自动识别 Java/C++(Velox)/Kernel 热点帧，映射到 Velox 业务代码模块，按功能域（Scan/Join/Aggregate/Shuffle 等）聚类生成结论，输出带可点击火焰图链接的交互式 HTML 报告，并针对 ARM/aarch64 平台提供专属优化建议。

## Skill 介绍

本技能面向 Velox 引擎的性能分析场景，从全量火焰图出发，跨语言层（Java/C++/Kernel）进行全局瓶颈归因与分级，帮助开发者快速定位 Velox 算子与表达式的性能瓶颈。

**适用场景：**
- 用户提供 async-profiler 火焰图 HTML 目录，要求 Velox 引擎瓶颈分析
- 用户在 ARM/Kunpeng/aarch64 平台上做 Velox 性能优化，需要平台级洞察
- 用户需要将火焰图热点与 Velox 源代码模块交叉对照
- 用户需要一份可直接分享的交互式 HTML 报告

## Features

- **Stream-parse** async-profiler flame graph HTML files (no DOM overhead, handles 1000+ files)
- **Classify** stack frames into Java, C++/native, kernel categories
- **Business code identification** via configurable keyword matching
- **ARM/aarch64 rule matching** — 6 built-in patterns (RLE decode, hash allocator, hash computation, hash table probe, JSON parsing, CollectList) with targeted optimization tips
- **Stratified sampling** — groups files by time batch for representative analysis
- **Interactive HTML report** — self-contained, clickable flame graph links, severity badges, ARM notes
- **Conclusions engine** — groups hotspots by functional area (Scan, Join, Aggregate, Shuffle, etc.) with severity ratings

## Quick Start

```bash
python scripts/analyze.py \
  --input /path/to/flame_graph_htmls \
  --output ./reports \
  --arch aarch64 \
  --engine "My Engine"
```

Open the generated `reports/flamegraph_analysis_report.html` in a browser.

## Installation for opencode

Copy this skill into your `.opencode/skills/` directory and register it in `opencode.json`:

```json
{
  "skills": {
    "velox-flamegraph-analyzer": {
      "path": ".opencode/skills/velox-flamegraph-analyzer-skill",
      "description": "Analyze async-profiler flame graph HTML files for Velox engine..."
    }
  }
}
```

Or use the skill directly by running the script:

```bash
python scripts/analyze.py --input ./flame_graphs --arch x86
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--input` | Yes | - | Directory with async-profiler HTML files |
| `--output` | No | `.` | Output directory |
| `--arch` | No | `aarch64` | Architecture: `x86`, `arm`, `aarch64` |
| `--engine` | No | `Gluten + Velox` | Engine name for report header |
| `--sample-size` | No | `60` | Number of files to sample |
| `--flame-rel-path` | No | `""` | Relative path for flame graph links |
| `--report-name` | No | `flamegraph_analysis_report.html` | Output filename |
| `--biz-keywords` | No | Gluten+Velox | Comma-separated business keywords |

## Custom Keywords

```bash
# Spark + ClickHouse
python scripts/analyze.py --input ./flames --biz-keywords "ClickHouse,CH,NativeExecutor"

# Pure Java application
python scripts/analyze.py --input ./flames --biz-keywords "com.myapp,MyService,MyDao"
```

## Requirements

- Python 3.6+ (no external dependencies)
- async-profiler flame graph HTML files (JFR conversion output)

## Examples

See `examples/` directory for sample analysis outputs:

- `flamegraph_analysis_report_sample_aarch64.html` — Gluten + Velox 在鲲鹏 aarch64 平台的全链路瓶颈分析报告（可直接在浏览器打开）
- `deep_analysis_data_sample.json` — 同一批火焰图的深度网络/内核/ORC 写入维度分析数据
- `deep_flamegraph_analysis_sample.py` — 独立深度分析脚本，聚焦网络传输、内核调用、ORC 写入等特定维度
- `README.md` — 示例文件说明与复现步骤

## License

Apache License 2.0