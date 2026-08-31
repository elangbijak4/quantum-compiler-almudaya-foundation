"""
Unit Tests for Module 2 Stage 3: RUTM Operational Semantics (Repaired & Patched).

Strictly compliant with Stage 3 requirements (main-technical-refference.md & STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md).
"""

import unittest
from src.module1.utm.model import Direction, UTMProgram, TransitionAction, UTMConfiguration, step_utm_configuration
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    create_initial_rutm_configuration,
    project_to_utm,
    valid_rutm_configuration,
)
from src.module2.rutm.semantics import (
    forward_step_rutm,
    reverse_step_rutm,
)


class TestStage3RUTMSemantics(unittest.TestCase):
    """Stage 3 RUTM Operational Semantics Test Suite."""

    def setUp(self):
        """Construct a simple standard test UTM program."""
        # Program:
        # (q_start, '0') -> (q1, '1', RIGHT)
        # (q1, '0') -> (q_halt, '0', STAY)
        self.program = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                ("q1", "0"): TransitionAction("q_halt", "0", Direction.STAY),
            },
        )

    def test_1_valid_forward_transition(self):
        """Test 1: One valid forward transition updates state, tape, head, step_count, and history."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)

        self.assertEqual(c1.current_state, "q1")
        self.assertEqual(c1.tape[0], "1")
        self.assertEqual(c1.head_pos, 1)
        self.assertEqual(c1.step_count, 1)
        self.assertEqual(len(c1.history), 1)
        self.assertFalse(c1.halted)
        self.assertIsNone(c1.error)

    def test_2_tape_symbol_replacement(self):
        """Test 2: Verification of exact symbol write at head position."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.tape[0], "1")

    def test_3_head_movement(self):
        """Test 3: Head movement updates according to direction (RIGHT -> +1)."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.head_pos, 1)

    def test_4_state_transition(self):
        """Test 4: Control state advances from q_start to q1."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.current_state, "q1")

    def test_5_history_record_creation(self):
        """Test 5: Verification that predecessor history record r = (q, s, d) is captured."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)

        rec = c1.history[0]
        self.assertEqual(rec.prev_state, "q_start")
        self.assertEqual(rec.overwritten_symbol, "0")
        self.assertEqual(rec.direction, Direction.RIGHT)

    def test_6_step_count_increment(self):
        """Test 6: Step count increments by 1."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.step_count, 1)

    def test_7_k_equals_len_H_preservation(self):
        """Test 7: Representation invariant k = |H| holds after forward transition."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        c2 = forward_step_rutm(c1, self.program)

        self.assertEqual(c2.step_count, len(c2.history))
        is_valid, err = valid_rutm_configuration(c2)
        self.assertTrue(is_valid, f"Validation failed after 2 steps: {err}")

    def test_8_unaffected_tape_cells_remain_unchanged(self):
        """Test 8: Cells not under head position remain strictly unchanged."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 5: "1", -3: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)

        self.assertEqual(c1.tape[5], "1")
        self.assertEqual(c1.tape[-3], "0")

    def test_9_halt_transition_behavior(self):
        """Test 9: HALT transition sets halted=True and acts as a terminal fixed point on subsequent steps."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        c2 = forward_step_rutm(c1, self.program)  # Hits q_halt

        self.assertEqual(c2.current_state, "q_halt")
        self.assertTrue(c2.halted)

        # Subsequent forward step from halted configuration returns fixed point
        c3 = forward_step_rutm(c2, self.program)
        self.assertEqual(c3.current_state, "q_halt")
        self.assertTrue(c3.halted)
        self.assertEqual(c3.step_count, c2.step_count)
        self.assertEqual(len(c3.history), len(c2.history))

    def test_10_undefined_transition_behavior(self):
        """Test 10: Undefined transition sets error string atomically without mutating tape, head, or history."""
        # Tape has symbol '1' at pos 0, but (q_start, '1') is undefined
        c0 = create_initial_rutm_configuration(tape={0: "1"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)

        self.assertIsNotNone(c1.error)
        self.assertIn("Undefined transition", c1.error)
        self.assertEqual(c1.current_state, "q_start")
        self.assertEqual(c1.head_pos, 0)
        self.assertEqual(c1.step_count, 0)
        self.assertEqual(len(c1.history), 0)
        self.assertEqual(c1.tape, {0: "1"})

    def test_11_invalid_source_configuration(self):
        """Test 11: Invalid input configuration returns error configuration."""
        c_bad = RUTMConfiguration(current_state="")
        c_res = forward_step_rutm(c_bad, self.program)
        self.assertIsNotNone(c_res.error)
        self.assertIn("Invalid configuration", c_res.error)

    def test_12_reverse_operational_behavior(self):
        """Test 12: Reverse operational step restores predecessor configuration."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        c0_restored = reverse_step_rutm(c1)

        self.assertEqual(c0_restored.current_state, c0.current_state)
        self.assertEqual(c0_restored.tape[0], c0.tape[0])
        self.assertEqual(c0_restored.head_pos, c0.head_pos)
        self.assertEqual(c0_restored.step_count, c0.step_count)
        self.assertEqual(len(c0_restored.history), 0)
        self.assertIsNone(c0_restored.error)

    def test_13_history_pop(self):
        """Test 13: History length decreases by 1 on reverse step."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(len(c1.history), 1)

        c0_restored = reverse_step_rutm(c1)
        self.assertEqual(len(c0_restored.history), 0)

    def test_14_step_count_decrement(self):
        """Test 14: Step count decrements by 1 on reverse step."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.step_count, 1)

        c0_restored = reverse_step_rutm(c1)
        self.assertEqual(c0_restored.step_count, 0)

    def test_15_restoration_of_predecessor_state(self):
        """Test 15: Exact restoration of predecessor control state."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        c0_restored = reverse_step_rutm(c1)
        self.assertEqual(c0_restored.current_state, "q_start")

    def test_16_restoration_of_predecessor_tape_symbol(self):
        """Test 16: Exact restoration of overwritten tape symbol."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.tape[0], "1")

        c0_restored = reverse_step_rutm(c1)
        self.assertEqual(c0_restored.tape[0], "0")

    def test_17_restoration_of_predecessor_head_position(self):
        """Test 17: Exact restoration of predecessor head position."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        self.assertEqual(c1.head_pos, 1)

        c0_restored = reverse_step_rutm(c1)
        self.assertEqual(c0_restored.head_pos, 0)

    def test_18_differential_projection_correspondence(self):
        """Test 18: Empirical differential correspondence check pi_UTM(R(C_R)) == step_utm(pi_UTM(C_R))."""
        c0_rutm = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1_rutm = forward_step_rutm(c0_rutm, self.program)
        pi_c1_rutm = project_to_utm(c1_rutm)

        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "0"}, head_pos=0, step_count=0)
        c1_utm = step_utm_configuration(c0_utm, self.program)

        self.assertEqual(pi_c1_rutm.current_state, c1_utm.current_state)
        self.assertEqual(pi_c1_rutm.tape, c1_utm.tape)
        self.assertEqual(pi_c1_rutm.head_pos, c1_utm.head_pos)
        self.assertEqual(pi_c1_rutm.step_count, c1_utm.step_count)
        self.assertEqual(pi_c1_rutm.halted, c1_utm.halted)
        self.assertEqual(pi_c1_rutm.error, c1_utm.error)

    # -------------------------------------------------------------------------
    # Issue A Reverse Validation Tests
    # -------------------------------------------------------------------------

    def test_19_reverse_validation_program_context(self):
        """Test 19: Reverse step with UTMProgram context validates program states and alphabet."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program)
        c0_restored = reverse_step_rutm(c1, program=self.program)

        self.assertEqual(c0_restored.current_state, "q_start")
        self.assertEqual(c0_restored.step_count, 0)
        self.assertIsNone(c0_restored.error)

    def test_20_negative_reverse_invalid_configuration(self):
        """Test 20: Negative test - Malformed configuration (k != |H|) passed to reverse_step_rutm is rejected."""
        r1 = HistoryRecord("q_start", "0", Direction.RIGHT)
        c_bad = RUTMConfiguration(
            current_state="q1",
            tape={0: "1"},
            head_pos=1,
            history=(r1,),
            step_count=5,  # Invalid: step_count != len(history)
            halted=False,
        )
        c_res = reverse_step_rutm(c_bad, program=self.program)
        self.assertIsNotNone(c_res.error)
        self.assertIn("Invalid configuration for reverse step", c_res.error)

    def test_21_negative_reverse_empty_history(self):
        """Test 21: Negative test - Reverse step on initial configuration (k=0, empty history) is rejected."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c_res = reverse_step_rutm(c0, program=self.program)
        self.assertIsNotNone(c_res.error)
        self.assertIn("Cannot reverse initial configuration", c_res.error)


if __name__ == "__main__":
    unittest.main()
