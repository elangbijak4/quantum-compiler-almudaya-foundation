"""
Module 6 Stage 5 Unit Test Suite — Integration with Stage 4 Multi-Level Equivalence.

Verifies PhaseOverlapEvaluator operator overlap for candidate gates vs target operators.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, get_reference_target_hadamard
from src.module6.equivalence import PhaseOverlapEvaluator


class TestStage5Equivalence(unittest.TestCase):
    def test_01_candidate_target_phase_overlap(self) -> None:
        """Positive test: Verifies exact operator match between candidate H and target H."""
        h_target = get_reference_target_hadamard()
        h_cand = CandidateGate("cand_h", "HADAMARD", 1, h_target.matrix)

        overlap, frob_res, is_exact, is_phase, _ = PhaseOverlapEvaluator.operator_phase_overlap(
            h_cand.matrix, h_target.matrix
        )

        self.assertTrue(is_exact)
        self.assertAlmostEqual(overlap, 1.0, places=12)
        self.assertLess(frob_res, 1e-12)


if __name__ == "__main__":
    unittest.main()
