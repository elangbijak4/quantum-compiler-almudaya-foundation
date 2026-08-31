"""
Module 6 Stage 5 — Target Operator Model & Pre-Defined Reference Targets.

Defines immutable TargetOperator abstraction and reference targets:
- HADAMARD: H = 1/sqrt(2) * [[1, 1], [1, -1]]
- PHASE: S = [[1, 0], [0, i]]
- T_GATE: T = [[1, 0], [0, exp(i*pi/4)]]
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import numpy as np
import cmath
from src.module6.evolution.candidate import compute_canonical_matrix_hash


@dataclass(frozen=True)
class TargetOperator:
    """
    Immutable Target Operator abstraction.
    """
    target_id: str
    name: str
    matrix: np.ndarray
    dimension: int
    arity: int
    provenance: Dict[str, str] = field(default_factory=dict)
    declared_properties: Dict[str, Any] = field(default_factory=dict)
    canonical_hash: str = field(init=False)

    def __post_init__(self) -> None:
        mat = np.asarray(self.matrix, dtype=complex)
        mat.flags.writeable = False
        object.__setattr__(self, "matrix", mat)

        expected_dim = 2 ** self.arity
        if mat.ndim != 2 or mat.shape[0] != self.dimension or mat.shape[1] != self.dimension:
            raise ValueError(f"INVALID_TARGET_OPERATOR: Matrix shape {mat.shape} does not match dimension {self.dimension}")

        if self.dimension != expected_dim:
            raise ValueError(f"INVALID_TARGET_OPERATOR: Dimension {self.dimension} inconsistent with arity {self.arity}")

        if not np.all(np.isfinite(mat)):
            raise ValueError(f"INVALID_TARGET_OPERATOR: Matrix contains non-finite values")

        c_hash = compute_canonical_matrix_hash(mat)
        object.__setattr__(self, "canonical_hash", c_hash)

    def to_dict(self) -> Dict[str, Any]:
        """Canonical dictionary representation."""
        mat_list = []
        for r in range(self.matrix.shape[0]):
            row = []
            for c in range(self.matrix.shape[1]):
                val = self.matrix[r, c]
                row.append([float(np.real(val)), float(np.imag(val))])
            mat_list.append(row)

        return {
            "target_id": self.target_id,
            "name": self.name,
            "dimension": self.dimension,
            "arity": self.arity,
            "matrix": mat_list,
            "provenance": dict(sorted(self.provenance.items())),
            "declared_properties": self.declared_properties,
            "canonical_hash": self.canonical_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TargetOperator":
        """Reconstructs TargetOperator from dictionary."""
        raw_mat = data["matrix"]
        rows = len(raw_mat)
        cols = len(raw_mat[0])
        mat = np.zeros((rows, cols), dtype=complex)
        for r in range(rows):
            for c in range(cols):
                re, im = raw_mat[r][c]
                mat[r, c] = complex(re, im)

        return cls(
            target_id=data["target_id"],
            name=data["name"],
            matrix=mat,
            dimension=data["dimension"],
            arity=data["arity"],
            provenance=data.get("provenance", {}),
            declared_properties=data.get("declared_properties", {}),
        )


def get_reference_target_hadamard() -> TargetOperator:
    """
    Constructs reference HADAMARD target operator.
    H = 1/sqrt(2) * [[1, 1], [1, -1]]
    """
    mat = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
    return TargetOperator(
        target_id="target_hadamard",
        name="HADAMARD",
        matrix=mat,
        dimension=2,
        arity=1,
        provenance={"specification": "Hadamard reference operator 1/sqrt(2)*[[1,1],[1,-1]]"},
        declared_properties={"superposition_creator": True, "real_amplitudes": True},
    )


def get_reference_target_phase() -> TargetOperator:
    """
    Constructs reference PHASE (S) target operator.
    S = [[1, 0], [0, i]]
    """
    mat = np.array([[1.0, 0.0], [0.0, 1j]], dtype=complex)
    return TargetOperator(
        target_id="target_phase_s",
        name="PHASE_S",
        matrix=mat,
        dimension=2,
        arity=1,
        provenance={"specification": "Phase S reference operator [[1,0],[0,i]]"},
        declared_properties={"complex_amplitudes": True},
    )


def get_reference_target_t() -> TargetOperator:
    """
    Constructs reference T_GATE target operator.
    T = [[1, 0], [0, exp(i*pi/4)]]
    """
    mat = np.array([[1.0, 0.0], [0.0, cmath.exp(1j * np.pi / 4.0)]], dtype=complex)
    return TargetOperator(
        target_id="target_t_gate",
        name="T_GATE",
        matrix=mat,
        dimension=2,
        arity=1,
        provenance={"specification": "T gate reference operator [[1,0],[0,exp(i*pi/4)]]"},
        declared_properties={"complex_amplitudes": True},
    )
