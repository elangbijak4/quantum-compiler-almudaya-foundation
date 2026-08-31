"""
Module 6 Stage 5 Unit Test Suite — Candidate Gate Redundancy Analysis.

Verifies detection of redundant candidate gates expressible by baseline G0 = {X, CNOT, TOFFOLI}.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, EvolvingCompilerAnalyzer, ExtendedVocabularyEvaluator


class TestStage5Redundancy(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = EvolvingCompilerAnalyzer()
        x_mat = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        self.cand_x = CandidateGate("cand_x", "X", 1, x_mat)

    def test_01_redundant_gate_detection(self) -> None:
        """Positive test: Redundant X gate candidate detected and classified as REDUNDANT."""
        is_red = ExtendedVocabularyEvaluator.evaluate_gate_redundancy(self.cand_x)
        self.assertTrue(is_red)

        report = self.analyzer.analyze_candidate_extension(self.cand_x)
        self.assertEqual(report.classification, "REDUNDANT")
        self.assertTrue(report.redundancy_detected)


if __name__ == "__main__":
    unittest.main()
