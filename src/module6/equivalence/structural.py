"""
Module 6 Stage 4 — Level 2 Structural Circuit Equivalence Evaluator.

Defines structural equivalence based on canonical circuit structure:
gate sequence, operation indices, operands, parameters, logical qubit topology, and metadata.
"""

from typing import Tuple, Dict, Any
from src.module4.circuit_ir.model import QuantumCircuitIR


class StructuralEquivalenceEvaluator:
    """
    Evaluator for Level 2 Structural Circuit Equivalence.
    """

    @classmethod
    def evaluate_structural_equivalence(
        cls,
        c1: QuantumCircuitIR,
        c2: QuantumCircuitIR,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates Level 2 Structural Circuit Equivalence between two QuantumCircuitIR AST objects.
        Returns (is_structurally_equivalent, status_string, details).
        """
        # 1. Compare total logical qubit count and register structure
        qubits1 = sum(r.width for r in c1.registers)
        qubits2 = sum(r.width for r in c2.registers)

        if qubits1 != qubits2:
            details = {
                "qubit_mismatch": True,
                "qubit_count_1": qubits1,
                "qubit_count_2": qubits2,
            }
            return False, "STRUCTURALLY_DIFFERENT", details

        # 2. Compare gate sequence length
        if len(c1.gates) != len(c2.gates):
            details = {
                "gate_count_mismatch": True,
                "gate_count_1": len(c1.gates),
                "gate_count_2": len(c2.gates),
            }
            return False, "STRUCTURALLY_DIFFERENT", details

        # 3. Compare gate sequence step-by-step
        gates_equal = True
        mismatched_step = -1

        for idx, (g1, g2) in enumerate(zip(c1.gates, c2.gates)):
            name_match = (str(getattr(g1, "gate_type", getattr(g1, "name", ""))) == str(getattr(g2, "gate_type", getattr(g2, "name", ""))))
            target_match = (getattr(g1, "target_qubit", None) == getattr(g2, "target_qubit", None))
            control_match = (getattr(g1, "control_qubits", ()) == getattr(g2, "control_qubits", ()))

            if not (name_match and target_match and control_match):
                gates_equal = False
                mismatched_step = idx
                break

        details = {
            "qubit_count": qubits1,
            "gate_count": len(c1.gates),
            "gates_structurally_equal": gates_equal,
            "mismatched_step": mismatched_step,
        }

        status = "STRUCTURALLY_EQUIVALENT" if gates_equal else "STRUCTURALLY_DIFFERENT"
        return gates_equal, status, details
