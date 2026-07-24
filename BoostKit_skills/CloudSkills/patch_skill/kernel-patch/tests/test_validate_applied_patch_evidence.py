import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_applied_patch as vap


class ValidateAppliedPatchEvidenceTests(unittest.TestCase):
    def test_build_validation_evidence_contains_summary_and_signals(self) -> None:
        issues = [
            {
                "path": "drivers/irqchip/irq-gic-v3-its.c",
                "status": "missing-hunk",
                "missing_added_lines": ["#ifdef CONFIG_VIRT_PLAT_DEV", "list_add(&devid_pool->entry, &rsv_devid_pools);"],
                "extra_added_lines": [],
                "removed_line_mismatches": ["return -EINVAL;"],
                "hunk_differences": [{"status": "missing-hunk"}],
            }
        ]
        config_results = []
        source_analysis = {
            "source_type": "prior-task",
            "confidence": "high",
            "auto_continue_eligible": True,
        }

        evidence = vap._build_validation_evidence(
            status="missing-hunk",
            issues=issues,
            config_results=config_results,
            source_analysis=source_analysis,
            saw_config_mapping=False,
            saw_config_problem=False,
        )

        self.assertEqual(evidence["schema_version"], 1)
        self.assertEqual(evidence["summary"]["issue_count"], 1)
        self.assertEqual(evidence["summary"]["line_stats"]["missing_added"], 2)
        self.assertEqual(evidence["source_analysis"]["source_type"], "prior-task")

        signal_codes = [item["code"] for item in evidence["signals"]]
        self.assertIn("issue-missing-hunk", signal_codes)
        self.assertIn("missing-hunk-source-analysis", signal_codes)

        file_signals = evidence["files"][0]["signals"]
        self.assertIn("macro-boundary-shift", file_signals)
        self.assertIn("critical-list-operation-shift", file_signals)
        self.assertIn("return-semantics-shift", file_signals)


if __name__ == "__main__":
    unittest.main()
