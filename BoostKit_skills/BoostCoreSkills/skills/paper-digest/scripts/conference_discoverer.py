"""Phase 1A: discover relevant conferences (LLM-driven) + DBLP verify + metadata enrich.

Design (Plan A — pure LLM-driven, no per-direction profile YAML):

  1A.1  LLM proposes Top-N (name, year, direction_score, rationale) candidates
        for the direction + window. No profile.direction_match hint — the LLM
        works from direction text + keywords alone.

  1A.2  Each candidate is verified against DBLP via `fetch_program`. 404 /
        empty page → dropped (fabricated year / made-up venue caught here).

  1A.3  When LLM yields < top_n verified candidates, top up from
        `conferences-metadata.yaml`'s known (name, year) entries inside the
        window. This is purely a fallback — the LLM is primary.

  1A.4  Metadata enrichment: CCF / CORE / h5 / dates / venue / Best Paper /
        full_name are stitched in from metadata.yaml for any verified
        candidate that has them. Missing fields gracefully degrade.

  direction_match emoji is derived **at this layer** from `direction_score`,
  not from any profile YAML — see `_score_to_emoji`. This makes the skill
  generalize to any direction with zero static configuration.
"""
import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import yaml

from scripts.utils import LLMClient, _http_get, fetch_program, relaxed_json_loads

log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "conference-rank.txt"
BULK_SCORE_PROMPT = (Path(__file__).parent.parent / "prompts"
                     / "conference-score-bulk.txt")
METADATA_PATH = (Path(__file__).parent.parent / "references"
                 / "conferences-metadata.yaml")


def _load_metadata() -> Dict:
    if not METADATA_PATH.exists():
        return {}
    return yaml.safe_load(METADATA_PATH.read_text()) or {}


def _ccf_core_score(ccf: str, core: str) -> float:
    """Map CCF (A/B/C) and CORE (A*/A/B/C) tiers to a 0-10 score."""
    table_ccf = {"A": 10.0, "B": 6.0, "C": 3.0}
    table_core = {"A*": 10.0, "A": 8.0, "B": 5.0, "C": 3.0}
    a = table_ccf.get(ccf, 0.0)
    b = table_core.get(core, 0.0)
    if a and b:
        return (a + b) / 2
    return a or b


def _h5_normalized(h5) -> float:
    """h5-index ~ 0..120; squash to 0..10."""
    try:
        return min(float(h5) / 12.0, 10.0)
    except Exception:
        return 0.0


def _composite_score(direction_score: float, ccf: str, core: str, h5) -> float:
    """direction_score × 0.6 + (ccf+core)/2 × 0.3 + h5_norm × 0.1.

    direction_score is the LLM's per-(conference, direction) relevance number;
    ccf/core/h5 are direction-agnostic metadata facts.
    """
    return (direction_score * 0.6
            + _ccf_core_score(ccf, core) * 0.3
            + _h5_normalized(h5) * 0.1)


def llm_bulk_score_metadata(direction_raw: str, keywords: List[str],
                              metadata: Dict, llm) -> Dict[str, float]:
    """One LLM call: score every conference in metadata.yaml against direction.

    Result is used by the renderer to fill direction_match emoji on metadata-
    only fillers (conferences in the window that didn't make Phase 1A's
    top-N + DBLP verify cut). Without this, those fillers would render with
    empty direction_match column — losing the at-a-glance "is this venue
    relevant to my direction?" signal the user sees in the overview table.

    Failure modes (no LLM, parse error) return an empty dict; the renderer
    just falls back to showing "—" for those rows.
    """
    if llm is None or not metadata:
        return {}
    names = sorted(metadata.keys())
    prompt = (BULK_SCORE_PROMPT.read_text()
              .replace("{direction_raw}", direction_raw)
              .replace("{keywords}", json.dumps(keywords, ensure_ascii=False))
              .replace("{conference_names}",
                       json.dumps(names, ensure_ascii=False)))
    try:
        resp, _ = llm.call(prompt, model="strong", max_tokens=1500,
                            json_mode=True)
        data = relaxed_json_loads(resp)
        scores_raw = data.get("scores", {}) or {}
        out: Dict[str, float] = {}
        for n, s in scores_raw.items():
            try:
                out[n] = float(s)
            except (TypeError, ValueError):
                continue
        log.info("Phase 1A.0 bulk-scored %d/%d metadata confs", len(out), len(names))
        return out
    except Exception as e:
        log.warning("Phase 1A.0 bulk-score failed: %s", e)
        return {}


def score_to_emoji(direction_score: float) -> str:
    """Map a 0-10 direction relevance number to the user-facing emoji used in
    overview tables. Single source of truth for what 🟢🟢🟢 / 🟢🟢 / 🟢 / 🟡 mean."""
    if direction_score >= 9:
        return "🟢🟢🟢"
    if direction_score >= 7:
        return "🟢🟢"
    if direction_score >= 5:
        return "🟢"
    if direction_score >= 3:
        return "🟡"
    return ""


# --- LLM-driven candidate generation (Phase 1A.1) ---

def llm_propose_candidates(direction_raw: str,
                            keywords: List[str],
                            start_date: str,
                            end_date: str,
                            top_n: int,
                            llm: LLMClient) -> List[Dict]:
    """Ask the LLM for Top-N (name, year, direction_score, rationale) candidates.

    No profile YAML, no static hint dict. The LLM works from direction +
    keywords + window alone. Caller validates each candidate via DBLP.
    """
    if llm is None:
        log.warning("No LLM available for Phase 1A.1 — returning empty candidate list")
        return []

    top_n_max = max(top_n + 5, int(top_n * 1.3))
    prompt = (PROMPT_PATH.read_text()
              .replace("{direction_raw}", direction_raw)
              .replace("{keywords}", json.dumps(keywords, ensure_ascii=False))
              .replace("{start_date}", start_date)
              .replace("{end_date}", end_date)
              .replace("{today}", date.today().isoformat())
              .replace("{top_n_max}", str(top_n_max))
              .replace("{top_n}", str(top_n)))
    try:
        resp, _ = llm.call(prompt, model="strong", max_tokens=3500, json_mode=True)
        data = relaxed_json_loads(resp)
    except Exception as e:
        log.error("Phase 1A.1 LLM proposal failed: %s", e)
        return []

    raw = data.get("ranked") or data.get("conferences") or []
    out: List[Dict] = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        name = (r.get("name") or "").strip()
        try:
            year = int(r.get("year"))
        except (TypeError, ValueError):
            continue
        if not name:
            continue
        out.append({
            "name": name,
            "year": year,
            "expected_month": r.get("expected_month"),
            "direction_score": float(r.get("direction_score") or 5.0),
            "rationale": r.get("rationale", ""),
        })
    # Dedupe by (name, year) preserving order
    seen, deduped = set(), []
    for c in out:
        key = (c["name"], c["year"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    log.info("Phase 1A.1: LLM proposed %d unique (name, year) candidates", len(deduped))
    return deduped


# --- Metadata-driven fallback (only when LLM yields too few verified) ---

def _parse_iso_date(s: str) -> Optional[date]:
    if not s:
        return None
    head = s.split("~")[0].strip()
    parts = head.split("-")
    try:
        if len(parts) >= 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        if len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
        if len(parts) == 1:
            return date(int(parts[0]), 1, 1)
    except Exception:
        return None
    return None


def _year_overlaps_window(year: int, year_meta: dict,
                          start: date, end: date) -> bool:
    d = _parse_iso_date(year_meta.get("dates", ""))
    if d is not None:
        return start <= d <= end
    return start.year <= year <= end.year


def _candidates_from_metadata(metadata: Dict, start: date, end: date) -> List[Dict]:
    """Generic metadata candidates with a neutral direction_score (5.0).

    Used only when the LLM path returned too few verified candidates and we
    need to top up. No direction-specific scoring — the renderer will display
    these without a meaningful emoji (the user's direction is unknown to a
    pure metadata enumeration)."""
    out: List[Dict] = []
    for name, meta in metadata.items():
        years = (meta.get("years") or {})
        for year, year_meta in years.items():
            if not isinstance(year, int):
                continue
            year_meta = year_meta or {}
            if year_meta.get("status") in ("skipped", "stopped"):
                continue
            if not _year_overlaps_window(year, year_meta, start, end):
                continue
            out.append({
                "name": name,
                "year": year,
                "direction_score": 5.0,  # neutral; LLM didn't rate it
                "rationale": "metadata fallback (LLM yielded too few candidates)",
            })
    return out


# --- DBLP verification (Phase 1A.2) ---

def verify_via_dblp(candidate: Dict) -> Tuple[bool, List[Dict], str]:
    """Try `fetch_program(name, year)`. ok=True iff ≥1 paper returned."""
    try:
        papers = fetch_program(candidate["name"], candidate["year"])
    except Exception as e:
        return False, [], f"fetch_error: {e}"
    if not papers:
        return False, [], "dblp_empty"
    return True, papers, "ok"


# --- Public entry ---

def discover_conferences(keywords: List[str], start_date: str, end_date: str,
                         top_n: int, llm: Optional[LLMClient] = None,
                         direction_raw: str = "",
                         use_metadata_fallback: bool = True,
                         recorder=None) -> List[Dict]:
    """Phase 1A: LLM proposes → DBLP verifies → metadata enriches → emoji from score.

    Each returned candidate carries:
      name, year, direction_score, direction_match (emoji), composite_score,
      papers (DBLP fetch result), fetch_status, rationale,
      ccf/core/h5/dates/venue/full_name (when metadata has them).
    """
    metadata = _load_metadata()
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except Exception:
        log.error("Phase 1A: invalid window %s..%s", start_date, end_date)
        return []

    candidates = llm_propose_candidates(
        direction_raw or " ".join(keywords),
        keywords, start_date, end_date, top_n, llm,
    )

    verified: List[Dict] = []
    rejected: List[Dict] = []
    seen_keys: set = set()
    for c in candidates:
        ok, papers, reason = verify_via_dblp(c)
        c["fetch_status"] = "success" if ok else "rejected"
        c["fetch_reject_reason"] = "" if ok else reason
        c["papers"] = papers
        seen_keys.add((c["name"], c["year"]))
        if ok:
            verified.append(c)
        else:
            rejected.append(c)
            log.info("Phase 1A.2: dropped LLM candidate %s %s (%s)",
                     c["name"], c["year"], reason)
            if recorder is not None:
                recorder.dblp_rejected(c["name"], c["year"], reason)
    log.info("Phase 1A.2: %d verified, %d rejected by DBLP",
             len(verified), len(rejected))

    if use_metadata_fallback and len(verified) < top_n:
        meta_cands = _candidates_from_metadata(metadata, start, end)
        for mc in meta_cands:
            if len(verified) >= top_n:
                break
            key = (mc["name"], mc["year"])
            if key in seen_keys:
                continue
            ok, papers, reason = verify_via_dblp(mc)
            mc["fetch_status"] = "success" if ok else "rejected"
            mc["fetch_reject_reason"] = "" if ok else reason
            mc["papers"] = papers
            seen_keys.add(key)
            if ok:
                verified.append(mc)

    # Enrichment from metadata + emoji from score
    for c in verified:
        meta = metadata.get(c["name"], {}) or {}
        year_meta = (meta.get("years") or {}).get(c["year"], {}) or {}
        c["ccf"] = meta.get("ccf", "")
        c["core"] = meta.get("core", "")
        c["h5"] = meta.get("h5")
        c["full_name"] = meta.get("full_name", "")
        c["tier_hint"] = meta.get("tier", "")
        c["dates"] = year_meta.get("dates", "")
        c["venue"] = year_meta.get("venue", "")
        c["acceptance_rate"] = year_meta.get("acceptance_rate", "")
        c["direction_match"] = score_to_emoji(c.get("direction_score", 5.0))
        c["composite_score"] = _composite_score(
            c.get("direction_score", 5.0), c["ccf"], c["core"], c["h5"],
        )

    verified.sort(key=lambda c: -c.get("composite_score", 0))
    return verified[:top_n]
