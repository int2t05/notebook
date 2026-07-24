"""Phase 2.5: fetch paper abstracts for green/yellow papers before Phase 3.

Sources in priority order:
1. USENIX presentation page (OSDI/ATC/NSDI/FAST/Security/...) — direct HTML scrape
2. arXiv (already populated by Phase 1B for external papers) — no-op pass-through
3. Semantic Scholar API by DOI — covers ACM DL / IEEE Xplore / Springer that block direct scraping
4. Semantic Scholar API by title (last resort when no DOI)

Critical correctness rule: when no source can produce an abstract, we set
`abstract = ""` AND `abstract_source = "missing"` so the extractor prompt
knows to use the [信息不足] honest-failure path instead of fabricating
from training data.
"""
import logging
import re
import time
from typing import Dict, List, Optional, Tuple

import httpx

log = logging.getLogger(__name__)

# Semantic Scholar API — free, ~100 req / 5min for unauthenticated.
# Recommended pacing: 1 req/sec.
S2_API = "https://api.semanticscholar.org/graph/v1/paper"
S2_PACE_SECONDS = 1.0
S2_TIMEOUT = 20

USENIX_DESC_BLOCK_RE = re.compile(
    # The description block ends where the next sibling block starts (open-access-content)
    # or before the closing </section>. Capture everything between the opening
    # field-items div and the next "field field-name-" / id="node-paper-full-group"
    # / </section> boundary.
    r'field-name-field-paper-description.*?field-items[^>]*>(.+?)'
    r'(?=<div\s+class="field\s+field-name-|<div\s+id="node-paper-full|</section>)',
    re.DOTALL,
)
USENIX_P_RE = re.compile(r'<p>(.+?)</p>', re.DOTALL)

DOI_FROM_PDF_RE = re.compile(r"(?:doi\.org/|dl\.acm\.org/doi/)(10\.\d+/[^/?#\s]+)")


def _http_get(url: str, timeout: int = 30) -> Optional[str]:
    headers = {"User-Agent": "paper-digest/0.1 (academic research)"}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as c:
            r = c.get(url, headers=headers)
            r.raise_for_status()
            return r.text
    except Exception as e:
        log.debug("HTTP GET failed for %s: %s", url, e)
        return None


def _clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fetch_usenix(pdf_url: str) -> Optional[str]:
    """USENIX presentation pages often have multi-paragraph abstracts where the
    quantitative effect (e.g., "reduces latency by 95%") only appears in the
    second or third <p>. We extract the whole description block and concatenate
    all <p> tags inside it, preserving paragraph order with double newlines.
    """
    if "usenix.org/conference/" not in pdf_url:
        return None
    html = _http_get(pdf_url)
    if not html:
        return None
    block_m = USENIX_DESC_BLOCK_RE.search(html)
    if not block_m:
        return None
    block = block_m.group(1)
    paragraphs = [_clean_text(p) for p in USENIX_P_RE.findall(block)]
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return None
    full = "\n\n".join(paragraphs)
    # Sometimes the field carries author bios; reject if too short
    if len(full) < 80:
        return None
    return full


def _extract_doi(paper: Dict) -> Optional[str]:
    if paper.get("doi"):
        return paper["doi"]
    pdf = paper.get("pdf") or ""
    m = DOI_FROM_PDF_RE.search(pdf)
    return m.group(1) if m else None


def _fetch_semantic_scholar_by_doi(doi: str) -> Optional[str]:
    url = f"{S2_API}/DOI:{doi}?fields=abstract"
    body = _http_get(url, timeout=S2_TIMEOUT)
    if not body:
        return None
    try:
        import json
        data = json.loads(body)
        abstract = data.get("abstract")
        return abstract if abstract and len(abstract) > 80 else None
    except Exception as e:
        log.debug("S2 JSON parse failed for DOI %s: %s", doi, e)
        return None


def _fetch_semantic_scholar_by_title(title: str) -> Optional[str]:
    """Last-resort search by exact title. Returns first match's abstract."""
    from urllib.parse import quote_plus
    q = title.rstrip(".").strip()
    url = f"{S2_API}/search?query={quote_plus(q)}&limit=1&fields=abstract,title"
    body = _http_get(url, timeout=S2_TIMEOUT)
    if not body:
        return None
    try:
        import json
        data = json.loads(body)
        results = data.get("data") or []
        if not results:
            return None
        cand = results[0]
        # Loose title match: normalized lowercase, no punctuation
        norm_a = re.sub(r"[^a-z0-9]", "", q.lower())
        norm_b = re.sub(r"[^a-z0-9]", "", (cand.get("title") or "").lower())
        if norm_a[:60] != norm_b[:60]:
            return None
        abs_ = cand.get("abstract")
        return abs_ if abs_ and len(abs_) > 80 else None
    except Exception as e:
        log.debug("S2 search failed for %r: %s", title[:60], e)
        return None


def fetch_abstract(paper: Dict) -> Tuple[str, str]:
    """Resolve a single paper's abstract.

    Returns:
        (abstract_text, source_tag) where source_tag ∈
        {"usenix", "arxiv", "semantic_scholar_doi", "semantic_scholar_title",
         "missing"}.
        abstract_text is "" when source_tag == "missing".
    """
    # Already populated (arXiv path)
    if paper.get("abstract") and len(paper["abstract"]) > 80:
        return paper["abstract"], paper.get("abstract_source", "arxiv")

    pdf = paper.get("pdf") or ""

    # 1. USENIX direct scrape
    if "usenix.org/conference/" in pdf:
        txt = _fetch_usenix(pdf)
        if txt:
            return txt, "usenix"

    # 2. Semantic Scholar by DOI
    doi = _extract_doi(paper)
    if doi:
        txt = _fetch_semantic_scholar_by_doi(doi)
        if txt:
            return txt, "semantic_scholar_doi"

    # 3. Semantic Scholar by title (last resort)
    title = paper.get("title") or ""
    if title:
        time.sleep(S2_PACE_SECONDS)  # avoid hammering S2 search endpoint
        txt = _fetch_semantic_scholar_by_title(title)
        if txt:
            return txt, "semantic_scholar_title"

    return "", "missing"


def fetch_all_abstracts(papers: List[Dict],
                         only_relevance: Optional[set] = None) -> Dict[str, int]:
    """Populate paper['abstract'] and paper['abstract_source'] in-place.

    Args:
        papers: list of paper dicts (modified in place)
        only_relevance: if set, only fetch for papers whose relevance ∈ this set
                        (typically {"green", "yellow"})

    Returns:
        stats dict: {"usenix":N, "semantic_scholar_doi":N, "missing":N, ...}
    """
    stats: Dict[str, int] = {}
    relevant = [p for p in papers
                if (only_relevance is None or p.get("relevance") in only_relevance)]
    log.info("fetch_all_abstracts: %d candidates (filter=%s)",
             len(relevant), only_relevance)
    for i, p in enumerate(relevant):
        # arXiv abstracts already populated upstream
        if p.get("abstract") and len(p["abstract"]) > 80:
            p["abstract_source"] = p.get("abstract_source") or "arxiv"
            stats[p["abstract_source"]] = stats.get(p["abstract_source"], 0) + 1
            continue
        txt, source = fetch_abstract(p)
        p["abstract"] = txt
        p["abstract_source"] = source
        stats[source] = stats.get(source, 0) + 1
        # Light pacing to be polite to S2 / USENIX
        if i % 5 == 4:
            time.sleep(0.5)
    log.info("fetch_all_abstracts stats: %s", stats)
    return stats
