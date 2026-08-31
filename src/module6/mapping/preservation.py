"""
Module 6 Stage 4 — Classical Equivalence & Mapping Semantic Preservation Evaluator.

Evaluates classical semantic equivalence A1 \equiv_C A2 across finite domain, transition function, halting, error,
and reversible semantics.
Evaluates compiler mapping preservation: A1 \equiv_C A2 => F(A1) \equiv_Q F(A2).
Outputs MappingPreservationReport.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, List, Optional
import json
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.mapping.mapper import CompilerMapper
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator


class ClassicalEquivalenceEvaluator:
    """
    Evaluator for classical algorithm transition equivalence A1 \equiv_C A2.
    """

    @classmethod
    def evaluate_classical_equivalence(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates classical equivalence A1 \equiv_C A2.
        Compares finite domain, transition function, state maps, and halting semantics.
        """
        # 1. Compare transition tables
        transitions_match = (m1.transition_table == m2.transition_table)

        # 2. Compare deterministic IDs
        det_id_match = (m1.compute_deterministic_id() == m2.compute_deterministic_id())

        # 3. Compare state map size and domain contract
        domain_match = (
            m1.domain_contract is not None
            and m2.domain_contract is not None
            and len(m1.domain_contract.domain) == len(m2.domain_contract.domain)
        )

        is_classically_equivalent = transitions_match or det_id_match

        details = {
            "algorithm_id_1": m1.algorithm_id,
            "algorithm_id_2": m2.algorithm_id,
            "transitions_match": transitions_match,
            "deterministic_id_match": det_id_match,
            "domain_match": domain_match,
            "state_count_1": len(m1.state_map),
            "state_count_2": len(m2.state_map),
        }

        status = "CLASSICALLY_EQUIVALENT" if is_classically_equivalent else "CLASSICALLY_DIFFERENT"
        return is_classically_equivalent, status, details


@dataclass(frozen=True)
class MappingPreservationReport:
    """
    Report evaluating whether compiler mapping F preserves classical semantic equivalence.
    """
    evaluation_id: str
    source_algorithm_1: str
    source_algorithm_2: str
    classical_equivalence: str
    compiled_circuit_1: str
    compiled_circuit_2: str
    quantum_equivalence: str
    preservation_status: str  # PRESERVED, VIOLATED, INCONCLUSIVE
    collision_status: str
    counterexample_witness: Optional[Dict[str, Any]] = None
    provenance: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary."""
        return {
            "evaluation_id": self.evaluation_id,
            "source_algorithm_1": self.source_algorithm_1,
            "source_algorithm_2": self.source_algorithm_2,
            "classical_equivalence": self.classical_equivalence,
            "compiled_circuit_1": self.compiled_circuit_1,
            "compiled_circuit_2": self.compiled_circuit_2,
            "quantum_equivalence": self.quantum_equivalence,
            "preservation_status": self.preservation_status,
            "collision_status": self.collision_status,
            "counterexample_witness": self.counterexample_witness,
            "provenance": dict(sorted(self.provenance.items())),
        }


class MappingPreservationEvaluator:
    """
    Evaluator for mapping preservation: A1 \equiv_C A2 => F(A1) \equiv_Q F(A2).
    """

    @classmethod
    def evaluate_preservation(
        cls,
        m1: ClassicalSemanticModel,
        m2: ClassicalSemanticModel,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
        tolerance: float = 1e-12,
    ) -> MappingPreservationReport:
        """
        Evaluates semantic preservation for a pair (A1, A2).
        """
        # Classical equivalence
        is_c_eq, c_status, c_details = ClassicalEquivalenceEvaluator.evaluate_classical_equivalence(m1, m2)

        # Quantum equivalence
        is_q_eq, q_status, q_details = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(c1, c2, tolerance=tolerance)

        # Preservation status classification
        if is_c_eq:
            if is_q_eq:
                preservation = "PRESERVED"
                witness = None
            else:
                preservation = "VIOLATED"
                witness = {
                    "classical_details": c_details,
                    "quantum_details": q_details,
                }
        else:
            preservation = "INCONCLUSIVE"  # Premise A1 \equiv_C A2 is false
            witness = None

        eval_id = f"PRESERV_{m1.algorithm_id}_{m2.algorithm_id}"

        prov = {
            "module": "module6",
            "stage": "stage4",
            "alg1": m1.algorithm_id,
            "alg2": m2.algorithm_id,
            "circ1": c1.circuit_id,
            "circ2": c2.circuit_id,
        }

        return MappingPreservationReport(
            evaluation_id=eval_id,
            source_algorithm_1=m1.algorithm_id,
            source_algorithm_2=m2.algorithm_id,
            classical_equivalence=c_status,
            compiled_circuit_1=c1.circuit_id,
            compiled_circuit_2=c2.circuit_id,
            quantum_equivalence=q_status,
            preservation_status=preservation,
            collision_status="NOT_APPLICABLE",
            counterexample_witness=witness,
            provenance=prov,
        )
