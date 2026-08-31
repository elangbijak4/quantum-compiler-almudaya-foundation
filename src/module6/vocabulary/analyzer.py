"""
Module 6 Stage 2 — Primitive Vocabulary Analyzer.

Analyzes reachability of candidate target operators from the primitive gate vocabulary
G_primitive = {X, CNOT, TOFFOLI}, separating <G_primitive> reachability from compiler image Img(F).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional
import numpy as np
from src.module6.targets.catalog import TargetOperator


class PrimitiveVocabularyReachabilityStatus(str, Enum):
    """Reachability classification under primitive gate vocabulary <G_primitive>."""
    EXPRESSIBLE = "EXPRESSIBLE"
    NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY = "NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY"
    BOUND_EXCEEDED = "BOUND_EXCEEDED"


@dataclass(frozen=True)
class PrimitiveVocabularyResult:
    """
    Result of primitive gate vocabulary expressibility analysis.
    """
    target_id: str
    reachability_status: PrimitiveVocabularyReachabilityStatus
    in_primitive_closure: bool
    best_matrix_residual: float
    depth_evaluated: int
    details: str


class PrimitiveVocabularyAnalyzer:
    """
    Analyzer for testing whether candidate target operators U_T belong to <G_primitive>.
    """
    PRIMITIVE_VOCABULARY: Set[str] = {"X", "CNOT", "TOFFOLI"}

    @classmethod
    def analyze_target_vocabulary(
        cls,
        target: TargetOperator,
        max_depth: int = 5,
        tolerance: float = 1e-12,
    ) -> PrimitiveVocabularyResult:
        """
        Evaluates whether target U_T is expressible from <G_primitive>.
        """
        mat = target.matrix
        n_qubits = target.qubit_count

        # 1. Algebraic Permutation Matrix Invariant Check:
        # All primitive gates (X, CNOT, TOFFOLI) are real-valued permutation/reversible operations.
        # Any composition of primitive gates produces a real integer permutation matrix (0s and 1s).
        is_real = np.allclose(mat.imag, 0.0, atol=tolerance)
        is_binary = np.all(np.isclose(mat.real, 0.0, atol=tolerance) | np.isclose(mat.real, 1.0, atol=tolerance))

        if not is_real or not is_binary:
            return PrimitiveVocabularyResult(
                target_id=target.target_id,
                reachability_status=PrimitiveVocabularyReachabilityStatus.NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY,
                in_primitive_closure=False,
                best_matrix_residual=1.0,
                depth_evaluated=max_depth,
                details=f"Target {target.target_id} has non-binary/complex entries and cannot be represented by primitive vocabulary G_primitive={cls.PRIMITIVE_VOCABULARY}.",
            )

        # 2. Reversible Permutation Check
        dim = 2 ** n_qubits
        if mat.shape != (dim, dim):
            return PrimitiveVocabularyResult(
                target_id=target.target_id,
                reachability_status=PrimitiveVocabularyReachabilityStatus.NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY,
                in_primitive_closure=False,
                best_matrix_residual=1.0,
                depth_evaluated=max_depth,
                details=f"Dimension mismatch for {target.target_id}: shape {mat.shape} != ({dim}, {dim}).",
            )

        row_sums = np.sum(mat.real, axis=1)
        col_sums = np.sum(mat.real, axis=0)
        is_permutation = np.allclose(row_sums, 1.0, atol=tolerance) and np.allclose(col_sums, 1.0, atol=tolerance)

        if is_permutation:
            return PrimitiveVocabularyResult(
                target_id=target.target_id,
                reachability_status=PrimitiveVocabularyReachabilityStatus.EXPRESSIBLE,
                in_primitive_closure=True,
                best_matrix_residual=0.0,
                depth_evaluated=max_depth,
                details=f"Target {target.target_id} is a valid reversible permutation expressible within <G_primitive>.",
            )

        return PrimitiveVocabularyResult(
            target_id=target.target_id,
            reachability_status=PrimitiveVocabularyReachabilityStatus.NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY,
            in_primitive_closure=False,
            best_matrix_residual=1.0,
            depth_evaluated=max_depth,
            details=f"Target {target.target_id} is not a valid reversible permutation matrix.",
        )
