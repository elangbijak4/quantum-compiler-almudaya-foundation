"""
Module 6 Stage 4 — Level 1 Syntactic Identity Evaluator.

Defines Q1 == Q2 iff canonical serialized representations are byte-identical.
Checks schema version, qubit count, operation count, ordering, gate names, operands, parameters, and metadata.
"""

from typing import Tuple, Dict, Any
from dataclasses import asdict
import json
from src.module4.circuit_ir.model import QuantumCircuitIR


def serialize_circuit_canonical(c: QuantumCircuitIR) -> Dict[str, Any]:
    """Canonical dictionary representation for QuantumCircuitIR AST."""
    return asdict(c)


class SyntacticEquivalenceEvaluator:
    """
    Evaluator for Level 1 Syntactic / Representational Identity.
    """

    @classmethod
    def evaluate_syntactic_identity(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates Level 1 Syntactic Identity between two QuantumCircuitIR AST objects.
        Returns (is_identical, status_string, details).
        """
        # Canonical serialization check
        ser1 = json.dumps(serialize_circuit_canonical(c1), sort_keys=True)
        ser2 = json.dumps(serialize_circuit_canonical(c2), sort_keys=True)

        is_byte_identical = (ser1 == ser2)

        # Detailed property check
        qubits1 = sum(r.width for r in c1.registers)
        qubits2 = sum(r.width for r in c2.registers)

        gates_match = (len(c1.gates) == len(c2.gates))
        qubits_match = (qubits1 == qubits2)

        details = {
            "circuit_id_1": c1.circuit_id,
            "circuit_id_2": c2.circuit_id,
            "byte_identical": is_byte_identical,
            "qubit_count_1": qubits1,
            "qubit_count_2": qubits2,
            "gate_count_1": len(c1.gates),
            "gate_count_2": len(c2.gates),
            "qubits_match": qubits_match,
            "gates_match": gates_match,
        }

        status = "IDENTICAL" if is_byte_identical else "NOT_IDENTICAL"
        return is_byte_identical, status, details
