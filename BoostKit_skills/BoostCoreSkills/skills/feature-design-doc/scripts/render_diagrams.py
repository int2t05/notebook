#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render all diagram sources in an images directory to PNG.

Two source kinds are supported, matching the skill's diagram strategy:
  * *.puml  -> rendered via plantuml.jar  (behavioral: sequence/state/usecase/activity/timing)
  * *.svg   -> rendered via cairosvg       (structural: layered/component/memory-layout)

A CJK font is injected into PlantUML (skinparam defaultFontName) so Chinese text
renders instead of tofu boxes. SVG sources should set font-family themselves
(see svglib.py, which defaults to the same CJK font).

Usage:
  python render_diagrams.py <images_dir> [--jar /path/plantuml.jar] \
         [--font "WenQuanYi Micro Hei"] [--scale 2]

Output: <name>.png next to each <name>.puml / <name>.svg.
Run setup_env.sh first to install plantuml.jar, cairosvg and a CJK font.
"""
import argparse, glob, os, re, subprocess, sys

DEFAULT_FONT = "WenQuanYi Micro Hei"

def find_jar(cli):
    for p in (cli, os.environ.get("PLANTUML_JAR"),
              os.path.expanduser("~/.cache/plantuml/plantuml.jar"),
              "/tmp/plantuml.jar"):
        if p and os.path.exists(p):
            return p
    return None

def render_puml(path, outdir, jar, font):
    src = open(path, encoding="utf-8").read()
    if "defaultFontName" not in src:
        src = src.replace("@startuml", f'@startuml\nskinparam defaultFontName "{font}"', 1)
    tmp = path  # write back the font-injected version so the .puml stays reproducible
    open(tmp, "w", encoding="utf-8").write(src)
    r = subprocess.run(["java", "-jar", jar, "-tpng", "-charset", "UTF-8",
                        "-o", outdir, tmp], capture_output=True, text=True)
    png = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".png")
    if not os.path.exists(png):
        sys.exit(f"[puml] FAILED {path}\n{r.stderr[:800]}")
    return png

def render_svg(path, outdir, scale):
    import cairosvg
    png = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".png")
    # honor intrinsic width/height; scale up for a crisp raster in docx
    cairosvg.svg2png(url=path, write_to=png, scale=scale, background_color="white")
    return png

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images_dir")
    ap.add_argument("--jar", default=None)
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--scale", type=float, default=2.0)
    a = ap.parse_args()
    # PlantUML interprets a relative -o against each input file's directory, not
    # the cwd; use an absolute output dir so PNGs land exactly where we expect.
    d = os.path.abspath(a.images_dir)
    pumls = sorted(glob.glob(os.path.join(d, "*.puml")))
    svgs = sorted(glob.glob(os.path.join(d, "*.svg")))
    if pumls:
        jar = find_jar(a.jar)
        if not jar:
            sys.exit("plantuml.jar not found; run setup_env.sh or pass --jar")
        for p in pumls:
            render_puml(p, d, jar, a.font); print("[puml] OK", os.path.basename(p))
    for s in svgs:
        render_svg(s, d, a.scale); print("[svg ] OK", os.path.basename(s))
    print(f"rendered {len(pumls)} puml + {len(svgs)} svg -> PNG in {d}")

if __name__ == "__main__":
    main()
