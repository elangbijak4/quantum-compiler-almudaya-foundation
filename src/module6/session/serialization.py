"""
Module 6 Stage 6 — Session Serialization.

Canonical JSON serialization and deserialization for SessionBaseline.
"""

import json
from src.module6.session.baseline import SessionBaseline, BaselineMode


def serialize_session_baseline(baseline: SessionBaseline) -> str:
    """Serializes SessionBaseline into a canonical JSON string."""
    raw = baseline.to_dict()
    return json.dumps(raw, indent=2, sort_keys=True)


def deserialize_session_baseline(json_str: str) -> SessionBaseline:
    """Deserializes canonical JSON string into SessionBaseline."""
    data = json.loads(json_str)
    return SessionBaseline(
        session_id=data["session_id"],
        selected_gates=tuple(data["selected_gates"]),
        baseline_hash=data["baseline_hash"],
        source_evolution_stage=data["source_evolution_stage"],
        source_vocabulary_hash=data["source_vocabulary_hash"],
        baseline_mode=BaselineMode(data["baseline_mode"]),
        provenance=data["provenance"],
    )
