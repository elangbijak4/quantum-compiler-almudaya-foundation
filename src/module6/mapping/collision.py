"""
Module 6 Stage 4 — 3x3 Collision Matrix & Collision Type Analyzer.

Implements 3x3 collision matrix mapping classical relations to compiled quantum relations.
Classifies collision types:
- TYPE_A_CLASSICAL_SEMANTIC_COLLISION: Syntactically different classical programs, classically semantically equivalent.
- TYPE_B_STRUCTURAL_COMPILATION_COLLISION: Classically different, compiled circuits structurally identical.
- TYPE_C_QUANTUM_SEMANTIC_COLLISION: Classically different, compiled circuits structurally different, but quantum semantically equivalent.
- TYPE_D_DISTINCT_MAPPING: Classically different, quantum semantically different.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Any
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.equivalence.syntactic import SyntacticEquivalenceEvaluator
from src.module6.equivalence.structural import StructuralEquivalenceEvaluator
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator
from src.module6.mapping.preservation import ClassicalEquivalenceEvaluator


class CollisionType(str, Enum):
    """
    Semantic and structural collision types.
    """
    TYPE_A_CLASSICAL_SEMANTIC_COLLISION = "TYPE_A_CLASSICAL_SEMANTIC_COLLISION"
    TYPE_B_STRUCTURAL_COMPILATION_COLLISION = "TYPE_B_STRUCTURAL_COMPILATION_COLLISION"
    TYPE_C_QUANTUM_SEMANTIC_COLLISION = "TYPE_C_QUANTUM_SEMANTIC_COLLISION"
    TYPE_D_DISTINCT_MAPPING = "TYPE_D_DISTINCT_MAPPING"
    SYNTACTIC_IDENTITY = "SYNTACTIC_IDENTITY"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CollisionRecord:
    """
    Record of pairwise collision analysis.
    """
    record_id: str
    algorithm_1_id: str
    algorithm_2_id: str
    classical_syntactic_equal: bool
    classical_semantic_equal: bool
    quantum_syntactic_equal: bool
    quantum_structural_equal: bool
    quantum_semantic_equal: bool
    collision_type: CollisionType
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary."""
        return {
            "record_id": self.record_id,
            "algorithm_1_id": self.algorithm_1_id,
            "algorithm_2_id": self.algorithm_2_id,
            "classical_syntactic_equal": self.classical_syntactic_equal,
            "classical_semantic_equal": self.classical_semantic_equal,
            "quantum_syntactic_equal": self.quantum_syntactic_equal,
            "quantum_structural_equal": self.quantum_structural_equal,
            "quantum_semantic_equal": self.quantum_semantic_equal,
            "collision_type": str(self.collision_type),
            "details": self.details,
        }


class CollisionAnalyzer:
    """
    Analyzer for 3x3 Collision Matrix and Semantic Collision Classification.
    """

    @classmethod
    def analyze_pair_collision(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> CollisionRecord:
        """
        Analyzes pairwise collision between two algorithms (A1, A2) and their compiled circuits (F(A1), F(A2)).
        """
        c_syn = (m1.algorithm_id == m2.algorithm_id)
        c_sem, _, _ = ClassicalEquivalenceEvaluator.evaluate_classical_equivalence(m1, m2)

        q_syn, _, _ = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(c1, c2)
        q_struct, _, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(c1, c2)
        q_sem, _, _ = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(c1, c2, tolerance=tolerance)

        # Classification logic
        if c_syn:
            col_type = CollisionType.SYNTACTIC_IDENTITY
        elif not c_syn and c_sem:
            col_type = CollisionType.TYPE_A_CLASSICAL_SEMANTIC_COLLISION
        elif not c_sem and q_struct:
            col_type = CollisionType.TYPE_B_STRUCTURAL_COMPILATION_COLLISION
        elif not c_sem and not q_struct and q_sem:
            col_type = CollisionType.TYPE_C_QUANTUM_SEMANTIC_COLLISION
        else:
            col_type = CollisionType.TYPE_D_DISTINCT_MAPPING

        rec_id = f"COL_{m1.algorithm_id}_{m2.algorithm_id}"

        details = {
            "m1_id": m1.algorithm_id,
            "m2_id": m2.algorithm_id,
            "c1_id": c1.circuit_id,
            "c2_id": c2.circuit_id,
        }

        return CollisionRecord(
            record_id=rec_id,
            algorithm_1_id=m1.algorithm_id,
            algorithm_2_id=m2.algorithm_id,
            classical_syntactic_equal=c_syn,
            classical_semantic_equal=c_sem,
            quantum_syntactic_equal=q_syn,
            quantum_structural_equal=q_struct,
            quantum_semantic_equal=q_sem,
            collision_type=col_type,
            details=details,
        )

    @classmethod
    def compute_collision_matrix(
        cls,
        records: List[CollisionRecord],
    ) -> Dict[str, Dict[str, int]]:
        """
        Computes 3x3 collision matrix counting occurrences.
        Classical rows: A1 == A2, A1 \equiv_C A2, A1 !=_C A2
        Quantum cols: F(A1) == F(A2), F(A1) \equiv_Q F(A2), F(A1) !=_Q F(A2)
        """
        matrix = {
            "A1_eq_A2": {"F1_eq_F2": 0, "F1_equiv_F2": 0, "F1_neq_F2": 0},
            "A1_equiv_A2": {"F1_eq_F2": 0, "F1_equiv_F2": 0, "F1_neq_F2": 0},
            "A1_neq_A2": {"F1_eq_F2": 0, "F1_equiv_F2": 0, "F1_neq_F2": 0},
        }

        for r in records:
            if r.classical_syntactic_equal:
                row_key = "A1_eq_A2"
            elif r.classical_semantic_equal:
                row_key = "A1_equiv_A2"
            else:
                row_key = "A1_neq_A2"

            if r.quantum_syntactic_equal or r.quantum_structural_equal:
                col_key = "F1_eq_F2"
            elif r.quantum_semantic_equal:
                col_key = "F1_equiv_F2"
            else:
                col_key = "F1_neq_F2"

            matrix[row_key][col_key] += 1

        return matrix
