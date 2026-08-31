"""
Module 6 Stage 2 — Target Operator Matcher.

Matches candidate target operators U_T against compiler-generated unitaries U_F(A) for A in A_N.
"""

from typing import List, Tuple, Optional
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module4.synthesis.verifier import execute_circuit_on_bitstring
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.image.signature import compute_circuit_unitary
from src.module6.targets.catalog import TargetOperator
from src.module6.vocabulary.analyzer import PrimitiveVocabularyAnalyzer, PrimitiveVocabularyReachabilityStatus
from src.module6.expressibility.report import TargetReachabilityResult, TargetReachabilityStatus


class TargetMatcher:
    """
    Evaluates reachability of target operators U_T within compiler image Img_N(F).
    """

    @classmethod
    def match_target(
        cls,
        target: TargetOperator,
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
        global_phase_mode: str = "GLOBAL_PHASE_EQUIVALENT",
        tolerance: float = 1e-12,
    ) -> TargetReachabilityResult:
        """
        Matches target operator against all compiled circuits F(A) in sample A_N.
        """
        # 1. Primitive Vocabulary Reachability Analysis
        vocab_res = PrimitiveVocabularyAnalyzer.analyze_target_vocabulary(target, tolerance=tolerance)
        primitive_reachability_str = vocab_res.reachability_status.value

        # 2. Compiler Image Match Search
        target_mat = target.matrix
        target_dim = target_mat.shape[0]

        matching_alg_ids: List[str] = []
        matching_circ_ids: List[str] = []
        best_residual: float = float("inf")
        dimension_mismatch_occurred = False

        for m, c in zip(models, circuits):
            total_qubits = sum(reg.width for reg in c.registers)
            circ_dim = 2 ** total_qubits

            if circ_dim != target_dim:
                dimension_mismatch_occurred = True
                continue

            u_circ = compute_circuit_unitary(c, max_qubits=10)
            if u_circ is None:
                u_circ = np.zeros((circ_dim, circ_dim), dtype=complex)
                for col in range(circ_dim):
                    ibits = format(col, f"0{total_qubits}b")
                    obits = execute_circuit_on_bitstring(c, ibits)
                    u_circ[int(obits, 2), col] = 1.0

            # Compare Unitaries
            residual: float
            matched = False

            if global_phase_mode == "GLOBAL_PHASE_EQUIVALENT":
                overlap = np.abs(np.trace(np.conjugate(target_mat.T) @ u_circ)) / target_dim
                residual = float(np.abs(1.0 - overlap))
                if residual < tolerance:
                    matched = True
            else:  # EXACT_OPERATOR
                diff = u_circ - target_mat
                residual = float(np.linalg.norm(diff, ord=2))
                if residual < tolerance:
                    matched = True

            if residual < best_residual:
                best_residual = residual

            if matched:
                matching_alg_ids.append(m.algorithm_id)
                matching_circ_ids.append(c.circuit_id)

        # 3. Determine Reachability Status
        status: TargetReachabilityStatus
        compiler_reachability_str: str

        if len(matching_alg_ids) > 0:
            status = TargetReachabilityStatus.FOUND
            compiler_reachability_str = "FOUND_IN_EXPERIMENTAL_IMAGE"
        elif dimension_mismatch_occurred and best_residual == float("inf"):
            status = TargetReachabilityStatus.DIMENSION_MISMATCH
            compiler_reachability_str = "DIMENSION_MISMATCH"
        else:
            status = TargetReachabilityStatus.NOT_FOUND_IN_SEARCH
            compiler_reachability_str = "NOT_FOUND_IN_SEARCH"

        return TargetReachabilityResult(
            target_id=target.target_id,
            target_operator_hash=target.compute_matrix_hash(),
            target_qubit_count=target.qubit_count,
            primitive_reachability=primitive_reachability_str,
            compiler_image_reachability=compiler_reachability_str,
            matching_algorithm_ids=tuple(matching_alg_ids),
            matching_circuit_ids=tuple(matching_circ_ids),
            best_operator_residual=0.0 if best_residual == float("inf") else best_residual,
            global_phase_status=global_phase_mode,
            status=status,
        )
