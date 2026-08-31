"""
Stage 6 Unit Tests: Formal UTM-IR & Configuration Transition Model.

Strictly verifies Stage 6 compliance per main-technical-refference.md.
"""

import unittest
from src.module1.utm.model import (
    Direction,
    TransitionAction,
    UTMProgram,
    UTMConfiguration,
    step_utm_configuration,
    validate_utm_program,
)


class TestStage6UTMIR(unittest.TestCase):
    """Test suite for Stage 6 UTM-IR data structures and configuration transitions."""

    def setUp(self):
        """Build a simple 2-state incrementer UTM program for testing."""
        # Program: Reads '0' -> writes '1', moves RIGHT, goes to q_halt
        self.valid_program = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                ("q1", "_"): TransitionAction("q_halt", "1", Direction.STAY),
            },
        )

    def test_utm_program_validation_positive(self):
        """Test architectural validation of a valid UTMProgram."""
        is_valid, err = validate_utm_program(self.valid_program)
        self.assertTrue(is_valid, f"Validation failed: {err}")

    def test_utm_program_validation_negative(self):
        """Test detection of invalid UTMProgram structures."""
        # 1. Invalid initial state
        prog1 = UTMProgram(initial_state="q_unknown")
        is_valid, err = validate_utm_program(prog1)
        self.assertFalse(is_valid)
        self.assertIn("Initial state", err)

        # 2. Blank symbol not in alphabet
        prog2 = UTMProgram(blank_symbol="#")
        is_valid, err = validate_utm_program(prog2)
        self.assertFalse(is_valid)
        self.assertIn("Blank symbol", err)

        # 3. Transition write symbol not in alphabet
        prog3 = UTMProgram(
            transitions={("q_start", "0"): TransitionAction("q_halt", "X", Direction.STAY)}
        )
        is_valid, err = validate_utm_program(prog3)
        self.assertFalse(is_valid)
        self.assertIn("write symbol", err)

    def test_valid_configuration_single_step_transitions(self):
        """Test valid single-step configuration transitions."""
        # C0: state=q_start, tape[0]='0', head=0
        c0 = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0)
        self.assertEqual(c0.get_tape_symbol(), "0")

        # Step 1: delta(q_start, '0') -> (q1, '1', RIGHT)
        c1 = step_utm_configuration(c0, self.valid_program)
        self.assertEqual(c1.current_state, "q1")
        self.assertEqual(c1.tape[0], "1")
        self.assertEqual(c1.head_pos, 1)
        self.assertEqual(c1.step_count, 1)
        self.assertFalse(c1.halted)
        self.assertIsNone(c1.error)

        # Step 2: delta(q1, '_') -> (q_halt, '1', STAY)
        c2 = step_utm_configuration(c1, self.valid_program)
        self.assertEqual(c2.current_state, "q_halt")
        self.assertEqual(c2.tape[1], "1")
        self.assertEqual(c2.head_pos, 1)
        self.assertEqual(c2.step_count, 2)
        self.assertTrue(c2.halted)
        self.assertIsNone(c2.error)

    def test_head_directions(self):
        """Test head movement directions LEFT, RIGHT, and STAY."""
        # Test LEFT movement
        prog_left = UTMProgram(
            transitions={("q_start", "_"): TransitionAction("q_halt", "1", Direction.LEFT)}
        )
        c0 = UTMConfiguration(head_pos=5)
        c1 = step_utm_configuration(c0, prog_left)
        self.assertEqual(c1.head_pos, 4)
        self.assertTrue(c1.halted)

        # Test STAY movement
        prog_stay = UTMProgram(
            transitions={("q_start", "_"): TransitionAction("q_halt", "1", Direction.STAY)}
        )
        c0_s = UTMConfiguration(head_pos=5)
        c1_s = step_utm_configuration(c0_s, prog_stay)
        self.assertEqual(c1_s.head_pos, 5)
        self.assertTrue(c1_s.halted)

    def test_invalid_configuration_undefined_transition(self):
        """Test handling of undefined transition error."""
        # c0 has symbol '1' at head 0, but valid_program has no rule for (q_start, '1')
        c0 = UTMConfiguration(current_state="q_start", tape={0: "1"}, head_pos=0)
        c1 = step_utm_configuration(c0, self.valid_program)

        self.assertIsNotNone(c1.error)
        self.assertIn("Undefined transition", c1.error)
        self.assertFalse(c1.halted)

    def test_halted_configuration_stepping(self):
        """Test that stepping an already halted configuration returns without state changes."""
        c_halt = UTMConfiguration(current_state="q_halt", halted=True, step_count=10)
        c_next = step_utm_configuration(c_halt, self.valid_program)
        self.assertEqual(c_next.step_count, 10)
        self.assertTrue(c_next.halted)


if __name__ == "__main__":
    unittest.main()
