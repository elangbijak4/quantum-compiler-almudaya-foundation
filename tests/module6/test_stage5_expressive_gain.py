"""
Module 6 Stage 5 Unit Test Suite — Expressive Gain Metrics.

Verifies calculation of expressive gain delta, target coverage, and image cardinality expansion.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, EvolvingCompilerAnalyzer, ExpressiveGainMetrics


class TestStage5ExpressiveGain(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = EvolvingCompilerAnalyzer()
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        self.cand_h = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

    def test_01_expressive_gain_metrics(self) -> None:
        """Positive test: Calculates ExpressiveGainMetrics for Hadamard extension."""
        report = self.analyzer.analyze_candidate_extension(self.cand_h)
        metrics = report.metrics

        self.assertGreater(metrics.expressive_gain_delta, 0)
        self.assertGreater(metrics.expressive_gain_ratio, 0.0)
        self.assertGreater(metrics.target_coverage_extended, metrics.target_coverage_baseline)


if __name__ == "__main__":
    unittest.main()
