"""
Module 6 Stage 4 Unit Test Suite — Global Phase vs Exact Equality.

Verifies state and operator phase overlap functions.
Verifies distinction between global phase shifts and relative phase changes.
"""

import unittest
import numpy as np
from src.module6 import PhaseOverlapEvaluator


class TestStage4Phase(unittest.TestCase):
    def test_01_state_global_phase(self) -> None:
        """Positive test: Global phase shift e^{i phi} on state vector."""
        v1 = np.array([1.0, 0.0], dtype=complex)
        v2 = np.array([1j, 0.0], dtype=complex)  # phase shift e^{i pi/2}

        overlap, l2_res, is_exact, is_phase = PhaseOverlapEvaluator.state_phase_overlap(v1, v2)
        self.assertFalse(is_exact)
        self.assertTrue(is_phase)
        self.assertAlmostEqual(overlap, 1.0, places=10)

    def test_02_state_relative_phase_not_global_phase(self) -> None:
        """Mandatory Test: Relative phase shift (|0> + i|1> vs |0> + |1>) is NOT global phase equivalent."""
        v1 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
        v2 = np.array([1.0, 1j], dtype=complex) / np.sqrt(2)

        overlap, l2_res, is_exact, is_phase = PhaseOverlapEvaluator.state_phase_overlap(v1, v2)
        self.assertFalse(is_exact)
        self.assertFalse(is_phase)
        self.assertLess(overlap, 0.99)

    def test_03_operator_global_phase(self) -> None:
        """Positive test: Global phase factor e^{i phi} on unitary matrix."""
        u1 = np.array([[0, 1], [1, 0]], dtype=complex)  # X
        u2 = 1j * u1  # iX

        overlap, frob_res, is_exact, is_phase, phase_fac = PhaseOverlapEvaluator.operator_phase_overlap(u1, u2)
        self.assertFalse(is_exact)
        self.assertTrue(is_phase)
        self.assertAlmostEqual(overlap, 1.0, places=10)
        self.assertAlmostEqual(phase_fac, 1j, places=10)


if __name__ == "__main__":
    unittest.main()
