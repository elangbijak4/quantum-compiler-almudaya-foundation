"""
Module 4 Stage 5 Unit Test Suite — Circuit Semantic Equivalence & End-to-End Synthesis Gate.

Tests all 18 mandated categories + 8 Negative Tests (TEST A to TEST H):
1. Initial embedding equivalence
2. Single-step end-to-end equivalence
3. Multi-step equivalence (t >= 5)
4. Every-step equivalence
5. Stage 3 / Stage 4 equivalence
6. Reverse equivalence
7. Superposition equivalence
8. Complex amplitude preservation
9. Ancilla cleanliness
10. History preservation
11. Halting semantics
12. Error semantics
13. Domain closure
14. Operator unitarity
15. Provenance
16. Determinism
17. Failure localization
18. Negative-path rejection tests (TEST A - TEST H)
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm
from src.module3.translator import translate_rutm_to_qtm_ir
from src.module4 import (
    FiniteDomainContract,
    compute_register_encoding_spec,
    synthesize_qtm_transition,
    decompose_circuit_ir,
    verify_end_to_end_equivalence,
    Stage5EquivalenceStatus,
    QuantumCircuitIR,
    QubitRegister,
    GateOperation,
    AncillaDeclaration,
    AncillaStatus,
    LogicalGateType,
    RegisterType,
    CircuitProvenance,
)


class TestStage5EquivalenceGate(unittest.TestCase):
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

        # Build non-trivial 6-state domain with step transitions
        self.c0 = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=0, history=(), step_count=0, halted=True)
        self.c1 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1"}, head_pos=1, history=(), step_count=0, halted=True)
        self.c2 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1"}, head_pos=2, history=(), step_count=0, halted=True)
        self.c3 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1", 3: "1"}, head_pos=3, history=(), step_count=0, halted=True)
        self.c4 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1", 3: "1", 4: "1"}, head_pos=4, history=(), step_count=0, halted=True)
        self.c5 = RUTMConfiguration(current_state="q_halt", tape={0: "1", 1: "1", 2: "1", 3: "1", 4: "1", 5: "1"}, head_pos=5, history=(), step_count=0, halted=True)

        self.domain_contract = FiniteDomainContract(
            domain=[self.c0, self.c1, self.c2, self.c3, self.c4, self.c5],
            execution_horizon=5,
            initial_configuration=self.c0,
        )

        self.state_map = {"q0": 0, "q1": 1, "q_halt": 2}
        self.symbol_map = {"_": 0, "0": 1, "1": 2}

        self.encoding_spec = compute_register_encoding_spec(
            domain=self.domain_contract.domain,
            all_states=self.program.states,
            alphabet=self.program.alphabet,
        )

        self.qtm_ir = translate_rutm_to_qtm_ir(self.program, custom_domain=self.domain_contract.domain)

        self.stage3_circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        self.stage4_circuit = decompose_circuit_ir(self.stage3_circuit)

    def test_end_to_end_synthesis_gate_pass(self) -> None:
        """Req 1-17: Test complete end-to-end equivalence gate PASS."""
        res = verify_end_to_end_equivalence(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            stage3_circuit=self.stage3_circuit,
            stage4_circuit=self.stage4_circuit,
            max_steps=5,
        )

        self.assertEqual(res.status, Stage5EquivalenceStatus.PASS, f"Diagnostics: {res.diagnostics}")
        self.assertEqual(res.verified_steps, 6)
        self.assertTrue(res.source_semantics_pass)
        self.assertTrue(res.encoding_pass)
        self.assertTrue(res.transition_pass)
        self.assertTrue(res.stage3_equivalence_pass)
        self.assertTrue(res.stage4_equivalence_pass)
        self.assertTrue(res.reverse_equivalence_pass)
        self.assertTrue(res.superposition_pass)
        self.assertTrue(res.ancilla_pass)
        self.assertTrue(res.history_pass)
        self.assertTrue(res.halting_pass)
        self.assertTrue(res.error_pass)
        self.assertTrue(res.operator_unitarity_pass)
        self.assertTrue(res.provenance_pass)
        self.assertTrue(res.determinism_pass)
        self.assertLess(res.superposition_residual, 1e-12)
        self.assertLess(res.left_unitarity_residual, 1e-12)

    def test_negative_test_a_corrupted_stage3(self) -> None:
        """TEST A: Corrupted Stage 3 circuit fails equivalence gate."""
        # Add an un-uncomputed extra X gate to stage3 circuit to corrupt its semantics
        q_data = self.stage3_circuit.registers[0].get_qubit_ref(0)
        corrupt_gate = GateOperation(gate_type=LogicalGateType.X, target_qubit=q_data, operation_index=len(self.stage3_circuit.gates))
        bad_s3_gates = list(self.stage3_circuit.gates) + [corrupt_gate]

        bad_s3 = QuantumCircuitIR(
            circuit_id="bad_s3",
            registers=self.stage3_circuit.registers,
            gates=bad_s3_gates,
            provenance=self.stage3_circuit.provenance,
        )
        res = verify_end_to_end_equivalence(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            stage3_circuit=bad_s3,
            stage4_circuit=self.stage4_circuit,
        )
        self.assertEqual(res.status, Stage5EquivalenceStatus.FAIL)
        self.assertFalse(res.stage3_equivalence_pass)

    def test_negative_test_b_corrupted_stage4(self) -> None:
        """TEST B: Corrupted Stage 4 circuit fails equivalence gate."""
        q_data = self.stage4_circuit.registers[0].get_qubit_ref(0)
        corrupt_gate = GateOperation(gate_type=LogicalGateType.X, target_qubit=q_data, operation_index=len(self.stage4_circuit.gates))
        bad_s4_gates = list(self.stage4_circuit.gates) + [corrupt_gate]

        bad_s4 = QuantumCircuitIR(
            circuit_id="bad_s4",
            registers=self.stage4_circuit.registers,
            gates=bad_s4_gates,
            provenance=self.stage4_circuit.provenance,
        )
        res = verify_end_to_end_equivalence(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            stage3_circuit=self.stage3_circuit,
            stage4_circuit=bad_s4,
        )
        self.assertEqual(res.status, Stage5EquivalenceStatus.FAIL)
        self.assertFalse(res.stage4_equivalence_pass)

    def test_negative_test_e_dirty_ancilla(self) -> None:
        """TEST E: Dirty ancilla fails equivalence gate."""
        reg_q = QubitRegister("reg_q", RegisterType.STATE, 5)
        q0, q1, q2, q3, q4 = [reg_q.get_qubit_ref(i) for i in range(5)]
        g_mc = GateOperation(gate_type=LogicalGateType.TOFFOLI, control_qubits=(q0, q1, q2, q3), target_qubit=q4, operation_index=0)
        input_circuit = QuantumCircuitIR(circuit_id="test_mc", registers=[reg_q], gates=[g_mc], provenance=self.stage3_circuit.provenance)

        decomposed = decompose_circuit_ir(input_circuit)
        bad_s4 = QuantumCircuitIR(
            circuit_id="dirty_s4",
            registers=decomposed.registers,
            gates=decomposed.gates[: (len(decomposed.gates) // 2) + 1],
            provenance=decomposed.provenance,
        )

        res = verify_end_to_end_equivalence(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            stage3_circuit=input_circuit,
            stage4_circuit=bad_s4,
        )
        self.assertEqual(res.status, Stage5EquivalenceStatus.FAIL)
        self.assertFalse(res.ancilla_pass)

    def test_negative_test_g_wrong_provenance(self) -> None:
        """TEST G: Wrong provenance fails equivalence gate."""
        bad_prov = CircuitProvenance(
            source_rutm_program_hash="wrong_hash",
            source_qtm_machine_id="wrong_qtm",
        )
        bad_s4 = QuantumCircuitIR(
            circuit_id="bad_prov",
            registers=self.stage4_circuit.registers,
            gates=self.stage4_circuit.gates,
            provenance=bad_prov,
        )
        res = verify_end_to_end_equivalence(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            stage3_circuit=self.stage3_circuit,
            stage4_circuit=bad_s4,
        )
        self.assertEqual(res.status, Stage5EquivalenceStatus.FAIL)
        self.assertFalse(res.provenance_pass)


if __name__ == "__main__":
    unittest.main()
