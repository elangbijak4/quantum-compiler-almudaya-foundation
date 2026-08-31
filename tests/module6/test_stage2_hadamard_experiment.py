"""
Module 6 Stage 2 Unit Test Suite — Mandatory Hadamard Experiment.

Executes mandatory Hadamard H target experiment, verifying exact primitive vocabulary vs compiler image status
without overclaiming universal non-surjectivity.
"""

import unittest
from src.module6 import (
    analyze_compiler_image_stage2,
    ExpressibilityExperimentConfig,
    TargetReachabilityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
)


class TestStage2HadamardExperiment(unittest.TestCase):
    def test_01_mandatory_hadamard_experiment_execution(self) -> None:
        """Positive test: Mandatory Hadamard H target experiment runs and returns valid TargetReachabilityResult."""
        config = ExpressibilityExperimentConfig(experiment_id="exp_hadamard_test")
        report = analyze_compiler_image_stage2(config)

        self.assertIsNotNone(report.hadamard_result)
        self.assertEqual(report.hadamard_result.target_id, "target_H")

        # Hadamard is not expressible in primitive vocabulary G_primitive={X, CNOT, TOFFOLI}
        self.assertEqual(
            report.hadamard_result.primitive_reachability,
            "NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY",
        )

        # In bounded classical compiler search over reversible primitive circuits, H status is NOT_FOUND_IN_SEARCH, DIMENSION_MISMATCH, or FOUND
        self.assertIn(
            report.hadamard_result.status,
            (
                TargetReachabilityStatus.NOT_FOUND_IN_SEARCH,
                TargetReachabilityStatus.DIMENSION_MISMATCH,
                TargetReachabilityStatus.FOUND,
            ),
        )

        # Surjectivity & Universal Expressibility MUST remain UNPROVEN
        self.assertEqual(report.surjectivity_status, SurjectivityStatus.UNPROVEN)
        self.assertEqual(report.universal_expressibility_status, UniversalExpressibilityStatus.UNPROVEN)

    def test_02_hadamard_result_does_not_overclaim(self) -> None:
        """Positive test: Verification that status does not overclaim H not in Img(F) as universal proof."""
        config = ExpressibilityExperimentConfig()
        report = analyze_compiler_image_stage2(config)

        # Must be bounded search statement, not a string asserting universal non-surjectivity
        self.assertNotEqual(report.hadamard_result.compiler_image_reachability, "IMPOSSIBLE")
        self.assertNotEqual(report.hadamard_result.compiler_image_reachability, "UNIVERSALLY_EXCLUDED")


if __name__ == "__main__":
    unittest.main()
