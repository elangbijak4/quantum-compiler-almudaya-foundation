"""
Application / Product Layer — Tutorial Examples Executable Validation Tests.

Validates that every sample program file in tutorial/examples/ compiles and executes cleanly
through the Production CLI entrypoint without errors.
"""

import os
import unittest

from src.application import (
    ApplicationContractService,
    CLIExitCode,
    run_cli,
)


class TestTutorialExamples(unittest.TestCase):
    """Executable validation test suite for tutorial example files."""

    def setUp(self) -> None:
        self.service = ApplicationContractService()
        self.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tutorial/examples"))

    def test_01_assignment_aml(self) -> None:
        """Validates 01_assignment.aml compilation through CLI."""
        filepath = os.path.join(self.examples_dir, "01_assignment.aml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read().strip()

        exit_code, output = run_cli(["compile", code, "--backend", "LOCAL_REFERENCE"], service=self.service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("SUCCESS", output)

    def test_02_multi_statement_aml(self) -> None:
        """Validates 02_multi_statement.aml compilation through CLI."""
        filepath = os.path.join(self.examples_dir, "02_multi_statement.aml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read().strip()

        exit_code, output = run_cli(["compile", code, "--backend", "LOCAL_REFERENCE"], service=self.service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("SUCCESS", output)

    def test_03_expression_aml(self) -> None:
        """Validates 03_expression.aml compilation through CLI."""
        filepath = os.path.join(self.examples_dir, "03_expression.aml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read().strip()

        exit_code, output = run_cli(["compile", code, "--backend", "LOCAL_REFERENCE"], service=self.service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("SUCCESS", output)

    def test_04_boolean_logic_aml(self) -> None:
        """Validates 04_boolean_logic.aml compilation through CLI."""
        filepath = os.path.join(self.examples_dir, "04_boolean_logic.aml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read().strip()

        exit_code, output = run_cli(["compile", code, "--backend", "LOCAL_REFERENCE"], service=self.service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("SUCCESS", output)

    def test_05_arithmetic_aml(self) -> None:
        """Validates 05_arithmetic.aml compilation through CLI."""
        filepath = os.path.join(self.examples_dir, "05_arithmetic.aml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read().strip()

        exit_code, output = run_cli(["compile", code, "--backend", "LOCAL_REFERENCE"], service=self.service)
        self.assertEqual(exit_code, CLIExitCode.SUCCESS.value)
        self.assertIn("SUCCESS", output)


if __name__ == "__main__":
    unittest.main()
