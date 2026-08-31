"""
Module 6 Stage 8 Test Suite — Level 6 Semantic Equivalence Gate Integration.
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


class TestStage8SemanticEquivalence(unittest.TestCase):
    """Tests for mandatory Level 6 Quantum Semantic Equivalence verification gate."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)

        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)

        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=1),
        ]

        self.circuit = QuantumCircuitIR(
            circuit_id="c_sem_test",
            registers=[reg],
            gates=gates,
            input_register_ids=["r0"],
            output_register_ids=["r0"],
        )

    def test_optimized_circuit_preserves_level6_semantic_equivalence(self) -> None:
        """Req 12, 24: Q_opt ≡Q Q_orig verified under Stage 4 Level 6 Semantic Verifier."""
        _, report = Stage8CircuitOptimizer.optimize_circuit(self.circuit, self.ctx)
        self.assertTrue(report.semantic_equivalence_verified)
        self.assertEqual(report.initial_metrics.total_gate_count, 2)
        self.assertEqual(report.optimized_metrics.total_gate_count, 0)


if __name__ == "__main__":
    unittest.main()
