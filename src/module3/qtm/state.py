"""
Quantum State Vector Model & Hilbert Space Representation (Module 3 Stage 2).

Implements sparse quantum state vectors |ψ⟩ = Σ α_C |C_R⟩ over Hilbert space H_Q = ℓ²(C_R),
supporting complex amplitudes α_C ∈ ℂ, vector space arithmetic, complex inner products ⟨ψ|φ⟩,
norm computation, and normalized state verification.
"""

import math
from typing import Dict, Any, Union, Set, Optional
from src.module2.rutm.model import RUTMConfiguration
from src.module3.qtm.basis import QuantumBasisState, iota, basis_inner_product

# Centralized numerical tolerance policy threshold for executable sparsification
DEFAULT_TOLERANCE: float = 1e-12


class QTMStateVector:
    """
    Finite executable sparse state vector representation of |ψ⟩ = Σ α_C |C_R⟩ in H_Q = ℓ²(C_R).

    Maintains sparse mapping from QuantumBasisState |C_R⟩ to complex amplitude α_C.
    Ensures state safety through defensive copying and immutable operations.

    Note on Sparsification Policy:
    The `tol` parameter specifies the implementation-level numerical sparsification threshold
    for omitting negligible amplitudes (|α_C| <= tol). This is a storage optimization policy
    and does NOT alter the underlying mathematical Hilbert space H_Q = ℓ²(C_R) or redefine
    exact mathematical zero (α_C = 0).
    """

    __slots__ = ("_amplitudes",)

    def __init__(
        self,
        amplitudes: Optional[Dict[QuantumBasisState, Union[complex, float, int]]] = None,
        tol: float = DEFAULT_TOLERANCE,
    ) -> None:
        """
        Initializes a quantum state vector |ψ⟩.

        :param amplitudes: Mapping from QuantumBasisState to complex amplitude α_C.
        :param tol: Numerical sparsification threshold for storage optimization (omits |α_C| <= tol).
        """
        self._amplitudes: Dict[QuantumBasisState, complex] = {}
        if amplitudes:
            for basis, amp in amplitudes.items():
                if not isinstance(basis, QuantumBasisState):
                    raise TypeError(f"State key {basis} must be a QuantumBasisState instance.")
                try:
                    c_amp = complex(amp)
                except (TypeError, ValueError) as exc:
                    raise TypeError(f"Invalid amplitude '{amp}' for basis state {basis}: {exc}") from exc

                if not (math.isnan(c_amp.real) or math.isnan(c_amp.imag)):
                    if abs(c_amp) > tol:
                        self._amplitudes[basis] = c_amp
                else:
                    raise ValueError(f"Amplitude for basis {basis} cannot be NaN.")

    @property
    def amplitudes(self) -> Dict[QuantumBasisState, complex]:
        """Returns a copy of the non-zero amplitudes map {basis: amplitude}."""
        return dict(self._amplitudes)

    @property
    def basis_states(self) -> Set[QuantumBasisState]:
        """Returns the set of basis states with non-zero amplitudes in superposition."""
        return set(self._amplitudes.keys())

    @property
    def dimension(self) -> int:
        """Returns the number of active basis states in the sparse superposition."""
        return len(self._amplitudes)

    def get_amplitude(self, basis: QuantumBasisState) -> complex:
        """
        Returns complex amplitude α_C for basis state |C⟩, defaulting to 0.0j if absent.
        """
        if not isinstance(basis, QuantumBasisState):
            raise TypeError("get_amplitude requires a QuantumBasisState argument.")
        return self._amplitudes.get(basis, 0.0 + 0.0j)

    def norm(self) -> float:
        """
        Calculates vector norm ||ψ|| = sqrt(⟨ψ|ψ⟩) = sqrt(Σ |α_C|²).

        :return: Non-negative float norm.
        """
        sq_sum = sum(abs(amp) ** 2 for amp in self._amplitudes.values())
        return math.sqrt(sq_sum)

    def is_normalized(self, tol: float = DEFAULT_TOLERANCE) -> bool:
        """
        Executable verification predicate checking if vector norm is 1.0 within numerical tolerance.

        :param tol: Numerical verification tolerance threshold.
        :return: True if ||ψ|| == 1.0 ± tol, False otherwise.
        """
        return abs(self.norm() - 1.0) <= tol

    def is_zero(self, tol: float = DEFAULT_TOLERANCE) -> bool:
        """
        Executable verification predicate checking if vector is zero vector |0⟩_vec (norm <= tol).

        :param tol: Numerical verification tolerance threshold.
        :return: True if zero vector, False otherwise.
        """
        return self.norm() <= tol

    def normalize(self, tol: float = DEFAULT_TOLERANCE) -> "QTMStateVector":
        """
        Returns a new normalized QTMStateVector |ψ_norm⟩ = |ψ⟩ / ||ψ||.

        :param tol: Numerical tolerance threshold.
        :return: Normalized state vector.
        :raises ValueError: If attempting to normalize the zero vector.
        """
        current_norm = self.norm()
        if current_norm <= tol:
            raise ValueError("Cannot normalize the zero vector |0⟩_vec.")
        scale = 1.0 / current_norm
        normalized_amps = {basis: amp * scale for basis, amp in self._amplitudes.items()}
        return QTMStateVector(normalized_amps, tol=tol)

    def inner_product(self, other: "QTMStateVector") -> complex:
        """
        Computes Hilbert space inner product ⟨self|other⟩ = Σ α_C* β_C.

        Handles complex conjugation of left-vector amplitudes strictly according to linear algebra.

        :param other: Right state vector |other⟩.
        :return: Complex inner product value.
        """
        if not isinstance(other, QTMStateVector):
            raise TypeError("inner_product requires a QTMStateVector argument.")

        # Compute over intersection of non-zero basis states for efficiency
        common_basis = self._amplitudes.keys() & other._amplitudes.keys()
        result = sum(
            self._amplitudes[b].conjugate() * other._amplitudes[b]
            for b in common_basis
        )
        return complex(result)

    def __add__(self, other: Any) -> "QTMStateVector":
        if not isinstance(other, QTMStateVector):
            return NotImplemented
        combined = dict(self._amplitudes)
        for b, amp in other._amplitudes.items():
            combined[b] = combined.get(b, 0.0 + 0.0j) + amp
        return QTMStateVector(combined)

    def __sub__(self, other: Any) -> "QTMStateVector":
        if not isinstance(other, QTMStateVector):
            return NotImplemented
        combined = dict(self._amplitudes)
        for b, amp in other._amplitudes.items():
            combined[b] = combined.get(b, 0.0 + 0.0j) - amp
        return QTMStateVector(combined)

    def __mul__(self, scalar: Any) -> "QTMStateVector":
        if not isinstance(scalar, (complex, float, int)):
            return NotImplemented
        c_scalar = complex(scalar)
        scaled = {b: amp * c_scalar for b, amp in self._amplitudes.items()}
        return QTMStateVector(scaled)

    def __rmul__(self, scalar: Any) -> "QTMStateVector":
        return self.__mul__(scalar)

    def __neg__(self) -> "QTMStateVector":
        return self.__mul__(-1.0)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, QTMStateVector):
            return False
        diff = self - other
        return diff.is_zero(DEFAULT_TOLERANCE)

    def __repr__(self) -> str:
        if not self._amplitudes:
            return "|0⟩_vec"
        terms = []
        for b, amp in self._amplitudes.items():
            if amp.imag == 0:
                amp_str = f"{amp.real:.4g}"
            else:
                amp_str = f"({amp:.4g})"
            terms.append(f"{amp_str}{b}")
        return " + ".join(terms)


def basis_state_vector(config: RUTMConfiguration) -> QTMStateVector:
    """
    Constructs a normalized quantum state vector 1.0 |C_R⟩ from an RUTMConfiguration.

    :param config: Valid RUTMConfiguration instance.
    :return: QTMStateVector containing single basis state with amplitude 1.0.
    """
    basis = iota(config)
    return QTMStateVector({basis: 1.0 + 0.0j})


def zero_state_vector() -> QTMStateVector:
    """
    Constructs the Hilbert space zero vector |0⟩_vec (containing zero basis states).

    :return: Empty QTMStateVector (norm = 0.0).
    """
    return QTMStateVector({})
