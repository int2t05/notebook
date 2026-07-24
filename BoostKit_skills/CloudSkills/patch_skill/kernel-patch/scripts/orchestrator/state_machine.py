"""State machine module for kernel-patch orchestrator."""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class Phase(Enum):
    """补丁合入阶段"""
    IDLE = "idle"
    RUNNING = "running"
    REVALIDATING = "revalidating"
    AUTO_FIXING = "auto_fixing"
    WAITING_AFTER_CONTINUE = "waiting_after_continue"
    WAITING_SEMANTIC_CONFIRMATION = "waiting_semantic_confirmation"
    WAITING_HUNK_CONFIRMATION = "waiting_hunk_confirmation"
    COMPLETED_PENDING_REVIEW = "completed_pending_review"
    NEEDS_HUMAN = "needs_human"
    ABORTED = "aborted"
    ENDED = "ended"


# 状态分类（向后兼容）
ACTIVE_PHASES: Set[str] = {
    Phase.RUNNING.value,
    Phase.REVALIDATING.value,
    Phase.AUTO_FIXING.value,
    Phase.WAITING_AFTER_CONTINUE.value,
    Phase.WAITING_SEMANTIC_CONFIRMATION.value,
    Phase.WAITING_HUNK_CONFIRMATION.value,
    Phase.COMPLETED_PENDING_REVIEW.value,
}

BLOCKED_PHASES: Set[str] = {
    Phase.NEEDS_HUMAN.value,
}

TERMINAL_PHASES: Set[str] = {
    Phase.ABORTED.value,
    Phase.ENDED.value,
}


class StateMachine:
    """轻量级状态机"""

    # 定义合法的状态转换
    VALID_TRANSITIONS: Dict[str, List[str]] = {
        Phase.IDLE.value: [Phase.RUNNING.value],
        Phase.RUNNING.value: [
            Phase.RUNNING.value,  # 允许继续运行（处理多个补丁）
            Phase.REVALIDATING.value,
            Phase.AUTO_FIXING.value,
            Phase.WAITING_AFTER_CONTINUE.value,
            Phase.WAITING_SEMANTIC_CONFIRMATION.value,
            Phase.WAITING_HUNK_CONFIRMATION.value,
            Phase.COMPLETED_PENDING_REVIEW.value,
            Phase.NEEDS_HUMAN.value,
            Phase.ABORTED.value,
        ],
        Phase.REVALIDATING.value: [
            Phase.RUNNING.value,
            Phase.AUTO_FIXING.value,
            Phase.NEEDS_HUMAN.value,
            Phase.ABORTED.value,
        ],
        Phase.AUTO_FIXING.value: [
            Phase.REVALIDATING.value,
            Phase.NEEDS_HUMAN.value,
            Phase.ABORTED.value,
        ],
        Phase.WAITING_AFTER_CONTINUE.value: [
            Phase.RUNNING.value,
            Phase.NEEDS_HUMAN.value,
            Phase.ABORTED.value,
        ],
        Phase.WAITING_SEMANTIC_CONFIRMATION.value: [
            Phase.RUNNING.value,
            Phase.ABORTED.value,
        ],
        Phase.WAITING_HUNK_CONFIRMATION.value: [
            Phase.RUNNING.value,
            Phase.ABORTED.value,
        ],
        Phase.NEEDS_HUMAN.value: [
            Phase.RUNNING.value,
            Phase.WAITING_SEMANTIC_CONFIRMATION.value,
            Phase.WAITING_HUNK_CONFIRMATION.value,
            Phase.ABORTED.value,
        ],
        Phase.COMPLETED_PENDING_REVIEW.value: [
            Phase.ENDED.value,
        ],
    }

    @classmethod
    def can_transition(cls, from_phase: str, to_phase: str) -> bool:
        """检查状态转换是否合法"""
        if from_phase in TERMINAL_PHASES:
            return False
        valid_targets = cls.VALID_TRANSITIONS.get(from_phase, [])
        return to_phase in valid_targets

    @classmethod
    def get_valid_transitions(cls, from_phase: str) -> List[str]:
        """获取合法的转换目标"""
        return cls.VALID_TRANSITIONS.get(from_phase, [])

    @classmethod
    def is_active(cls, phase: str | None) -> bool:
        """判断是否是活跃阶段"""
        return bool(phase) and phase in ACTIVE_PHASES

    @classmethod
    def is_blocked(cls, phase: str | None) -> bool:
        """判断是否是阻塞阶段"""
        return bool(phase) and phase in BLOCKED_PHASES

    @classmethod
    def is_terminal(cls, phase: str | None) -> bool:
        """判断是否是终端阶段"""
        return bool(phase) and phase in TERMINAL_PHASES


# === 向后兼容的函数 ===

def is_active_phase(phase: str | None) -> bool:
    """向后兼容：判断是否是活跃阶段"""
    return StateMachine.is_active(phase)


def is_blocked_phase(phase: str | None) -> bool:
    """向后兼容：判断是否是阻塞阶段"""
    return StateMachine.is_blocked(phase)


def update_state_phase(state: dict[str, Any], phase: str) -> dict[str, Any]:
    """向后兼容：更新状态阶段"""
    old_phase = state.get("phase")
    if old_phase and not StateMachine.can_transition(old_phase, phase):
        raise ValueError(f"Invalid phase transition: {old_phase} -> {phase}")
    state["phase"] = phase
    return state


def visualize_state_machine() -> str:
    """生成状态机图（Mermaid 格式）"""
    lines = ["stateDiagram-v2"]
    for from_phase, to_phases in StateMachine.VALID_TRANSITIONS.items():
        for to_phase in to_phases:
            lines.append(f"    {from_phase} --> {to_phase}")
    return "\n".join(lines)
