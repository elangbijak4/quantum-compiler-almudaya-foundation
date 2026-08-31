"""
Module 6 Stage 6 Test Suite — Evolutionary Vocabulary State & Lineage.
"""

import unittest
import hashlib
import json

from src.module6.evolution.state import EvolutionaryVocabularyState, create_initial_evolutionary_state


class TestStage6State(unittest.TestCase):
    """Tests for EvolutionaryVocabularyState and GE(0) baseline."""

    def test_initial_state_ge0(self) -> None:
        """Req 2, 4, 5: Verify initial state GE(0) = {"CNOT", "TOFFOLI", "X"}."""
        ge0 = create_initial_evolutionary_state()
        self.assertEqual(ge0.evolution_stage_id, "GE_0")
        self.assertIsNone(ge0.parent_stage_id)
        self.assertEqual(ge0.vocabulary, ("CNOT", "TOFFOLI", "X"))
        self.assertEqual(len(ge0.vocabulary), 3)

        expected_hash = hashlib.sha256(json.dumps(ge0.vocabulary).encode("utf-8")).hexdigest()
        self.assertEqual(ge0.vocabulary_hash, expected_hash)

    def test_immutability(self) -> None:
        """Req 4, 9: Verify state is frozen and immutable."""
        ge0 = create_initial_evolutionary_state()
        with self.assertRaises(Exception):
            ge0.vocabulary = ("X",)  # type: ignore

    def test_to_dict_and_version(self) -> None:
        """Req 4: Verify to_dict structure."""
        ge0 = create_initial_evolutionary_state()
        d = ge0.to_dict()
        self.assertEqual(d["evolution_stage_id"], "GE_0")
        self.assertEqual(d["compiler_version"], "1.0.0")
        self.assertIn("vocabulary_hash", d)


if __name__ == "__main__":
    unittest.main()
