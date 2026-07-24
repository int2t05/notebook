"""End-to-end smoke test: full pipeline with all I/O mocked."""
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def fake_llm():
    """LLM stub that returns canned JSON per stage.

    Phase ordering (Plan A — Phase 0.5 always-on, Phase 1B.5 LLM curate):
      0   parse input
      0.5 focus-areas expansion
      1A.1 conference proposal
      1B.5 external sources curate
      2   classify
      3 x2 extract per green/yellow paper
    """
    llm = MagicMock()
    responses = iter([
        # Phase 0: input parse
        ('{"keywords":["memory","allocator","CXL"],"exclude":["blockchain"]}', 200),
        # Phase 0.5: focus-areas expansion
        ('{"primary":[{"name":"memory","keywords":["memory","allocator","CXL"]}],'
         '"secondary":[],"tertiary":[],"exclude":[],'
         '"arxiv_categories":["cs.OS"]}', 400),
        # Phase 1A.1: LLM proposes ISMM-2025 (DBLP will confirm via mock)
        ('{"ranked":[{"name":"ISMM","year":2025,"direction_score":9.5,'
         '"expected_month":6,"rationale":"memory venue"}]}', 300),
        # Phase 1B.5: curate external sources
        ('{"labs":[],"researchers":[],"blogs":[],"rfcs":[]}', 200),
        # Phase 2: classify (1 batch of 2 papers)
        ('{"results":['
         '{"id":"C-ISMM-2025-001","relevance":"green","reason":"hit"},'
         '{"id":"X-arxiv-001","relevance":"green","reason":"hit"}'
         ']}', 200),
        # Phase 3: extract paper 1
        ('{"summary":{"background":"bg","core":"co","effect":"提升 69%","insight":"in"},'
         '"tags":{"industry":"hybrid","opensource":"no","deployability":"high"},'
         '"tag_notes":{}}', 600),
        # Phase 3: extract paper 2
        ('{"summary":{"background":"bg2","core":"co2","effect":"减少 30%","insight":"in2"},'
         '"tags":{"industry":"academic","opensource":"yes","deployability":"medium"},'
         '"tag_notes":{}}', 600),
    ])
    llm.call.side_effect = lambda *a, **kw: next(responses)
    llm.tokens_used = 0
    return llm


def test_full_pipeline_with_mocks(tmp_path, fake_llm, monkeypatch):
    """Run full pipeline; verify archive structure + key file contents.

    With the Phase 1A rewrite, conference candidates are sourced from
    `references/conferences-metadata.yaml`. We don't mock the old
    fetch_ccf_list / fetch_scholar_metrics shims — the metadata path covers
    discovery deterministically — but we still mock fetch_program and
    arxiv_query to avoid live network.
    """
    monkeypatch.setattr("scripts.conference_discoverer.fetch_program",
                        lambda name, year: [{
                            "id": f"C-{name}-{year}-001",
                            "source_type": "conference",
                            "conference": name, "year": year,
                            "title": "EMD: Fair THP De-bloating",
                            "authors": ["A"], "affiliation": "Fujitsu",
                            "pdf": "https://example.com/emd.pdf",
                            "doi": None, "date": "2025-06-17",
                            # Long enough (>80 chars) abstract to satisfy
                            # the fetcher pass-through; the no-fabrication
                            # guard in extractor only kicks in when abstract
                            # is genuinely missing.
                            "abstract": ("EMD fairly de-bloats transparent huge pages by "
                                         "tracking allocation-time pressure and reclaiming "
                                         "pages with 69% lower latency."),
                            "abstract_source": "test_fixture",
                        }])
    # Mock arXiv (Plan A signature: keywords, start, end, categories=None, max_results=..., recorder=None)
    monkeypatch.setattr("scripts.external_discoverer.arxiv_query",
                        lambda kw, sd, ed, categories=None, max_results=50, recorder=None: [{
                            "id": "X-arxiv-001",
                            "source_type": "external",
                            "source_subtype": "arxiv",
                            "title": "MIKU: CXL Tiering",
                            "authors": ["B"], "affiliation": "MIT",
                            "pdf": "https://arxiv.org/abs/x",
                            "doi": None, "date": "2025-03-15",
                            "abstract": ("MIKU does adaptive CXL tiering with hotness profiling "
                                         "and lightweight migration, achieving 30% lower tail latency."),
                            "abstract_source": "arxiv",
                        }])
    # Skip real abstract fetching (would hit live USENIX / Semantic Scholar APIs)
    monkeypatch.setattr("scripts.run.fetch_all_abstracts",
                        lambda papers, only_relevance=None: {"test_fixture": len(papers)})
    # Mock LLM build
    monkeypatch.setattr("scripts.run.build_llm",
                         lambda cfg, mb, backend="auto": fake_llm)
    monkeypatch.setenv("PAPER_DIGEST_LLM_API_KEY", "fake")

    # Invoke main via direct call (avoids subprocess for simpler debug)
    import sys
    from scripts.run import main
    # Use a 1-day window covering exactly ISMM-2025's date (2025-06-17), so
    # the metadata candidate list collapses to one conference — keeps the
    # canned LLM responses minimal and the assertions deterministic.
    sys.argv = ["run.py", "--direction", "memory allocator and CXL",
                "--window", "2025-06-17..2025-06-17",
                "--output-dir", str(tmp_path)]
    main()

    # Find created archive
    archives = list(tmp_path.glob("*"))
    assert len(archives) == 1, f"Expected 1 archive, got {archives}"
    archive = archives[0]

    # Assert structure
    assert (archive / "manifest.json").exists()
    assert (archive / "overview.md").exists()
    assert (archive / "conferences" / "ISMM-2025.md").exists()
    assert (archive / "external-sources.md").exists()
    assert (archive / "intermediate" / "phase3-detailed.json").exists()

    # Assert content
    overview = (archive / "overview.md").read_text()
    assert "ISMM" in overview
    assert "memory allocator and CXL" in overview

    conf_md = (archive / "conferences" / "ISMM-2025.md").read_text()
    assert "EMD" in conf_md
    assert "提升 69%" in conf_md  # quantified effect rendered

    # Assert quantification was preserved
    detailed = json.loads((archive / "intermediate" / "phase3-detailed.json").read_text())
    emd = next(p for p in detailed["papers"] if p["id"] == "C-ISMM-2025-001")
    assert emd["summary"]["effect_quantified"] is True
