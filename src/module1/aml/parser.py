"""
AML v0.1 Parser: Classical Source Text -> AML-IR (AMLProgram).

Strictly compliant with Stage 4 requirements (main-technical-refference.md Section 25).
"""

from dataclasses import dataclass, field
import hashlib
from typing import Dict, List, Optional, Set

from .spec import Opcode, validate_instruction_spec, detect_operand_type, OperandType
from .grammar import TokenType, Token, tokenize_line, validate_line_grammar


class ParseError(Exception):
    """Exception raised when AML parsing fails."""
    def __init__(self, line_number: int, message: str):
        self.line_number = line_number
        self.message = message
        super().__init__(f"Line {line_number}: {message}")


@dataclass(frozen=True)
class AMLInstruction:
    """Represents a single executable instruction in AML-IR."""
    line_number: int
    pc: int
    label: Optional[str]
    opcode: Opcode
    operands: List[str]


@dataclass
class AMLProgram:
    """Represents a complete parsed AML program in AML-IR."""
    instructions: List[AMLInstruction] = field(default_factory=list)
    label_table: Dict[str, int] = field(default_factory=dict)
    symbol_table: Set[str] = field(default_factory=set)
    source_hash: str = ""


def parse_aml_source(source_text: str) -> AMLProgram:
    """
    Parse multi-line AML source code text into structured AML-IR (AMLProgram).

    Args:
        source_text: Raw AML source text

    Returns:
        AMLProgram (AML-IR data structure)

    Raises:
        ParseError: If syntax, grammar, or specification errors occur.
    """
    # Calculate deterministic source hash
    normalized_source = source_text.strip().encode("utf-8")
    source_hash = hashlib.sha256(normalized_source).hexdigest()

    lines = source_text.splitlines()
    
    # intermediate line representations
    raw_lines_tokens: List[tuple[int, List[Token]]] = []
    label_table: Dict[str, int] = {}
    symbol_table: Set[str] = set()
    current_pc = 0

    # Pass 1 & 2: Tokenize, validate line grammar, and register labels
    for line_idx, line in enumerate(lines, start=1):
        tokens, lex_err = tokenize_line(line)
        if lex_err:
            raise ParseError(line_idx, lex_err)

        # Ignore empty/comment lines
        code_tokens = [t for t in tokens if t.token_type != TokenType.COMMENT]
        if not code_tokens:
            continue

        is_valid_gram, gram_err = validate_line_grammar(tokens)
        if not is_valid_gram:
            raise ParseError(line_idx, gram_err or "Line grammar error")

        # Check for Label Declaration
        pending_label: Optional[str] = None
        start_token_idx = 0

        if code_tokens[0].token_type == TokenType.LABEL_DECL:
            label_name = code_tokens[0].value[:-1]  # remove trailing ':'
            if label_name in label_table:
                raise ParseError(line_idx, f"Duplicate label declaration '{label_name}'")
            label_table[label_name] = current_pc
            pending_label = label_name
            start_token_idx = 1

        # If line contains an opcode
        if start_token_idx < len(code_tokens):
            raw_lines_tokens.append((line_idx, pending_label, current_pc, code_tokens[start_token_idx:]))
            current_pc += 1

    # Pass 3: Opcode Specification Validation & AML-IR Assembly
    instructions: List[AMLInstruction] = []

    for line_idx, pending_label, pc, instruction_tokens in raw_lines_tokens:
        opcode_token = instruction_tokens[0]
        opcode_enum = Opcode(opcode_token.value)

        # Extract operands
        operands = [t.value for t in instruction_tokens[1:] if t.token_type != TokenType.COMMA]

        # Validate instruction specification
        is_valid_spec, spec_err = validate_instruction_spec(opcode_token.value, operands)
        if not is_valid_spec:
            raise ParseError(line_idx, spec_err)

        # Collect symbolic memory locations referenced
        for op in operands:
            if detect_operand_type(op) == OperandType.LABEL_OR_ADDRESS and op not in label_table:
                symbol_table.add(op)

        instruction_ir = AMLInstruction(
            line_number=line_idx,
            pc=pc,
            label=pending_label,
            opcode=opcode_enum,
            operands=operands,
        )
        instructions.append(instruction_ir)

    return AMLProgram(
        instructions=instructions,
        label_table=label_table,
        symbol_table=symbol_table,
        source_hash=source_hash,
    )
