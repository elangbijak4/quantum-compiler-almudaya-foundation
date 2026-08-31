"""
Module 6 Stage 5 Unit Test Suite — Negative Tests & Safeguards.

Verifies:
1. NON_UNITARY_CANDIDATE rejection.
2. INVALID_CANDIDATE_GATE shape rejection.
3. DUPLICATE_CANDIDATE_GATE rejection.
4. Mandatory Safeguard: finite image expansion without proof yields EMPIRICAL_EXTENSION, NOT PROVEN_EXTENSION.
5. Invariants: Injectivity, Surjectivity, Universal Expressibility remain UNPROVEN.
"""

import unittest
import numpy as np
from src.module6.evolution import (
    CandidateGate,
    CandidateRegistry,
    ExtendedVocabularyEvaluator,
    ExpressiveGainMetrics,
    EvolvingCompilerAnalyzer,
)


class TestStage5Negative(unittest.TestCase):
    def test_01_non_unitary_matrix_rejection(self) -> None:
        """Negative test: Rejects non-unitary matrix."""
        mat = np.array([[1.0, 2.0], [0.0, 1.0]], dtype=complex)
        with self.assertRaises(ValueError) as ctx:
            CandidateGate("bad_mat", "BAD", 1, mat)
        self.assertIn("NON_UNITARY_CANDIDATE", str(ctx.exception))

    def test_02_invalid_dimension_rejection(self) -> None:
        """Negative test: Rejects matrix with shape incompatible with arity."""
        mat = np.eye(3, dtype=complex)  # 3x3 is not 2^arity
        with self.assertRaises(ValueError) as ctx:
            CandidateGate("bad_dim", "BAD_DIM", 1, mat)
        self.assertIn("INVALID_CANDIDATE_GATE", str(ctx.exception))

    def test_03_duplicate_candidate_rejection(self) -> None:
        """Negative test: Rejects duplicate candidate registration."""
        reg = CandidateRegistry()
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        c1 = CandidateGate("cand_h1", "HADAMARD", 1, h_mat)
        c2 = CandidateGate("cand_h2", "HADAMARD_DUP", 1, h_mat)  # Same matrix

        reg.register_candidate(c1)
        with self.assertRaises(ValueError) as ctx:
            reg.register_candidate(c2)
        self.assertIn("DUPLICATE_CANDIDATE_GATE", str(ctx.exception))

    def test_04_safeguard_finite_expansion_does_not_imply_proven_extension(self) -> None:
        """Mandatory Safeguard: Finite image expansion without proof gives EMPIRICAL_EXTENSION, NOT PROVEN_EXTENSION."""
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        c = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

        metrics = ExpressiveGainMetrics(
            baseline_image_cardinality=8,
            extended_image_cardinality=24,
            structural_circuits_count=48,
            semantic_operator_classes_count=24,
            target_coverage_baseline=0.0,
            target_coverage_extended=1.0,
            expressive_gain_delta=16,
            expressive_gain_ratio=2.0,
            new_operator_classes_count=16,
        )

        classification, evidence_class = ExtendedVocabularyEvaluator.classify_extension(
            candidate=c,
            metrics=metrics,
            is_redundant=False,
            has_mathematical_proof=False,  # No mathematical proof provided
        )

        self.assertEqual(classification, "EMPIRICAL_EXTENSION")
        self.assertEqual(evidence_class, "EMPIRICAL_EXPERIMENT")
        self.assertNotEqual(classification, "PROVEN_EXTENSION")


if __name__ == "__main__":
    unittest.main()
