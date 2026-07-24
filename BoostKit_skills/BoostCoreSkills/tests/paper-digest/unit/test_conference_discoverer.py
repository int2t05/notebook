"""Phase 1A tests — LLM proposes, DBLP verifies, metadata enriches (Plan A)."""
from unittest.mock import patch, MagicMock

from scripts.conference_discoverer import (
    discover_conferences, llm_propose_candidates, verify_via_dblp,
    _composite_score, score_to_emoji,
)


# === Phase 1A.1: LLM-driven proposal ===

def test_llm_propose_candidates_parses_ranked_json():
    llm = MagicMock()
    llm.call.return_value = ('{"ranked":[{"name":"ISMM","year":2025,'
                              '"direction_score":9.5,"expected_month":6,'
                              '"rationale":"memory venue"},'
                              '{"name":"OSDI","year":2025,"direction_score":8,'
                              '"expected_month":7,"rationale":"OS top venue"}]}',
                              500)
    out = llm_propose_candidates("memory allocator", ["memory"],
                                  "2025-01-01", "2025-12-31", 10, llm)
    names = [c["name"] for c in out]
    assert "ISMM" in names and "OSDI" in names
    assert out[0]["direction_score"] == 9.5


def test_llm_propose_candidates_dedupes_same_name_year():
    llm = MagicMock()
    llm.call.return_value = ('{"ranked":[{"name":"ISMM","year":2025,"direction_score":9},'
                              '{"name":"ISMM","year":2025,"direction_score":8}]}', 100)
    out = llm_propose_candidates("x", ["y"], "2025-01-01", "2025-12-31", 10, llm)
    assert len(out) == 1


def test_llm_propose_candidates_returns_empty_on_error():
    llm = MagicMock()
    llm.call.side_effect = RuntimeError("api down")
    out = llm_propose_candidates("x", ["y"], "2025-01-01", "2025-12-31", 10, llm)
    assert out == []


def test_llm_propose_skipped_when_llm_is_none():
    out = llm_propose_candidates("x", ["y"], "2025-01-01", "2025-12-31", 10, None)
    assert out == []


# === Phase 1A.2: DBLP verification ===

def test_verify_via_dblp_ok_for_real_conference():
    with patch("scripts.conference_discoverer.fetch_program",
               return_value=[{"id": "C-X-2025-001", "title": "x"}]):
        ok, papers, reason = verify_via_dblp({"name": "ISMM", "year": 2025})
    assert ok and len(papers) == 1 and reason == "ok"


def test_verify_via_dblp_rejects_hallucinated():
    with patch("scripts.conference_discoverer.fetch_program", return_value=[]):
        ok, papers, reason = verify_via_dblp({"name": "FAKE-VENUE", "year": 2099})
    assert not ok and papers == [] and reason == "dblp_empty"


def test_verify_via_dblp_rejects_on_exception():
    with patch("scripts.conference_discoverer.fetch_program",
               side_effect=RuntimeError("404")):
        ok, _, reason = verify_via_dblp({"name": "FAKE", "year": 2099})
    assert not ok and "fetch_error" in reason


# === Phase 1A end-to-end (LLM proposal → DBLP → enrichment) ===

def test_discover_drops_hallucinated_keeps_real():
    """LLM proposes 2 conferences; DBLP confirms 1, rejects 1; only confirmed
    one survives, enriched with metadata."""
    llm = MagicMock()
    llm.call.return_value = ('{"ranked":[{"name":"ISMM","year":2025,"direction_score":9.5},'
                              '{"name":"COMPLETELY-FAKE-VENUE","year":2099,'
                              '"direction_score":7}]}', 200)

    def mock_fetch(name, year):
        if name == "ISMM" and year == 2025:
            return [{"id": "C-ISMM-2025-001", "title": "Real paper"}]
        return []

    with patch("scripts.conference_discoverer.fetch_program",
               side_effect=mock_fetch):
        result = discover_conferences(
            ["memory"], "2025-01-01", "2025-12-31",
            top_n=3, llm=llm, direction_raw="memory allocator",
            use_metadata_fallback=False,
        )
    names = [r["name"] for r in result]
    assert names == ["ISMM"]
    ismm = result[0]
    assert ismm["core"] == "A"      # from metadata.yaml
    assert ismm["h5"] == 25
    assert ismm["full_name"].startswith("ACM SIGPLAN")
    assert ismm["composite_score"] > 0
    assert ismm["direction_match"] == "🟢🟢🟢"  # score 9.5 → 🟢🟢🟢


def test_discover_falls_back_to_metadata_when_llm_none():
    with patch("scripts.conference_discoverer.fetch_program",
               return_value=[{"id": "C-ISMM-2025-001", "title": "x"}]):
        result = discover_conferences(
            ["memory"], "2025-06-17", "2025-06-17",
            top_n=3, llm=None, use_metadata_fallback=True,
        )
    names = {r["name"] for r in result}
    assert "ISMM" in names


# === Score → emoji + composite ===

def test_score_to_emoji_mapping():
    assert score_to_emoji(9.5) == "🟢🟢🟢"
    assert score_to_emoji(9.0) == "🟢🟢🟢"
    assert score_to_emoji(8.9) == "🟢🟢"
    assert score_to_emoji(7.0) == "🟢🟢"
    assert score_to_emoji(6.0) == "🟢"
    assert score_to_emoji(5.0) == "🟢"
    assert score_to_emoji(4.0) == "🟡"
    assert score_to_emoji(3.0) == "🟡"
    assert score_to_emoji(2.0) == ""
    assert score_to_emoji(0) == ""


def test_composite_score_combines_direction_ccf_h5():
    s = _composite_score(direction_score=9, ccf="A", core="A*", h5=60)
    # 9*0.6 + 10*0.3 + 5.0*0.1 = 5.4 + 3.0 + 0.5 = 8.9
    assert abs(s - 8.9) < 0.01
