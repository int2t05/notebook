# -*- coding: utf-8 -*-
"""Minimal SVG builder for neat layered/structural diagrams (non-PlantUML).
Palette & grid style modeled after openeuler/compiler-docs sizeclasses_span.png."""
from xml.sax.saxutils import escape as _esc

FONT = "WenQuanYi Micro Hei"

# palette
INK      = "#1F2A37"
SUB      = "#5B6B7B"
LINE     = "#5A6675"
NEUTRAL  = ("#F2F3F5", "#8A93A0")   # fill, stroke
GRAY     = ("#E2E6EB", "#8A93A0")
YELLOW   = ("#FFE08A", "#BF9000")   # object cells
BLUE     = ("#DCEAF9", "#2E75B6")
GREEN    = ("#E2EFDA", "#538135")
ORANGE   = ("#FCE4D6", "#C55A11")
PURPLE   = ("#E6E0F0", "#7B5EA7")
BAND     = ("#EEF3FA", "#9DB4CE")

class Canvas:
    def __init__(self, w, h, title=None):
        self.w, self.h = w, h
        self.parts = []
        self.title = title

    def raw(self, s): self.parts.append(s)

    def rect(self, x, y, w, h, fill="#FFFFFF", stroke=INK, rx=8, sw=1.5, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def text(self, x, y, s, size=14, anchor="middle", fill=INK, bold=False, italic=False):
        w = ' font-weight="bold"' if bold else ""
        it = ' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'text-anchor="{anchor}"{w}{it} fill="{fill}">{_esc(str(s))}</text>')

    def lines(self, cx, y, rows, size=13, fill=INK, bold=False, anchor="middle", lh=None):
        lh = lh or (size + 5)
        for i, r in enumerate(rows):
            self.text(cx, y + i * lh, r, size=size, fill=fill, bold=bold, anchor=anchor)

    def boxlabel(self, x, y, w, h, rows, fill="#FFFFFF", stroke=INK, size=13,
                 rx=8, sw=1.5, tfill=INK, bold=False, dash=None):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=sw, dash=dash)
        if isinstance(rows, str): rows = [rows]
        total = len(rows) * (size + 4) - 4
        sy = y + h / 2 - total / 2 + size - 2
        self.lines(x + w / 2, sy, rows, size=size, fill=tfill, bold=bold)

    def arrow(self, x1, y1, x2, y2, color=LINE, sw=1.8, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#ah)"{d}/>')

    def plainline(self, x1, y1, x2, y2, color=LINE, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def cells(self, x, y, cw, ch, items, default_fill=YELLOW):
        """items: list of (label, fillpair) or label(str). draw a horizontal strip."""
        cx = x
        for it in items:
            if isinstance(it, tuple):
                label, fp = it
            else:
                label, fp = it, default_fill
            self.rect(cx, y, cw, ch, fill=fp[0], stroke=fp[1], rx=2, sw=1.2)
            self.text(cx + cw / 2, y + ch / 2 + 4, label, size=11)
            cx += cw
        return cx  # right edge

    def svg(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">')
        defs = ('<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                'orient="auto" markerUnits="strokeWidth">'
                f'<path d="M0,0 L8,3 L0,6 z" fill="{LINE}"/></marker>'
                '<marker id="ahd" markerWidth="12" markerHeight="12" refX="9" refY="3.5" '
                'orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0,0 L9,3.5 L0,7 z" fill="{LINE}"/></marker></defs>')
        bg = f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#FFFFFF"/>'
        t = ""
        if self.title:
            t = (f'<text x="{self.w/2}" y="28" font-family="{FONT}" font-size="17" '
                 f'text-anchor="middle" font-weight="bold" fill="{INK}">{_esc(self.title)}</text>')
        return head + defs + bg + t + "".join(self.parts) + "</svg>"

    def save(self, path):
        open(path, "w", encoding="utf-8").write(self.svg())
