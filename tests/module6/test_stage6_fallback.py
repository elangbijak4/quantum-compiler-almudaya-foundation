"""
Module 6 Stage 6 Test Suite — Fallback Policy.
"""

import unittest

from src.module6.classical.semantic import ClassicalSemanticModel, create_sample_adder_model
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import CompilationStatus


class TestStage6Fallback(unittest.TestCase):
    """Tests for Fallback Policy (Recommendation-only, no auto-execution)."""

    def test_fallback_is_recommendation_only(self) -> None:
        """Req 20: Fallback available = True does NOT trigger automatic fallback compilation."""
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

        ctx = CompilerContext(ge1)
        # Set user baseline Bu = {X, CNOT}
        ctx.session_lifecycle.select_user_baseline(("CNOT", "X"))

        base_model = create_sample_adder_model()
        from dataclasses import replace
        q_model = replace(base_model, algorithm_id="quantum_superposition_demo")


        res = ctx.compile(q_model)
        self.assertEqual(res.compilation_status, CompilationStatus.INEXPRESSIBLE_UNDER_BASELINE)
        self.assertTrue(res.fallback_available)
        self.assertEqual(res.fallback_baseline, ("CNOT", "HADAMARD", "TOFFOLI", "X"))
        # Circuit MUST NOT be generated without explicit user authorization
        self.assertIsNone(res.circuit_id)


if __name__ == "__main__":
    unittest.main()
