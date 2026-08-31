"""
AML v0.1 Formal Operational Semantics S = (PC, R, M, F) and Transition Primitives.

Strictly compliant with Stage 3 requirements (main-technical-refference.md Section 5 & 25).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from .spec import Opcode, REGISTER_NAMES, validate_instruction_spec, detect_operand_type, OperandType


@dataclass
class Flags:
    """Status flags and execution state for AML machine."""
    zero: bool = False
    halted: bool = False
    error: Optional[str] = None


@dataclass
class AMLState:
    """
    Formal AML machine operational state tuple:
    S = (PC, R, M, F)
    """
    pc: int = 0
    registers: Dict[str, int] = field(default_factory=lambda: {r: 0 for r in REGISTER_NAMES})
    memory: Dict[str, int] = field(default_factory=dict)
    flags: Flags = field(default_factory=Flags)

    def copy(self) -> "AMLState":
        """Return a deep copy of the current state."""
        return AMLState(
            pc=self.pc,
            registers=dict(self.registers),
            memory=dict(self.memory),
            flags=Flags(
                zero=self.flags.zero,
                halted=self.flags.halted,
                error=self.flags.error,
            ),
        )


def resolve_value(state: AMLState, token: str) -> int:
    """
    Resolve value of an operand token in the current state.
    - If register -> return R[reg]
    - If immediate -> return int(token)
    - If memory symbol -> return M[symbol] (or 0 if uninitialized)
    """
    clean_token = token.strip()
    opt_type = detect_operand_type(clean_token)

    if opt_type == OperandType.REGISTER:
        return state.registers.get(clean_token.upper(), 0)

    if opt_type == OperandType.IMMEDIATE:
        return int(clean_token)

    if opt_type == OperandType.LABEL_OR_ADDRESS:
        return state.memory.get(clean_token, 0)

    raise ValueError(f"Cannot resolve operand value for token '{token}'")


def step_operational_semantics(
    state: AMLState,
    opcode_str: str,
    operands: List[str],
    label_table: Optional[Dict[str, int]] = None
) -> AMLState:
    """
    Compute small-step operational transition <I, S> -> S' for an AML instruction.

    Args:
        state: Current machine state S = (PC, R, M, F)
        opcode_str: Instruction opcode string
        operands: List of operand strings
        label_table: Optional mapping from label name to PC target line

    Returns:
        New machine state S'
    """
    if state.flags.halted:
        return state.copy()

    # Validate against Stage 1 specification
    is_valid, err_msg = validate_instruction_spec(opcode_str, operands)
    if not is_valid:
        new_state = state.copy()
        new_state.flags.error = err_msg
        return new_state

    opcode_enum = Opcode(opcode_str.strip().upper())
    new_state = state.copy()

    # 1. HALT
    if opcode_enum == Opcode.HALT:
        new_state.flags.halted = True
        return new_state

    # 2. LOAD
    if opcode_enum == Opcode.LOAD:
        dst_reg = operands[0].strip().upper()
        src_val = resolve_value(state, operands[1])
        new_state.registers[dst_reg] = src_val
        new_state.pc += 1
        return new_state

    # 3. STORE
    if opcode_enum == Opcode.STORE:
        dst_mem = operands[0].strip()
        src_val = resolve_value(state, operands[1])
        new_state.memory[dst_mem] = src_val
        new_state.pc += 1
        return new_state

    # 4. MOV
    if opcode_enum == Opcode.MOV:
        dst_reg = operands[0].strip().upper()
        src_val = resolve_value(state, operands[1])
        new_state.registers[dst_reg] = src_val
        new_state.pc += 1
        return new_state

    # 5. ADD
    if opcode_enum == Opcode.ADD:
        dst_reg = operands[0].strip().upper()
        src_val = resolve_value(state, operands[1])
        new_state.registers[dst_reg] = state.registers[dst_reg] + src_val
        new_state.pc += 1
        return new_state

    # 6. SUB
    if opcode_enum == Opcode.SUB:
        dst_reg = operands[0].strip().upper()
        src_val = resolve_value(state, operands[1])
        new_state.registers[dst_reg] = state.registers[dst_reg] - src_val
        new_state.pc += 1
        return new_state

    # 7. MUL
    if opcode_enum == Opcode.MUL:
        dst_reg = operands[0].strip().upper()
        src_val = resolve_value(state, operands[1])
        new_state.registers[dst_reg] = state.registers[dst_reg] * src_val
        new_state.pc += 1
        return new_state

    # 8. CMP
    if opcode_enum == Opcode.CMP:
        reg1_val = state.registers[operands[0].strip().upper()]
        reg2_val = resolve_value(state, operands[1])
        new_state.flags.zero = (reg1_val == reg2_val)
        new_state.pc += 1
        return new_state

    # Helper for resolving jump target
    def resolve_jump_target(target_str: str) -> int:
        clean_target = target_str.strip()
        if detect_operand_type(clean_target) == OperandType.IMMEDIATE:
            return int(clean_target)
        if label_table and clean_target in label_table:
            return label_table[clean_target]
        # Default fallback to int or memory value
        return state.memory.get(clean_target, 0)

    # 9. JMP
    if opcode_enum == Opcode.JMP:
        new_state.pc = resolve_jump_target(operands[0])
        return new_state

    # 10. JZ
    if opcode_enum == Opcode.JZ:
        if state.flags.zero:
            new_state.pc = resolve_jump_target(operands[0])
        else:
            new_state.pc += 1
        return new_state

    # 11. JNZ
    if opcode_enum == Opcode.JNZ:
        if not state.flags.zero:
            new_state.pc = resolve_jump_target(operands[0])
        else:
            new_state.pc += 1
        return new_state

    return new_state
