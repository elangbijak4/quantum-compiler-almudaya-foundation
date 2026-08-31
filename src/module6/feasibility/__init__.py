"""
Module 6 Stage 6 — Compilation Feasibility Subpackage.
"""

from src.module6.feasibility.model import (
    FeasibilityStatus,
    DiagnosisLevel,
    CompilationFeasibilityReport,
)
from src.module6.feasibility.augmentation import MinimalAugmentationAnalyzer
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer
from src.module6.feasibility.serialization import (
    serialize_feasibility_report,
    deserialize_feasibility_report,
)

__all__ = [
    "FeasibilityStatus",
    "DiagnosisLevel",
    "CompilationFeasibilityReport",
    "MinimalAugmentationAnalyzer",
    "CompilationFeasibilityAnalyzer",
    "serialize_feasibility_report",
    "deserialize_feasibility_report",
]
