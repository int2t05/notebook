#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep analysis: find listingtask-related flame graphs,
extract kernel/network/shuffle frames, trace ARM perf gap root cause.
"""
import re, sys, json
from collections import defaultdict
from pathlib import Path

FLAME_DIR = Path(r"C:\Users\z00613209\Desktop\code\archive\home\flame_graph")
F_RE = re.compile(r"f\((\d+),(\d+),(\d+),(\d+),'([^']*)'")

# Network/shuffle/kernel related keywords
NET_KW = ['TransportClient', 'TransportClientFactory', 'BlockTransferService',
           'NettyRpcEnv', 'shuffle', 'Shuffle', 'fetch', 'Fetch', 'network',
           'Netty', 'netty', 'Channel', 'channel', 'Socket', 'socket',
           'Stream', 'stream', 'buffer', 'ChunkFetch', 'OneForOneBlockFetcher',
           'RetryingBlockFetcher', 'BlockFetchingListener', 'shuffleFetch',
           'SparkExecutor', 'Executor', 'TaskRunner', 'taskRunner',
           'listing', 'Listing', 'ORC', 'orc', 'HiveOutput', 'HiveWrite',
           'LegacyWriter', 'LegacyDynamicIntArray', 'HiveInspectors',
           'Serializer', 'Deserializer', 'KryoSerializer', 'Serialization']

KERNEL_KW = ['__do_softirq', '__schedule', 'schedule', 'sock_recvmsg',
             'tcp_recvmsg', '__sys_recvmsg', '__sys_sendmsg', 'do_syscall_64',
             'entry_SYSCALL_64', '_raw_spin_lock', 'mutex_lock', 'mutex_unlock',
             'ep_wait', 'ep_poll', 'futex_wait_queue_me', 'hrtimer_nanosleep',
             'netif_receive_skb', '__netif_receive_skb_core',
             'tcp_sendmsg', 'sock_sendmsg', '__tcp_transmit_skb',
             'tcp_ack', 'tcp_rcv_established', 'ip_queue_xmit',
             'dev_queue_xmit', '__dev_xmit_skb', 'napi_poll',
             'softirq', 'irq', 'interrupt', 'do_softirq',
             'schedule_timeout', 'wait_for_interruptible',
             'poll_schedule_timeout', 'do_select', '__do_select']

SHUFFLE_JAVA_KW = ['ShuffleMapTask', 'ShuffleWriter', 'BypassMergeSortShuffleWriter',
                    'UnsafeShuffleWriter', 'SortShuffleWriter', 'ShuffleBlockResolver',
                    'MapOutputTracker', 'MapOutputTrackerMaster', 'MapOutputTrackerWorker',
                    'shuffleClient', 'ExternalShuffleClient', 'NettyBlockTransferService',
                    'OneForOneBlockFetcher', 'RetryingBlockFetcher', 'BlockFetchResult']

JAVA_EXEC_KW = ['TaskRunner', 'Executor$TaskRunner', 'SparkExecutor', 'ExecutorBackend',
                'CoarseGrainedExecutorBackend', 'taskRunner', 'runTask',
                'TaskSchedulerImpl', 'TaskSetManager', 'DAGScheduler']

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

def build_hotspots_deep(frames, threshold=0.01):
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
            if sp >= threshold:
                hs.append({
                    'level': lv, 'title': fr['title'],
                    'self_width': sw, 'total_width': fr['width'],
                    'self_pct': sp, 'total_pct': (fr['width']/root_w*100) if root_w else 0,
                })
    return hs, root_w

def match_any(title, kw_list):
    tl = title.lower()
    return any(k.lower() in tl for k in kw_list)

def main():
    all_files = sorted(FLAME_DIR.glob('*.html'))
    print(f"Processing {len(all_files)} files with deep threshold (0.01%)...")

    # Per-file stats
    file_net_pct = {}   # file -> network-related self_pct
    file_kernel_pct = {}
    file_shuffle_pct = {}
    file_java_exec_pct = {}
    file_orc_write_pct = {}
    file_total_root = {}

    # Aggregate
    net_hs = defaultdict(float)
    kernel_hs = defaultdict(float)
    shuffle_java_hs = defaultdict(float)
    orc_write_hs = defaultdict(float)
    java_exec_hs = defaultdict(float)
    all_java_hs = defaultdict(float)

    # Track which files have high network/kernel content
    net_rich_files = []
    kernel_rich_files = []

    for fp in all_files:
        frames = stream_extract(fp)
        if not frames: continue
        hs, rw = build_hotspots_deep(frames, threshold=0.01)
        if rw == 0: continue

        fn = fp.name
        file_total_root[fn] = rw
        f_net = f_kernel = f_shuffle = f_orc = f_exec = 0.0

        for h in hs:
            t = h['title']
            sp = h['self_pct']
            all_java_hs[t] += sp

            if match_any(t, NET_KW):
                net_hs[t] += sp; f_net += sp
            if match_any(t, KERNEL_KW):
                kernel_hs[t] += sp; f_kernel += sp
            if match_any(t, SHUFFLE_JAVA_KW):
                shuffle_java_hs[t] += sp; f_shuffle += sp
            if match_any(t, ['ORC','orc','LegacyWriter','LegacyDynamicIntArray','HiveOutput','HiveInspectors','HiveWrite']):
                orc_write_hs[t] += sp; f_orc += sp
            if match_any(t, JAVA_EXEC_KW):
                java_exec_hs[t] += sp; f_exec += sp

        file_net_pct[fn] = f_net
        file_kernel_pct[fn] = f_kernel
        file_shuffle_pct[fn] = f_shuffle
        file_orc_write_pct[fn] = f_orc
        file_java_exec_pct[fn] = f_exec

        if f_net > 5: net_rich_files.append((fn, f_net, rw))
        if f_kernel > 3: kernel_rich_files.append((fn, f_kernel, rw))

    # Sort rich files
    net_rich_files.sort(key=lambda x: x[1], reverse=True)
    kernel_rich_files.sort(key=lambda x: x[1], reverse=True)

    print(f"\n=== Network-rich files (network self_pct > 5%) ===")
    for fn, pct, rw in net_rich_files[:20]:
        print(f"  {pct:.2f}%  {fn}  (root_width={rw})")

    print(f"\n=== Kernel-rich files (kernel self_pct > 3%) ===")
    for fn, pct, rw in kernel_rich_files[:20]:
        print(f"  {pct:.2f}%  {fn}  (root_width={rw})")

    print(f"\n=== Network Hotspot Frames (Top 30) ===")
    net_top = sorted(net_hs.items(), key=lambda x: x[1], reverse=True)[:30]
    for t, p in net_top:
        print(f"  {p:.2f}%  {t}")

    print(f"\n=== Kernel Hotspot Frames (Top 30) ===")
    kernel_top = sorted(kernel_hs.items(), key=lambda x: x[1], reverse=True)[:30]
    for t, p in kernel_top:
        print(f"  {p:.2f}%  {t}")

    print(f"\n=== Shuffle Java Frames (Top 20) ===")
    shuffle_top = sorted(shuffle_java_hs.items(), key=lambda x: x[1], reverse=True)[:20]
    for t, p in shuffle_top:
        print(f"  {p:.2f}%  {t}")

    print(f"\n=== ORC Write Frames (Top 20) ===")
    orc_top = sorted(orc_write_hs.items(), key=lambda x: x[1], reverse=True)[:20]
    for t, p in orc_top:
        print(f"  {p:.2f}%  {t}")

    print(f"\n=== Java Executor/Task Frames (Top 20) ===")
    exec_top = sorted(java_exec_hs.items(), key=lambda x: x[1], reverse=True)[:20]
    for t, p in exec_top:
        print(f"  {p:.2f}%  {t}")

    # Find "listingtask" signature: ORC write + network fetch + shuffle
    print(f"\n=== Files matching 'listing task' pattern (ORC_write > 3% AND net > 5%) ===")
    listing_candidates = []
    for fn in all_files:
        fn_str = fn.name
        orc_p = file_orc_write_pct.get(fn_str, 0)
        net_p = file_net_pct.get(fn_str, 0)
        exec_p = file_java_exec_pct.get(fn_str, 0)
        if orc_p > 1 and net_p > 1:
            listing_candidates.append((fn_str, orc_p, net_p, exec_p, file_total_root.get(fn_str,0)))
    listing_candidates.sort(key=lambda x: x[1]+x[2], reverse=True)
    for fn, orc, net, exec, rw in listing_candidates[:15]:
        print(f"  ORC={orc:.2f}%  Net={net:.2f}%  Exec={exec:.2f}%  root={rw}  {fn}")

    # Deep analysis of top listing candidate files
    print(f"\n=== Deep stack trace for top listing candidate ===")
    if listing_candidates:
        top_fn = listing_candidates[0][0]
        top_fp = FLAME_DIR / top_fn
        frames = stream_extract(top_fp)
        hs, rw = build_hotspots_deep(frames, threshold=0.05)
        print(f"  File: {top_fn}  root_width={rw}")
        print(f"  All frames with self_pct >= 0.05%:")
        for h in sorted(hs, key=lambda x: x['self_pct'], reverse=True)[:50]:
            print(f"    {h['self_pct']:.2f}%  L{h['level']}  {h['title']}")

    # Save analysis data as JSON for later HTML generation
    result = {
        'net_top': net_top,
        'kernel_top': sorted(kernel_hs.items(), key=lambda x: x[1], reverse=True)[:30],
        'shuffle_top': shuffle_top,
        'orc_top': orc_top,
        'exec_top': exec_top,
        'net_rich_files': net_rich_files[:15],
        'kernel_rich_files': kernel_rich_files[:15],
        'listing_candidates': listing_candidates[:15],
    }
    outfile = Path(r"C:\Users\z00613209\Desktop\code") / "deep_analysis_data.json"
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nData saved to {outfile}")

if __name__ == '__main__':
    main()