"""Phase 3: deep detail extraction (4 段 + 3-tag) with mandatory quantification."""
import json
import logging
import re
import time
from pathlib import Path
from typing import List, Dict, Optional

from scripts.utils import LLMClient, relaxed_json_loads

log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "detail-extract.txt"

EXTRACT_ERROR_PLACEHOLDER = "[抽取失败]"

QUANTIFIED_PATTERNS = re.compile(
    r"(\d+\.?\d*\s*(%|x|×|×|ms|μs|us|ns|s|MB|GB|TB|KB|ops|Mops|Gops|FLOPS))"
    r"|(\[未量化\])"
    r"|(\[信息不足\])"
)

# Anti-fabrication scanner: requires a real unit (not just a bare number),
# so things like "O(1)", "log(N)", "GPU-2", or year "2024" don't trigger
# the missing-abstract guard.
NUMBER_RE = re.compile(r"\d+\.?\d*\s*(%|x|×|ms|μs|us|ns|MB|GB|TB|KB|ops|Mops|Gops|FLOPS)")


def is_effect_quantified(text: str) -> bool:
    """Return True if effect text contains a quantitative pattern or [未量化]/[信息不足] marker."""
    if not text:
        return False
    return bool(QUANTIFIED_PATTERNS.search(text))


def looks_fabricated_when_missing(summary: Dict, abstract_source: str) -> bool:
    """If abstract is missing, the LLM must not produce numbers in any segment.

    Returns True when we detect numbers in any summary section but the abstract
    was never fetched — strong signal of fabrication from training memory.
    """
    if abstract_source != "missing":
        return False
    for key in ("background", "core", "effect", "insight"):
        seg = (summary.get(key) or "")
        # Strip the honest [信息不足] prefix so legitimate prefix doesn't false-trigger
        seg_stripped = seg.replace("[信息不足，abstract 未获取]", "").replace("[信息不足]", "")
        if NUMBER_RE.search(seg_stripped):
            return True
    return False


def extract_one(paper: Dict, keywords: List[str], llm: LLMClient,
                recorder: Optional[object] = None) -> Dict:
    """Extract 4-段 summary + 3 tags for a single paper. Retries once if effect
    段 lacks quantification.

    `recorder` (QualityRecorder | None) — when provided, records timing /
    retries / parse failures for the post-run quality report.
    """
    _t0 = time.time()
    prompt_template = PROMPT_PATH.read_text()

    abstract_text = paper.get("abstract", "") or ""
    abstract_source = paper.get("abstract_source") or (
        "fetched" if abstract_text else "missing"
    )

    def _build(extra_note: str = "") -> str:
        # When abstract is genuinely missing, pass an explicit sentinel
        # so the prompt's [信息不足] enforcement path triggers reliably.
        abstract_for_prompt = (
            abstract_text + extra_note
            if abstract_text
            else "(none — abstract not fetched; do not fabricate)"
        )
        return (prompt_template
                .replace("{keywords}", json.dumps(keywords, ensure_ascii=False))
                .replace("{paper_id}", paper["id"])
                .replace("{title}", paper["title"])
                .replace("{authors}", json.dumps(paper.get("authors", []), ensure_ascii=False))
                .replace("{affiliation}", paper.get("affiliation", ""))
                .replace("{abstract_source}", abstract_source)
                .replace("{abstract}", abstract_for_prompt))

    for attempt in (1, 2):
        try:
            resp_text, _ = llm.call(_build(""), model="strong", max_tokens=1500, json_mode=True)
            data = relaxed_json_loads(resp_text)
        except json.JSONDecodeError as e:
            log.warning("extract_one attempt %d JSON parse failed for %s: %s",
                        attempt, paper["id"], e)
            if recorder is not None:
                recorder.json_parse_failure("phase3", paper["id"], attempt, str(e))
            if attempt == 2:
                paper["summary"] = {
                    "background": EXTRACT_ERROR_PLACEHOLDER,
                    "core": EXTRACT_ERROR_PLACEHOLDER,
                    "effect": EXTRACT_ERROR_PLACEHOLDER,
                    "effect_quantified": False,
                    "insight": EXTRACT_ERROR_PLACEHOLDER,
                }
                paper["tags"] = {"industry": "academic", "opensource": "no",
                                 "deployability": "medium"}
                paper["tag_notes"] = {"error": f"json_parse: {e}"}
                if recorder is not None:
                    recorder.extract_failed(paper["id"], f"json_parse: {e}")
                    recorder.extract_timing(paper["id"], time.time() - _t0)
                return paper
            continue
        except Exception as e:
            # API errors, timeouts, etc. — distinguish from JSON failures
            # so callers can later read tag_notes.error to route retries.
            log.warning("extract_one attempt %d API/runtime failed for %s: %s",
                        attempt, paper["id"], e)
            if recorder is not None:
                recorder.record("phase3", "extract_api_error",
                                paper_id=paper["id"], attempt=attempt, error=str(e))
            if attempt == 2:
                paper["summary"] = {
                    "background": EXTRACT_ERROR_PLACEHOLDER,
                    "core": EXTRACT_ERROR_PLACEHOLDER,
                    "effect": EXTRACT_ERROR_PLACEHOLDER,
                    "effect_quantified": False,
                    "insight": EXTRACT_ERROR_PLACEHOLDER,
                }
                paper["tags"] = {"industry": "academic", "opensource": "no",
                                 "deployability": "medium"}
                paper["tag_notes"] = {"error": f"api: {e}"}
                if recorder is not None:
                    recorder.extract_failed(paper["id"], f"api: {e}")
                    recorder.extract_timing(paper["id"], time.time() - _t0)
                return paper
            continue

        summary = data.get("summary", {})
        effect = summary.get("effect", "")

        # Anti-fabrication guard: when abstract is missing, any numbers in the
        # 4 segments are treated as hallucination → force [信息不足] sanitization.
        if looks_fabricated_when_missing(summary, abstract_source):
            log.warning("Suspected fabrication for %s (abstract=missing but numbers in output); "
                        "sanitizing to [信息不足]", paper["id"])
            for k in ("background", "core", "effect", "insight"):
                seg = summary.get(k, "") or ""
                if k == "effect":
                    summary[k] = "[信息不足，abstract 未获取] 标题未给出量化信息，请阅读原文"
                else:
                    if not seg.startswith("[信息不足"):
                        summary[k] = "[信息不足] " + (seg or "abstract 未获取，仅可从标题层面推断")
            data["summary"] = summary
            paper["summary"] = summary
            paper["summary"]["effect_quantified"] = False
            paper["tags"] = data.get("tags", {})
            paper["tag_notes"] = data.get("tag_notes", {})
            paper["tag_notes"]["effect_source"] = "missing"
            return paper

        if is_effect_quantified(effect):
            paper["summary"] = summary
            paper["summary"]["effect_quantified"] = (
                "[未量化]" not in effect and "[信息不足]" not in effect
            )
            paper["tags"] = data.get("tags", {})
            paper["tag_notes"] = data.get("tag_notes", {})
            if recorder is not None:
                recorder.extract_timing(paper["id"], time.time() - _t0)
            return paper

        if attempt == 1:
            log.info("Effect not quantified for %s, retrying with stronger nudge",
                     paper["id"])
            if recorder is not None:
                recorder.extract_retry(paper["id"], "effect_not_quantified")
            continue

        # After 2 attempts, force [未量化] prefix
        forced = "[未量化] " + effect
        summary["effect"] = forced
        paper["summary"] = summary
        paper["summary"]["effect_quantified"] = False
        paper["tags"] = data.get("tags", {})
        paper["tag_notes"] = data.get("tag_notes", {})
        if recorder is not None:
            recorder.extract_timing(paper["id"], time.time() - _t0)
        return paper

    return paper  # safety, unreachable


# LLM-curated external entries (lab / researcher / blog / rfc) come from
# Phase 1B.5 with a hand-crafted `relevance_reason` already. They aren't
# actual papers with abstracts, so sending them to Phase 3's 4-段量化 extract
# wastes tokens and produces `[抽取失败]` placeholders. We skip them and let
# the template render `relevance_reason` as a one-liner.
_CURATED_SUBTYPES = {"labs", "researchers", "blogs", "rfcs"}


def extract_all(papers: List[Dict], keywords: List[str], llm: LLMClient,
                include_yellow: bool = True,
                recorder: Optional[object] = None) -> List[Dict]:
    """Run extract_one for all green/yellow papers EXCEPT curated externals.

    Curated externals (Phase 1B.5 lab/researcher/blog/rfc) carry a useful
    `relevance_reason` instead of a paper abstract, so the renderer's
    "no-summary" branch handles them cleanly — Phase 3 would only burn
    tokens producing `[抽取失败]` placeholders.
    """
    target_levels = {"green", "yellow"} if include_yellow else {"green"}
    for p in papers:
        if p.get("relevance") not in target_levels:
            continue
        if p.get("source_subtype") in _CURATED_SUBTYPES:
            continue  # curated entries: relevance_reason is the summary
        if not p.get("abstract"):
            p["abstract"] = ""
        try:
            extract_one(p, keywords, llm, recorder=recorder)
        except Exception as e:
            log.error("extract_all error on %s: %s", p["id"], e)
            p["extract_error"] = str(e)
            if recorder is not None:
                recorder.extract_failed(p["id"], f"unhandled: {e}")
    return papers
