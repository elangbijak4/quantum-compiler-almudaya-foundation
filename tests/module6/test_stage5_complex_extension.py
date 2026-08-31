"""
Module 6 Stage 5 Unit Test Suite — Complex Amplitude Expansion.

Verifies Phase gate S and T gate complex amplitude generation.
"""

import unittest
import numpy as np
from src.module6.evolution import (
    CandidateGate,
    ExtendedVocabularyEvaluator,
    get_reference_target_phase,
    get_reference_target_t,
)


class TestStage5ComplexExtension(unittest.TestCase):
    def setUp(self) -> None:
        s_mat = np.array([[1.0, 0.0], [0.0, 1j]], dtype=complex)
        t_mat = np.array([[1.0, 0.0], [0.0, np.exp(1j * np.pi / 4.0)]], dtype=complex)

        self.cand_s = CandidateGate("cand_s", "PHASE_S", 1, s_mat)
        self.cand_t = CandidateGate("cand_t", "T_GATE", 1, t_mat)

    def test_01_phase_s_complex_amplitude_generation(self) -> None:
        """Positive test: Phase S gate breaks real-amplitude invariant."""
        b_real, e_real = ExtendedVocabularyEvaluator.evaluate_complex_amplitude_expansion(self.cand_s)
        self.assertTrue(b_real)
        self.assertFalse(e_real)

    def test_02_t_gate_complex_amplitude_generation(self) -> None:
        """Positive test: T gate breaks real-amplitude invariant."""
        b_real, e_real = ExtendedVocabularyEvaluator.evaluate_complex_amplitude_expansion(self.cand_t)
        self.assertTrue(b_real)
        self.assertFalse(e_real)


if __name__ == "__main__":
    unittest.main()
