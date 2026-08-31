"""
AML v0.1 Formal Specification Data Structures and Stage 1 Validation Primitives.

Strictly compliant with Stage 1 requirements (main-technical-refference.md Section 25).
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Set, Optional
import re


class Opcode(Enum):
    """AML v0.1 valid opcodes (11 instructions)."""
    # Data Movement
    LOAD = "LOAD"
    STORE = "STORE"
    MOV = "MOV"

    # Arithmetic & Logic
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    CMP = "CMP"

    # Control Flow
    JMP = "JMP"
    JZ = "JZ"
    JNZ = "JNZ"

    # Control
    HALT = "HALT"


class OperandType(Enum):
    """Allowed AML operand categories."""
    REGISTER = auto()
    IMMEDIATE = auto()
    LABEL_OR_ADDRESS = auto()


# 16 General Purpose Registers R0..R15
REGISTER_NAMES: Set[str] = {f"R{i}" for i in range(16)}

# Pattern for valid symbolic memory labels or addresses
SYMBOLIC_LABEL_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


@dataclass(frozen=True)
class InstructionSpec:
    """Specification signature for an AML instruction opcode."""
    opcode: Opcode
    arity: int
    allowed_operand_types: Tuple[Set[OperandType], ...]
    description: str


# Operational signature matrix for AML v0.1
VALID_INSTRUCTIONS: dict[Opcode, InstructionSpec] = {
    Opcode.LOAD: InstructionSpec(
        opcode=Opcode.LOAD,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.LABEL_OR_ADDRESS, OperandType.IMMEDIATE},
        ),
        description="Load memory or immediate into target register",
    ),
    Opcode.STORE: InstructionSpec(
        opcode=Opcode.STORE,
        arity=2,
        allowed_operand_types=(
            {OperandType.LABEL_OR_ADDRESS},
            {OperandType.REGISTER},
        ),
        description="Store source register into target memory label",
    ),
    Opcode.MOV: InstructionSpec(
        opcode=Opcode.MOV,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.REGISTER, OperandType.IMMEDIATE},
        ),
        description="Copy register or immediate to destination register",
    ),
    Opcode.ADD: InstructionSpec(
        opcode=Opcode.ADD,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.REGISTER, OperandType.IMMEDIATE},
        ),
        description="Add operand 2 to operand 1",
    ),
    Opcode.SUB: InstructionSpec(
        opcode=Opcode.SUB,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.REGISTER, OperandType.IMMEDIATE},
        ),
        description="Subtract operand 2 from operand 1",
    ),
    Opcode.MUL: InstructionSpec(
        opcode=Opcode.MUL,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.REGISTER, OperandType.IMMEDIATE},
        ),
        description="Multiply operand 1 by operand 2",
    ),
    Opcode.CMP: InstructionSpec(
        opcode=Opcode.CMP,
        arity=2,
        allowed_operand_types=(
            {OperandType.REGISTER},
            {OperandType.REGISTER, OperandType.IMMEDIATE},
        ),
        description="Compare operand 1 and operand 2",
    ),
    Opcode.JMP: InstructionSpec(
        opcode=Opcode.JMP,
        arity=1,
        allowed_operand_types=(
            {OperandType.LABEL_OR_ADDRESS, OperandType.IMMEDIATE},
        ),
        description="Unconditional jump to target",
    ),
    Opcode.JZ: InstructionSpec(
        opcode=Opcode.JZ,
        arity=1,
        allowed_operand_types=(
            {OperandType.LABEL_OR_ADDRESS, OperandType.IMMEDIATE},
        ),
        description="Jump if zero flag set",
    ),
    Opcode.JNZ: InstructionSpec(
        opcode=Opcode.JNZ,
        arity=1,
        allowed_operand_types=(
            {OperandType.LABEL_OR_ADDRESS, OperandType.IMMEDIATE},
        ),
        description="Jump if zero flag not set",
    ),
    Opcode.HALT: InstructionSpec(
        opcode=Opcode.HALT,
        arity=0,
        allowed_operand_types=(),
        description="Halt program execution",
    ),
}


def detect_operand_type(token: str) -> Optional[OperandType]:
    """
    Detect the operand category of a token string at Stage 1 specification level.
    """
    clean_token = token.strip()
    if not clean_token:
        return None

    # Register check
    if clean_token.upper() in REGISTER_NAMES:
        return OperandType.REGISTER

    # Immediate integer check
    try:
        int(clean_token)
        return OperandType.IMMEDIATE
    except ValueError:
        pass

    # Symbolic label / memory location check
    if SYMBOLIC_LABEL_PATTERN.match(clean_token):
        return OperandType.LABEL_OR_ADDRESS

    return None


def validate_instruction_spec(opcode_str: str, operands: List[str]) -> Tuple[bool, str]:
    """
    Validate opcode and operands against AML v0.1 Stage 1 specification.
    
    Returns:
        (is_valid, error_message)
    """
    clean_opcode = opcode_str.strip().upper()
    
    # 1. Opcode validity check
    try:
        opcode_enum = Opcode(clean_opcode)
    except ValueError:
        return False, f"Unknown or invalid AML opcode: '{opcode_str}'"

    spec = VALID_INSTRUCTIONS[opcode_enum]

    # 2. Arity check
    if len(operands) != spec.arity:
        return (
            False,
            f"Instruction '{clean_opcode}' expects {spec.arity} operand(s), "
            f"but got {len(operands)}"
        )

    # 3. Operand type validity check
    for idx, (operand_token, allowed_types) in enumerate(zip(operands, spec.allowed_operand_types)):
        detected_type = detect_operand_type(operand_token)
        if detected_type is None:
            return False, f"Invalid operand token '{operand_token}' at position {idx + 1}"
        if detected_type not in allowed_types:
            allowed_str = ", ".join(t.name for t in allowed_types)
            return (
                False,
                f"Operand '{operand_token}' at position {idx + 1} for '{clean_opcode}' "
                f"is of type {detected_type.name}, expected one of [{allowed_str}]"
            )

    return True, "Valid AML instruction specification"
