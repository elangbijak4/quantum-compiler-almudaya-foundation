"""
Stage 1 Unit Tests: AML v0.1 Formal Specification & Validation Primitives.

Strictly verifies Stage 1 compliance per main-technical-refference.md.
"""

import unittest
from src.module1.aml.spec import (
    Opcode,
    OperandType,
    InstructionSpec,
    REGISTER_NAMES,
    VALID_INSTRUCTIONS,
    validate_instruction_spec,
    detect_operand_type,
)


class TestStage1AMLSpecification(unittest.TestCase):
    """Test suite for Stage 1 AML v0.1 specification."""

    def test_opcode_count(self):
        """Verify exactly 11 valid opcodes in AML v0.1."""
        self.assertEqual(len(Opcode), 11)
        self.assertEqual(len(VALID_INSTRUCTIONS), 11)

    def test_register_domain(self):
        """Verify register set contains R0..R15."""
        self.assertEqual(len(REGISTER_NAMES), 16)
        for i in range(16):
            self.assertIn(f"R{i}", REGISTER_NAMES)

    def test_operand_type_detection(self):
        """Test detection of registers, immediates, and memory labels."""
        self.assertEqual(detect_operand_type("R0"), OperandType.REGISTER)
        self.assertEqual(detect_operand_type("r15"), OperandType.REGISTER)
        self.assertEqual(detect_operand_type("5"), OperandType.IMMEDIATE)
        self.assertEqual(detect_operand_type("-42"), OperandType.IMMEDIATE)
        self.assertEqual(detect_operand_type("A"), OperandType.LABEL_OR_ADDRESS)
        self.assertEqual(detect_operand_type("VAR_123"), OperandType.LABEL_OR_ADDRESS)
        self.assertIsNone(detect_operand_type(""))
        self.assertIsNone(detect_operand_type("!!!"))

    def test_positive_instruction_validation(self):
        """Test valid instruction signatures for all 11 opcodes."""
        valid_cases = [
            ("LOAD", ["R1", "A"]),
            ("LOAD", ["R2", "100"]),
            ("STORE", ["OUT", "R1"]),
            ("MOV", ["R1", "R2"]),
            ("MOV", ["R3", "42"]),
            ("ADD", ["R1", "R2"]),
            ("ADD", ["R1", "5"]),
            ("SUB", ["R1", "R2"]),
            ("MUL", ["R1", "R2"]),
            ("CMP", ["R1", "R2"]),
            ("JMP", ["LABEL_MAIN"]),
            ("JZ", ["TARGET_LABEL"]),
            ("JNZ", ["10"]),
            ("HALT", []),
        ]

        for opcode, operands in valid_cases:
            with self.subTest(opcode=opcode, operands=operands):
                is_valid, msg = validate_instruction_spec(opcode, operands)
                self.assertTrue(is_valid, f"Failed for {opcode} {operands}: {msg}")

    def test_poc_first_example(self):
        """Validate all instructions in the first PoC example (add_two_values.aml)."""
        poc_program = [
            ("LOAD", ["R1", "A"]),
            ("LOAD", ["R2", "B"]),
            ("ADD", ["R1", "R2"]),
            ("STORE", ["OUT", "R1"]),
            ("HALT", []),
        ]

        for opcode, operands in poc_program:
            is_valid, msg = validate_instruction_spec(opcode, operands)
            self.assertTrue(is_valid, f"PoC instruction '{opcode}' invalid: {msg}")

    def test_negative_invalid_opcodes(self):
        """Test rejection of unauthorized opcodes."""
        invalid_opcodes = ["DIV", "NOP", "AND", "OR", "XOR", "CALL", "RET", "PUSH", "POP"]
        for op in invalid_opcodes:
            is_valid, msg = validate_instruction_spec(op, ["R1"])
            self.assertFalse(is_valid)
            self.assertIn("Unknown or invalid AML opcode", msg)

    def test_negative_arity_mismatch(self):
        """Test rejection of wrong operand count."""
        invalid_arity = [
            ("LOAD", ["R1"]),               # expects 2
            ("LOAD", ["R1", "A", "EXTRA"]), # expects 2
            ("HALT", ["R1"]),               # expects 0
            ("JMP", []),                    # expects 1
            ("ADD", ["R1"]),                # expects 2
        ]

        for opcode, operands in invalid_arity:
            is_valid, msg = validate_instruction_spec(opcode, operands)
            self.assertFalse(is_valid)
            self.assertIn("expects", msg)

    def test_negative_operand_type_mismatch(self):
        """Test rejection of invalid operand types or register names."""
        invalid_types = [
            ("STORE", ["123", "R1"]),      # STORE dst must be memory label/address, not immediate
            ("LOAD", ["100", "A"]),         # LOAD dst must be register, not immediate
            ("ADD", ["A", "R1"]),           # ADD dst must be register, not memory label
            ("MOV", ["R99", "R1"]),         # R99 is not a valid register (R0..R15)
        ]

        for opcode, operands in invalid_types:
            is_valid, msg = validate_instruction_spec(opcode, operands)
            self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
