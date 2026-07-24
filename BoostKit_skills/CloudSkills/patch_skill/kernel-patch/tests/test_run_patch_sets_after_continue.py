import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_patch_sets as rps
from orchestrator.state_manager import StateManager


class RunPatchSetsFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.target_repo = self.root / "repo"
        self.source_repo = self.root / "source"
        self.reject_dir = self.root / "rejects"
        self.patches_dir = self.root / "patches"
        self.target_repo.mkdir()
        self.source_repo.mkdir()
        self.reject_dir.mkdir()
        self.patches_dir.mkdir()
        self.state_file = self.patches_dir / "kernel_patch_state.json"
        self.payload = {
            "target_repo": str(self.target_repo),
            "target_branch": "main",
            "reject_dir": str(self.reject_dir),
            "patches_dir": str(self.patches_dir),
            "config_files": [],
            "patch_sets": [
                {
                    "name": "set0",
                    "source_repo": str(self.source_repo),
                    "commits": ["c0", "c1"],
                }
            ],
        }

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _state_manager(self) -> StateManager:
        return StateManager(str(self.state_file))

    def test_needs_human_blocked_returns_recommendations(self) -> None:
        manager = self._state_manager()
        manager.state["phase"] = "needs_human"
        manager.state["config"]["test_branch"] = "auto-patch-20260331_155414"
        manager.state["runtime"]["last_validation_status"] = "semantic-substitution-suspected"
        manager.state["runtime"]["escalation_reason"] = "semantic-substitution-suspected"
        manager.state["runtime"]["last_observed_commit_ref"] = "abc123def456"
        manager.state["runtime"]["last_evidence_snapshot"] = {
            "status": "semantic-substitution-suspected",
            "issue_count": 1,
            "signal_codes": ["macro-boundary-shift"],
        }
        manager.save()

        result = json.loads(rps.run_patch_sets(self.payload, state_file=str(self.state_file)))

        self.assertFalse(result["success"])
        self.assertEqual(result["next_action"], "stop_manual_recovery_required")
        self.assertTrue(result["decision_required"])
        self.assertEqual(
            result["recommended_decisions"],
            ["accept-semantic", "continue", "abort"],
        )
        self.assertEqual(result["current_phase"], "needs_human")
        self.assertEqual(result["test_branch"], "auto-patch-20260331_155414")
        self.assertEqual(result["last_observed_commit_ref"], "abc123def456")
        self.assertEqual(result["decision_options"], rps.DECISION_OPTIONS)
        self.assertEqual(result["evidence_snapshot"]["issue_count"], 1)
        self.assertEqual(
            [item["scenario"] for item in result["resume_command_examples"]],
            [
                "manual-fix-applied",
                "accept-current-head",
                "accept-semantic-substitution",
                "accept-hunk-recovery",
            ],
        )
        self.assertTrue(
            result["resume_command_examples"][0]["command"].endswith("--resume-after-fix")
        )

    def test_human_decision_non_recommended_keeps_execution_with_warning(self) -> None:
        manager = self._state_manager()
        manager.state["phase"] = "needs_human"
        manager.state["runtime"]["escalation_reason"] = "apply_failed"
        manager.state["runtime"]["last_validation_status"] = None
        manager.save()

        with patch.object(
            rps.PatchWorkflow,
            "accept_semantic_substitution",
            return_value=json.dumps({"success": True, "next_action": "noop"}),
        ):
            result = json.loads(
                rps.run_patch_sets(
                    self.payload,
                    state_file=str(self.state_file),
                    human_decision="accept-semantic",
                )
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["next_action"], "noop")
        self.assertIn("decision_warning", result)
        self.assertEqual(result["recommended_decisions"], ["continue", "abort"])

    def test_human_decision_requires_needs_human_phase(self) -> None:
        manager = self._state_manager()
        manager.state["phase"] = "running"
        manager.save()

        result = json.loads(
            rps.run_patch_sets(
                self.payload,
                state_file=str(self.state_file),
                human_decision="continue",
            )
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["next_action"], "stop_invalid_input")

    def test_after_continue_dispatches_workflow_on_waiting_phase(self) -> None:
        manager = self._state_manager()
        manager.state["phase"] = "waiting_after_continue"
        manager.save()

        with patch.object(rps.PatchWorkflow, "git_am_in_progress", return_value=False), patch.object(
            rps.PatchWorkflow,
            "resume_after_continue",
            return_value=json.dumps({"success": True, "next_action": "continue"}),
        ) as resume_mock:
            result = json.loads(
                rps.run_patch_sets(
                    self.payload,
                    state_file=str(self.state_file),
                    after_continue=True,
                )
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["next_action"], "continue")
        resume_mock.assert_called_once()

    def test_after_continue_rejects_wrong_phase(self) -> None:
        manager = self._state_manager()
        manager.state["phase"] = "running"
        manager.save()

        with patch.object(rps.PatchWorkflow, "git_am_in_progress", return_value=False):
            result = json.loads(
                rps.run_patch_sets(
                    self.payload,
                    state_file=str(self.state_file),
                    after_continue=True,
                )
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["next_action"], "stop_invalid_input")


if __name__ == "__main__":
    unittest.main()
