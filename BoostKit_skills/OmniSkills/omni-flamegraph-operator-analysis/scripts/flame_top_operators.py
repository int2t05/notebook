"""
flame_top_operators.py — Step 1 of omni-flamegraph-operator-analysis

Scans async-profiler HTML flame graphs, auto-discovers top-N operators
(frames matching OmniOperator naming conventions) and outputs a CSV.

Matched % computation replicates the async-profiler browser Search behavior,
borrowing the cpool+unpack+f/u/n parser from flamegraph_batch_search.py.

Usage:
    python flame_top_operators.py --dir PATH --out CSV [--top N] [--min-pct F]

Output columns:
    file, query, rank, operator, matched_pct
"""

import re
import sys
import csv
import argparse
from pathlib import Path
from collections import defaultdict


# ── Parser (same logic as flamegraph_batch_search.py) ────────────────────────

def _extract_cpool(html: str):
    m = re.search(r"const cpool = \[(.*?)\];\s*unpack\(cpool\)", html, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    raw = []
    for mo in re.finditer(r"'((?:[^'\\]|\\.)*)'", block):
        s = mo.group(1).replace("\\'", "'").replace("\\\\", "\\")
        raw.append(s)
    if not raw:
        return None
    cpool = [raw[0]]
    for i in range(1, len(raw)):
        first = raw[i]
        if not first:
            cpool.append(cpool[-1])
            continue
        prefix_len = ord(first[0]) - 32
        prev = cpool[i - 1]
        if prefix_len <= 0:
            decoded = first[1:]
        else:
            decoded = prev[:prefix_len] + first[1:]
        cpool.append(decoded)
    return cpool


def _simulate_fun(html: str, cpool: list):
    """Simulate f/u/n frame calls; returns (levels, root_width)."""
    pos = html.find("unpack(cpool);")
    if pos == -1:
        return None, None
    data_section = html[pos:]

    re_f = re.compile(r"^f\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?")
    re_u = re.compile(r"u\((\d+)(?:,\s*(\d+))?")
    re_n = re.compile(r"n\((\d+)(?:,\s*(\d+))?")

    levels = [[] for _ in range(256)]
    level0 = 0
    left0 = 0
    width0 = 0

    for line in data_section.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("f("):
            mo = re_f.match(line)
            if mo:
                key, level, left_delta = int(mo.group(1)), int(mo.group(2)), int(mo.group(3))
                w_arg = mo.group(4)
                level0 = level
                while level0 >= len(levels):
                    levels.append([])
                left0 += left_delta
                prev_w = width0
                if w_arg is None:
                    frame_w = prev_w
                else:
                    wi = int(w_arg)
                    frame_w = prev_w if wi == 0 else wi
                width0 = frame_w
                idx = key >> 3
                if idx < len(cpool):
                    levels[level0].append({"left": left0, "width": width0, "title": cpool[idx]})
        elif line.startswith("u("):
            mo = re_u.search(line)
            if mo:
                key = int(mo.group(1))
                w = int(mo.group(2)) if mo.group(2) is not None else width0
                level0 += 1
                while level0 >= len(levels):
                    levels.append([])
                idx = key >> 3
                if idx < len(cpool):
                    levels[level0].append({"left": left0, "width": w, "title": cpool[idx]})
                width0 = w
        elif line.startswith("n("):
            mo = re_n.search(line)
            if mo:
                key = int(mo.group(1))
                w = int(mo.group(2)) if mo.group(2) is not None else width0
                left0 += width0
                width0 = w
                idx = key >> 3
                if idx < len(cpool):
                    levels[level0].append({"left": left0, "width": width0, "title": cpool[idx]})

    if levels[0]:
        root_width = levels[0][0]["width"]
    else:
        root_width = 0
    return levels, root_width


def _parse_flame_html(html_path: str):
    """Returns (levels, root_width) or (None, None)."""
    text = Path(html_path).read_text(encoding="utf-8", errors="replace")
    cpool = _extract_cpool(text)
    if cpool:
        return _simulate_fun(text, cpool)
    return None, None


def _matched_pct(levels, root_width: int, pattern: re.Pattern) -> float:
    """Replicate browser Search matched %, deduplicating by left position."""
    if not root_width or not levels:
        return 0.0
    marked_at_left = {}
    for frame_list in levels:
        for f in frame_list:
            if pattern.search(f["title"]):
                left = f["left"]
                if left not in marked_at_left:
                    marked_at_left[left] = f
    if not marked_at_left:
        return 0.0
    total = 0
    left_cursor = 0
    for x in sorted(marked_at_left.keys()):
        if x >= left_cursor:
            m = marked_at_left[x]
            total += m["width"]
            left_cursor = x + m["width"]
    return 100.0 * total / root_width


# ── Operator discovery ────────────────────────────────────────────────────────

# Extract OmniOperator physical operators from frame titles.
#
# Only frames under omniruntime::op:: are treated as operators, with Splitter::
# as an explicit whitelist because it is the native shuffle split operator.
# This excludes Spark/Gluten wrappers, readers, deserializers, and helper
# classes that can otherwise enclose or overlap the real C++ operator work.
_OP_EXTRACT_RE = re.compile(
    r'\bomniruntime::op::([A-Za-z_][A-Za-z0-9_]*(?:Operator))(?=::|[^A-Za-z0-9_:]|$)'
    r'|\b(Splitter)(?=::)'
)

def _canonical_operator_name(raw_name: str) -> str | None:
    name = raw_name
    if not name or not name[0].isupper():
        return None

    # Expr wrappers are the same physical operator for bottleneck attribution.
    name = name.replace('HashAggregationWithExprOperator', 'HashAggregationOperator')
    name = name.replace('AggregationWithExprOperator', 'HashAggregationOperator')
    name = name.replace('LookupJoinWithExprOperator', 'LookupJoinOperator')
    return name


def _extract_operator_names(title: str) -> list[tuple[str, str]]:
    names = []
    for m in _OP_EXTRACT_RE.finditer(title):
        raw = m.group(1) or m.group(2)
        canonical = _canonical_operator_name(raw)
        if canonical:
            raw_pattern = f'omniruntime::op::{raw}' if m.group(1) else f'{raw}::'
            names.append((canonical, raw_pattern))
    return names


def discover_operators(levels, root_width: int) -> dict[str, float]:
    """For each discovered operator, compute matched % using the proper dedup algorithm."""
    # First collect canonical operator names and all raw spellings that map to them.
    op_names: dict[str, set[str]] = defaultdict(set)
    for frame_list in levels:
        for f in frame_list:
            for canonical, raw in _extract_operator_names(f["title"]):
                op_names[canonical].add(raw)

    # Then compute matched % for each operator pattern
    results = {}
    for op, raw_names in op_names.items():
        pat = re.compile('|'.join(re.escape(name) for name in sorted(raw_names, key=len, reverse=True)))
        pct = _matched_pct(levels, root_width, pat)
        if pct > 0:
            results[op] = pct
    return results


# ── Query name from file path ─────────────────────────────────────────────────

def _query_from_path(p: Path) -> str:
    stem = p.stem
    m = re.search(r'(q\d+[a-z]?)', stem, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return stem


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Extract top operators from async-profiler flame graph HTMLs')
    parser.add_argument('--dir', required=True, help='Directory containing .html flame graphs')
    parser.add_argument('--out', required=True, help='Output CSV path')
    parser.add_argument('--top', type=int, default=5, help='Top N operators per file (default 5)')
    parser.add_argument('--min-pct', type=float, default=0.3,
                        help='Minimum matched %% to include (default 0.3)')
    args = parser.parse_args()

    html_files = sorted(Path(args.dir).rglob('*.html'))
    if not html_files:
        print(f'[WARN] No .html files found under {args.dir}', file=sys.stderr)
        sys.exit(1)

    rows = []
    for html_path in html_files:
        query = _query_from_path(html_path)
        print(f'Processing {html_path.name} (query={query}) ...', file=sys.stderr)

        levels, root_width = _parse_flame_html(str(html_path))
        if levels is None or root_width == 0:
            print(f'  [WARN] Could not parse {html_path.name}', file=sys.stderr)
            continue

        print(f'  Parsed OK: root_width={root_width}, levels={len([l for l in levels if l])}',
              file=sys.stderr)

        op_pcts = discover_operators(levels, root_width)
        if not op_pcts:
            print(f'  [WARN] No operators discovered in {html_path.name}', file=sys.stderr)
            continue

        top_ops = sorted(op_pcts.items(), key=lambda x: -x[1])[:args.top]
        for rank, (op, pct) in enumerate(top_ops, 1):
            if pct < args.min_pct:
                break
            rows.append({
                'file': html_path.name,
                'query': query,
                'rank': rank,
                'operator': op,
                'matched_pct': round(pct, 4),
            })
            print(f'  #{rank} {op}: {pct:.2f}%', file=sys.stderr)

    if not rows:
        print('[ERROR] No results produced.', file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'query', 'rank', 'operator', 'matched_pct'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'\n[OK] Wrote {len(rows)} rows to {out_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
