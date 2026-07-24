"""Phase 0.5 — LLM-driven keyword expansion (Plan A: always-on by default).

Takes the 6-10 core keywords from Phase 0 and expands them into a tiered
focus-areas structure (primary / secondary / tertiary, each with 5-10 keyword
variants), an exclude list, and a recommended set of arxiv_categories. The
output drives Phase 1B arXiv search keyword set and category selection.

Disable with `--no-expand-keywords` on the CLI; Phase 1B will then use just
the Phase 0 keywords with a broad default arxiv-categories set.

Output is cached to `intermediate/phase0.5-focus-areas.json` + a human-readable
`phase0.5-focus-areas.md` inside the archive — so `--resume` reuses the
expansion without re-spending tokens.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from scripts.utils import relaxed_json_loads

log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "focus-areas-gen.txt"

_DEFAULT = {
    "primary": [],
    "secondary": [],
    "tertiary": [],
    "exclude": [],
    "arxiv_categories": [],
    "scoring_dimensions": ["直接相关性", "工程价值", "创新度", "影响力", "实用性"],
}


def generate_via_llm(direction_raw: str,
                      phase0_keywords: List[str],
                      conference_hits: List[str],
                      llm) -> Dict:
    """Call the strong-model LLM to expand keywords into focus-areas.

    Args:
        direction_raw: user direction phrase as typed
        phase0_keywords: the 6-10 core keywords Phase 0 produced
        conference_hits: conference names (for prompt context, can be empty)
        llm: LLMClient-like with `.call(prompt, model, json_mode)`.

    Returns:
        dict with keys: primary, secondary, tertiary, exclude,
        arxiv_categories, scoring_dimensions.

    Robust to malformed JSON via relaxed_json_loads. Raises ValueError on
    unrecoverable parse failure (caller should catch and fall back).
    """
    prompt = (PROMPT_PATH.read_text()
              .replace("{direction_raw}", direction_raw)
              .replace("{phase0_keywords}",
                       json.dumps(phase0_keywords, ensure_ascii=False))
              .replace("{conference_hits}",
                       json.dumps(conference_hits, ensure_ascii=False)))
    resp, _ = llm.call(prompt, model="strong", max_tokens=2500, json_mode=True)
    try:
        data = relaxed_json_loads(resp)
    except json.JSONDecodeError as e:
        raise ValueError(f"focus-areas LLM returned unparseable JSON: {e}") from e
    # Merge with defaults so callers get a known shape
    out = {**_DEFAULT, **data}
    # Coerce common sloppy types
    for level in ("primary", "secondary", "tertiary"):
        out[level] = out.get(level) or []
    out["exclude"] = list(out.get("exclude") or [])
    out["arxiv_categories"] = list(out.get("arxiv_categories") or [])
    return out


def flatten_keywords(focus: Dict) -> List[str]:
    """Return all primary + secondary + tertiary keywords as a deduped flat list."""
    kws: List[str] = []
    for level in ("primary", "secondary", "tertiary"):
        for group in focus.get(level, []) or []:
            kws.extend(group.get("keywords", []) or [])
    seen, out = set(), []
    for k in kws:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def merge_into_synonym_map(focus: Dict,
                            base_synonym_map: Optional[Dict[str, List[str]]] = None
                            ) -> Dict[str, List[str]]:
    """Convert focus-areas groups into a synonym_map shape compatible with
    a generic synonym_map shape. Each group becomes one synonym_map entry
    keyed by the FIRST keyword of the group. If `base_synonym_map` is given,
    focus-areas wins on key collisions.

    Plan A no longer uses synonym_map at runtime (Phase 1B passes the
    flattened keyword list directly), so this function is kept only for
    backwards-compatible callers and tests.
    """
    out: Dict[str, List[str]] = dict(base_synonym_map or {})
    for level in ("primary", "secondary", "tertiary"):
        for group in focus.get(level, []) or []:
            kws = group.get("keywords") or []
            if not kws:
                continue
            key = kws[0].lower()
            out[key] = kws
    return out


def to_markdown(focus: Dict, direction_raw: str,
                phase0_keywords: List[str]) -> str:
    """Render focus-areas dict into a human-readable markdown summary."""
    lines: List[str] = []
    lines.append(f"# Focus Areas — {direction_raw}")
    lines.append("")
    lines.append("> 由 paper-digest Phase 0.5 自动扩展（基于 direction + Phase 0 关键词）。")
    lines.append(f"> Phase 0 核心关键词: {', '.join(phase0_keywords)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    sections = [
        ("primary", "🎯 一级方向（核心关注 → 🟢 强相关）"),
        ("secondary", "🔧 二级方向（紧密相关 → 🟡 中相关）"),
        ("tertiary", "📚 三级方向（外围参考）"),
    ]
    for key, title in sections:
        groups = focus.get(key) or []
        if not groups:
            continue
        lines.append(f"## {title}")
        lines.append("")
        for i, group in enumerate(groups, 1):
            lines.append(f"### {i}. {group.get('name', '(未命名)')}")
            for kw in group.get("keywords") or []:
                lines.append(f"- `{kw}`")
            lines.append("")
        lines.append("---")
        lines.append("")

    if focus.get("arxiv_categories"):
        lines.append("## 🗂️ arXiv 类目")
        lines.append("")
        lines.append(", ".join(f"`{c}`" for c in focus["arxiv_categories"]))
        lines.append("")
        lines.append("---")
        lines.append("")

    if focus.get("exclude"):
        lines.append("## ❌ 不重点关注")
        lines.append("")
        for e in focus["exclude"]:
            lines.append(f"- {e}")
        lines.append("")

    return "\n".join(lines) + "\n"
