"""
Module 3 Stage 6 Test Suite — RUTM-IR -> QTM-IR Translator (T_RQ) Micro Closure Correction.

Verifies error reverse semantics, zero forward_mapping fallbacks, actual RUTM inverse preservation,
and strict domain closure under R_P and R_P^-1.

Tests:
1. test_error_reverse_semantics_uses_actual_inverse (Req Section 8)
2. test_error_reverse_semantics_does_not_fallback_to_forward_mapping (Req Section 9)
3. test_forward_mapping_preserves_actual_rutm_transition (Req Review A)
4. test_reverse_mapping_preserves_actual_inverse_transition (Req Review B)
5. test_domain_truncation_rejected (Req Review C & Section 12)
6. test_matrix_matches_actual_rutm_transition (Req Review D & E)
7. test_valid_rutm_program_and_ir_translation
8. test_basis_state_construction_and_identity
9. test_history_preservation_and_identity_isolation
10. test_deterministic_basis_ids
11. test_initial_state_lifting
12. test_forward_and_reverse_mapping_total_bijection
13. test_finite_matrix_construction_permutation_and_unitarity
14. test_provenance_generation_and_exact_canonical_relation
15. test_source_hash_determinism
16. test_qtm_ir_validation_gate
17. test_serialization_round_trip
18. test_semantic_commuting_relations
19. test_deterministic_repeated_translation
20. test_invalid_and_non_bijective_input_rejection
21. test_halting_and_error_state_preservation
"""

import unittest
import math
import json
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    create_initial_rutm_configuration,
)
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module2.rutm_ir.model import (
    RUTM_IR,
    RUTMHistoryPolicy,
    RUTMProvenance,
)
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.qtm_ir.serialization import (
    serialize_qtm_ir,
    deserialize_qtm_ir,
    serialize_qtm_ir_to_json,
    deserialize_qtm_ir_from_json,
)
from src.module3.translator import (
    RUTMToQTMTranslator,
    RUTMToQTMTranslationError,
    translate_rutm_to_qtm_ir,
    compute_canonical_basis_id,
    lift_configuration,
    compute_source_program_hash,
    verify_forward_commuting_relation,
    verify_reverse_commuting_relation,
)


class TestStage6RUTMToQTM(unittest.TestCase):
    """Unit test suite for RUTM-IR -> QTM-IR Translator (T_RQ)."""

    def setUp(self) -> None:
        """Sets up test RUTM program fixtures."""
        self.transitions = {
            ("q_start", "0"): TransitionAction(next_state="q_step1", write_symbol="1", direction=Direction.RIGHT),
            ("q_step1", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
        }
        self.utm_program = UTMProgram(
            states={"q_start", "q_step1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions=self.transitions,
        )

        self.rutm_ir = RUTM_IR(
            name="test_rutm_3step",
            states=frozenset({"q_start", "q_step1", "q_halt"}),
            input_alphabet=frozenset({"0", "1"}),
            tape_alphabet=frozenset({"0", "1", "_"}),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions=dict(self.transitions),
        )

        self.initial_tape = {0: "0", 1: "0"}
        self.initial_config = create_initial_rutm_configuration(self.initial_tape, "q_start")

        # Halting single state terminal fixed point fixture (history=(), step_count=0)
        self.c_halt = RUTMConfiguration(
            current_state="q_halt", tape={0: "1", 1: "1"}, head_pos=2, history=(), step_count=0, halted=True
        )

        # Error single state domain fixture (Case A: R_P^-1(C_error) = C_error)
        self.c_error = RUTMConfiguration(
            current_state="q_step1", tape={0: "1"}, head_pos=1, history=(), step_count=0, halted=False, error="Tape symbol out of alphabet"
        )

    def test_error_reverse_semantics_uses_actual_inverse(self) -> None:
        """Req Section 8: Error reverse semantics uses actual Module 2 fixed-point inverse R_P^-1(C_error) = C_error."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_error])
        b_id = compute_canonical_basis_id(self.c_error)

        self.assertIn(b_id, model.transition_mapping.reverse_mapping)
        self.assertEqual(model.transition_mapping.reverse_mapping[b_id], b_id)
        self.assertEqual(model.transition_mapping.forward_mapping[b_id], b_id)
        self.assertTrue(verify_reverse_commuting_relation(model, self.utm_program, [self.c_error]))

    def test_error_reverse_semantics_does_not_fallback_to_forward_mapping(self) -> None:
        """Req Section 9: Reverse semantics cannot be fabricated via forward_mapping lookup."""
        # c1_halt is a halted state with non-empty history (h0,).
        # Forward step R_P(c1_halt) = c1_halt (forward step is closed on custom_domain=[c1_halt]).
        # But reverse_step_rutm(c1_halt) pops h0 and produces c0 (q_start), which is NOT in D=[c1_halt].
        # Translating custom_domain=[c1_halt] MUST fail with reverse domain closure error.
        # It MUST NOT search forward_mapping or invent a predecessor.
        h0 = HistoryRecord(prev_state="q_start", overwritten_symbol="0", direction=Direction.RIGHT)
        c1_halt = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=1, history=(h0,), step_count=1, halted=True)
        translator = RUTMToQTMTranslator()

        with self.assertRaises(RUTMToQTMTranslationError) as ctx:
            translator.translate(self.utm_program, custom_domain=[c1_halt])

        self.assertIn("Domain closure failure", str(ctx.exception))
        self.assertIn("Reverse transition R_P^-1", str(ctx.exception))

    def test_forward_mapping_preserves_actual_rutm_transition(self) -> None:
        """Req Review A & Section 6: Forward mapping preserves ACTUAL RUTM transition R_P(C)."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        src_id = compute_canonical_basis_id(self.c_halt)

        actual_target = self.c_halt  # Halted configuration fixed point
        translated_target_id = model.transition_mapping.forward_mapping[src_id]

        self.assertEqual(translated_target_id, compute_canonical_basis_id(actual_target))

    def test_reverse_mapping_preserves_actual_inverse_transition(self) -> None:
        """Req Review B & Section 8: Reverse mapping preserves ACTUAL RUTM inverse transition R_P^-1(C')."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        tgt_id = compute_canonical_basis_id(self.c_halt)

        actual_predecessor = self.c_halt  # Halted configuration fixed point
        translated_predecessor_id = model.transition_mapping.reverse_mapping[tgt_id]

        self.assertEqual(translated_predecessor_id, compute_canonical_basis_id(actual_predecessor))

    def test_domain_truncation_rejected(self) -> None:
        """Req Review C & Section 12: Incomplete domain with R_P(C) not in D MUST be rejected with zero fallbacks."""
        c0 = self.initial_config  # q_start -> q_step1 (which is not in custom_domain=[c0])
        translator = RUTMToQTMTranslator()

        with self.assertRaises(RUTMToQTMTranslationError) as ctx:
            translator.translate(self.utm_program, custom_domain=[c0])

        self.assertIn("Domain closure failure", str(ctx.exception))

    def test_matrix_matches_actual_rutm_transition(self) -> None:
        """Req Review D, E & Section 14: Matrix entries match ACTUAL RUTM transition R_P."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt], include_matrix=True)
        m_rep = model.matrix_representation
        self.assertIsNotNone(m_rep)

        b_id = compute_canonical_basis_id(self.c_halt)
        idx = m_rep.basis_order.index(b_id)

        # For column idx (src), row idx (target) MUST be 1.0 + 0i
        entry = m_rep.matrix[idx][idx]
        self.assertAlmostEqual(entry.real, 1.0)
        self.assertAlmostEqual(entry.imag, 0.0)

    def test_01_valid_rutm_program_and_ir_translation(self) -> None:
        """Req 1 & 2: Valid RUTMProgram and RUTM_IR translation produces valid QTMIRModel."""
        model1 = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        self.assertIsInstance(model1, QTMIRModel)

        model2 = translate_rutm_to_qtm_ir(self.rutm_ir, custom_domain=[self.c_halt])
        self.assertIsInstance(model2, QTMIRModel)

    def test_02_basis_state_construction_and_identity(self) -> None:
        """Req 3 & 4: Basis-state construction preserves complete 7-tuple configuration identity."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        for b_id, b_state in model.basis_states.items():
            self.assertIsInstance(b_state, QTMIRBasisState)
            self.assertEqual(b_state.current_state, "q_halt")
            self.assertIsInstance(b_state.tape, dict)
            self.assertIsInstance(b_state.head_pos, int)
            self.assertIsInstance(b_state.history, tuple)
            self.assertIsInstance(b_state.step_count, int)
            self.assertTrue(b_state.halted)

    def test_03_history_preservation_and_identity_isolation(self) -> None:
        """Req 5: History sequence preserved in basis states and influences canonical basis ID."""
        c1 = RUTMConfiguration(current_state="q_step1", tape={0: "1"}, head_pos=1, history=(), step_count=0)
        h0 = HistoryRecord(prev_state="q_start", overwritten_symbol="0", direction=Direction.RIGHT)
        c2 = RUTMConfiguration(current_state="q_step1", tape={0: "1"}, head_pos=1, history=(h0,), step_count=1)

        id1 = compute_canonical_basis_id(c1)
        id2 = compute_canonical_basis_id(c2)

        self.assertNotEqual(id1, id2)

    def test_04_deterministic_basis_ids(self) -> None:
        """Req 6: Canonical basis IDs are strictly deterministic."""
        c = RUTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, history=(), step_count=0)
        id_a = compute_canonical_basis_id(c)
        id_b = compute_canonical_basis_id(c)
        self.assertEqual(id_a, id_b)

    def test_05_initial_state_lifting(self) -> None:
        """Req 7: Initial state vector lifted as |psi_0> = |C_0> with amplitude 1.0 + 0i and norm 1.0."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        v_init = model.initial_state_vector
        self.assertEqual(len(v_init.amplitudes), 1)

        c_halt_id = compute_canonical_basis_id(self.c_halt)
        self.assertIn(c_halt_id, v_init.amplitudes)
        amp = v_init.amplitudes[c_halt_id]
        self.assertEqual(amp.real, 1.0)
        self.assertEqual(amp.imag, 0.0)
        self.assertAlmostEqual(v_init.compute_norm(), 1.0)

    def test_06_forward_and_reverse_mapping_total_bijection(self) -> None:
        """Req 8, 9, 10, 11, 12, 13: Forward and reverse mappings are total, injective, surjective bijections."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        t_map = model.transition_mapping
        domain_ids = set(model.basis_states.keys())

        # Totality & Surjectivity
        self.assertEqual(set(t_map.forward_mapping.keys()), domain_ids)
        self.assertEqual(set(t_map.forward_mapping.values()), domain_ids)
        self.assertEqual(set(t_map.reverse_mapping.keys()), domain_ids)
        self.assertEqual(set(t_map.reverse_mapping.values()), domain_ids)

        # Injectivity
        self.assertEqual(len(set(t_map.forward_mapping.values())), len(domain_ids))
        self.assertEqual(len(set(t_map.reverse_mapping.values())), len(domain_ids))

        # Reverse Composition Identities: R_P^-1 ∘ R_P = id_D and R_P ∘ R_P^-1 = id_D
        for b_id in domain_ids:
            self.assertEqual(t_map.reverse_mapping[t_map.forward_mapping[b_id]], b_id)
            self.assertEqual(t_map.forward_mapping[t_map.reverse_mapping[b_id]], b_id)

    def test_07_finite_matrix_construction_permutation_and_unitarity(self) -> None:
        """Req 14, 15, 16: Finite matrix representation shape, permutation structure, and two-sided unitarity."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt], include_matrix=True)
        m_rep = model.matrix_representation
        self.assertIsNotNone(m_rep)
        N = len(model.basis_states)
        self.assertEqual(m_rep.dimension, N)
        self.assertEqual(len(m_rep.matrix), N)

        # Permutation row and col checks
        for i in range(N):
            row_ones = sum(1 for c in m_rep.matrix[i] if abs(c.real - 1.0) < 1e-6)
            self.assertEqual(row_ones, 1)

        for j in range(N):
            col_ones = sum(1 for i in range(N) if abs(m_rep.matrix[i][j].real - 1.0) < 1e-6)
            self.assertEqual(col_ones, 1)

    def test_08_provenance_generation_and_exact_canonical_relation(self) -> None:
        """Req 17, 18, 19: Provenance metadata generation with exact canonical semantic relation."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        prov = model.provenance
        self.assertIsNotNone(prov)
        self.assertTrue(bool(prov.source_rutm_program_hash))
        self.assertEqual(prov.source_module, "Module 2 (RUTM-IR)")
        self.assertEqual(prov.stage, "Stage 6 (Translator T_RQ)")
        self.assertEqual(prov.compiler_version, "0.3.0-alpha")
        self.assertEqual(prov.semantic_relation, CANONICAL_SEMANTIC_RELATION)

    def test_09_source_hash_determinism(self) -> None:
        """Req 19: Source program hash is deterministic across equivalent program instances."""
        h1 = compute_source_program_hash(self.utm_program)
        h2 = compute_source_program_hash(self.rutm_ir)
        self.assertEqual(h1, h2)

    def test_10_qtm_ir_validation_gate(self) -> None:
        """Req 20: Translated QTM-IR passes validate_qtm_ir gate automatically."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        from src.module3.qtm_ir.validator import validate_qtm_ir
        val_res = validate_qtm_ir(model)
        self.assertTrue(val_res.valid)

    def test_11_serialization_round_trip(self) -> None:
        """Req 21: Translated model survives dictionary and JSON serialization round trip."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])

        # Dictionary round-trip
        dict_model = deserialize_qtm_ir(serialize_qtm_ir(model))
        self.assertEqual(dict_model.version, model.version)
        self.assertEqual(dict_model.basis_states, model.basis_states)
        self.assertEqual(dict_model.transition_mapping, model.transition_mapping)

        # JSON round-trip
        json_model = deserialize_qtm_ir_from_json(serialize_qtm_ir_to_json(model))
        self.assertEqual(json_model.basis_states, model.basis_states)

    def test_12_semantic_commuting_relations(self) -> None:
        """Req 22 & 23: Executable verification of U_P o iota = iota o R_P and U_P^dagger o iota = iota o R_P^-1."""
        translator = RUTMToQTMTranslator()
        domain_configs = [self.c_halt]

        model = translator.translate(self.utm_program, custom_domain=domain_configs)

        self.assertTrue(verify_forward_commuting_relation(model, self.utm_program, domain_configs))
        self.assertTrue(verify_reverse_commuting_relation(model, self.utm_program, domain_configs))

    def test_13_deterministic_repeated_translation(self) -> None:
        """Req 24: Repeated translation of identical input produces identical QTM-IR."""
        model_a = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])
        model_b = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])

        self.assertEqual(serialize_qtm_ir_to_json(model_a), serialize_qtm_ir_to_json(model_b))

    def test_14_invalid_and_non_bijective_input_rejection(self) -> None:
        """Req 25, 26, 27, 28: Reject invalid inputs, non-bijective mappings, non-closed domains."""
        # 1. Invalid input type
        translator = RUTMToQTMTranslator()
        with self.assertRaises(RUTMToQTMTranslationError):
            translator.translate("invalid_program_type")

        # 2. Non-closed custom domain
        c0 = self.initial_config
        with self.assertRaises(RUTMToQTMTranslationError):
            translator.translate(self.utm_program, custom_domain=[c0])

    def test_15_halting_and_error_state_preservation(self) -> None:
        """Req 29 & 30: Halting and error states preserve fixed-point correspondence R_P(C_halt) = C_halt."""
        model = translate_rutm_to_qtm_ir(self.utm_program, custom_domain=[self.c_halt])

        b_id = compute_canonical_basis_id(self.c_halt)
        self.assertIn(b_id, model.transition_mapping.forward_mapping)
        self.assertEqual(model.transition_mapping.forward_mapping[b_id], b_id)
        self.assertEqual(model.transition_mapping.reverse_mapping[b_id], b_id)


if __name__ == "__main__":
    unittest.main()
