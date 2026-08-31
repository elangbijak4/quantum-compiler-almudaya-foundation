"""
Stage 9 Unit Tests: Dual Execution Orchestration.

Strictly verifies Stage 9 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.verification.dual import (
    DualExecutionResult,
    execute_dual_pipeline,
)


class TestStage9DualExecution(unittest.TestCase):
    """Test suite for Stage 9 Dual Execution Orchestration."""

    def test_golden_poc_dual_execution(self):
        """
        Test dual pipeline execution of golden PoC program (add_two_values.aml).
        Input: A = 5, B = 7
        """
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            source = f.read()

        initial_mem = {"A": 5, "B": 7}
        result = execute_dual_pipeline(source, initial_memory=initial_mem)

        self.assertEqual(result.status, "DUAL_EXECUTION_COMPLETED")
        self.assertIsNone(result.error)

        # Check Pathway A (AML Reference Interpreter)
        self.assertIsNotNone(result.aml_result)
        self.assertEqual(result.aml_result.status, "SUCCESS")
        self.assertEqual(result.aml_result.observable_output.get("OUT"), 12)

        # Check Pathway B1 (AML -> UTM Translator)
        self.assertIsNotNone(result.translation_result)
        self.assertEqual(result.translation_result.status, "TRANSLATION_GENERATED")

        # Check Pathway B2 (UTM Simulator)
        self.assertIsNotNone(result.utm_result)
        self.assertEqual(result.utm_result.status, "SUCCESS")
        self.assertTrue(result.utm_result.halted)

    def test_loop_program_dual_execution(self):
        """Test dual execution of a countdown loop program."""
        loop_source = """
        LOAD R1, 3
        LOAD R2, 0
LOOP:   ADD  R2, R1
        SUB  R1, 1
        CMP  R1, 0
        JNZ  LOOP
        STORE SUM, R2
        HALT
"""
        result = execute_dual_pipeline(loop_source)
        self.assertEqual(result.status, "DUAL_EXECUTION_COMPLETED")
        self.assertEqual(result.aml_result.observable_output.get("SUM"), 6)
        self.assertEqual(result.utm_result.status, "SUCCESS")

    def test_parser_error_handling(self):
        """Test dual execution failure on malformed source code."""
        bad_source = "LOAD R1 A\nHALT"  # Missing comma
        result = execute_dual_pipeline(bad_source)
        self.assertEqual(result.status, "PARSER_ERROR")
        self.assertIsNotNone(result.error)
        self.assertIsNone(result.aml_result)

    def test_side_by_side_source_hash(self):
        """Test source hash preservation in dual execution result."""
        source = "LOAD R1, 10\nHALT"
        result = execute_dual_pipeline(source)
        self.assertEqual(result.status, "DUAL_EXECUTION_COMPLETED")
        self.assertEqual(len(result.source_hash), 64)


if __name__ == "__main__":
    unittest.main()
