"""
Module 6 Stage 1 Unit Test Suite — Level 3 Computational-Basis Semantic Equivalence.

Tests Level 3 basis equivalence verification, fixed-point preservation, halting & error categories,
and negative failure path rejection.
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4 import FiniteDomainContract
from src.module4.circuit_ir.model import QuantumCircuitIR, GateOperation, LogicalGateType, QubitRef
from src.module6 import (
    build_classical_semantic_model,
    CompilerMapper,
    Level3BasisVerifier,
    Stage1SemanticVerifier,
    EquivalenceStatus,
    FailureCode,
)


class TestStage1BasisEquivalence(unittest.TestCase):
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
            self.program, self.domain_contract, self.state_map, self.symbol_map, "basis_alg"
        )
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_level3_basis_equivalence_pass(self) -> None:
        """Positive test: Level 3 basis equivalence PASSES over all C in D_fin."""
        all_passed, records, diagnostics = Level3BasisVerifier.verify_basis_equivalence(
            self.model, self.circuit
        )

        self.assertTrue(all_passed, f"Diagnostics: {diagnostics}")
        self.assertEqual(len(records), 3)
        for r in records:
            self.assertTrue(r.passed)
            self.assertEqual(r.residual_l2, 0.0)

    def test_02_halting_fixed_point_preservation(self) -> None:
        """Positive test: Halting fixed point configuration preserves exact state under U_F."""
        all_passed, records, _ = Level3BasisVerifier.verify_basis_equivalence(
            self.model, self.circuit
        )

        halting_records = [r for r in records if r.config_category == "HALTING"]
        self.assertTrue(len(halting_records) > 0)
        for r in halting_records:
            self.assertTrue(r.passed)

    def test_03_negative_dirty_ancilla_rejection(self) -> None:
        """Negative test: Rejects circuit if an extra X gate leaves a workspace ancilla dirty."""
        ancilla_register = [r for r in self.circuit.registers if r.register_type == "ANCILLA"][0]
        dirty_circuit = QuantumCircuitIR(
            circuit_id=f"{self.circuit.circuit_id}_dirty",
            registers=self.circuit.registers,
            gates=list(self.circuit.gates) + [
                GateOperation(
                    gate_type=LogicalGateType.X,
                    target_qubit=QubitRef(ancilla_register.register_id, 0),
                )
            ],
            ancilla_declarations=self.circuit.ancilla_declarations,
            input_register_ids=self.circuit.input_register_ids,
            output_register_ids=self.circuit.output_register_ids,
            provenance=self.circuit.provenance,
        )

        report = Stage1SemanticVerifier.verify_semantic_equivalence(self.model, dirty_circuit)

        self.assertEqual(report.status, EquivalenceStatus.FAILED)
        self.assertFalse(report.ancilla_cleanliness_pass)
        self.assertEqual(report.failure_code, FailureCode.ANCILLA_CLEANLINESS_FAILURE)

    def test_04_negative_data_mismatch_rejection(self) -> None:
        """Negative test: Rejects circuit if an extra X gate corrupts data output."""
        data_register = [r for r in self.circuit.registers if r.register_type != "ANCILLA"][0]
        corrupt_circuit = QuantumCircuitIR(
            circuit_id=f"{self.circuit.circuit_id}_corrupt",
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

        report = Stage1SemanticVerifier.verify_semantic_equivalence(self.model, corrupt_circuit)

        self.assertEqual(report.status, EquivalenceStatus.FAILED)
        self.assertEqual(report.level_3_status, EquivalenceStatus.FAILED)
        self.assertEqual(report.failure_code, FailureCode.BASIS_EQUIVALENCE_FAILURE)


if __name__ == "__main__":
    unittest.main()
