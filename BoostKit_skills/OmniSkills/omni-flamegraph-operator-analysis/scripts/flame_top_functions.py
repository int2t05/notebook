"""
flame_top_functions.py — Step 2 of omni-flamegraph-operator-analysis

For each top operator from result-operators.csv, finds the top-N hottest
functions that appear *inside* that operator's call subtree.

Algorithm:
  1. For each operator frame at level L, range [left, left+width]:
     collect all frames at level > L whose [left, left+width] is contained
     within the operator's range.
  2. Aggregate by short function name, sum widths.
  3. Normalize against operator's total width.

Usage:
    python flame_top_functions.py \
        --dir PATH \
        --operators-csv result-operators.csv \
        --out result-functions.csv \
        [--top N] [--min-pct F]

Output columns:
    file, query, operator, operator_pct, rank, function, function_pct
"""

import re
import sys
import csv
import argparse
from pathlib import Path
from collections import defaultdict


# ── Parser (identical to flame_top_operators.py) ─────────────────────────────

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
        decoded = (prev[:prefix_len] if prefix_len > 0 else '') + first[1:]
        cpool.append(decoded)
    return cpool


def _simulate_fun(html: str, cpool: list):
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
                wi = int(w_arg) if w_arg is not None else 0
                frame_w = width0 if wi == 0 else wi
                width0 = frame_w
                idx = key >> 3
                if idx < len(cpool):
                    levels[level0].append({"left": left0, "width": width0, "title": cpool[idx], "level": level0})
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
                    levels[level0].append({"left": left0, "width": w, "title": cpool[idx], "level": level0})
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
                    levels[level0].append({"left": left0, "width": width0, "title": cpool[idx], "level": level0})

    root_width = levels[0][0]["width"] if levels[0] else 0
    return levels, root_width


def _parse_flame_html(html_path: str):
    text = Path(html_path).read_text(encoding="utf-8", errors="replace")
    cpool = _extract_cpool(text)
    if cpool:
        return _simulate_fun(text, cpool)
    return None, None


# ── Function name cleaning ─────────────────────────────────────────────────────

_NOISE_RE = re.compile(
    r'^(?:all|idle|cpu_idle|pthread_|__libc_|_start|__start|clone'
    r'|libc\.so|libpthread|ld-linux|JavaThread|Interpreter|G1|GC'
    r'|CompileBroker|safepoint|JVM|jvm|JavaCalls)', re.IGNORECASE
)

_JVM_RE = re.compile(r'^(?:Ljava|org\.apache|scala\.|java\.)', re.IGNORECASE)


def _is_noise(title: str) -> bool:
    return bool(_NOISE_RE.search(title)) or bool(_JVM_RE.search(title))


def _short_name(title: str) -> str:
    """Extract a readable short name from a C++ symbol."""
    # Remove template parameters (simple greedy, handles nested <> imperfectly)
    s = re.sub(r'<[^<>]*>', '', title)
    s = re.sub(r'<[^<>]*>', '', s)  # second pass for nested templates
    # Take last 2 :: components
    parts = [p for p in s.split('::') if p]
    if len(parts) >= 2:
        return '::'.join(parts[-2:])
    elif len(parts) == 1:
        return parts[0]
    return s.strip()


# ── Operator pattern ──────────────────────────────────────────────────────────

_OP_ALIASES = {
    # Expr wrappers are the same physical operator for bottleneck attribution.
    'HashAggregationOperator': (
        'HashAggregationOperator',
        'HashAggregationWithExprOperator',
        'AggregationWithExprOperator',
    ),
    'LookupJoinOperator': ('LookupJoinOperator', 'LookupJoinWithExprOperator'),
}


def _operator_pattern(operator_name: str) -> re.Pattern:
    if operator_name == 'Splitter':
        return re.compile(r'\bSplitter::')

    names = _OP_ALIASES.get(operator_name, (operator_name,))
    patterns = [
        re.escape(f'omniruntime::op::{name}') + r'(?=::|[^A-Za-z0-9_:]|$)'
        for name in sorted(names, key=len, reverse=True)
    ]
    return re.compile('|'.join(patterns))


def _is_operator_frame(title: str, operator_pattern: re.Pattern) -> bool:
    return bool(operator_pattern.search(title))


# ── Main analysis: find functions inside operator subtree ─────────────────────

def top_functions_in_operator(levels: list, root_width: int,
                               operator_name: str, top_n: int,
                               min_pct: float) -> list[tuple[str, float]]:
    """
    Find top-N hottest functions within the operator's call subtree.

    For each operator frame at level L with range [left, left+width],
    collect all frames at level > L that fall inside this range.
    Aggregate by short_name, dedup by left position (same as matched_pct algorithm).
    Normalize against operator's total sampled width.
    """
    # Collect all operator frame ranges
    operator_pattern = _operator_pattern(operator_name)
    op_ranges = []  # list of (level, left, left+width)
    for frame_list in levels:
        for f in frame_list:
            if _is_operator_frame(f["title"], operator_pattern):
                op_ranges.append((f["level"], f["left"], f["left"] + f["width"]))

    if not op_ranges:
        return []

    # Total operator width (for normalization) — using dedup by left same as matched_pct
    op_marked = {}
    for lvl, left, right in op_ranges:
        if left not in op_marked:
            op_marked[left] = right - left
    op_total = 0
    cursor = 0
    for x in sorted(op_marked.keys()):
        if x >= cursor:
            op_total += op_marked[x]
            cursor = x + op_marked[x]

    if op_total == 0:
        return []

    # Collect callee frames (strictly inside any operator range, at deeper levels)
    fn_widths: dict[str, dict[int, int]] = defaultdict(dict)  # name -> {left: width}

    for frame_list in levels:
        for f in frame_list:
            fl = f["left"]
            fr = fl + f["width"]
            flevel = f["level"]
            if _is_noise(f["title"]):
                continue
            # Check if this frame falls inside any operator range at a deeper level
            for op_lvl, op_left, op_right in op_ranges:
                if flevel > op_lvl and fl >= op_left and fr <= op_right:
                    short = _short_name(f["title"])
                    if short and short != _short_name(operator_name + '::x'):
                        # dedup by left position within each function name
                        if fl not in fn_widths[short]:
                            fn_widths[short][fl] = f["width"]
                    break  # only need to match one range

    # Compute total width per function (dedup by left, then sort)
    fn_totals: dict[str, int] = {}
    for name, left_map in fn_widths.items():
        total = 0
        cursor = 0
        for x in sorted(left_map.keys()):
            if x >= cursor:
                total += left_map[x]
                cursor = x + left_map[x]
        fn_totals[name] = total

    # Sort and normalize
    sorted_fns = sorted(fn_totals.items(), key=lambda x: -x[1])
    results = []
    for name, w in sorted_fns[:top_n * 2]:  # take extra, filter below
        pct = 100.0 * w / op_total
        if pct >= min_pct and name:
            results.append((name, round(pct, 4)))
        if len(results) >= top_n:
            break

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Find top functions within each operator from flame graphs')
    parser.add_argument('--dir', required=True, help='Directory containing .html flame graphs')
    parser.add_argument('--operators-csv', required=True,
                        help='CSV from flame_top_operators.py')
    parser.add_argument('--out', required=True, help='Output CSV path')
    parser.add_argument('--top', type=int, default=5, help='Top N functions per operator (default 5)')
    parser.add_argument('--min-pct', type=float, default=0.1,
                        help='Minimum function %% (relative to operator) to include (default 0.1)')
    args = parser.parse_args()

    # Load operator list — use only rank=1 operators per file to avoid redundancy
    with open(args.operators_csv, newline='', encoding='utf-8') as f:
        op_rows = list(csv.DictReader(f))

    if not op_rows:
        print('[ERROR] operators CSV is empty', file=sys.stderr)
        sys.exit(1)

    # Build map: file_name -> [(query, operator, op_pct), ...]
    # Group by operator across files to get the representative set
    from collections import defaultdict as dd
    file_to_ops: dict[str, list] = dd(list)
    for row in op_rows:
        file_to_ops[row['file']].append((row['query'], row['operator'], float(row['matched_pct'])))

    # Find HTML files
    html_dir = Path(args.dir)
    html_map = {p.name: p for p in html_dir.rglob('*.html')}

    out_rows = []
    # Process only the first file for each operator (consistent enough across executors)
    processed_ops: set[str] = set()
    for file_name, op_list in file_to_ops.items():
        html_path = html_map.get(file_name)
        if not html_path:
            continue

        # Check if we have new operators to process
        new_ops = [(q, op, pct) for q, op, pct in op_list if op not in processed_ops]
        if not new_ops:
            continue

        print(f'Processing {file_name} ...', file=sys.stderr)
        levels, root_width = _parse_flame_html(str(html_path))
        if levels is None or root_width == 0:
            print(f'  [WARN] Parse failed for {file_name}', file=sys.stderr)
            continue

        for query, operator, op_pct in new_ops:
            if operator in processed_ops:
                continue
            processed_ops.add(operator)
            print(f'  Operator: {operator} ({op_pct:.2f}%)', file=sys.stderr)
            top_fns = top_functions_in_operator(levels, root_width, operator, args.top, args.min_pct)
            if not top_fns:
                print(f'    [WARN] No functions found inside {operator}', file=sys.stderr)
                continue
            for rank, (fn_name, fn_pct) in enumerate(top_fns, 1):
                out_rows.append({
                    'file': file_name,
                    'query': query,
                    'operator': operator,
                    'operator_pct': round(op_pct, 4),
                    'rank': rank,
                    'function': fn_name,
                    'function_pct': round(fn_pct, 4),
                })
                print(f'    #{rank} {fn_name}: {fn_pct:.2f}%', file=sys.stderr)

    if not out_rows:
        print('[ERROR] No function results produced.', file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'file', 'query', 'operator', 'operator_pct', 'rank', 'function', 'function_pct'])
        writer.writeheader()
        writer.writerows(out_rows)
    print(f'\n[OK] Wrote {len(out_rows)} rows to {out_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
