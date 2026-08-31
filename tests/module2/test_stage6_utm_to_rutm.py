"""
Unit Tests for Module 2 Stage 6: UTM-IR -> RUTM-IR Translator & Golden PoC.

Strictly compliant with Stage 6 requirements (main-technical-refference.md & STAGE_6_UTM_TO_RUTM_TRANSLATION.md).
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram, UTMConfiguration, step_utm_configuration
from src.module2.rutm.model import project_to_utm
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module2.rutm_ir.validator import validate_rutm_ir
from src.module2.rutm_ir.serialization import serialize_rutm_ir
from src.module2.translation.utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm


class TestStage6UTMToRUTM(unittest.TestCase):
    """Stage 6 UTM-IR -> RUTM-IR Translator Test Suite."""

    def setUp(self):
        """Construct standard source UTMProgram instances for testing."""
        # Program A: 3-step trace with L, R, S directions
        self.utm_program_a = UTMProgram(
            states={"q_start", "q1", "q2", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q2", "0", Direction.LEFT),
                ("q2", "1"): TransitionAction("q_halt", "1", Direction.STAY),
            },
        )

    def test_1_valid_utm_ir_translates_successfully(self):
        """Test 1: Valid UTMProgram translates with success=True."""
        res = translate_utm_to_rutm(self.utm_program_a, machine_name="MachineA")
        self.assertTrue(res.success)
        self.assertIsNotNone(res.target_ir)
        self.assertEqual(res.errors, ())

    def test_2_generated_rutm_ir_validates(self):
        """Test 2: Generated RUTM_IR passes validate_rutm_ir()."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertTrue(res.success)
        is_valid, err = validate_rutm_ir(res.target_ir)
        self.assertTrue(is_valid, f"Generated RUTM_IR failed validation: {err}")

    def test_3_states_are_preserved(self):
        """Test 3: Target states match source states set."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.states, frozenset(self.utm_program_a.states))

    def test_4_input_alphabet_is_preserved(self):
        """Test 4: Input alphabet is correctly derived from non-blank symbols."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.input_alphabet, frozenset({"0", "1"}))

    def test_5_tape_alphabet_is_preserved(self):
        """Test 5: Tape alphabet matches source alphabet."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.tape_alphabet, frozenset(self.utm_program_a.alphabet))

    def test_6_blank_symbol_is_preserved(self):
        """Test 6: Blank symbol matches source blank symbol."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.blank_symbol, self.utm_program_a.blank_symbol)

    def test_7_initial_state_is_preserved(self):
        """Test 7: Initial state matches source initial state."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.initial_state, self.utm_program_a.initial_state)

    def test_8_halt_state_is_preserved(self):
        """Test 8: Halt state matches source halt state."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.halt_state, self.utm_program_a.halt_state)

    def test_9_transition_count_is_preserved(self):
        """Test 9: Transition table length matches source transition count."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(len(res.target_ir.transitions), len(self.utm_program_a.transitions))

    def test_10_transition_actions_are_preserved(self):
        """Test 10: Transition rules map identically."""
        res = translate_utm_to_rutm(self.utm_program_a)
        self.assertEqual(res.target_ir.transitions, self.utm_program_a.transitions)

    def test_11_history_policy_is_correctly_attached(self):
        """Test 11: History policy metadata matches Stage 4 proven model."""
        res = translate_utm_to_rutm(self.utm_program_a)
        hp = res.target_ir.history_policy
        self.assertTrue(hp.enabled)
        self.assertEqual(hp.record_schema, ("prev_state", "overwritten_symbol", "direction"))
        self.assertEqual(hp.inverse_policy, "LIFO_stack")

    def test_12_provenance_is_correct(self):
        """Test 12: Provenance metadata correctly identifies Stage 6 translation."""
        res = translate_utm_to_rutm(self.utm_program_a)
        prov = res.target_ir.provenance
        self.assertEqual(prov.source_model, "UTM-IR")
        self.assertEqual(prov.source_stage, "Stage 6")
        self.assertEqual(prov.proof_reference, "docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md")

    def test_13_translation_is_deterministic(self):
        """Test 13: Translating identical source produces identical canonical JSON serialization."""
        res1 = translate_utm_to_rutm(self.utm_program_a, machine_name="FixedName")
        res2 = translate_utm_to_rutm(self.utm_program_a, machine_name="FixedName")

        s1 = serialize_rutm_ir(res1.target_ir)
        s2 = serialize_rutm_ir(res2.target_ir)
        self.assertEqual(s1, s2)

    def test_14_invalid_source_utm_ir_is_rejected(self):
        """Test 14: Invalid source UTMProgram returns TranslationResult(success=False)."""
        bad_program = UTMProgram(states=set())  # Empty states
        res = translate_utm_to_rutm(bad_program)
        self.assertFalse(res.success)
        self.assertIsNone(res.target_ir)
        self.assertIn("Invalid source UTMProgram", res.errors[0])

    def test_15_translated_initial_configuration_is_valid(self):
        """Test 15: Initial mapped configuration E_UR(C_U,0) is valid."""
        res = translate_utm_to_rutm(self.utm_program_a)
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, step_count=0)
        c0_rutm = map_utm_configuration_to_rutm(c0_utm, res.target_ir)

        self.assertEqual(c0_rutm.current_state, "q_start")
        self.assertEqual(c0_rutm.tape, {0: "0"})
        self.assertEqual(c0_rutm.head_pos, 0)
        self.assertEqual(c0_rutm.step_count, 0)
        self.assertEqual(c0_rutm.history, ())
        self.assertFalse(c0_rutm.halted)

    def test_16_one_step_projected_behavior_matches_source_utm(self):
        """Test 16: pi_UTM(R(C_R, T_UR(U))) == step_utm(C_U, U)."""
        res = translate_utm_to_rutm(self.utm_program_a)
        target_program = res.target_ir.to_utm_program()

        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, step_count=0)
        c0_rutm = map_utm_configuration_to_rutm(c0_utm, res.target_ir)

        c1_utm = step_utm_configuration(c0_utm, self.utm_program_a)
        c1_rutm = forward_step_rutm(c0_rutm, target_program)
        pi_c1_rutm = project_to_utm(c1_rutm)

        self.assertEqual(pi_c1_rutm, c1_utm)

    def test_17_multi_step_projected_behavior_matches_source_utm(self):
        """Test 17: Multi-step trace projected matching across 3 computational steps."""
        res = translate_utm_to_rutm(self.utm_program_a)
        target_program = res.target_ir.to_utm_program()

        c_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        c_rutm = map_utm_configuration_to_rutm(c_utm, res.target_ir)

        for step_idx in range(3):
            c_utm = step_utm_configuration(c_utm, self.utm_program_a)
            c_rutm = forward_step_rutm(c_rutm, target_program)
            self.assertEqual(project_to_utm(c_rutm), c_utm)

    def test_18_halt_behavior_corresponds(self):
        """Test 18: Reaching q_halt in target RUTM execution sets halted=True matching source UTM."""
        res = translate_utm_to_rutm(self.utm_program_a)
        target_program = res.target_ir.to_utm_program()

        c_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        c_rutm = map_utm_configuration_to_rutm(c_utm, res.target_ir)

        # Run 3 steps to reach q_halt
        for _ in range(3):
            c_utm = step_utm_configuration(c_utm, self.utm_program_a)
            c_rutm = forward_step_rutm(c_rutm, target_program)

        self.assertTrue(c_utm.halted)
        self.assertTrue(c_rutm.halted)
        self.assertEqual(c_rutm.current_state, "q_halt")

    def test_19_forward_then_reverse_restores_target_configuration(self):
        """Test 19: R^{-1}(R(C_R, T_UR(U))) == C_R for translated machine."""
        res = translate_utm_to_rutm(self.utm_program_a)
        target_program = res.target_ir.to_utm_program()

        c0_rutm = map_utm_configuration_to_rutm(
            UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, step_count=0),
            res.target_ir,
        )
        c1_rutm = forward_step_rutm(c0_rutm, target_program)
        c0_restored = reverse_step_rutm(c1_rutm, program=target_program)

        self.assertEqual(c0_restored, c0_rutm)

    def test_20_golden_poc_pipeline_differential_execution(self):
        """
        Test 20: Golden PoC Pipeline Differential Execution Check.
        Translates a multi-step deterministic program, executes 3 forward steps,
        verifies projected UTM correspondence at every step, then reverses 3 steps
        to perfectly restore the exact initial configuration C_{R,0}.
        """
        res = translate_utm_to_rutm(self.utm_program_a, machine_name="GoldenPoC_RUTM")
        self.assertTrue(res.success)
        self.assertGreater(res.metrics["target_transition_count"], 0)

        target_program = res.target_ir.to_utm_program()

        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        c0_rutm = map_utm_configuration_to_rutm(c0_utm, res.target_ir)

        # Forward trace execution
        c1_rutm = forward_step_rutm(c0_rutm, target_program)
        c1_utm = step_utm_configuration(c0_utm, self.utm_program_a)
        self.assertEqual(project_to_utm(c1_rutm), c1_utm)

        c2_rutm = forward_step_rutm(c1_rutm, target_program)
        c2_utm = step_utm_configuration(c1_utm, self.utm_program_a)
        self.assertEqual(project_to_utm(c2_rutm), c2_utm)

        c3_rutm = forward_step_rutm(c2_rutm, target_program)
        c3_utm = step_utm_configuration(c2_utm, self.utm_program_a)
        self.assertEqual(project_to_utm(c3_rutm), c3_utm)

        # Reverse trace execution back to C0
        c2_rev = reverse_step_rutm(c3_rutm, program=target_program)
        self.assertEqual(c2_rev, c2_rutm)

        c1_rev = reverse_step_rutm(c2_rev, program=target_program)
        self.assertEqual(c1_rev, c1_rutm)

        c0_rev = reverse_step_rutm(c1_rev, program=target_program)
        self.assertEqual(c0_rev, c0_rutm)


if __name__ == "__main__":
    unittest.main()
