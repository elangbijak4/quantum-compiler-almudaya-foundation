"""
AML-IR to UTM-IR Translator T: AMLProgram -> UTMProgram.

Strictly compliant with Stage 7 requirements (main-technical-refference.md & STAGE_7_AML_TO_UTM.md).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from ..aml.parser import AMLProgram, AMLInstruction
from ..aml.spec import Opcode, detect_operand_type, OperandType
from ..utm.model import (
    Direction,
    TransitionAction,
    UTMProgram,
    validate_utm_program,
)
from .encoder import (
    TAPE_START_MARKER,
    TAPE_PC_MARKER,
    TAPE_ZERO_FLAG_MARKER,
    TAPE_HALT_FLAG_MARKER,
    TAPE_SECTION_DELIMITER,
    TAPE_MEM_MARKER,
    POS_START,
    POS_PC_VAL,
    POS_ZERO_VAL,
    POS_HALT_VAL,
    POS_REG_START,
    POS_MEM_START,
    get_register_val_cell,
)


@dataclass
class TranslationResult:
    """Represents the complete result of AML-IR -> UTM-IR translation."""
    utm_program: Optional[UTMProgram]
    status: str  # "TRANSLATION_GENERATED", "ERROR"
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


def translate_aml_to_utm(program: AMLProgram) -> TranslationResult:
    """
    Translate an AMLProgram (AML-IR) into a valid UTMProgram (UTM-IR).

    Args:
        program: Parsed AMLProgram (AML-IR)

    Returns:
        TranslationResult
    """
    if not program or not program.instructions:
        return TranslationResult(
            utm_program=None,
            status="ERROR",
            error="Cannot translate empty or null AML program",
        )

    # Build tape alphabet
    alphabet: Set[str] = {
        TAPE_START_MARKER,
        TAPE_PC_MARKER,
        TAPE_ZERO_FLAG_MARKER,
        TAPE_HALT_FLAG_MARKER,
        TAPE_SECTION_DELIMITER,
        TAPE_MEM_MARKER,
        "0",
        "1",
        "_",
    }

    for i in range(16):
        alphabet.add(f"R{i}")

    sorted_mem_symbols = sorted(list(program.symbol_table))
    mem_symbol_to_cell: Dict[str, int] = {}
    for idx, sym in enumerate(sorted_mem_symbols):
        alphabet.add(str(sym))
        mem_symbol_to_cell[sym] = POS_MEM_START + (idx * 2) + 1

    for instr in program.instructions:
        for op in instr.operands:
            clean_op = str(op).strip()
            alphabet.add(clean_op)

    # Pre-add standard small numeric literals (0..15)
    for n in range(16):
        alphabet.add(str(n))

    states: Set[str] = {"q_start", "q_halt"}
    transitions: Dict[Tuple[str, str], TransitionAction] = {}
    total_instructions = len(program.instructions)

    def add_state(s_name: str):
        states.add(s_name)

    # Alias q_start to q_instr_0_start
    transitions[("q_start", "_")] = TransitionAction(
        next_state="q_instr_0_start",
        write_symbol="_",
        direction=Direction.STAY,
    )

    def get_jump_target_pc(target_str: str) -> int:
        clean_t = target_str.strip()
        if clean_t in program.label_table:
            return program.label_table[clean_t]
        try:
            return int(clean_t)
        except ValueError:
            return 0

    def get_value_symbols() -> List[str]:
        return [s for s in list(alphabet) if s == "_" or s.lstrip('-').isdigit()]

    # Helper: navigate head from current_pos to target_cell
    def make_nav_chain(from_state: str, target_cell: int, prefix: str) -> str:
        curr = from_state
        for step in range(target_cell):
            st_next = f"{prefix}_nav_{step+1}"
            add_state(st_next)
            transitions[(curr, "_")] = TransitionAction(
                next_state=st_next,
                write_symbol="_",
                direction=Direction.RIGHT,
            )
            curr = st_next
        return curr

    # Helper: navigate head from target_cell back to 0
    def make_nav_back_chain(from_state: str, current_cell: int, final_next_state: str, prefix: str):
        curr = from_state
        for step in range(current_cell, 0, -1):
            st_next = f"{prefix}_back_{step-1}" if step - 1 > 0 else final_next_state
            if step - 1 > 0:
                add_state(st_next)
            transitions[(curr, "_")] = TransitionAction(
                next_state=st_next,
                write_symbol="_",
                direction=Direction.LEFT,
            )
            curr = st_next

    # Helper: write static symbol to target_cell
    def build_static_write_chain(curr_state: str, next_state: str, target_cell: int, write_symbol: str, instr_idx: int):
        prefix = f"q_i{instr_idx}_w"
        at_cell_state = make_nav_chain(curr_state, target_cell, prefix)

        written_state = f"{prefix}_written"
        add_state(written_state)

        alphabet.add(str(write_symbol))
        transitions[(at_cell_state, "_")] = TransitionAction(
            next_state=written_state,
            write_symbol=str(write_symbol),
            direction=Direction.STAY,
        )

        make_nav_back_chain(written_state, target_cell, next_state, prefix)

    # Helper: read cell A and copy value to cell B
    def build_copy_cell_chain(curr_state: str, next_state: str, src_cell: int, dst_cell: int, instr_idx: int):
        prefix = f"q_i{instr_idx}_cpy"
        at_src_state = make_nav_chain(curr_state, src_cell, prefix)
        val_syms = get_value_symbols()

        for sym in val_syms:
            read_st = f"{prefix}_rd_{sym}"
            add_state(read_st)
            transitions[(at_src_state, sym)] = TransitionAction(
                next_state=read_st,
                write_symbol=sym,
                direction=Direction.STAY,
            )

            if dst_cell >= src_cell:
                curr_n = read_st
                for step in range(src_cell, dst_cell):
                    nxt_n = f"{prefix}_rd_{sym}_to_{step+1}"
                    add_state(nxt_n)
                    transitions[(curr_n, "_")] = TransitionAction(
                        next_state=nxt_n,
                        write_symbol="_",
                        direction=Direction.RIGHT,
                    )
                    curr_n = nxt_n
                at_dst_state = curr_n
            else:
                curr_n = read_st
                for step in range(src_cell, dst_cell, -1):
                    nxt_n = f"{prefix}_rd_{sym}_to_{step-1}"
                    add_state(nxt_n)
                    transitions[(curr_n, "_")] = TransitionAction(
                        next_state=nxt_n,
                        write_symbol="_",
                        direction=Direction.LEFT,
                    )
                    curr_n = nxt_n
                at_dst_state = curr_n

            written_st = f"{prefix}_wr_{sym}"
            add_state(written_st)
            transitions[(at_dst_state, "_")] = TransitionAction(
                next_state=written_st,
                write_symbol=sym,
                direction=Direction.STAY,
            )

            make_nav_back_chain(written_st, dst_cell, next_state, f"{prefix}_b_{sym}")

    # Helper: Binary arithmetic on registers R_dst and R_src (ADD/SUB/MUL)
    def build_arithmetic_chain(curr_state: str, next_state: str, dst_cell: int, src_cell_or_val: Any, op_type: str, instr_idx: int):
        prefix = f"q_i{instr_idx}_arith"
        at_dst_state = make_nav_chain(curr_state, dst_cell, prefix)
        val_syms = get_value_symbols()

        for sym1 in val_syms:
            st1 = f"{prefix}_v1_{sym1}"
            add_state(st1)
            transitions[(at_dst_state, sym1)] = TransitionAction(
                next_state=st1,
                write_symbol=sym1,
                direction=Direction.STAY,
            )

            prefix_s1 = f"{prefix}_v1_{sym1}"

            if isinstance(src_cell_or_val, int):
                src_cell = src_cell_or_val
                if src_cell >= dst_cell:
                    curr_n = st1
                    for step in range(dst_cell, src_cell):
                        nxt_n = f"{prefix_s1}_to_{step+1}"
                        add_state(nxt_n)
                        transitions[(curr_n, "_")] = TransitionAction(
                            next_state=nxt_n, write_symbol="_", direction=Direction.RIGHT
                        )
                        curr_n = nxt_n
                    at_src_state = curr_n
                else:
                    curr_n = st1
                    for step in range(dst_cell, src_cell, -1):
                        nxt_n = f"{prefix_s1}_to_{step-1}"
                        add_state(nxt_n)
                        transitions[(curr_n, "_")] = TransitionAction(
                            next_state=nxt_n, write_symbol="_", direction=Direction.LEFT
                        )
                        curr_n = nxt_n
                    at_src_state = curr_n

                for sym2 in val_syms:
                    st2 = f"{prefix_s1}_v2_{sym2}"
                    add_state(st2)
                    transitions[(at_src_state, sym2)] = TransitionAction(
                        next_state=st2, write_symbol=sym2, direction=Direction.STAY
                    )

                    try:
                        i1, i2 = int(sym1), int(sym2)
                        if op_type == "ADD":
                            res_val = str(i1 + i2)
                        elif op_type == "SUB":
                            res_val = str(i1 - i2)
                        elif op_type == "MUL":
                            res_val = str(i1 * i2)
                        else:
                            res_val = str(i1)
                    except ValueError:
                        res_val = sym1

                    alphabet.add(res_val)

                    if dst_cell <= src_cell:
                        curr_n = st2
                        for step in range(src_cell, dst_cell, -1):
                            nxt_n = f"{prefix_s1}_c_{sym2}_b_{step-1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.LEFT
                            )
                            curr_n = nxt_n
                        wr_at_dst = curr_n
                    else:
                        curr_n = st2
                        for step in range(src_cell, dst_cell):
                            nxt_n = f"{prefix_s1}_c_{sym2}_f_{step+1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.RIGHT
                            )
                            curr_n = nxt_n
                        wr_at_dst = curr_n

                    wr_done_st = f"{prefix_s1}_wrdone_{sym2}"
                    add_state(wr_done_st)
                    transitions[(wr_at_dst, "_")] = TransitionAction(
                        next_state=wr_done_st, write_symbol=res_val, direction=Direction.STAY
                    )

                    make_nav_back_chain(wr_done_st, dst_cell, next_state, f"{prefix_s1}_fin_{sym2}")
            else:
                val2_str = str(src_cell_or_val)
                try:
                    i1, i2 = int(sym1), int(val2_str)
                    if op_type == "ADD":
                        res_val = str(i1 + i2)
                    elif op_type == "SUB":
                        res_val = str(i1 - i2)
                    elif op_type == "MUL":
                        res_val = str(i1 * i2)
                    else:
                        res_val = str(i1)
                except ValueError:
                    res_val = sym1

                alphabet.add(res_val)

                wr_done_st = f"{prefix_s1}_wrdone"
                add_state(wr_done_st)
                transitions[(st1, "_")] = TransitionAction(
                    next_state=wr_done_st, write_symbol=res_val, direction=Direction.STAY
                )

                make_nav_back_chain(wr_done_st, dst_cell, next_state, f"{prefix_s1}_fin")

    # Process all instructions
    for idx, instr in enumerate(program.instructions):
        curr_state = f"q_instr_{idx}_start"
        next_state = f"q_instr_{idx + 1}_start" if idx + 1 < total_instructions else "q_halt"
        add_state(curr_state)

        opcode = instr.opcode
        operands = instr.operands

        # 1. HALT
        if opcode == Opcode.HALT:
            build_static_write_chain(curr_state, "q_halt", POS_HALT_VAL, "1", idx)
            continue

        # 2. JMP
        if opcode == Opcode.JMP:
            target_pc = get_jump_target_pc(operands[0])
            target_state = f"q_instr_{target_pc}_start" if target_pc < total_instructions else "q_halt"
            build_static_write_chain(curr_state, target_state, POS_PC_VAL, str(target_pc), idx)
            continue

        # 3. JZ
        if opcode == Opcode.JZ:
            target_pc = get_jump_target_pc(operands[0])
            target_state = f"q_instr_{target_pc}_start" if target_pc < total_instructions else "q_halt"

            prefix = f"q_i{idx}_jz"
            at_zero_cell = make_nav_chain(curr_state, POS_ZERO_VAL, prefix)

            st_jump = f"{prefix}_do_jump"
            add_state(st_jump)
            make_nav_back_chain(st_jump, POS_ZERO_VAL, target_state, f"{prefix}_b_jump")

            st_next = f"{prefix}_do_next"
            add_state(st_next)
            make_nav_back_chain(st_next, POS_ZERO_VAL, next_state, f"{prefix}_b_next")

            transitions[(at_zero_cell, "1")] = TransitionAction(next_state=st_jump, write_symbol="1", direction=Direction.STAY)
            transitions[(at_zero_cell, "0")] = TransitionAction(next_state=st_next, write_symbol="0", direction=Direction.STAY)
            continue

        # 4. JNZ
        if opcode == Opcode.JNZ:
            target_pc = get_jump_target_pc(operands[0])
            target_state = f"q_instr_{target_pc}_start" if target_pc < total_instructions else "q_halt"

            prefix = f"q_i{idx}_jnz"
            at_zero_cell = make_nav_chain(curr_state, POS_ZERO_VAL, prefix)

            st_jump = f"{prefix}_do_jump"
            add_state(st_jump)
            make_nav_back_chain(st_jump, POS_ZERO_VAL, target_state, f"{prefix}_b_jump")

            st_next = f"{prefix}_do_next"
            add_state(st_next)
            make_nav_back_chain(st_next, POS_ZERO_VAL, next_state, f"{prefix}_b_next")

            transitions[(at_zero_cell, "0")] = TransitionAction(next_state=st_jump, write_symbol="0", direction=Direction.STAY)
            transitions[(at_zero_cell, "1")] = TransitionAction(next_state=st_next, write_symbol="1", direction=Direction.STAY)
            continue

        # 5. LOAD R_dst, src
        if opcode == Opcode.LOAD:
            dst_reg = operands[0].strip().upper()
            dst_cell = get_register_val_cell(dst_reg)
            src_str = operands[1].strip()

            if src_str in mem_symbol_to_cell:
                src_cell = mem_symbol_to_cell[src_str]
                build_copy_cell_chain(curr_state, next_state, src_cell, dst_cell, idx)
            elif src_str.upper() in [f"R{i}" for i in range(16)]:
                src_cell = get_register_val_cell(src_str.upper())
                build_copy_cell_chain(curr_state, next_state, src_cell, dst_cell, idx)
            else:
                build_static_write_chain(curr_state, next_state, dst_cell, src_str, idx)
            continue

        # 6. STORE dst_mem, R_src
        if opcode == Opcode.STORE:
            dst_mem = operands[0].strip()
            src_reg = operands[1].strip().upper()
            dst_cell = mem_symbol_to_cell.get(dst_mem, POS_MEM_START + 1)
            src_cell = get_register_val_cell(src_reg)

            build_copy_cell_chain(curr_state, next_state, src_cell, dst_cell, idx)
            continue

        # 7. MOV R_dst, src
        if opcode == Opcode.MOV:
            dst_reg = operands[0].strip().upper()
            dst_cell = get_register_val_cell(dst_reg)
            src_str = operands[1].strip()

            if src_str.upper() in [f"R{i}" for i in range(16)]:
                src_cell = get_register_val_cell(src_str.upper())
                build_copy_cell_chain(curr_state, next_state, src_cell, dst_cell, idx)
            else:
                build_static_write_chain(curr_state, next_state, dst_cell, src_str, idx)
            continue

        # 8. ADD R_dst, src
        if opcode == Opcode.ADD:
            dst_reg = operands[0].strip().upper()
            dst_cell = get_register_val_cell(dst_reg)
            src_str = operands[1].strip()

            if src_str.upper() in [f"R{i}" for i in range(16)]:
                src_cell = get_register_val_cell(src_str.upper())
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_cell, "ADD", idx)
            else:
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_str, "ADD", idx)
            continue

        # 9. SUB R_dst, src
        if opcode == Opcode.SUB:
            dst_reg = operands[0].strip().upper()
            dst_cell = get_register_val_cell(dst_reg)
            src_str = operands[1].strip()

            if src_str.upper() in [f"R{i}" for i in range(16)]:
                src_cell = get_register_val_cell(src_str.upper())
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_cell, "SUB", idx)
            else:
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_str, "SUB", idx)
            continue

        # 10. MUL R_dst, src
        if opcode == Opcode.MUL:
            dst_reg = operands[0].strip().upper()
            dst_cell = get_register_val_cell(dst_reg)
            src_str = operands[1].strip()

            if src_str.upper() in [f"R{i}" for i in range(16)]:
                src_cell = get_register_val_cell(src_str.upper())
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_cell, "MUL", idx)
            else:
                build_arithmetic_chain(curr_state, next_state, dst_cell, src_str, "MUL", idx)
            continue

        # 11. CMP R1, src
        if opcode == Opcode.CMP:
            reg1 = operands[0].strip().upper()
            reg1_cell = get_register_val_cell(reg1)
            src_str = operands[1].strip()
            src_cell_or_val = get_register_val_cell(src_str.upper()) if src_str.upper() in [f"R{i}" for i in range(16)] else src_str

            prefix = f"q_i{idx}_cmp"
            at_r1_state = make_nav_chain(curr_state, reg1_cell, prefix)
            val_syms = get_value_symbols()

            for sym1 in val_syms:
                st1 = f"{prefix}_v1_{sym1}"
                add_state(st1)
                transitions[(at_r1_state, sym1)] = TransitionAction(
                    next_state=st1, write_symbol=sym1, direction=Direction.STAY
                )

                prefix_s1 = f"{prefix}_v1_{sym1}"

                if isinstance(src_cell_or_val, int):
                    src_cell = src_cell_or_val
                    if src_cell >= reg1_cell:
                        curr_n = st1
                        for step in range(reg1_cell, src_cell):
                            nxt_n = f"{prefix_s1}_to_{step+1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.RIGHT
                            )
                            curr_n = nxt_n
                        at_src = curr_n
                    else:
                        curr_n = st1
                        for step in range(reg1_cell, src_cell, -1):
                            nxt_n = f"{prefix_s1}_to_{step-1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.LEFT
                            )
                            curr_n = nxt_n
                        at_src = curr_n

                    for sym2 in val_syms:
                        cmp_val = "1" if sym1 == sym2 else "0"
                        st_cmp = f"{prefix_s1}_res_{sym2}"
                        add_state(st_cmp)
                        transitions[(at_src, sym2)] = TransitionAction(
                            next_state=st_cmp, write_symbol=sym2, direction=Direction.STAY
                        )

                        if POS_ZERO_VAL <= src_cell:
                            curr_n = st_cmp
                            for step in range(src_cell, POS_ZERO_VAL, -1):
                                nxt_n = f"{prefix_s1}_cmp_{sym2}_b_{step-1}"
                                add_state(nxt_n)
                                transitions[(curr_n, "_")] = TransitionAction(
                                    next_state=nxt_n, write_symbol="_", direction=Direction.LEFT
                                )
                                curr_n = nxt_n
                            at_zero = curr_n
                        else:
                            curr_n = st_cmp
                            for step in range(src_cell, POS_ZERO_VAL):
                                nxt_n = f"{prefix_s1}_cmp_{sym2}_f_{step+1}"
                                add_state(nxt_n)
                                transitions[(curr_n, "_")] = TransitionAction(
                                    next_state=nxt_n, write_symbol="_", direction=Direction.RIGHT
                                )
                                curr_n = nxt_n
                            at_zero = curr_n

                        wr_zero_st = f"{prefix_s1}_wrzero_{sym2}"
                        add_state(wr_zero_st)
                        transitions[(at_zero, "_")] = TransitionAction(
                            next_state=wr_zero_st, write_symbol=cmp_val, direction=Direction.STAY
                        )

                        make_nav_back_chain(wr_zero_st, POS_ZERO_VAL, next_state, f"{prefix_s1}_fin_{sym2}")
                else:
                    val2_str = str(src_cell_or_val)
                    cmp_val = "1" if sym1 == val2_str else "0"

                    if POS_ZERO_VAL <= reg1_cell:
                        curr_n = st1
                        for step in range(reg1_cell, POS_ZERO_VAL, -1):
                            nxt_n = f"{prefix_s1}_cmp_b_{step-1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.LEFT
                            )
                            curr_n = nxt_n
                        at_zero = curr_n
                    else:
                        curr_n = st1
                        for step in range(reg1_cell, POS_ZERO_VAL):
                            nxt_n = f"{prefix_s1}_cmp_f_{step+1}"
                            add_state(nxt_n)
                            transitions[(curr_n, "_")] = TransitionAction(
                                next_state=nxt_n, write_symbol="_", direction=Direction.RIGHT
                            )
                            curr_n = nxt_n
                        at_zero = curr_n

                    wr_zero_st = f"{prefix_s1}_wrzero"
                    add_state(wr_zero_st)
                    transitions[(at_zero, "_")] = TransitionAction(
                        next_state=wr_zero_st, write_symbol=cmp_val, direction=Direction.STAY
                    )

                    make_nav_back_chain(wr_zero_st, POS_ZERO_VAL, next_state, f"{prefix_s1}_fin")
            continue

    # Build UTMProgram
    utm_program = UTMProgram(
        states=states,
        alphabet=alphabet,
        blank_symbol="_",
        initial_state="q_start",
        halt_state="q_halt",
        transitions=transitions,
    )

    # Validate generated UTM program
    is_valid, val_err = validate_utm_program(utm_program)
    if not is_valid:
        return TranslationResult(
            utm_program=utm_program,
            status="ERROR",
            error=f"Generated UTMProgram failed validation: {val_err}",
        )

    # Calculate complexity metrics
    metrics = {
        "aml_instruction_count": total_instructions,
        "utm_state_count": len(states),
        "utm_transition_count": len(transitions),
        "tape_alphabet_size": len(alphabet),
        "estimated_tape_footprint": 42 + (len(program.symbol_table) * 2),
    }

    return TranslationResult(
        utm_program=utm_program,
        status="TRANSLATION_GENERATED",
        metrics=metrics,
        error=None,
    )
