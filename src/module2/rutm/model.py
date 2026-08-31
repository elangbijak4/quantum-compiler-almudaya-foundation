"""
Reversible Universal Turing Machine (RUTM) Configuration Model (Stage 2).

Strictly compliant with Stage 2 formalization (main-technical-refference.md & STAGE_2_RUTM_CONFIGURATION.md).
Consumes frozen Module 1 UTMConfiguration contract without modifying Module 1.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Set, List, Any, Union

# Consume Direction and UTMConfiguration from frozen Module 1
from src.module1.utm.model import Direction, UTMConfiguration


@dataclass(frozen=True)
class HistoryRecord:
    """
    Immutable auxiliary transition record capturing predecessor state,
    overwritten main tape symbol, and head movement direction.
    """
    prev_state: str
    overwritten_symbol: str
    direction: Direction


@dataclass
class RUTMConfiguration:
    """
    Extended 7-tuple RUTM configuration C_R = (q, T, h, H, k, halted, error).
    """
    current_state: str = "q_start"
    tape: Dict[int, str] = field(default_factory=dict)
    head_pos: int = 0
    history: Tuple[HistoryRecord, ...] = field(default_factory=tuple)
    step_count: int = 0
    halted: bool = False
    error: Optional[str] = None

    def get_tape_symbol(self, pos: Optional[int] = None) -> str:
        """Returns symbol at head_pos or specified position, defaulting to '_' if empty."""
        target_pos = self.head_pos if pos is None else pos
        return self.tape.get(target_pos, "_")


def move_head(head_pos: int, direction: Direction) -> int:
    """Computes forward head movement: move(h, d)."""
    if direction == Direction.LEFT:
        return head_pos - 1
    elif direction == Direction.RIGHT:
        return head_pos + 1
    return head_pos


def inverse_move_head(head_pos: int, direction: Direction) -> int:
    """Computes inverse head movement: inverse_move(h', d)."""
    if direction == Direction.LEFT:
        return head_pos + 1
    elif direction == Direction.RIGHT:
        return head_pos - 1
    return head_pos


def push_history(
    history: Tuple[HistoryRecord, ...], record: HistoryRecord
) -> Tuple[HistoryRecord, ...]:
    """Pushes a new transition record onto the history sequence."""
    return history + (record,)


def pop_history(
    history: Tuple[HistoryRecord, ...]
) -> Tuple[Tuple[HistoryRecord, ...], HistoryRecord]:
    """
    Pops the top transition record from history sequence.
    Raises ValueError if history is empty.
    """
    if not history:
        raise ValueError("Cannot pop from empty RUTM history sequence.")
    return history[:-1], history[-1]


def top_history(
    history: Tuple[HistoryRecord, ...]
) -> Optional[HistoryRecord]:
    """Returns top history record without modifying history sequence."""
    if not history:
        return None
    return history[-1]


def valid_rutm_configuration(
    config: Any,
    program_states: Optional[Set[str]] = None,
    program_alphabet: Optional[Set[str]] = None,
    halt_state: str = "q_halt",
) -> Tuple[bool, Optional[str]]:
    """
    Evaluates the formal representation predicate Valid_RUTM(C_R).

    Enforces invariants:
    1. config is RUTMConfiguration instance.
    2. q is non-empty str (and in program_states if provided).
    3. head_pos is int.
    4. step_count is non-negative int.
    5. halted is bool.
    6. error is None or str.
    7. history is tuple or list of valid HistoryRecord items.
    8. Representation invariant: k = |H| (step_count == len(history)).
    9. Halting consistency invariant: halted == True <==> current_state == halt_state.
    10. Tape keys are integers and values are strings (and in program_alphabet if provided).
    11. History records prev_state, overwritten_symbol, and direction are strictly valid.
    """
    if not isinstance(config, RUTMConfiguration):
        return False, "Configuration must be a RUTMConfiguration instance."

    if not isinstance(config.current_state, str) or not config.current_state:
        return False, "RUTM current_state must be a non-empty string."

    if program_states is not None and config.current_state not in program_states:
        return False, f"State '{config.current_state}' not found in program states."

    if type(config.head_pos) is not int:
        return False, "RUTM head_pos must be an integer."

    if type(config.step_count) is not int or config.step_count < 0:
        return False, "RUTM step_count must be a non-negative integer."

    if type(config.halted) is not bool:
        return False, "RUTM halted must be a boolean."

    if config.error is not None and not isinstance(config.error, str):
        return False, "RUTM error must be None or a string."

    if not isinstance(config.history, (tuple, list)):
        return False, "RUTM history must be a sequence (tuple or list)."

    # Representation Invariant: k = |H|
    if config.step_count != len(config.history):
        return False, f"Representation invariant violated: step_count ({config.step_count}) != |history| ({len(config.history)})."

    # Halting Consistency Invariant: halted == True <==> current_state == halt_state
    if (config.current_state == halt_state) != config.halted:
        return False, f"Halting consistency invariant violated: state '{config.current_state}' vs halted={config.halted}."

    if not isinstance(config.tape, dict):
        return False, "RUTM tape must be a dictionary."

    for pos, sym in config.tape.items():
        if type(pos) is not int:
            return False, f"Tape key '{pos}' must be an integer."
        if not isinstance(sym, str):
            return False, f"Tape value at cell {pos} must be a string."
        if program_alphabet is not None and sym not in program_alphabet:
            return False, f"Tape symbol '{sym}' at cell {pos} not in program alphabet."

    for idx, rec in enumerate(config.history):
        if not isinstance(rec, HistoryRecord):
            return False, f"History item at index {idx} is not a HistoryRecord instance."
        if not isinstance(rec.prev_state, str) or not rec.prev_state:
            return False, f"History record {idx} prev_state must be a non-empty string."
        if program_states is not None and rec.prev_state not in program_states:
            return False, f"History record {idx} state '{rec.prev_state}' not in program states."
        if not isinstance(rec.overwritten_symbol, str) or not rec.overwritten_symbol:
            return False, f"History record {idx} overwritten_symbol must be a non-empty string."
        if program_alphabet is not None and rec.overwritten_symbol not in program_alphabet:
            return False, f"History record {idx} symbol '{rec.overwritten_symbol}' not in program alphabet."
        if not isinstance(rec.direction, Direction):
            return False, f"History record {idx} direction must be a valid Direction enum."

    return True, None


def project_to_utm(config: RUTMConfiguration) -> UTMConfiguration:
    """
    Canonical projection function pi_UTM : C_R -> C_UTM.
    Maps RUTMConfiguration directly to Module 1's frozen UTMConfiguration.
    """
    return UTMConfiguration(
        current_state=config.current_state,
        tape=dict(config.tape),
        head_pos=config.head_pos,
        step_count=config.step_count,
        halted=config.halted,
        error=config.error,
    )


def create_initial_rutm_configuration(
    tape: Dict[int, str],
    initial_state: str = "q_start",
) -> RUTMConfiguration:
    """
    Constructs an initial RUTM configuration C_{R,0} = (q_start, T_0, 0, [], 0, False, None).
    """
    return RUTMConfiguration(
        current_state=initial_state,
        tape=dict(tape),
        head_pos=0,
        history=(),
        step_count=0,
        halted=False,
        error=None,
    )
