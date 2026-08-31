"""
Module 6 Stage 2 — Target Circuit & Operator Catalog Data Models.

Defines target classification, TargetOperator, and TargetCircuit models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import numpy as np


class TargetClassification(str, Enum):
    """Semantic classification of candidate target operators and circuits."""
    PRIMITIVE_GATE = "PRIMITIVE_GATE"
    SHORT_COMPOSITION = "SHORT_COMPOSITION"
    SINGLE_QUBIT = "SINGLE_QUBIT"
    MULTI_QUBIT_REVERSIBLE = "MULTI_QUBIT_REVERSIBLE"
    ENTANGLING = "ENTANGLING"
    SUPERPOSITION_TRANSFORMATION = "SUPERPOSITION_TRANSFORMATION"
    COMPOSITE_GATE = "COMPOSITE_GATE"


@dataclass
class TargetOperator:
    """
    Immutable representation of a candidate target unitary operator U_T.
    """
    target_id: str
    qubit_count: int
    matrix: np.ndarray
    classification: TargetClassification
    provenance: str = "SYNTHETIC_TARGET_FAMILY"
    is_open_hypothesis: bool = False

    def compute_matrix_hash(self) -> str:
        """Computes deterministic hash of matrix elements to 1e-12 precision."""
        mat_rows: List[str] = []
        for r in range(self.matrix.shape[0]):
            for c in range(self.matrix.shape[1]):
                val = self.matrix[r, c]
                mat_rows.append(f"{val.real:.12f}+{val.imag:.12f}i")
        raw_op = f"{self.target_id}|{self.qubit_count}|" + "|".join(mat_rows)
        return hashlib.sha256(raw_op.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TargetCircuit:
    """
    Immutable representation of a candidate target logical circuit.
    """
    target_id: str
    qubit_count: int
    gate_sequence: Tuple[str, ...]
    target_operator: TargetOperator
    classification: TargetClassification
    provenance: str = "SYNTHETIC_TARGET_FAMILY"
