"""
QTM Execution Engine Package (Module 3 Stage 7).

Provides state vector evolution, unitary transition operator execution,
adjoint execution, execution traces, inner products, and matrix cross-validation.
"""

from src.module3.execution.engine import (
    QTMExecutionError,
    QTMExecutionTrace,
    QTMExecutionEngine,
    apply_unitary,
    apply_adjoint,
    apply_matrix,
    execute,
    execute_matrix,
    normalize_state,
    inner_product,
)

__all__ = [
    "QTMExecutionError",
    "QTMExecutionTrace",
    "QTMExecutionEngine",
    "apply_unitary",
    "apply_adjoint",
    "apply_matrix",
    "execute",
    "execute_matrix",
    "normalize_state",
    "inner_product",
]
