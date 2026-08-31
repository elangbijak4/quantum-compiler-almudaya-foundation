"""
Module 6 Stage 6 — Compilation Feasibility Data Models.

Defines FeasibilityStatus and CompilationFeasibilityReport data models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json


class FeasibilityStatus(str, Enum):
    """Status classification for compilation feasibility under G_effective."""
    FEASIBLE = "FEASIBLE"
    INFEASIBLE_UNDER_USER_BASELINE = "INFEASIBLE_UNDER_USER_BASELINE"
    INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE = "INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE"
    INCONCLUSIVE = "INCONCLUSIVE"


class DiagnosisLevel(str, Enum):
    """Three-level vocabulary diagnosis hierarchy."""
    LEVEL_1_USER_BASELINE_INSUFFICIENT = "LEVEL_1_USER_BASELINE_INSUFFICIENT"
    LEVEL_2_EVOLUTIONARY_BASELINE_INSUFFICIENT = "LEVEL_2_EVOLUTIONARY_BASELINE_INSUFFICIENT"
    LEVEL_3_INCONCLUSIVE = "LEVEL_3_INCONCLUSIVE"
    FEASIBLE = "FEASIBLE"


@dataclass(frozen=True)
class CompilationFeasibilityReport:
    """
    Immutable report of compilation feasibility evaluation for a source algorithm under G_effective.
    """
    algorithm_id: str
    effective_vocabulary: Tuple[str, ...]
    evolutionary_vocabulary: Tuple[str, ...]
    feasibility_status: FeasibilityStatus
    diagnosis_level: DiagnosisLevel
    required_capabilities: Tuple[str, ...]
    missing_capabilities: Tuple[str, ...]
    fallback_available: bool
    fallback_baseline: Tuple[str, ...]
    recommended_augmentation: Tuple[str, ...]
    search_depth_evaluated: int
    provenance: Dict[str, Any] = field(default_factory=dict)
    deterministic_report_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation."""
        return {
            "algorithm_id": self.algorithm_id,
            "effective_vocabulary": list(self.effective_vocabulary),
            "evolutionary_vocabulary": list(self.evolutionary_vocabulary),
            "feasibility_status": self.feasibility_status.value,
            "diagnosis_level": self.diagnosis_level.value,
            "required_capabilities": list(self.required_capabilities),
            "missing_capabilities": list(self.missing_capabilities),
            "fallback_available": self.fallback_available,
            "fallback_baseline": list(self.fallback_baseline),
            "recommended_augmentation": list(self.recommended_augmentation),
            "search_depth_evaluated": self.search_depth_evaluated,
            "provenance": dict(self.provenance),
            "deterministic_report_id": self.deterministic_report_id,
        }
