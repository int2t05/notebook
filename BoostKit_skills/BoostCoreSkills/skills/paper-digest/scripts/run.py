"""paper-digest entry point — Plan A (pure LLM-driven, no per-direction profile).

Phases:
  0     parse input  (LLM flash)        direction → keywords / exclude / slug / window
  0.5   expand keywords (LLM strong, always-on)
                                        Phase 0 keywords → 30-60 keywords + arxiv_categories
  1A    discover conferences (LLM strong) + DBLP verify + metadata enrichment
  1B    discover external (arXiv 1B.1 + LLM-curated lab/researcher/blog 1B.5)
  2     coarse-classify titles (LLM flash, batched)
  2.5   fetch abstracts (USENIX / Semantic Scholar; deterministic)
  3     4-段量化摘要 + 3-tag (LLM strong, with anti-fabrication guard)
  4     render Jinja2 templates (deterministic)

`--resume` skips phases already marked done in manifest.json. Phase 0.5 and
Phase 2.5 are idempotent and always rerun (cheap).
"""
import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from scripts.utils import LLMClient, CLISubprocessLLM, Archive, BudgetExceeded
from scripts.input_parser import parse_input
from scripts.conference_discoverer import discover_conferences, llm_bulk_score_metadata, _load_metadata as _load_conf_metadata
from scripts.external_discoverer import discover_external
from scripts.classifier import classify_all
from scripts.abstract_fetcher import fetch_all_abstracts
from scripts.extractor import extract_all
from scripts.renderer import render_archive
from scripts.focus_areas import (
    generate_via_llm as expand_focus_areas,
    flatten_keywords as flatten_focus_keywords,
    to_markdown as focus_to_markdown,
)
from scripts.quality_report import QualityRecorder

log = logging.getLogger("paper-digest")


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text())


# ============================================================
# Backend resolution (CLI / API)
# ============================================================

def _api_cfg(cfg: dict) -> dict:
    llm = cfg.get("llm", {}) or {}
    return llm.get("api") or llm


def _cli_cfg(cfg: dict) -> dict:
    llm = cfg.get("llm", {}) or {}
    return llm.get("cli_backend") or llm.get("claude_cli") or {}


def _resolve_backend_choice(cfg: dict, requested: str) -> str:
    """Auto: prefer CLI binary on PATH; else API if key set; else error."""
    if requested in ("api", "cli"):
        return requested
    cli_bin = (_cli_cfg(cfg) or {}).get("binary", "claude")
    cli_available = shutil.which(cli_bin) is not None
    api_key_env = (_api_cfg(cfg) or {}).get("api_key_env", "PAPER_DIGEST_LLM_API_KEY")
    api_key_set = bool(os.getenv(api_key_env))
    if cli_available:
        return "cli"
    if api_key_set:
        return "api"
    raise SystemExit(
        f"No LLM backend available. Either install the agent CLI configured "
        f"as `llm.cli_backend.binary` (default: '{cli_bin}'), or export "
        f"`{api_key_env}` for the API backend. See SKILL.md / README for setup."
    )


def list_backends(cfg: dict) -> None:
    cli = _cli_cfg(cfg) or {}
    cli_bin = cli.get("binary", "claude")
    cli_path = shutil.which(cli_bin)
    print(f"CLI backend (binary='{cli_bin}'): "
          f"{'AVAILABLE at ' + cli_path if cli_path else 'NOT FOUND on PATH'}")
    api = _api_cfg(cfg) or {}
    api_key_env = api.get("api_key_env", "PAPER_DIGEST_LLM_API_KEY")
    api_ok = bool(os.getenv(api_key_env))
    print(f"API backend (env='{api_key_env}'): "
          f"{'AVAILABLE (key set)' if api_ok else 'NOT CONFIGURED (key unset)'}")


def build_llm(cfg: dict, max_budget: int, backend: str = "auto"):
    """CLI = subscription-auth agent CLI; API = OpenAI-protocol endpoint."""
    choice = _resolve_backend_choice(cfg, backend)
    if choice == "cli":
        cli = _cli_cfg(cfg)
        return CLISubprocessLLM(
            max_budget=max_budget,
            binary=cli.get("binary", "claude"),
            prompt_arg=cli.get("prompt_arg", "-p"),
            model_arg=cli.get("model_arg", "--model"),
            extra_args=cli.get("extra_args", ["--no-session-persistence"]),
            model_map={"flash": cli.get("model_flash", "haiku"),
                       "strong": cli.get("model_strong", "sonnet")},
            timeout_flash=int(cli.get("timeout_flash_seconds", 120)),
            timeout_strong=int(cli.get("timeout_strong_seconds", 240)),
        )
    api = _api_cfg(cfg)
    api_key_env = api.get("api_key_env", "PAPER_DIGEST_LLM_API_KEY")
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise SystemExit(
            f"Backend 'api' requires env var {api_key_env}. "
            f"Either set it, or use `--backend cli` / `--backend auto`."
        )
    base_url = (os.getenv(api.get("base_url_env", "PAPER_DIGEST_LLM_BASE_URL"))
                or api.get("base_url_default", "https://api.deepseek.com/v1"))
    return LLMClient(
        api_key=api_key, max_budget=max_budget, base_url=base_url,
        model_flash=api.get("model_flash", "deepseek-chat"),
        model_strong=api.get("model_strong", "deepseek-reasoner"),
    )


# ============================================================
# Phase 1 parallel runner
# ============================================================

async def run_phase_1_parallel(keywords, start_date, end_date, top_n,
                                arxiv_categories, llm, direction_raw,
                                recorder=None):
    """Phase 1A (conferences) + Phase 1B (arXiv + curated external) in parallel."""
    conf_task = asyncio.to_thread(
        discover_conferences, keywords, start_date, end_date, top_n,
        llm, direction_raw, True, recorder,
    )
    ext_task = asyncio.to_thread(
        discover_external, keywords, start_date, end_date,
        direction_raw, arxiv_categories, llm, recorder,
    )
    return await asyncio.gather(conf_task, ext_task)


# ============================================================
# Dry-run preview
# ============================================================

def print_dry_run(parsed: dict, tier_cfg: dict,
                  start_date: str, end_date: str,
                  llm, direction_raw: str,
                  arxiv_categories: list) -> None:
    """Preview Phase 0/0.5 result + Phase 1A.1 LLM candidates (no DBLP, no archive)."""
    from scripts.conference_discoverer import (
        llm_propose_candidates, _composite_score, score_to_emoji, _load_metadata,
    )
    metadata = _load_metadata()
    top_n = tier_cfg["top_n_conferences"]

    llm_cands = []
    if llm is not None:
        try:
            llm_cands = llm_propose_candidates(
                direction_raw or " ".join(parsed["keywords"]),
                parsed["keywords"], start_date, end_date, top_n, llm,
            )
        except Exception as e:
            log.warning("dry-run LLM proposal failed (%s)", e)

    print()
    print("=" * 70)
    print("DRY RUN — Phase 0/0.5 done + Phase 1A.1 LLM proposal only.")
    print("           No DBLP fetch, no Phase 1B.5 curate, no archive written.")
    print("=" * 70)
    print(f"Direction         : {direction_raw}")
    print(f"Window            : {start_date} .. {end_date}")
    print(f"Phase-0 keywords  : {parsed['keywords']}")
    print(f"Phase-0 exclude   : {parsed['exclude']}")
    print(f"Phase-0.5 expanded: {len(parsed.get('expanded_keywords', parsed['keywords']))} keywords")
    print(f"arXiv categories  : {arxiv_categories}")
    print(f"Slug              : {parsed['slug']}")
    print()
    if llm_cands:
        print(f"Phase 1A.1 LLM-proposed Top-{top_n} candidates "
              f"(direction_score / composite / emoji / month / rationale):")
        for c in llm_cands[:top_n]:
            meta = metadata.get(c["name"], {}) or {}
            comp = _composite_score(c["direction_score"], meta.get("ccf", ""),
                                     meta.get("core", ""), meta.get("h5"))
            emoji = score_to_emoji(c["direction_score"]) or "—"
            print(f"  ds={c['direction_score']:4.1f}  comp={comp:5.2f}  "
                  f"{emoji:>4}  {c['name']:<14} {c['year']}  "
                  f"M{c.get('expected_month') or '?':>2}  "
                  f"{c.get('rationale','')[:60]}")
        if len(llm_cands) > top_n:
            print(f"  ... (+ {len(llm_cands) - top_n} more LLM proposals)")
    else:
        print("Phase 1A.1: LLM unavailable; would fall back to metadata enumeration.")
    print()


# ============================================================
# main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="paper-digest pipeline (Plan A — pure LLM-driven, profile-free)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--direction", default=None,
                        help='Natural-language direction, e.g. "memory allocator and CXL"')
    parser.add_argument("--window", default=None,
                        help='Time window, e.g. "last 6 months" / "近 1 年" / '
                             '"2025-11-01..2026-05-22" / "Q1 2026"')
    parser.add_argument("--quality", default="standard",
                        choices=["fast", "standard", "deep"],
                        help="Quality tier (top-N / budget / extract_yellow)")
    parser.add_argument("--top-n", type=int, default=None,
                        help="Override top_n_conferences from --quality tier")
    parser.add_argument("--output-dir", default=None,
                        help="Override output base dir (default: paper-digest-output/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run Phase 0 + Phase 0.5 + Phase 1A.1 LLM proposal only; "
                             "no DBLP fetch, no archive written.")
    parser.add_argument("--resume", action="store_true",
                        help="Skip phases already marked done in archive manifest.json.")
    parser.add_argument("--backend", default=None,
                        choices=["auto", "api", "cli"],
                        help="LLM backend. cli = local agent CLI subprocess; "
                             "api = OpenAI-protocol endpoint; auto = prefer cli.")
    parser.add_argument("--list-backends", action="store_true",
                        help="Print which LLM backends are available and exit.")
    parser.add_argument("--no-expand-keywords", action="store_true",
                        help="Skip Phase 0.5 (LLM keyword expansion). Phase 1B "
                             "will then use only the 6-10 Phase-0 keywords against "
                             "the default arXiv categories.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    cfg = load_config()

    if args.list_backends:
        list_backends(cfg)
        return

    if not args.direction or not args.window:
        parser.error("--direction and --window are required (unless --list-backends)")

    backend = args.backend or cfg.get("llm", {}).get("backend_default", "auto")
    tier_cfg = dict(cfg["quality_tiers"][args.quality])
    if args.top_n is not None:
        tier_cfg["top_n_conferences"] = args.top_n
    output_base = Path(args.output_dir or cfg["output"]["base_dir"])
    output_base.mkdir(parents=True, exist_ok=True)

    llm = build_llm(cfg, tier_cfg["max_budget_tokens"], backend=backend)
    log.info("LLM backend: %s (requested=%s)", type(llm).__name__, backend)

    # Recorder for warnings / retries / failures across all phases.
    # Written to archive/quality-report.{md,json} at the end of the run.
    recorder = QualityRecorder()

    include_date_label = cfg.get("output", {}).get("include_date_label", False)

    # ============================================================
    # Resume vs fresh
    # ============================================================
    archive: Optional[Archive] = None
    parsed: Optional[dict] = None
    if args.resume:
        try:
            from scripts.input_parser import parse_time_window
            start_d, end_d = parse_time_window(args.window)
            archive = Archive.resume(
                base_dir=output_base, slug="", window_label="",
                start_date=start_d.isoformat(), end_date=end_d.isoformat(),
                include_date_label=include_date_label,
            )
        except Exception as e:
            log.warning("resume pre-search failed: %s", e)
        if archive is not None:
            log.info("Resuming archive: %s (phases done: %s)",
                     archive.path, archive.phases_done())
            parsed = archive.read_manifest().get("parsed")

    # ============================================================
    # Phase 0: parse direction → keywords / exclude
    # ============================================================
    if parsed is None:
        log.info("Phase 0: parsing input")
        parsed = parse_input(args.direction, args.window, llm)

    log.info("Parsed: keywords=%s window=%s..%s",
             parsed["keywords"], parsed["start_date"], parsed["end_date"])

    # ============================================================
    # Phase 0.5: LLM-driven keyword expansion (DEFAULT ON, --no-expand-keywords to disable)
    # ============================================================
    focus_areas: Optional[dict] = None
    arxiv_categories: Optional[list] = None
    expanded_keywords: list = list(parsed["keywords"])

    if not args.no_expand_keywords:
        log.info("Phase 0.5: LLM keyword expansion")
        try:
            focus_areas = expand_focus_areas(
                direction_raw=args.direction,
                phase0_keywords=parsed["keywords"],
                conference_hits=[],
                llm=llm,
            )
            expanded_keywords = flatten_focus_keywords(focus_areas) or expanded_keywords
            arxiv_categories = focus_areas.get("arxiv_categories") or None
            if focus_areas.get("exclude"):
                parsed["exclude"] = list(dict.fromkeys(
                    list(parsed.get("exclude") or []) + focus_areas["exclude"]))
            log.info("Phase 0.5 → %d expanded keywords, arxiv_categories=%s",
                     len(expanded_keywords), arxiv_categories)
            parsed["expanded_keywords"] = expanded_keywords
        except Exception as e:
            log.warning("Phase 0.5 failed (%s); proceeding with Phase 0 keywords only", e)
            focus_areas = None

    # Dry-run early exit
    if args.dry_run:
        print_dry_run(parsed, tier_cfg,
                      parsed["start_date"], parsed["end_date"],
                      llm=llm, direction_raw=args.direction,
                      arxiv_categories=arxiv_categories or [])
        return

    # ============================================================
    # Archive (fresh) — must come after Phase 0/0.5 so slug is known
    # ============================================================
    if archive is None:
        archive = Archive.new(
            base_dir=output_base,
            slug=parsed.get("slug", "search"),
            window_label=parsed.get("window_label", ""),
            date_label=datetime.now().strftime("%Y-%m-%d"),
            start_date=parsed.get("start_date"),
            end_date=parsed.get("end_date"),
            include_date_label=include_date_label,
            manifest={
                "input": {
                    "direction_raw": args.direction,
                    "window_raw": args.window,
                    "quality": args.quality,
                    "max_budget_tokens": tier_cfg["max_budget_tokens"],
                },
                "parsed": parsed,
            },
        )
        log.info("Archive: %s", archive.path)
        archive.mark_phase_done("phase0", llm.tokens_used)

    if focus_areas is not None:
        archive.write_intermediate("phase0.5-focus-areas", focus_areas)
        (archive.path / "intermediate" / "phase0.5-focus-areas.md").write_text(
            focus_to_markdown(focus_areas, args.direction, parsed["keywords"]))
        archive.mark_phase_done("phase0.5", llm.tokens_used)
    elif args.resume:
        try:
            focus_areas = archive.read_intermediate("phase0.5-focus-areas")
            expanded_keywords = flatten_focus_keywords(focus_areas) or expanded_keywords
            arxiv_categories = focus_areas.get("arxiv_categories") or arxiv_categories
            log.info("Resumed Phase 0.5 from cache: %d expanded keywords",
                     len(expanded_keywords))
        except FileNotFoundError:
            pass

    done = set(archive.phases_done())
    errors: dict = {}
    conferences: list = []
    external: dict = {"arxiv": [], "lab": [], "researcher": [], "rfc": [], "blog": []}
    all_papers: list = []

    try:
        # ============================================================
        # Phase 1A (conferences) + Phase 1B (external) in parallel
        # ============================================================
        if "phase1" not in done:
            log.info("Phase 1A+1B in parallel (LLM proposes confs + arXiv + LLM curates external)")
            conferences, external = asyncio.run(run_phase_1_parallel(
                expanded_keywords, parsed["start_date"], parsed["end_date"],
                tier_cfg["top_n_conferences"], arxiv_categories, llm, args.direction,
                recorder,
            ))
            archive.write_intermediate("phase1a-conferences", {"conferences": conferences})
            archive.write_intermediate("phase1b-external", external)
            archive.mark_phase_done("phase1", llm.tokens_used)
        else:
            log.info("Phase 1 (resume): loading from intermediate")
            conferences = archive.read_intermediate("phase1a-conferences")["conferences"]
            external = archive.read_intermediate("phase1b-external")

        for c in conferences:
            all_papers.extend(c.get("papers", []))
        for paper_list in external.values():
            all_papers.extend(paper_list)
        log.info("Merged %d papers (conf + external) for Phase 2", len(all_papers))

        # ============================================================
        # Phase 2: coarse classify
        # ============================================================
        if "phase2" not in done:
            log.info("Phase 2: coarse classification")
            classify_all(all_papers, parsed["keywords"], parsed["exclude"], llm,
                         batch_size=cfg["llm"].get("batch_size_classify", 25),
                         recorder=recorder)
            archive.write_intermediate("phase2-classified", {"papers": all_papers})
            archive.mark_phase_done("phase2", llm.tokens_used)
        else:
            log.info("Phase 2 (resume): loading classified papers")
            all_papers = archive.read_intermediate("phase2-classified")["papers"]

        # ============================================================
        # Phase 2.5: abstract fetch (idempotent, no LLM, always rerun)
        # ============================================================
        log.info("Phase 2.5: fetching abstracts for green/yellow papers")
        abs_stats = fetch_all_abstracts(all_papers, only_relevance={"green", "yellow"})
        log.info("Phase 2.5 abstract sources: %s", abs_stats)
        archive.write_intermediate("phase2.5-abstracts",
                                   {"papers": all_papers, "stats": abs_stats})

        # ============================================================
        # Phase 3: deep extract
        # ============================================================
        if "phase3" not in done:
            log.info("Phase 3: deep extraction (green + yellow)")
            extract_all(all_papers, parsed["keywords"], llm,
                        include_yellow=tier_cfg["extract_yellow"],
                        recorder=recorder)
            archive.write_intermediate("phase3-detailed", {"papers": all_papers})
            archive.mark_phase_done("phase3", llm.tokens_used)
        else:
            log.info("Phase 3 (resume): loading extracted papers")
            all_papers = archive.read_intermediate("phase3-detailed")["papers"]

    except BudgetExceeded as e:
        log.error("Budget exceeded: %s", e)
        errors["budget_exceeded"] = str(e)

    # ============================================================
    # Phase 4: render — one extra LLM call (Phase 1A.0 bulk-score) to give
    # direction_match emoji to metadata-only fillers in the overview table,
    # then deterministic Jinja2 rendering. The bulk-score is cached + reused
    # on --resume.
    log.info("Phase 4: rendering")
    metadata_scores: dict = {}
    try:
        cached = archive.read_intermediate("phase1a0-metadata-scores")
        metadata_scores = cached.get("scores", {})
        log.info("Resumed metadata bulk-scores (%d confs)", len(metadata_scores))
    except FileNotFoundError:
        metadata_scores = llm_bulk_score_metadata(
            args.direction, parsed["keywords"], _load_conf_metadata(), llm)
        if metadata_scores:
            archive.write_intermediate("phase1a0-metadata-scores",
                                       {"scores": metadata_scores})

    conf_papers = [p for p in all_papers if p.get("source_type") == "conference"]
    ext_papers = [p for p in all_papers if p.get("source_type") == "external"]
    render_archive(
        archive_dir=archive.path,
        manifest=archive.read_manifest(),
        conferences=conferences,
        conf_papers=conf_papers,
        external_papers=ext_papers,
        tag_emoji=cfg["tags"],
        metadata_scores=metadata_scores,
    )
    archive.mark_phase_done("phase4", llm.tokens_used)

    if errors:
        (archive.path / "errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False))

    # Quality report (warnings / retries / failures aggregation)
    recorder.write_report(archive.path)
    log.info("Quality report: %s", archive.path / "quality-report.md")

    log.info("Done. Archive: %s | Tokens used: %d / %d",
             archive.path, llm.tokens_used, tier_cfg["max_budget_tokens"])


if __name__ == "__main__":
    main()
