"""
Module 6 Stage 6 Test Suite — Compilation Feasibility Analyzer.
"""

import unittest

from src.module6.classical.semantic import create_sample_adder_model, ClassicalSemanticModel
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.feasibility.model import FeasibilityStatus
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer


class TestStage6Feasibility(unittest.TestCase):
    """Tests for CompilationFeasibilityAnalyzer."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.adder = create_sample_adder_model()

    def test_feasible_adder_on_g0(self) -> None:
        """Req 12, 13: Adder algorithm model is feasible under G0."""
        b_g0 = SessionBaseline(
            session_id="s_g0",
            selected_gates=self.ge0.vocabulary,
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )

        report = CompilationFeasibilityAnalyzer.analyze_feasibility(self.adder, self.ge0, b_g0)
        self.assertEqual(report.feasibility_status, FeasibilityStatus.FEASIBLE)
        self.assertEqual(report.algorithm_id, self.adder.algorithm_id)
        self.assertFalse(report.fallback_available)

    def test_infeasible_user_baseline(self) -> None:
        """Req 14: Quantum superposition model infeasible under user baseline Bu = {X, CNOT} when GE(1) has HADAMARD."""
        from src.module6.evolution.lineage import EvolutionaryLineageManager
        from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
        lineage = EvolutionaryLineageManager()
        ge0 = lineage.current_state
        prom_rec = PromotionRecord(
            promotion_id="PROM_001",
            parent_evolution_stage=ge0.evolution_stage_id,
            candidate_gate_ids=("HADAMARD",),
            candidate_hashes=("h1",),
            evidence_reference="EVID",
            equivalence_reference="EQ",
            authorization_status=PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED,
            authorized_by="GOVERNOR",
            promotion_timestamp="2026-08-24T13:00:00Z",
            resulting_vocabulary_hash="",
        )
        ge1 = lineage.promote_candidates(prom_rec, ("HADAMARD",))

        from dataclasses import replace
        q_model = replace(self.adder, algorithm_id="quantum_superposition_demo")

        b_user = SessionBaseline(
            session_id="s_user",
            selected_gates=("CNOT", "X"),
            baseline_hash="",
            source_evolution_stage="GE_1",
            source_vocabulary_hash=ge1.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )

        report = CompilationFeasibilityAnalyzer.analyze_feasibility(q_model, ge1, b_user)
        self.assertEqual(report.feasibility_status, FeasibilityStatus.INFEASIBLE_UNDER_USER_BASELINE)
        self.assertIn("SUPERPOSITION", report.missing_capabilities)



if __name__ == "__main__":
    unittest.main()
