"""
Module 6 Stage 8 Test Suite — Synthesis Cost Model & Evaluator.
"""

import unittest
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    RegisterType,
    QubitRef,
    GateOperation,
    LogicalGateType,
)
from src.module6.optimization.metrics import CircuitCostEvaluator


class TestStage8CostMetrics(unittest.TestCase):
    """Tests for exact deterministic cost metrics evaluation."""

    def setUp(self) -> None:
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=2)
        q0 = QubitRef("r0", 0)
        q1 = QubitRef("r0", 1)

        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=q1, control_qubits=(q0,), operation_index=1),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=2),
        ]

        self.circuit = QuantumCircuitIR(
            circuit_id="c_test",
            registers=[reg],
            gates=gates,
            input_register_ids=["r0"],
            output_register_ids=["r0"],
        )

    def test_cost_metrics_computation(self) -> None:
        """Req 6: Exact deterministic integer metrics for gate count, gate breakdown, and depth."""
        metrics = CircuitCostEvaluator.evaluate_cost(self.circuit)
        self.assertEqual(metrics.total_gate_count, 3)
        self.assertEqual(metrics.gate_counts_by_type, {"X": 2, "CNOT": 1})
        self.assertEqual(metrics.circuit_depth, 3)
        self.assertEqual(metrics.cnot_depth, 1)
        self.assertEqual(metrics.t_gate_depth, 0)
        self.assertEqual(metrics.qubit_count, 2)


if __name__ == "__main__":
    unittest.main()
