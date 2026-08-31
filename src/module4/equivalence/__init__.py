"""
Module 4 Equivalence Package — Circuit Semantic Equivalence & End-to-End Synthesis Gate.
"""

from src.module4.equivalence.model import (
    Stage5EquivalenceStatus,
    Stage5StepResult,
    Stage5EquivalenceResult,
)
from src.module4.equivalence.gate import (
    EquivalenceGate,
    verify_end_to_end_equivalence,
)

__all__ = [
    "Stage5EquivalenceStatus",
    "Stage5StepResult",
    "Stage5EquivalenceResult",
    "EquivalenceGate",
    "verify_end_to_end_equivalence",
]
