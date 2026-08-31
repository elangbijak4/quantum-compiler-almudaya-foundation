"""
Module 4 Decomposition Package — Gate Decomposition & Ancilla Uncomputation.
"""

from src.module4.decomposition.decomposer import (
    decompose_circuit_ir,
)
from src.module4.decomposition.verifier import (
    Stage4VerificationResult,
    verify_decomposed_circuit_equivalence,
)

__all__ = [
    "decompose_circuit_ir",
    "Stage4VerificationResult",
    "verify_decomposed_circuit_equivalence",
]
