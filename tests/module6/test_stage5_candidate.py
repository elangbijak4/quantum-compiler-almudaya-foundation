"""
Module 6 Stage 5 Unit Test Suite — Candidate Gate Model & Unitarity.

Verifies candidate gate creation, matrix shape validation, and left/right unitarity checks.
"""

import unittest
import numpy as np
from src.module6.evolution import CandidateGate, compute_canonical_matrix_hash


class TestStage5Candidate(unittest.TestCase):
    def test_01_valid_candidate_creation(self) -> None:
        """Positive test: Creates valid 1-qubit candidate gate H."""
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        cand = CandidateGate(
            gate_id="cand_h",
            name="HADAMARD",
            arity=1,
            matrix=h_mat,
            provenance={"author": "test"},
        )
        self.assertEqual(cand.gate_id, "cand_h")
        self.assertEqual(cand.arity, 1)
        self.assertIsNotNone(cand.canonical_hash)

    def test_02_non_unitary_candidate_rejection(self) -> None:
        """Negative test: Rejects non-unitary matrix with NON_UNITARY_CANDIDATE."""
        non_unitary_mat = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=complex)  # Shear matrix
        with self.assertRaises(ValueError) as ctx:
            CandidateGate(
                gate_id="cand_bad",
                name="BAD_SHEAR",
                arity=1,
                matrix=non_unitary_mat,
            )
        self.assertIn("NON_UNITARY_CANDIDATE", str(ctx.exception))

    def test_03_invalid_shape_rejection(self) -> None:
        """Negative test: Rejects matrix shape incompatible with declared arity."""
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        with self.assertRaises(ValueError) as ctx:
            CandidateGate(
                gate_id="cand_bad_arity",
                name="HADAMARD_2Q",
                arity=2,  # Declared arity 2 expects 4x4 matrix, but provided 2x2
                matrix=h_mat,
            )
        self.assertIn("INVALID_CANDIDATE_GATE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
