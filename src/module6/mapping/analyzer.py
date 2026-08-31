"""
Module 6 Stage 4 — Master Mapping Analyzer.

Provides unified, immutable operations:
- analyze_classical_pair()
- analyze_quantum_pair()
- analyze_mapping_pair()
- analyze_collision()
- analyze_quotient_preservation()
- analyze_injectivity()
- analyze_semantic_preservation()
- analyze_reverse_equivalence()
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.equivalence.syntactic import SyntacticEquivalenceEvaluator
from src.module6.equivalence.structural import StructuralEquivalenceEvaluator
from src.module6.equivalence.basis import BasisEquivalenceEvaluator
from src.module6.equivalence.state_vector import StateVectorEquivalenceEvaluator
from src.module6.equivalence.operator import Level5OperatorVerifier
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator
from src.module6.equivalence.report import EquivalenceReport, EquivalenceStatus, FailureCode
from src.module6.mapping.preservation import (
    ClassicalEquivalenceEvaluator,
    MappingPreservationEvaluator,
    MappingPreservationReport,
)
from src.module6.mapping.collision import (
    CollisionRecord,
    CollisionType,
    CollisionAnalyzer,
)
from src.module6.mapping.model import QuotientWellDefinednessStatus
from src.module6.mapping.quotient import QuotientWellDefinednessAnalyzer
from src.module6.image.signature import compute_circuit_unitary


class MappingAnalyzer:
    """
    Master Mapping Analyzer for Stage 4 multi-level equivalence and compiler mapping analysis.
    """

    @classmethod
    def analyze_classical_pair(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Evaluates classical transition semantic equivalence A1 \equiv_C A2."""
        return ClassicalEquivalenceEvaluator.evaluate_classical_equivalence(m1, m2)

    @classmethod
    def analyze_quantum_pair(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> EquivalenceReport:
        """
        Evaluates 6-level quantum equivalence matrix between c1 and c2.
        Generates structured EquivalenceReport.
        """
        is_syn, l1_st, l1_det = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(c1, c2)
        is_struct, l2_st, l2_det = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(c1, c2)
        is_basis, l3_st, l3_det = BasisEquivalenceEvaluator.evaluate_basis_equivalence(c1, c2, tolerance=tolerance)
        l4_st, l4_det = StateVectorEquivalenceEvaluator.evaluate_state_vector_equivalence(c1, c2, tolerance=tolerance)
        l5_st, l5_det = Level5OperatorVerifier.evaluate_operator_equivalence(c1, c2, tolerance=tolerance)
        is_sem, l6_st, l6_det = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(c1, c2, tolerance=tolerance)

        level_matrix = {
            "LEVEL_1_SYNTACTIC": l1_st,
            "LEVEL_2_STRUCTURAL": l2_st,
            "LEVEL_3_BASIS": l3_st,
            "LEVEL_4_STATE_VECTOR": l4_st,
            "LEVEL_5_OPERATOR": l5_st,
            "LEVEL_6_SEMANTIC": l6_st,
        }

        # Final status determination
        if l5_st == "OPERATOR_IDENTICAL" or l5_st == "OPERATOR_EQUIVALENT":
            final_st = EquivalenceStatus.EQUIVALENT
        elif l5_st == "OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE" or l4_st == "GLOBAL_PHASE_EQUIVALENCE":
            final_st = EquivalenceStatus.EQUIVALENT_UP_TO_GLOBAL_PHASE
        elif is_sem or is_basis:
            final_st = EquivalenceStatus.EQUIVALENT
        elif l3_st == "BASIS_INCONCLUSIVE":
            final_st = EquivalenceStatus.INCONCLUSIVE
        else:
            final_st = EquivalenceStatus.NON_EQUIVALENT

        residuals = {
            "frobenius_residual": l5_det.get("frobenius_residual", float("inf")),
            "max_l2_residual": l4_det.get("max_l2_residual", float("inf")),
            "normalized_trace_overlap": l5_det.get("normalized_trace_overlap", 0.0),
        }

        comp_id = f"EQ_REPORT_{c1.circuit_id}_{c2.circuit_id}"
        det_id = f"DET_{comp_id}"

        prov = {
            "module": "module6",
            "stage": "stage4",
            "c1": c1.circuit_id,
            "c2": c2.circuit_id,
        }

        return EquivalenceReport(
            comparison_id=comp_id,
            source_type="QuantumCircuitIR",
            target_type="QuantumCircuitIR",
            level_results=level_matrix,
            final_status=final_st,
            numerical_residuals=residuals,
            phase_status=l5_st,
            basis_results=l3_det,
            state_results=l4_det,
            operator_results=l5_det,
            evidence_class="EMPIRICAL_EXPERIMENT",
            provenance=prov,
            deterministic_analysis_id=det_id,
        )

    @classmethod
    def analyze_semantic_preservation(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> MappingPreservationReport:
        """Evaluates mapping semantic preservation A1 \equiv_C A2 => F(A1) \equiv_Q F(A2)."""
        return MappingPreservationEvaluator.evaluate_preservation(m1, m2, c1, c2, tolerance=tolerance)

    @classmethod
    def analyze_collision(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> CollisionRecord:
        """Analyzes 3x3 collision matrix classification for a pair (A1, A2) and (F(A1), F(A2))."""
        return CollisionAnalyzer.analyze_pair_collision(m1, m2, c1, c2, tolerance=tolerance)

    @classmethod
    def analyze_quotient_preservation(
        cls,
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
        tolerance: float = 1e-12,
    ) -> Tuple[str, List[Any]]:
        """Evaluates quotient mapping F_bar well-definedness over sample models and circuits."""
        status, records = QuotientWellDefinednessAnalyzer.analyze_quotient(models, circuits, tolerance=tolerance)
        status_str = (
            "EMPIRICALLY_WELL_DEFINED_OVER_TESTED_SET"
            if status == QuotientWellDefinednessStatus.WELL_DEFINED_OBSERVED
            else ("NOT_WELL_DEFINED" if status == QuotientWellDefinednessStatus.COUNTEREXAMPLE_OBSERVED else "NOT_ESTABLISHED")
        )
        return status_str, records

    @classmethod
    def analyze_injectivity(
        cls,
        collision_records: List[CollisionRecord],
    ) -> Tuple[str, bool]:
        """
        Evaluates injectivity status over collision records.
        Distinguishes INJECTIVE_PROVEN, COLLISION_OBSERVED, NO_COLLISION_OBSERVED, UNPROVEN.
        Finite absence of collision MUST remain NO_COLLISION_OBSERVED (Clarification #4).
        """
        collisions_found = False
        for r in collision_records:
            if r.collision_type in (
                CollisionType.TYPE_B_STRUCTURAL_COMPILATION_COLLISION,
                CollisionType.TYPE_C_QUANTUM_SEMANTIC_COLLISION,
            ):
                collisions_found = True
                break

        if collisions_found:
            return "COLLISION_OBSERVED", False
        else:
            # Finite absence of collision cannot be claimed as universal proof
            return "NO_COLLISION_OBSERVED", False

    @classmethod
    def analyze_reverse_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Evaluates reverse equivalence U^\dagger U |psi> = |psi> and U1^\dagger U2 \equiv I.
        Returns (is_reverse_equivalent, identity_residual, details).
        """
        u1 = compute_circuit_unitary(c1, max_qubits=10)
        u2 = compute_circuit_unitary(c2, max_qubits=10)

        if u1 is None or u2 is None or u1.shape != u2.shape:
            return False, float("inf"), {"error": "Dimension mismatch or unitary simulation failed (>10 qubits)"}

        dim = u1.shape[0]
        eye = np.eye(dim, dtype=complex)

        # U1^\dagger U2
        u1_dag_u2 = np.conjugate(u1.T) @ u2
        res = float(np.linalg.norm(u1_dag_u2 - eye))

        is_rev_eq = bool(res < tolerance)

        details = {
            "matrix_dim": dim,
            "identity_residual": res,
            "tolerance": tolerance,
            "is_reverse_equivalent": is_rev_eq,
        }

        return is_rev_eq, res, details
