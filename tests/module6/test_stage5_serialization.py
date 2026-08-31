"""
Module 6 Stage 5 Unit Test Suite — Canonical JSON Serialization.

Verifies canonical JSON serialization and deserialization round-trip for Stage 5 analytical objects.
"""

import unittest
import numpy as np
from src.module6.evolution import (
    CandidateGate,
    TargetOperator,
    EvolvingCompilerAnalyzer,
    serialize_stage5_object,
    deserialize_candidate_gate,
    deserialize_target_operator,
    deserialize_extension_report,
)


class TestStage5Serialization(unittest.TestCase):
    def test_01_candidate_gate_serialization_roundtrip(self) -> None:
        """Positive test: CandidateGate JSON roundtrip."""
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        cand = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

        json_str = serialize_stage5_object(cand)
        reconstructed = deserialize_candidate_gate(json_str)

        self.assertEqual(cand.gate_id, reconstructed.gate_id)
        self.assertEqual(cand.canonical_hash, reconstructed.canonical_hash)
        self.assertTrue(np.allclose(cand.matrix, reconstructed.matrix, atol=1e-12))

    def test_02_extension_report_serialization_roundtrip(self) -> None:
        """Positive test: ExtensionReport JSON roundtrip."""
        analyzer = EvolvingCompilerAnalyzer()
        h_mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        cand = CandidateGate("cand_h", "HADAMARD", 1, h_mat)

        report = analyzer.analyze_candidate_extension(cand)
        json_str = serialize_stage5_object(report)
        reconstructed = deserialize_extension_report(json_str)

        self.assertEqual(report.candidate_id, reconstructed.candidate_id)
        self.assertEqual(report.classification, reconstructed.classification)
        self.assertEqual(report.provenance.deterministic_analysis_id, reconstructed.provenance.deterministic_analysis_id)


if __name__ == "__main__":
    unittest.main()
