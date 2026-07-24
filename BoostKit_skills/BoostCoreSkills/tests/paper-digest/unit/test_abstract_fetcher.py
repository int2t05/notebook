"""Unit tests for scripts.abstract_fetcher — verifies the USENIX scraper
captures every <p> in a multi-paragraph abstract, and that the doi/title
priority chain doesn't drop early-bailout cases.
"""
from unittest.mock import patch

import pytest

from scripts.abstract_fetcher import fetch_abstract, _fetch_usenix


# Real-world shape: USENIX puts the abstract inside a nested div, often with
# 2-3 <p> tags. Earlier regex only captured the first <p>, so quantitative
# effects in later paragraphs (e.g., "reduces latency by 95%") were lost.
# Real USENIX HTML packs the inner divs without whitespace; we keep test
# fixtures close to that shape and end the description block with the next
# field-name- sibling so the lookahead boundary is exercised.
USENIX_MULTI_P_HTML = (
    '<div class="field field-name-field-paper-description field-type-text-long field-label-hidden">'
    '<div class="field-items field-items"><div class="field-item odd">'
    '<p>RDMA-enabled memory disaggregation reduces memory costs in data centers. '
    'Existing systems use coarse-grained allocations, leading to memory waste.</p>'
    '<p>We introduce FineMem, an RDMA-connected remote memory management system. '
    'We show that FineMem reduces remote memory allocation latency by as much as 95% '
    'compared to state-of-the-art remote memory management systems.</p>'
    '</div></div></div>'
    '<div class="field field-name-field-paper-people-text">authors here</div>'
)

USENIX_SINGLE_P_HTML = (
    '<div class="field field-name-field-paper-description">'
    '<div class="field-items"><div class="field-item odd">'
    '<p>Tiered memory systems often rely on hotness for placement decisions, but '
    'SOAR and ALTO outperform state-of-the-art designs by up to 12.4x.</p>'
    '</div></div></div>'
    '<div class="field field-name-next">x</div>'
)

USENIX_AUTHOR_BIO_ONLY = (
    '<div class="field field-name-field-paper-description">'
    '<div class="field-items"><div class="field-item odd">'
    '<p>Bob Smith</p>'
    '</div></div></div>'
    '<div class="field field-name-next">x</div>'
)


@patch("scripts.abstract_fetcher._http_get")
def test_usenix_multi_paragraph_captures_all_paragraphs(mock_get):
    """Multi-paragraph USENIX abstract must include effect numbers from later <p>."""
    mock_get.return_value = USENIX_MULTI_P_HTML
    txt = _fetch_usenix("https://www.usenix.org/conference/osdi25/presentation/x")
    assert txt is not None
    # Both paragraphs must be present
    assert "RDMA-enabled memory disaggregation" in txt
    assert "95%" in txt
    # Paragraphs are separated by double newline
    assert "\n\n" in txt


@patch("scripts.abstract_fetcher._http_get")
def test_usenix_single_paragraph_still_works(mock_get):
    mock_get.return_value = USENIX_SINGLE_P_HTML
    txt = _fetch_usenix("https://www.usenix.org/conference/osdi25/presentation/y")
    assert txt is not None
    assert "12.4x" in txt
    # No double newline because only one paragraph
    assert "\n\n" not in txt


@patch("scripts.abstract_fetcher._http_get")
def test_usenix_rejects_short_author_bio(mock_get):
    """Author-bio-only blocks are too short to be real abstracts; reject."""
    mock_get.return_value = USENIX_AUTHOR_BIO_ONLY
    assert _fetch_usenix("https://www.usenix.org/conference/osdi25/presentation/z") is None


@patch("scripts.abstract_fetcher._http_get")
def test_usenix_returns_none_when_no_description_block(mock_get):
    mock_get.return_value = "<html><body>nothing here</body></html>"
    assert _fetch_usenix("https://www.usenix.org/conference/osdi25/presentation/w") is None


def test_non_usenix_url_skips_scrape():
    """fetch_abstract should not attempt USENIX scrape on non-USENIX URLs."""
    p = {"pdf": "https://doi.org/10.1145/123.456", "doi": "10.1145/123.456", "title": "X"}
    with patch("scripts.abstract_fetcher._fetch_usenix") as mock_usenix, \
         patch("scripts.abstract_fetcher._fetch_semantic_scholar_by_doi") as mock_s2_doi, \
         patch("scripts.abstract_fetcher._fetch_semantic_scholar_by_title") as mock_s2_title:
        mock_usenix.return_value = None  # would be skipped anyway
        mock_s2_doi.return_value = "An abstract long enough to count" + "." * 80
        mock_s2_title.return_value = None
        txt, src = fetch_abstract(p)
        assert src == "semantic_scholar_doi"
        mock_usenix.assert_not_called()


def test_already_populated_abstract_passes_through():
    """If paper already has a 'real' abstract (e.g. arXiv), don't refetch."""
    p = {"abstract": "Long enough arxiv abstract " * 5, "title": "X", "pdf": ""}
    txt, src = fetch_abstract(p)
    assert "arxiv abstract" in txt
    assert src == "arxiv"  # default when abstract_source not set
