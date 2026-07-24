#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flame Graph Analyzer — Generic, parameterized tool for analyzing async-profiler
flame graph HTML files, identifying Java/C++/kernel bottlenecks, mapping to
business code modules, and generating an interactive HTML summary report.

Usage:
  python analyze.py \
    --input <flame_graph_dir> \
    --output <report_output_dir> \
    [--arch x86|arm|aarch64] \
    [--engine "Gluten 1.3.0 + Velox"] \
    [--sample-size 60] \
    [--flame-rel-path archive/home/flame_graph/] \
    [--report-name flamegraph_analysis_report.html] \
    [--biz-keywords velox,Gluten,substrait,...]
"""

import os, re, sys, math, argparse
from collections import defaultdict
from pathlib import Path

F_RE = re.compile(r"f\((\d+),(\d+),(\d+),(\d+),'([^']*)'")

def is_java(title):
    if not title or title in ('all', 'root'): return False
    if '/' in title and not title.startswith('/usr/') and not title.startswith('/lib') and not title.endswith('.so'):
        return True
    return any(title.startswith(p) for p in ('java.', 'javax.', 'sun.', 'jdk.', 'com.', 'org.'))

def is_cpp(title):
    if not title or title in ('all', 'root'): return False
    return (title.endswith('.so') or title.endswith('.o') or
            title.startswith('/usr/') or title.startswith('/lib') or
            ('::' in title and '(' in title) or
            title.startswith('VM::') or title.startswith('[vdso]') or title.startswith('[unknown]'))

def is_kernel(title):
    km = ['__do_softirq', '__schedule', 'schedule', 'sock_recvmsg', 'tcp_recvmsg',
          '__sys_recvmsg', '__sys_sendmsg', 'do_syscall_64', 'entry_SYSCALL_64',
          '_raw_spin_lock', 'mutex_lock', 'mutex_unlock', 'ep_wait', 'ep_poll',
          'futex_wait_queue_me', 'hrtimer_nanosleep', '__hrtimer_run_queues',
          'netif_receive_skb', '__netif_receive_skb_core', '__dev_queue_xmit',
          '__tcp_transmit_skb', 'tcp_sendmsg_locked', 'tcp_rcv_established',
          'lock_page_lruvec_irqsave', 'pthread_mutex_lock', 'pthread_mutex_unlock',
          'mlx5e_napi_poll', '__do_softirq']
    return any(k in title for k in km)

def is_jvm_runtime(title):
    return ('libjvm' in title or 'CodeCache' in title or
            'JVM_' in title or title.endswith('libjvm.so'))

def is_business_code(title, biz_keywords):
    tl = title.lower()
    return any(k.lower() in tl for k in biz_keywords)

def classify(title, biz_keywords):
    if is_kernel(title): return 'kernel'
    if is_java(title): return 'java'
    if is_cpp(title): return 'cpp'
    return 'other'

MODULE_MAP = {
    'scan':      ['scan', 'table_scan', 'parquet', 'dwio', 'reader', 'connector'],
    'join':      ['hash_join', 'join', 'merge_join'],
    'aggregate': ['aggregate', 'accum', 'hash_agg'],
    'expression': ['expression', 'expr', 'eval', 'evaluate'],
    'shuffle':   ['shuffle', 'splitter', 'writer', 'serializer'],
    'sort':      ['sort', 'order', 'orderby', 'topn'],
    'jni':       ['jni', 'java_', 'calljava'],
    'memory':    ['memory', 'alloc', 'mempool', 'buffer', 'arena'],
    'substrait': ['substrait'],
    'io':        ['dwio', 'connector', 'cache', 'filesystem', 's3', 'hdfs', 'gcs'],
}

def guess_module(title):
    tl = title.lower()
    for mod, kws in MODULE_MAP.items():
        if any(k in tl for k in kws): return mod
    return 'other'

ARM_RULES = {
    'RleDecoderV2': {
        'pattern': ['RleDecoderV2', 'nextDirect', 'readValue'],
        'arm_note': 'RLE/BIT_PACK decode lacks NEON vectorization on aarch64; ~60-70% of x86 throughput.',
        'arm_tip': 'Add NEON-optimized RLE decode paths. Consider -march=armv8.2-a+dotprod for integer batch ops.',
    },
    'HashStringAllocator': {
        'pattern': ['HashStringAllocator', 'allocateFromFreeLists', 'free', 'copyMultipart'],
        'arm_note': 'String allocator has many small malloc/free cycles; ARM cache hierarchy penalizes this more than x86.',
        'arm_tip': 'Switch to jemalloc with large pages. Pre-allocate string buffers in bulk.',
    },
    'hashBytes': {
        'pattern': ['hashBytes', 'Murmur3Hash', 'hashNotNullAt', 'hashOne'],
        'arm_note': 'Hash functions may not leverage ARM CRC32/crypto extensions.',
        'arm_tip': 'Compile with -march=armv8.2-a+crypto to use ARM CRC32 instructions in hash computation.',
    },
    'HashTableProbe': {
        'pattern': ['groupProbe', 'HashTable', 'storeRowPointer'],
        'arm_note': 'Hash table probe suffers from higher memory latency on ARM platforms.',
        'arm_tip': 'Use prefetch hints. Consider larger hash table initial allocation to reduce rehashing.',
    },
    'simdjson': {
        'pattern': ['simdjson', 'json_path', 'dom_parser'],
        'arm_note': 'simdjson arm64 backend is optimized but get_json_object path is still expensive.',
        'arm_tip': 'Cache JSON parsing results. Consider pre-processing JSON columns outside the query engine.',
    },
    'GetJsonObject': {
        'pattern': ['GetJsonObject', 'get_json_object'],
        'arm_note': 'get_json_object is a scalar UDF calling simdjson per-row; no vectorization possible.',
        'arm_tip': 'Replace with native Velox UDF using batch JSON extraction. Cache repeated path evaluations.',
    },
    'CollectList': {
        'pattern': ['CollectList', 'deserializeToValueList', 'ValueList', 'UnsafeRowFastDeserializer'],
        'arm_note': 'CollectList aggregation deserializes per-row UnsafeRow data; heavy on ARM due to string copy overhead.',
        'arm_tip': 'Optimize UnsafeRow deserialization with bulk memcpy. Consider specialized ARM string copy using NEON.',
    },
    'NEON_memcpy': {
        'pattern': ['fastCopy', 'simd::memcpy', 'splitBinaryType', 'VeloxHashShuffleWriter'],
        'arm_note': 'velox::simd::memcpy uses 16-byte NEON on ARM vs 32-byte AVX2 on x86; 50% less copy bandwidth per iteration.',
        'arm_tip': 'Replace velox::simd::memcpy with std::memcpy for sizes >64 bytes (glibc has optimized ARM NEON+LDP loops). Add SVE support if available.',
    },
    'MutexLock': {
        'pattern': ['pthread_mutex_lock', 'pthread_mutex_unlock', 'futex_wait'],
        'arm_note': 'ARM mutex uses ldxr/stxr exclusive access loops; ~2x latency vs x86 lock cmpxchg under contention.',
        'arm_tip': 'Reduce lock contention. Use lock-free data structures where possible. Consider adaptive spin mutex tuning.',
    },
}

def match_arm_rule(title):
    for name, rule in ARM_RULES.items():
        if any(p.lower() in title.lower() for p in rule['pattern']):
            return rule
    return None

JAVA_CONC_TEMPLATES = [
    ('Spark CodeGen (Janino)', ['janino', 'codegen', 'CodeGenerator'],
     'Janino compiler consuming significant CPU. In Gluten most compute is offloaded to native, but Janino still runs for fallback stages.',
     'Check if Gluten correctly offloaded the corresponding operators. If fallback is happening, check fallback logs. Ensure spark.gluten.enabled=true.'),
    ('Spark Network / Shuffle', ['network', 'Transport', 'shuffle', 'ShuffleWriter', 'block_transfer'],
     'Network transport and shuffle serialization/deserialization consuming significant CPU.',
     'Use Columnar Shuffle (Gluten built-in). Set spark.shuffle.manager=org.apache.spark.shuffle.sort.ColumnarShuffleManager. Consider Celeborn/Uniffle remote shuffle.'),
    ('JVM GC Overhead', ['GC', 'Garbage', 'gc_pause'],
     'Garbage collection consuming CPU time.',
     'Increase offHeap memory (spark.memory.offHeap.size). Reduce JVM heap object allocations.'),
    ('Spark Task Scheduling', ['scheduler', 'dag', 'stage', 'TaskSetManager'],
     'Task scheduling overhead, typically fixed cost.',
     'If too high, reduce small tasks by tuning spark.sql.shuffle.partitions.'),
    ('ORC/Hive Write', ['LegacyDynamicIntArray', 'LegacyWriterImpl', 'HiveOutputWriter', 'HiveInspectors'],
     'ORC file writing and Hive serialization consuming CPU on the Java side.',
     'Consider using Parquet format instead of ORC for better native write support. Check if Velox backend can handle the write path natively.'),
]

CPP_CONC_TEMPLATES = [
    ('TableScan / DWRF/ORC I/O', ['scan', 'table_scan', 'Parquet', 'dwio', 'dwrf', 'reader', 'connector', 'RleDecoder', 'StringColumnRead'],
     'Data reading and decoding consuming major CPU. On ARM (aarch64), DWRF/ORC RLE decode may lack NEON SIMD optimization.',
     'Enable column pruning and predicate pushdown. Consider NEON-optimized decode on ARM. Check data locality.'),
    ('HashJoin', ['hash_join', 'HashJoin', 'merge_join', 'MergeJoin', 'groupProbe', 'HashTable'],
     'Hash Join build & probe are CPU-intensive. ARM hash table performance may suffer from memory access latency.',
     'Set spark.gluten.sql.columnar.forceShuffledHashJoin=true. Use broadcast join for small build side. Compile with -march=armv8.2-a+crypto.'),
    ('HashAggregate / CollectList', ['aggregate', 'Aggregate', 'hash_agg', 'HashAgg', 'accumulat', 'CollectList', 'deserializeToValueList', 'ValueList'],
     'Aggregation hash table and accumulator operations consuming CPU. CollectList deserialization is especially expensive on ARM.',
     'Check for unnecessary complex types. Tune spark.sql.shuffle.partitions. Optimize UnsafeRow deserialization for ARM.'),
    ('Expression / Function Evaluation', ['expression', 'Expression', 'expr', 'Expr', 'eval', 'Evaluate', 'function', 'peekable', 'GetJsonObject', 'simdjson'],
     'Expression evaluation (Project/Filter) function call overhead. Some functions (JSON parsing, string ops) lack NEON optimization on ARM.',
     'Identify specific slow functions and check for NEON/vectorized implementations. Replace scalar UDFs with batch implementations.'),
    ('Native Shuffle / Columnar Serialize', ['shuffle', 'Shuffle', 'VeloxHashShuffleWriter', 'splitBinary', 'splitter', 'Splitter', 'serializer'],
     'Native-side Columnar Shuffle data serialization/compression consuming CPU.',
     'Check shuffle compression codec config. Consider QAT/IAA acceleration on Kunpeng. Tune partition count.'),
    ('Sort / OrderBy', ['Sort', 'sort', 'OrderBy', 'orderBy', 'TopN'],
     'Sort operation CPU overhead.',
     'Reduce sorted data volume with filter pushdown. Tune spill config. Consider ARM-optimized sort kernels.'),
    ('Memory Management / Allocation', ['Memory', 'memory', 'MemoryPool', 'Alloc', 'alloc', 'HashStringAllocator', 'Buffer', 'arena'],
     'Memory allocation/deallocation overhead, possibly frequent small-object allocation. ARM cache hierarchy amplifies this.',
     'Enable jemalloc (spark.gluten.memory.offHeap.jemalloc.enabled). Use large pages for better TLB performance on ARM.'),
    ('JNI Boundary Calls', ['JNI', 'jni', 'Java_', 'callJava'],
     'Java-Native boundary call and data conversion overhead.',
     'Reduce JNI call frequency. Ensure batch data transfer not per-row. Check Arrow zero-copy usage.'),
]

def stream_extract(filepath):
    frames = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
        for line in fh:
            m = F_RE.match(line.strip())
            if m:
                frames.append({
                    'level': int(m.group(1)),
                    'left': int(m.group(2)),
                    'width': int(m.group(3)),
                    'title': m.group(5),
                })
    return frames

def build_hotspots(frames, biz_keywords):
    root_w = 0
    for fr in frames:
        if fr['level'] == 0 and fr['title'] == 'all':
            root_w = fr['width']; break
    if not root_w and frames:
        root_w = max(fr['width'] for fr in frames)

    lvl = defaultdict(list)
    for fr in frames:
        lvl[fr['level']].append(fr)

    hs = []
    for lv in sorted(lvl.keys()):
        for fr in lvl[lv]:
            cw = 0
            nxt = lv + 1
            if nxt in lvl:
                for ch in lvl[nxt]:
                    if ch['left'] >= fr['left'] and ch['left'] < fr['left'] + fr['width']:
                        cw += ch['width']
            sw = fr['width'] - cw
            sp = (sw / root_w * 100) if root_w else 0
            if sp >= 0.3:
                cat = classify(fr['title'], biz_keywords)
                isbiz = is_business_code(fr['title'], biz_keywords)
                hs.append((lv, fr['title'], sw, fr['width'], sp, cat, isbiz))
    return hs, root_w

def build_conclusions(java_top, biz_top, arch):
    def grp(top, kws):
        return [(t, p) for t, p in top if any(k.lower() in t.lower() for k in kws)]

    jconc = []
    for (name, kws, desc, tip) in JAVA_CONC_TEMPLATES:
        frames = grp(java_top, kws)
        if frames:
            s = sum(p for _, p in frames)
            sev = 'HIGH' if s > 10 else 'MEDIUM' if s > 3 else 'LOW'
            jconc.append((name, s, sev, desc, tip, frames[:8]))

    bconc = []
    for (name, kws, desc, tip) in CPP_CONC_TEMPLATES:
        frames = grp(biz_top, kws)
        if frames:
            s = sum(p for _, p in frames)
            sev = 'HIGH' if s > 20 else 'MEDIUM' if s > 5 else 'LOW'
            arm_notes = []
            for t, p in frames:
                rule = match_arm_rule(t)
                if rule and arch in ('arm', 'aarch64'):
                    arm_notes.append(f"[{t[:60]}] {rule['arm_note']}")
            if arm_notes:
                desc += '\nARM-specific: ' + '; '.join(arm_notes[:3])
                tip += '\nARM-specific: ' + '; '.join([rule['arm_tip'] for t, p in frames if (rule := match_arm_rule(t))][:3])
            bconc.append((name, s, sev, desc, tip, frames[:8]))

    return jconc, bconc

CSS = '''
body{font-family:"Segoe UI","Microsoft YaHei",sans-serif;margin:0;padding:20px;background:#f0f2f5;color:#333}
h1{color:#1a1a2e;text-align:center;font-size:28px;border-bottom:3px solid #e94560;padding-bottom:10px}
h2{color:#16213e;font-size:20px;margin-top:30px;border-left:4px solid #0f3460;padding-left:10px}
h3{color:#533483;font-size:16px}
.br{display:flex;gap:20px;margin:20px 0}
.bc{background:white;border-radius:8px;padding:15px 20px;box-shadow:0 2px 8px rgba(0,0,0,.1);flex:1;text-align:center}
.bc .lb{font-size:14px;color:#666}.bc .vl{font-size:28px;font-weight:bold}
.bc.j .vl{color:#e94560}.bc.c .vl{color:#0f3460}.bc.k .vl{color:#533483}.bc.v .vl{color:#1a936f}.bc.f .vl{color:#333}
.cb{background:white;border-radius:8px;padding:15px 20px;margin:10px 0;box-shadow:0 2px 8px rgba(0,0,0,.1)}
.cb.high{border-left:5px solid #e94560}.cb.medium{border-left:5px solid #f5a623}.cb.low{border-left:5px solid #1a936f}
.sev-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:bold}
.sev-badge.high{background:#e94560;color:white}.sev-badge.medium{background:#f5a623;color:white}.sev-badge.low{background:#1a936f;color:white}
.ht{width:100%;border-collapse:collapse;margin:10px 0}
.ht th{background:#16213e;color:white;padding:8px;text-align:left}
.ht td{padding:6px 8px;border-bottom:1px solid #ddd}.ht tr:hover{background:#f5f5f5}
.pct-bar{display:inline-block;height:14px;border-radius:2px}
.pct-bar.java{background:linear-gradient(90deg,#e94560,#ff6b8a)}.pct-bar.cpp{background:linear-gradient(90deg,#0f3460,#4a90d9)}
.pct-bar.velox{background:linear-gradient(90deg,#1a936f,#76c893)}.pct-bar.kernel{background:linear-gradient(90deg,#533483,#9b59b6)}
.flame-link{color:#0366d6;text-decoration:none}.flame-link:hover{text-decoration:underline}
.dv{height:1px;background:#ddd;margin:30px 0}
.cr{background:#f5f5f5;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:12px;max-width:600px;display:inline-block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bdg{display:inline-block;padding:2px 6px;border-radius:3px;font-size:11px}
.bdg.j{background:#ffebee;color:#e94560}.bdg.c{background:#e3f2fd;color:#0f3460}.bdg.v{background:#e8f5e9;color:#1a936f}.bdg.k{background:#f3e5f5;color:#533483}
.tip{background:#e8f5e9;padding:10px;border-radius:4px;margin-top:8px}
.arm-note{background:#fff3e0;padding:10px;border-radius:4px;margin-top:8px;border-left:3px solid #ff9800}
.gr{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:768px){.gr{grid-template-columns:1fr}.br{flex-wrap:wrap}}
'''

def sev_b(s):
    c = s.lower()
    return f'<span class="sev-badge {c}">{s}</span>'

def bar(pct, cls, scale=5, mw=100):
    w = min(pct * scale, mw)
    return f'<span class="pct-bar {cls}" style="width:{w}px"></span> {pct:.2f}%'

def flame_link(title, rep_cache, rel_path):
    if title in rep_cache:
        fn = rep_cache[title][0]
        return f'<a class="flame-link" href="{rel_path}{fn}" target="_blank">Open Flame Graph</a>'
    return ''

def biz_tag(title, biz_keywords):
    if is_business_code(title, biz_keywords): return '<span class="bdg v">Business</span>'
    return '<span class="bdg c">Runtime</span>'

def generate_html(data, jconc, bconc, arch, engine_name, sample_count, total_count, rel_path, biz_keywords):
    rep_cache = data['rep_cache']
    java_top = data['java_top']
    cpp_top = data['cpp_top']
    kernel_top = data['kernel_top']
    biz_top = data['biz_top']
    java_dom = data['java_dom']
    cpp_dom = data['cpp_dom']
    jt = data['java_total']
    ct = data['cpp_total']
    kt = data['kernel_total']
    vt = data['biz_total']

    arch_label = {'x86': 'x86_64', 'arm': 'ARMv8', 'aarch64': 'Kunpeng aarch64'}.get(arch, arch)

    h = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Flame Graph Analysis Report</title><style>{CSS}</style></head><body>
<h1>Flame Graph Bottleneck Analysis Report</h1>
<p style="text-align:center;color:#666">Platform: {arch_label} | Engine: {engine_name} | Profiler: async-profiler | Sample: {sample_count}/{total_count} files</p>
<div class="br">
<div class="bc f"><div class="lb">Files Analyzed</div><div class="vl">{sample_count}/{total_count}</div></div>
<div class="bc j"><div class="lb">Java CPU%</div><div class="vl">{jt:.1f}%</div></div>
<div class="bc c"><div class="lb">C++ CPU%</div><div class="vl">{ct:.1f}%</div></div>
<div class="bc k"><div class="lb">Kernel CPU%</div><div class="vl">{kt:.1f}%</div></div>
<div class="bc v"><div class="lb">Business Code%</div><div class="vl">{vt:.1f}%</div></div>
</div>
'''

    h += '<div class="dv"></div><h2>Java Side Bottleneck Analysis</h2>\n'
    for (area, pct, sev, desc, tip, frames) in jconc:
        s = sev.lower()
        h += f'<div class="cb {s}">\n<h3>{area} {sev_b(sev)} <span style="float:right;font-size:14px;color:#666">{pct:.1f}%</span></h3>\n<p>{desc}</p>\n'
        h += '<table class="ht"><tr><th>Stack Frame</th><th>Self%</th><th>Flame Graph</th></tr>\n'
        for t, p in frames:
            h += f'<tr><td><span class="cr">{t}</span></td><td>{bar(p,"java")}</td><td>{flame_link(t,rep_cache,rel_path)}</td></tr>\n'
        h += f'</table>\n<div class="tip">{tip}</div>\n</div>\n'

    h += '<h3>Java Top 30 Hotspot Frames</h3>\n<table class="ht"><tr><th>#</th><th>Frame</th><th>Self%</th><th>Flame</th></tr>\n'
    for i, (t, p) in enumerate(java_top, 1):
        h += f'<tr><td>{i}</td><td><span class="cr">{t}</span></td><td>{bar(p,"java",3)}</td><td>{flame_link(t,rep_cache,rel_path)}</td></tr>\n'
    h += '</table>\n'

    h += '<div class="dv"></div><h2>C++ / Native Side Bottleneck Analysis</h2>\n'
    for (area, pct, sev, desc, tip, frames) in bconc:
        s = sev.lower()
        h += f'<div class="cb {s}">\n<h3>{area} {sev_b(sev)} <span style="float:right;font-size:14px;color:#666">{pct:.1f}%</span></h3>\n<p>{desc}</p>\n'
        if '\nARM-specific:' in desc:
            base_desc, arm_part = desc.split('\nARM-specific:', 1)
            h += f'<div class="arm-note"><strong>ARM-specific findings:</strong> {arm_part}</div>\n'
        h += '<table class="ht"><tr><th>Stack Frame</th><th>Self%</th><th>Flame Graph</th><th>Type</th></tr>\n'
        for t, p in frames:
            rule = match_arm_rule(t)
            arm_extra = ''
            if rule and arch in ('arm', 'aarch64'):
                arm_extra = f' <span class="bdg k" title="{rule["arm_note"]}">ARM</span>'
            h += f'<tr><td><span class="cr">{t}</span>{arm_extra}</td><td>{bar(p,"cpp")}</td><td>{flame_link(t,rep_cache,rel_path)}</td><td>{biz_tag(t,biz_keywords)}</td></tr>\n'
        h += f'</table>\n<div class="tip">{tip}</div>\n</div>\n'

    h += '<h3>Business Code Top 30 (Non-runtime)</h3>\n<table class="ht"><tr><th>#</th><th>Frame</th><th>Self%</th><th>Flame</th><th>Module</th></tr>\n'
    for i, (t, p) in enumerate(biz_top, 1):
        rule = match_arm_rule(t)
        arm_extra = ''
        if rule and arch in ('arm', 'aarch64'):
            arm_extra = f' <span class="bdg k" title="{rule["arm_tip"]}">ARM tip</span>'
        h += f'<tr><td>{i}</td><td><span class="cr">{t}</span>{arm_extra}</td><td>{bar(p,"velox",3)}</td><td>{flame_link(t,rep_cache,rel_path)}</td><td>{guess_module(t)}</td></tr>\n'
    h += '</table>\n'

    h += '<h3>C++ All Top 30 Hotspot Frames</h3>\n<table class="ht"><tr><th>#</th><th>Frame</th><th>Self%</th><th>Flame</th><th>Type</th></tr>\n'
    for i, (t, p) in enumerate(cpp_top, 1):
        h += f'<tr><td>{i}</td><td><span class="cr">{t}</span></td><td>{bar(p,"cpp",3)}</td><td>{flame_link(t,rep_cache,rel_path)}</td><td>{biz_tag(t,biz_keywords)}</td></tr>\n'
    h += '</table>\n'

    h += '<div class="dv"></div><h2>Kernel Side Bottlenecks</h2>\n<table class="ht"><tr><th>#</th><th>Frame</th><th>Self%</th><th>Flame</th></tr>\n'
    for i, (t, p) in enumerate(kernel_top, 1):
        h += f'<tr><td>{i}</td><td><span class="cr">{t}</span></td><td>{bar(p,"kernel",3)}</td><td>{flame_link(t,rep_cache,rel_path)}</td></tr>\n'
    h += '</table>\n'

    h += '<div class="dv"></div><h2>Representative Flame Graph Files</h2>\n<div class="gr">\n'
    h += '<div><h3>Java Dominant (Top 10)</h3>\n<table class="ht"><tr><th>File</th><th>Java%</th><th>C++%</th><th>Biz%</th><th>Link</th></tr>\n'
    for f, c in java_dom:
        h += f'<tr><td><span class="cr">{f}</span></td><td>{c["j"]:.1f}%</td><td>{c["c"]:.1f}%</td><td>{c["v"]:.1f}%</td><td><a class="flame-link" href="{rel_path}{f}" target="_blank">Open</a></td></tr>\n'
    h += '</table></div>\n<div><h3>C++/Native Dominant (Top 10)</h3>\n<table class="ht"><tr><th>File</th><th>C++%</th><th>Biz%</th><th>Java%</th><th>Link</th></tr>\n'
    for f, c in cpp_dom:
        h += f'<tr><td><span class="cr">{f}</span></td><td>{c["c"]:.1f}%</td><td>{c["v"]:.1f}%</td><td>{c["j"]:.1f}%</td><td><a class="flame-link" href="{rel_path}{f}" target="_blank">Open</a></td></tr>\n'
    h += '</table></div></div>\n'

    all_conc = sorted(jconc + bconc, key=lambda c: c[1], reverse=True)
    h += '<div class="dv"></div><h2>Overall Bottleneck Summary</h2>\n'
    h += '<div class="cb high"><h3>Key Bottlenecks (Ranked)</h3>\n<table class="ht"><tr><th>Area</th><th>Ratio</th><th>Severity</th><th>Cause</th><th>Recommendation</th></tr>\n'
    for (area, pct, sev, desc, tip, frames) in all_conc:
        h += f'<tr><td>{sev_b(sev)} {area}</td><td>{pct:.1f}%</td><td>{sev}</td><td>{desc[:80]}</td><td>{tip[:80]}</td></tr>\n'
    h += '</table></div>\n'

    if arch in ('arm', 'aarch64'):
        h += '''<div class="cb medium">
<h3>ARM / aarch64 Platform Specific Notes</h3>
<ul>
<li><strong>NEON Coverage Gap</strong>: Many x86 SIMD (AVX/SSE) optimizations in native engine lack aarch64 NEON equivalents; string processing and float arithmetic show significant performance gaps.</li>
<li><strong>Hash Table Latency</strong>: HashJoin/HashAggregate hash tables use same 64B cache line size as x86, but ARM memory access latency differences cause hash probe performance degradation.</li>
<li><strong>DWRF/ORC Decode</strong>: RLE/BIT_PACK encoding lacks NEON optimization on ARM; decode speed is ~60-70% of x86 equivalent.</li>
<li><strong>Compile Flags</strong>: Recommended: <code>-march=armv8.2-a+crypto+dotprod</code> for Kunpeng-specific instructions (CRC32, AES, dot-product for hash and matrix ops).</li>
<li><strong>Memory Allocator</strong>: Consider jemalloc with large page (2MB) support on ARM for better TLB performance and reduced page fault overhead.</li>
<li><strong>SIMD memcpy</strong>: velox::simd::memcpy uses 16B NEON on ARM vs 32B AVX2 on x86; consider std::memcpy for bulk copies or add SVE support.</li>
<li><strong>Mutex Contention</strong>: ARM ldxr/stxr exclusive monitor has ~2x latency vs x86 LOCK prefix under contention; reduce lock scope or use lock-free structures.</li>
</ul>
</div>\n'''

    h += '<p style="text-align:center;color:#999;margin-top:40px">Generated by Flame Graph Analyzer Skill</p>\n</body></html>'
    return h

DEFAULT_BIZ_KEYWORDS = [
    'velox', 'Gluten', 'substrait', 'Columnar', 'columnar', 'Arrow', 'arrow',
    'JNI', 'jni', 'shuffle', 'Shuffle', 'Parquet', 'parquet', 'dwio', 'dwrf',
    'HashJoin', 'hash_join', 'Project', 'project', 'Filter', 'filter',
    'Aggregate', 'aggregate', 'Sort', 'sort', 'Exchange', 'exchange',
    'TableScan', 'table_scan', 'ValueStream', 'ExpressionEval', 'expression',
    'HashAggregation', 'OrderBy', 'TopN', 'Operator', 'operator', 'Task', 'task',
    'Driver', 'driver', 'MemoryPool', 'memory', 'exec', 'Exec', 'connectors',
    'simdjson', 'GetJsonObject', 'Murmur3Hash', 'UnsafeRowFastDeserializer',
    'CollectList', 'ValueList', 'HashStringAllocator',
]

def main():
    parser = argparse.ArgumentParser(description='Flame Graph Bottleneck Analyzer')
    parser.add_argument('--input', required=True, help='Directory containing async-profiler flame graph HTML files')
    parser.add_argument('--output', default='.', help='Output directory for the HTML report')
    parser.add_argument('--arch', default='aarch64', choices=['x86', 'arm', 'aarch64'], help='Target architecture')
    parser.add_argument('--engine', default='Gluten + Velox', help='Engine name for report header')
    parser.add_argument('--sample-size', type=int, default=60, help='Number of files to sample for analysis')
    parser.add_argument('--flame-rel-path', default='', help='Relative path prefix for flame graph links in report')
    parser.add_argument('--report-name', default='flamegraph_analysis_report.html', help='Output report filename')
    parser.add_argument('--biz-keywords', default=None, help='Comma-separated business code keywords (default: Gluten+Velox set)')
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    biz_keywords = args.biz_keywords.split(',') if args.biz_keywords else DEFAULT_BIZ_KEYWORDS

    if not input_dir.exists():
        print(f"Error: input directory does not exist: {input_dir}")
        sys.exit(1)

    all_files = sorted(input_dir.glob('*.html'))
    if not all_files:
        print(f"Error: no HTML files found in {input_dir}")
        sys.exit(1)
    total = len(all_files)
    print(f"Found {total} flame graph files in {input_dir}")

    batches = defaultdict(list)
    for f in all_files:
        parts = f.name.split('_')
        if len(parts) >= 2:
            ts = parts[0].lstrip('$')
            batch_key = ts.split('-')[1][:4] if '-' in ts else 'unknown'
            batches[batch_key].append(f)
        else:
            batches['unknown'].append(f)

    sample = []
    for bk, files in sorted(batches.items()):
        n = max(2, int(args.sample_size / len(batches)))
        n = min(n, len(files))
        sample.extend(files[:n])
    remaining = [f for f in all_files if f not in sample]
    if len(sample) < args.sample_size and remaining:
        sample.extend(remaining[:args.sample_size - len(sample)])
    print(f"Sampling {len(sample)} files from {len(batches)} time batches")

    java_hs = defaultdict(float)
    cpp_hs = defaultdict(float)
    kernel_hs = defaultdict(float)
    biz_hs = defaultdict(float)
    jt = ct = kt = vt = 0.0
    file_info = {}
    rep_cache = {}

    for fp in sample:
        frames = stream_extract(fp)
        if not frames: continue
        hs, rw = build_hotspots(frames, biz_keywords)
        if rw == 0: continue

        fj = fc = fk = fvel = 0.0
        for (lv, title, sw, tw, sp, cat, isbiz) in hs:
            if cat == 'java': java_hs[title] += sp; fj += sp; jt += sp
            elif cat == 'cpp': cpp_hs[title] += sp; fc += sp; ct += sp
            if isbiz: biz_hs[title] += sp; fvel += sp; vt += sp
            elif cat == 'kernel': kernel_hs[title] += sp; fk += sp; kt += sp
            if title not in rep_cache or sp > rep_cache[title][1]:
                rep_cache[title] = (fp.name, sp)

        file_info[fp.name] = {'j': fj, 'c': fc, 'k': fk, 'v': fvel, 'rw': rw}

    print(f"Java%={jt:.1f}  C++%={ct:.1f}  Kernel%={kt:.1f}  BizCode%={vt:.1f}")

    java_top = sorted(java_hs.items(), key=lambda x: x[1], reverse=True)[:30]
    cpp_top = sorted(cpp_hs.items(), key=lambda x: x[1], reverse=True)[:30]
    kernel_top = sorted(kernel_hs.items(), key=lambda x: x[1], reverse=True)[:20]
    biz_top = sorted(biz_hs.items(), key=lambda x: x[1], reverse=True)[:30]

    java_dom = sorted([(f, c) for f, c in file_info.items() if c['j'] > c['c'] and c['j'] > 5],
                      key=lambda x: x[1]['j'], reverse=True)[:10]
    cpp_dom = sorted([(f, c) for f, c in file_info.items() if c['c'] > c['j'] and c['c'] > 5],
                     key=lambda x: x[1]['c'], reverse=True)[:10]

    jconc, bconc = build_conclusions(java_top, biz_top, args.arch)

    data = {
        'java_top': java_top, 'cpp_top': cpp_top, 'kernel_top': kernel_top,
        'biz_top': biz_top, 'java_dom': java_dom, 'cpp_dom': cpp_dom,
        'java_total': jt, 'cpp_total': ct, 'kernel_total': kt, 'biz_total': vt,
        'rep_cache': rep_cache,
    }

    html = generate_html(data, jconc, bconc, args.arch, args.engine,
                         len(sample), total, args.flame_rel_path, biz_keywords)

    outfile = output_dir / args.report_name
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report saved: {outfile}")

    print("\n=== Java Top 10 ===")
    for t, p in java_top[:10]: print(f"  {p:.2f}%  {t}")
    print("\n=== C++ Top 10 ===")
    for t, p in cpp_top[:10]: print(f"  {p:.2f}%  {t}")
    print("\n=== Business Code Top 10 ===")
    for t, p in biz_top[:10]: print(f"  {p:.2f}%  {t}")

if __name__ == '__main__':
    main()