"""
Module 6 Stage 7 — Resolution Serialization (Initialization Scaffold).

Canonical JSON serialization and deserialization for EffectiveCompilationContext.
"""

import json
from src.module6.resolution.model import (
    EffectiveCompilationContext,
    ConfigurationStatus,
    ResolutionConflict,
)


def serialize_compilation_context(context: EffectiveCompilationContext) -> str:
    """Serializes EffectiveCompilationContext into a canonical JSON string."""
    raw = context.to_dict()
    return json.dumps(raw, indent=2, sort_keys=True)


def deserialize_compilation_context(json_str: str) -> EffectiveCompilationContext:
    """Deserializes canonical JSON string into EffectiveCompilationContext."""
    data = json.loads(json_str)
    conflicts = tuple(
        ResolutionConflict(
            conflict_id=f"c_{i}",
            conflict_type=c if isinstance(c, str) else c.get("conflict_type", "UNKNOWN"),
            description="",
            competing_sources=(),
            resolution_action="",
        )
        for i, c in enumerate(data.get("conflicts", []))
    )

    return EffectiveCompilationContext(
        evolution_stage=data["evolution_stage"],
        evolutionary_vocabulary_hash=data["evolutionary_vocabulary_hash"],
        session_id=data["session_id"],
        baseline_mode=data["baseline_mode"],
        selected_baseline=tuple(data["selected_baseline"]),
        effective_vocabulary=tuple(data["effective_vocabulary"]),
        compilation_constraints=data.get("compilation_constraints", {}),
        backend_constraints=data.get("backend_constraints", {}),
        equivalence_policy=data.get("equivalence_policy", "LEVEL_6_SEMANTIC"),
        feasibility_policy=data.get("feasibility_policy", "THREE_LEVEL_DIAGNOSIS"),
        configuration_status=ConfigurationStatus(data["configuration_status"]),
        conflicts=conflicts,
        provenance=data.get("provenance", {}),
        context_hash=data.get("context_hash", ""),
    )
