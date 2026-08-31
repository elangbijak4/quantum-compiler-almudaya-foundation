"""
AML (Algorithmic Machine Language) Module.
"""

from .spec import (
    Opcode,
    OperandType,
    InstructionSpec,
    REGISTER_NAMES,
    VALID_INSTRUCTIONS,
    validate_instruction_spec,
    detect_operand_type,
)

from .grammar import (
    TokenType,
    Token,
    tokenize_line,
    validate_line_grammar,
)

from .semantics import (
    Flags,
    AMLState,
    resolve_value,
    step_operational_semantics,
)

from .parser import (
    ParseError,
    AMLInstruction,
    AMLProgram,
    parse_aml_source,
)

from .interpreter import (
    AMLInterpreterResult,
    AMLInterpreter,
    execute_aml_source,
)

__all__ = [
    "Opcode",
    "OperandType",
    "InstructionSpec",
    "REGISTER_NAMES",
    "VALID_INSTRUCTIONS",
    "validate_instruction_spec",
    "detect_operand_type",
    "TokenType",
    "Token",
    "tokenize_line",
    "validate_line_grammar",
    "Flags",
    "AMLState",
    "resolve_value",
    "step_operational_semantics",
    "ParseError",
    "AMLInstruction",
    "AMLProgram",
    "parse_aml_source",
    "AMLInterpreterResult",
    "AMLInterpreter",
    "execute_aml_source",
]
