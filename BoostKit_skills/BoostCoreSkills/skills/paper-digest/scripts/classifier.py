"""Phase 2: coarse-grained relevance classification (title-only, batch of 25)."""
import json
import logging
from pathlib import Path
from typing import List, Dict

from scripts.utils import LLMClient, relaxed_json_loads

log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "coarse-classify.txt"


def _title_matches_any(title: str, words: List[str]) -> bool:
    title_lower = title.lower()
    return any(w.lower() in title_lower for w in words)


def classify_batch(papers: List[Dict], keywords: List[str],
                   exclude: List[str], llm: LLMClient,
                   recorder=None) -> List[Dict]:
    """Send a batch of up to 25 papers to LLM and merge relevance back."""
    prompt = (PROMPT_PATH.read_text()
              .replace("{keywords}", json.dumps(keywords, ensure_ascii=False))
              .replace("{exclude}", json.dumps(exclude, ensure_ascii=False))
              .replace("{papers_json}", json.dumps(
                  [{"id": p["id"], "title": p["title"]} for p in papers],
                  ensure_ascii=False,
              )))
    response, _ = llm.call(prompt, model="flash", max_tokens=2000, json_mode=True)
    try:
        results = relaxed_json_loads(response).get("results", [])
    except json.JSONDecodeError as e:
        log.error("classify_batch JSON parse failed: %s", e)
        if recorder is not None:
            recorder.classify_batch_failed(
                len(papers), [p["id"] for p in papers], str(e))
        # Mark all as unknown so caller can review
        for p in papers:
            p["relevance"] = "unknown"
            p["relevance_reason"] = f"json_parse_error: {e}"
        return papers
    by_id = {r["id"]: r for r in results}
    for p in papers:
        r = by_id.get(p["id"])
        if r:
            p["relevance"] = r.get("relevance", "unknown")
            p["relevance_reason"] = r.get("reason", "")
            # category only meaningful for red; classifier-provided value
            # takes priority over renderer's text-based bucketing.
            cat = r.get("category")
            if cat:
                p["relevance_category"] = cat
        else:
            p["relevance"] = "unknown"
            p["relevance_reason"] = "missing in LLM response"
    return papers


def classify_all(papers: List[Dict], keywords: List[str], exclude: List[str],
                 llm: LLMClient, batch_size: int = 25,
                 recorder=None) -> List[Dict]:
    """Pre-filter exclude_keywords, then batch-classify the rest."""
    todo: List[Dict] = []
    for p in papers:
        if _title_matches_any(p["title"], exclude):
            p["relevance"] = "red"
            p["relevance_reason"] = "exclude_keyword_match"
            p["relevance_category"] = "excluded_by_filter"
        else:
            todo.append(p)
    log.info("Pre-filtered %d red by exclude_keyword; %d to LLM classify",
             len(papers) - len(todo), len(todo))

    for i in range(0, len(todo), batch_size):
        batch = todo[i:i + batch_size]
        classify_batch(batch, keywords, exclude, llm, recorder=recorder)

    return papers
