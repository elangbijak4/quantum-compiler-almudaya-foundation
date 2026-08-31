"""
Module 6 Stage 7 Test Suite — Session Lifecycle & Baseline Restoration.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.lifecycle import SessionLifecycle
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7Session(unittest.TestCase):
    """Tests for session lifecycle integration with resolver."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.lifecycle = SessionLifecycle(self.ge0)

    def test_session_lifecycle_flow(self) -> None:
        """Req 34: Session creation, baseline selection, resolution, and reset."""
        sb_def = self.lifecycle.create_session("s_test")
        ctx_def = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb_def)
        self.assertEqual(ctx_def.effective_vocabulary, ("CNOT", "TOFFOLI", "X"))

        # Select user baseline
        sb_user = self.lifecycle.select_user_baseline(("CNOT", "X"))
        ctx_user = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb_user)
        self.assertEqual(ctx_user.effective_vocabulary, ("CNOT", "X"))

        # Reset baseline
        sb_reset = self.lifecycle.reset_baseline()
        ctx_reset = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb_reset)
        self.assertEqual(ctx_reset.effective_vocabulary, ("CNOT", "TOFFOLI", "X"))


if __name__ == "__main__":
    unittest.main()
