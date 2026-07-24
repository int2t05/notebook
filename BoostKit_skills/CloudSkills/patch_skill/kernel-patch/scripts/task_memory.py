#!/usr/bin/env python3
"""Inspect and update kernel_patch task state (state-file only)."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Any, Dict

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from shared.cli import emit_json
from shared.paths import resolve_user_path


def _resolve_state_file(patches_dir: str | None, state_file: str | None) -> str:
    if state_file:
        return resolve_user_path(state_file)
    if patches_dir:
        return os.path.join(resolve_user_path(patches_dir), "kernel_patch_state.json")
    raise ValueError("one of --state-file or --patches-dir is required")


def inspect_state(state_file: str) -> dict:
    from orchestrator.state_manager import StateManager
    from orchestrator.state_machine import Phase, ACTIVE_PHASES, TERMINAL_PHASES

    manager = StateManager(state_file)

    if not manager.state.get("task_id"):
        return {
            "success": True,
            "exists": False,
            "state_file": state_file,
            "task_started": False,
            "should_resume": False,
            "task_status": Phase.IDLE.value,
        }

    phase = manager.state.get("phase")
    return {
        "success": True,
        "exists": True,
        "state_file": state_file,
        "task_started": phase not in {Phase.IDLE.value, None},
        "should_resume": phase in ACTIVE_PHASES,
        "should_ignore": phase in TERMINAL_PHASES,
        "task_status": phase,
        "task_id": manager.state.get("task_id"),
        "summary": manager.state["llm"]["summary"],
        "state": manager.get_llm_view(),
    }


def mark_state_ended(state_file: str, final_head: str | None, note: str | None) -> dict:
    from orchestrator.state_manager import StateManager
    from orchestrator.state_machine import Phase

    manager = StateManager(state_file)

    if not manager.state.get("task_id"):
        return {
            "success": False,
            "state_file": state_file,
            "error": "state file does not exist or has no task_id",
        }

    manager.state["phase"] = Phase.ENDED.value
    manager.state.setdefault("final", {})
    manager.state["final"]["final_head"] = final_head
    manager.state["final"]["completed_at"] = datetime.now().isoformat()

    if note:
        manager.state.setdefault("llm", {})
        manager.state["llm"]["summary"] = note
    manager.save()

    return {
        "success": True,
        "state_file": state_file,
        "task_status": Phase.ENDED.value,
        "final_head": manager.state["final"]["final_head"],
        "summary": manager.state["llm"]["summary"],
    }


def mark_state_aborted(state_file: str, note: str | None) -> dict:
    from orchestrator.state_manager import StateManager
    from orchestrator.state_machine import Phase

    manager = StateManager(state_file)

    if not manager.state.get("task_id"):
        return {
            "success": False,
            "state_file": state_file,
            "error": "state file does not exist or has no task_id",
        }

    manager.state["phase"] = Phase.ABORTED.value
    manager.state.setdefault("runtime", {})
    manager.state["runtime"]["escalation_reason"] = note or "Manually aborted"

    if note:
        manager.state.setdefault("llm", {})
        manager.state["llm"]["summary"] = note
    manager.save()

    return {
        "success": True,
        "state_file": state_file,
        "task_status": Phase.ABORTED.value,
        "summary": manager.state["llm"]["summary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or update kernel_patch task state (state-only)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect current task state.")
    inspect_parser.add_argument("--patches-dir", default="", help="Patch directory.")
    inspect_parser.add_argument("--state-file", default="", help="State file path.")

    mark_ended_parser = subparsers.add_parser("mark-ended", help="Mark task as ended.")
    mark_ended_parser.add_argument("--patches-dir", default="", help="Patch directory.")
    mark_ended_parser.add_argument("--state-file", default="", help="State file path.")
    mark_ended_parser.add_argument("--final-head", default=None, help="Final commit at task end.")
    mark_ended_parser.add_argument("--note", default=None, help="Optional final summary override.")

    mark_aborted_parser = subparsers.add_parser("mark-aborted", help="Mark task as aborted.")
    mark_aborted_parser.add_argument("--patches-dir", default="", help="Patch directory.")
    mark_aborted_parser.add_argument("--state-file", default="", help="State file path.")
    mark_aborted_parser.add_argument("--note", default=None, help="Optional abort summary override.")

    args = parser.parse_args()

    try:
        state_file = _resolve_state_file(
            patches_dir=getattr(args, "patches_dir", None) or None,
            state_file=getattr(args, "state_file", None) or None,
        )

        if args.command == "inspect":
            return emit_json(inspect_state(state_file))
        if args.command == "mark-ended":
            return emit_json(mark_state_ended(state_file, args.final_head, args.note))
        if args.command == "mark-aborted":
            return emit_json(mark_state_aborted(state_file, args.note))

    except ValueError as exc:
        return emit_json({
            "success": False,
            "error": str(exc),
        })

    return emit_json({
        "success": False,
        "error": f"unknown command: {args.command}",
    })


if __name__ == "__main__":
    raise SystemExit(main())
