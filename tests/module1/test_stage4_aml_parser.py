"""
Stage 4 Unit Tests: AML v0.1 Parser & AML-IR (AMLProgram).

Strictly verifies Stage 4 compliance per main-technical-refference.md.
"""

import os
import unittest
from src.module1.aml.spec import Opcode
from src.module1.aml.parser import (
    ParseError,
    AMLInstruction,
    AMLProgram,
    parse_aml_source,
)


class TestStage4AMLParser(unittest.TestCase):
    """Test suite for Stage 4 AML v0.1 parser and AML-IR data structures."""

    def test_parse_poc_example_string(self):
        """Test parsing first PoC example string into AML-IR."""
        poc_source = """
# Module 1 first PoC
# Expected OUT = 12 when A = 5 and B = 7

LOAD R1, A
LOAD R2, B
ADD  R1, R2
STORE OUT, R1
HALT
"""
        program = parse_aml_source(poc_source)
        self.assertEqual(len(program.instructions), 5)
        self.assertEqual(program.symbol_table, {"A", "B", "OUT"})
        self.assertTrue(len(program.source_hash) == 64)  # SHA-256 length

        # Verify individual AMLInstruction IR items
        self.assertEqual(program.instructions[0].opcode, Opcode.LOAD)
        self.assertEqual(program.instructions[0].operands, ["R1", "A"])
        self.assertEqual(program.instructions[0].pc, 0)

        self.assertEqual(program.instructions[2].opcode, Opcode.ADD)
        self.assertEqual(program.instructions[2].operands, ["R1", "R2"])
        self.assertEqual(program.instructions[2].pc, 2)

        self.assertEqual(program.instructions[4].opcode, Opcode.HALT)
        self.assertEqual(program.instructions[4].operands, [])
        self.assertEqual(program.instructions[4].pc, 4)

    def test_parse_poc_example_file(self):
        """Test parsing actual add_two_values.aml file on disk."""
        poc_path = "examples/aml/add_two_values.aml"
        self.assertTrue(os.path.exists(poc_path))
        with open(poc_path, "r", encoding="utf-8") as f:
            source_content = f.read()

        program = parse_aml_source(source_content)
        self.assertEqual(len(program.instructions), 5)
        self.assertEqual(program.symbol_table, {"A", "B", "OUT"})

    def test_parse_labels_and_label_table(self):
        """Test parsing programs with labels and jump targets."""
        source_with_labels = """
START:  LOAD R1, 10
LOOP:   SUB R1, 1
        CMP R1, 0
        JNZ LOOP
        HALT
"""
        program = parse_aml_source(source_with_labels)
        self.assertEqual(len(program.instructions), 5)
        self.assertIn("START", program.label_table)
        self.assertIn("LOOP", program.label_table)

        self.assertEqual(program.label_table["START"], 0)
        self.assertEqual(program.label_table["LOOP"], 1)

        self.assertEqual(program.instructions[0].label, "START")
        self.assertEqual(program.instructions[1].label, "LOOP")
        self.assertIsNone(program.instructions[2].label)

    def test_parse_error_reporting(self):
        """Test explicit ParseError raising on invalid AML source code."""
        # 1. Missing comma on line 2
        bad_source_1 = "LOAD R1, 5\nLOAD R2 A\nHALT"
        with self.assertRaises(ParseError) as cm:
            parse_aml_source(bad_source_1)
        self.assertEqual(cm.exception.line_number, 2)

        # 2. Unknown opcode on line 3
        bad_source_2 = "LOAD R1, 5\nLOAD R2, 10\nDIV R1, R2\nHALT"
        with self.assertRaises(ParseError) as cm:
            parse_aml_source(bad_source_2)
        self.assertEqual(cm.exception.line_number, 3)

        # 3. Duplicate label on line 4
        bad_source_3 = "LOOP: ADD R1, 1\nMOV R2, R1\nLOOP: SUB R1, 1"
        with self.assertRaises(ParseError) as cm:
            parse_aml_source(bad_source_3)
        self.assertEqual(cm.exception.line_number, 3)


if __name__ == "__main__":
    unittest.main()
