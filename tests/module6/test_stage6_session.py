"""
Module 6 Stage 6 Test Suite — User Session Baseline & Lifecycle.
"""

import unittest

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.lifecycle import SessionLifecycle


class TestStage6Session(unittest.TestCase):
    """Tests for SessionBaseline and SessionLifecycle operations."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.lifecycle = SessionLifecycle(self.ge0)

    def test_default_session(self) -> None:
        """Req 8, 11: Default session uses GE(0)."""
        sess = self.lifecycle.create_session("sess_1")
        self.assertEqual(sess.session_id, "sess_1")
        self.assertEqual(sess.baseline_mode, BaselineMode.DEFAULT_EVOLUTIONARY)
        self.assertEqual(sess.selected_gates, ("CNOT", "TOFFOLI", "X"))

    def test_select_user_baseline(self) -> None:
        """Req 8, 9, 10: Select Bu subseteq GE(0)."""
        sess = self.lifecycle.select_user_baseline(("X", "CNOT"), session_id="sess_user")
        self.assertEqual(sess.baseline_mode, BaselineMode.USER_SELECTED)
        self.assertEqual(sess.selected_gates, ("CNOT", "X"))
        self.assertEqual(self.ge0.vocabulary_hash, self.lifecycle.evolution_state.vocabulary_hash)

    def test_reset_and_end_session(self) -> None:
        """Req 9, 11: Verify reset and end session restore GE(0) without mutating GE(0)."""
        hash_before = self.ge0.vocabulary_hash
        self.lifecycle.select_user_baseline(("X",))

        # Reset
        res_sess = self.lifecycle.reset_baseline()
        self.assertEqual(res_sess.baseline_mode, BaselineMode.DEFAULT_EVOLUTIONARY)
        self.assertEqual(res_sess.selected_gates, ("CNOT", "TOFFOLI", "X"))

        # End session
        self.lifecycle.end_session()
        self.assertIsNone(self.lifecycle.active_session)
        self.assertEqual(self.lifecycle.get_effective_vocabulary(), ("CNOT", "TOFFOLI", "X"))

        hash_after = self.ge0.vocabulary_hash
        self.assertEqual(hash_before, hash_after)


if __name__ == "__main__":
    unittest.main()
