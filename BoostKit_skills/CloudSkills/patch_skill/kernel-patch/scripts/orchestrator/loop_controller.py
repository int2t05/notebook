"""Auto-loop decisions for per-patch validation retries."""

from __future__ import annotations

from dataclasses import dataclass


RETRYABLE_STATUSES = {
    "missing-hunk",
    "semantic-substitution-suspected",
    "different",
}


@dataclass
class LoopDecision:
    should_retry: bool
    should_escalate: bool
    iteration: int
    reason: str


def decide_retry(status: str | None, iteration: int, max_iteration: int) -> LoopDecision:
    if status not in RETRYABLE_STATUSES:
        return LoopDecision(False, True, iteration, "fatal-validation-status")
    next_iteration = iteration + 1
    if next_iteration >= max_iteration:
        return LoopDecision(False, True, next_iteration, "max-iteration-reached")
    return LoopDecision(True, False, next_iteration, "retryable-validation-status")

