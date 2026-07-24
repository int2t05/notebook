"""Quality recorder + report generator.

Captures per-phase warnings, retries, slow papers, and failed outcomes during
a pipeline run, so the user gets a post-run quality-report.md to identify:

  - Which papers hit JSON parse failures and how often
  - Which papers needed "Effect not quantified" retries
  - Which Phase 3 papers ended with [抽取失败] placeholders
  - Which Phase 2 batches failed wholesale
  - Which Phase 1A LLM candidates were rejected by DBLP
  - Which extractions took unusually long (> threshold seconds)

Two entry points:

1. **Live recording** during a run: `QualityRecorder` is created in `run.py`
   and threaded into each phase. Each phase calls `recorder.record(...)` at
   warning sites. At the end of the run, `recorder.write_report(archive_dir)`
   emits `intermediate/quality-events.json` + `quality-report.md`.

2. **Post-mortem log parsing** for runs that finished before instrumentation:
   `python -m scripts.quality_report <run_log> [<archive_dir>]` parses log
   lines into the same event shape and writes the same report files.
"""
import json
import re
import time
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any


# Threshold: any phase-3 extract beyond this is flagged as "slow" in the report.
SLOW_PAPER_THRESHOLD_S = 60


class QualityRecorder:
    """Append-only event log for a single pipeline run."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def record(self, phase: str, kind: str, **fields) -> None:
        self.events.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "kind": kind,
            **fields,
        })

    # --- Convenience emitters (callers don't have to remember kind strings) ---

    def json_parse_failure(self, phase: str, paper_id: str, attempt: int, error: str):
        self.record(phase, "json_parse_failure",
                    paper_id=paper_id, attempt=attempt, error=error)

    def extract_retry(self, paper_id: str, reason: str):
        self.record("phase3", "extract_retry",
                    paper_id=paper_id, reason=reason)

    def extract_failed(self, paper_id: str, reason: str):
        """Paper ended with [抽取失败] placeholder after all retries."""
        self.record("phase3", "extract_failed",
                    paper_id=paper_id, reason=reason)

    def extract_timing(self, paper_id: str, seconds: float):
        self.record("phase3", "extract_timing",
                    paper_id=paper_id, seconds=round(seconds, 1))

    def classify_batch_failed(self, batch_size: int, paper_ids: List[str], error: str):
        self.record("phase2", "classify_batch_failed",
                    batch_size=batch_size, paper_ids=paper_ids, error=error)

    def dblp_rejected(self, name: str, year: int, reason: str):
        self.record("phase1a", "dblp_rejected",
                    name=name, year=year, reason=reason)

    def arxiv_chunk_failed(self, chunk_index: int, error: str):
        self.record("phase1b", "arxiv_chunk_failed",
                    chunk_index=chunk_index, error=error)

    def curate_failed(self, error: str):
        self.record("phase1b", "curate_failed", error=error)

    # --- Report writing ---

    def to_report(self) -> Dict[str, Any]:
        """Aggregate events into a structured report dict."""
        by_kind: Dict[str, List[Dict]] = defaultdict(list)
        for e in self.events:
            by_kind[f"{e['phase']}.{e['kind']}"].append(e)

        # Per-paper rollup for Phase 3
        per_paper: Dict[str, Dict] = defaultdict(
            lambda: {"json_parse_failures": 0, "retries": 0,
                     "failed": False, "elapsed_s": None})
        for e in self.events:
            pid = e.get("paper_id")
            if not pid:
                continue
            if e["kind"] == "json_parse_failure":
                per_paper[pid]["json_parse_failures"] += 1
            elif e["kind"] == "extract_retry":
                per_paper[pid]["retries"] += 1
            elif e["kind"] == "extract_failed":
                per_paper[pid]["failed"] = True
                per_paper[pid]["fail_reason"] = e.get("reason", "")
            elif e["kind"] == "extract_timing":
                per_paper[pid]["elapsed_s"] = e.get("seconds")

        slow_papers = [(pid, info) for pid, info in per_paper.items()
                       if info["elapsed_s"] and info["elapsed_s"] >= SLOW_PAPER_THRESHOLD_S]
        slow_papers.sort(key=lambda kv: -kv[1]["elapsed_s"])

        failed_papers = [(pid, info) for pid, info in per_paper.items() if info["failed"]]

        return {
            "total_events": len(self.events),
            "events_by_kind": {k: len(v) for k, v in sorted(by_kind.items())},
            "phase3": {
                "total_papers_seen": len(per_paper),
                "failed_papers": [pid for pid, _ in failed_papers],
                "papers_with_retries": [pid for pid, info in per_paper.items()
                                         if info["retries"] > 0],
                "papers_with_json_failures": [
                    pid for pid, info in per_paper.items()
                    if info["json_parse_failures"] > 0],
                "slow_papers": [
                    {"id": pid, "seconds": info["elapsed_s"]}
                    for pid, info in slow_papers],
            },
            "phase2": {
                "batch_failures": len(by_kind.get("phase2.classify_batch_failed", [])),
                "papers_lost_to_batch_failure": [
                    pid for e in by_kind.get("phase2.classify_batch_failed", [])
                    for pid in e.get("paper_ids", [])],
            },
            "phase1a": {
                "dblp_rejected": [
                    {"name": e["name"], "year": e["year"], "reason": e["reason"]}
                    for e in by_kind.get("phase1a.dblp_rejected", [])],
            },
            "phase1b": {
                "arxiv_chunk_failures": [
                    e["chunk_index"]
                    for e in by_kind.get("phase1b.arxiv_chunk_failed", [])],
                "curate_failed": len(by_kind.get("phase1b.curate_failed", [])) > 0,
            },
            "raw_events": self.events,
        }

    def write_report(self, archive_dir: Path) -> None:
        report = self.to_report()
        intermediate = archive_dir / "intermediate"
        intermediate.mkdir(exist_ok=True)
        (intermediate / "quality-events.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False))
        (archive_dir / "quality-report.md").write_text(_render_markdown(report))


def _render_markdown(report: Dict[str, Any]) -> str:
    """Human-readable markdown summary."""
    lines: List[str] = ["# 运行质量报告", ""]
    lines.append(f"> 共记录 **{report['total_events']}** 个质量事件。事件类型分布：")
    lines.append("")
    if report["events_by_kind"]:
        lines.append("| 事件类型 | 计数 |")
        lines.append("|----------|------|")
        for k, n in report["events_by_kind"].items():
            lines.append(f"| `{k}` | {n} |")
        lines.append("")
    else:
        lines.append("✅ 无质量事件。")
        lines.append("")

    # Phase 3 detail
    p3 = report["phase3"]
    lines.append("## Phase 3 — 4 段量化抽取")
    lines.append(f"- 触达的论文数（含告警/重试/失败）: **{p3['total_papers_seen']}**")
    if p3["failed_papers"]:
        lines.append(f"- ❌ **`[抽取失败]`** 终态: {len(p3['failed_papers'])} 篇")
        lines.append("")
        lines.append("  | 论文 ID | |")
        lines.append("  |---------|---|")
        for pid in p3["failed_papers"][:50]:
            lines.append(f"  | `{pid}` | |")
        if len(p3["failed_papers"]) > 50:
            lines.append(f"  | ... +{len(p3['failed_papers']) - 50} 篇省略 | |")
        lines.append("")
    if p3["papers_with_json_failures"]:
        lines.append(f"- ⚠️ **JSON 解析失败**（被 relaxed_json_loads 救回的）: "
                     f"{len(p3['papers_with_json_failures'])} 篇")
    if p3["papers_with_retries"]:
        lines.append(f"- 🔁 **effect 未量化触发重试**: {len(p3['papers_with_retries'])} 篇")
    if p3["slow_papers"]:
        lines.append(f"- 🐢 **慢抽取**（≥ {SLOW_PAPER_THRESHOLD_S} s）: {len(p3['slow_papers'])} 篇")
        lines.append("")
        lines.append("  | 论文 ID | 耗时 (s) |")
        lines.append("  |---------|----------|")
        for r in p3["slow_papers"][:20]:
            lines.append(f"  | `{r['id']}` | {r['seconds']} |")
        if len(p3["slow_papers"]) > 20:
            lines.append(f"  | ... +{len(p3['slow_papers']) - 20} 篇省略 | |")
    lines.append("")

    # Phase 2 detail
    p2 = report["phase2"]
    lines.append("## Phase 2 — 粗分类")
    if p2["batch_failures"]:
        lines.append(f"- ❌ **整批失败**: {p2['batch_failures']} 批 "
                     f"（{len(p2['papers_lost_to_batch_failure'])} 篇被 mark unknown）")
    else:
        lines.append("- ✅ 所有批次解析成功")
    lines.append("")

    # Phase 1A detail
    p1a = report["phase1a"]
    lines.append("## Phase 1A — 会议候选 DBLP 验证")
    if p1a["dblp_rejected"]:
        lines.append(f"- 被 DBLP 丢弃的 LLM 候选: {len(p1a['dblp_rejected'])} 条")
        lines.append("")
        lines.append("  | 会议 | 年份 | 拒绝原因 |")
        lines.append("  |------|------|----------|")
        for r in p1a["dblp_rejected"][:30]:
            lines.append(f"  | {r['name']} | {r['year']} | {r['reason']} |")
        if len(p1a["dblp_rejected"]) > 30:
            lines.append(f"  | ... +{len(p1a['dblp_rejected']) - 30} 省略 | | |")
    else:
        lines.append("- ✅ 所有 LLM 候选都被 DBLP 确认")
    lines.append("")

    # Phase 1B detail
    p1b = report["phase1b"]
    lines.append("## Phase 1B — arXiv + LLM 外部源 curate")
    if p1b["arxiv_chunk_failures"]:
        lines.append(f"- ⚠️ arXiv 分块查询失败: chunks {p1b['arxiv_chunk_failures']}")
    if p1b["curate_failed"]:
        lines.append(f"- ⚠️ LLM curate 调用失败（external lab/researcher/blog/rfc 列表为空）")
    if not p1b["arxiv_chunk_failures"] and not p1b["curate_failed"]:
        lines.append("- ✅ arXiv 与 curate 均正常")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 完整事件序列见 `intermediate/quality-events.json`")
    return "\n".join(lines) + "\n"


# ============================================================
# Post-mortem log parser (for runs that finished before instrumentation)
# ============================================================

LOG_PATTERNS = [
    # extract_one attempt N JSON parse failed for <id>: <err>
    (re.compile(r"extract_one attempt (\d+) JSON parse failed for (\S+): (.+)"),
     lambda m, r: r.json_parse_failure("phase3", m.group(2), int(m.group(1)),
                                         m.group(3))),
    # extract_one attempt N API/runtime failed for <id>: <err>
    (re.compile(r"extract_one attempt (\d+) API/runtime failed for (\S+): (.+)"),
     lambda m, r: r.record("phase3", "extract_api_error",
                            paper_id=m.group(2), attempt=int(m.group(1)),
                            error=m.group(3))),
    # Effect not quantified for <id>, retrying with stronger nudge
    (re.compile(r"Effect not quantified for (\S+), retrying"),
     lambda m, r: r.extract_retry(m.group(1), "effect_not_quantified")),
    # Suspected fabrication for <id> (abstract=missing but numbers in output)
    (re.compile(r"Suspected fabrication for (\S+) "),
     lambda m, r: r.record("phase3", "fabrication_sanitized",
                            paper_id=m.group(1))),
    # extract_all error on <id>: <err>
    (re.compile(r"extract_all error on (\S+): (.+)"),
     lambda m, r: r.extract_failed(m.group(1), m.group(2))),
    # Phase 1A.2 dropped LLM candidate <NAME> <YEAR> (<reason>)
    (re.compile(r"Phase 1A\.2: dropped LLM candidate (\S+) (\d+) \(([^)]+)\)"),
     lambda m, r: r.dblp_rejected(m.group(1), int(m.group(2)), m.group(3))),
    # arXiv chunk N page M failed: <err>
    (re.compile(r"arXiv chunk (\d+) page \d+ failed:"),
     lambda m, r: r.arxiv_chunk_failed(int(m.group(1)), "")),
    # Phase 1B.5 curate LLM failed: <err>
    (re.compile(r"Phase 1B\.5 curate LLM failed: (.+)"),
     lambda m, r: r.curate_failed(m.group(1))),
    # classify_batch JSON parse failed: <err>
    (re.compile(r"classify_batch JSON parse failed: (.+)"),
     lambda m, r: r.record("phase2", "classify_batch_failed",
                            error=m.group(1), batch_size=0, paper_ids=[])),
]


def parse_log(log_path: Path) -> QualityRecorder:
    """Parse a paper-digest run log file into a QualityRecorder."""
    rec = QualityRecorder()
    text = log_path.read_text()
    for line in text.splitlines():
        for pattern, handler in LOG_PATTERNS:
            m = pattern.search(line)
            if m:
                try:
                    handler(m, rec)
                except Exception:
                    pass
                break
    return rec


def main():
    """CLI: python -m scripts.quality_report <log_path> [<archive_dir>]."""
    if len(sys.argv) < 2:
        print("usage: python -m scripts.quality_report <log_path> [<archive_dir>]",
              file=sys.stderr)
        sys.exit(2)
    log = Path(sys.argv[1])
    archive = Path(sys.argv[2]) if len(sys.argv) >= 3 else log.parent
    rec = parse_log(log)
    rec.write_report(archive)
    print(f"Wrote {archive / 'quality-report.md'}")
    print(f"Wrote {archive / 'intermediate' / 'quality-events.json'}")


if __name__ == "__main__":
    main()
