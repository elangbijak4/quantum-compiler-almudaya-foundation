"""
Module 6 Stage 7 Test Suite — Comprehensive Negative Cases.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.classical.semantic import create_sample_adder_model, ClassicalSemanticModel
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.model import ConfigurationStatus
from src.module6.integration.result import CompilationStatus


class TestStage7Negative(unittest.TestCase):
    """Tests covering mandatory negative cases for Stage 7 Resolution Engine."""

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

    def test_neg_01_baseline_contains_unknown_gate(self) -> None:
        """Neg Case 1: Baseline containing gate outside GE(0) marks INVALID_CONFIGURATION."""
        sb = SessionBaseline(
            session_id="s_bad",
            selected_gates=("X", "INVALID_GATE_XYZ"),
            baseline_hash="h1",
            source_evolution_stage="GE_0",
            source_vocabulary_hash=self.ge0.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0, sb)
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)

    def test_neg_02_empty_baseline_prohibited(self) -> None:
        """Neg Case 2: Forbidding all gates resulting in empty effective baseline marks INVALID_CONFIGURATION."""
        comp_c = {"forbidden_gates": ["CNOT", "TOFFOLI", "X"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, compilation_constraints=comp_c
        )
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)
        self.assertEqual(ctx.effective_vocabulary, ())

    def test_neg_03_required_gate_unavailable(self) -> None:
        """Neg Case 3: Required gate unavailable in GE(0) marks INVALID_CONFIGURATION."""
        comp_c = {"required_gates": ["HADAMARD"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, compilation_constraints=comp_c
        )
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)

    def test_neg_04_no_automatic_fallback(self) -> None:
        """Neg Case 4: Automatic fallback does NOT mutate user baseline or execute automatically."""
        sb = SessionBaseline(
            session_id="s_restr",
            selected_gates=("CNOT", "X"),
            baseline_hash="h3",
            source_evolution_stage="GE_1",
            source_vocabulary_hash=self.ge1.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        res = Stage7CompilerResolver.resolve_and_evaluate_feasibility(
            model=self.model_hadamard,
            evolution_state=self.ge1,
            session_baseline=sb,
        )
        self.assertEqual(res.user_configuration_status, "INFEASIBLE")
        self.assertEqual(res.action_required, "USER_AUTHORIZATION_REQUIRED")
        # Ensure user baseline wasn't modified
        self.assertEqual(sb.selected_gates, ("CNOT", "X"))

    def test_neg_05_no_hidden_gate_expansion(self) -> None:
        """Neg Case 5: Synthesis is strictly restricted to effective vocabulary; no hidden expansion."""
        sb = SessionBaseline(
            session_id="s_restr",
            selected_gates=("CNOT", "X"),
            baseline_hash="h4",
            source_evolution_stage="GE_1",
            source_vocabulary_hash=self.ge1.vocabulary_hash,
            baseline_mode=BaselineMode.USER_SELECTED,
        )
        comp_res = Stage7CompilerResolver.compile_with_resolution(
            model=self.model_hadamard,
            evolution_state=self.ge1,
            session_baseline=sb,
        )
        self.assertEqual(comp_res.compilation_status, CompilationStatus.INEXPRESSIBLE_UNDER_BASELINE)


if __name__ == "__main__":
    unittest.main()
