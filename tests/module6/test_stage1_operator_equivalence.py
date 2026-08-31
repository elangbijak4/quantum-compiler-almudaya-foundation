"""
Module 6 Stage 1 Unit Test Suite — Level 5 Operator Equivalence.

Tests Level 5 operator equivalence, matrix unitarity, superposition linearity check,
reverse operator execution, global phase overlap, and negative failure paths.
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4 import FiniteDomainContract
from src.module4.circuit_ir.model import QuantumCircuitIR, GateOperation, LogicalGateType, QubitRef
from src.module6 import (
    build_classical_semantic_model,
    CompilerMapper,
    Level5OperatorVerifier,
    Stage1SemanticVerifier,
    EquivalenceStatus,
    FailureCode,
)


class TestStage1OperatorEquivalence(unittest.TestCase):
    def setUp(self) -> None:
        self.program = UTMProgram(
            states={"q0", "q1", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions={
                ("q0", "0"): TransitionAction(next_state="q1", write_symbol="1", direction=Direction.RIGHT),
                ("q1", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
            },
        )

        self.c0 = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=0, history=(), step_count=0, halted=True)
        self.c1 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1"}, head_pos=1, history=(), step_count=0, halted=True)
        self.c2 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1"}, head_pos=2, history=(), step_count=0, halted=True)

        self.domain_contract = FiniteDomainContract(
            domain=[self.c0, self.c1, self.c2],
            execution_horizon=2,
            initial_configuration=self.c0,
        )

        self.state_map = {"q0": 0, "q1": 1, "q_halt": 2}
        self.symbol_map = {"_": 0, "0": 1, "1": 2}

        self.model = build_classical_semantic_model(
            self.program, self.domain_contract, self.state_map, self.symbol_map, "op_alg"
        )
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_level5_operator_equivalence_pass(self) -> None:
        """Positive test: Level 5 operator equivalence PASSES for compiled circuit."""
        (
            overall_pass,
            op_res,
            left_u,
            right_u,
            superpos_res,
            ancilla_pass,
            phase_pass,
            reverse_pass,
            diagnostics,
        ) = Level5OperatorVerifier.verify_operator_equivalence(self.model, self.circuit)

        self.assertTrue(overall_pass, f"Diagnostics: {diagnostics}")
        self.assertEqual(op_res, 0.0)
        self.assertEqual(left_u, 0.0)
        self.assertEqual(right_u, 0.0)
        self.assertEqual(superpos_res, 0.0)
        self.assertTrue(ancilla_pass)
        self.assertTrue(phase_pass)
        self.assertTrue(reverse_pass)

    def test_02_superposition_linearity_check_pass(self) -> None:
        """Positive test: Superposition linearity check preserves linear state evolution < 1e-12."""
        report = Stage1SemanticVerifier.verify_semantic_equivalence(self.model, self.circuit)

        self.assertEqual(report.status, EquivalenceStatus.VERIFIED)
        self.assertLess(report.superposition_residual, 1e-12)

    def test_03_reverse_operator_execution_pass(self) -> None:
        """Positive test: Reverse operator U_F^dag U_F |E(C)> == |E(C)> PASSES."""
        report = Stage1SemanticVerifier.verify_semantic_equivalence(self.model, self.circuit)

        self.assertTrue(report.reverse_equivalence_pass)

    def test_04_negative_operator_mismatch_rejection(self) -> None:
        """Negative test: Rejects circuit with perturbed gate causing operator mismatch."""
        data_register = [r for r in self.circuit.registers if r.register_type != "ANCILLA"][0]
        perturbed_circuit = QuantumCircuitIR(
            circuit_id=f"{self.circuit.circuit_id}_perturbed",
            registers=self.circuit.registers,
            gates=list(self.circuit.gates) + [
                GateOperation(
                    gate_type=LogicalGateType.X,
                    target_qubit=QubitRef(data_register.register_id, 0),
                )
            ],
            ancilla_declarations=self.circuit.ancilla_declarations,
            input_register_ids=self.circuit.input_register_ids,
            output_register_ids=self.circuit.output_register_ids,
            provenance=self.circuit.provenance,
        )

        report = Stage1SemanticVerifier.verify_semantic_equivalence(self.model, perturbed_circuit)

        self.assertEqual(report.status, EquivalenceStatus.FAILED)
        self.assertEqual(report.level_5_status, EquivalenceStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
