"""
Module 6 Stage 3 — Codomain Bounds Analyzer.

Formally characterizes Logical Quantum Circuit Codomain C_Q^\text{logical}, computing qubit, size, and ancilla bounds.
"""

from typing import List, Tuple
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.mapping.model import CodomainDescriptor, MappingComplexityRecord
from src.module6.bounds.cardinality import CardinalityBound, CardinalityType


class CodomainBoundsAnalyzer:
    """
    Analyzes mathematical codomain bounds for C_Q^\text{logical}, C_Q^\text{struct}, C_Q^\text{semantic}.
    """

    @classmethod
    def analyze_codomain(
        cls,
        models: List[ClassicalSemanticModel],
        circuits: List[QuantumCircuitIR],
    ) -> Tuple[CodomainDescriptor, CardinalityBound, List[MappingComplexityRecord]]:
        """
        Builds formal CodomainDescriptor, CardinalityBound, and MappingComplexityRecords for C_Q^\text{logical}.
        """
        complexity_records: List[MappingComplexityRecord] = []

        for m, c in zip(models, circuits):
            total_qubits = sum(reg.width for reg in c.registers)
            gate_count = len(c.gates)
            ancillas = sum(
                reg.width
                for reg in c.registers
                if "ancilla" in reg.register_type.value.lower() or "work" in reg.register_type.value.lower()
            )

            rec = MappingComplexityRecord(
                algorithm_id=m.algorithm_id,
                circuit_id=c.circuit_id,
                source_state_count=len(m.state_map),
                transition_count=len(m.transition_table),
                encoded_configuration_count=len(m.domain_contract.domain),
                logical_qubit_count=total_qubits,
                logical_gate_count=gate_count,
                ancilla_qubit_count=ancillas,
                provenance={"algorithm": m.algorithm_id, "circuit": c.circuit_id},
            )
            complexity_records.append(rec)

        codomain_desc = CodomainDescriptor(
            codomain_name="C_Q^logical",
            formal_definition="C_Q^logical is the logical QuantumCircuitIR AST space admitted by the frozen Module 4 contract.",
            circuit_ir_schema="Module 4 QuantumCircuitIR AST Schema",
            qubit_register_policy="Logical Qubit Register Partitioning (STATE, TAPE, HEAD, ANCILLA, HISTORY)",
            ancilla_uncomputation_policy="Clean Ancilla Uncomputation (|0_A> -> |0_A>)",
            cardinality_type=CardinalityType.COUNTABLE.value,
            provenance={"module": "module6", "stage": "stage3", "codomain": "C_Q^logical"},
        )

        card_bound = CardinalityBound(
            space_name="C_Q^logical",
            cardinality_type=CardinalityType.COUNTABLE,
            upper_bound_formula="Aleph_0 (Countably Infinite for all finite logical circuits over finite discrete gate set {X, CNOT, TOFFOLI})",
            exact_sample_size=len(circuits),
            is_formally_proven=True,
            details="Discrete gate vocabulary with unbounded finite circuit depth yields countably infinite logical circuit space.",
            provenance={"module": "module6", "stage": "stage3", "space": "C_Q^logical"},
        )

        return codomain_desc, card_bound, complexity_records
