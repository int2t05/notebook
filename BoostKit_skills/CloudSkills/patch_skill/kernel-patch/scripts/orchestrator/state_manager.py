#!/usr/bin/env python3
"""统一状态管理器"""

from __future__ import annotations
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from .state_machine import StateMachine, Phase, TERMINAL_PHASES, ACTIVE_PHASES

logger = logging.getLogger(__name__)


class StateManager:
    """统一状态管理器 - 管理单一状态文件"""

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self._state: Optional[Dict[str, Any]] = None

    @property
    def state(self) -> Dict[str, Any]:
        """获取状态（延迟加载）"""
        if self._state is None:
            self._state = self._load()
        return self._state

    def _load(self) -> Dict[str, Any]:
        """加载状态文件"""
        if not self.state_file.exists():
            return self._create_empty_state()
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _create_empty_state(self) -> Dict[str, Any]:
        """创建空状态"""
        return {
            "task_id": None,
            "skill": "kernel-patch",
            "version": 2,
            "phase": Phase.IDLE.value,
            "config": {},
            "progress": {
                "expected_commit_count": 0,
                "applied_commit_count": 0,
                "current_patch_set": None,
                "current_patch_set_index": 0,
                "current_commit_index": 0,
                "current_commit_id": None,
                "current_patch_file": None,
            },
            "iteration": {"current": 0, "max": 4},
            "runtime": {
                "last_observed_commit_ref": None,
                "last_validation_status": None,
                "review_handoff_ready": False,
                "escalation_reason": None,
                "exported_patch_index": {},
                "artifacts": {},
            },
            "llm": {
                "summary": "任务尚未开始。",
                "next_action": None,
                "history": [],
            },
            "final": {
                "final_head": None,
                "review_prompt": None,
                "completed_at": None,
            },
        }

    def save(self):
        """保存状态（事务式写入）"""
        # 更新 summary
        self.state["llm"]["summary"] = self._generate_summary()

        # 确保目录存在
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # 事务式写入
        temp_file = self.state_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            temp_file.rename(self.state_file)
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def transition(self, new_phase: str, **kwargs) -> Dict[str, Any]:
        """执行状态转换"""
        old_phase = self.state.get("phase")

        # 验证状态转换
        if old_phase and old_phase != new_phase and not StateMachine.can_transition(old_phase, new_phase):
            raise ValueError(f"Invalid phase transition: {old_phase} -> {new_phase}")

        # 更新状态
        self.state["phase"] = new_phase
        for key, value in kwargs.items():
            if "." in key:
                # 支持嵌套更新，如 "progress.applied_commit_count"
                parts = key.split(".")
                obj = self.state
                for part in parts[:-1]:
                    obj = obj.setdefault(part, {})
                obj[parts[-1]] = value
            else:
                self.state[key] = value

        # 记录历史
        self._add_history(old_phase, new_phase)

        # 保存
        self.save()

        logger.info(f"Phase transition: {old_phase} -> {new_phase}")
        return self.state

    def update(self, **kwargs):
        """更新状态（不改变阶段）"""
        for key, value in kwargs.items():
            if "." in key:
                parts = key.split(".")
                obj = self.state
                for part in parts[:-1]:
                    obj = obj.setdefault(part, {})
                obj[parts[-1]] = value
            else:
                self.state[key] = value
        self.save()

    def _generate_summary(self) -> str:
        """根据当前状态自动生成摘要"""
        phase = self.state.get("phase", "idle")
        progress = self.state.get("progress", {})
        applied = progress.get("applied_commit_count", 0)
        total = progress.get("expected_commit_count", 0)
        patch_set = progress.get("current_patch_set", "N/A")
        commit_idx = progress.get("current_commit_index")
        iteration = self.state.get("iteration", {}).get("current", 0)
        runtime = self.state.get("runtime", {})
        last_status = runtime.get("last_validation_status")

        templates = {
            "idle": "任务尚未开始。",
            "running": (
                f"任务进行中，已记录 {applied}/{total} 个补丁；"
                f"当前位置 {patch_set} 第 {(commit_idx or 0) + 1} 个补丁；"
                f"当前自动轮次 {iteration}。"
            ) if commit_idx is not None else f"任务进行中，已记录 {applied}/{total} 个补丁。",
            "revalidating": (
                f"任务停在自动复检阶段，已记录 {applied}/{total} 个补丁；"
                f"上一轮状态 {last_status or 'unknown'}。"
            ),
            "auto_fixing": (
                f"任务停在自动修复阶段，已记录 {applied}/{total} 个补丁；"
                f"当前自动轮次 {iteration}。"
            ),
            "waiting_after_continue": (
                f"任务停在冲突恢复后续跑阶段，已记录 {applied}/{total} 个补丁；"
                f"下一步应先处理 git am --continue 后续验证。"
            ),
            "waiting_semantic_confirmation": (
                f"任务停在语义替代确认阶段，已记录 {applied}/{total} 个补丁；"
                f"下一步应先确认当前 patch 的语义适配。"
            ),
            "waiting_hunk_confirmation": (
                f"任务停在 hunk 恢复确认阶段，已记录 {applied}/{total} 个补丁；"
                f"下一步应先确认 missing-hunk 的恢复策略。"
            ),
            "completed_pending_review": (
                f"合入阶段已完成，共记录 {applied}/{total} 个补丁，等待拉起 patch-validator。"
            ),
            "ended": f"任务已结束，共记录 {applied}/{total} 个补丁。",
            "aborted": f"任务异常停止，停在 {patch_set}；已记录 {applied}/{total} 个补丁。",
            "needs_human": (
                f"任务已阻塞并需人工修复，停在 {patch_set}；已记录 {applied}/{total} 个补丁；"
                f"原因 {runtime.get('escalation_reason') or 'unknown'}；当前不可自动续跑。"
            ),
        }
        return templates.get(phase, "任务状态未知。")

    def _add_history(self, old_phase: Optional[str], new_phase: str):
        """添加状态转换历史"""
        history = self.state.setdefault("llm", {}).setdefault("history", [])
        history.append({
            "time": datetime.now().isoformat(),
            "from_phase": old_phase,
            "to_phase": new_phase,
        })
        # 只保留最近 20 条
        if len(history) > 20:
            history[:] = history[-20:]

    def get_program_view(self) -> Dict[str, Any]:
        """返回程序需要的视图"""
        return {
            "phase": self.state["phase"],
            "config": self.state["config"],
            "progress": self.state["progress"],
            "iteration": self.state["iteration"],
            "runtime": self.state["runtime"],
        }

    def get_llm_view(self) -> Dict[str, Any]:
        """返回 LLM 需要的视图"""
        progress = self.state["progress"]
        return {
            "task_id": self.state["task_id"],
            "phase": self.state["phase"],
            "summary": self.state["llm"]["summary"],
            "progress": {
                "applied": progress["applied_commit_count"],
                "total": progress["expected_commit_count"],
                "current": f"{progress['current_patch_set']} 第 {progress['current_commit_index'] + 1} 个",
            },
            "config": {
                "target_repo": self.state["config"].get("target_repo"),
                "target_branch": self.state["config"].get("target_branch"),
                "test_branch": self.state["config"].get("test_branch"),
            },
            "next_action": self.state["llm"].get("next_action"),
            "history": self.state["llm"]["history"][-10:],
        }

    # === 向后兼容方法 ===

    def get_task_status(self) -> str:
        """向后兼容：返回 task_status"""
        return self.state["phase"]

    def get_applied_count(self) -> int:
        """向后兼容：返回 applied_commit_count"""
        return self.state["progress"]["applied_commit_count"]

    def is_active(self) -> bool:
        """判断是否是活跃状态"""
        return StateMachine.is_active(self.state["phase"])

    def is_terminal(self) -> bool:
        """判断是否是终端状态"""
        return StateMachine.is_terminal(self.state["phase"])
