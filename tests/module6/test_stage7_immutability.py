"""
Module 6 Stage 7 Test Suite — Evolutionary State Immutability.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7Immutability(unittest.TestCase):
    """Tests verifying that resolution operations never mutate evolutionary state GE(k)."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.initial_hash = self.ge0.vocabulary_hash

    def test_resolution_never_mutates_ge0_hash(self) -> None:
        """Req 33: GE(0) hash remains byte-identical before and after resolution."""
        sb = SessionBaseline(
            session_id="s_immut",
            selected_gates=("CNOT", "X"),
            baseline_hash="h_immut",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )

        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb)
        self.assertEqual(self.ge0.vocabulary_hash, self.initial_hash)
        self.assertEqual(self.ge0.vocabulary, ("CNOT", "TOFFOLI", "X"))


if __name__ == "__main__":
    unittest.main()
