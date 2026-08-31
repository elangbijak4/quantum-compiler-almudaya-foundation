"""
Module 6 Stage 6 Test Suite — Effective Vocabulary Resolver.
"""

import unittest

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.resolver import EffectiveVocabularyResolver


class TestStage6Resolver(unittest.TestCase):
    """Tests for EffectiveVocabularyResolver."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_default_mode_resolution(self) -> None:
        """Req 10: Default mode resolves GE(0)."""
        b_default = SessionBaseline(
            session_id="s1",
            selected_gates=("CNOT", "TOFFOLI", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )
        eff = EffectiveVocabularyResolver.resolve_effective_vocabulary(self.ge0, b_default)
        self.assertEqual(eff, ("CNOT", "TOFFOLI", "X"))

    def test_user_selected_mode_resolution(self) -> None:
        """Req 10: User mode resolves Bu subseteq GE(0)."""
        b_user = SessionBaseline(
            session_id="s2",
            selected_gates=("CNOT", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        eff = EffectiveVocabularyResolver.resolve_effective_vocabulary(self.ge0, b_user)
        self.assertEqual(eff, ("CNOT", "X"))

    def test_invalid_gates_outside_ge_raises_error(self) -> None:
        """Req 10, 30: Gates outside GE(0) raise ValueError."""
        b_invalid = SessionBaseline(
            session_id="s3",
            selected_gates=("HADAMARD", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        with self.assertRaises(ValueError):
            EffectiveVocabularyResolver.resolve_effective_vocabulary(self.ge0, b_invalid)


if __name__ == "__main__":
    unittest.main()
