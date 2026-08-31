"""
Module 6 Stage 8 Test Suite — Deterministic Fixed-Point & Byte-Identical Output.
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
from src.module6.optimization.serialization import serialize_optimization_report


class TestStage8Determinism(unittest.TestCase):
    """Tests for deterministic fixed-point termination and byte-identical outputs."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)

        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=2)
        q0 = QubitRef("r0", 0)
        q1 = QubitRef("r0", 1)

        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=1),
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=q1, control_qubits=(q0,), operation_index=2),
        ]
        self.circuit = QuantumCircuitIR(circuit_id="c_det", registers=[reg], gates=gates)

    def test_byte_identical_optimization_outputs(self) -> None:
        """Req 10, 21, 24: Repeated execution on identical inputs produces byte-identical serialized output."""
        c1, r1 = Stage8CircuitOptimizer.optimize_circuit(self.circuit, self.ctx)
        c2, r2 = Stage8CircuitOptimizer.optimize_circuit(self.circuit, self.ctx)

        json1 = serialize_optimization_report(r1)
        json2 = serialize_optimization_report(r2)

        self.assertEqual(json1, json2)
        self.assertEqual(r1.report_hash, r2.report_hash)
        self.assertEqual(len(c1.gates), len(c2.gates))


if __name__ == "__main__":
    unittest.main()
