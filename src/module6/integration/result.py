"""
Module 6 Stage 6 — Compilation Result Data Model.

Defines CompilationStatus, EquivalenceStatus, and CompilationResult models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json

from src.module6.equivalence.levels import EquivalenceLevel
from src.module6.equivalence.report import EquivalenceStatus
from src.module6.feasibility.model import CompilationFeasibilityReport, FeasibilityStatus


class CompilationStatus(str, Enum):
    """Result status for compilation under effective vocabulary G_effective."""
    SUCCESS = "SUCCESS"
    INCOMPLETE = "INCOMPLETE"
    INEXPRESSIBLE_UNDER_BASELINE = "INEXPRESSIBLE_UNDER_BASELINE"
    INEXPRESSIBLE_UNDER_EVOLUTIONARY_VOCABULARY = "INEXPRESSIBLE_UNDER_EVOLUTIONARY_VOCABULARY"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class CompilationResult:
    """
    Immutable compilation result model for a classical algorithm under effective gate vocabulary G_effective.
    
    Rule:
    SUCCESS requires:
    1. Valid QuantumCircuitIR generated using only G_effective.
    2. Semantic equivalence to source algorithm VERIFIED under Module 6 Stage 4 policy.
    """
    source_algorithm_id: str
    requested_baseline: Tuple[str, ...]
    effective_baseline: Tuple[str, ...]
    compilation_status: CompilationStatus
    equivalence_status: EquivalenceStatus
    equivalence_level: EquivalenceLevel
    circuit_id: Optional[str]
    required_gates: Tuple[str, ...]
    missing_capabilities: Tuple[str, ...]
    fallback_available: bool
    fallback_baseline: Tuple[str, ...]
    recommended_augmentation: Tuple[str, ...]
    feasibility_report: CompilationFeasibilityReport
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return {
            "source_algorithm_id": self.source_algorithm_id,
            "requested_baseline": list(self.requested_baseline),
            "effective_baseline": list(self.effective_baseline),
            "compilation_status": self.compilation_status.value,
            "equivalence_status": self.equivalence_status.value,
            "equivalence_level": self.equivalence_level.value,
            "circuit_id": self.circuit_id,
            "required_gates": list(self.required_gates),
            "missing_capabilities": list(self.missing_capabilities),
            "fallback_available": self.fallback_available,
            "fallback_baseline": list(self.fallback_baseline),
            "recommended_augmentation": list(self.recommended_augmentation),
            "feasibility_report": self.feasibility_report.to_dict(),
            "provenance": dict(self.provenance),
        }


def serialize_compilation_result(result: CompilationResult) -> str:
    """Serializes CompilationResult into a canonical JSON string."""
    raw = result.to_dict()
    return json.dumps(raw, indent=2, sort_keys=True)


def deserialize_compilation_result(json_str: str) -> CompilationResult:
    """Deserializes canonical JSON string into CompilationResult."""
    from src.module6.feasibility.serialization import deserialize_feasibility_report
    data = json.loads(json_str)

    feas_rep = deserialize_feasibility_report(json.dumps(data["feasibility_report"]))

    return CompilationResult(
        source_algorithm_id=data["source_algorithm_id"],
        requested_baseline=tuple(data["requested_baseline"]),
        effective_baseline=tuple(data["effective_baseline"]),
        compilation_status=CompilationStatus(data["compilation_status"]),
        equivalence_status=EquivalenceStatus(data["equivalence_status"]),
        equivalence_level=EquivalenceLevel(data["equivalence_level"]),
        circuit_id=data["circuit_id"],
        required_gates=tuple(data["required_gates"]),
        missing_capabilities=tuple(data["missing_capabilities"]),
        fallback_available=data["fallback_available"],
        fallback_baseline=tuple(data["fallback_baseline"]),
        recommended_augmentation=tuple(data["recommended_augmentation"]),
        feasibility_report=feas_rep,
        provenance=data["provenance"],
    )
