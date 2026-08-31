"""
Module 6 Stage 7 — Evolutionary Compiler Resolution & User-Configured Compilation Control Subpackage.
"""

from src.module6.resolution.model import (
    ConfigurationStatus,
    ConfigurationPrecedence,
    ResolutionConflict,
    EffectiveCompilationContext,
    ResolutionResult,
)
from src.module6.resolution.validator import ResolutionValidator
from src.module6.resolution.policy import ResolutionPolicy
from src.module6.resolution.conflicts import ConflictManager
from src.module6.resolution.provenance import ResolutionProvenanceGenerator
from src.module6.resolution.serialization import (
    serialize_compilation_context,
    deserialize_compilation_context,
)
from src.module6.resolution.resolver import Stage7CompilerResolver

__all__ = [
    "ConfigurationStatus",
    "ConfigurationPrecedence",
    "ResolutionConflict",
    "EffectiveCompilationContext",
    "ResolutionResult",
    "ResolutionValidator",
    "ResolutionPolicy",
    "ConflictManager",
    "ResolutionProvenanceGenerator",
    "serialize_compilation_context",
    "deserialize_compilation_context",
    "Stage7CompilerResolver",
]
