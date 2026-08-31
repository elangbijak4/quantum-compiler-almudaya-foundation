"""
Module 6 Stage 7 Test Suite — Recommendation-Only Fallback Policy.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.classical.semantic import create_sample_adder_model, ClassicalSemanticModel
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7Fallback(unittest.TestCase):
    """Tests enforcing recommendation-only fallback policy (zero automatic execution/mutation)."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.mgr = EvolutionaryLineageManager(self.ge0)
        p_record = PromotionRecord(
            promotion_id="p_1",
            parent_evolution_stage=self.ge0.evolution_stage_id,
            candidate_gate_ids=("HADAMARD", "PHASE_S", "T_GATE"),
            candidate_hashes=("h1", "h2", "h3"),
            evidence_reference="EVID_STAGE5",
            equivalence_reference="EQUIV_STAGE5",
            authorization_status=PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED,
            authorized_by="ARCHITECT",
            promotion_timestamp="2026-08-24T00:00:00Z",
            resulting_vocabulary_hash="",
        )
        self.ge1 = self.mgr.promote_candidates(p_record, ("HADAMARD", "PHASE_S", "T_GATE"))

        sample = create_sample_adder_model()
        self.model_hadamard = ClassicalSemanticModel(
            algorithm_id="hadamard_quantum_model",
            source_program_hash=sample.source_program_hash,
            domain_contract=sample.domain_contract,
            encoding_spec=sample.encoding_spec,
            state_map=sample.state_map,
            symbol_map=sample.symbol_map,
            transition_table=sample.transition_table,
        )

    def test_fallback_is_recommendation_only(self) -> None:
        """Req 19: Fallback status is recommendation-only and requires explicit user authorization."""
        sb_restr = SessionBaseline(
            session_id="s_restr",
            selected_gates=("CNOT", "X"),
            baseline_hash="h_restr",
            source_evolution_stage="GE_1",
            source_vocabulary_hash=self.ge1.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        res = Stage7CompilerResolver.resolve_and_evaluate_feasibility(
            model=self.model_hadamard,
            evolution_state=self.ge1,
            session_baseline=sb_restr,
        )
        self.assertTrue(res.fallback_available)
        self.assertEqual(res.action_required, "USER_AUTHORIZATION_REQUIRED")
        self.assertEqual(res.evolutionary_fallback_vocabulary, ("CNOT", "HADAMARD", "PHASE_S", "TOFFOLI", "T_GATE", "X"))
        # Verify that underlying session baseline was NOT automatically mutated
        self.assertEqual(sb_restr.selected_gates, ("CNOT", "X"))


if __name__ == "__main__":
    unittest.main()
