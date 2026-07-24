import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrator.state_manager import StateManager


class StateOnlyTaskMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.patches_dir = self.root / "patches"
        self.patches_dir.mkdir()
        self.state_file = self.patches_dir / "kernel_patch_state.json"
        self.task_memory_script = REPO_ROOT / "kernel-patch" / "scripts" / "task_memory.py"
        self.run_patch_sets_script = REPO_ROOT / "kernel-patch" / "scripts" / "run_patch_sets.py"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_inspect_uses_state_only(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.task_memory_script),
                "inspect",
                "--patches-dir",
                str(self.patches_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["success"])
        self.assertFalse(payload["exists"])
        self.assertEqual(payload["state_file"], str(self.state_file))

    def test_mark_ended_updates_state(self) -> None:
        manager = StateManager(str(self.state_file))
        manager.state["task_id"] = "task-1"
        manager.transition("running")

        result = subprocess.run(
            [
                sys.executable,
                str(self.task_memory_script),
                "mark-ended",
                "--state-file",
                str(self.state_file),
                "--final-head",
                "abc123",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["task_status"], "ended")
        self.assertEqual(payload["final_head"], "abc123")

    def test_task_memory_rejects_memory_flag(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.task_memory_script),
                "inspect",
                "--patches-dir",
                str(self.patches_dir),
                "--memory-file",
                str(self.patches_dir / ".kernel_patch_memory.json"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments: --memory-file", result.stderr)

    def test_run_patch_sets_rejects_memory_flag(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.run_patch_sets_script),
                "--memory-file",
                "dummy.json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments: --memory-file", result.stderr)


if __name__ == "__main__":
    unittest.main()
