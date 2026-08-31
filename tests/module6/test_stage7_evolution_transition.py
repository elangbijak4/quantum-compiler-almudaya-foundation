"""
Module 6 Stage 7 Test Suite — Evolutionary Lineage & GE(k) Transition.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7EvolutionTransition(unittest.TestCase):
    """Tests for resolution across evolutionary stage transitions GE(0) -> GE(1)."""

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

    def test_ge1_default_resolution(self) -> None:
        """Req 6: GE(1) default resolution includes promoted gates H, S, T."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge1)
        self.assertEqual(ctx.evolution_stage, "GE_1")
        self.assertEqual(
            ctx.effective_vocabulary,
            ("CNOT", "HADAMARD", "PHASE_S", "TOFFOLI", "T_GATE", "X"),
        )


if __name__ == "__main__":
    unittest.main()
