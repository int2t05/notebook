"""Phase 1B tests — arXiv 1B.1 + LLM-curated 1B.5 (Plan A)."""
from unittest.mock import patch, MagicMock

from scripts.external_discoverer import (
    arxiv_query, curate_external_via_llm, _to_paper_shape, discover_external,
)


# === Phase 1B.1: arXiv search ===

def test_arxiv_query_parses_atom_entries():
    fake_xml = """<?xml version="1.0"?>
<feed>
<entry>
<id>http://arxiv.org/abs/2503.17864v1</id>
<title>MIKU: CXL Tiering</title>
<published>2025-03-15T00:00:00Z</published>
<author><name>Alice</name></author>
<author><name>Bob</name></author>
<summary>This paper presents MIKU, a system for tiered memory.</summary>
</entry>
</feed>"""
    with patch("scripts.external_discoverer._http_get", return_value=fake_xml):
        papers = arxiv_query(["memory"], "2025-01-01", "2026-01-01",
                              categories=["cs.OS"], max_results=10)
    assert len(papers) == 1
    assert papers[0]["title"] == "MIKU: CXL Tiering"
    assert papers[0]["authors"] == ["Alice", "Bob"]
    assert papers[0]["source_subtype"] == "arxiv"


def test_arxiv_query_filters_outside_window():
    fake_xml = """<?xml version="1.0"?>
<feed>
<entry>
<id>http://arxiv.org/abs/2401.00001</id>
<title>Old Paper</title>
<published>2024-01-01T00:00:00Z</published>
<author><name>X</name></author>
<summary>Old.</summary>
</entry>
</feed>"""
    with patch("scripts.external_discoverer._http_get", return_value=fake_xml):
        papers = arxiv_query(["x"], "2025-01-01", "2026-01-01",
                              categories=["cs.OS"], max_results=10)
    assert papers == []


def test_arxiv_query_uses_default_categories_when_none_passed():
    """When Phase 0.5 didn't supply arxiv_categories, the default broad set
    (cs.OS / cs.PL / cs.AR / cs.DC / cs.PF / cs.SE / cs.CR / cs.LG / cs.DB)
    is used so any direction still gets a search."""
    captured = {}
    def fake_get(url, timeout=30):
        captured["url"] = url
        return '<feed></feed>'
    with patch("scripts.external_discoverer._http_get", side_effect=fake_get):
        arxiv_query(["memory"], "2025-01-01", "2026-01-01",
                     categories=None, max_results=10)
    # default categories include cs.CR (security) so non-memory directions covered
    assert "cs.CR" in captured["url"] or "cs.OS" in captured["url"]


# === Phase 1B.5: LLM curated ===

_CURATE_RESPONSE = """{
  "labs": [
    {"title": "mimalloc roadmap", "url": "https://github.com/microsoft/mimalloc",
     "source": "Microsoft Research", "date": "2025",
     "relevance": "green", "relevance_reason": "core allocator reference"}
  ],
  "researchers": [
    {"title": "Jason Evans postmortem", "url": "https://jasone.github.io/2025/06/12/jemalloc-postmortem/",
     "source": "Jason Evans", "date": "2025-06",
     "relevance": "green", "relevance_reason": "jemalloc maintainer reflection"}
  ],
  "blogs": [],
  "rfcs": []
}"""


def test_curate_external_via_llm_parses_sections():
    llm = MagicMock()
    llm.call.return_value = (_CURATE_RESPONSE, 500)
    out = curate_external_via_llm("memory allocator", ["memory"],
                                   "2025-01-01", "2025-12-31", llm)
    assert len(out["labs"]) == 1 and out["labs"][0]["title"] == "mimalloc roadmap"
    assert len(out["researchers"]) == 1
    assert out["blogs"] == [] and out["rfcs"] == []


def test_curate_external_returns_empty_on_llm_none():
    out = curate_external_via_llm("x", ["y"], "2025-01-01", "2025-12-31", None)
    assert out == {"labs": [], "researchers": [], "blogs": [], "rfcs": []}


def test_curate_external_returns_empty_on_garbage_json():
    llm = MagicMock()
    llm.call.return_value = ("totally not json {{{", 100)
    out = curate_external_via_llm("x", ["y"], "2025-01-01", "2025-12-31", llm)
    assert out == {"labs": [], "researchers": [], "blogs": [], "rfcs": []}


# === paper-shape conversion ===

def test_to_paper_shape_minimum_fields():
    out = _to_paper_shape(
        [{"title": "foo", "url": "https://x", "source": "Y",
          "date": "2025", "relevance": "green"}],
        "labs", "X-lab")
    assert len(out) == 1
    p = out[0]
    assert p["id"] == "X-lab-001"
    assert p["source_type"] == "external"
    assert p["source_subtype"] == "labs"
    assert p["relevance"] == "green"


def test_to_paper_shape_drops_titleless_entries():
    out = _to_paper_shape(
        [{"url": "https://x"}, {"title": "y", "url": "https://y"}],
        "labs", "X-lab")
    assert len(out) == 1
    assert out[0]["title"] == "y"


# === discover_external integration ===

def test_discover_external_combines_arxiv_and_curate():
    """End-to-end: arXiv search + LLM curate are both invoked and dict-merged."""
    arxiv_xml = """<?xml version="1.0"?>
<feed><entry>
<id>http://arxiv.org/abs/2503.17864v1</id>
<title>A Paper</title>
<published>2025-03-15T00:00:00Z</published>
<author><name>X</name></author>
<summary>An abstract long enough.</summary>
</entry></feed>"""
    llm = MagicMock()
    llm.call.return_value = (_CURATE_RESPONSE, 500)
    with patch("scripts.external_discoverer._http_get", return_value=arxiv_xml):
        result = discover_external(["memory"], "2025-01-01", "2025-12-31",
                                    direction_raw="memory allocator",
                                    arxiv_categories=["cs.OS"], llm=llm)
    assert len(result["arxiv"]) == 1
    assert len(result["lab"]) == 1
    assert len(result["researcher"]) == 1
    assert result["blog"] == []
