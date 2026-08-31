"""
Module 6 Stage 6 Test Suite — Governed Vocabulary Promotion.
"""

import unittest

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager


class TestStage6Promotion(unittest.TestCase):
    """Tests for PromotionRecord and Governed Vocabulary Promotion."""

    def test_governed_promotion_success(self) -> None:
        """Req 6, 7: Verify explicit, governed promotion of candidates into GE(1)."""
        lineage = EvolutionaryLineageManager()
        ge0 = lineage.current_state

        prom_rec = PromotionRecord(
            promotion_id="PROM_001",
            parent_evolution_stage=ge0.evolution_stage_id,
            candidate_gate_ids=("HADAMARD", "PHASE_S", "T_GATE"),
            candidate_hashes=("h1", "h2", "h3"),
            evidence_reference="STAGE_5_EVIDENCE_001",
            equivalence_reference="STAGE_4_LEVEL_6",
            authorization_status=PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED,
            authorized_by="HUMAN_GOVERNOR",
            promotion_timestamp="2026-08-24T13:00:00Z",
            resulting_vocabulary_hash="",
        )

        ge1 = lineage.promote_candidates(prom_rec, ("HADAMARD", "PHASE_S", "T_GATE"))
        self.assertEqual(ge1.evolution_stage_id, "GE_1")
        self.assertEqual(ge1.parent_stage_id, "GE_0")
        self.assertEqual(ge1.vocabulary, ("CNOT", "HADAMARD", "PHASE_S", "TOFFOLI", "T_GATE", "X"))
        self.assertTrue(set(ge0.vocabulary).issubset(set(ge1.vocabulary)))

    def test_unauthorized_promotion_rejected(self) -> None:
        """Req 6: Verify pending or unauthorized promotion raises ValueError."""
        lineage = EvolutionaryLineageManager()
        ge0 = lineage.current_state

        unauth_rec = PromotionRecord(
            promotion_id="PROM_UNAUTH",
            parent_evolution_stage=ge0.evolution_stage_id,
            candidate_gate_ids=("HADAMARD",),
            candidate_hashes=("h1",),
            evidence_reference="NONE",
            equivalence_reference="NONE",
            authorization_status=PromotionAuthorizationStatus.PENDING_AUTHORIZATION,
            authorized_by="NONE",
            promotion_timestamp="2026-08-24T13:00:00Z",
            resulting_vocabulary_hash="",
        )

        with self.assertRaises(ValueError):
            lineage.promote_candidates(unauth_rec, ("HADAMARD",))


if __name__ == "__main__":
    unittest.main()
