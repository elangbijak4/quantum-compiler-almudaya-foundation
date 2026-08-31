"""
Module 6 Stage 3 — Semantic Quotient Mapping Analyzer.

Evaluates well-definedness of semantic quotient mapping F_bar: A_C/\equiv_C -> C_Q^\text{logical}/\equiv_Q.
Tests condition: A1 \equiv_C A2 => F(A1) \equiv_Q F(A2).
"""

from typing import List, Tuple, Dict
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.image.signature import compute_circuit_unitary
from src.module6.mapping.model import SemanticQuotientRecord, QuotientWellDefinednessStatus


class QuotientWellDefinednessAnalyzer:
    """
    Analyzes whether quotient mapping F_bar is well-defined over a finite sample A_N.
    """

    @classmethod
    def analyze_quotient(
        cls,
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
        tolerance: float = 1e-12,
    ) -> Tuple[QuotientWellDefinednessStatus, List[SemanticQuotientRecord]]:
        """
        Evaluates quotient well-definedness across all pairs (A_i, A_j) in sample.
        """
        records: List[SemanticQuotientRecord] = []
        n = len(models)
        equivalent_pairs_found = False
        counterexample_found = False

        for i in range(n):
            for j in range(i + 1, n):
                m1, m2 = models[i], models[j]
                c1, c2 = circuits[i], circuits[j]

                # Check classical transition equivalence A1 \equiv_C A2
                classically_eq = (m1.compute_deterministic_id() == m2.compute_deterministic_id()) or (
                    m1.transition_table == m2.transition_table
                )

                if classically_eq:
                    equivalent_pairs_found = True

                    # Check quantum operator equivalence F(A1) \equiv_Q F(A2)
                    u1 = compute_circuit_unitary(c1, max_qubits=10)
                    u2 = compute_circuit_unitary(c2, max_qubits=10)

                    if u1 is not None and u2 is not None and u1.shape == u2.shape:
                        overlap = np.abs(np.trace(np.conjugate(u1.T) @ u2)) / u1.shape[0]
                        quantum_eq = bool(np.abs(1.0 - overlap) < tolerance)
                    else:
                        quantum_eq = (c1.circuit_id == c2.circuit_id)

                    well_defined = quantum_eq
                    if not well_defined:
                        counterexample_found = True

                    records.append(
                        SemanticQuotientRecord(
                            evaluation_id=f"QUOT_{m1.algorithm_id}_{m2.algorithm_id}",
                            classical_equivalence_class_id=m1.compute_deterministic_id(),
                            quantum_equivalence_class_id=f"EQ_{c1.circuit_id}",
                            algorithms_in_class=(m1.algorithm_id, m2.algorithm_id),
                            circuits_in_class=(c1.circuit_id, c2.circuit_id),
                            well_defined_in_class=well_defined,
                            details=f"Classically equivalent: {classically_eq}, Quantum equivalent: {quantum_eq}",
                        )
                    )

        if counterexample_found:
            status = QuotientWellDefinednessStatus.COUNTEREXAMPLE_OBSERVED
        elif equivalent_pairs_found:
            status = QuotientWellDefinednessStatus.WELL_DEFINED_OBSERVED
        else:
            status = QuotientWellDefinednessStatus.NOT_ESTABLISHED

        return status, records
