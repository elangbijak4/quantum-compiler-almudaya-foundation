"""
Module 5 Stage 5 — Quantum State Representation.

Provides deterministic in-process QuantumState representation for N-qubit state vectors in C^(2^N).
"""

from typing import List, Dict, Tuple, Optional
import math
from src.module5.execution.model import EPSILON


class QuantumState:
    """
    Representation of an N-qubit quantum state vector in Hilbert space C^(2^N).
    Uses big-endian bit indexing (qubit 0 is MSB, qubit N-1 is LSB).
    """

    def __init__(self, vector: List[complex], n_qubits: int) -> None:
        expected_dim = 1 << n_qubits
        if len(vector) != expected_dim:
            raise ValueError(f"State vector length mismatch: expected 2^{n_qubits} = {expected_dim}, got {len(vector)}.")

        self._vector: List[complex] = list(vector)
        self._n_qubits: int = n_qubits

    @classmethod
    def initialize_zero(cls, n_qubits: int) -> "QuantumState":
        """Initializes canonical zero state |0...0> = (1, 0, ..., 0)^T."""
        if n_qubits < 1:
            raise ValueError(f"Number of qubits must be >= 1, got {n_qubits}.")
        dim = 1 << n_qubits
        vec = [0.0 + 0.0j] * dim
        vec[0] = 1.0 + 0.0j
        return cls(vec, n_qubits)

    @classmethod
    def from_vector(cls, vector: List[complex]) -> "QuantumState":
        """Constructs QuantumState from an explicit complex vector."""
        dim = len(vector)
        if dim < 2 or (dim & (dim - 1)) != 0:
            raise ValueError(f"State vector dimension must be a power of 2 (>= 2), got {dim}.")
        n_qubits = int(math.log2(dim))
        state = cls(vector, n_qubits)
        if not state.is_normalized():
            raise ValueError(f"Initial state vector is not normalized: norm = {state.norm():.10f}.")
        return state

    def dimension(self) -> int:
        """Returns dimension 2^N of the state vector."""
        return len(self._vector)

    def num_qubits(self) -> int:
        """Returns number of qubits N."""
        return self._n_qubits

    def vector(self) -> List[complex]:
        """Returns a copy of the state vector amplitudes."""
        return list(self._vector)

    def norm(self) -> float:
        """Computes state vector L2 norm sqrt(sum |alpha_i|^2)."""
        return math.sqrt(sum(abs(c) ** 2 for c in self._vector))

    def is_normalized(self, tolerance: float = EPSILON) -> bool:
        """Checks if ||psi|| == 1.0 within tolerance."""
        return abs(self.norm() - 1.0) < tolerance

    def probabilities(self) -> Dict[str, float]:
        """
        Returns computational-basis probability distribution P(i) = |alpha_i|^2
        keyed by bitstring representations (e.g. '00', '01').
        """
        probs: Dict[str, float] = {}
        fmt = f"0{self._n_qubits}b"
        for i, c in enumerate(self._vector):
            bitstr = format(i, fmt)
            probs[bitstr] = abs(c) ** 2
        return probs

    def to_state_dict(self) -> Dict[str, complex]:
        """Returns dictionary of complex amplitudes keyed by bitstrings."""
        fmt = f"0{self._n_qubits}b"
        return {format(i, fmt): c for i, c in enumerate(self._vector)}
