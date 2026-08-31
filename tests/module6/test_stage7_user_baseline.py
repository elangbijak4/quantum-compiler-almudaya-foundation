"""
Module 6 Stage 7 Test Suite — User Baseline Resolution.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.model import ConfigurationStatus


class TestStage7UserBaseline(unittest.TestCase):
    """Tests for user-selected session baseline resolution."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_user_selected_valid_subset(self) -> None:
        """Req 7, 10: Valid user baseline Bu subseteq GE(k) resolves correctly."""
        sb = SessionBaseline(
            session_id="s_valid",
            selected_gates=("CNOT", "X"),
            baseline_hash="hash_valid",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb)
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "X"))
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.VALID_CONFIGURATION)

    def test_user_selected_outside_ge0_invalid(self) -> None:
        """Req 10: User baseline containing gates outside GE(k) is marked INVALID_CONFIGURATION."""
        sb = SessionBaseline(
            session_id="s_invalid",
            selected_gates=("HADAMARD", "X"),
            baseline_hash="hash_inv",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb)
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)
        self.assertEqual(ctx.effective_vocabulary, ())


if __name__ == "__main__":
    unittest.main()
