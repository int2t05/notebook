#!/usr/bin/env python3
"""
Run patch sets through the kernel_patch workflow - Refactored version.

This is the refactored version focusing on:
1. CLI argument parsing
2. Calling PatchWorkflow
3. Special mode handling (reconcile, after_continue, semantic, hunk)
4. Results returning

Total lines: ~350 (reduced from 2320)
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Optional, Any, List

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from orchestrator.state_manager import StateManager
from orchestrator.state_machine import Phase, StateMachine, is_active_phase, is_blocked_phase
from orchestrator.workflow import PatchWorkflow
from shared.cli import emit_json, load_json_arg, load_json_file
from shared.config import LOG_FORMAT, LOG_LEVEL
from shared.paths import resolve_user_path

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DECISION_OPTIONS: List[str] = ["continue", "accept-semantic", "accept-hunk", "abort"]

# === CLI 参数解析 ===

def _load_input(input_json: str | None, input_json_inline: str | None) -> dict:
    if input_json:
        return load_json_file(resolve_user_path(input_json))
    if input_json_inline:
        return load_json_arg(input_json_inline)
    raise ValueError("one of input_json or input_json_inline is required")


def _build_payload_from_flat_args(args: argparse.Namespace) -> dict:
    flat_values = {
        "target_repo": args.target_repo,
        "target_branch": args.target_branch,
        "reject_dir": args.reject_dir,
        "patches_dir": args.patches_dir,
        "patch_sets_json": args.patch_sets_json,
    }
    missing = [name for name, value in flat_values.items() if not value]
    if missing:
        raise ValueError(
            "missing flat CLI arguments: "
            + ", ".join(f"--{name.replace('_', '-')}" for name in missing)
            + "; use --input-json/--input-json-inline or provide the complete flat argument set"
        )

    patch_sets = load_json_arg(args.patch_sets_json)
    if not isinstance(patch_sets, list):
        raise ValueError("--patch-sets-json must decode to a JSON list")

    return {
        "target_repo": args.target_repo,
        "target_branch": args.target_branch,
        "reject_dir": args.reject_dir,
        "patches_dir": args.patches_dir,
        "config_files": list(args.config_files or []),
        "patch_sets": patch_sets,
        "max_iteration_per_patch": args.max_iteration_per_patch,
    }


def _load_cli_payload(args: argparse.Namespace) -> dict:
    if args.input_json or args.input_json_inline:
        return _load_input(args.input_json or None, args.input_json_inline or None)
    return _build_payload_from_flat_args(args)


def _normalize_paths(payload: dict) -> dict:
    normalized = dict(payload)
    for key in ("target_repo", "reject_dir", "patches_dir"):
        normalized[key] = resolve_user_path(payload[key])
    normalized["config_files"] = [
        resolve_user_path(path) for path in payload.get("config_files", [])
    ]
    patch_sets = []
    for patch_set in payload["patch_sets"]:
        patch_sets.append({
            "name": patch_set["name"],
            "source_repo": resolve_user_path(patch_set["source_repo"]),
            "commits": list(patch_set["commits"]),
        })
    normalized["patch_sets"] = patch_sets
    normalized["max_iteration_per_patch"] = int(payload.get("max_iteration_per_patch", 4))
    return normalized


def _resolve_state_file(config: dict, state_file: str | None) -> str:
    if state_file:
        return resolve_user_path(state_file)
    return os.path.join(config["patches_dir"], "kernel_patch_state.json")


# === 辅助函数 ===

def _failure_payload(
    config: dict,
    test_branch: str | None,
    results: list,
    next_action: str,
    state_file: str,
    resume_source: str | None = None,
    **extra: Any,
) -> str:
    payload = {
        "success": False,
        "target_repo": config["target_repo"],
        "target_branch": config["target_branch"],
        "test_branch": test_branch,
        "next_action": next_action,
        "results": results,
        "state_file": state_file,
        "resume_source": resume_source,
    }
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _build_review_prompt(target_repo: str, test_branch: str, patches_dir: str) -> str:
    return (
        f"/patch-validator 帮我检查一下{target_repo}的分支"
        f"{test_branch}合入的补丁，与在{patches_dir}的补丁是否存在差异。"
    )


def _recommended_decisions_for_reason(reason: str | None) -> List[str]:
    normalized = (reason or "unknown").strip().lower()
    if normalized in {"semantic-substitution-suspected"}:
        return ["accept-semantic", "continue", "abort"]
    if normalized in {"missing-hunk", "missing-hunk-source-confirmed"}:
        return ["accept-hunk", "continue", "abort"]
    if normalized in {"apply_failed", "conflict_detected"}:
        return ["continue", "abort"]
    return ["continue", "abort"]


def _decision_reason_from_runtime(runtime: Dict[str, Any]) -> str:
    return (
        runtime.get("last_validation_status")
        or runtime.get("escalation_reason")
        or "unknown"
    )


def _resume_command_examples() -> List[Dict[str, str]]:
    """Build generic CLI examples for blocked recovery states."""
    base_cmd = "python3 /path/to/kernel-patch/scripts/run_patch_sets.py --input-json /path/to/input.json"
    return [
        {
            "scenario": "manual-fix-applied",
            "command": f"{base_cmd} --resume-after-fix",
        },
        {
            "scenario": "accept-current-head",
            "command": f"{base_cmd} --human-decision continue",
        },
        {
            "scenario": "accept-semantic-substitution",
            "command": f"{base_cmd} --human-decision accept-semantic",
        },
        {
            "scenario": "accept-hunk-recovery",
            "command": f"{base_cmd} --human-decision accept-hunk",
        },
    ]


def _attach_decision_warning(
    raw_response: str,
    *,
    decision: str,
    reason: str,
    recommended_decisions: List[str],
) -> str:
    if decision in recommended_decisions:
        return raw_response
    payload = json.loads(raw_response)
    payload["decision_warning"] = (
        f"Decision '{decision}' is not recommended for current context '{reason}'."
    )
    payload["recommended_decisions"] = recommended_decisions
    context = payload.get("decision_context")
    if isinstance(context, dict):
        context.setdefault("reason", reason)
    else:
        payload["decision_context"] = {"reason": reason}
    return json.dumps(payload, ensure_ascii=False, indent=2)


# === 特殊模式处理 ===

def _handle_reconcile(
    config: dict,
    state_manager: StateManager,
    resume_test_branch: str | None,
) -> str:
    """Handle reconcile mode - rebuild progress from test branch history."""
    from shared.git_helpers import branch_exists

    # 获取测试分支
    test_branch = resume_test_branch or state_manager.state.get("config", {}).get("test_branch")
    if not test_branch:
        return json.dumps({
            "success": False,
            "next_action": "stop_manual_recovery_required",
            "error": "cannot reconcile without a test branch",
        }, ensure_ascii=False, indent=2)

    # 检查分支是否存在
    if not branch_exists(test_branch, config["target_repo"]):
        return json.dumps({
            "success": False,
            "next_action": "stop_manual_recovery_required",
            "error": f"test branch does not exist: {test_branch}",
        }, ensure_ascii=False, indent=2)

    # 创建工作流并执行 reconcile
    workflow = PatchWorkflow(config=config, state_manager=state_manager)
    return workflow.reconcile(test_branch)


def _handle_after_continue(
    config: dict,
    state_manager: StateManager,
) -> str:
    """Handle after_continue mode - validate patch at HEAD after git am --continue."""
    # 检查 git am 是否还在进行
    workflow = PatchWorkflow(config=config, state_manager=state_manager)

    if workflow.git_am_in_progress():
        return json.dumps({
            "success": False,
            "next_action": "continue_git_am",
            "message": "git am is still in progress; finish git am --continue first",
        }, ensure_ascii=False, indent=2)

    # 检查阶段是否正确
    phase = state_manager.state.get("phase")
    if phase != "waiting_after_continue":
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--after-continue requires phase=waiting_after_continue",
            "current_phase": phase,
        }, ensure_ascii=False, indent=2)

    return workflow.resume_after_continue()


def _handle_semantic_acceptance(
    config: dict,
    state_manager: StateManager,
) -> str:
    """Handle semantic substitution acceptance."""
    if state_manager.state.get("phase") != "waiting_semantic_confirmation":
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--accept-semantic-substitution requires phase=waiting_semantic_confirmation",
        }, ensure_ascii=False, indent=2)

    workflow = PatchWorkflow(config=config, state_manager=state_manager)
    return workflow.accept_semantic_substitution()


def _handle_hunk_acceptance(
    config: dict,
    state_manager: StateManager,
    accept_hunk_recovery: str,
) -> str:
    """Handle hunk recovery acceptance."""
    if state_manager.state.get("phase") != "waiting_hunk_confirmation":
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--accept-hunk-recovery requires phase=waiting_hunk_confirmation",
        }, ensure_ascii=False, indent=2)

    if accept_hunk_recovery not in {"ignore-and-continue", "stop-and-abort"}:
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--accept-hunk-recovery must be one of: ignore-and-continue, stop-and-abort",
        }, ensure_ascii=False, indent=2)

    workflow = PatchWorkflow(config=config, state_manager=state_manager)
    return workflow.accept_hunk_recovery(accept_hunk_recovery)


def _handle_resume_after_fix(
    config: dict,
    state_manager: StateManager,
) -> str:
    """Handle resume after manual fix from needs_human state."""
    current_phase = state_manager.state.get("phase")
    if current_phase != "needs_human":
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--resume-after-fix requires phase=needs_human",
            "current_phase": current_phase,
        }, ensure_ascii=False, indent=2)

    workflow = PatchWorkflow(config=config, state_manager=state_manager)
    return workflow.resume_after_fix()


def _handle_human_decision(
    config: dict,
    state_manager: StateManager,
    decision: str,
) -> str:
    """Handle explicit human decision when phase is needs_human."""
    if state_manager.state.get("phase") != Phase.NEEDS_HUMAN.value:
        return json.dumps({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": "--human-decision requires phase=needs_human",
            "current_phase": state_manager.state.get("phase"),
        }, ensure_ascii=False, indent=2)

    workflow = PatchWorkflow(config=config, state_manager=state_manager)
    runtime = state_manager.state.get("runtime", {})
    reason = _decision_reason_from_runtime(runtime)
    recommended = _recommended_decisions_for_reason(reason)

    if decision == "continue":
        return _attach_decision_warning(
            workflow.resume_after_fix(),
            decision=decision,
            reason=reason,
            recommended_decisions=recommended,
        )
    if decision == "abort":
        state_manager.transition(
            Phase.ABORTED.value,
            **{
                "runtime.escalation_reason": "human_decision_abort",
            }
        )
        response = json.dumps({
            "success": False,
            "next_action": "stop_manual_recovery_required",
            "message": "Task aborted by human decision.",
            "human_decision": decision,
            "recommended_decisions": recommended,
            "decision_context": {"reason": reason},
        }, ensure_ascii=False, indent=2)
        return _attach_decision_warning(
            response,
            decision=decision,
            reason=reason,
            recommended_decisions=recommended,
        )
    if decision == "accept-semantic":
        state_manager.transition(Phase.WAITING_SEMANTIC_CONFIRMATION.value)
        return _attach_decision_warning(
            workflow.accept_semantic_substitution(),
            decision=decision,
            reason=reason,
            recommended_decisions=recommended,
        )
    if decision == "accept-hunk":
        state_manager.transition(Phase.WAITING_HUNK_CONFIRMATION.value)
        return _attach_decision_warning(
            workflow.accept_hunk_recovery("ignore-and-continue"),
            decision=decision,
            reason=reason,
            recommended_decisions=recommended,
        )

    return json.dumps({
        "success": False,
        "next_action": "stop_invalid_input",
        "error": "invalid --human-decision value",
        "human_decision": decision,
    }, ensure_ascii=False, indent=2)


# === 主入口 ===

def run_patch_sets(
    payload: dict,
    resume_test_branch: str | None = None,
    resume_set_index: int = 0,
    resume_commit_index: int = 0,
    after_continue: bool = False,
    reconcile: bool = False,
    accept_semantic_substitution: bool = False,
    accept_hunk_recovery: str | None = None,
    resume_after_fix: bool = False,
    human_decision: str | None = None,
    state_file: str | None = None,
) -> str:
    """
    Main entry point for running patch sets through the workflow.
    """
    config = _normalize_paths(payload)
    resolved_state_file = _resolve_state_file(config, state_file)

    # 初始化 StateManager
    state_manager = StateManager(resolved_state_file)

    # 阻塞态保护：needs_human 必须由人工决策明确解锁
    current_phase = state_manager.state.get("phase")
    if current_phase == Phase.NEEDS_HUMAN.value and not human_decision:
        runtime = state_manager.state.get("runtime", {})
        state_config = state_manager.state.get("config", {})
        reason = _decision_reason_from_runtime(runtime)
        return _failure_payload(
            config=config,
            test_branch=resume_test_branch or state_config.get("test_branch"),
            results=[],
            next_action="stop_manual_recovery_required",
            state_file=resolved_state_file,
            current_phase=current_phase,
            phase=current_phase,
            validation_status=runtime.get("last_validation_status"),
            escalation_reason=runtime.get("escalation_reason"),
            decision_required=True,
            decision_options=DECISION_OPTIONS,
            recommended_decisions=_recommended_decisions_for_reason(reason),
            resume_command_examples=_resume_command_examples(),
            decision_context={"reason": reason},
            last_observed_commit_ref=runtime.get("last_observed_commit_ref"),
            evidence_snapshot=runtime.get("last_evidence_snapshot"),
        )

    # 检查互斥参数
    if sum(
        1
        for flag in (
            after_continue,
            reconcile,
            accept_semantic_substitution,
            bool(accept_hunk_recovery),
            resume_after_fix,
            bool(human_decision),
        )
        if flag
    ) > 1:
        return _failure_payload(
            config=config,
            test_branch=resume_test_branch,
            results=[],
            next_action="stop_invalid_input",
            state_file=resolved_state_file,
            error="--after-continue, --reconcile, --accept-semantic-substitution, --accept-hunk-recovery, --resume-after-fix and --human-decision are mutually exclusive",
        )

    if human_decision:
        return _handle_human_decision(config, state_manager, human_decision)

    # 处理 reconcile 模式
    if reconcile:
        return _handle_reconcile(config, state_manager, resume_test_branch)

    # 处理 after_continue 模式
    if after_continue:
        return _handle_after_continue(config, state_manager)

    # 处理 resume_after_fix 模式
    if resume_after_fix:
        return _handle_resume_after_fix(config, state_manager)

    # 处理语义确认
    if accept_semantic_substitution:
        return _handle_semantic_acceptance(config, state_manager)

    # 处理 hunk 确认
    if accept_hunk_recovery:
        return _handle_hunk_acceptance(config, state_manager, accept_hunk_recovery)

    # 创建并运行工作流
    workflow = PatchWorkflow(
        config=config,
        state_manager=state_manager,
    )

    return workflow.run()


# === CLI 入口 ===

def main() -> int:
    parser = argparse.ArgumentParser(description="Run patch sets through the kernel_patch workflow.")
    parser.add_argument("--input-json", default="", help="Path to an input JSON file.")
    parser.add_argument("--input-json-inline", default="", help="Inline JSON payload.")
    parser.add_argument("--target-repo", default="", help="Target repository path.")
    parser.add_argument("--target-branch", default="", help="Target branch.")
    parser.add_argument("--reject-dir", default="", help="Reject directory.")
    parser.add_argument("--patches-dir", default="", help="Patch export directory.")
    parser.add_argument("--config-files", nargs="+", default=None, help="Config files.")
    parser.add_argument("--patch-sets-json", default="", help="Patch-set list encoded as JSON.")
    parser.add_argument("--resume-test-branch", default=None, help="Existing test branch to resume.")
    parser.add_argument("--resume-set-index", type=int, default=0, help="Patch set index to resume from.")
    parser.add_argument("--resume-commit-index", type=int, default=1, help="Commit index to resume from.")
    parser.add_argument("--after-continue", action="store_true", help="Validate current patch at HEAD, then continue.")
    parser.add_argument("--reconcile", action="store_true", help="Rebuild progress from test branch history.")
    parser.add_argument("--accept-semantic-substitution", action="store_true", help="Accept semantic substitution.")
    parser.add_argument("--accept-hunk-recovery", default=None, help="Accept hunk recovery: ignore-and-continue or stop-and-abort.")
    parser.add_argument("--resume-after-fix", action="store_true", help="Resume after manual fix from needs_human state.")
    parser.add_argument(
        "--human-decision",
        default=None,
        help="Explicit decision for needs_human: continue|accept-semantic|accept-hunk|abort.",
    )
    parser.add_argument("--state-file", default=None, help="Optional state file path.")
    parser.add_argument("--max-iteration-per-patch", type=int, default=4, help="Max auto-revalidation iterations.")

    args = parser.parse_args()

    try:
        payload = _load_cli_payload(args)
    except ValueError as exc:
        return emit_json({
            "success": False,
            "next_action": "stop_invalid_input",
            "error": str(exc),
        })

    payload["max_iteration_per_patch"] = args.max_iteration_per_patch

    result = run_patch_sets(
        payload=payload,
        resume_test_branch=args.resume_test_branch,
        resume_set_index=args.resume_set_index,
        resume_commit_index=args.resume_commit_index,
        after_continue=args.after_continue,
        reconcile=args.reconcile,
        accept_semantic_substitution=args.accept_semantic_substitution,
        accept_hunk_recovery=args.accept_hunk_recovery,
        resume_after_fix=args.resume_after_fix,
        human_decision=args.human_decision,
        state_file=args.state_file,
    )

    return emit_json(json.loads(result))


if __name__ == "__main__":
    raise SystemExit(main())
