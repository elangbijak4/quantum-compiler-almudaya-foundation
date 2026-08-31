"""
Module 6 Stage 9 Test Suite — Dual Result Analysis Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality


class TestStage9DualResult(unittest.TestCase):
    """Tests verifying Stage 7 Dual Result compatibility and comparative reporting without fallback execution."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit_user = CompilerMapper.map_classical_model(self.model, self.program)
        self.circuit_evo = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_both_feasible_dual_result_comparison(self) -> None:
        """Case A: Both user baseline and evolutionary baseline circuits present -> compare both."""
        report = analyze_stage9_compilation_quality(
            circuit=self.circuit_user,
            context=self.ctx,
            model=self.model,
            user_baseline_circuit=self.circuit_user,
            evolutionary_baseline_circuit=self.circuit_evo,
        )
        self.assertTrue(report.dual_result_analysis["user_baseline_present"])
        self.assertTrue(report.dual_result_analysis["evolutionary_baseline_present"])
        self.assertIn("comparison", report.dual_result_analysis)
        self.assertIn("CASE_A_BOTH_FEASIBLE_COMPARISON", report.dual_result_analysis["cases_evaluated"])

    def test_02_no_dual_result_provided(self) -> None:
        """Standard compilation without explicit dual result circuits handles gracefully."""
        report = analyze_stage9_compilation_quality(
            circuit=self.circuit_user,
            context=self.ctx,
            model=self.model,
        )
        self.assertFalse(report.dual_result_analysis["user_baseline_present"])
        self.assertFalse(report.dual_result_analysis["evolutionary_baseline_present"])


if __name__ == "__main__":
    unittest.main()
