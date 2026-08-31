"""
Module 6 Stage 5 Unit Test Suite — Candidate Registry & Base Vocabulary Immutability.

Verifies CandidateRegistry, base vocabulary G0 immutability hashing, and duplicate detection.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, CandidateRegistry, compute_base_vocabulary_hash


class TestStage5Registry(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = CandidateRegistry()
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        self.h_cand = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

    def test_01_g0_hash_immutability(self) -> None:
        """Positive test: G0 hash before and after execution are identical."""
        h_before = compute_base_vocabulary_hash()
        self.assertTrue(self.registry.verify_g0_immutability())
        h_after = compute_base_vocabulary_hash()
        self.assertEqual(h_before, h_after)

    def test_02_extended_vocabulary_construction(self) -> None:
        """Positive test: Constructs extended vocabulary G' = G0 U {H} without modifying G0."""
        self.registry.register_candidate(self.h_cand)
        g0 = self.registry.get_base_vocabulary()
        g_ext = self.registry.get_extended_vocabulary(("cand_h",))

        self.assertEqual(g0, ("X", "CNOT", "TOFFOLI"))
        self.assertIn("HADAMARD", g_ext)
        self.assertIn("X", g_ext)

    def test_03_duplicate_candidate_rejection(self) -> None:
        """Negative test: Rejects duplicate candidate registration with DUPLICATE_CANDIDATE_GATE."""
        self.registry.register_candidate(self.h_cand)

        # Duplicate ID
        with self.assertRaises(ValueError) as ctx:
            self.registry.register_candidate(self.h_cand)
        self.assertIn("DUPLICATE_CANDIDATE_GATE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
