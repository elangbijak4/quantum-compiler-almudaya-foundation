"""
Module 6 Stage 6 Test Suite — 3-Level Vocabulary Diagnosis.
"""

import unittest

from src.module6.classical.semantic import ClassicalSemanticModel, create_sample_adder_model
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.feasibility.model import FeasibilityStatus, DiagnosisLevel
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer


class TestStage6Diagnosis(unittest.TestCase):
    """Tests for 3-Level Vocabulary Diagnosis Hierarchy."""

    def test_three_level_diagnosis_distinction(self) -> None:
        """Req 22: Distinguish Level 1, Level 2, and Level 3 diagnosis levels."""
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

        base_model = create_sample_adder_model()
        from dataclasses import replace
        q_model = replace(base_model, algorithm_id="quantum_superposition_demo")


        # Level 1: User baseline Bu = {X, CNOT} insufficient, GE(1) = {X, CNOT, TOFFOLI, HADAMARD} sufficient
        b_user = SessionBaseline(
            session_id="s_user",
            selected_gates=("CNOT", "X"),
            baseline_hash="",
            source_evolution_stage="GE_1",
            source_vocabulary_hash=ge1.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        rep1 = CompilationFeasibilityAnalyzer.analyze_feasibility(q_model, ge1, b_user)
        self.assertEqual(rep1.diagnosis_level, DiagnosisLevel.LEVEL_1_USER_BASELINE_INSUFFICIENT)

        # Level 2: Evolutionary baseline GE(0) = {X, CNOT, TOFFOLI} insufficient for superposition model
        b_ge0 = SessionBaseline(
            session_id="s_ge0",
            selected_gates=ge0.vocabulary,
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=ge0.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )
        rep2 = CompilationFeasibilityAnalyzer.analyze_feasibility(q_model, ge0, b_ge0)
        self.assertEqual(rep2.diagnosis_level, DiagnosisLevel.LEVEL_2_EVOLUTIONARY_BASELINE_INSUFFICIENT)


if __name__ == "__main__":
    unittest.main()
