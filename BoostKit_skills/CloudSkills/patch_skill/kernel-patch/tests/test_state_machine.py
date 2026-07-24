#!/usr/bin/env python3
"""Tests for the state machine module."""

import unittest
import sys
import os

# Add scripts directory to path
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_scripts_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from scripts.orchestrator.state_machine import StateMachine, Phase


class TestStateMachine(unittest.TestCase):
    def test_can_transition_valid(self):
        """Test valid phase transitions."""
        self.assertTrue(StateMachine.can_transition("running", "revalidating"))
        self.assertTrue(StateMachine.can_transition("running", "waiting_after_continue"))
        self.assertTrue(StateMachine.can_transition("revalidating", "auto_fixing"))
        self.assertTrue(StateMachine.can_transition("auto_fixing", "revalidating"))
        self.assertTrue(StateMachine.can_transition("completed_pending_review", "ended"))

    def test_can_transition_invalid(self):
        """Test invalid phase transitions."""
        self.assertFalse(StateMachine.can_transition("ended", "running"))
        self.assertFalse(StateMachine.can_transition("aborted", "running"))
        self.assertFalse(StateMachine.can_transition("idle", "auto_fixing"))

    def test_is_terminal(self):
        """Test terminal phase detection."""
        self.assertTrue(StateMachine.is_terminal("ended"))
        self.assertTrue(StateMachine.is_terminal("aborted"))
        self.assertFalse(StateMachine.is_terminal("running"))
        self.assertFalse(StateMachine.is_terminal("idle"))

    def test_is_active(self):
        """Test active phase detection."""
        self.assertTrue(StateMachine.is_active("running"))
        self.assertTrue(StateMachine.is_active("revalidating"))
        self.assertTrue(StateMachine.is_active("auto_fixing"))
        self.assertFalse(StateMachine.is_active("ended"))
        self.assertFalse(StateMachine.is_active("idle"))

    def test_get_valid_transitions(self):
        """Test getting valid transitions."""
        self.assertEqual(StateMachine.get_valid_transitions("idle"), ["running"])
        self.assertEqual(
            set(StateMachine.get_valid_transitions("running")),
            {"running", "revalidating", "auto_fixing", "waiting_after_continue", "waiting_semantic_confirmation", "waiting_hunk_confirmation", "completed_pending_review", "needs_human", "aborted"}
        )

    def test_running_to_auto_fixing_transition(self):
        """Test that running -> auto_fixing transition is valid (Fix 1)."""
        self.assertTrue(
            StateMachine.can_transition("running", "auto_fixing"),
            "running -> auto_fixing should be a valid transition"
        )

    def test_running_to_auto_fixing_via_update_state(self):
        """Test that update_state_phase allows running -> auto_fixing."""
        from scripts.orchestrator.state_machine import update_state_phase
        state = {"phase": "running"}
        result = update_state_phase(state, "auto_fixing")
        self.assertEqual(result["phase"], "auto_fixing")


if __name__ == "__main__":
    unittest.main()
