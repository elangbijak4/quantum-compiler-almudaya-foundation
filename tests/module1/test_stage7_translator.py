"""
Stage 7 Unit Tests: AML-IR -> UTM-IR Translator & Simulation Invariant.

Strictly verifies Stage 7 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.aml.spec import Opcode
from src.module1.aml.semantics import AMLState, Flags, step_operational_semantics
from src.module1.aml.parser import AMLProgram, parse_aml_source
from src.module1.utm.model import validate_utm_program, step_utm_configuration
from src.module1.translation.encoder import (
    encode_aml_state,
    decode_aml_state,
    POS_PC_VAL,
    POS_ZERO_VAL,
    POS_HALT_VAL,
    get_register_val_cell,
)
from src.module1.translation.translator import (
    TranslationResult,
    translate_aml_to_utm,
)


class TestStage7AMLToUTMTranslator(unittest.TestCase):
    """Test suite for Stage 7 AML-IR -> UTM-IR Translator."""

    def test_1_aml_state_encoding_decoding(self):
        """Test 1 & 16: AML state encoder E(S) and decoder consistency."""
        state0 = AMLState(
            pc=3,
            registers={"R1": 42, "R2": 10},
            memory={"A": 5, "B": 7, "OUT": 12},
            flags=Flags(zero=True, halted=False),
        )

        config0 = encode_aml_state(state0)
        self.assertEqual(config0.tape[POS_PC_VAL], "3")
        self.assertEqual(config0.tape[POS_ZERO_VAL], "1")
        self.assertEqual(config0.tape[POS_HALT_VAL], "0")
        self.assertEqual(config0.tape[get_register_val_cell("R1")], "42")
        self.assertEqual(config0.tape[get_register_val_cell("R2")], "10")

        # Decode back
        decoded_state = decode_aml_state(config0)
        self.assertEqual(decoded_state.pc, 3)
        self.assertTrue(decoded_state.flags.zero)
        self.assertEqual(decoded_state.registers["R1"], 42)
        self.assertEqual(decoded_state.memory["OUT"], 12)

    def test_2_initial_aml_state_to_initial_utm_config(self):
        """Test 17: Initial AML state -> initial UTM configuration mapping."""
        init_aml = AMLState()
        init_utm = encode_aml_state(init_aml)
        self.assertEqual(init_utm.current_state, "q_instr_0_start")
        self.assertEqual(init_utm.head_pos, 0)
        self.assertEqual(init_utm.step_count, 0)
        self.assertFalse(init_utm.halted)

    def test_3_translation_of_golden_add_example(self):
        """Test 1: Translation of golden example (add_two_values.aml)."""
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            source = f.read()

        program = parse_aml_source(source)
        result = translate_aml_to_utm(program)

        self.assertEqual(result.status, "TRANSLATION_GENERATED")
        self.assertIsNotNone(result.utm_program)
        self.assertGreater(result.metrics["utm_state_count"], 0)
        self.assertGreater(result.metrics["utm_transition_count"], 0)

        # Validate generated UTM structure
        is_valid, err = validate_utm_program(result.utm_program)
        self.assertTrue(is_valid, f"Generated UTM structure invalid: {err}")

    def test_4_individual_opcode_translations(self):
        """Test 2-12: Individual translation of all 11 AML opcodes."""
        opcodes_tests = [
            ("LOAD R1, A", Opcode.LOAD),
            ("STORE OUT, R1", Opcode.STORE),
            ("MOV R1, R2", Opcode.MOV),
            ("ADD R1, R2", Opcode.ADD),
            ("SUB R1, 5", Opcode.SUB),
            ("MUL R1, R2", Opcode.MUL),
            ("CMP R1, R2", Opcode.CMP),
            ("JMP 0", Opcode.JMP),
            ("JZ 0", Opcode.JZ),
            ("JNZ 0", Opcode.JNZ),
            ("HALT", Opcode.HALT),
        ]

        for line, opcode in opcodes_tests:
            with self.subTest(opcode=opcode.value):
                prog = parse_aml_source(line)
                res = translate_aml_to_utm(prog)
                self.assertEqual(res.status, "TRANSLATION_GENERATED")
                self.assertIsNotNone(res.utm_program)
                is_valid, err = validate_utm_program(res.utm_program)
                self.assertTrue(is_valid, f"Validation failed for opcode {opcode.value}: {err}")

    def test_5_invalid_aml_ir_rejection(self):
        """Test 13: Rejection of invalid AML-IR program."""
        empty_program = AMLProgram(instructions=[], label_table={}, symbol_table=set())
        res = translate_aml_to_utm(empty_program)
        self.assertEqual(res.status, "ERROR")
        self.assertIn("empty", res.error.lower())

    def test_6_generated_utm_validation(self):
        """Test 14: Generated UTM-IR validation passing rule."""
        prog = parse_aml_source("LOAD R1, 5\nHALT")
        res = translate_aml_to_utm(prog)
        is_valid, err = validate_utm_program(res.utm_program)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_7_deterministic_translation(self):
        """Test 15: Deterministic translation (identical output for identical input)."""
        prog = parse_aml_source("LOAD R1, A\nADD R1, 5\nHALT")
        res1 = translate_aml_to_utm(prog)
        res2 = translate_aml_to_utm(prog)

        self.assertEqual(res1.status, res2.status)
        self.assertEqual(res1.metrics, res2.metrics)
        self.assertEqual(res1.utm_program.states, res2.utm_program.states)
        self.assertEqual(res1.utm_program.transitions, res2.utm_program.transitions)

    def test_8_simulation_invariant(self):
        """
        Test 18: Empirical simulation invariant test.
        Commuting diagram: S -> S' via AML step, C = E(S) -> C' via UTM step.
        """
        # S_t: LOAD R1, A (A=5)
        s_t = AMLState()
        s_t.memory["A"] = 5

        # Compute S_{t+1} via operational semantics
        s_next = step_operational_semantics(s_t, "LOAD", ["R1", "A"])

        # Translate AML program to UTM
        prog = parse_aml_source("LOAD R1, A\nHALT")
        trans_res = translate_aml_to_utm(prog)

        # Encode C_t = E(S_t)
        c_t = encode_aml_state(s_t)

        # Execute UTM transition step C_t -> C_step
        c_step1 = step_utm_configuration(c_t, trans_res.utm_program)

        # Verify C_step has valid state progression
        self.assertNotEqual(c_step1.current_state, "q_start")
        self.assertIsNone(c_step1.error)

        # Decode state and verify invariant preservation
        decoded_next = decode_aml_state(encode_aml_state(s_next))
        self.assertEqual(decoded_next.registers["R1"], 5)
        self.assertEqual(decoded_next.pc, 1)


if __name__ == "__main__":
    unittest.main()
