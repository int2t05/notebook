# -*- coding: utf-8 -*-
"""Starting-point example for authoring STRUCTURAL diagrams as neat SVG.

Copy this next to scripts/svglib.py (or add scripts/ to sys.path), adapt the
two example functions to your feature, and write the .svg files into your doc's
images/ folder. Then run scripts/render_diagrams.py <images_dir> to get PNGs.

Two patterns shown:
  layered_arch()  -> stacked layer bands with arrows (architecture / 分层结构)
  before_after()  -> grid of object cells, default vs optimized (内存布局对比)
These cover the most common structural figures; compose freely for others
(component swimlanes, memory layout bars, dataflow boxes, dimension stacks).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from svglib import Canvas, INK, SUB, LINE, NEUTRAL, GRAY, YELLOW, BLUE, GREEN, ORANGE

OUT = os.environ.get("IMAGES_DIR", "./images")
os.makedirs(OUT, exist_ok=True)

def layered_arch():
    c = Canvas(820, 360, "图X 分层架构示例")
    cx = 410
    bands = [("上层(无锁快路径)", BLUE), ("中层(加锁补给)", GREEN), ("底层(全局资源)", ORANGE)]
    y = 60
    for i, (t, col) in enumerate(bands):
        c.rect(40, y, 740, 70, fill=col[0], stroke=col[1], rx=10, sw=1.8)
        c.text(60, y + 40, t, size=15, anchor="start", bold=True)
        if i < len(bands) - 1:
            c.arrow(cx, y + 70, cx, y + 100)
            c.text(cx + 12, y + 92, f"① 命中失败下沉到第 {i+2} 层", size=11, anchor="start", fill=SUB)
        y += 100
    c.save(os.path.join(OUT, "example_layered.svg"))
    print("wrote example_layered.svg")

def before_after():
    c = Canvas(900, 230, "图X 默认 vs 优化 内存布局对比")
    c.text(60, 70, "默认", size=13, anchor="start", bold=True)
    c.cells(60, 80, 38, 32, [("o0", YELLOW)] + [("", YELLOW)] * 3 + [("…", ("#FFFFFF", "#BF9000"))])
    c.text(60, 140, "8 KB 容纳 N 个对象", size=11, anchor="start")
    c.arrow(360, 96, 415, 96); c.text(388, 88, "优化后", size=10, fill=SUB)
    c.cells(435, 80, 38, 32, [("o0", YELLOW)] + [("", YELLOW)] * 8 + [("…", ("#FFFFFF", "#BF9000"))])
    c.text(435, 140, "8×8 KB(64 KB)容纳 8N 个对象", size=11, anchor="start")
    c.text(450, 200, "对象大小不变,单 span 容量 ×8 → 加锁频率降至约 1/8", size=12, fill=SUB)
    c.save(os.path.join(OUT, "example_before_after.svg"))
    print("wrote example_before_after.svg")

if __name__ == "__main__":
    layered_arch()
    before_after()
