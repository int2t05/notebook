"""Build repair plans from post-apply gate results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


RETRYABLE_STATUSES = {
    "missing-hunk",
    "semantic-substitution-suspected",
    "different",
}

NON_REPAIRABLE_STATUSES = {
    "missing-file",
    "extra-file",
    "config-unmapped",
    "config-target-missing",
    "config-mapped-incomplete",
}


@dataclass
class RepairPlan:
    should_repair: bool
    strategy: str
    reason: str
    target_files: List[str] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)


def build_repair_plan(validation: dict) -> RepairPlan:
    if not validation.get("success"):
        return RepairPlan(False, "none", "validation-failed")

    status = str(validation.get("status") or "")
    if status in NON_REPAIRABLE_STATUSES:
        return RepairPlan(False, "none", f"non-repairable-status:{status}")
    if status not in RETRYABLE_STATUSES:
        return RepairPlan(False, "none", f"unsupported-status:{status}")

    issues = validation.get("issues") or []
    target_files: List[str] = []
    issue_statuses: List[str] = []
    repairable_issues: List[Dict[str, Any]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue_status = str(issue.get("status") or "")
        issue_statuses.append(issue_status)
        if issue_status in NON_REPAIRABLE_STATUSES:
            return RepairPlan(False, "none", f"non-repairable-issue:{issue_status}")
        if issue_status not in RETRYABLE_STATUSES and issue_status != "identical":
            return RepairPlan(False, "none", f"unsupported-issue:{issue_status}")
        path = issue.get("path") or issue.get("target_file") or issue.get("source_file")
        if isinstance(path, str) and path and path not in target_files:
            target_files.append(path)
        if issue_status in RETRYABLE_STATUSES:
            repairable_issues.append(issue)

    if not repairable_issues:
        return RepairPlan(False, "none", "no-repairable-issues")

    return RepairPlan(
        should_repair=True,
        strategy="reapply-patch-hunks",
        reason="retryable-validation-status",
        target_files=target_files,
        statuses=issue_statuses,
        issues=repairable_issues,
    )
