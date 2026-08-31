"""
Module 6 Stage 4 — Phase Overlap Evaluator.

Implements phase_overlap for states |<psi1|psi2>| and operators |Tr(U1^\dagger U2)| / d.
Distinguishes global phase from relative phase.
"""

from typing import Tuple, Dict, Any
import numpy as np


class PhaseOverlapEvaluator:
    """
    Evaluator for phase-invariant inner products and operator overlaps.
    """

    @classmethod
    def state_phase_overlap(
        cls,
        v1: np.ndarray,
        v2: np.ndarray,
        tolerance: float = 1e-12,
    ) -> Tuple[float, float, bool, bool]:
        """
        Computes state overlap |<v1|v2>| and L2 residual ||v1 - v2||_2.
        Returns (overlap, l2_residual, is_exact_equal, is_global_phase_equivalent).
        """
        if v1.shape != v2.shape:
            return 0.0, float("inf"), False, False

        # L2 distance
        l2_res = float(np.linalg.norm(v1 - v2))
        is_exact = bool(l2_res < tolerance)

        # Inner product overlap
        inner_prod = complex(np.vdot(v1, v2))
        overlap = float(np.abs(inner_prod))
        is_global_phase = bool(np.abs(1.0 - overlap) < tolerance)

        return overlap, l2_res, is_exact, is_global_phase

    @classmethod
    def operator_phase_overlap(
        cls,
        u1: np.ndarray,
        u2: np.ndarray,
        tolerance: float = 1e-12,
    ) -> Tuple[float, float, bool, bool, complex]:
        """
        Computes normalized trace overlap |Tr(U1^\dagger U2)| / d and Frobenius residual ||U1 - U2||.
        Returns (overlap, frobenius_residual, is_exact_equal, is_global_phase_equivalent, phase_factor).
        """
        if u1.shape != u2.shape or u1.ndim != 2 or u1.shape[0] != u1.shape[1]:
            return 0.0, float("inf"), False, False, 0.0

        dim = u1.shape[0]

        # Frobenius norm distance
        frob_res = float(np.linalg.norm(u1 - u2))
        is_exact = bool(frob_res < tolerance)

        # Normalized trace overlap
        trace_val = complex(np.trace(np.conjugate(u1.T) @ u2))
        overlap = float(np.abs(trace_val) / dim)
        is_global_phase = bool(np.abs(1.0 - overlap) < tolerance)

        phase_factor = trace_val / (dim * overlap) if overlap > 1e-15 else 0.0

        return overlap, frob_res, is_exact, is_global_phase, phase_factor
