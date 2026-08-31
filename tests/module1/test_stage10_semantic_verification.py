"""
Stage 10 Unit Tests: Semantic Equivalence Verification.

Strictly verifies Stage 10 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.verification.dual import (
    DualExecutionResult,
    execute_dual_pipeline,
)
from src.module1.verification.verifier import (
    SemanticVerificationResult,
    verify_semantic_equivalence,
)
from src.module1.utm.simulator import UTMExecutionResult
from src.module1.utm.model import UTMConfiguration


class TestStage10SemanticVerification(unittest.TestCase):
    """Test suite for Stage 10 Semantic Equivalence Verifier."""

    def test_1_golden_poc_semantic_equivalence(self):
        """
        Test 1: Empirical semantic equivalence verification for golden PoC (add_two_values.aml).
        Input: A = 5, B = 7
        Expected: VERIFIED, verified=True, source_result == target_result == {"OUT": 12}
        """
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            source = f.read()

        dual_res = execute_dual_pipeline(source, initial_memory={"A": 5, "B": 7})
        ver_res = verify_semantic_equivalence(dual_res)

        print("\n[DEBUG VER_RES]:", ver_res)

        self.assertEqual(ver_res.status, "VERIFIED")
        self.assertTrue(ver_res.verified)
        self.assertIsNone(ver_res.mismatch_reason)
        self.assertEqual(ver_res.source_result.get("OUT"), 12)
        self.assertEqual(ver_res.target_result.get("OUT"), 12)
        self.assertTrue(ver_res.source_halted)
        self.assertTrue(ver_res.target_halted)
        self.assertEqual(len(ver_res.source_program_hash), 64)

    def test_2_sequential_and_loop_equivalence(self):
        """Test 2-8: Verification of sequential, loop, arithmetic, store, branch, and HALT equivalence."""
        loop_source = """
        LOAD R1, 4
        LOAD R2, 0
LOOP:   ADD  R2, R1
        SUB  R1, 1
        CMP  R1, 0
        JNZ  LOOP
        STORE TOTAL, R2
        HALT
"""
        dual_res = execute_dual_pipeline(loop_source)
        ver_res = verify_semantic_equivalence(dual_res)

        self.assertEqual(ver_res.status, "VERIFIED")
        self.assertTrue(ver_res.verified)
        self.assertEqual(ver_res.source_result.get("TOTAL"), 10)
        self.assertEqual(ver_res.target_result.get("TOTAL"), 10)

    def test_3_negative_output_mismatch_detection(self):
        """Test 13: CRITICAL NEGATIVE TEST - Output mismatch detection returning MISMATCH."""
        source = "LOAD R1, 5\nSTORE OUT, R1\nHALT"
        dual_res = execute_dual_pipeline(source)
        self.assertEqual(dual_res.status, "DUAL_EXECUTION_COMPLETED")

        # Corrupt target output manually in dual_res for testing mismatch detection
        corrupted_utm_tape = dict(dual_res.utm_result.final_configuration.tape)

        # Decode cell index for 'OUT' and alter its value
        for idx, val in corrupted_utm_tape.items():
            if val == "5":
                corrupted_utm_tape[idx] = "99"  # Corrupt output value 5 to 99

        corrupted_utm_config = UTMConfiguration(
            current_state=dual_res.utm_result.final_configuration.current_state,
            tape=corrupted_utm_tape,
            head_pos=dual_res.utm_result.final_configuration.head_pos,
            step_count=dual_res.utm_result.step_count,
            halted=dual_res.utm_result.halted,
        )

        corrupted_utm_result = UTMExecutionResult(
            final_configuration=corrupted_utm_config,
            status="SUCCESS",
            halted=True,
            step_count=dual_res.utm_result.step_count,
            tape_usage=dual_res.utm_result.tape_usage,
        )

        corrupted_dual_result = DualExecutionResult(
            aml_result=dual_res.aml_result,
            translation_result=dual_res.translation_result,
            utm_result=corrupted_utm_result,
            source_hash=dual_res.source_hash,
            status="DUAL_EXECUTION_COMPLETED",
        )

        ver_res = verify_semantic_equivalence(corrupted_dual_result)

        self.assertEqual(ver_res.status, "MISMATCH")
        self.assertFalse(ver_res.verified)
        self.assertIsNotNone(ver_res.mismatch_reason)
        self.assertIn("mismatch", ver_res.mismatch_reason.lower())

    def test_4_negative_halting_mismatch_detection(self):
        """Test 14: Halting mismatch detection returning MISMATCH."""
        source = "LOAD R1, 5\nHALT"
        dual_res = execute_dual_pipeline(source)

        # Corrupt target halting status to False
        corrupted_utm_result = UTMExecutionResult(
            final_configuration=dual_res.utm_result.final_configuration,
            status="SUCCESS",
            halted=False,  # Halting mismatch!
            step_count=dual_res.utm_result.step_count,
            tape_usage=dual_res.utm_result.tape_usage,
        )

        corrupted_dual_result = DualExecutionResult(
            aml_result=dual_res.aml_result,
            translation_result=dual_res.translation_result,
            utm_result=corrupted_utm_result,
            source_hash=dual_res.source_hash,
            status="DUAL_EXECUTION_COMPLETED",
        )

        ver_res = verify_semantic_equivalence(corrupted_dual_result)

        self.assertEqual(ver_res.status, "MISMATCH")
        self.assertFalse(ver_res.verified)
        self.assertIn("Halting mismatch", ver_res.mismatch_reason)

    def test_5_failure_classification(self):
        """Test 9-12: Correct failure status classification (SOURCE_EXECUTION_FAILURE, INVALID_TRANSLATION, etc.)."""
        # Parser failure
        bad_syntax_dual = execute_dual_pipeline("LOAD R1 A\nHALT")
        ver_res1 = verify_semantic_equivalence(bad_syntax_dual)
        self.assertEqual(ver_res1.status, "SOURCE_EXECUTION_FAILURE")
        self.assertFalse(ver_res1.verified)

        # Resource limit
        inf_loop_dual = execute_dual_pipeline("START: JMP START", utm_max_steps=10)
        ver_res2 = verify_semantic_equivalence(inf_loop_dual)
        self.assertEqual(ver_res2.status, "RESOURCE_LIMIT")
        self.assertFalse(ver_res2.verified)

    def test_6_deterministic_verification_result(self):
        """Test 15-16: Deterministic verification result and source program hash preservation."""
        source = "LOAD R1, 5\nSTORE OUT, R1\nHALT"
        dual_res1 = execute_dual_pipeline(source)
        dual_res2 = execute_dual_pipeline(source)

        ver1 = verify_semantic_equivalence(dual_res1)
        ver2 = verify_semantic_equivalence(dual_res2)

        self.assertEqual(ver1.status, ver2.status)
        self.assertEqual(ver1.verified, ver2.verified)
        self.assertEqual(ver1.source_program_hash, ver2.source_program_hash)


if __name__ == "__main__":
    unittest.main()
