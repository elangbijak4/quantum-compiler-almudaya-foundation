"""
Module 3 QTM Package — Quantum Turing Machine Formal Model, State Space & Operational Semantics (Stages 1–3).

Exports computational basis states, Hilbert space state vectors, unitary operators,
and matrix representations.
"""

from src.module3.qtm.basis import (
    QuantumBasisState,
    iota,
    basis_inner_product,
)
from src.module3.qtm.state import (
    QTMStateVector,
    DEFAULT_TOLERANCE,
    basis_state_vector,
    zero_state_vector,
)
from src.module3.qtm.operator import (
    LiftedUnitaryOperator,
    PermutationMatrixRepresentation,
    create_unitary_operator_from_program,
    create_unitary_operator_from_mapping,
)

__all__ = [
    "QuantumBasisState",
    "iota",
    "basis_inner_product",
    "QTMStateVector",
    "DEFAULT_TOLERANCE",
    "basis_state_vector",
    "zero_state_vector",
    "LiftedUnitaryOperator",
    "PermutationMatrixRepresentation",
    "create_unitary_operator_from_program",
    "create_unitary_operator_from_mapping",
]
