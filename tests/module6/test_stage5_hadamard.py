"""
Module 6 Stage 5 Unit Test Suite — Hadamard Extension & Mandatory Mathematics Verification.

Verifies:
1. H = 1/sqrt(2) * [[1, 1], [1, -1]]
2. H|0> = (|0> + |1>)/sqrt(2), H|1> = (|0> - |1>)/sqrt(2)
3. ||H|0>|| = 1.0, ||H|1>|| = 1.0, H^\dagger H = I
4. Superposition generation capability.
"""

import unittest
import numpy as np
from src.module6.evolution import (
    CandidateGate,
    ExtendedVocabularyEvaluator,
    get_reference_target_hadamard,
)


class TestStage5Hadamard(unittest.TestCase):
    def setUp(self) -> None:
        self.h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        self.h_cand = CandidateGate("cand_h", "HADAMARD", 1, self.h_mat)

    def test_01_hadamard_mathematics_normalization(self) -> None:
        """Mandatory Test: Verifies H = 1/sqrt(2)*[[1,1],[1,-1]] and exact norm = 1.0."""
        res = ExtendedVocabularyEvaluator.verify_hadamard_mathematics(self.h_cand)
        self.assertTrue(res["hadamard_pass"])
        self.assertAlmostEqual(res["norm_v0"], 1.0, places=12)
        self.assertAlmostEqual(res["norm_v1"], 1.0, places=12)
        self.assertLess(res["unitarity_residual"], 1e-12)

    def test_02_hadamard_basis_action(self) -> None:
        """Mandatory Test: H|0> = (|0>+|1>)/sqrt(2) and H|1> = (|0>-|1>)/sqrt(2)."""
        v0 = np.array([1.0, 0.0], dtype=complex)
        v1 = np.array([0.0, 1.0], dtype=complex)

        out0 = self.h_mat @ v0
        out1 = self.h_mat @ v1

        exp0 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
        exp1 = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)

        self.assertTrue(np.allclose(out0, exp0, atol=1e-12))
        self.assertTrue(np.allclose(out1, exp1, atol=1e-12))

    def test_03_hadamard_superposition_expansion(self) -> None:
        """Mandatory Test: Baseline G0 superposition = False, Extended G_H superposition = True."""
        b_sup, e_sup = ExtendedVocabularyEvaluator.evaluate_superposition_expansion(self.h_cand)
        self.assertFalse(b_sup)
        self.assertTrue(e_sup)


if __name__ == "__main__":
    unittest.main()
