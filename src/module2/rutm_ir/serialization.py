"""
RUTM-IR Deterministic JSON Serialization & Deserialization (Module 2 Stage 5).

Provides canonical, reproducible JSON serialization and deserialization for RUTM_IR objects.
"""

import json
from typing import Dict, Tuple, Any, Optional
from src.module1.utm.model import Direction, TransitionAction
from src.module2.rutm_ir.model import RUTM_IR, RUTMHistoryPolicy, RUTMProvenance


def serialize_rutm_ir(ir: RUTM_IR, indent: Optional[int] = 2) -> str:
    """
    Serializes a RUTM_IR object into a canonical, deterministic JSON string.

    Sets and transition keys are sorted deterministically for reproducibility.
    """
    # Canonical transitions serialization: sorted by state then symbol
    transitions_data = []
    sorted_transition_keys = sorted(ir.transitions.keys(), key=lambda k: (k[0], k[1]))

    for state, sym in sorted_transition_keys:
        action = ir.transitions[(state, sym)]
        transitions_data.append(
            {
                "current_state": state,
                "read_symbol": sym,
                "next_state": action.next_state,
                "write_symbol": action.write_symbol,
                "direction": action.direction.value,
            }
        )

    canonical_dict = {
        "name": ir.name,
        "states": sorted(list(ir.states)),
        "input_alphabet": sorted(list(ir.input_alphabet)),
        "tape_alphabet": sorted(list(ir.tape_alphabet)),
        "blank_symbol": ir.blank_symbol,
        "initial_state": ir.initial_state,
        "halt_state": ir.halt_state,
        "transitions": transitions_data,
        "history_policy": {
            "enabled": ir.history_policy.enabled,
            "record_schema": list(ir.history_policy.record_schema),
            "inverse_policy": ir.history_policy.inverse_policy,
        },
        "provenance": {
            "source_model": ir.provenance.source_model,
            "source_stage": ir.provenance.source_stage,
            "proof_reference": ir.provenance.proof_reference,
            "specification_version": ir.provenance.specification_version,
        },
    }

    return json.dumps(canonical_dict, indent=indent, sort_keys=True)


def deserialize_rutm_ir(json_str: str) -> RUTM_IR:
    """
    Deserializes a canonical JSON string into a valid RUTM_IR object.
    """
    data = json.loads(json_str)

    # Reconstruct transitions
    transitions: Dict[Tuple[str, str], TransitionAction] = {}
    for t_item in data["transitions"]:
        key = (t_item["current_state"], t_item["read_symbol"])
        action = TransitionAction(
            next_state=t_item["next_state"],
            write_symbol=t_item["write_symbol"],
            direction=Direction(t_item["direction"]),
        )
        transitions[key] = action

    # Reconstruct history policy
    hp_data = data.get("history_policy", {})
    history_policy = RUTMHistoryPolicy(
        enabled=hp_data.get("enabled", True),
        record_schema=tuple(hp_data.get("record_schema", ("prev_state", "overwritten_symbol", "direction"))),
        inverse_policy=hp_data.get("inverse_policy", "LIFO_stack"),
    )

    # Reconstruct provenance
    prov_data = data.get("provenance", {})
    provenance = RUTMProvenance(
        source_model=prov_data.get("source_model", "RUTM"),
        source_stage=prov_data.get("source_stage", "Stage 4"),
        proof_reference=prov_data.get("proof_reference", "docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md"),
        specification_version=prov_data.get("specification_version", "2.0"),
    )

    return RUTM_IR(
        name=data["name"],
        states=frozenset(data["states"]),
        input_alphabet=frozenset(data["input_alphabet"]),
        tape_alphabet=frozenset(data["tape_alphabet"]),
        blank_symbol=data["blank_symbol"],
        initial_state=data["initial_state"],
        halt_state=data["halt_state"],
        transitions=transitions,
        history_policy=history_policy,
        provenance=provenance,
    )
