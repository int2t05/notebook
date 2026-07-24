"""Phase 4: render Jinja2 templates → archive markdown files.

The renderer reads:
  - `references/conferences-metadata.yaml` — direction-agnostic conference
    attributes (CCF/CORE/h5, full_name, per-year dates/venue/best_papers).
  - Per-candidate `direction_match` field (emoji) coming straight from the
    Phase 1A LLM proposal — no per-direction profile YAML involved. This is
    the Plan A simplification: direction relevance is computed end-to-end by
    the LLM and rendered as-is.

Outputs: overview.md (S/A/B/未分档 tables), per-conference markdown,
external-sources.md.

TODO(comment-preserving merge): rerunning the skill overwrites existing
per-conference .md files, wiping any `📌 _<...>_` notes the user wrote.
When implementing, parse the prior .md, key notes by `paper.id`, and
re-inject them into the new render.
"""
from datetime import date as _date
from pathlib import Path
from typing import List, Dict, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
METADATA_PATH = Path(__file__).parent.parent / "references" / "conferences-metadata.yaml"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(disabled_extensions=("md", "j2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _load_metadata() -> Dict:
    if not METADATA_PATH.exists():
        return {}
    return yaml.safe_load(METADATA_PATH.read_text()) or {}


def _composite_score_from_meta(c: Dict, direction_score: float) -> float:
    """Composite for metadata-only conferences (no Phase 1A.1 entry). Mirrors
    conference_discoverer._composite_score but defined here to avoid an
    import cycle."""
    ccf_score = {"A": 10.0, "B": 6.0, "C": 3.0}.get(c.get("ccf", ""), 0.0)
    core_score = {"A*": 10.0, "A": 8.0, "B": 5.0, "C": 3.0}.get(c.get("core", ""), 0.0)
    h5_norm = 0.0
    try:
        h5_norm = min(float(c.get("h5") or 0) / 12.0, 10.0)
    except Exception:
        pass
    ccf_core = ((ccf_score + core_score) / 2
                if ccf_score and core_score else (ccf_score or core_score))
    return direction_score * 0.6 + ccf_core * 0.3 + h5_norm * 0.1


def _norm_title(t: str) -> str:
    """Normalize title for best-paper lookup (lowercase, strip punctuation/whitespace)."""
    return "".join(ch.lower() for ch in t if ch.isalnum())


def _bucket_red(reason: str) -> str:
    """Map free-text relevance_reason → coarse bucket used by the template."""
    r = (reason or "").lower()
    if "exclude_keyword" in r:
        return "excluded_by_filter"
    if "false positive" in r or "keyword pre-pass" in r or "keyword pre-filter" in r:
        return "keyword_false_positive"
    if "workshop" in r or "panel" in r or "tutorial" in r or "proceedings" in r:
        return "tooling_or_workshop"
    if "ai system" in r or "llm system" in r or "ml system" in r:
        return "ai_systems_offtopic"
    if "no match" in r or "off-topic" in r or "off topic" in r or r == "":
        return "off_topic"
    return "uncategorized"


def _annotate_red_categories(papers: List[Dict]) -> None:
    """Best-effort bucket assignment.

    Classifier-provided `relevance_category` (from the LLM in the new prompt
    format) wins; we only fall back to text-bucketing when the field is
    absent — e.g. older runs or the exclude_keyword_match pre-filter path.
    """
    for p in papers:
        if p.get("relevance") != "red":
            continue
        if not p.get("relevance_category"):
            p["relevance_category"] = _bucket_red(p.get("relevance_reason", ""))


def _annotate_papers_with_awards(papers: List[Dict], meta_year: Dict) -> None:
    """Set p['award'] in {'best','outstanding','artifact',None} by title match against metadata."""
    best_set = {_norm_title(t) for t in (meta_year.get("best_papers") or [])}
    outstanding_set = {_norm_title(t) for t in (meta_year.get("outstanding_papers") or [])}
    artifact_set = {_norm_title(t) for t in (meta_year.get("distinguished_artifacts") or [])}
    for p in papers:
        key = _norm_title(p.get("title", ""))
        if key in best_set:
            p["award"] = "best"
        elif key in outstanding_set:
            p["award"] = "outstanding"
        elif key in artifact_set:
            p["award"] = "artifact"
        else:
            p.setdefault("award", None)


def _enrich_conf_entry(c: Dict, metadata: Dict) -> Dict:
    """Merge static metadata into a runtime conf dict.

    direction_match is taken from the candidate's own field (set by Phase 1A
    from LLM direction_score → emoji via `score_to_emoji`). No profile YAML.
    """
    meta = metadata.get(c["name"], {}) or {}
    year_meta = (meta.get("years") or {}).get(c["year"], {}) or {}
    enriched = {
        **c,
        "tier": meta.get("tier"),
        "ccf": meta.get("ccf"),
        "core": meta.get("core"),
        "h5": meta.get("h5"),
        "direction_match": c.get("direction_match", ""),
        "full_name": meta.get("full_name"),
        "dates": year_meta.get("dates") or c.get("dates", ""),
        "venue": year_meta.get("venue") or c.get("venue", ""),
        "acceptance_rate": year_meta.get("acceptance_rate", ""),
        "_year_meta": year_meta,
    }
    enriched["status"] = _compute_status(enriched)
    return enriched


def _compute_status(c: Dict) -> str:
    """Decide one of {fetched, happened_not_fetched, future, skipped,
    stopped, unknown}.

    The status drives the emoji column in the overview table:
        ✅ fetched  / 📚 happened_not_fetched  / 🔜 future
        ⚫ skipped (biennial off-year, cancelled)  / 📉 stopped (discontinued)
        ❓ unknown (no date metadata at all)

    `skipped` / `stopped` are pulled directly from the per-year metadata
    when the user has annotated the YAML (e.g. SOSP 2026 = "双年制 不办").
    """
    # Explicit annotation in metadata wins over date-based guess
    explicit = (c.get("_year_meta") or {}).get("status")
    if explicit in ("skipped", "stopped", "postponed"):
        return explicit
    total = c.get("total", 0)
    if total and total > 0:
        return "fetched"
    dates_str = (c.get("dates") or "").strip()
    if not dates_str:
        return "unknown"
    # dates_str patterns: "2025-07-07~09" / "2026-01-31~02-04" / "2025-06-17"
    start = dates_str.split("~")[0].strip()
    try:
        # tolerate "2025-07-07" / "2025-07"
        parts = start.split("-")
        if len(parts) >= 3:
            d = _date(int(parts[0]), int(parts[1]), int(parts[2]))
        elif len(parts) == 2:
            d = _date(int(parts[0]), int(parts[1]), 1)
        else:
            return "unknown"
    except Exception:
        return "unknown"
    return "future" if d > _date.today() else "happened_not_fetched"


def _derive_year_columns(window_start: str, window_end: str) -> List[int]:
    """Return ascending years touching the time window (e.g. ['2025','2026'])."""
    try:
        sy = int(window_start[:4]) if window_start else 0
        ey = int(window_end[:4]) if window_end else 9999
    except Exception:
        return []
    if sy == 0 or ey == 9999:
        return []
    return list(range(sy, ey + 1))


def _expand_metadata_only_years(grouped: List[Dict], metadata: Dict,
                                  year_columns: List[int]) -> List[Dict]:
    """Backfill year cells from metadata when the runtime never produced one.

    A conference like SOSP might only have its 2025 entry in `grouped` because
    runtime fetched papers for 2025 only. For 2026, metadata says status=skipped
    (双年制); we want the 2026 cell to carry that info so the overview can
    render "⚫ 双年制 · 不办" instead of "—".
    """
    for slot in grouped:
        meta = metadata.get(slot["name"], {}) or {}
        years_meta = meta.get("years") or {}
        for y in year_columns:
            if slot["years"].get(y) is not None:
                continue
            ym = years_meta.get(y)
            if not ym:
                continue
            slot["years"][y] = {
                "status": ym.get("status") or _date_to_status(ym.get("dates", "")),
                "total": 0, "green": 0,
                "dates": ym.get("dates", ""),
                "venue": ym.get("venue", ""),
                "reason": ym.get("reason", ""),
                "md_link": "",
            }
    return grouped


def _date_to_status(dates_str: str) -> str:
    """Helper mirroring _compute_status's date arm — used for backfilled cells."""
    from datetime import date as _d
    if not dates_str:
        return "unknown"
    start = dates_str.split("~")[0].strip()
    try:
        parts = start.split("-")
        if len(parts) >= 3:
            d = _d(int(parts[0]), int(parts[1]), int(parts[2]))
        elif len(parts) == 2:
            d = _d(int(parts[0]), int(parts[1]), 1)
        else:
            return "unknown"
    except Exception:
        return "unknown"
    return "future" if d > _d.today() else "happened_not_fetched"


def _group_by_name(conf_entries: List[Dict], year_columns: List[int]) -> List[Dict]:
    """Pivot conf_entries by conference name with one cell per year column.

    Output shape:
        [
          {
            "name": "ASPLOS",
            "tier": "S", "ccf": "A", "core": "A*", "h5": 77,
            "direction_match": "🟢🟢", "full_name": "...",
            "composite_score": 9.3,                     # best across years
            "years": {                                  # one entry per year_columns
              2025: {"status":"fetched","total":182,"green":10,
                     "dates":"...","venue":"...","md_link":"./conferences/ASPLOS-2025.md"},
              2026: {"status":"happened_not_fetched","total":0,...},
            },
          }, ...
        ]
    """
    by_name: Dict[str, Dict] = {}
    for c in conf_entries:
        name = c["name"]
        slot = by_name.setdefault(name, {
            "name": name,
            "tier": c.get("tier"),
            "ccf": c.get("ccf"),
            "core": c.get("core"),
            "h5": c.get("h5"),
            "direction_match": c.get("direction_match"),
            "full_name": c.get("full_name"),
            "composite_score": c.get("composite_score", 0.0),
            "years": {},
        })
        # Lock in canonical metadata from whatever entry first set it; later
        # entries can only fill gaps.
        for k in ("tier", "ccf", "core", "h5", "direction_match", "full_name"):
            if not slot.get(k) and c.get(k):
                slot[k] = c.get(k)
        slot["composite_score"] = max(slot["composite_score"], c.get("composite_score", 0.0))
        slot["years"][c["year"]] = {
            "status": c.get("status", "unknown"),
            "total": c.get("total", 0),
            "green": c.get("green", 0),
            "dates": c.get("dates", ""),
            "venue": c.get("venue", ""),
            "reason": (c.get("_year_meta") or {}).get("reason", ""),
            "md_link": f"./conferences/{name}-{c['year']}.md",
        }
    # Ensure every conference has a cell for each year column (None if unknown)
    result = []
    for slot in by_name.values():
        for y in year_columns:
            slot["years"].setdefault(y, None)
        slot["_year_columns"] = year_columns
        result.append(slot)
    return result


def _merge_with_metadata_conferences(conf_entries: List[Dict],
                                      metadata: Dict,
                                      window_start: str,
                                      window_end: str) -> List[Dict]:
    """Append metadata-known conferences (any year overlapping the window)
    that weren't already discovered at runtime, so overview shows them with
    🔜 / 📚 status instead of silently omitting them."""
    have = {(c["name"], c["year"]) for c in conf_entries}
    try:
        start_year = int(window_start[:4]) if window_start else 0
        end_year = int(window_end[:4]) if window_end else 9999
    except Exception:
        start_year, end_year = 0, 9999

    extras: List[Dict] = []
    for name, meta in metadata.items():
        years = (meta.get("years") or {})
        for year, year_meta in years.items():
            if not isinstance(year, int):
                continue
            if year < start_year or year > end_year:
                continue
            if (name, year) in have:
                continue
            stub = {
                "name": name, "year": year,
                "total": 0, "green": 0,
                "composite_score": 0.0,
                "program_url": "",
            }
            extras.append(_enrich_conf_entry(stub, metadata))
    return conf_entries + extras


def render_archive(archive_dir: Path, manifest: Dict,
                   conferences: List[Dict],
                   conf_papers: List[Dict], external_papers: List[Dict],
                   tag_emoji: Dict,
                   metadata_scores: Optional[Dict[str, float]] = None) -> None:
    """Render overview.md + conferences/*.md + external-sources.md.

    `metadata_scores`: optional {conf_name: direction_score 0-10} from Phase
    1A.0 LLM bulk-scoring. Applied to metadata-only stubs (conferences in
    the window that didn't make Phase 1A.1's top-N) so their direction_match
    emoji column isn't empty in the overview tables.
    """
    env = _env()
    parsed = manifest.get("parsed", {})
    input_data = manifest.get("input", {})
    metadata = _load_metadata()
    metadata_scores = metadata_scores or {}

    # Group conf papers by conference
    by_conf: Dict[tuple, List[Dict]] = {}
    for p in conf_papers:
        key = (p["conference"], p["year"])
        by_conf.setdefault(key, []).append(p)

    # Augment conferences with paper stats + static metadata
    conf_entries: List[Dict] = []
    for c in conferences:
        cps = by_conf.get((c["name"], c["year"]), [])
        c["total"] = len(cps)
        c["green"] = sum(1 for p in cps if p.get("relevance") == "green")
        conf_entries.append(_enrich_conf_entry(c, metadata))

    # Merge in metadata-known conferences whose year overlaps the time window
    # but weren't fetched at runtime (future / not-crawled), so the overview
    # gives a complete S/A/B view rather than a fetch-only one.
    conf_entries = _merge_with_metadata_conferences(
        conf_entries, metadata,
        parsed.get("start_date", ""), parsed.get("end_date", ""),
    )

    # Apply Phase 1A.0 bulk scores to fillers whose direction_match is empty
    # (i.e. metadata-only conferences not proposed by Phase 1A.1)
    from scripts.conference_discoverer import score_to_emoji as _score_to_emoji
    for c in conf_entries:
        if not c.get("direction_match"):
            sc = metadata_scores.get(c["name"])
            if sc is not None:
                c["direction_match"] = _score_to_emoji(sc)
                if not c.get("composite_score"):
                    c["composite_score"] = _composite_score_from_meta(c, sc)

    # Compute the year columns shown in overview (from time window)
    year_columns = _derive_year_columns(
        parsed.get("start_date", ""), parsed.get("end_date", ""))

    # Sort each tier by best-known composite_score then alpha by name
    def _sort_key(c: Dict):
        return (-c.get("composite_score", 0), c.get("name", ""))

    # Split by tier — pivoted: each conference name appears once, with one
    # cell per year in year_columns. We pick the canonical metadata-derived
    # attributes (tier/ccf/core/h5/direction_match) from whichever year
    # entry has them; runtime stats (total/green) stay per-year.
    grouped = _group_by_name(conf_entries, year_columns)
    grouped = _expand_metadata_only_years(grouped, metadata, year_columns)
    tier_s = sorted([g for g in grouped if g.get("tier") == "S"], key=_sort_key)
    tier_a = sorted([g for g in grouped if g.get("tier") == "A"], key=_sort_key)
    tier_b = sorted([g for g in grouped if g.get("tier") == "B"], key=_sort_key)
    tier_unranked = sorted([g for g in grouped if not g.get("tier")], key=_sort_key)

    # Compute real external counts by source_subtype (replaces old hardcoded zeros)
    from collections import Counter as _Counter
    ext_by_sub = _Counter((p.get("source_subtype") or "arxiv")
                          for p in external_papers)
    external_counts = {
        "arxiv": ext_by_sub.get("arxiv", 0),
        "lab": ext_by_sub.get("labs", 0),
        "researcher": ext_by_sub.get("researchers", 0),
        "rfc": ext_by_sub.get("rfcs", 0),
        "blog": ext_by_sub.get("blogs", 0),
    }

    # Render overview
    overview_tpl = env.get_template("overview.md.j2")
    overview_md = overview_tpl.render(
        direction_raw=input_data.get("direction_raw", ""),
        start_date=parsed.get("start_date", ""),
        end_date=parsed.get("end_date", ""),
        created_at=manifest.get("created_at", ""),
        keywords=parsed.get("keywords", []),
        total_papers=len(conf_papers) + len(external_papers),
        green_count=sum(1 for p in conf_papers + external_papers
                        if p.get("relevance") == "green"),
        yellow_count=sum(1 for p in conf_papers + external_papers
                         if p.get("relevance") == "yellow"),
        red_count=sum(1 for p in conf_papers + external_papers
                      if p.get("relevance") == "red"),
        conferences=conf_entries,
        tier_s=tier_s,
        tier_a=tier_a,
        tier_b=tier_b,
        tier_unranked=tier_unranked,
        year_columns=year_columns,
        external_counts=external_counts,
        has_errors=False,
        error_count=0,
    )
    (archive_dir / "overview.md").write_text(overview_md)

    # Render each conference md — only for conferences with actual fetched papers.
    # Metadata-only stubs (📚 / 🔜) appear in overview but don't get their own page.
    conf_tpl = env.get_template("conference.md.j2")
    for c in conf_entries:
        cps = by_conf.get((c["name"], c["year"]), [])
        if not cps:
            continue
        year_meta = c.get("_year_meta") or {}
        _annotate_papers_with_awards(cps, year_meta)
        _annotate_red_categories(cps)
        conf_md = conf_tpl.render(
            conference=c["name"], year=c["year"],
            dates=c.get("dates", ""),
            venue=c.get("venue", ""),
            ccf=c.get("ccf"),
            core=c.get("core"),
            h5=c.get("h5"),
            direction_match=c.get("direction_match"),
            full_name=c.get("full_name"),
            acceptance_rate=c.get("acceptance_rate", ""),
            total_papers=len(cps),
            program_url=c.get("program_url", ""),
            fetch_date=manifest.get("created_at", "")[:10],
            papers=cps, tag_emoji=tag_emoji,
        )
        (archive_dir / "conferences" / f"{c['name']}-{c['year']}.md").write_text(conf_md)

    # Render external
    ext_tpl = env.get_template("external.md.j2")
    ext_md = ext_tpl.render(
        direction_raw=input_data.get("direction_raw", ""),
        start_date=parsed.get("start_date", ""),
        end_date=parsed.get("end_date", ""),
        created_at=manifest.get("created_at", ""),
        papers=external_papers,
        tag_emoji=tag_emoji,
    )
    (archive_dir / "external-sources.md").write_text(ext_md)
