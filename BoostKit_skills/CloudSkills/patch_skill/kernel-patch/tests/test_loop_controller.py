import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrator.loop_controller import decide_retry


class LoopControllerTests(unittest.TestCase):
    def test_retryable_status_retries_before_limit(self) -> None:
        decision = decide_retry("missing-hunk", iteration=0, max_iteration=4)
        self.assertTrue(decision.should_retry)
        self.assertFalse(decision.should_escalate)
        self.assertEqual(decision.iteration, 1)

    def test_retryable_status_escalates_at_limit(self) -> None:
        decision = decide_retry("semantic-substitution-suspected", iteration=3, max_iteration=4)
        self.assertFalse(decision.should_retry)
        self.assertTrue(decision.should_escalate)
        self.assertEqual(decision.reason, "max-iteration-reached")

    def test_fatal_status_escalates_immediately(self) -> None:
        decision = decide_retry("config-unmapped", iteration=0, max_iteration=4)
        self.assertFalse(decision.should_retry)
        self.assertTrue(decision.should_escalate)
        self.assertEqual(decision.reason, "fatal-validation-status")

    def test_different_is_retryable(self) -> None:
        decision = decide_retry("different", iteration=0, max_iteration=4)
        self.assertTrue(decision.should_retry)
        self.assertFalse(decision.should_escalate)
        self.assertEqual(decision.iteration, 1)


if __name__ == "__main__":
    unittest.main()

