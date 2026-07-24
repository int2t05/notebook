#!/usr/bin/env python3
"""Deterministic post-apply gate for a single patch commit pair."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from shared.config import VALIDATION_PASS_STATUSES
from validate_applied_patch import validate_applied_patch

RETRYABLE_GATE_STATUSES = {
    "missing-hunk",
    "semantic-substitution-suspected",
    "different",
}

FATAL_GATE_STATUSES = {
    "missing-file",
    "extra-file",
    "config-unmapped",
    "config-target-missing",
    "config-mapped-incomplete",
}


def _artifact_path(patches_dir: str, commit_id: str, iteration: int) -> str:
    artifacts_dir = os.path.join(patches_dir, ".kernel_patch_artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    safe_commit = commit_id.replace("/", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(artifacts_dir, f"{safe_commit}.iter{iteration}.{ts}.gate.json")


def evaluate_patch_commit(
    *,
    patch_file: str,
    repo_path: str,
    commit_ref: str,
    config_targets: Optional[Dict[str, List[str]]] = None,
    prior_patch_files: Optional[List[str]] = None,
    patches_dir: str,
    commit_id: str,
    iteration: int,
) -> dict:
    validation = json.loads(validate_applied_patch(
        patch_file=patch_file,
        repo_path=repo_path,
        commit_ref=commit_ref,
        config_targets=config_targets or {},
        prior_patch_files=prior_patch_files or [],
    ))
    status = validation.get("status")
    evidence = validation.get("evidence") if isinstance(validation.get("evidence"), dict) else {}
    source_analysis = (
        evidence.get("source_analysis")
        if isinstance(evidence.get("source_analysis"), dict)
        else validation.get("source_analysis") or {}
    )
    source_level = source_analysis.get("auto_continue_level")
    source_confidence = source_analysis.get("confidence")
    auto_continue_eligible = source_analysis.get("auto_continue_eligible")
    if auto_continue_eligible is None:
        auto_continue_eligible = (
            bool(source_analysis.get("auto_continue"))
            and (source_level == "high" or source_confidence == "high")
        )
    source_auto_continue = bool(
        status == "missing-hunk"
        and isinstance(source_analysis, dict)
        and auto_continue_eligible
    )
    if validation.get("success") and (status in VALIDATION_PASS_STATUSES or source_auto_continue):
        verdict = "pass"
        if source_auto_continue:
            status = "missing-hunk-source-confirmed"
    elif status in RETRYABLE_GATE_STATUSES:
        verdict = "retryable_fail"
    elif status in FATAL_GATE_STATUSES:
        verdict = "fatal_fail"
    else:
        verdict = "fatal_fail"

    payload = {
        "verdict": verdict,
        "status": status,
        "repairability": "auto" if verdict == "retryable_fail" else ("none" if verdict == "pass" else "manual"),
        "validation": validation,
        "validation_evidence": evidence,
        "commit_ref": commit_ref,
        "commit_id": commit_id,
        "iteration": iteration,
    }
    artifact = _artifact_path(patches_dir, commit_id=commit_id, iteration=iteration)
    with open(artifact, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    payload["artifact_path"] = artifact
    return payload
