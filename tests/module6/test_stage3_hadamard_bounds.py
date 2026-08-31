"""
Module 6 Stage 3 Unit Test Suite — Hadamard Formal Exclusion & Serialization Roundtrip.

Verifies Hadamard formal exclusion derivation (H not in Perm(2) => H not in Img_Q(F)) and canonical JSON serialization.
"""

import unittest
from src.module6 import (
    analyze_compiler_mapping_stage3,
    serialize_stage3_report,
    deserialize_stage3_report,
    ExpressibilityExperimentConfig,
    MappingTotalityStatus,
    QuotientWellDefinednessStatus,
)


class TestStage3HadamardBounds(unittest.TestCase):
    def test_01_hadamard_formal_exclusion_derivation(self) -> None:
        """Positive test: Verification of Hadamard formal exclusion derivation."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_hadamard_stage3")
        report = analyze_compiler_mapping_stage3(config)

        self.assertEqual(report.hadamard_formal_status, "FORMALLY_EXCLUDED")
        self.assertIn("Hadamard Formal Exclusion", report.hadamard_exclusion_proof)
        self.assertIn("H is NOT a computational-basis permutation matrix", report.hadamard_exclusion_proof)
        self.assertEqual(report.mapping_totality_status, MappingTotalityStatus.TOTAL_OVER_DEFINED_DOMAIN)

    def test_02_report_serialization_roundtrip(self) -> None:
        """Positive test: Stage3AnalysisReport canonical JSON serialization roundtrip invariant."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_ser_test")
        report = analyze_compiler_mapping_stage3(config)

        json_str = serialize_stage3_report(report)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 100)

        deserialized = deserialize_stage3_report(json_str)
        self.assertEqual(deserialized.experiment_id, report.experiment_id)
        self.assertEqual(deserialized.hadamard_formal_status, report.hadamard_formal_status)
        self.assertEqual(deserialized.deterministic_analysis_id, report.deterministic_analysis_id)
        self.assertEqual(deserialized.mapping_totality_status, report.mapping_totality_status)

    def test_03_determinism_and_repeated_analysis(self) -> None:
        """Positive test: Repeated Stage 3 analysis produces identical report and deterministic_analysis_id."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_det_test")
        rep1 = analyze_compiler_mapping_stage3(config)
        rep2 = analyze_compiler_mapping_stage3(config)

        self.assertEqual(rep1.deterministic_analysis_id, rep2.deterministic_analysis_id)
        self.assertEqual(serialize_stage3_report(rep1), serialize_stage3_report(rep2))


if __name__ == "__main__":
    unittest.main()
