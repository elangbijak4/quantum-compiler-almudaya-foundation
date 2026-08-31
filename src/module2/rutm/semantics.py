"""
Reversible Universal Turing Machine (RUTM) Operational Semantics (Stage 3).

Strictly compliant with Stage 3 specifications (main-technical-refference.md & STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md).
Consumes frozen Module 1 UTMProgram contract and Stage 2 RUTM configuration model.
"""

from typing import Tuple, Optional, Dict, Set, Any

from src.module1.utm.model import Direction, UTMProgram, TransitionAction, step_utm_configuration
from src.module2.rutm.model import (
    HistoryRecord,
    RUTMConfiguration,
    move_head,
    inverse_move_head,
    push_history,
    pop_history,
    top_history,
    valid_rutm_configuration,
    project_to_utm,
)


def forward_step_rutm(
    config: RUTMConfiguration,
    program: UTMProgram,
) -> RUTMConfiguration:
    """
    Executes a single atomic forward step of the Reversible Universal Turing Machine R(C_R, program) -> C'_R.

    Order of operational steps:
    1. Pre-validation of input configuration C_R against program context.
    2. Fixed-point check for halted or error configurations.
    3. Read current main tape symbol s = T(h).
    4. Transition action lookup (exact match or wildcard fallback).
    5. Capture predecessor history record r = (q, s, d) BEFORE state/tape/head mutation.
    6. Update main tape T'[h] = s'.
    7. Move head position h' = move_head(h, d).
    8. Append history record H' = H ++ [r].
    9. Increment step counter k' = k + 1 (preserving invariant k' = |H'|).
    10. Update halted flag and return new configuration.
    """
    # 1. Pre-validation against program context
    is_valid, err = valid_rutm_configuration(
        config, program.states, program.alphabet, program.halt_state
    )
    if not is_valid:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=config.halted,
            error=f"Invalid configuration for forward step: {err}",
        )

    # 2. Terminal / Fixed-Point / Error Check
    if config.error is not None:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=config.halted,
            error=config.error,
        )

    if config.halted or config.current_state == program.halt_state:
        return RUTMConfiguration(
            current_state=program.halt_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=True,
            error=None,
        )

    # 3. Read symbol
    read_sym = config.get_tape_symbol()

    # 4. Transition lookup (exact match or wildcard fallback)
    action = program.transitions.get((config.current_state, read_sym))
    if action is None:
        action_fallback = program.transitions.get((config.current_state, "_"))
        if action_fallback is not None:
            write_sym = read_sym if action_fallback.write_symbol == "_" else action_fallback.write_symbol
            action = TransitionAction(
                next_state=action_fallback.next_state,
                write_symbol=write_sym,
                direction=action_fallback.direction,
            )

    # 5. Undefined transition handling (atomic error assignment, no state/history mutation)
    if action is None:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=False,
            error=f"Undefined transition for state '{config.current_state}' and symbol '{read_sym}'",
        )

    # 6. Capture predecessor history record BEFORE mutating state/tape/head
    record = HistoryRecord(
        prev_state=config.current_state,
        overwritten_symbol=read_sym,
        direction=action.direction,
    )

    # 7. Update main tape
    new_tape = dict(config.tape)
    new_tape[config.head_pos] = action.write_symbol

    # 8. Move head position
    new_head = move_head(config.head_pos, action.direction)

    # 9. Update history sequence
    new_history = push_history(config.history, record)

    # 10. Increment step counter and set halted flag
    new_step_count = config.step_count + 1
    is_halted = (action.next_state == program.halt_state)

    return RUTMConfiguration(
        current_state=action.next_state,
        tape=new_tape,
        head_pos=new_head,
        history=new_history,
        step_count=new_step_count,
        halted=is_halted,
        error=None,
    )


def reverse_step_rutm(
    config: RUTMConfiguration,
    program: Optional[UTMProgram] = None,
    halt_state: str = "q_halt",
) -> RUTMConfiguration:
    """
    Executes a single atomic reverse step of the Reversible Universal Turing Machine R^{-1}(C'_R) -> C_R.

    Supports optional UTMProgram context for full program state/alphabet validation,
    or structural validation using halt_state when program context is omitted.

    Order of reverse operational steps:
    1. Pre-validation of input configuration C'_R against program context (or structural context).
    2. Error / Initial boundary check (k = 0 or empty history).
    3. Pop top history record r = (q_prev, s_overwritten, d_prev).
    4. Invert head movement h = inverse_move_head(h', d_prev).
    5. Restore overwritten symbol on main tape T[h] = s_overwritten.
    6. Restore predecessor control state q = q_prev.
    7. Decrement step counter k = k' - 1 (preserving invariant k = |H|).
    8. Return restored predecessor configuration.
    """
    target_halt_state = program.halt_state if program is not None else halt_state
    program_states = program.states if program is not None else None
    program_alphabet = program.alphabet if program is not None else None

    # 1. Pre-validation
    is_valid, err = valid_rutm_configuration(
        config,
        program_states=program_states,
        program_alphabet=program_alphabet,
        halt_state=target_halt_state,
    )
    if not is_valid:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=config.halted,
            error=f"Invalid configuration for reverse step: {err}",
        )

    # 2. Error & Boundary checks
    if config.error is not None:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=config.halted,
            error=config.error,
        )

    if config.step_count == 0 or len(config.history) == 0:
        return RUTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            history=config.history,
            step_count=config.step_count,
            halted=config.halted,
            error="Cannot reverse initial configuration (history is empty)",
        )

    # 3. Pop history record
    remaining_history, top_record = pop_history(config.history)
    prev_state = top_record.prev_state
    overwritten_sym = top_record.overwritten_symbol
    direction = top_record.direction

    # 4. Invert head movement
    prev_head = inverse_move_head(config.head_pos, direction)

    # 5. Restore overwritten tape symbol
    prev_tape = dict(config.tape)
    prev_tape[prev_head] = overwritten_sym

    # 6. Decrement step counter & restore predecessor state
    prev_step_count = config.step_count - 1
    is_halted = (prev_state == target_halt_state)

    return RUTMConfiguration(
        current_state=prev_state,
        tape=prev_tape,
        head_pos=prev_head,
        history=remaining_history,
        step_count=prev_step_count,
        halted=is_halted,
        error=None,
    )
