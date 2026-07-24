import json
import pytest
from unittest.mock import MagicMock, patch
from scripts.utils import LLMClient, BudgetExceeded, Archive


def test_llm_client_tracks_tokens():
    client = LLMClient(api_key="fake", max_budget=1000)
    with patch.object(client, "_raw_call", return_value=("hello", 100)):
        text, used = client.call("prompt", model="flash")
    assert text == "hello"
    assert client.tokens_used == 100


def test_llm_client_raises_when_budget_exceeded():
    client = LLMClient(api_key="fake", max_budget=50)
    with patch.object(client, "_raw_call", return_value=("hello", 100)):
        with pytest.raises(BudgetExceeded):
            client.call("prompt", model="flash")


def test_archive_new_creates_directory_with_manifest(tmp_path):
    archive = Archive.new(
        base_dir=tmp_path,
        slug="memory-allocator",
        window_label="6mo",
        date_label="2026-05-22",
        manifest={"input": {"direction_raw": "memory allocator"}},
    )
    assert archive.path.is_dir()
    assert (archive.path / "conferences").is_dir()
    manifest = json.loads((archive.path / "manifest.json").read_text())
    assert manifest["input"]["direction_raw"] == "memory allocator"
    assert "phases_completed" in manifest


def test_archive_mark_phase_done_updates_manifest(tmp_path):
    archive = Archive.new(
        base_dir=tmp_path,
        slug="x",
        window_label="3mo",
        date_label="2026-05-22",
        manifest={"input": {}},
    )
    archive.mark_phase_done("phase1a", tokens_used=1234)
    manifest = json.loads((archive.path / "manifest.json").read_text())
    assert {"phase": "phase1a", "tokens_used": 1234} in manifest["phases_completed"]


from unittest.mock import patch
from scripts.utils import fetch_program


def test_fetch_program_parses_dblp_response():
    fake_html = """
    <ul class="publ-list">
      <li class="entry inproceedings">
        <div class="data">
          <span itemprop="author"><span itemprop="name">Alice</span></span>
          <span class="title">EMD: Fair THP De-bloating</span>
          <span itemprop="datePublished">2025</span>
        </div>
        <nav>
          <ul>
            <li><div class="head">view</div><ul><li><a href="https://dl.acm.org/doi/10.1145/x">acm</a></li></ul></li>
          </ul>
        </nav>
      </li>
    </ul>
    """
    with patch("scripts.utils._http_get", return_value=fake_html):
        papers = fetch_program(conf_name="ISMM", year=2025)
    assert len(papers) == 1
    assert papers[0]["title"] == "EMD: Fair THP De-bloating"
    assert papers[0]["authors"] == ["Alice"]
    assert papers[0]["year"] == 2025
    assert papers[0]["pdf"].startswith("https://")
