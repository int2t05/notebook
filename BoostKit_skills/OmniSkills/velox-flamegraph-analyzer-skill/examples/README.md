# Examples

本目录包含 Velox 火焰图分析的示例文件，可直接在浏览器中打开 HTML 报告查看效果。

## 示例文件

### flamegraph_analysis_report_sample_aarch64.html

Gluten 1.3.0 + Velox 引擎在鲲鹏 aarch64 平台上的火焰图全链路瓶颈分析报告。

- **平台**: Kunpeng aarch64
- **引擎**: Gluten + Velox
- **分析工具**: `scripts/analyze.py`，使用 `--arch aarch64 --engine "Gluten + Velox"` 参数
- **报告内容**:
  - Java/C++(Velox)/Kernel CPU 占比总览
  - Java 侧瓶颈分析（Shuffle / CodeGen / GC 等）
  - C++/Velox 侧瓶颈分析（TableScan / HashJoin / HashAggregate / Expression / Shuffle 等）
  - 业务代码（Velox/Gluten）Top 30 热点帧 + 模块分类
  - ARM/aarch64 平台专属优化建议（NEON 覆盖缺口、哈希延迟、RLE 解码、SIMD memcpy、互斥锁争用等）
  - 可点击的火焰图链接（需配合原始火焰图 HTML 文件）

### deep_analysis_data_sample.json

对同一批火焰图文件做深度网络/内核/ORC 写入分析后输出的 JSON 数据，包含：

- 网络/内核/Shuffle/ORC 写入/Executor 等维度的 Top 热点帧
- 按文件维度统计的各维度 CPU 占比
- 识别符合"listing task"模式的火焰图候选文件

### deep_flamegraph_analysis_sample.py

独立深度分析脚本，聚焦网络传输、内核调用、ORC 写入和 Shuffle 等特定维度的瓶颈挖掘。本脚本不在 `scripts/analyze.py` 的主流程中，可作为补充分析工具单独使用。

## 如何复现

```bash
python scripts/analyze.py \
  --input /path/to/flame_graph_htmls \
  --output ./reports \
  --arch aarch64 \
  --engine "Gluten + Velox" \
  --flame-rel-path archive/home/flame_graph/
```

打开 `./reports/flamegraph_analysis_report.html` 即可查看与本示例相同风格的报告。