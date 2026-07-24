#!/usr/bin/env bash
# Install the toolchain the feature-design-doc skill needs:
#   * python deps: cairosvg (SVG->PNG), python-docx (docx), pillow (image size)
#   * plantuml.jar (PlantUML -> PNG) into ~/.cache/plantuml/
#   * a CJK font that covers BOTH Latin and Chinese (WenQuanYi Micro Hei),
#     so diagrams don't render Chinese / punctuation as tofu boxes.
#
# Idempotent: skips anything already present. Safe to re-run.
set -u

echo "== python deps =="
python3 - <<'PY' 2>/dev/null || pip install --quiet cairosvg python-docx pillow
import cairosvg, docx, PIL  # noqa
print("python deps already present")
PY

echo "== plantuml.jar =="
JAR_DIR="$HOME/.cache/plantuml"; JAR="$JAR_DIR/plantuml.jar"
if [ ! -s "$JAR" ]; then
  mkdir -p "$JAR_DIR"
  VER="1.2024.7"
  URL="https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/${VER}/plantuml-${VER}.jar"
  echo "downloading $URL"
  curl -fsSL -o "$JAR" "$URL" && echo "plantuml.jar -> $JAR" || echo "WARN: plantuml.jar download failed; set PLANTUML_JAR manually"
else
  echo "plantuml.jar already present: $JAR"
fi
command -v java >/dev/null || echo "WARN: java not found; PlantUML rendering needs a JRE (e.g. dnf install java-11-openjdk-headless)"

echo "== CJK font (WenQuanYi Micro Hei) =="
if ! fc-list 2>/dev/null | grep -qi "WenQuanYi Micro Hei"; then
  mkdir -p "$HOME/.fonts"
  FURL="https://github.com/layerssss/wqy/raw/master/fonts/WenQuanYiMicroHei.ttf"
  curl -fsSL -o "$HOME/.fonts/WenQuanYiMicroHei.ttf" "$FURL" \
    && fc-cache -f "$HOME/.fonts" >/dev/null 2>&1 \
    && echo "WenQuanYi Micro Hei installed" \
    || echo "WARN: font download failed; install any Latin+CJK font and update svglib FONT / --font"
else
  echo "WenQuanYi Micro Hei already installed"
fi

echo "== done =="
echo "PLANTUML_JAR=$JAR (export this if render_diagrams.py can't find it)"
