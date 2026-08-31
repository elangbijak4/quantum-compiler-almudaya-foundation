"""
Module 6 Stage 5 Unit Test Suite — Baseline vs Extended Expressibility Analysis.

Verifies EvolvingCompilerAnalyzer candidate extension analysis and image comparison.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, EvolvingCompilerAnalyzer


class TestStage5BaselineExtension(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = EvolvingCompilerAnalyzer()
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        self.cand_h = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

    def test_01_hadamard_extension_analysis(self) -> None:
        """Positive test: Hadamard extension yields EMPIRICAL_EXTENSION and target coverage."""
        report = self.analyzer.analyze_candidate_extension(self.cand_h)
        self.assertEqual(report.candidate_id, "cand_h")
        self.assertEqual(report.classification, "EMPIRICAL_EXTENSION")
        self.assertTrue(report.hadamard_extension_pass)
        self.assertTrue(report.superposition_capability_extended)
        self.assertTrue(report.backward_compatibility_pass)


if __name__ == "__main__":
    unittest.main()
