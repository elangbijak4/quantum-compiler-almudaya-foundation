"""
Module 6 Stage 4 — Level 6 Full Semantic / Quotient Equivalence Evaluator.

Evaluates Q1 \equiv_Q Q2 under the project's frozen semantic interpretation.
Records which lower levels were evaluated and required to establish Level 6 quotient equivalence.
"""

from typing import Tuple, Dict, Any
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.equivalence.syntactic import SyntacticEquivalenceEvaluator
from src.module6.equivalence.structural import StructuralEquivalenceEvaluator
from src.module6.equivalence.basis import BasisEquivalenceEvaluator
from src.module6.equivalence.state_vector import StateVectorEquivalenceEvaluator
from src.module6.equivalence.operator import Level5OperatorVerifier


class SemanticEquivalenceEvaluator:
    """
    Evaluator for Level 6 Full Semantic / Quotient Equivalence.
    """

    @classmethod
    def evaluate_semantic_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates Level 6 Full Semantic / Quotient Equivalence across all lower levels.
        Returns (is_semantically_equivalent, status_string, details).
        """
        # Run Level 1 to Level 5 evaluators independently
        is_syn, l1_status, l1_det = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(c1, c2)
        is_struct, l2_status, l2_det = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(c1, c2)
        is_basis, l3_status, l3_det = BasisEquivalenceEvaluator.evaluate_basis_equivalence(c1, c2, tolerance=tolerance)
        l4_status, l4_det = StateVectorEquivalenceEvaluator.evaluate_state_vector_equivalence(c1, c2, tolerance=tolerance)
        l5_status, l5_det = Level5OperatorVerifier.evaluate_operator_equivalence(c1, c2, tolerance=tolerance)

        # Level 6 Quantum Semantic Equivalence condition:
        # Operator equivalence (OPERATOR_IDENTICAL, OPERATOR_EQUIVALENT, or OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE)
        # OR Basis Equivalence (BASIS_EQUIVALENT)
        is_sem_eq = (
            l5_status in ("OPERATOR_IDENTICAL", "OPERATOR_EQUIVALENT", "OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE")
            or l3_status == "BASIS_EQUIVALENT"
        )

        required_levels = []
        if is_syn:
            required_levels.append("LEVEL_1_SYNTACTIC")
        if is_struct:
            required_levels.append("LEVEL_2_STRUCTURAL")
        if l3_status == "BASIS_EQUIVALENT":
            required_levels.append("LEVEL_3_BASIS")
        if l4_status in ("EXACT_STATE_EQUIVALENCE", "GLOBAL_PHASE_EQUIVALENCE"):
            required_levels.append("LEVEL_4_STATE_VECTOR")
        if l5_status in ("OPERATOR_IDENTICAL", "OPERATOR_EQUIVALENT", "OPERATOR_EQUIVALENT_UP_TO_GLOBAL_PHASE"):
            required_levels.append("LEVEL_5_OPERATOR")

        details = {
            "level_1_syntactic": l1_status,
            "level_2_structural": l2_status,
            "level_3_basis": l3_status,
            "level_4_state_vector": l4_status,
            "level_5_operator": l5_status,
            "required_levels_established": required_levels,
            "level_6_quotient_equivalent": is_sem_eq,
        }

        status = "SEMANTICALLY_EQUIVALENT" if is_sem_eq else "SEMANTICALLY_NON_EQUIVALENT"
        return is_sem_eq, status, details
