"""
Module 6 Stage 2 Unit Test Suite — Expressibility Reporting, Serialization, & Negative Rejections.

Tests end-to-end Stage 2 analysis, JSON serialization roundtrip, determinism, provenance, and negative failure paths.
"""

import unittest
from src.module6 import (
    analyze_compiler_image_stage2,
    ExpressibilityExperimentConfig,
    serialize_expressibility_report,
    deserialize_expressibility_report,
    Stage2FailureCode,
)


class TestStage2ExpressibilityReport(unittest.TestCase):
    def test_01_end_to_end_stage2_analysis_pass(self) -> None:
        """Positive test: End-to-end Stage 2 analysis orchestrator PASS."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_e2e_pass")
        report = analyze_compiler_image_stage2(config)

        self.assertEqual(report.experiment_id, "exp_e2e_pass")
        self.assertGreater(report.sample_size, 0)
        self.assertGreater(report.circuit_image_size, 0)
        self.assertGreater(report.operator_image_size, 0)
        self.assertGreater(report.target_count, 0)
        self.assertIsNone(report.failure_code)

    def test_02_report_serialization_roundtrip(self) -> None:
        """Positive test: Report JSON serialization and deserialization roundtrip invariant."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_ser_test")
        report = analyze_compiler_image_stage2(config)

        json_str = serialize_expressibility_report(report)
        reconstructed = deserialize_expressibility_report(json_str)

        self.assertEqual(reconstructed.experiment_id, report.experiment_id)
        self.assertEqual(reconstructed.sample_size, report.sample_size)
        self.assertEqual(reconstructed.circuit_image_size, report.circuit_image_size)
        self.assertEqual(reconstructed.operator_image_size, report.operator_image_size)
        self.assertEqual(reconstructed.deterministic_analysis_id, report.deterministic_analysis_id)
        self.assertEqual(len(reconstructed.target_results), len(report.target_results))

    def test_03_determinism_and_repeated_analysis(self) -> None:
        """Positive test: Repeated analysis produces identical report and deterministic_analysis_id."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_det_test")
        rep1 = analyze_compiler_image_stage2(config)
        rep2 = analyze_compiler_image_stage2(config)

        self.assertEqual(rep1.deterministic_analysis_id, rep2.deterministic_analysis_id)
        self.assertEqual(rep1.circuit_image_size, rep2.circuit_image_size)
        self.assertEqual(rep1.operator_image_size, rep2.operator_image_size)

    def test_04_negative_empty_algorithm_family_rejection(self) -> None:
        """Negative test: Rejects empty algorithm family configuration."""
        empty_config = ExpressibilityExperimentConfig(algorithm_family_ids=())
        report = analyze_compiler_image_stage2(empty_config)

        self.assertEqual(report.failure_code, Stage2FailureCode.INVALID_ALGORITHM_FAMILY)
        self.assertEqual(report.sample_size, 0)


if __name__ == "__main__":
    unittest.main()
