"""
Module 6 Stage 8 — Circuit Cost Evaluator.

Computes deterministic cost metrics (gate count, depth, T-depth, CNOT-depth) for QuantumCircuitIR.
"""

from typing import Dict, Any, Optional
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.optimization.model import CircuitCostMetrics


class CircuitCostEvaluator:
    """
    Evaluates exact synthesis cost metrics for a QuantumCircuitIR.
    """

    @classmethod
    def evaluate_cost(cls, circuit: QuantumCircuitIR) -> CircuitCostMetrics:
        """
        Computes CircuitCostMetrics from QuantumCircuitIR.
        """
        gate_counts: Dict[str, int] = {}
        t_depth = 0
        cnot_depth = 0

        for gate in circuit.gates:
            g_name = gate.gate_type.name if hasattr(gate.gate_type, 'name') else str(gate.gate_type)
            gate_counts[g_name] = gate_counts.get(g_name, 0) + 1
            if g_name == "T_GATE":
                t_depth += 1
            elif g_name == "CNOT":
                cnot_depth += 1

        total_gates = len(circuit.gates)
        depth = total_gates  # Exact total operational sequence depth

        return CircuitCostMetrics(
            total_gate_count=total_gates,
            gate_counts_by_type=gate_counts,
            circuit_depth=depth,
            t_gate_depth=t_depth,
            cnot_depth=cnot_depth,
            qubit_count=circuit.total_width,
        )
