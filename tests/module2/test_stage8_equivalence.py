"""
Unit Tests for Module 2 Stage 8: UTM -> RUTM Equivalence Verification Gate.

Strictly compliant with Stage 8 requirements (main-technical-refference.md & STAGE_8_UTM_RUTM_EQUIVALENCE.md).
"""

import unittest
from unittest.mock import patch
from src.module1.utm.model import Direction, TransitionAction, UTMProgram, UTMConfiguration
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm_ir.model import RUTM_IR
from src.module2.translation.utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm
from src.module2.execution.executor import execute_rutm_ir
from src.module2.execution.result import RUTMExecutionResult
from src.module2.execution.verifier import verify_trace_reversibility, verify_projected_utm_correspondence
from src.module2.verification.equivalence import verify_utm_to_rutm_equivalence


class TestStage8EquivalenceGate(unittest.TestCase):
    """Stage 8 UTM -> RUTM Equivalence Verification Gate Test Suite."""

    def setUp(self):
        """Construct standard test machines and programs."""
        # 1. Standard 3-step program A (Golden PoC)
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
        self.c0_a = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)

        # 2. Countdown/Loop Program
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
        self.c0_loop = UTMConfiguration(current_state="q_start", tape={0: "1", 1: "1", 2: "0"}, head_pos=0, step_count=0)

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

    def test_1_golden_poc_equivalence_pass(self):
        """Test 1: Golden PoC pipeline executes and yields PASS."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res.status, "PASS")
        self.assertTrue(res.equivalent)
        self.assertIsNone(res.error)

    def test_2_initial_configuration_correspondence(self):
        """Test 2: Initial configuration correspondence verified at step 0."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res.status, "PASS")
        self.assertGreaterEqual(res.steps_compared, 1)

    def test_3_complete_finite_trace_correspondence(self):
        """Test 3: Complete 3-step finite trace corresponds component-wise."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res.steps_compared, 4)  # steps 0, 1, 2, 3
        self.assertEqual(res.source_trace_length, 4)
        self.assertEqual(res.target_trace_length, 4)

    def test_4_state_correspondence(self):
        """Test 4: Control states correspond throughout execution trace."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertTrue(res.equivalent)

    def test_5_tape_correspondence(self):
        """Test 5: Main tape contents correspond throughout execution trace."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertTrue(res.equivalent)

    def test_6_head_correspondence(self):
        """Test 6: Head position corresponds throughout execution trace."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertTrue(res.equivalent)

    def test_7_step_count_correspondence(self):
        """Test 7: Step counter corresponds throughout execution trace."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertTrue(res.equivalent)

    def test_8_halt_correspondence(self):
        """Test 8: Source and target reach q_halt simultaneously."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertTrue(res.source_halted)
        self.assertTrue(res.target_halted)

    def test_9_loop_countdown_equivalence(self):
        """Test 9: Loop/countdown program yields status PASS."""
        res = verify_utm_to_rutm_equivalence(self.loop_program, self.c0_loop)
        self.assertEqual(res.status, "PASS")
        self.assertTrue(res.equivalent)
        self.assertEqual(res.steps_compared, 4)

    def test_10_runtime_error_produces_fail(self):
        """Test 10: Defined runtime error (undefined transition) produces status FAIL."""
        undefined_prog = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "1", "_"},
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        c0_undef = UTMConfiguration(current_state="q_start", tape={0: "1"}, head_pos=0, step_count=0)
        res = verify_utm_to_rutm_equivalence(undefined_prog, c0_undef)
        self.assertEqual(res.status, "FAIL")
        self.assertFalse(res.equivalent)

    def test_11_mismatch_step_is_reported(self):
        """Test 11: Mismatch step index is non-null on runtime or projection failure."""
        undefined_prog = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "1", "_"},
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        c0_undef = UTMConfiguration(current_state="q_start", tape={0: "1"}, head_pos=0, step_count=0)
        res = verify_utm_to_rutm_equivalence(undefined_prog, c0_undef)
        self.assertIsNotNone(res.mismatch_step)
        self.assertGreaterEqual(res.mismatch_step, 0)

    def test_12_resource_exhaustion_produces_inconclusive(self):
        """Test 12: Infinite loop reaching max_steps produces status INCONCLUSIVE, not PASS or FAIL."""
        c0_inf = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, step_count=0)
        res = verify_utm_to_rutm_equivalence(self.infinite_program, c0_inf, max_steps=5)
        self.assertEqual(res.status, "INCONCLUSIVE")
        self.assertFalse(res.equivalent)
        self.assertTrue(res.resource_limit_reached)

    def test_13_invalid_source_ir_is_rejected(self):
        """Test 13: Invalid source UTMProgram yields status FAIL."""
        bad_utm = UTMProgram(states=set())  # Empty states
        res = verify_utm_to_rutm_equivalence(bad_utm)
        self.assertEqual(res.status, "FAIL")
        self.assertIn("Invalid source UTMProgram", res.error)

    def test_14_invalid_translated_ir_is_rejected(self):
        """Test 14: Translator returning invalid RUTM-IR causes gate failure."""
        bad_utm = UTMProgram(states=set())
        res = verify_utm_to_rutm_equivalence(bad_utm)
        self.assertEqual(res.status, "FAIL")

    def test_15_translation_failure_is_reported(self):
        """Test 15: Translation error message is captured in result."""
        bad_utm = UTMProgram(states=set())
        res = verify_utm_to_rutm_equivalence(bad_utm)
        self.assertIsNotNone(res.error)

    def test_16_runtime_error_classification(self):
        """Test 16: Program encountering undefined transition yields status FAIL."""
        undefined_prog = UTMProgram(
            states={"q_start", "q_halt"},
            alphabet={"0", "1", "_"},
            initial_state="q_start",
            halt_state="q_halt",
            transitions={},
        )
        c0_undef = UTMConfiguration(current_state="q_start", tape={0: "1"}, head_pos=0, step_count=0)
        res = verify_utm_to_rutm_equivalence(undefined_prog, c0_undef)
        self.assertEqual(res.status, "FAIL")

    def test_17_deterministic_verification_result(self):
        """Test 17: Repeated verification produces identical status and metrics."""
        res1 = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        res2 = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res1.status, res2.status)
        self.assertEqual(res1.steps_compared, res2.steps_compared)

    def test_18_provenance_preservation(self):
        """Test 18: Result retains provenance metadata."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertIsNotNone(res.provenance)
        self.assertEqual(res.provenance.get("gate_stage"), "Stage 8")

    def test_19_existing_stage7_verifier_integration(self):
        """Test 19: Integrates Stage 7 verifiers (reversibility and projection) smoothly."""
        rutm_ir = translate_utm_to_rutm(self.utm_program_a).target_ir
        rutm_res = execute_rutm_ir(rutm_ir, initial_tape={0: "0", 1: "_"})
        diff_res = verify_projected_utm_correspondence(rutm_res, self.utm_program_a, self.c0_a)
        self.assertTrue(diff_res.matched)

    def test_20_full_pipeline(self):
        """Test 20: Full pipeline UTM -> RUTM -> execution -> projection -> gate PASS."""
        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res.status, "PASS")
        self.assertTrue(res.equivalent)
        self.assertEqual(res.steps_compared, 4)

    @patch("src.module2.verification.equivalence.execute_rutm_ir")
    def test_21_real_semantic_mismatch_produces_fail(self, mock_execute):
        """Test 21: Actual projection step semantic mismatch (state mismatch) produces status FAIL."""
        # Execute genuine translator to get real target IR
        rutm_ir = translate_utm_to_rutm(self.utm_program_a).target_ir
        real_res = execute_rutm_ir(rutm_ir, initial_config=map_utm_configuration_to_rutm(self.c0_a, rutm_ir))

        # Construct a corrupted target trace where step 1 has mismatched state "q_WRONG"
        corrupted_trace = list(real_res.trace)
        c1 = corrupted_trace[1]
        corrupted_c1 = RUTMConfiguration(
            current_state="q_WRONG",
            tape=dict(c1.tape),
            head_pos=c1.head_pos,
            history=c1.history,
            step_count=c1.step_count,
            halted=c1.halted,
            error=c1.error,
        )
        corrupted_trace[1] = corrupted_c1

        mock_execute.return_value = RUTMExecutionResult(
            success=True,
            initial_configuration=corrupted_trace[0],
            final_configuration=corrupted_trace[-1],
            trace=tuple(corrupted_trace),
            steps_executed=len(corrupted_trace) - 1,
            halted=True,
            error=None,
        )

        res = verify_utm_to_rutm_equivalence(self.utm_program_a, self.c0_a)
        self.assertEqual(res.status, "FAIL")
        self.assertFalse(res.equivalent)
        self.assertEqual(res.mismatch_step, 1)
        self.assertIsNotNone(res.error)
        self.assertIn("Semantic mismatch at step 1", res.error)

    @patch("src.module2.verification.equivalence.execute_rutm_ir")
    def test_22_terminal_halt_mismatch_produces_fail(self, mock_execute):
        """Test 22: Terminal halt mismatch (source non-halting, target halted) takes precedence over max_steps -> FAIL."""
        # Non-halting infinite source program
        c0_inf = UTMConfiguration(current_state="q_start", tape={0: "0"}, head_pos=0, step_count=0)
        rutm_ir = translate_utm_to_rutm(self.infinite_program).target_ir
        real_res = execute_rutm_ir(rutm_ir, initial_config=map_utm_configuration_to_rutm(c0_inf, rutm_ir), max_steps=5)

        # Corrupt final configuration to claim target halted=True
        halted_final = RUTMConfiguration(
            current_state="q_halt",
            tape=dict(real_res.final_configuration.tape),
            head_pos=real_res.final_configuration.head_pos,
            history=real_res.final_configuration.history,
            step_count=real_res.final_configuration.step_count,
            halted=True,
            error=None,
        )

        mock_execute.return_value = RUTMExecutionResult(
            success=True,
            initial_configuration=real_res.initial_configuration,
            final_configuration=halted_final,
            trace=real_res.trace,
            steps_executed=5,
            halted=True,  # Mismatched target halt!
            error=None,
        )

        res = verify_utm_to_rutm_equivalence(self.infinite_program, c0_inf, max_steps=5)
        self.assertEqual(res.status, "FAIL")
        self.assertFalse(res.equivalent)
        self.assertFalse(res.source_halted)
        self.assertTrue(res.target_halted)
        self.assertIn("Halt correspondence mismatch", res.error)


if __name__ == "__main__":
    unittest.main()
