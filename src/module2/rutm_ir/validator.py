"""
RUTM-IR Executable Validator (Module 2 Stage 5).

Validates representation integrity, determinism, state/alphabet boundaries,
history policy, and proof provenance for RUTM_IR machine descriptions.
"""

from typing import Tuple, Optional
from src.module1.utm.model import Direction, TransitionAction
from src.module2.rutm_ir.model import RUTM_IR


def validate_rutm_ir(ir: RUTM_IR) -> Tuple[bool, Optional[str]]:
    """
    Executes structural and representation validation for a RUTM_IR object.

    Returns:
        (True, None) if valid.
        (False, error_message) if invalid.
    """
    # 1. Machine name check
    if not isinstance(ir.name, str) or not ir.name.strip():
        return False, "Machine name must be a non-empty string"

    # 2. State set validation
    if not isinstance(ir.states, (set, frozenSet := type(frozenset()))):
        return False, "States must be a set or frozenset"
    if len(ir.states) == 0:
        return False, "States set cannot be empty"
    for st in ir.states:
        if not isinstance(st, str) or not st.strip():
            return False, f"State identifier must be a non-empty string, got '{st}'"

    # 3. Input & Tape Alphabet validation
    if not isinstance(ir.input_alphabet, (set, frozenSet)):
        return False, "Input alphabet must be a set or frozenset"
    if len(ir.input_alphabet) == 0:
        return False, "Input alphabet cannot be empty"

    if not isinstance(ir.tape_alphabet, (set, frozenSet)):
        return False, "Tape alphabet must be a set or frozenset"
    if len(ir.tape_alphabet) == 0:
        return False, "Tape alphabet cannot be empty"

    if not ir.input_alphabet.issubset(ir.tape_alphabet):
        missing = ir.input_alphabet - ir.tape_alphabet
        return False, f"Input alphabet symbols {missing} must be a subset of tape alphabet"

    # 4. Blank symbol validation
    if not isinstance(ir.blank_symbol, str) or not ir.blank_symbol:
        return False, "Blank symbol must be a non-empty string"
    if ir.blank_symbol not in ir.tape_alphabet:
        return False, f"Blank symbol '{ir.blank_symbol}' must belong to tape alphabet {ir.tape_alphabet}"

    # 5. Initial state & Halt state validation
    if ir.initial_state not in ir.states:
        return False, f"Initial state '{ir.initial_state}' must belong to states set {ir.states}"
    if ir.halt_state not in ir.states:
        return False, f"Halt state '{ir.halt_state}' must belong to states set {ir.states}"

    # 6. Transitions validation
    if not isinstance(ir.transitions, dict):
        return False, "Transitions must be a dictionary mapping (state, symbol) -> TransitionAction"

    seen_keys = set()
    for (state, sym), action in ir.transitions.items():
        if (state, sym) in seen_keys:
            return False, f"Duplicate transition rule detected for key ('{state}', '{sym}')"
        seen_keys.add((state, sym))

        if state not in ir.states:
            return False, f"Transition source state '{state}' does not belong to states set {ir.states}"
        if state == ir.halt_state:
            return False, f"Transitions out of halt_state '{ir.halt_state}' are invalid"
        if sym not in ir.tape_alphabet:
            return False, f"Transition read symbol '{sym}' does not belong to tape alphabet {ir.tape_alphabet}"

        if not isinstance(action, TransitionAction):
            return False, f"Transition action for ('{state}', '{sym}') must be a TransitionAction object"

        if action.next_state not in ir.states:
            return (
                False,
                f"Transition action target state '{action.next_state}' does not belong to states set {ir.states}",
            )
        if action.write_symbol not in ir.tape_alphabet:
            return (
                False,
                f"Transition action write symbol '{action.write_symbol}' does not belong to tape alphabet {ir.tape_alphabet}",
            )
        if not isinstance(action.direction, Direction):
            return False, f"Transition action direction '{action.direction}' must be a valid Direction enum"

    # 7. History Policy validation (Closure Item #1)
    if not hasattr(ir, "history_policy") or ir.history_policy is None:
        return False, "RUTM_IR must include a valid history_policy"
    if not isinstance(ir.history_policy.enabled, bool):
        return False, "History policy 'enabled' field must be a boolean"
    if ir.history_policy.enabled:
        expected_schema = ("prev_state", "overwritten_symbol", "direction")
        if ir.history_policy.record_schema != expected_schema:
            return (
                False,
                f"Unsupported history policy record_schema '{ir.history_policy.record_schema}'. Proven RUTM model requires {expected_schema}.",
            )
        if ir.history_policy.inverse_policy != "LIFO_stack":
            return (
                False,
                f"Unsupported history policy inverse_policy '{ir.history_policy.inverse_policy}'. Proven RUTM model requires 'LIFO_stack'.",
            )

    # 8. Provenance metadata validation
    if not hasattr(ir, "provenance") or ir.provenance is None:
        return False, "RUTM_IR must include valid provenance metadata"
    if not isinstance(ir.provenance.source_model, str) or not ir.provenance.source_model.strip():
        return False, "Provenance 'source_model' must be a non-empty string"
    if not isinstance(ir.provenance.source_stage, str) or not ir.provenance.source_stage.strip():
        return False, "Provenance 'source_stage' must be a non-empty string"
    if not isinstance(ir.provenance.proof_reference, str) or not ir.provenance.proof_reference.strip():
        return False, "Provenance 'proof_reference' must be a non-empty string"

    return True, None
