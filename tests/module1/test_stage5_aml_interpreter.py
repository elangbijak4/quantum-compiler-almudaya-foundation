"""
Stage 5 Unit Tests: AML v0.1 Interpreter & Executable Reference Semantics.

Strictly verifies Stage 5 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.aml.parser import parse_aml_source
from src.module1.aml.interpreter import (
    AMLInterpreterResult,
    AMLInterpreter,
    execute_aml_source,
)


class TestStage5AMLInterpreter(unittest.TestCase):
    """Test suite for Stage 5 AML v0.1 Reference Interpreter."""

    def test_poc_add_two_values_execution(self):
        """
        Test full end-to-end execution of the first PoC program (add_two_values.aml).
        Input: A = 5, B = 7
        Expected: OUT = 12, Status = SUCCESS, Steps = 5
        """
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            poc_source = f.read()

        initial_mem = {"A": 5, "B": 7}
        result = execute_aml_source(poc_source, initial_memory=initial_mem)

        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(result.final_state.flags.halted)
        self.assertEqual(result.step_count, 5)
        self.assertEqual(result.observable_output.get("OUT"), 12)
        self.assertEqual(result.final_state.registers["R1"], 12)

    def test_loop_countdown_execution(self):
        """Test execution of a countdown loop using CMP, JNZ, SUB, ADD."""
        loop_source = """
# Compute sum of 5 + 4 + 3 + 2 + 1 = 15
        LOAD R1, 5
        LOAD R2, 0
LOOP:   ADD  R2, R1
        SUB  R1, 1
        CMP  R1, 0
        JNZ  LOOP
        STORE SUM, R2
        HALT
"""
        result = execute_aml_source(loop_source)
        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(result.final_state.flags.halted)
        self.assertEqual(result.observable_output.get("SUM"), 15)

    def test_resource_limit_enforcement(self):
        """Test enforcement of max_steps returning RESOURCE_LIMIT on infinite loop."""
        infinite_loop = """
START:  JMP START
        HALT
"""
        result = execute_aml_source(infinite_loop, max_steps=50)
        self.assertEqual(result.status, "RESOURCE_LIMIT")
        self.assertFalse(result.final_state.flags.halted)
        self.assertEqual(result.step_count, 50)

    def test_pc_out_of_bounds_error(self):
        """Test PC out of bounds error when program ends without HALT."""
        no_halt_source = """
LOAD R1, 10
ADD  R1, 5
"""
        result = execute_aml_source(no_halt_source)
        self.assertEqual(result.status, "ERROR")
        self.assertIn("out of bounds", result.final_state.flags.error)


if __name__ == "__main__":
    unittest.main()
