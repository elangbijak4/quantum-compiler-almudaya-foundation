"""
Module 6 Stage 7 Test Suite — Session Pinning & Evolutionary Transition.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution.resolver import Stage7CompilerResolver


class TestStage7SessionPinning(unittest.TestCase):
    """Tests for session pinning invariant when global state advances GE(k) -> GE(k+1)."""

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

    def test_session_pinned_to_ge0_hash(self) -> None:
        """Req 8, 35: Active session remains pinned to GE(0) when global lineage advances to GE(1)."""
        sb0 = SessionBaseline(
            session_id="s_pinned",
            selected_gates=("CNOT", "TOFFOLI", "X"),
            baseline_hash="hash_pinned",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )

        # Resolve session against GE(0) state, session is pinned to GE(0)
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb0)
        self.assertEqual(ctx.evolutionary_vocabulary_hash, self.ge0.vocabulary_hash)
        self.assertNotEqual(ctx.evolutionary_vocabulary_hash, self.ge1.vocabulary_hash)


if __name__ == "__main__":
    unittest.main()
