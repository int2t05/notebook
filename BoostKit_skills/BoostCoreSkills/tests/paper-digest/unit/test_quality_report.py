"""Tests for QualityRecorder + post-mortem log parser."""
from pathlib import Path

from scripts.quality_report import QualityRecorder, parse_log


def test_recorder_aggregates_per_paper_events():
    r = QualityRecorder()
    r.json_parse_failure("phase3", "C-X-001", 1, "bad delimiter")
    r.json_parse_failure("phase3", "C-X-001", 2, "still bad")
    r.extract_failed("C-X-001", "json_parse: still bad")
    r.extract_timing("C-X-001", 75.3)
    r.extract_retry("C-X-002", "effect_not_quantified")
    r.extract_timing("C-X-002", 35.0)

    rep = r.to_report()
    assert rep["total_events"] == 6
    assert "C-X-001" in rep["phase3"]["failed_papers"]
    assert "C-X-001" in rep["phase3"]["papers_with_json_failures"]
    assert "C-X-002" in rep["phase3"]["papers_with_retries"]
    # 75.3s exceeds slow threshold; 35.0s does not
    slow_ids = [s["id"] for s in rep["phase3"]["slow_papers"]]
    assert slow_ids == ["C-X-001"]


def test_recorder_phase2_batch_failure():
    r = QualityRecorder()
    r.classify_batch_failed(25, ["P-1", "P-2"], "json broken")
    rep = r.to_report()
    assert rep["phase2"]["batch_failures"] == 1
    assert rep["phase2"]["papers_lost_to_batch_failure"] == ["P-1", "P-2"]


def test_recorder_phase1a_dblp_reject():
    r = QualityRecorder()
    r.dblp_rejected("FAKE-VENUE", 2099, "dblp_empty")
    rep = r.to_report()
    assert rep["phase1a"]["dblp_rejected"] == [
        {"name": "FAKE-VENUE", "year": 2099, "reason": "dblp_empty"}]


def test_recorder_phase1b_curate_failed():
    r = QualityRecorder()
    r.curate_failed("api timeout")
    rep = r.to_report()
    assert rep["phase1b"]["curate_failed"] is True


def test_write_report_emits_md_and_json(tmp_path):
    r = QualityRecorder()
    r.json_parse_failure("phase3", "C-X-001", 1, "bad")
    r.extract_failed("C-X-001", "bad json")
    r.extract_timing("C-X-001", 90)
    r.write_report(tmp_path)
    assert (tmp_path / "quality-report.md").exists()
    assert (tmp_path / "intermediate" / "quality-events.json").exists()
    md = (tmp_path / "quality-report.md").read_text()
    assert "C-X-001" in md
    assert "抽取失败" in md


def test_parse_log_extracts_json_parse_failures(tmp_path):
    log = tmp_path / "run.log"
    log.write_text(
        "2026-05-24 14:08:14,782 [WARNING] extract_one attempt 1 JSON parse failed "
        "for C-ISMM-2025-008: Expecting ',' delimiter\n"
        "2026-05-24 14:08:37,632 [WARNING] extract_one attempt 2 JSON parse failed "
        "for C-ISMM-2025-008: still bad\n"
        "2026-05-24 14:30:00,000 [INFO] Effect not quantified for X-arxiv-013, "
        "retrying with stronger nudge\n"
        "2026-05-24 14:31:00,000 [INFO] Phase 1A.2: dropped LLM candidate FAKE 2099 "
        "(dblp_empty)\n"
    )
    rec = parse_log(log)
    rep = rec.to_report()
    assert rep["events_by_kind"].get("phase3.json_parse_failure") == 2
    assert rep["events_by_kind"].get("phase3.extract_retry") == 1
    assert rep["events_by_kind"].get("phase1a.dblp_rejected") == 1
    assert "C-ISMM-2025-008" in rep["phase3"]["papers_with_json_failures"]
    assert "X-arxiv-013" in rep["phase3"]["papers_with_retries"]
