"""
Empirical Proof Verification & Boundary Test Suite for Stage 4: Formal RUTM Reversibility.

Strictly compliant with Stage 4 requirements (main-technical-refference.md & STAGE_4_RUTM_REVERSIBILITY_PROOF.md).
Empirically verifies Theorem 1 (Single-Step Reversibility), Theorem 2 (Finite-Trace Reversibility),
and Theorem 3 (Projection Preservation / Commuting Diagram).
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


class TestStage4Reversibility(unittest.TestCase):
    """Stage 4 RUTM Reversibility Proof Verification Test Suite."""

    def setUp(self):
        """Construct multi-step test UTM programs covering L, R, S movements and blank restoration."""
        # Program A: 3-step trace with L, R, S directions
        # (q_start, '0') -> (q1, '1', RIGHT)
        # (q1, '_') -> (q2, '0', LEFT)
        # (q2, '1') -> (q_halt, '1', STAY)
        self.program_a = UTMProgram(
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

    # -------------------------------------------------------------------------
    # Theorem 1: Single-Step Component-Wise Reversibility Tests
    # -------------------------------------------------------------------------

    def test_1_single_step_reversibility_exact(self):
        """Test 1: Theorem 1 verification - forward then reverse returns exact configuration."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        c0_restored = reverse_step_rutm(c1, program=self.program_a)

        self.assertEqual(c0_restored, c0)

    def test_2_tape_restoration(self):
        """Test 2: Lemma 3 verification - exact extensional tape restoration."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "_", 5: "1"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        c0_restored = reverse_step_rutm(c1, program=self.program_a)

        self.assertEqual(c0_restored.tape, c0.tape)

    def test_3_head_restoration(self):
        """Test 3: Lemma 1 verification - exact head position restoration."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        self.assertEqual(c1.head_pos, 1)

        c0_restored = reverse_step_rutm(c1, program=self.program_a)
        self.assertEqual(c0_restored.head_pos, 0)

    def test_4_state_restoration(self):
        """Test 4: State restoration lemma verification."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        self.assertEqual(c1.current_state, "q1")

        c0_restored = reverse_step_rutm(c1, program=self.program_a)
        self.assertEqual(c0_restored.current_state, "q_start")

    def test_5_history_restoration(self):
        """Test 5: Lemma 2 verification - exact history sequence restoration."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        self.assertEqual(len(c1.history), 1)

        c0_restored = reverse_step_rutm(c1, program=self.program_a)
        self.assertEqual(c0_restored.history, ())

    def test_6_step_count_restoration(self):
        """Test 6: Lemma 4 verification - exact step counter restoration."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        self.assertEqual(c1.step_count, 1)

        c0_restored = reverse_step_rutm(c1, program=self.program_a)
        self.assertEqual(c0_restored.step_count, 0)

    def test_7_halted_restoration(self):
        """Test 7: Lemma 5 verification - exact halted flag restoration."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        c0_restored = reverse_step_rutm(c1, program=self.program_a)

        self.assertFalse(c0_restored.halted)

    def test_8_error_restoration(self):
        """Test 8: Lemma 5 verification - error state remains None on valid reverse step."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)
        c0_restored = reverse_step_rutm(c1, program=self.program_a)

        self.assertIsNone(c0_restored.error)

    # -------------------------------------------------------------------------
    # Direction Case Inversion Tests (Lemma 1)
    # -------------------------------------------------------------------------

    def test_9_direction_left_inversion(self):
        """Test 9: Head movement inversion for LEFT direction."""
        p_left = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={("q_start", "0"): TransitionAction("q1", "1", Direction.LEFT)},
        )
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, p_left)
        self.assertEqual(c1.head_pos, -1)

        c0_restored = reverse_step_rutm(c1, program=p_left)
        self.assertEqual(c0_restored.head_pos, 0)
        self.assertEqual(c0_restored, c0)

    def test_10_direction_right_inversion(self):
        """Test 10: Head movement inversion for RIGHT direction."""
        p_right = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT)},
        )
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, p_right)
        self.assertEqual(c1.head_pos, 1)

        c0_restored = reverse_step_rutm(c1, program=p_right)
        self.assertEqual(c0_restored.head_pos, 0)
        self.assertEqual(c0_restored, c0)

    def test_11_direction_stay_inversion(self):
        """Test 11: Head movement inversion for STAY direction."""
        p_stay = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={("q_start", "0"): TransitionAction("q1", "1", Direction.STAY)},
        )
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, p_stay)
        self.assertEqual(c1.head_pos, 0)

        c0_restored = reverse_step_rutm(c1, program=p_stay)
        self.assertEqual(c0_restored.head_pos, 0)
        self.assertEqual(c0_restored, c0)

    def test_12_blank_symbol_restoration(self):
        """Test 12: Blank symbol restoration ('_' overwritten by non-blank)."""
        p_blank = UTMProgram(
            states={"q_start", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={("q_start", "_"): TransitionAction("q1", "1", Direction.RIGHT)},
        )
        c0 = create_initial_rutm_configuration(tape={0: "_"}, initial_state="q_start")
        self.assertEqual(c0.get_tape_symbol(0), "_")

        c1 = forward_step_rutm(c0, p_blank)
        self.assertEqual(c1.tape[0], "1")

        c0_restored = reverse_step_rutm(c1, program=p_blank)
        self.assertEqual(c0_restored.get_tape_symbol(0), "_")
        self.assertEqual(c0_restored, c0)

    # -------------------------------------------------------------------------
    # Theorem 2: Finite-Trace Reversibility Tests
    # -------------------------------------------------------------------------

    def test_13_finite_trace_reversibility(self):
        """Test 13: Theorem 2 verification - multi-step forward run followed by multi-step reverse returns c0."""
        c0 = create_initial_rutm_configuration(tape={0: "0", 1: "_"}, initial_state="q_start")

        # Step 1
        c1 = forward_step_rutm(c0, self.program_a)
        # Step 2
        c2 = forward_step_rutm(c1, self.program_a)
        # Step 3 (Halting)
        c3 = forward_step_rutm(c2, self.program_a)

        self.assertEqual(c3.current_state, "q_halt")
        self.assertTrue(c3.halted)

        # Reverse Step 3 -> 2 -> 1 -> 0
        c2_rev = reverse_step_rutm(c3, program=self.program_a)
        self.assertEqual(c2_rev, c2)

        c1_rev = reverse_step_rutm(c2_rev, program=self.program_a)
        self.assertEqual(c1_rev, c1)

        c0_rev = reverse_step_rutm(c1_rev, program=self.program_a)
        self.assertEqual(c0_rev, c0)

    # -------------------------------------------------------------------------
    # Theorem 3: Projection Preservation & Commuting Diagram Tests
    # -------------------------------------------------------------------------

    def test_14_projection_preservation_commuting_diagram(self):
        """Test 14: Theorem 3 verification - pi_UTM(R(C_R, P)) == step_utm_configuration(pi_UTM(C_R), P)."""
        c0_rutm = create_initial_rutm_configuration(tape={0: "0", 1: "_"}, initial_state="q_start")
        c1_rutm = forward_step_rutm(c0_rutm, self.program_a)
        c2_rutm = forward_step_rutm(c1_rutm, self.program_a)

        # Projected UTM configurations
        pi_c0 = project_to_utm(c0_rutm)
        pi_c1 = project_to_utm(c1_rutm)
        pi_c2 = project_to_utm(c2_rutm)

        # Source UTM steps
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        c1_utm = step_utm_configuration(c0_utm, self.program_a)
        c2_utm = step_utm_configuration(c1_utm, self.program_a)

        self.assertEqual(pi_c0, c0_utm)
        self.assertEqual(pi_c1, c1_utm)
        self.assertEqual(pi_c2, c2_utm)

    # -------------------------------------------------------------------------
    # Negative / Boundary Tests (Domain Rejection)
    # -------------------------------------------------------------------------

    def test_15_negative_error_configuration_domain_rejection(self):
        """Test 15: Error configurations are outside Dom_rev(P) and rejected by forward/reverse steps."""
        c_err = RUTMConfiguration(error="Existing error string")
        c_fwd = forward_step_rutm(c_err, self.program_a)
        self.assertEqual(c_fwd.error, "Existing error string")

        c_rev = reverse_step_rutm(c_err, program=self.program_a)
        self.assertEqual(c_rev.error, "Existing error string")

    def test_16_negative_initial_empty_history_rejection(self):
        """Test 16: Reverse step on initial configuration (history=[]) is rejected with domain error."""
        c0 = create_initial_rutm_configuration(tape={0: "0"}, initial_state="q_start")
        c_rev = reverse_step_rutm(c0, program=self.program_a)

        self.assertIsNotNone(c_rev.error)
        self.assertIn("Cannot reverse initial configuration", c_rev.error)

    def test_17_negative_undefined_transition_domain_rejection(self):
        """Test 17: Undefined transition assigns error string without mutating configuration."""
        c0 = create_initial_rutm_configuration(tape={0: "1"}, initial_state="q_start")
        c1 = forward_step_rutm(c0, self.program_a)  # (q_start, '1') undefined

        self.assertIsNotNone(c1.error)
        self.assertIn("Undefined transition", c1.error)
        self.assertEqual(c1.step_count, 0)
        self.assertEqual(len(c1.history), 0)

    def test_18_negative_malformed_configuration_domain_rejection(self):
        """Test 18: Malformed configuration (k != |H|) is rejected by domain validation."""
        r1 = HistoryRecord("q_start", "0", Direction.RIGHT)
        c_bad = RUTMConfiguration(
            current_state="q1",
            tape={0: "1"},
            head_pos=1,
            history=(r1,),
            step_count=99,  # Invalid: step_count != len(history)
            halted=False,
        )
        c_fwd = forward_step_rutm(c_bad, self.program_a)
        self.assertIsNotNone(c_fwd.error)
        self.assertIn("Invalid configuration", c_fwd.error)

        c_rev = reverse_step_rutm(c_bad, program=self.program_a)
        self.assertIsNotNone(c_rev.error)
        self.assertIn("Invalid configuration", c_rev.error)


if __name__ == "__main__":
    unittest.main()
