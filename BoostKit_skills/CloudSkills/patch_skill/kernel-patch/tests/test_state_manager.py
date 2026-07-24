#!/usr/bin/env python3
"""Tests for the state manager module."""

import json
import os
import sys
import tempfile
import unittest

# Add scripts directory to path
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_scripts_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from scripts.orchestrator.state_manager import StateManager
from scripts.orchestrator.state_machine import Phase, StateMachine


class TestStateManager(unittest.TestCase):
    def setUp(self):
        """Set up a temporary state file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "kernel_patch_state.json")

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_empty_state(self):
        """Test creating empty state."""
        manager = StateManager(self.state_file)
        state = manager.state

        self.assertEqual(state["phase"], "idle")
        self.assertEqual(state["skill"], "kernel-patch")
        self.assertEqual(state["version"], 2)
        self.assertIsNone(state["task_id"])
        self.assertEqual(state["progress"]["expected_commit_count"], 0)
        self.assertEqual(state["progress"]["applied_commit_count"], 0)

        self.assertIsInstance(state["progress"], dict)
        self.assertIsInstance(state["iteration"], dict)
        self.assertIsInstance(state["runtime"], dict)
        self.assertIsInstance(state["llm"], dict)
        self.assertIsInstance(state["final"], dict)

    def test_transition(self):
        """Test state transition."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        self.assertEqual(manager.state["phase"], "running")
        self.assertIn("任务进行中", manager.state["llm"]["summary"])
        # Check history
        history = manager.state["llm"]["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["from_phase"], "idle")
        self.assertEqual(history[0]["to_phase"], "running")

        # Check saved file
        self.assertTrue(os.path.exists(self.state_file))
        with open(self.state_file, "r") as f:
            saved = json.load(f)
        self.assertEqual(saved["phase"], "running")

    def test_invalid_transition_raises(self):
        """Test that invalid transitions raise errors."""
        manager = StateManager(self.state_file)
        manager.transition("running")

        with self.assertRaises(ValueError):
            manager.transition("ended")

    def test_summary_auto_generated(self):
        """Test that summary is auto-generated on state changes."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        summary = manager.state["llm"]["summary"]
        self.assertIn("任务进行中", summary)

        manager.transition("needs_human")
        summary = manager.state["llm"]["summary"]
        self.assertIn("任务已阻塞", summary)

    def test_update(self):
        """Test update without changing phase."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        manager.update(
            **{
                "progress.applied_commit_count": 5,
                "progress.expected_commit_count": 10,
                "iteration.current": 2,
            }
        )
        self.assertEqual(manager.state["progress"]["applied_commit_count"], 5)
        self.assertEqual(manager.state["progress"]["expected_commit_count"], 10)
        self.assertEqual(manager.state["iteration"]["current"], 2)
        # Phase should not change
        self.assertEqual(manager.state["phase"], "running")

    def test_get_llm_view(self):
        """Test LLM view generation."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        manager.update(
            **{
                "progress.applied_commit_count": 5,
                "progress.expected_commit_count": 10,
            }
        )
        view = manager.get_llm_view()

        self.assertEqual(view["task_id"], manager.state["task_id"])
        self.assertEqual(view["phase"], "running")
        self.assertIn("5", view["summary"])
        self.assertEqual(view["progress"]["applied"], 5)
        self.assertEqual(view["progress"]["total"], 10)

    def test_get_program_view(self):
        """Test program view generation."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        manager.update(
            **{
                "progress.applied_commit_count": 5,
                "progress.expected_commit_count": 10,
                "runtime.last_validation_status": "identical",
                "runtime.exported_patch_index": {"commit1": {"patch_str": "/path/to/patch"}},
            }
        )
        view = manager.get_program_view()

        self.assertEqual(view["phase"], "running")
        self.assertEqual(view["progress"]["applied_commit_count"], 5)
        self.assertEqual(view["progress"]["expected_commit_count"], 10)
        self.assertEqual(view["runtime"]["last_validation_status"], "identical")
        self.assertEqual(view["runtime"]["exported_patch_index"]["commit1"]["patch_str"], "/path/to/patch")

    def test_backward_compatibility(self):
        """Test backward compatibility methods."""
        manager = StateManager(self.state_file)
        manager.transition("running")
        manager.update(**{"progress.applied_commit_count": 5})

        # Test get_task_status
        self.assertEqual(manager.get_task_status(), "running")

        # Test get_applied_count
        self.assertEqual(manager.get_applied_count(), 5)

        # Test is_active
        self.assertTrue(manager.is_active())

        # Test is_terminal
        self.assertFalse(manager.is_terminal())


if __name__ == "__main__":
    unittest.main()
