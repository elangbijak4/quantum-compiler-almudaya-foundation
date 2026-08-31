"""
Unit Tests for Module 2 Stage 2: RUTM Configuration Model (Repaired & Extended).

Strictly compliant with Stage 2 requirements (main-technical-refference.md & STAGE_2_RUTM_CONFIGURATION.md).
"""

import unittest
from src.module1.utm.model import Direction, UTMConfiguration
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    move_head,
    inverse_move_head,
    push_history,
    pop_history,
    top_history,
    valid_rutm_configuration,
    project_to_utm,
    create_initial_rutm_configuration,
)


class TestStage2RUTMModel(unittest.TestCase):
    """Stage 2 RUTM Configuration Model Test Suite."""

    # -------------------------------------------------------------------------
    # Positive Tests
    # -------------------------------------------------------------------------

    def test_1_valid_initial_configuration(self):
        """Positive Test: Initial configuration C_{R,0} creation and initial invariants."""
        tape = {0: "1", 1: "0"}
        c0 = create_initial_rutm_configuration(tape, initial_state="q_start")
        self.assertEqual(c0.current_state, "q_start")
        self.assertEqual(c0.head_pos, 0)
        self.assertEqual(c0.step_count, 0)
        self.assertEqual(len(c0.history), 0)
        self.assertFalse(c0.halted)
        self.assertIsNone(c0.error)

        is_valid, err = valid_rutm_configuration(c0)
        self.assertTrue(is_valid, f"Initial config validation failed: {err}")

    def test_2_valid_non_empty_history(self):
        """Positive Test: Valid configuration with history tracking."""
        r1 = HistoryRecord("q_start", "_", Direction.RIGHT)
        r2 = HistoryRecord("q1", "0", Direction.LEFT)
        c = RUTMConfiguration(
            current_state="q2",
            tape={0: "1", 1: "1"},
            head_pos=0,
            history=(r1, r2),
            step_count=2,
            halted=False,
            error=None,
        )
        is_valid, err = valid_rutm_configuration(c)
        self.assertTrue(is_valid, f"Valid config with history failed: {err}")

    def test_3_valid_halt_configuration(self):
        """Positive Test: Valid halted configuration."""
        c_halt = RUTMConfiguration(
            current_state="q_halt",
            tape={0: "1"},
            head_pos=0,
            history=(),
            step_count=0,
            halted=True,
            error=None,
        )
        is_valid, err = valid_rutm_configuration(c_halt, halt_state="q_halt")
        self.assertTrue(is_valid, f"Valid halt config failed: {err}")

    def test_4_head_movement_and_inversion(self):
        """Positive Test: Head movement and exact inverse movement identity."""
        for h in [-10, 0, 5]:
            for d in [Direction.LEFT, Direction.RIGHT, Direction.STAY]:
                moved_h = move_head(h, d)
                restored_h = inverse_move_head(moved_h, d)
                self.assertEqual(restored_h, h, f"Failed for h={h}, d={d}")

    def test_5_history_push_pop_top_operations(self):
        """Positive Test: History sequence push, top, and pop operations."""
        h0 = ()
        r1 = HistoryRecord("q_start", "_", Direction.RIGHT)
        r2 = HistoryRecord("q1", "1", Direction.LEFT)

        h1 = push_history(h0, r1)
        self.assertEqual(len(h1), 1)
        self.assertEqual(top_history(h1), r1)

        h2 = push_history(h1, r2)
        self.assertEqual(len(h2), 2)
        self.assertEqual(top_history(h2), r2)

        h_after_pop, popped_r2 = pop_history(h2)
        self.assertEqual(popped_r2, r2)
        self.assertEqual(len(h_after_pop), 1)
        self.assertEqual(top_history(h_after_pop), r1)

    def test_6_extensional_tape_equality(self):
        """Positive Test: Sparse tape symbol retrieval and default blank value."""
        c = RUTMConfiguration(tape={2: "A"})
        self.assertEqual(c.get_tape_symbol(2), "A")
        self.assertEqual(c.get_tape_symbol(0), "_")
        self.assertEqual(c.get_tape_symbol(-5), "_")

    def test_7_utm_projection(self):
        """Positive Test: Canonical projection pi_UTM : C_R -> C_UTM into Module 1's frozen UTMConfiguration."""
        r1 = HistoryRecord("q_start", "_", Direction.RIGHT)
        c_rutm = RUTMConfiguration(
            current_state="q1",
            tape={0: "1", 1: "0"},
            head_pos=1,
            history=(r1,),
            step_count=1,
            halted=False,
            error=None,
        )

        c_utm = project_to_utm(c_rutm)
        self.assertIsInstance(c_utm, UTMConfiguration)
        self.assertEqual(c_utm.current_state, "q1")
        self.assertEqual(c_utm.tape, {0: "1", 1: "0"})
        self.assertEqual(c_utm.head_pos, 1)
        self.assertEqual(c_utm.step_count, 1)
        self.assertFalse(c_utm.halted)
        self.assertIsNone(c_utm.error)

    # -------------------------------------------------------------------------
    # Negative Invariant Verification Tests
    # -------------------------------------------------------------------------

    def test_8_negative_invalid_empty_state(self):
        """Negative Test: Empty or non-string current_state."""
        c1 = RUTMConfiguration(current_state="")
        is_valid, err = valid_rutm_configuration(c1)
        self.assertFalse(is_valid)
        self.assertIn("non-empty string", err)

        c2 = RUTMConfiguration(current_state=123)  # type: ignore
        is_valid, err = valid_rutm_configuration(c2)
        self.assertFalse(is_valid)

    def test_9_negative_state_not_in_program_states(self):
        """Negative Test: State not present in allowed program_states set."""
        c = RUTMConfiguration(current_state="q_unknown")
        is_valid, err = valid_rutm_configuration(c, program_states={"q_start", "q_halt"})
        self.assertFalse(is_valid)
        self.assertIn("not found in program states", err)

    def test_10_negative_non_integer_head(self):
        """Negative Test: Non-integer head position."""
        c1 = RUTMConfiguration(head_pos=1.5)  # type: ignore
        is_valid, err = valid_rutm_configuration(c1)
        self.assertFalse(is_valid)
        self.assertIn("head_pos must be an integer", err)

        c2 = RUTMConfiguration(head_pos=True)  # bool is subclass of int in Python
        is_valid, err = valid_rutm_configuration(c2)
        self.assertFalse(is_valid)

    def test_11_negative_invalid_step_count_type_and_negative(self):
        """Negative Test: Invalid step_count type (str, float, bool) or negative step_count."""
        c_str = RUTMConfiguration(step_count="1")  # type: ignore
        is_valid, err = valid_rutm_configuration(c_str)
        self.assertFalse(is_valid)
        self.assertIn("step_count must be a non-negative integer", err)

        c_bool = RUTMConfiguration(step_count=True)  # type: ignore
        is_valid, err = valid_rutm_configuration(c_bool)
        self.assertFalse(is_valid)

        c_neg = RUTMConfiguration(step_count=-1)
        is_valid, err = valid_rutm_configuration(c_neg)
        self.assertFalse(is_valid)
        self.assertIn("non-negative integer", err)

    def test_12_negative_k_not_equal_len_H(self):
        """Negative Test: Invariant violation k != |H|."""
        r1 = HistoryRecord("q_start", "_", Direction.RIGHT)
        c = RUTMConfiguration(
            history=(r1,),
            step_count=5,  # Mismatch! len(history) == 1
        )
        is_valid, err = valid_rutm_configuration(c)
        self.assertFalse(is_valid)
        self.assertIn("Representation invariant violated", err)

    def test_13_negative_non_boolean_halted(self):
        """Negative Test: Non-boolean halted flag (int, str)."""
        c = RUTMConfiguration(halted=1)  # type: ignore
        is_valid, err = valid_rutm_configuration(c)
        self.assertFalse(is_valid)
        self.assertIn("halted must be a boolean", err)

    def test_14_negative_halted_state_mismatch(self):
        """Negative Test: Halting consistency invariant mismatch (state vs halted flag)."""
        # Mismatch 1: q_halt state but halted=False
        c1 = RUTMConfiguration(current_state="q_halt", halted=False)
        is_valid, err = valid_rutm_configuration(c1, halt_state="q_halt")
        self.assertFalse(is_valid)
        self.assertIn("Halting consistency invariant violated", err)

        # Mismatch 2: q_start state but halted=True
        c2 = RUTMConfiguration(current_state="q_start", halted=True)
        is_valid, err = valid_rutm_configuration(c2, halt_state="q_halt")
        self.assertFalse(is_valid)
        self.assertIn("Halting consistency invariant violated", err)

    def test_15_negative_invalid_error_type(self):
        """Negative Test: Invalid error type (int, dict, list)."""
        c = RUTMConfiguration(error=123)  # type: ignore
        is_valid, err = valid_rutm_configuration(c)
        self.assertFalse(is_valid)
        self.assertIn("error must be None or a string", err)

    def test_16_negative_invalid_tape_symbols_and_keys(self):
        """Negative Test: Non-integer tape keys or invalid tape symbols."""
        c_key = RUTMConfiguration(tape={"0": "1"})  # type: ignore
        is_valid, err = valid_rutm_configuration(c_key)
        self.assertFalse(is_valid)
        self.assertIn("Tape key '0' must be an integer", err)

        c_val = RUTMConfiguration(tape={0: 123})  # type: ignore
        is_valid, err = valid_rutm_configuration(c_val)
        self.assertFalse(is_valid)
        self.assertIn("Tape value at cell 0 must be a string", err)

        c_alpha = RUTMConfiguration(tape={0: "X"})
        is_valid, err = valid_rutm_configuration(c_alpha, program_alphabet={"0", "1", "_"})
        self.assertFalse(is_valid)
        self.assertIn("Tape symbol 'X' at cell 0 not in program alphabet", err)

    def test_17_negative_malformed_history_items(self):
        """Negative Test: History containing malformed items or non-HistoryRecord objects."""
        c_item = RUTMConfiguration(history=("invalid_item",), step_count=1)  # type: ignore
        is_valid, err = valid_rutm_configuration(c_item)
        self.assertFalse(is_valid)
        self.assertIn("is not a HistoryRecord instance", err)

    def test_18_negative_invalid_history_record_fields(self):
        """Negative Test: HistoryRecord with invalid prev_state, overwritten_symbol, or direction."""
        # Empty prev_state
        r_state = HistoryRecord(prev_state="", overwritten_symbol="0", direction=Direction.RIGHT)
        c1 = RUTMConfiguration(history=(r_state,), step_count=1)
        is_valid, err = valid_rutm_configuration(c1)
        self.assertFalse(is_valid)
        self.assertIn("prev_state must be a non-empty string", err)

        # Symbol not in alphabet
        r_sym = HistoryRecord(prev_state="q_start", overwritten_symbol="X", direction=Direction.RIGHT)
        c2 = RUTMConfiguration(history=(r_sym,), step_count=1)
        is_valid, err = valid_rutm_configuration(c2, program_alphabet={"0", "1", "_"})
        self.assertFalse(is_valid)
        self.assertIn("History record 0 symbol 'X' not in program alphabet", err)

        # Invalid direction
        r_dir = HistoryRecord(prev_state="q_start", overwritten_symbol="0", direction="RIGHT")  # type: ignore
        c3 = RUTMConfiguration(history=(r_dir,), step_count=1)
        is_valid, err = valid_rutm_configuration(c3)
        self.assertFalse(is_valid)
        self.assertIn("direction must be a valid Direction enum", err)


if __name__ == "__main__":
    unittest.main()
