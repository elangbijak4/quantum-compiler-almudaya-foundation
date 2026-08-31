"""
Module 6 Stage 8 Test Suite — Comprehensive Negative Cases.
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
from src.module6.resolution.model import EffectiveCompilationContext, ConfigurationStatus
from src.module6.optimization.optimizer import Stage8CircuitOptimizer
from src.module6.optimization.model import OptimizationStatus


class TestStage8Negative(unittest.TestCase):
    """Tests covering mandatory negative cases for Stage 8 Circuit Optimizer."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)

    def test_infeasible_context_rejected(self) -> None:
        """Req 4, 13, 25: Infeasible context precondition returns INVALID_INPUT status."""
        bad_ctx = EffectiveCompilationContext(
            evolution_stage="GE_0",
            evolutionary_vocabulary_hash=self.ge0.vocabulary_hash,
            session_id="s_bad",
            baseline_mode="DEFAULT_EVOLUTIONARY",
            selected_baseline=self.ge0.vocabulary,
            effective_vocabulary=(),
            compilation_constraints={},
            backend_constraints={},
            equivalence_policy="LEVEL_6_SEMANTIC",
            feasibility_policy="THREE_LEVEL_DIAGNOSIS",
            configuration_status=ConfigurationStatus.INVALID_CONFIGURATION,
            conflicts=(),
            provenance={},
            context_hash="hash_bad",
        )

        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)
        gates = [GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0)]
        circuit = QuantumCircuitIR(circuit_id="c_bad", registers=[reg], gates=gates)

        _, report = Stage8CircuitOptimizer.optimize_circuit(circuit, bad_ctx)
        self.assertEqual(report.status, OptimizationStatus.INVALID_INPUT)

    def test_unauthorized_gate_in_input_returns_vocabulary_violation(self) -> None:
        """Req 5, 20, 25: Input circuit containing unauthorized gate marks VOCABULARY_VIOLATION."""
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)
        # HADAMARD is unauthorized in GE(0)
        h_type = getattr(LogicalGateType, 'HADAMARD', 'HADAMARD')
        gates = [GateOperation(gate_type=h_type, target_qubit=q0, operation_index=0)]
        circuit = QuantumCircuitIR(circuit_id="c_bad_g", registers=[reg], gates=gates)

        _, report = Stage8CircuitOptimizer.optimize_circuit(circuit, self.ctx)
        self.assertEqual(report.status, OptimizationStatus.VOCABULARY_VIOLATION)

    def test_input_immutability(self) -> None:
        """Req 17, 25: Input QuantumCircuitIR remains unchanged after optimization."""
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)
        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=1),
        ]
        circuit = QuantumCircuitIR(circuit_id="c_immut", registers=[reg], gates=gates)

        initial_len = len(circuit.gates)
        Stage8CircuitOptimizer.optimize_circuit(circuit, self.ctx)
        self.assertEqual(len(circuit.gates), initial_len)


if __name__ == "__main__":
    unittest.main()
