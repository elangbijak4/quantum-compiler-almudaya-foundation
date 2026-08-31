"""
AML v0.1 Textual Grammar & Lexical Tokenization Primitives.

Strictly compliant with Stage 2 requirements (main-technical-refference.md Section 25).
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Optional
import re

from .spec import Opcode, REGISTER_NAMES, SYMBOLIC_LABEL_PATTERN, VALID_INSTRUCTIONS


class TokenType(Enum):
    """Lexical token types for AML v0.1 grammar."""
    LABEL_DECL = auto()  # e.g. "START:"
    OPCODE = auto()      # e.g. "LOAD"
    REGISTER = auto()    # e.g. "R1"
    IMMEDIATE = auto()   # e.g. "5", "-10"
    SYMBOL = auto()      # e.g. "A", "VAR_1"
    COMMA = auto()       # ","
    COMMENT = auto()     # "# comment"


@dataclass(frozen=True)
class Token:
    """Represents a single lexical token in AML source."""
    token_type: TokenType
    value: str
    column: int


def tokenize_line(line_text: str) -> Tuple[List[Token], Optional[str]]:
    """
    Tokenize a single line of AML text into a list of Lexical Tokens according to
    Stage 2 EBNF grammar rules.

    Returns:
        (tokens_list, error_message_if_any)
    """
    tokens: List[Token] = []
    
    # 1. Handle comment
    comment_idx = line_text.find("#")
    code_part = line_text if comment_idx == -1 else line_text[:comment_idx]
    comment_part = "" if comment_idx == -1 else line_text[comment_idx:]

    # Parse code tokens
    idx = 0
    length = len(code_part)

    while idx < length:
        ch = code_part[idx]

        # Skip whitespace
        if ch in (" ", "\t", "\r", "\n"):
            idx += 1
            continue

        # Handle comma
        if ch == ",":
            tokens.append(Token(TokenType.COMMA, ",", idx + 1))
            idx += 1
            continue

        # Extract word / atom
        start_col = idx + 1
        atom_chars = []
        while idx < length and code_part[idx] not in (" ", "\t", "\r", "\n", ",", "#"):
            atom_chars.append(code_part[idx])
            idx += 1

        atom = "".join(atom_chars)
        if not atom:
            continue

        # Classify atom
        # 1. Label declaration (ends with ':')
        if atom.endswith(":"):
            label_name = atom[:-1]
            if not SYMBOLIC_LABEL_PATTERN.match(label_name):
                return [], f"Invalid label declaration syntax '{atom}' at column {start_col}"
            tokens.append(Token(TokenType.LABEL_DECL, atom, start_col))
            continue

        # 2. Register
        if atom.upper() in REGISTER_NAMES:
            tokens.append(Token(TokenType.REGISTER, atom.upper(), start_col))
            continue

        # 3. Opcode
        try:
            op_enum = Opcode(atom.upper())
            tokens.append(Token(TokenType.OPCODE, op_enum.value, start_col))
            continue
        except ValueError:
            pass

        # 4. Immediate integer
        try:
            int(atom)
            tokens.append(Token(TokenType.IMMEDIATE, atom, start_col))
            continue
        except ValueError:
            pass

        # 5. Symbolic identifier
        if SYMBOLIC_LABEL_PATTERN.match(atom):
            tokens.append(Token(TokenType.SYMBOL, atom, start_col))
            continue

        # Unrecognized lexical token
        return [], f"Lexical error: Unrecognized token '{atom}' at column {start_col}"

    # Add comment token if present
    if comment_part:
        tokens.append(Token(TokenType.COMMENT, comment_part.strip(), comment_idx + 1))

    return tokens, None


def validate_line_grammar(tokens: List[Token]) -> Tuple[bool, Optional[str]]:
    """
    Validate line-level EBNF grammar structure for a list of tokens on a single line.

    Rule: [LABEL_DECL] [OPCODE [OPERAND (COMMA OPERAND)*]] [COMMENT]
    Also validates opcode arity match against Stage 1 specification.
    """
    # Filter out comments for structural checking
    code_tokens = [t for t in tokens if t.token_type != TokenType.COMMENT]
    if not code_tokens:
        return True, None  # Empty or comment-only line is valid

    cursor = 0
    # Optional Label Declaration
    if code_tokens[cursor].token_type == TokenType.LABEL_DECL:
        cursor += 1
        if cursor == len(code_tokens):
            return True, None  # Label-only line is valid

    # Opcode check
    if cursor >= len(code_tokens) or code_tokens[cursor].token_type != TokenType.OPCODE:
        bad_token = code_tokens[cursor].value if cursor < len(code_tokens) else "EOF"
        return False, f"Expected Opcode or Label Declaration, got '{bad_token}'"

    opcode_token = code_tokens[cursor]
    opcode_enum = Opcode(opcode_token.value)
    spec = VALID_INSTRUCTIONS[opcode_enum]
    cursor += 1

    # Check for trailing comma at line end
    if code_tokens[-1].token_type == TokenType.COMMA:
        return False, f"Trailing comma at end of line in instruction '{opcode_token.value}'"

    # Collect operands
    operand_tokens: List[Token] = []
    expect_operand = True

    while cursor < len(code_tokens):
        t = code_tokens[cursor]
        if expect_operand:
            if t.token_type not in (TokenType.REGISTER, TokenType.IMMEDIATE, TokenType.SYMBOL):
                return False, f"Expected operand, got '{t.value}' at column {t.column}"
            operand_tokens.append(t)
            expect_operand = False
        else:
            if t.token_type != TokenType.COMMA:
                return False, f"Expected ',' between operands, got '{t.value}' at column {t.column}"
            expect_operand = True
        cursor += 1

    if expect_operand and len(code_tokens) > 1 and code_tokens[-1].token_type == TokenType.COMMA:
        return False, "Trailing comma at end of instruction"

    # Check arity against Stage 1 specification
    if len(operand_tokens) != spec.arity:
        return (
            False,
            f"Instruction '{opcode_token.value}' expects {spec.arity} operand(s), "
            f"got {len(operand_tokens)}"
        )

    return True, None
