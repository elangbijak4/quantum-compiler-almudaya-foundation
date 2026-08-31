"""
Module 6 Stage 5 — Candidate Gate Model & Unitarity Validation.

Defines immutable CandidateGate abstraction and deterministic canonical matrix hashing.
Validates left and right unitarity: U^\dagger U = I and U U^\dagger = I within eps = 1e-12.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
import numpy as np
import hashlib
import json


def compute_canonical_matrix_hash(matrix: np.ndarray, precision: int = 12) -> str:
    """
    Computes platform-independent canonical SHA-256 hash for a complex matrix.
    Rounds real and imaginary parts to precision decimal places to eliminate floating point artifacts.
    """
    arr = np.asarray(matrix, dtype=complex)
    rows, cols = arr.shape
    canonical_list = []

    for r in range(rows):
        row_list = []
        for c in range(cols):
            val = arr[r, c]
            re_val = round(float(np.real(val)), precision)
            im_val = round(float(np.imag(val)), precision)
            # Normalize zero to avoid -0.0
            if abs(re_val) < 10**(-precision):
                re_val = 0.0
            if abs(im_val) < 10**(-precision):
                im_val = 0.0
            row_list.append(f"{re_val:.12f}+{im_val:.12f}j")
        canonical_list.append(row_list)

    canonical_str = json.dumps(canonical_list, sort_keys=True)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CandidateGate:
    """
    Immutable Candidate Gate abstraction.
    """
    gate_id: str
    name: str
    arity: int
    matrix: np.ndarray
    parameters: Tuple[float, ...] = ()
    provenance: Dict[str, str] = field(default_factory=dict)
    source: str = "CANDIDATE"
    declared_properties: Dict[str, Any] = field(default_factory=dict)
    canonical_hash: str = field(init=False)

    def __post_init__(self) -> None:
        # Freeze matrix as read-only ndarray
        mat = np.asarray(self.matrix, dtype=complex)
        mat.flags.writeable = False
        object.__setattr__(self, "matrix", mat)

        # Validate arity & dimension
        expected_dim = 2 ** self.arity
        if mat.ndim != 2 or mat.shape[0] != expected_dim or mat.shape[1] != expected_dim:
            raise ValueError(f"INVALID_CANDIDATE_GATE: Matrix shape {mat.shape} incompatible with arity {self.arity} (expected {expected_dim}x{expected_dim})")

        # Validate numerical finiteness
        if not np.all(np.isfinite(mat)):
            raise ValueError(f"INVALID_CANDIDATE_GATE: Matrix contains non-finite values (NaN/Inf)")

        # Validate Unitarity
        is_unitary, res1, res2 = self._check_unitarity(mat)
        if not is_unitary:
            raise ValueError(f"NON_UNITARY_CANDIDATE: Matrix is non-unitary (res1={res1:.2e}, res2={res2:.2e})")

        # Compute canonical hash
        c_hash = compute_canonical_matrix_hash(mat)
        object.__setattr__(self, "canonical_hash", c_hash)

    @staticmethod
    def _check_unitarity(mat: np.ndarray, tolerance: float = 1e-12) -> Tuple[bool, float, float]:
        dim = mat.shape[0]
        eye = np.eye(dim, dtype=complex)
        u_dag = np.conjugate(mat.T)

        res1 = float(np.linalg.norm(u_dag @ mat - eye))
        res2 = float(np.linalg.norm(mat @ u_dag - eye))
        is_unitary = (res1 < tolerance) and (res2 < tolerance)
        return is_unitary, res1, res2

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
            "gate_id": self.gate_id,
            "name": self.name,
            "arity": self.arity,
            "matrix": mat_list,
            "parameters": list(self.parameters),
            "provenance": dict(sorted(self.provenance.items())),
            "source": self.source,
            "declared_properties": self.declared_properties,
            "canonical_hash": self.canonical_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateGate":
        """Reconstructs CandidateGate from canonical dictionary."""
        raw_mat = data["matrix"]
        rows = len(raw_mat)
        cols = len(raw_mat[0])
        mat = np.zeros((rows, cols), dtype=complex)
        for r in range(rows):
            for c in range(cols):
                re, im = raw_mat[r][c]
                mat[r, c] = complex(re, im)

        return cls(
            gate_id=data["gate_id"],
            name=data["name"],
            arity=data["arity"],
            matrix=mat,
            parameters=tuple(data.get("parameters", ())),
            provenance=data.get("provenance", {}),
            source=data.get("source", "CANDIDATE"),
            declared_properties=data.get("declared_properties", {}),
        )
