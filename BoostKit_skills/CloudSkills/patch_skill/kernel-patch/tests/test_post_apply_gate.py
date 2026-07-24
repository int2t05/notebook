import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import post_apply_gate as gate


class PostApplyGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.patches_dir = self.root / "patches"
        self.patches_dir.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_pass_verdict_for_identical_status(self) -> None:
        payload = {"success": True, "status": "identical", "issues": [], "config_results": []}
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c1",
                iteration=0,
            )

        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(Path(result["artifact_path"]).is_file())

    def test_retryable_fail_for_missing_hunk(self) -> None:
        payload = {"success": True, "status": "missing-hunk", "issues": [], "config_results": []}
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c2",
                iteration=1,
            )
        self.assertEqual(result["verdict"], "retryable_fail")

    def test_missing_hunk_high_confidence_can_pass(self) -> None:
        payload = {
            "success": True,
            "status": "missing-hunk",
            "issues": [],
            "config_results": [],
            "source_analysis": {
                "auto_continue": True,
                "confidence": "high",
                "auto_continue_level": "high",
            },
        }
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c2h",
                iteration=1,
            )
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["status"], "missing-hunk-source-confirmed")

    def test_missing_hunk_medium_confidence_stays_retryable(self) -> None:
        payload = {
            "success": True,
            "status": "missing-hunk",
            "issues": [],
            "config_results": [],
            "source_analysis": {
                "auto_continue": True,
                "confidence": "medium",
                "auto_continue_level": "medium",
            },
        }
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c2m",
                iteration=1,
            )
        self.assertEqual(result["verdict"], "retryable_fail")

    def test_missing_hunk_not_eligible_stays_retryable(self) -> None:
        payload = {
            "success": True,
            "status": "missing-hunk",
            "issues": [],
            "config_results": [],
            "evidence": {
                "source_analysis": {
                    "auto_continue": True,
                    "confidence": "high",
                    "auto_continue_level": "high",
                    "auto_continue_eligible": False,
                }
            },
            "source_analysis": {
                "auto_continue": True,
                "confidence": "high",
                "auto_continue_level": "high",
            },
        }
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c2ne",
                iteration=1,
            )
        self.assertEqual(result["verdict"], "retryable_fail")

    def test_retryable_fail_for_different(self) -> None:
        payload = {"success": True, "status": "different", "issues": [], "config_results": []}
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c3",
                iteration=2,
            )
        self.assertEqual(result["verdict"], "retryable_fail")

    def test_fatal_fail_for_extra_file(self) -> None:
        payload = {"success": True, "status": "extra-file", "issues": [], "config_results": []}
        with patch.object(gate, "validate_applied_patch", return_value=json.dumps(payload)):
            result = gate.evaluate_patch_commit(
                patch_file="/tmp/p.patch",
                repo_path="/tmp/repo",
                commit_ref="HEAD",
                config_targets={},
                prior_patch_files=[],
                patches_dir=str(self.patches_dir),
                commit_id="c4",
                iteration=0,
            )
        self.assertEqual(result["verdict"], "fatal_fail")


if __name__ == "__main__":
    unittest.main()
