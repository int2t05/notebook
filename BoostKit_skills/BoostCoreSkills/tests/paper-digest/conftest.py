import json
import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def stub_llm_responses():
    """Loader for canned LLM responses keyed by prompt hash."""
    def _load(prompt_hash: str) -> dict:
        path = FIXTURES_DIR / "llm-responses" / f"{prompt_hash}.json"
        with open(path) as f:
            return json.load(f)
    return _load


@pytest.fixture
def tmp_archive(tmp_path):
    """Provides a temporary archive directory."""
    archive = tmp_path / "test_archive"
    archive.mkdir()
    (archive / "conferences").mkdir()
    return archive


@pytest.fixture
def sample_papers():
    """A 3-paper sample (conf + arxiv) for testing classifier/extractor."""
    return [
        {
            "id": "C-ISMM-2025-001",
            "source_type": "conference",
            "conference": "ISMM",
            "year": 2025,
            "title": "EMD: Fair THP De-bloating",
            "authors": ["A", "B"],
            "affiliation": "Fujitsu",
            "pdf": "https://example.com/emd.pdf",
            "doi": "10.1145/x.y",
            "date": "2025-06-17",
        },
        {
            "id": "X-arxiv-001",
            "source_type": "external",
            "source_subtype": "arxiv",
            "title": "Memory Tiering for CXL",
            "authors": ["C"],
            "affiliation": "MIT",
            "pdf": "https://arxiv.org/abs/2503.17864",
            "date": "2025-03-15",
        },
    ]
