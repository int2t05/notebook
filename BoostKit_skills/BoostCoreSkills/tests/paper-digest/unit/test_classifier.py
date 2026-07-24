from unittest.mock import MagicMock
from scripts.classifier import classify_batch, classify_all


def test_classify_batch_passes_results_back(sample_papers):
    llm = MagicMock()
    llm.call.return_value = (
        '{"results":['
        '{"id":"C-ISMM-2025-001","relevance":"green","reason":"hit"},'
        '{"id":"X-arxiv-001","relevance":"yellow","reason":"partial"}'
        ']}',
        300,
    )
    classified = classify_batch(sample_papers, keywords=["memory"],
                                exclude=["blockchain"], llm=llm)
    by_id = {p["id"]: p for p in classified}
    assert by_id["C-ISMM-2025-001"]["relevance"] == "green"
    assert by_id["X-arxiv-001"]["relevance"] == "yellow"


def test_classify_all_preflag_exclude_keywords():
    papers = [
        {"id": "A", "title": "Blockchain consensus protocol", "authors": [], "pdf": ""},
        {"id": "B", "title": "Memory allocator design", "authors": [], "pdf": ""},
    ]
    llm = MagicMock()
    llm.call.return_value = ('{"results":[{"id":"B","relevance":"green","reason":"x"}]}', 100)
    result = classify_all(papers, keywords=["memory"], exclude=["blockchain"], llm=llm,
                          batch_size=25)
    by_id = {p["id"]: p for p in result}
    # A pre-tagged red without LLM
    assert by_id["A"]["relevance"] == "red"
    assert "exclude_keyword_match" in by_id["A"]["relevance_reason"]
    # B classified by LLM as green
    assert by_id["B"]["relevance"] == "green"
