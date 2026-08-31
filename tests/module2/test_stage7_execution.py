"""
Unit Tests for Module 2 Stage 7: RUTM-IR Execution Engine & Trace Verification.

Strictly compliant with Stage 7 requirements (main-technical-refference.md & STAGE_7_RUTM_EXECUTION.md).
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram, UTMConfiguration
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm_ir.model import RUTM_IR, RUTMHistoryPolicy, RUTMProvenance
from src.module2.translation.utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm
from src.module2.execution.executor import execute_rutm_ir
from src.module2.execution.verifier import verify_trace_reversibility, verify_projected_utm_correspondence


class TestStage7Execution(unittest.TestCase):
    """Stage 7 RUTM-IR Execution Engine and Trace Verification Test Suite."""

    def setUp(self):
        """Construct standard test machines and programs."""
        # 1. Standard 3-step program A
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
        self.rutm_ir_a = translate_utm_to_rutm(self.utm_program_a, machine_name="MachineA").target_ir

        # 2. Countdown/Loop Program (decrements binary counter or loops 3 times)
        self.loop_program = UTMProgram(
            states={"q_start", "q_loop", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "1"): TransitionAction("q_loop", "1", Direction.RIGHT),
                ("q_loop", "1"): TransitionAction("q_loop", "0", Direction.RIGHT),
                ("q_loop", "0"): TransitionAction("q_halt", "1", Direction.STAY),
            },
        )
        self.loop_ir = translate_utm_to_rutm(self.loop_program, machine_name="LoopMachine").target_ir

        # 3. Non-halting infinite loop program for resource limit test
        self.infinite_program = UTMProgram(
            states={"q_start", "q_loop", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={
                ("q_start", "0"): TransitionAction("q_loop", "0", Direction.RIGHT),
                ("q_loop", "_"): TransitionAction("q_start", "0", Direction.LEFT),
            },
        )
        self.infinite_ir = translate_utm_to_rutm(self.infinite_program, machine_name="InfiniteMachine").target_ir

    def test_1_valid_rutm_ir_execution(self):
        """Test 1: Valid RUTM-IR executes with success=True."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"})
        self.assertTrue(res.success)
        self.assertTrue(res.halted)
        self.assertIsNone(res.error)

    def test_2_initial_configuration_correctness(self):
        """Test 2: Initial trace entry C_0 has step_count=0, empty history, and matches tape input."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"})
        c0 = res.initial_configuration
        self.assertEqual(c0.current_state, "q_start")
        self.assertEqual(c0.tape, {0: "0"})
        self.assertEqual(c0.head_pos, 0)
        self.assertEqual(c0.step_count, 0)
        self.assertEqual(c0.history, ())
        self.assertFalse(c0.halted)

    def test_3_single_step_execution(self):
        """Test 3: Single-step execution with max_steps=1 produces 2 trace entries."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"}, max_steps=1)
        self.assertTrue(res.success)
        self.assertEqual(len(res.trace), 2)
        self.assertEqual(res.steps_executed, 1)

    def test_4_multi_step_trace(self):
        """Test 4: Multi-step execution trace captures correct sequence length."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        self.assertTrue(res.halted)
        self.assertEqual(res.steps_executed, 3)
        self.assertEqual(len(res.trace), 4)

    def test_5_trace_configuration_integrity(self):
        """Test 5: Every trace entry has step_count matching its trace index."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        for idx, cfg in enumerate(res.trace):
            self.assertEqual(cfg.step_count, idx)

    def test_6_trace_immutability(self):
        """Test 6: Later execution steps do not mutate earlier trace entries."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        # Verify trace[0] tape remains original initial configuration tape {0: '0', 1: '_'}
        self.assertEqual(res.trace[0].tape, {0: "0", 1: "_"})
        self.assertEqual(res.trace[0].current_state, "q_start")
        self.assertEqual(res.trace[0].step_count, 0)

        # Verify trace[1] tape has overwritten symbol '1' at pos 0
        self.assertEqual(res.trace[1].tape.get(0), "1")
        self.assertEqual(res.trace[1].step_count, 1)

        # Verify trace[0] was NOT mutated when trace[1] was produced
        self.assertEqual(res.trace[0].tape.get(0), "0")

    def test_7_halt_detection(self):
        """Test 7: Reaching q_halt stops execution and sets halted=True, resource_limit_reached=False."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        self.assertTrue(res.halted)
        self.assertFalse(res.resource_limit_reached)
        self.assertEqual(res.final_configuration.current_state, "q_halt")

    def test_8_runtime_error_handling(self):
        """Test 8: Undefined transition produces controlled execution result with error message."""
        bad_trans_prog = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "1", "_"},
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},  # No transitions defined
        )
        bad_ir = translate_utm_to_rutm(bad_trans_prog, machine_name="BadTrans").target_ir
        res = execute_rutm_ir(bad_ir, initial_tape={0: "1"})

        self.assertFalse(res.success)
        self.assertFalse(res.halted)
        self.assertIsNotNone(res.error)
        self.assertIn("Undefined transition", res.error)

    def test_9_resource_limit(self):
        """Test 9: Infinite loop hits max_steps, sets resource_limit_reached=True without false halt."""
        res = execute_rutm_ir(self.infinite_ir, initial_tape={0: "0"}, max_steps=5)
        self.assertTrue(res.success)
        self.assertFalse(res.halted)
        self.assertTrue(res.resource_limit_reached)
        self.assertEqual(res.steps_executed, 5)

    def test_10_deterministic_execution(self):
        """Test 10: Repeated execution produces identical trace configurations."""
        res1 = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"})
        res2 = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"})
        self.assertEqual(res1.trace, res2.trace)

    def test_11_history_evolution(self):
        """Test 11: History length grows monotonically matching step_count (|H_i| == i)."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"})
        for i, cfg in enumerate(res.trace):
            self.assertEqual(len(cfg.history), i)

    def test_12_reverse_single_step_verification(self):
        """Test 12: Reverse step verification restores single-step predecessor configuration."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0"}, max_steps=1)
        v_res = verify_trace_reversibility(res, self.rutm_ir_a)
        self.assertTrue(v_res.verified)
        self.assertEqual(v_res.reverse_steps, 1)

    def test_13_complete_finite_trace_reversal(self):
        """Test 13: Full finite-trace reversal succeeds for complete execution trace."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        v_res = verify_trace_reversibility(res, self.rutm_ir_a)
        self.assertTrue(v_res.verified)
        self.assertEqual(v_res.reverse_steps, 3)

    def test_14_original_configuration_restoration(self):
        """Test 14: Restored configuration component-wise equals initial C_0."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        v_res = verify_trace_reversibility(res, self.rutm_ir_a)
        self.assertEqual(v_res.restored_configuration, res.initial_configuration)

    def test_15_invalid_ir_rejection(self):
        """Test 15: Executing invalid RUTM_IR returns success=False before runtime execution."""
        bad_ir = RUTM_IR(
            name="",
            states=frozenset(),
            input_alphabet=frozenset(),
            tape_alphabet=frozenset(),
            blank_symbol="_",
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        res = execute_rutm_ir(bad_ir)
        self.assertFalse(res.success)
        self.assertIn("Invalid RUTM_IR", res.error)

    def test_16_golden_poc(self):
        """Test 16: Golden PoC pipeline (Translation -> Execution -> Reversibility -> Projection)."""
        # Execute translated Golden PoC machine
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        self.assertTrue(res.success)
        self.assertTrue(res.halted)

        # Verify finite-trace reversibility back to C_0
        rev_res = verify_trace_reversibility(res, self.rutm_ir_a)
        self.assertTrue(rev_res.verified)

        # Verify differential projection against classical source UTM
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        diff_res = verify_projected_utm_correspondence(res, self.utm_program_a, c0_utm)
        self.assertTrue(diff_res.matched)

    def test_17_loop_countdown_program(self):
        """Test 17: Loop/countdown program execution, projection matching, and trace reversal."""
        res = execute_rutm_ir(self.loop_ir, initial_tape={0: "1", 1: "1", 2: "0"})
        self.assertTrue(res.success)
        self.assertTrue(res.halted)
        self.assertEqual(res.steps_executed, 3)

        # Reversibility check
        rev_res = verify_trace_reversibility(res, self.loop_ir)
        self.assertTrue(rev_res.verified)

        # Differential projection check
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "1", 1: "1", 2: "0"}, head_pos=0, step_count=0)
        diff_res = verify_projected_utm_correspondence(res, self.loop_program, c0_utm)
        self.assertTrue(diff_res.matched)

    def test_18_utm_rutm_projected_trace_equivalence(self):
        """Test 18: pi_UTM(C_{R,i}) == C_{U,i} across full execution trace."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        diff_res = verify_projected_utm_correspondence(res, self.utm_program_a, c0_utm)
        self.assertTrue(diff_res.matched)
        self.assertEqual(diff_res.steps_compared, 4)

    def test_19_mismatch_reporting(self):
        """Test 19: Differential verifier detects mismatch when wrong UTM program is provided."""
        res = execute_rutm_ir(self.rutm_ir_a, initial_tape={0: "0", 1: "_"})
        # Provide different UTM program to trigger mismatch
        wrong_utm = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "1", "_"},
            initial_state="q_start",
            halt_state="q_halt",
            transitions={("q_start", "0"): TransitionAction("q_halt", "0", Direction.STAY)},
        )
        c0_utm = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)
        diff_res = verify_projected_utm_correspondence(res, wrong_utm, c0_utm)

        self.assertFalse(diff_res.matched)
        self.assertEqual(diff_res.mismatch_step, 1)
        self.assertIsNotNone(diff_res.error)

    def test_20_no_false_halt_on_resource_exhaustion(self):
        """Test 20: Resource exhaustion sets resource_limit_reached=True with halted=False."""
        res = execute_rutm_ir(self.infinite_ir, initial_tape={0: "0"}, max_steps=3)
        self.assertTrue(res.resource_limit_reached)
        self.assertFalse(res.halted)


if __name__ == "__main__":
    unittest.main()
