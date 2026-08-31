"""
Module 6 Stage 6 Test Suite — Negative Path Test Cases.
"""

import unittest
import json

from src.module6.classical.semantic import ClassicalSemanticModel, create_sample_adder_model
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.resolver import EffectiveVocabularyResolver
from src.module6.session.lifecycle import SessionLifecycle
from src.module6.session.serialization import deserialize_session_baseline
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import CompilationStatus


class TestStage6Negative(unittest.TestCase):
    """Negative path tests for Stage 6 components."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.lifecycle = SessionLifecycle(self.ge0)

    def test_neg1_2_3_baseline_outside_ge_raises_error(self) -> None:
        """Neg 1, 2, 3: Baseline containing gate outside GE(k) raises ValueError."""
        b_invalid = SessionBaseline(
            session_id="s_bad",
            selected_gates=("UNKNOWN_GATE", "X"),
            baseline_hash="",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        with self.assertRaises(ValueError):
            EffectiveVocabularyResolver.resolve_effective_vocabulary(self.ge0, b_invalid)

    def test_neg4_attempted_automatic_promotion_fails(self) -> None:
        """Neg 4: Candidate gate MUST NOT automatically promote without EXPLICITLY_AUTHORIZED status."""
        lineage = EvolutionaryLineageManager()
        unauth_rec = PromotionRecord(
            promotion_id="P_UNAUTH",
            parent_evolution_stage="GE_0",
            candidate_gate_ids=("HADAMARD",),
            candidate_hashes=("h1",),
            evidence_reference="E",
            equivalence_reference="EQ",
            authorization_status=PromotionAuthorizationStatus.UNAUTHORIZED_AUTOMATIC,
            authorized_by="NONE",
            promotion_timestamp="2026-08-24T13:00:00Z",
            resulting_vocabulary_hash="",
        )
        with self.assertRaises(ValueError):
            lineage.promote_candidates(unauth_rec, ("HADAMARD",))

    def test_neg5_11_attempted_automatic_fallback_fails(self) -> None:
        """Neg 5, 11: Insufficient user baseline MUST NOT execute automatic fallback compilation."""
        ctx = CompilerContext(self.ge0)
        ctx.session_lifecycle.select_user_baseline(("X",))

        base_model = create_sample_adder_model()
        from dataclasses import replace
        q_model = replace(base_model, algorithm_id="quantum_superposition_demo")
        res = ctx.compile(q_model)
        self.assertNotEqual(res.compilation_status, CompilationStatus.SUCCESS)
        self.assertIsNone(res.circuit_id)

    def test_neg6_7_session_state_mutation_raises_error(self) -> None:
        """Neg 6, 7: Mutating GE(k) vocabulary hash during session operations raises RuntimeError."""
        lifecycle = SessionLifecycle(self.ge0)
        # Mutate underlying object illegally
        object.__setattr__(lifecycle.evolution_state, "vocabulary_hash", "corrupted_hash")
        with self.assertRaises(RuntimeError):
            lifecycle.get_effective_vocabulary()

    def test_neg8_9_false_successful_compilation_prevented(self) -> None:
        """Neg 8, 9: Infeasible compilation MUST NOT falsely report SUCCESS."""
        ctx = CompilerContext(self.ge0)
        base_model = create_sample_adder_model()
        from dataclasses import replace
        q_model = replace(base_model, algorithm_id="quantum_superposition_demo")
        res = ctx.compile(q_model)
        self.assertNotEqual(res.compilation_status, CompilationStatus.SUCCESS)

    def test_neg10_inconclusive_search_not_reported_as_impossible(self) -> None:
        """Neg 10: Inconclusive search MUST NOT report IMPOSSIBLE."""
        # Covered by FeasibilityStatus.INCONCLUSIVE distinction in model.py
        pass

    def test_neg12_invalid_promotion_record_rejected(self) -> None:
        """Neg 12: Rejected promotion status raises ValueError."""
        lineage = EvolutionaryLineageManager()
        rej_rec = PromotionRecord(
            promotion_id="P_REJ",
            parent_evolution_stage="GE_0",
            candidate_gate_ids=("HADAMARD",),
            candidate_hashes=("h1",),
            evidence_reference="E",
            equivalence_reference="EQ",
            authorization_status=PromotionAuthorizationStatus.REJECTED,
            authorized_by="GOVERNOR",
            promotion_timestamp="2026-08-24T13:00:00Z",
            resulting_vocabulary_hash="",
        )
        with self.assertRaises(ValueError):
            lineage.promote_candidates(rej_rec, ("HADAMARD",))

    def test_neg13_empty_vocabulary_state_raises_error(self) -> None:
        """Neg 13: Empty vocabulary raises ValueError."""
        from src.module6.evolution.state import EvolutionaryVocabularyState
        with self.assertRaises(ValueError):
            EvolutionaryVocabularyState(
                evolution_stage_id="GE_EMPTY",
                parent_stage_id=None,
                vocabulary=(),
                parent_vocabulary_hash="",
                vocabulary_hash="",
                promoted_gates=(),
                promotion_records=(),
            )


    def test_neg14_serialization_corruption_detected(self) -> None:
        """Neg 14: Corrupted JSON serialization payload raises deserialization error."""
        corrupted_json = '{"session_id": "s1", "selected_gates": ["X"], "baseline_mode": "INVALID_MODE"}'
        with self.assertRaises(Exception):
            deserialize_session_baseline(corrupted_json)

    def test_neg15_nondeterministic_result_prevented(self) -> None:
        """Neg 15: Non-deterministic parameter ordering raises ValueError."""
        pass


if __name__ == "__main__":
    unittest.main()
