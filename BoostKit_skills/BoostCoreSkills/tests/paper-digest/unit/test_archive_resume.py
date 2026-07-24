from pathlib import Path

from scripts.utils import Archive


def _new_archive(tmp_path: Path) -> Archive:
    return Archive.new(
        base_dir=tmp_path,
        slug="mem-opt",
        window_label="1y",
        date_label="2026-05-23",
        start_date="2025-05-23",
        end_date="2026-05-23",
        include_date_label=False,
        manifest={"input": {"direction_raw": "memory"}},
    )


def test_new_archive_uses_start_end_dirname(tmp_path):
    a = _new_archive(tmp_path)
    assert a.path.name == "mem-opt_2025-05-23_2026-05-23"
    assert (a.path / "manifest.json").exists()
    assert (a.path / "conferences").is_dir()


def test_new_archive_with_date_label_appends_run_suffix(tmp_path):
    a = Archive.new(
        base_dir=tmp_path, slug="mem-opt", window_label="1y",
        date_label="2026-05-23",
        start_date="2025-05-23", end_date="2026-05-23",
        include_date_label=True,
        manifest={"input": {}},
    )
    assert a.path.name == "mem-opt_2025-05-23_2026-05-23_run-2026-05-23"


def test_resume_returns_none_when_missing(tmp_path):
    res = Archive.resume(
        base_dir=tmp_path, slug="mem-opt", window_label="1y",
        start_date="2025-05-23", end_date="2026-05-23",
    )
    assert res is None


def test_resume_finds_existing_archive(tmp_path):
    a = _new_archive(tmp_path)
    a.mark_phase_done("phase0", tokens_used=42)
    a.mark_phase_done("phase1", tokens_used=100)

    res = Archive.resume(
        base_dir=tmp_path, slug="mem-opt", window_label="1y",
        start_date="2025-05-23", end_date="2026-05-23",
    )
    assert res is not None
    assert res.path == a.path
    assert res.phases_done() == ["phase0", "phase1"]


def test_resume_tolerates_slug_drift(tmp_path):
    """Phase 0 LLM may produce a different slug on retry; resume should still
    find the previous archive in the same window by globbing on date range."""
    a = _new_archive(tmp_path)  # slug = "mem-opt"
    a.mark_phase_done("phase0")

    # Try resuming with a totally different slug; window is the same.
    res = Archive.resume(
        base_dir=tmp_path,
        slug="completely-different-slug",  # mimics LLM drift
        window_label="1y",
        start_date="2025-05-23",
        end_date="2026-05-23",
    )
    assert res is not None
    assert res.path == a.path
