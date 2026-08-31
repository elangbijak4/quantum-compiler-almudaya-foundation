"""
Module 6 Stage 7 — Evolutionary Compiler Resolution Data Models.

Defines EffectiveCompilationContext, ConfigurationStatus, ResolutionConflict, and ResolutionResult models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class ConfigurationStatus(str, Enum):
    """Validation status for a resolved compilation configuration."""
    VALID_CONFIGURATION = "VALID_CONFIGURATION"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    CONFIGURATION_CONFLICT = "CONFIGURATION_CONFLICT"
    UNSUPPORTED_CONFIGURATION = "UNSUPPORTED_CONFIGURATION"
    INCONCLUSIVE_CONFIGURATION = "INCONCLUSIVE_CONFIGURATION"


class ConfigurationPrecedence(str, Enum):
    """Deterministic configuration precedence order."""
    EVOLUTIONARY_DEFAULT = "1_EVOLUTIONARY_DEFAULT"
    SESSION_BASELINE = "2_SESSION_BASELINE"
    USER_CONSTRAINTS = "3_USER_CONSTRAINTS"
    BACKEND_CONSTRAINTS = "4_BACKEND_CONSTRAINTS"
    EQUIVALENCE_POLICY = "5_EQUIVALENCE_POLICY"
    FEASIBILITY_POLICY = "6_FEASIBILITY_POLICY"


@dataclass(frozen=True)
class ResolutionConflict:
    """
    Immutable description of a configuration resolution conflict.
    """
    conflict_id: str
    conflict_type: str
    description: str
    competing_sources: Tuple[str, ...]
    resolution_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type,
            "description": self.description,
            "competing_sources": list(self.competing_sources),
            "resolution_action": self.resolution_action,
        }


@dataclass(frozen=True)
class EffectiveCompilationContext:
    """
    Immutable authoritative EffectiveCompilationContext passed into compilation analysis.
    
    Invariants:
    1. DefaultResolution(GE(k)) = GE(k).
    2. SessionConfiguration MUST NOT mutate EvolutionaryState.
    3. Resolution MUST precede compilation (no hidden gate expansion during compilation).
    """
    evolution_stage: str
    evolutionary_vocabulary_hash: str
    session_id: str
    baseline_mode: str
    selected_baseline: Tuple[str, ...]
    effective_vocabulary: Tuple[str, ...]
    compilation_constraints: Dict[str, Any] = field(default_factory=dict)
    backend_constraints: Dict[str, Any] = field(default_factory=dict)
    equivalence_policy: str = "LEVEL_6_SEMANTIC"
    feasibility_policy: str = "THREE_LEVEL_DIAGNOSIS"
    configuration_status: ConfigurationStatus = ConfigurationStatus.VALID_CONFIGURATION
    conflicts: Tuple[ResolutionConflict, ...] = ()
    provenance: Dict[str, Any] = field(default_factory=dict)
    context_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts context to dictionary representation."""
        return {
            "evolution_stage": self.evolution_stage,
            "evolutionary_vocabulary_hash": self.evolutionary_vocabulary_hash,
            "session_id": self.session_id,
            "baseline_mode": self.baseline_mode,
            "selected_baseline": list(self.selected_baseline),
            "effective_vocabulary": list(self.effective_vocabulary),
            "compilation_constraints": dict(self.compilation_constraints),
            "backend_constraints": dict(self.backend_constraints),
            "equivalence_policy": self.equivalence_policy,
            "feasibility_policy": self.feasibility_policy,
            "configuration_status": self.configuration_status.value,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "provenance": dict(self.provenance),
            "context_hash": self.context_hash,
        }


@dataclass(frozen=True)
class ResolutionResult:
    """
    Immutable outcome of resolution and optional feasibility evaluation.
    Enforces Dual Result Semantics:
      Result A: User configuration outcome (FEASIBLE / INFEASIBLE / INVALID)
      Result B: Evolutionary fallback recommendation (FEASIBLE / UNAVAILABLE)
    """
    context: EffectiveCompilationContext
    user_configuration_status: str
    user_feasibility_status: Optional[str] = None
    evolutionary_fallback_status: Optional[str] = None
    evolutionary_fallback_vocabulary: Optional[Tuple[str, ...]] = None
    fallback_available: bool = False
    action_required: str = "NONE"  # NONE, USER_AUTHORIZATION_REQUIRED
    compilation_result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context.to_dict(),
            "user_configuration_status": self.user_configuration_status,
            "user_feasibility_status": self.user_feasibility_status,
            "evolutionary_fallback_status": self.evolutionary_fallback_status,
            "evolutionary_fallback_vocabulary": (
                list(self.evolutionary_fallback_vocabulary)
                if self.evolutionary_fallback_vocabulary is not None
                else None
            ),
            "fallback_available": self.fallback_available,
            "action_required": self.action_required,
            "compilation_result": (
                self.compilation_result.to_dict()
                if hasattr(self.compilation_result, "to_dict")
                else str(self.compilation_result)
                if self.compilation_result is not None
                else None
            ),
        }
