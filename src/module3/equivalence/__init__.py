"""
Reversible -> Quantum Equivalence Verification Gate Package (Module 3 Stage 8).

Provides independent step-by-step equivalence verification between Module 2 reversible execution
and Module 3 Stage 7 QTM state vector evolution.
"""

from src.module3.equivalence.result import (
    EquivalenceStatus,
    EquivalenceStepResult,
    EquivalenceResult,
)
from src.module3.equivalence.gate import (
    EquivalenceGate,
    verify_equivalence,
)

__all__ = [
    "EquivalenceStatus",
    "EquivalenceStepResult",
    "EquivalenceResult",
    "EquivalenceGate",
    "verify_equivalence",
]
