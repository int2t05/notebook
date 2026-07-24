#!/usr/bin/env python3
"""补丁合入工作流"""

from __future__ import annotations
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# 添加父目录到路径
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from .state_manager import StateManager
from .state_machine import Phase, StateMachine

logger = logging.getLogger(__name__)
DECISION_OPTIONS: List[str] = ["continue", "accept-semantic", "accept-hunk", "abort"]


class PatchWorkflow:
    """补丁合入工作流"""

    def __init__(
        self,
        config: Dict[str, Any],
        state_manager: StateManager,
    ):
        self.config = config
        self.state_manager = state_manager
        self.results: List[Dict[str, Any]] = []

    def _recommended_decisions_for_reason(self, reason: str | None) -> List[str]:
        normalized = (reason or "unknown").strip().lower()
        if normalized in {"semantic-substitution-suspected"}:
            return ["accept-semantic", "continue", "abort"]
        if normalized in {"missing-hunk", "missing-hunk-source-confirmed"}:
            return ["accept-hunk", "continue", "abort"]
        if normalized in {"apply_failed", "conflict_detected"}:
            return ["continue", "abort"]
        return ["continue", "abort"]

    def _decision_hint_payload(self, reason: str | None) -> Dict[str, Any]:
        return {
            "decision_required": True,
            "decision_options": DECISION_OPTIONS,
            "recommended_decisions": self._recommended_decisions_for_reason(reason),
        }

    def _extract_evidence_snapshot(self, validation_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        validation_payload = validation_result.get("validation", {})
        if not isinstance(validation_payload, dict):
            return None
        evidence = validation_payload.get("evidence")
        if not isinstance(evidence, dict):
            return None
        summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
        signals = evidence.get("signals") if isinstance(evidence.get("signals"), list) else []
        signal_codes = [
            item.get("code")
            for item in signals
            if isinstance(item, dict) and isinstance(item.get("code"), str)
        ]
        return {
            "status": validation_result.get("status") or validation_payload.get("status"),
            "issue_count": summary.get("issue_count", 0),
            "line_stats": summary.get("line_stats", {}),
            "signal_codes": signal_codes[:8],
            "source_analysis": evidence.get("source_analysis", {}),
        }

    def run(self) -> str:
        """执行工作流"""
        try:
            # 初始化
            self._initialize()

            # 主循环
            patch_sets = self.config.get("patch_sets", [])
            progress = self.state_manager.state["progress"]
            set_index = progress.get("current_patch_set_index", 0)
            commit_index = progress.get("current_commit_index", 0)

            for set_idx in range(set_index, len(patch_sets)):
                patch_set = patch_sets[set_idx]
                commits = patch_set.get("commits", [])

                start_commit_idx = commit_index if set_idx == set_index else 0
                for c_idx in range(start_commit_idx, len(commits)):
                    commit_id = commits[c_idx]

                    # 处理单个补丁
                    result = self._process_single_patch(
                        patch_set=patch_set,
                        set_index=set_idx,
                        commit_index=c_idx,
                        commit_id=commit_id,
                    )
                    self.results.append(result)

                    # 检查是否需要停止
                    if result.get("stop"):
                        return self._build_response(result)

            # 完成
            return self._complete()

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return self._handle_error(e)

    def _initialize(self):
        """初始化工作流"""
        if not self.state_manager.state.get("task_id"):
            self.state_manager.state["task_id"] = (
                f"kernel-patch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )

        # 计算预期提交数
        total_commits = sum(
            len(ps.get("commits", []))
            for ps in self.config.get("patch_sets", [])
        )

        # 检查是否已有测试分支（用于复用）
        existing_test_branch = self.state_manager.state.get("config", {}).get("test_branch")

        self.state_manager.transition(
            Phase.RUNNING.value,
            **{
                "config": {
                    "target_repo": self.config.get("target_repo"),
                    "target_branch": self.config.get("target_branch"),
                    "test_branch": existing_test_branch or self.config.get("test_branch"),
                    "patches_dir": self.config.get("patches_dir"),
                    "config_files": self.config.get("config_files", []),
                    "patch_sets": self.config.get("patch_sets", []),
                    "reject_dir": self.config.get("reject_dir"),
                },
                "progress.expected_commit_count": total_commits,
            }
        )

    def _process_single_patch(
        self,
        patch_set: Dict[str, Any],
        set_index: int,
        commit_index: int,
        commit_id: str,
    ) -> Dict[str, Any]:
        """处理单个补丁"""
        # 更新进度
        self.state_manager.update(
            **{
                "progress.current_patch_set": patch_set.get("name"),
                "progress.current_patch_set_index": set_index,
                "progress.current_commit_index": commit_index,
                "progress.current_commit_id": commit_id,
            }
        )

        # 1. 导出补丁
        patch_file = self._export_patch(patch_set, commit_id)
        if not patch_file:
            return {"success": False, "stop": True, "reason": "export_failed"}

        self.state_manager.update(**{"progress.current_patch_file": patch_file})

        # 2. 应用补丁
        apply_result = self._apply_patch(patch_file)

        # 检查冲突
        if apply_result.get("git_am_status") == "paused":
            return self._handle_conflict(apply_result)

        if not apply_result.get("success"):
            return self._handle_apply_failure(apply_result)

        # 3. 验证补丁
        validation_result = self._validate_patch(patch_file, apply_result)

        # 处理验证结果
        return self._handle_validation_result(validation_result)

    def _export_patch(self, patch_set: Dict[str, Any], commit_id: str) -> Optional[str]:
        """导出补丁"""
        # 检查缓存
        cache = self.state_manager.state.get("runtime", {}).get("exported_patch_index", {})
        if commit_id in cache:
            cached_path = cache[commit_id].get("patch_str")
            if cached_path and os.path.isfile(cached_path):
                return cached_path

        # 导出
        from export_patches import export_patches

        result = json.loads(export_patches(
            repo_path=patch_set["source_repo"],
            commit_ids=[commit_id],
            output_dir=self.config["patches_dir"],
        ))

        if not result.get("success"):
            logger.error(f"Failed to export patch for {commit_id}")
            return None

        exported = result.get("exported_patches", {}).get(commit_id, {})
        patch_file = exported.get("patch_str")

        # 更新缓存
        if patch_file:
            runtime_cache = self.state_manager.state.setdefault("runtime", {})
            patch_cache = runtime_cache.setdefault("exported_patch_index", {})
            patch_cache[commit_id] = {"patch_str": patch_file, "commit_msg": exported.get("commit_msg")}
            self.state_manager.save()

        return patch_file

    def _apply_patch(self, patch_file: str) -> Dict[str, Any]:
        """应用补丁"""
        from apply_patches import apply_single_patch

        test_branch = self.state_manager.state["config"].get("test_branch")

        result = apply_single_patch(
            patch_file=patch_file,
            target_repo_path=self.config["target_repo"],
            target_branch=self.config["target_branch"],
            reject_dir=self.config.get("reject_dir", "rejects"),
            test_branch=test_branch,
        )

        result_data = json.loads(result)

        # 更新 test_branch
        if result_data.get("test_branch"):
            self.state_manager.update(**{"config.test_branch": result_data["test_branch"]})

        return result_data

    def _validate_patch(
        self,
        patch_file: str,
        apply_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证补丁"""
        from post_apply_gate import evaluate_patch_commit

        progress = self.state_manager.state["progress"]

        return evaluate_patch_commit(
            patch_file=patch_file,
            repo_path=self.config["target_repo"],
            commit_ref=apply_result.get("applied_commit") or "HEAD",
            config_targets=self._build_config_targets(patch_file),
            prior_patch_files=self._resolve_prior_patch_files(progress["current_patch_set_index"], progress["current_commit_index"]),
            patches_dir=self.config["patches_dir"],
            commit_id=progress["current_commit_id"],
            iteration=self.state_manager.state["iteration"]["current"],
        )

    def _build_config_targets(self, patch_file: str) -> Optional[Dict[str, List[str]]]:
        """Build config target mapping.

        Parses the patch file for source config paths (e.g. defconfig),
        and maps them to the user-provided config_files target list.
        """
        config_files = self.config.get("config_files", [])
        if not config_files:
            return None

        from shared.config import is_config_mapping_source_path
        try:
            with open(patch_file, "r", encoding="utf-8", errors="ignore") as f:
                patch_text = f.read()
            from validate_applied_patch import _parse_patch_text
            local_files = _parse_patch_text(patch_text)
            source_paths = [p for p in local_files if is_config_mapping_source_path(p)]
        except Exception:
            source_paths = []

        if not source_paths:
            # No config source paths in patch; return identity mapping for backward compat
            return {path: [path] for path in config_files}

        config_targets: Dict[str, List[str]] = {}
        for source_path in source_paths:
            config_targets[source_path] = list(config_files)
        return config_targets

    def _resolve_prior_patch_files(self, set_index: int, commit_index: int) -> List[str]:
        """解析之前的补丁文件"""
        prior_files = []
        patch_sets = self.config.get("patch_sets", [])
        cache = self.state_manager.state.get("runtime", {}).get("exported_patch_index", {})

        for i, ps in enumerate(patch_sets):
            if i > set_index:
                break
            commits = ps.get("commits", [])
            end_idx = commit_index if i == set_index else len(commits)
            for j in range(end_idx):
                if j < len(commits):
                    commit_id = commits[j]
                    if commit_id in cache:
                        pf = cache[commit_id].get("patch_str")
                        if pf:
                            prior_files.append(pf)

        return prior_files

    def _handle_validation_result(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证结果"""
        # 检查顶层 verdict (来自 gate 校验)
        verdict = validation_result.get("verdict")
        # 兼容两种格式：顶层 success 或嵌套的 validation.success
        success = validation_result.get("success") or validation_result.get("validation", {}).get("success")

        # 如果 verdict 是 pass，直接处理成功
        if verdict == "pass":
            status = validation_result.get("status")
            # 如果当前不在 RUNNING 状态（如 REVALIDATING），先转回 RUNNING
            current_phase = self.state_manager.state.get("phase")
            if current_phase != Phase.RUNNING.value:
                self.state_manager.transition(Phase.RUNNING.value)
            self._advance_after_success(status=status)
            return {"success": True, "stop": False}

        # 失败情况
        if not success and verdict != "pass":
            return self._handle_validation_failure(validation_result)

        status = validation_result.get("status")

        # 兜底通过（verdict 非 pass 但 status 为 pass — 不应发生）
        if status in {"identical", "config-mapped-equivalent"}:
            logger.warning(
                "Unexpected: verdict=%s but status=%s, treating as pass",
                verdict, status,
            )
            self._advance_after_success(status=status)
            return {"success": True, "stop": False}

        # 需要确认
        if status == "semantic-substitution-suspected":
            return self._handle_semantic_confirmation(validation_result)

        # hunk 恢复确认
        if status == "missing-hunk":
            source_analysis = validation_result.get("validation", {}).get("source_analysis", {})
            if (
                source_analysis.get("auto_continue")
                and source_analysis.get("confidence") == "high"
            ):
                self._advance_after_success(status="missing-hunk-source-confirmed")
                return {"success": True, "stop": False}
            return self._handle_hunk_confirmation(validation_result)

        # 可重试
        if status == "different":
            return self._handle_auto_repair(validation_result)

        # 失败
        return self._handle_validation_failure(validation_result)

    def _handle_conflict(self, apply_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理冲突"""
        self.state_manager.transition(
            Phase.WAITING_AFTER_CONTINUE.value,
            **{
                "runtime.escalation_reason": "conflict_detected",
            }
        )

        return {
            "success": False,
            "stop": True,
            "next_action": "resolve_conflicts",
            "message": "Patch application paused due to conflicts",
            "conflict_files": apply_result.get("repo_relative_conflict_files", []),
        }

    def _handle_semantic_confirmation(
        self,
        validation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """处理语义确认"""
        evidence_snapshot = self._extract_evidence_snapshot(validation_result)
        self.state_manager.transition(
            Phase.WAITING_SEMANTIC_CONFIRMATION.value,
            **{
                "runtime.last_validation_status": validation_result.get("status"),
                "runtime.last_evidence_snapshot": evidence_snapshot,
            }
        )

        return {
            "success": False,
            "stop": True,
            "next_action": "confirm_semantic_substitution",
            "message": "Semantic substitution suspected, needs confirmation",
            "validation": validation_result,
            "evidence_snapshot": evidence_snapshot,
        }

    def _handle_hunk_confirmation(
        self,
        validation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """处理 hunk 确认"""
        evidence_snapshot = self._extract_evidence_snapshot(validation_result)
        self.state_manager.transition(
            Phase.WAITING_HUNK_CONFIRMATION.value,
            **{
                "runtime.last_validation_status": validation_result.get("status"),
                "runtime.last_evidence_snapshot": evidence_snapshot,
            }
        )

        return {
            "success": False,
            "stop": True,
            "next_action": "confirm_hunk_recovery",
            "message": "Missing hunk detected, needs confirmation",
            "validation": validation_result,
            "evidence_snapshot": evidence_snapshot,
        }

    def _handle_auto_repair(
        self,
        validation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """处理自动修复"""
        max_iteration = self.state_manager.state["iteration"]["max"]
        current_iteration = self.state_manager.state["iteration"]["current"]

        if current_iteration >= max_iteration:
            # 达到最大重试次数
            current_head = self._read_head_commit()
            evidence_snapshot = self._extract_evidence_snapshot(validation_result)
            self.state_manager.transition(
                Phase.NEEDS_HUMAN.value,
                **{
                    "runtime.escalation_reason": "max_iteration_reached",
                    "runtime.last_validation_status": validation_result.get("status"),
                    "runtime.last_observed_commit_ref": current_head,
                    "runtime.last_evidence_snapshot": evidence_snapshot,
                }
            )
            return {
                "success": False,
                "stop": True,
                "next_action": "escalate_human",
                "message": f"Max auto-repair iterations ({max_iteration}) reached",
                "evidence_snapshot": evidence_snapshot,
                **self._decision_hint_payload(validation_result.get("status")),
            }

        # 执行自动修复
        self.state_manager.transition(
            Phase.AUTO_FIXING.value,
            **{
                "iteration.current": current_iteration + 1,
                "runtime.last_validation_status": validation_result.get("status"),
            }
        )

        repair_result = self._execute_repair(validation_result)

        if repair_result.get("success"):
            # 修复成功，只重新验证（不重新 apply）
            self.state_manager.transition(Phase.REVALIDATING.value)

            progress = self.state_manager.state["progress"]
            patch_file = progress.get("current_patch_file")
            if not patch_file or not os.path.isfile(patch_file):
                return self._handle_validation_failure(repair_result)

            # 直接对当前 HEAD 做 validate，跳过 apply 步骤
            revalidate_result = self._validate_patch(
                patch_file,
                {"applied_commit": "HEAD"},
            )
            return self._handle_validation_result(revalidate_result)
        else:
            # 修复失败 — 但如果原因是 repair-noop，先验证 HEAD 是否已通过
            if repair_result.get("reason") == "repair-noop":
                progress = self.state_manager.state["progress"]
                patch_file = progress.get("current_patch_file")
                if patch_file and os.path.isfile(patch_file):
                    # 先转到 REVALIDATING（与修复成功路径一致）
                    self.state_manager.transition(Phase.REVALIDATING.value)
                    revalidate_result = self._validate_patch(
                        patch_file, {"applied_commit": "HEAD"},
                    )
                    verdict = revalidate_result.get("verdict")
                    if verdict == "pass":
                        # HEAD 已通过验证，直接推进
                        return self._handle_validation_result(revalidate_result)

            return self._handle_validation_failure(
                self._normalize_failure_payload(
                    validation_result=validation_result,
                    repair_result=repair_result,
                )
            )

    def _execute_repair(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """执行自动修复"""
        from orchestrator.repair_planner import build_repair_plan
        from orchestrator.repair_actions import apply_repair_plan

        plan = build_repair_plan(validation_result.get("validation", {}))

        if not plan.should_repair:
            return {"success": False, "reason": plan.reason}

        progress = self.state_manager.state["progress"]

        return apply_repair_plan(
            repo_path=self.config["target_repo"],
            patch_file=progress["current_patch_file"],
            patches_dir=self.config["patches_dir"],
            commit_id=progress["current_commit_id"],
            iteration=self.state_manager.state["iteration"]["current"],
            target_files=plan.target_files,
        )

    def _handle_validation_failure(
        self,
        validation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """处理验证失败"""
        status = validation_result.get("status") or "validation_failed"
        current_head = self._read_head_commit()
        evidence_snapshot = self._extract_evidence_snapshot(validation_result)
        self.state_manager.transition(
            Phase.NEEDS_HUMAN.value,
            **{
                "runtime.escalation_reason": status,
                "runtime.last_validation_status": status,
                "runtime.last_observed_commit_ref": current_head,
                "runtime.last_evidence_snapshot": evidence_snapshot,
            }
        )

        return {
            "success": False,
            "stop": True,
            "next_action": "escalate_human",
            "message": f"Validation failed: {status}",
            "validation": validation_result,
            "evidence_snapshot": evidence_snapshot,
            **self._decision_hint_payload(status),
            "decision_context": {
                "status": status,
                "commit_id": self.state_manager.state.get("progress", {}).get("current_commit_id"),
                "last_observed_commit_ref": current_head,
            },
        }

    def _handle_apply_failure(self, apply_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理应用失败"""
        current_head = self._read_head_commit()
        self.state_manager.transition(
            Phase.NEEDS_HUMAN.value,
            **{
                "runtime.escalation_reason": apply_result.get("error") or "apply_failed",
                "runtime.last_observed_commit_ref": current_head,
            }
        )

        return {
            "success": False,
            "stop": True,
            "next_action": "escalate_human",
            "message": f"Patch apply failed: {apply_result.get('error')}",
            **self._decision_hint_payload("apply_failed"),
            "decision_context": {
                "status": "apply_failed",
                "commit_id": self.state_manager.state.get("progress", {}).get("current_commit_id"),
                "last_observed_commit_ref": current_head,
            },
        }

    def _complete(self) -> str:
        """完成工作流"""
        final_head = self._read_head_commit()
        review_prompt = self._build_review_prompt()

        self.state_manager.transition(
            Phase.COMPLETED_PENDING_REVIEW.value,
            **{
                "final.final_head": final_head,
                "final.review_prompt": review_prompt,
            }
        )

        return json.dumps({
            "success": True,
            "next_action": "handoff_review",
            "review_prompt": review_prompt,
            "results": self.results,
            "final_head": final_head,
        }, ensure_ascii=False, indent=2)

    def _handle_error(self, error: Exception) -> str:
        """处理错误"""
        self.state_manager.transition(
            Phase.ABORTED.value,
            **{
                "runtime.escalation_reason": str(error),
            }
        )

        return json.dumps({
            "success": False,
            "next_action": "stop_manual_recovery_required",
            "error": str(error),
        }, ensure_ascii=False, indent=2)

    def _read_head_commit(self) -> Optional[str]:
        """读取 HEAD commit"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.config["target_repo"],
                text=True,
                capture_output=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _build_review_prompt(self) -> str:
        """构建 review prompt"""
        test_branch = self.state_manager.state["config"].get("test_branch", "")
        patches_dir = self.config["patches_dir"]
        return (
            f"/patch-validator 帮我检查一下{self.config['target_repo']}的分支"
            f"{test_branch}合入的补丁，与在{patches_dir}的补丁是否存在差异。"
        )

    def _build_response(self, result: Dict[str, Any]) -> str:
        """构建响应"""
        response = {
            "success": result.get("success", False),
            "next_action": result.get("next_action"),
            "results": self.results,
            **{k: v for k, v in result.items() if k not in {"success", "stop"}},
        }
        return json.dumps(response, ensure_ascii=False, indent=2)

    # === 后续恢复方法 ===

    def resume_after_continue(self) -> str:
        """在 git am --continue 后恢复"""
        # 验证 git am 状态
        if self.git_am_in_progress():
            return json.dumps({
                "success": False,
                "next_action": "continue_git_am",
                "message": "git am still in progress, please run 'git add -A && git am --continue' first",
            })

        # 转换回 running 状态
        self.state_manager.transition(Phase.RUNNING.value)

        # 获取当前进度
        progress = self.state_manager.state["progress"]
        patch_sets = self.config["patch_sets"]

        if progress["current_patch_set_index"] >= len(patch_sets):
            return self._complete()

        patch_set = patch_sets[progress["current_patch_set_index"]]

        # 验证当前补丁
        patch_file = progress.get("current_patch_file")
        if not patch_file or not os.path.isfile(patch_file):
            return json.dumps({
                "success": False,
                "next_action": "escalate_human",
                "message": "Cannot find current patch file for re-validation",
            })

        validation_result = self._validate_patch(patch_file, {"applied_commit": "HEAD"})
        result = self._handle_validation_result(validation_result)

        if result.get("stop"):
            return self._build_response(result)

        # 继续下一个补丁
        return self.run()

    def accept_semantic_substitution(self) -> str:
        """接受语义替换"""
        self.state_manager.transition(Phase.RUNNING.value)

        self._advance_after_success(status="semantic-substitution-accepted")

        return self.run()

    def accept_hunk_recovery(self, decision: str) -> str:
        """接受 hunk 恢复"""
        if decision not in {"ignore-and-continue", "stop-and-abort"}:
            return json.dumps({
                "success": False,
                "next_action": "stop_invalid_input",
                "error": "Invalid hunk recovery decision",
                "recovery_decision": decision,
            }, ensure_ascii=False, indent=2)

        if decision == "stop-and-abort":
            self.state_manager.transition(
                Phase.ABORTED.value,
                **{
                    "runtime.escalation_reason": "hunk-recovery-stop-and-abort",
                    "runtime.last_validation_status": "missing-hunk",
                }
            )
            return json.dumps({
                "success": False,
                "next_action": "stop_validation_failed",
                "message": "Hunk recovery rejected by operator",
                "recovery_decision": decision,
            }, ensure_ascii=False, indent=2)

        self.state_manager.transition(Phase.RUNNING.value)
        self._advance_after_success(status="hunk-recovery-accepted")

        return self.run()

    def resume_after_fix(self) -> str:
        """人工修复后从 needs_human 状态恢复"""
        # 1. 检查 git am 状态
        if self.git_am_in_progress():
            return json.dumps({
                "success": False,
                "next_action": "continue_git_am",
                "message": "git am still in progress, please run 'git add -A && git am --continue' first",
            }, ensure_ascii=False, indent=2)

        # 1.5 检查人工修复是否生效（要求 HEAD 已变化）
        runtime = self.state_manager.state.get("runtime", {})
        last_observed = runtime.get("last_observed_commit_ref")
        current_head = self._read_head_commit()
        if last_observed and current_head and last_observed == current_head:
            reason = runtime.get("last_validation_status") or runtime.get("escalation_reason")
            return json.dumps({
                "success": False,
                "next_action": "stop_manual_recovery_required",
                "message": "No manual fix detected on HEAD. Please apply human decision or amend commit before resume.",
                **self._decision_hint_payload(reason),
                "decision_context": {
                    "last_observed_commit_ref": last_observed,
                    "current_head": current_head,
                    "reason": reason or "unknown",
                },
            }, ensure_ascii=False, indent=2)

        # 2. 转换回 running 状态
        self.state_manager.transition(Phase.RUNNING.value)

        # 3. 验证当前 HEAD 的补丁
        progress = self.state_manager.state["progress"]
        patch_file = progress.get("current_patch_file")

        if patch_file and os.path.isfile(patch_file):
            # 验证当前补丁
            validation_result = self._validate_patch(patch_file, {"applied_commit": "HEAD"})
            result = self._handle_validation_result(validation_result)

            if result.get("stop"):
                return self._build_response(result)

        # 4. 继续下一个补丁
        return self.run()

    def _normalize_failure_payload(
        self,
        *,
        validation_result: Optional[Dict[str, Any]] = None,
        repair_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """规范化失败结构，确保 always 有 status 字段。"""
        status = None
        if validation_result:
            status = validation_result.get("status")
        if not status and repair_result:
            reason = repair_result.get("reason")
            if reason:
                status = f"repair-{reason}"
        status = status or "validation_failed"
        payload: Dict[str, Any] = {"status": status}
        if validation_result is not None:
            payload["validation"] = validation_result
        if repair_result is not None:
            payload["repair"] = repair_result
        return payload

    def _advance_after_success(self, status: Optional[str] = None):
        """统一推进成功后的游标与计数，避免 phase/progress 不一致。"""
        progress = self.state_manager.state["progress"]
        patch_sets = self.config.get("patch_sets", [])

        current_set_idx = int(progress.get("current_patch_set_index", 0) or 0)
        current_commit_idx = int(progress.get("current_commit_index", 0) or 0)
        applied = int(progress.get("applied_commit_count", 0) or 0) + 1

        next_set_idx = current_set_idx
        next_commit_idx = current_commit_idx + 1

        while next_set_idx < len(patch_sets):
            commits = patch_sets[next_set_idx].get("commits", [])
            if next_commit_idx < len(commits):
                break
            next_set_idx += 1
            next_commit_idx = 0

        if next_set_idx >= len(patch_sets):
            next_patch_set = None
            next_commit_id = None
        else:
            next_patch_set = patch_sets[next_set_idx].get("name")
            commits = patch_sets[next_set_idx].get("commits", [])
            next_commit_id = commits[next_commit_idx] if next_commit_idx < len(commits) else None

        self.state_manager.update(
            **{
                "progress.applied_commit_count": applied,
                "progress.current_patch_set_index": min(next_set_idx, len(patch_sets)),
                "progress.current_commit_index": next_commit_idx if next_set_idx < len(patch_sets) else 0,
                "progress.current_patch_set": next_patch_set,
                "progress.current_commit_id": next_commit_id,
                "progress.current_patch_file": None,
                "runtime.last_validation_status": status,
                "runtime.escalation_reason": None,
                "runtime.last_evidence_snapshot": None,
                "iteration.current": 0,
            }
        )

    def git_am_in_progress(self) -> bool:
        """检查 git am 是否正在进行"""
        try:
            repo_path = self.config["target_repo"]
            git_dir = os.path.join(repo_path, ".git")
            if os.path.isfile(git_dir):
                with open(git_dir, "r") as f:
                    git_dir = f.read().strip().replace("gitdir: ", "")
            am_dir = os.path.join(git_dir, "rebase-apply")
            return os.path.isdir(am_dir)
        except Exception:
            return False

    def _reconcile_validate_commits(
        self,
        branch_commits: List[str],
        expected_commits: List[Dict[str, Any]],
        count: int,
    ) -> List[Dict[str, Any]]:
        """Validate each reconciled commit against its original patch.

        Returns a list of validation failure dicts.  Empty list means all OK.
        """
        from post_apply_gate import evaluate_patch_commit

        failures: List[Dict[str, Any]] = []
        cache = self.state_manager.state.get("runtime", {}).get("exported_patch_index", {})

        for index in range(min(count, len(branch_commits), len(expected_commits))):
            commit_ref = branch_commits[index]
            expected = expected_commits[index]
            commit_id = expected["commit_id"]

            patch_file = cache.get(commit_id, {}).get("patch_str")
            if not patch_file or not os.path.isfile(patch_file):
                # patch not cached – skip silently; subject already matched
                continue

            try:
                gate = evaluate_patch_commit(
                    patch_file=patch_file,
                    repo_path=self.config["target_repo"],
                    commit_ref=commit_ref,
                    config_targets=self._build_config_targets(patch_file),
                    prior_patch_files=[],
                    patches_dir=self.config["patches_dir"],
                    commit_id=commit_id,
                    iteration=0,
                )
                verdict = gate.get("verdict")
                if verdict != "pass":
                    failures.append({
                        "index": index,
                        "commit_ref": commit_ref,
                        "commit_id": commit_id,
                        "subject": expected.get("patch_set_name", ""),
                        "verdict": verdict,
                        "status": gate.get("status"),
                        "detail": gate.get("validation", {}),
                    })
            except Exception as exc:
                logger.warning("reconcile validate error for %s: %s", commit_id, exc)
                failures.append({
                    "index": index,
                    "commit_ref": commit_ref,
                    "commit_id": commit_id,
                    "subject": expected.get("patch_set_name", ""),
                    "verdict": "error",
                    "status": "error",
                    "detail": str(exc),
                })

        return failures

    def reconcile(self, test_branch: str) -> str:
        """从已有测试分支恢复进度"""
        from shared.git_helpers import branch_exists

        # 1. 验证分支存在
        if not branch_exists(test_branch, self.config["target_repo"]):
            return json.dumps({
                "success": False,
                "next_action": "stop_manual_recovery_required",
                "error": f"test branch does not exist: {test_branch}",
                "test_branch": test_branch,
            }, ensure_ascii=False, indent=2)

        # 2. 获取分支上的提交列表
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--reverse",
                 f"{self.config['target_branch']}..{test_branch}"],
                cwd=self.config["target_repo"],
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                return json.dumps({
                    "success": False,
                    "next_action": "stop_manual_recovery_required",
                    "error": f"failed to get branch commits: {result.stderr}",
                    "test_branch": test_branch,
                }, ensure_ascii=False, indent=2)

            branch_commits = [line.split()[0] for line in result.stdout.strip().split('\n') if line]
        except Exception as e:
            return json.dumps({
                "success": False,
                "next_action": "stop_manual_recovery_required",
                "error": str(e),
                "test_branch": test_branch,
            }, ensure_ascii=False, indent=2)

        # 3. 构建预期的提交序列
        expected_commits = []
        for set_idx, patch_set in enumerate(self.config.get("patch_sets", [])):
            for commit_idx, commit_id in enumerate(patch_set.get("commits", [])):
                expected_commits.append({
                    "patch_set_index": set_idx,
                    "commit_index": commit_idx,
                    "commit_id": commit_id,
                    "patch_set_name": patch_set.get("name"),
                })

        # 4. 验证分支提交数量
        if len(branch_commits) > len(expected_commits):
            return json.dumps({
                "success": False,
                "next_action": "stop_manual_recovery_required",
                "error": "test branch has more commits than expected patch sequence",
                "test_branch": test_branch,
                "branch_commit_count": len(branch_commits),
                "expected_commit_count": len(expected_commits),
            }, ensure_ascii=False, indent=2)

        # 5. 验证每个提交（commit subject 匹配检查）
        matched = 0
        mismatched_commits = []
        validation_failures = []
        for index, commit_ref in enumerate(branch_commits):
            expected = expected_commits[index]
            # 验证 commit subject 匹配
            commit_id = expected["commit_id"]
            subject_result = subprocess.run(
                ["git", "log", "-1", "--format=%s", commit_ref],
                cwd=self.config["target_repo"],
                text=True,
                capture_output=True,
            )
            if subject_result.returncode == 0:
                commit_subject = subject_result.stdout.strip()
                cached = self.state_manager.state.get("runtime", {}).get("exported_patch_index", {})
                expected_subject = cached.get(commit_id, {}).get("commit_msg", "")
                if expected_subject and commit_subject != expected_subject:
                    mismatched_commits.append({
                        "index": index,
                        "commit_ref": commit_ref,
                        "expected_subject": expected_subject,
                        "actual_subject": commit_subject,
                    })
            matched += 1

        if mismatched_commits:
            logger.warning(
                "Reconcile found %d subject mismatches: %s",
                len(mismatched_commits),
                "; ".join(m["actual_subject"] for m in mismatched_commits),
            )

        # 5.5 逐 commit 内容校验
        if matched > 0:
            validation_failures = self._reconcile_validate_commits(
                branch_commits, expected_commits, matched
            )

        if validation_failures:
            logger.warning(
                "Reconcile validation failures: %s",
                "; ".join(v["subject"] for v in validation_failures),
            )

        # 6. 计算新的游标位置
        if matched >= len(expected_commits):
            new_set_index = len(self.config.get("patch_sets", []))
            new_commit_index = 0
        else:
            new_set_index = expected_commits[matched]["patch_set_index"]
            new_commit_index = expected_commits[matched]["commit_index"]

        # 7. 检查 git am 状态
        paused = self.git_am_in_progress()

        # 8. 确定新阶段
        if validation_failures and not paused:
            # 存在校验失败的 commit，需要人工介入
            first_failure = validation_failures[0]
            new_phase = Phase.NEEDS_HUMAN.value
            next_action = "escalate_human"
        elif paused:
            new_phase = Phase.WAITING_AFTER_CONTINUE.value
            next_action = "resolve_conflicts"
        elif matched >= len(expected_commits):
            new_phase = Phase.COMPLETED_PENDING_REVIEW.value
            next_action = "handoff_review"
        else:
            new_phase = Phase.RUNNING.value
            next_action = "continue"

        # 9. 更新状态
        update_data = {
            "config.test_branch": test_branch,
            "progress.current_patch_set_index": new_set_index,
            "progress.current_commit_index": new_commit_index,
            "progress.applied_commit_count": matched,
            "progress.current_patch_set": expected_commits[matched - 1]["patch_set_name"] if matched > 0 and matched <= len(expected_commits) else None,
            "progress.current_commit_id": expected_commits[matched]["commit_id"] if matched < len(expected_commits) else None,
            "runtime.last_observed_commit_ref": branch_commits[-1] if branch_commits else None,
        }

        if validation_failures:
            update_data["runtime.escalation_reason"] = "reconcile_validation_failed"
            update_data["runtime.reconcile_validation_failures"] = validation_failures

        if matched >= len(expected_commits) and not paused and not validation_failures:
            final_head = self._read_head_commit()
            review_prompt = self._build_review_prompt()
            update_data["final.final_head"] = final_head
            update_data["final.review_prompt"] = review_prompt

        self.state_manager.transition(new_phase, **update_data)

        # 10. 返回结果
        response = {
            "success": not bool(validation_failures),
            "next_action": next_action,
            "test_branch": test_branch,
            "patch_set_index": new_set_index,
            "commit_index": new_commit_index,
            "phase": new_phase,
            "applied_commit_count": matched,
            "expected_commit_count": len(expected_commits),
        }

        if validation_failures:
            response["message"] = (
                f"Reconcile found {len(validation_failures)} commit(s) with validation failures. "
                "Use --resume-after-fix after manual correction."
            )
            response["validation_failures"] = validation_failures
            response.update(self._decision_hint_payload("reconcile_validation_failed"))

        if matched >= len(expected_commits) and not paused and not validation_failures:
            response["review_prompt"] = self.state_manager.state["final"]["review_prompt"]
            response["final_head"] = self.state_manager.state["final"]["final_head"]

        return json.dumps(response, ensure_ascii=False, indent=2)
