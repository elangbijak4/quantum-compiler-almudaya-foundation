"""
Formal UTM-IR Model & State Configuration Specification.

Strictly compliant with Stage 6 specifications (main-technical-refference.md & STAGE_6_UTM_SPECIFICATION.md).
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Set, Tuple, Optional, List, Any


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


@dataclass(frozen=True)
class TransitionAction:
    next_state: str
    write_symbol: str
    direction: Direction


@dataclass(frozen=True)
class UTMProgram:
    states: Set[str] = field(default_factory=lambda: {"q_start", "q_halt"})
    alphabet: Set[str] = field(default_factory=lambda: {"0", "1", "_"})
    blank_symbol: str = "_"
    initial_state: str = "q_start"
    halt_state: str = "q_halt"
    transitions: Dict[Tuple[str, str], TransitionAction] = field(default_factory=dict)


@dataclass
class UTMConfiguration:
    current_state: str = "q_start"
    tape: Dict[int, str] = field(default_factory=dict)
    head_pos: int = 0
    step_count: int = 0
    halted: bool = False
    error: Optional[str] = None

    def get_tape_symbol(self, pos: Optional[int] = None) -> str:
        """Returns the symbol at head_pos or specified pos, defaulting to '_' if empty."""
        target_pos = self.head_pos if pos is None else pos
        return self.tape.get(target_pos, "_")


def validate_utm_program(program: UTMProgram) -> Tuple[bool, Optional[str]]:
    """
    Validate deterministic Turing Machine invariants:
    - Non-empty states & alphabet
    - Initial state in states
    - Halt state in states
    - Blank symbol in alphabet
    - Determinism: at most one transition per (state, symbol) pair
    - Valid transition targets and write symbols
    """
    if not program.states:
        return False, "UTMProgram states set cannot be empty."

    if not program.alphabet:
        return False, "UTMProgram alphabet set cannot be empty."

    if program.initial_state not in program.states:
        return False, f"Initial state '{program.initial_state}' not found in states set."

    if program.halt_state not in program.states:
        return False, f"Halt state '{program.halt_state}' not found in states set."

    if program.blank_symbol not in program.alphabet:
        return False, f"Blank symbol '{program.blank_symbol}' not in alphabet."

    for (state, sym), action in program.transitions.items():
        if state not in program.states:
            return False, f"Transition origin state '{state}' not in states set."
        if sym not in program.alphabet:
            return False, f"Transition read symbol '{sym}' not in alphabet."
        if action.next_state not in program.states:
            return False, f"Transition destination state '{action.next_state}' not in states set."
        if action.write_symbol not in program.alphabet:
            return False, f"Transition write symbol '{action.write_symbol}' not in alphabet."

    return True, None


def step_utm_configuration(
    config: UTMConfiguration,
    program: UTMProgram,
) -> UTMConfiguration:
    """
    Executes a single step of the Universal Turing Machine.

    Returns:
        UTMConfiguration
    """
    if config.halted or config.current_state == program.halt_state:
        return UTMConfiguration(
            current_state=program.halt_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            step_count=config.step_count,
            halted=True,
            error=config.error,
        )

    read_sym = config.get_tape_symbol()

    # Fast O(1) dict lookup for exact (state, symbol) transition or wildcard "_"
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

    if action is None:
        return UTMConfiguration(
            current_state=config.current_state,
            tape=dict(config.tape),
            head_pos=config.head_pos,
            step_count=config.step_count,
            halted=False,
            error=f"Undefined transition for state '{config.current_state}' and symbol '{read_sym}'",
        )

    new_tape = dict(config.tape)
    new_tape[config.head_pos] = action.write_symbol

    new_head_pos = config.head_pos
    if action.direction == Direction.LEFT:
        new_head_pos -= 1
    elif action.direction == Direction.RIGHT:
        new_head_pos += 1

    is_halted = (action.next_state == program.halt_state)

    return UTMConfiguration(
        current_state=action.next_state,
        tape=new_tape,
        head_pos=new_head_pos,
        step_count=config.step_count + 1,
        halted=is_halted,
        error=None,
    )
