"""Phase 1B: discover external sources (arXiv + LLM-driven curated lab/researcher/blog/rfc).

Two sub-stages:

**Phase 1B.1 — arXiv search**
    Uses the keyword set Phase 0.5 expanded (or raw Phase 0 keywords if Phase
    0.5 was skipped). Categories come from Phase 0.5's LLM output too. The
    keyword list is chunked into 6-phrase groups to dodge arXiv's silent
    long-OR misbehavior.

**Phase 1B.5 — LLM-driven curated sources**
    For each direction, the strong-model LLM proposes 8-15 lab/researcher/blog/
    RFC entries with URLs marked "[manual verify]" when uncertain. Replaces
    the previous hand-maintained `references/external-sources.yaml` so the
    skill generalizes to any direction without YAML edits.

Both sub-stages produce paper-shaped dicts that flow through Phase 2/4
identically to conference papers.
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from urllib.parse import quote_plus

from scripts.utils import _http_get, relaxed_json_loads

log = logging.getLogger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_PAGE_SIZE = 50
ARXIV_MAX_PAGES = 4  # up to 200 candidates per direction

# Minimal default arXiv categories if Phase 0.5 didn't supply any. Covers a
# broad systems/PL surface; LLM-supplied list always wins when present.
DEFAULT_ARXIV_CATEGORIES = [
    "cs.OS", "cs.PL", "cs.AR", "cs.DC", "cs.PF", "cs.SE",
    "cs.CR", "cs.LG", "cs.DB",
]

EXTERNAL_CURATE_PROMPT = (Path(__file__).parent.parent
                          / "prompts" / "external-curate.txt")


# ============================================================
# Phase 1B.1: arXiv
# ============================================================

def _build_search_query(keywords: List[str], categories: List[str]) -> str:
    quoted = [f'"{kw}"' if " " in kw or "-" in kw else kw for kw in keywords]
    title_clause = " OR ".join(f"ti:{q}" for q in quoted)
    abs_clause = " OR ".join(f"abs:{q}" for q in quoted)
    if categories:
        cat_clause = " OR ".join(f"cat:{c}" for c in categories)
        return f"(({title_clause}) OR ({abs_clause})) AND ({cat_clause})"
    return f"({title_clause}) OR ({abs_clause})"


def _chunk_keywords(keywords: List[str], chunk_size: int = 6) -> List[List[str]]:
    return [keywords[i:i + chunk_size] for i in range(0, len(keywords), chunk_size)]


def _arxiv_one_request(search_query: str, start: int = 0,
                        page_size: int = ARXIV_PAGE_SIZE) -> str:
    url = (f"{ARXIV_API}?search_query={quote_plus(search_query)}"
           f"&start={start}&max_results={page_size}"
           f"&sortBy=submittedDate&sortOrder=descending")
    return _http_get(url, timeout=30)


def _parse_arxiv_entries(xml: str, start_date: str, end_date: str,
                          seen_ids: Set[str], next_id_start: int) -> List[Dict]:
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.DOTALL)
    out: List[Dict] = []
    for entry in entries:
        title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        id_m = re.search(r"<id>http://arxiv.org/abs/([^<]+)</id>", entry)
        date_m = re.search(r"<published>(\d{4}-\d{2}-\d{2})", entry)
        authors = re.findall(r"<name>(.*?)</name>", entry)
        summary_m = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        if not (title_m and id_m and date_m):
            continue
        pub_date = date_m.group(1)
        if not (start_date <= pub_date <= end_date):
            continue
        arxiv_id = id_m.group(1).strip()
        base_id = arxiv_id.split("v")[0]
        if base_id in seen_ids:
            continue
        seen_ids.add(base_id)
        out.append({
            "id": f"X-arxiv-{next_id_start + len(out):03d}",
            "source_type": "external",
            "source_subtype": "arxiv",
            "title": " ".join(title_m.group(1).split()),
            "authors": authors,
            "affiliation": "",
            "pdf": f"https://arxiv.org/abs/{arxiv_id}",
            "doi": None,
            "date": pub_date,
            "abstract": " ".join(summary_m.group(1).split()) if summary_m else "",
        })
    return out


def arxiv_query(keywords: List[str], start_date: str, end_date: str,
                categories: Optional[List[str]] = None,
                max_results: int = ARXIV_PAGE_SIZE * ARXIV_MAX_PAGES,
                recorder=None) -> List[Dict]:
    """Query arXiv with chunked sub-queries (long OR-disjunctions trigger silent
    arXiv API failures, so we issue one request per 6-keyword chunk and dedupe
    by arxiv id)."""
    cats = list(categories) if categories else list(DEFAULT_ARXIV_CATEGORIES)
    chunks = _chunk_keywords(keywords, chunk_size=6)
    log.info("arXiv search: %d keywords → %d chunks · categories=%s",
             len(keywords), len(chunks), cats)

    papers: List[Dict] = []
    seen_ids: Set[str] = set()
    per_chunk_pages = max(1, (max_results // max(len(chunks), 1)) // ARXIV_PAGE_SIZE)
    per_chunk_pages = min(max(per_chunk_pages, 1), ARXIV_MAX_PAGES)

    for ci, chunk in enumerate(chunks):
        sub_query = _build_search_query(chunk, cats)
        chunk_added = 0
        for page in range(per_chunk_pages):
            try:
                xml = _arxiv_one_request(sub_query, start=page * ARXIV_PAGE_SIZE)
            except Exception as e:
                log.warning("arXiv chunk %d page %d failed: %s", ci, page, e)
                if recorder is not None:
                    recorder.arxiv_chunk_failed(ci, str(e))
                break
            new = _parse_arxiv_entries(xml, start_date, end_date,
                                       seen_ids, next_id_start=len(papers) + 1)
            if not new:
                break
            papers.extend(new)
            chunk_added += len(new)
            if len(new) < ARXIV_PAGE_SIZE:
                break
        log.info("arXiv chunk %d (%s ..): +%d papers (cumulative %d)",
                 ci, ", ".join(chunk[:2]), chunk_added, len(papers))
        if len(papers) >= max_results:
            break

    log.info("arXiv returned %d unique papers via %d chunked queries",
             len(papers), len(chunks))
    return papers[:max_results]


# ============================================================
# Phase 1B.5: LLM-driven curated external sources
# ============================================================

def curate_external_via_llm(direction_raw: str, keywords: List[str],
                              start_date: str, end_date: str, llm,
                              recorder=None) -> Dict:
    """Ask the LLM to propose lab/researcher/blog/RFC entries for the direction.

    Returns a dict shaped like the legacy external-sources.yaml schema:
        {"labs": [...], "researchers": [...], "blogs": [...], "rfcs": [...]}
    Each list item carries title / url / source / date / relevance /
    relevance_reason. URLs the LLM is unsure about are suffixed with
    " [manual verify]" so downstream rendering can flag them.

    Failure modes (LLM down, JSON parse fail) return an all-empty dict — the
    arXiv branch (Phase 1B.1) still works on its own.
    """
    if llm is None:
        return {"labs": [], "researchers": [], "blogs": [], "rfcs": []}

    from datetime import date as _date
    prompt = (EXTERNAL_CURATE_PROMPT.read_text()
              .replace("{direction_raw}", direction_raw)
              .replace("{keywords}", str(keywords))
              .replace("{start_date}", start_date)
              .replace("{end_date}", end_date)
              .replace("{today}", _date.today().isoformat()))
    try:
        resp, _ = llm.call(prompt, model="strong", max_tokens=2500, json_mode=True)
        data = relaxed_json_loads(resp)
    except Exception as e:
        log.warning("Phase 1B.5 curate LLM failed: %s — skipping curated sources", e)
        if recorder is not None:
            recorder.curate_failed(str(e))
        return {"labs": [], "researchers": [], "blogs": [], "rfcs": []}

    out = {"labs": [], "researchers": [], "blogs": [], "rfcs": []}
    for section in out:
        items = data.get(section, []) or []
        if not isinstance(items, list):
            continue
        out[section] = [i for i in items if isinstance(i, dict) and i.get("title")]
    log.info("Phase 1B.5 curated: labs=%d researchers=%d blogs=%d rfcs=%d",
             len(out["labs"]), len(out["researchers"]),
             len(out["blogs"]), len(out["rfcs"]))
    return out


def _to_paper_shape(items: List[Dict], section: str, id_prefix: str) -> List[Dict]:
    """Convert LLM-curated entries into the paper-shaped dicts the rest of the
    pipeline consumes."""
    out: List[Dict] = []
    for i, raw in enumerate(items, 1):
        if not raw.get("title"):
            continue
        p = {
            "id": f"{id_prefix}-{i:03d}",
            "source_type": "external",
            "source_subtype": section,
            "title": raw["title"],
            "authors": raw.get("authors", []),
            "affiliation": raw.get("source", ""),
            "pdf": raw.get("url", ""),
            "doi": raw.get("doi"),
            "date": raw.get("date", ""),
            "abstract": raw.get("abstract", ""),
            "abstract_source": "curated" if raw.get("abstract") else "missing",
            "relevance": raw.get("relevance", "yellow"),
            "relevance_reason": raw.get("relevance_reason", "curated entry"),
        }
        if raw.get("summary"):
            p["summary"] = raw["summary"]
            p["summary"]["effect_quantified"] = (
                "[未量化]" not in p["summary"].get("effect", "")
                and "[信息不足]" not in p["summary"].get("effect", "")
            )
        if raw.get("tags"):
            p["tags"] = raw["tags"]
        out.append(p)
    return out


# ============================================================
# Public Phase 1B entry
# ============================================================

def discover_external(keywords: List[str], start_date: str, end_date: str,
                       direction_raw: str = "",
                       arxiv_categories: Optional[List[str]] = None,
                       llm=None, recorder=None) -> Dict:
    """Phase 1B entry: arXiv (1B.1) + LLM-curated lab/researcher/blog/rfc (1B.5).

    Args:
        keywords: keywords to search arXiv with (Phase 0.5 expanded or Phase 0 raw)
        start_date / end_date: ISO date strings
        direction_raw: original direction text (for the curate LLM prompt)
        arxiv_categories: optional cs.X list (Phase 0.5 supplies these);
                          defaults to a broad systems/PL/security/ML/DB set
        llm: LLMClient (or any backend); needed for Phase 1B.5. If None,
             the curated sources are empty and only arXiv runs.

    Returns:
        Dict shape: {"arxiv": [...], "lab": [...], "researcher": [...],
                     "rfc": [...], "blog": [...]}  (keys singular for renderer
        compat).
    """
    arxiv_papers = arxiv_query(keywords, start_date, end_date,
                                categories=arxiv_categories, recorder=recorder)

    curated = curate_external_via_llm(direction_raw, keywords,
                                       start_date, end_date, llm,
                                       recorder=recorder)

    return {
        "arxiv": arxiv_papers,
        "lab": _to_paper_shape(curated["labs"], "labs", "X-lab"),
        "researcher": _to_paper_shape(curated["researchers"], "researchers", "X-researcher"),
        "rfc": _to_paper_shape(curated["rfcs"], "rfcs", "X-rfc"),
        "blog": _to_paper_shape(curated["blogs"], "blogs", "X-blog"),
    }
