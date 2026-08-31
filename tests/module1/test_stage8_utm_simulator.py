"""
Stage 8 Unit Tests: Universal Turing Machine Simulator.

Strictly verifies Stage 8 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.aml.parser import parse_aml_source
from src.module1.aml.semantics import AMLState
from src.module1.translation.encoder import encode_aml_state, decode_aml_state
from src.module1.translation.translator import translate_aml_to_utm
from src.module1.utm.model import (
    Direction,
    TransitionAction,
    UTMProgram,
    UTMConfiguration,
)
from src.module1.utm.simulator import (
    UTMExecutionResult,
    UTMSimulator,
    simulate_utm,
)


class TestStage8UTMSimulator(unittest.TestCase):
    """Test suite for Stage 8 UTM Simulator."""

    def test_1_single_and_multiple_transitions(self):
        """Test 1-7: Single & multiple sequential transitions, tape read/write, head movement, state change."""
        # Program: q_start -(read 0, write 1, RIGHT)-> q1 -(read _, write 1, LEFT)-> q_halt
        prog = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q_halt", "1", Direction.LEFT),
            },
        )

        c0 = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0)
        res = simulate_utm(prog, c0, enable_trace=True)

        self.assertEqual(res.status, "SUCCESS")
        self.assertTrue(res.halted)
        self.assertEqual(res.step_count, 2)
        self.assertEqual(res.final_configuration.head_pos, 0)
        self.assertEqual(res.final_configuration.tape[0], "1")
        self.assertEqual(res.final_configuration.tape[1], "1")
        self.assertIsNotNone(res.execution_trace)
        self.assertEqual(len(res.execution_trace), 2)

    def test_2_head_left_and_right_movements(self):
        """Test 5-6: Head movement left and right explicit verification."""
        prog = UTMProgram(
            states={"q_start", "q1", "q2", "q_halt"},
            alphabet={"A", "_"},
            transitions={
                ("q_start", "_"): TransitionAction("q1", "A", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q2", "A", Direction.LEFT),
                ("q2", "A"): TransitionAction("q_halt", "A", Direction.STAY),
            },
        )
        c0 = UTMConfiguration(head_pos=10)
        res = simulate_utm(prog, c0)

        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.step_count, 3)
        self.assertEqual(res.final_configuration.head_pos, 10)

    def test_3_halt_detection(self):
        """Test 8: Correct HALT detection."""
        prog = UTMProgram(
            states={"q_start", "q_halt"},
            transitions={("q_start", "_"): TransitionAction("q_halt", "_", Direction.STAY)},
        )
        res = simulate_utm(prog, UTMConfiguration())
        self.assertEqual(res.status, "SUCCESS")
        self.assertTrue(res.halted)

    def test_4_invalid_transition_detection(self):
        """Test 9: Invalid transition detection (INVALID_TRANSITION status)."""
        prog = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "_"},
            transitions={},  # No transitions defined
        )
        c0 = UTMConfiguration(current_state="q_start", tape={0: "0"})
        res = simulate_utm(prog, c0)

        self.assertEqual(res.status, "INVALID_TRANSITION")
        self.assertFalse(res.halted)
        self.assertIsNotNone(res.error)

    def test_5_max_steps_resource_limit(self):
        """Test 10-11: max_steps handling and RESOURCE_LIMIT != HALTED."""
        infinite_prog = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"_"},
            transitions={
                ("q_start", "_"): TransitionAction("q1", "_", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q_start", "_", Direction.LEFT),
            },
        )
        res = simulate_utm(infinite_prog, UTMConfiguration(), max_steps=20)

        self.assertEqual(res.status, "RESOURCE_LIMIT")
        self.assertFalse(res.halted)
        self.assertNotEqual(res.status, "SUCCESS")
        self.assertEqual(res.step_count, 20)

    def test_6_step_counting_and_tape_usage(self):
        """Test 12-13: Step counting and tape usage measurement."""
        prog = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"X", "_"},
            transitions={
                ("q_start", "_"): TransitionAction("q1", "X", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q_halt", "X", Direction.STAY),
            },
        )
        res = simulate_utm(prog, UTMConfiguration())
        self.assertEqual(res.step_count, 2)
        self.assertEqual(res.tape_usage, 2)

    def test_7_deterministic_execution(self):
        """Test 14: Deterministic execution across multiple runs."""
        prog = UTMProgram(
            states={"q_start", "q_halt"},
            transitions={("q_start", "_"): TransitionAction("q_halt", "1", Direction.STAY)},
        )
        res1 = simulate_utm(prog, UTMConfiguration())
        res2 = simulate_utm(prog, UTMConfiguration())

        self.assertEqual(res1.step_count, res2.step_count)
        self.assertEqual(res1.tape_usage, res2.tape_usage)
        self.assertEqual(res1.final_configuration.tape, res2.final_configuration.tape)

    def test_8_golden_poc_utm_execution(self):
        """Test 16-17: Execution of Stage 7 generated UTM for golden PoC without simulator errors."""
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            source = f.read()

        aml_prog = parse_aml_source(source)
        trans_res = translate_aml_to_utm(aml_prog)
        self.assertEqual(trans_res.status, "TRANSLATION_GENERATED")

        # Encode initial state (A=5, B=7)
        init_aml_state = AMLState(memory={"A": 5, "B": 7})
        init_utm_config = encode_aml_state(init_aml_state)

        # Run UTM Simulator
        res = simulate_utm(trans_res.utm_program, init_utm_config, max_steps=1000)

        self.assertEqual(res.status, "SUCCESS")
        self.assertTrue(res.halted)
        self.assertGreater(res.step_count, 0)
        self.assertGreater(res.tape_usage, 0)
        self.assertIsNone(res.error)


if __name__ == "__main__":
    unittest.main()
