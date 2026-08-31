"""
AML State Encoding E: AMLState -> UTMConfiguration & Tape Layout Specification.

Strictly compliant with Stage 7 requirements (main-technical-refference.md & STAGE_7_AML_TO_UTM.md).
"""

from typing import Dict
from ..aml.semantics import AMLState, Flags
from ..aml.spec import REGISTER_NAMES
from ..utm.model import UTMConfiguration

# Tape Layout Markers
TAPE_START_MARKER = "^"
TAPE_PC_MARKER = "PC"
TAPE_ZERO_FLAG_MARKER = "FLAG_ZERO"
TAPE_HALT_FLAG_MARKER = "FLAG_HALT"
TAPE_SECTION_DELIMITER = "|"
TAPE_MEM_MARKER = "MEM"

# Fixed Cell Indices
POS_START = 0
POS_PC_LABEL = 1
POS_PC_VAL = 2
POS_ZERO_LABEL = 3
POS_ZERO_VAL = 4
POS_HALT_LABEL = 5
POS_HALT_VAL = 6
POS_DELIM1 = 7
POS_REG_START = 8  # Cells 8 to 39 for R0..R15
POS_DELIM2 = 40
POS_MEM_LABEL = 41
POS_MEM_START = 42


def get_register_val_cell(reg_name: str) -> int:
    """Get tape cell index for a register value (e.g. 'R0' -> 9, 'R1' -> 11)."""
    reg_idx = int(reg_name.strip().upper()[1:])
    return POS_REG_START + (reg_idx * 2) + 1


def get_register_label_cell(reg_name: str) -> int:
    """Get tape cell index for a register label (e.g. 'R0' -> 8, 'R1' -> 10)."""
    reg_idx = int(reg_name.strip().upper()[1:])
    return POS_REG_START + (reg_idx * 2)


def encode_aml_state(state: AMLState) -> UTMConfiguration:
    """
    Encode an AML machine state S = (PC, R, M, F) into a deterministic UTMConfiguration.

    Args:
        state: Source AMLState

    Returns:
        Encoded UTMConfiguration with populated tape dictionary.
    """
    tape: Dict[int, str] = {}

    # 1. Header Metadata Section
    tape[POS_START] = TAPE_START_MARKER
    tape[POS_PC_LABEL] = TAPE_PC_MARKER
    tape[POS_PC_VAL] = str(state.pc)
    tape[POS_ZERO_LABEL] = TAPE_ZERO_FLAG_MARKER
    tape[POS_ZERO_VAL] = "1" if state.flags.zero else "0"
    tape[POS_HALT_LABEL] = TAPE_HALT_FLAG_MARKER
    tape[POS_HALT_VAL] = "1" if state.flags.halted else "0"
    tape[POS_DELIM1] = TAPE_SECTION_DELIMITER

    # 2. Register Section (R0..R15)
    for i in range(16):
        reg_name = f"R{i}"
        lbl_idx = POS_REG_START + (i * 2)
        val_idx = lbl_idx + 1
        tape[lbl_idx] = reg_name
        tape[val_idx] = str(state.registers.get(reg_name, 0))

    tape[POS_DELIM2] = TAPE_SECTION_DELIMITER
    tape[POS_MEM_LABEL] = TAPE_MEM_MARKER

    # 3. Memory Section (Sorted deterministic key order)
    sorted_mem_keys = sorted(state.memory.keys())
    for k_idx, mem_key in enumerate(sorted_mem_keys):
        k_cell = POS_MEM_START + (k_idx * 2)
        v_cell = k_cell + 1
        tape[k_cell] = str(mem_key)
        tape[v_cell] = str(state.memory[mem_key])

    # Initial state determination
    current_state = "q_halt" if state.flags.halted else f"q_instr_{state.pc}_start"

    return UTMConfiguration(
        current_state=current_state,
        tape=tape,
        head_pos=0,
        step_count=0,
        halted=state.flags.halted,
        error=state.flags.error,
    )


def decode_aml_state(config: UTMConfiguration) -> AMLState:
    """
    Decode a UTMConfiguration tape back into an AMLState S = (PC, R, M, F).

    Args:
        config: Encoded UTMConfiguration

    Returns:
        Reconstructed AMLState
    """
    pc = int(config.tape.get(POS_PC_VAL, "0"))
    zero_flag = (config.tape.get(POS_ZERO_VAL, "0") == "1")
    halt_flag = (config.tape.get(POS_HALT_VAL, "0") == "1") or config.halted

    flags = Flags(zero=zero_flag, halted=halt_flag, error=config.error)

    # Decode registers
    registers: Dict[str, int] = {}
    for i in range(16):
        reg_name = f"R{i}"
        val_idx = POS_REG_START + (i * 2) + 1
        registers[reg_name] = int(config.tape.get(val_idx, "0"))

    # Decode memory section
    memory: Dict[str, int] = {}
    idx = POS_MEM_START
    while idx in config.tape and (idx + 1) in config.tape:
        mem_key = config.tape[idx]
        mem_val = int(config.tape[idx + 1])
        memory[mem_key] = mem_val
        idx += 2

    return AMLState(
        pc=pc,
        registers=registers,
        memory=memory,
        flags=flags,
    )
