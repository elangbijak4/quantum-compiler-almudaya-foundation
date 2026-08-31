"""
Module 6 Stage 8 Test Suite — Master Optimizer Pipeline.
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
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.optimization.optimizer import Stage8CircuitOptimizer
from src.module6.optimization.model import OptimizationStatus


class TestStage8Optimizer(unittest.TestCase):
    """Tests for Stage8CircuitOptimizer master pipeline."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)

        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=2)
        q0 = QubitRef("r0", 0)
        q1 = QubitRef("r0", 1)

        # X(0) X(0) CNOT(0->1) X(1) X(1) -> should optimize to CNOT(0->1)
        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=1),
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=q1, control_qubits=(q0,), operation_index=2),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q1, operation_index=3),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q1, operation_index=4),
        ]

        self.circuit = QuantumCircuitIR(
            circuit_id="c_opt_test",
            registers=[reg],
            gates=gates,
            input_register_ids=["r0"],
            output_register_ids=["r0"],
        )

    def test_optimizer_reduces_gate_count(self) -> None:
        """Req 9, 11, 28: Optimizer reduces 5 gates to 1 gate (CNOT)."""
        opt_circuit, report = Stage8CircuitOptimizer.optimize_circuit(self.circuit, self.ctx)
        self.assertEqual(report.status, OptimizationStatus.OPTIMIZED)
        self.assertEqual(report.initial_metrics.total_gate_count, 5)
        self.assertEqual(report.optimized_metrics.total_gate_count, 1)
        self.assertEqual(report.gate_count_reduction, 4)
        self.assertTrue(report.semantic_equivalence_verified)
        self.assertTrue(report.vocabulary_containment_verified)
        self.assertEqual(len(opt_circuit.gates), 1)
        self.assertEqual(opt_circuit.gates[0].gate_type, LogicalGateType.CNOT)

    def test_optimizer_already_canonical_circuit(self) -> None:
        """Req 10, 24: Unchanged circuit report when already canonical."""
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=2)
        q0 = QubitRef("r0", 0)
        q1 = QubitRef("r0", 1)
        single_cnot = [
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=q1, control_qubits=(q0,), operation_index=0)
        ]
        c_canon = QuantumCircuitIR(circuit_id="c_canon", registers=[reg], gates=single_cnot)

        _, report = Stage8CircuitOptimizer.optimize_circuit(c_canon, self.ctx)
        self.assertEqual(report.status, OptimizationStatus.NO_REDUCTION_POSSIBLE)
        self.assertEqual(report.gate_count_reduction, 0)


if __name__ == "__main__":
    unittest.main()
