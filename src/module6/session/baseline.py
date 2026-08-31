"""
Module 6 Stage 6 — Session Baseline & BaselineMode.

Defines immutable SessionBaseline and BaselineMode (DEFAULT_EVOLUTIONARY, USER_SELECTED).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class BaselineMode(str, Enum):
    """Mode for user session gate vocabulary selection."""
    DEFAULT_EVOLUTIONARY = "DEFAULT_EVOLUTIONARY"
    USER_SELECTED = "USER_SELECTED"


@dataclass(frozen=True)
class SessionBaseline:
    """
    Immutable user session gate vocabulary baseline Bu.
    
    Invariants:
    1. A selected baseline is a constraint on compilation, NOT a guarantee of compilation feasibility.
    2. Selected baseline MUST be a subset of the current evolutionary state: Bu subseteq GE(k).
    3. Session operations MUST NOT mutate the current evolutionary state GE(k).
    """
    session_id: str
    selected_gates: Tuple[str, ...]
    baseline_hash: str
    source_evolution_stage: str
    source_vocabulary_hash: str
    baseline_mode: BaselineMode
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.selected_gates:
            raise ValueError("SessionBaseline selected_gates cannot be empty.")
        sorted_gates = tuple(sorted(set(self.selected_gates)))
        if self.selected_gates != sorted_gates:
            object.__setattr__(self, "selected_gates", sorted_gates)

        computed_hash = hashlib.sha256(json.dumps(self.selected_gates).encode("utf-8")).hexdigest()
        if self.baseline_hash != computed_hash:
            object.__setattr__(self, "baseline_hash", computed_hash)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return {
            "session_id": self.session_id,
            "selected_gates": list(self.selected_gates),
            "baseline_hash": self.baseline_hash,
            "source_evolution_stage": self.source_evolution_stage,
            "source_vocabulary_hash": self.source_vocabulary_hash,
            "baseline_mode": self.baseline_mode.value,
            "provenance": dict(self.provenance),
        }
