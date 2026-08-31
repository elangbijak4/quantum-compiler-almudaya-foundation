"""
Stage 2 Unit Tests: AML v0.1 Textual Grammar & Lexical Rules.

Strictly verifies Stage 2 compliance per main-technical-refference.md.
"""

import unittest
from src.module1.aml.grammar import (
    TokenType,
    Token,
    tokenize_line,
    validate_line_grammar,
)


class TestStage2AMLGrammar(unittest.TestCase):
    """Test suite for Stage 2 AML v0.1 textual grammar tokenization and validation."""

    def test_lexical_tokenization_tokens(self):
        """Test tokenization of basic lexical token types."""
        line = "LOOP: LOAD R1, A # Load variable A"
        tokens, err = tokenize_line(line)
        self.assertIsNone(err)
        self.assertEqual(len(tokens), 6)

        self.assertEqual(tokens[0].token_type, TokenType.LABEL_DECL)
        self.assertEqual(tokens[0].value, "LOOP:")

        self.assertEqual(tokens[1].token_type, TokenType.OPCODE)
        self.assertEqual(tokens[1].value, "LOAD")

        self.assertEqual(tokens[2].token_type, TokenType.REGISTER)
        self.assertEqual(tokens[2].value, "R1")

        self.assertEqual(tokens[3].token_type, TokenType.COMMA)

        self.assertEqual(tokens[4].token_type, TokenType.SYMBOL)
        self.assertEqual(tokens[4].value, "A")

        self.assertEqual(tokens[5].token_type, TokenType.COMMENT)
        self.assertEqual(tokens[5].value, "# Load variable A")

    def test_line_grammar_validation_positive(self):
        """Test valid EBNF line grammar structures."""
        valid_lines = [
            "LOAD R1, A",
            "LOAD R2, 100",
            "STORE OUT, R1",
            "MOV R1, R2",
            "ADD R1, 5",
            "HALT",
            "START: HALT",
            "LOOP:",
            "  # Just a comment",
            "ADD R1, R2 # Inline comment",
        ]

        for line in valid_lines:
            with self.subTest(line=line):
                tokens, lex_err = tokenize_line(line)
                self.assertIsNone(lex_err, f"Lexical error on line '{line}': {lex_err}")
                is_valid, gram_err = validate_line_grammar(tokens)
                self.assertTrue(is_valid, f"Grammar error on line '{line}': {gram_err}")

    def test_poc_file_lines(self):
        """Test tokenization and line grammar for add_two_values.aml lines."""
        poc_lines = [
            "# Module 1 first PoC",
            "# Expected OUT = 12 when A = 5 and B = 7",
            "LOAD R1, A",
            "LOAD R2, B",
            "ADD  R1, R2",
            "STORE OUT, R1",
            "HALT",
        ]

        for line in poc_lines:
            tokens, lex_err = tokenize_line(line)
            self.assertIsNone(lex_err)
            is_valid, gram_err = validate_line_grammar(tokens)
            self.assertTrue(is_valid)

    def test_line_grammar_validation_negative(self):
        """Test detection of syntax/grammar violations."""
        invalid_lines = [
            "LOAD R1 A",          # Missing comma between operands
            "ADD R1, R2,",        # Trailing comma
            "123LABEL: HALT",     # Invalid label declaration syntax
            "LOAD R1, R2, R3",    # Extra comma without operand
        ]

        for line in invalid_lines:
            with self.subTest(line=line):
                tokens, lex_err = tokenize_line(line)
                if lex_err is None:
                    is_valid, gram_err = validate_line_grammar(tokens)
                    self.assertFalse(is_valid, f"Line '{line}' should have failed grammar check")


if __name__ == "__main__":
    unittest.main()
