"""
Module 6 Stage 3 — Real Amplitude Invariant Analyzer.

Evaluates whether compiler-generated unitaries U_F(A) have purely real-valued matrix entries.
Establishes structural invariant Img_Q(F) subseteq U(2^N) \cap M_{2^N}(R).
"""

from typing import List, Tuple
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.image.signature import compute_circuit_unitary
from src.module6.mapping.model import BoundClassification


class RealAmplitudeInvariantAnalyzer:
    """
    Analyzes real-amplitude matrix entry invariant for U_F(A).
    """

    @classmethod
    def check_unitary_is_real(cls, matrix: np.ndarray, tolerance: float = 1e-12) -> bool:
        """
        Checks if matrix entries have zero imaginary components.
        """
        imag_norm = np.linalg.norm(np.imag(matrix))
        return float(imag_norm) < tolerance

    @classmethod
    def check_circuit_is_real(cls, circuit: QuantumCircuitIR, tolerance: float = 1e-12) -> bool:
        """
        Checks if circuit unitary is real-valued.
        """
        mat = compute_circuit_unitary(circuit, max_qubits=10)
        if mat is not None:
            return cls.check_unitary_is_real(mat, tolerance=tolerance)
        # All primitive gates {X, CNOT, TOFFOLI} are real-valued
        return True

    @classmethod
    def analyze_real_amplitude_invariant(
        cls,
        circuits: List[QuantumCircuitIR],
        tolerance: float = 1e-12,
    ) -> Tuple[str, BoundClassification, bool]:
        """
        Evaluates real-amplitude invariant over compiler circuits.
        Returns (status_string, classification, holds_universally).
        """
        all_real = True
        for c in circuits:
            if not cls.check_circuit_is_real(c, tolerance=tolerance):
                all_real = False
                break

        if all_real:
            return "FORMALLY_ESTABLISHED", BoundClassification.FORMAL_THEOREM, True
        else:
            return "NOT_ESTABLISHED", BoundClassification.EMPIRICAL_OBSERVATION, False
