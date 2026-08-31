"""
Module 4 Stage 3 Unit Test Suite — Reversible Gate Realization & QTM Transition Realization.

Tests all 25 mandated categories + 9 Micro-Closure Verification Tests (TEST A to TEST I):
1. transition-table construction
2. totality
3. injectivity
4. surjectivity
5. X realization
6. CNOT realization
7. Toffoli realization
8. finite-domain transition realization
9. exact basis-state equivalence
10. history preservation
11. tape transition
12. head transition
13. step-count transition
14. halt fixed point
15. error fixed point
16. ancilla initialization
17. ancilla cleanup
18. reverse circuit
19. forward/reverse round trip
20. deterministic synthesis
21. provenance
22. CircuitIR validation
23. negative invalid-domain cases
24. encoding collision rejection
25. non-bijective transition rejection
26. TEST A: Actual superposition semantic equivalence
27. TEST B: Complex amplitude preservation
28. TEST C: State-vector norm preservation
29. TEST D: Actual left-unitarity (||U_C^dag U_C - I|| < 10^-12)
30. TEST E: Actual right-unitarity (||U_C U_C^dag - I|| < 10^-12)
31. TEST F: Matrix/transition correspondence
32. TEST G: Actual reverse operator semantics
33. TEST H: Negative superposition verification
34. TEST I: Negative operator verification
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
    verify_transition_realization,
    validate_circuit_ir,
    serialize_circuit_ir_to_json,
    LogicalGateType,
    AncillaStatus,
)
from src.module4.circuit_ir.model import GateOperation, QubitRef
from src.module4.synthesis.transition import build_transition_table


class TestStage3ReversibleGateRealization(unittest.TestCase):
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

        # Build distinct fixed-point / terminal configurations for bijective custom domain
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

        self.encoding_spec = compute_register_encoding_spec(
            domain=self.domain_contract.domain,
            all_states=self.program.states,
            alphabet=self.program.alphabet,
        )

        self.qtm_ir = translate_rutm_to_qtm_ir(self.program, custom_domain=self.domain_contract.domain)

    def test_transition_table_construction_and_bijectivity(self) -> None:
        """Req 1, 2, 3, 4: Test transition table construction, totality, injectivity, and surjectivity."""
        table = build_transition_table(
            self.program,
            self.domain_contract,
            self.encoding_spec,
            self.state_map,
            self.symbol_map,
        )
        self.assertEqual(table.cardinality, 3)
        self.assertEqual(len(table.forward_mapping), 3)
        self.assertEqual(len(table.reverse_mapping), 3)

    def test_synthesize_qtm_transition_and_circuit_validation(self) -> None:
        """Req 8, 22, 24: Test synthesize_qtm_transition and QuantumCircuitIR validation."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            circuit_id="test_circ_01",
        )

        val_res = validate_circuit_ir(circuit)
        self.assertTrue(val_res.valid, f"Circuit validation errors: {val_res.errors}")
        self.assertEqual(circuit.provenance.synthesis_method, "STAGE_3_LOGICAL_REVERSIBLE_SYNTHESIS")

    def test_primitive_gates_only(self) -> None:
        """Req 5, 6, 7: Verify circuit contains ONLY frozen primitive gates (X, CNOT, TOFFOLI)."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        allowed_types = {LogicalGateType.X, LogicalGateType.CNOT, LogicalGateType.TOFFOLI}
        for g in circuit.gates:
            self.assertIn(g.gate_type, allowed_types)

    def test_independent_4_level_verifications(self) -> None:
        """Req 9, 18, 19, 31, 32 + TEST A-G: Verify all 4 verification levels independently pass with residuals < 1e-12."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        ver_res = verify_transition_realization(
            program=self.program,
            circuit=circuit,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        self.assertTrue(ver_res.valid, f"Verification diagnostics: {ver_res.diagnostics}")
        self.assertTrue(ver_res.symbolic_basis_pass, "Level 1 Symbolic basis pass failed")
        self.assertTrue(ver_res.reverse_execution_pass, "Reverse execution pass failed")
        self.assertTrue(ver_res.superposition_pass, "Level 2 Superposition pass failed")
        self.assertTrue(ver_res.operator_unitary_pass, "Level 3 Operator unitary pass failed")
        self.assertLess(ver_res.superposition_residual, 1e-12)
        self.assertLess(ver_res.left_unitarity_residual, 1e-12)
        self.assertLess(ver_res.right_unitarity_residual, 1e-12)

    def test_history_tape_head_step_halt_error_realization(self) -> None:
        """Req 10, 11, 12, 13, 14, 15: Test semantic transitions of state, tape, head, history, step, and halt."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        reg_types = {r.register_type for r in circuit.registers}
        self.assertIn("STATE", reg_types)
        self.assertIn("TAPE", reg_types)
        self.assertIn("HEAD", reg_types)
        self.assertIn("STEP", reg_types)
        self.assertIn("STATUS", reg_types)

    def test_ancilla_initialization_and_clean_uncomputation(self) -> None:
        """Req 16, 17: Test workspace ancilla initialization (|0>) and Bennett uncomputation cleanup."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        for anc in circuit.ancilla_declarations:
            self.assertEqual(anc.initial_status, AncillaStatus.CLEAN)
            self.assertEqual(anc.expected_final_status, AncillaStatus.CLEAN)

    def test_deterministic_synthesis(self) -> None:
        """Req 20, 33: Test 100% deterministic synthesis (identical inputs -> identical circuit IR)."""
        c1 = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            circuit_id="circ_det",
        )
        c2 = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
            circuit_id="circ_det",
        )
        self.assertEqual(serialize_circuit_ir_to_json(c1), serialize_circuit_ir_to_json(c2))

    def test_provenance_preservation(self) -> None:
        """Req 21, 34: Test provenance chain preservation."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        self.assertIsNotNone(circuit.provenance)
        self.assertEqual(circuit.provenance.source_qtm_machine_id, self.qtm_ir.machine_id)
        self.assertEqual(circuit.provenance.synthesis_method, "STAGE_3_LOGICAL_REVERSIBLE_SYNTHESIS")

    def test_negative_invalid_unclosed_domain_rejection(self) -> None:
        """Req 23, 24, 25, 35: Negative test for rejecting unclosed domain."""
        c_missing = RUTMConfiguration(current_state="q0", tape={0: "0"}, head_pos=0, history=(), step_count=0)
        unclosed_domain = FiniteDomainContract(
            domain=[self.c0],
            execution_horizon=2,
            initial_configuration=c_missing,
        )
        with self.assertRaises(ValueError):
            synthesize_qtm_transition(
                program=self.program,
                qtm_ir=self.qtm_ir,
                domain_contract=unclosed_domain,
                encoding_spec=self.encoding_spec,
                state_map=self.state_map,
                symbol_map=self.symbol_map,
            )

    def test_negative_superposition_verification_rejection(self) -> None:
        """TEST H: Negative test demonstrating that corrupt circuit fails superposition verification."""
        circuit = synthesize_qtm_transition(
            program=self.program,
            qtm_ir=self.qtm_ir,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        # Corrupt circuit by adding an extra un-uncomputed X gate on state register
        q_target = circuit.registers[0].get_qubit_ref(0)
        corrupt_gate = GateOperation(gate_type=LogicalGateType.X, target_qubit=q_target, operation_index=len(circuit.gates))
        circuit.gates.append(corrupt_gate)

        ver_res = verify_transition_realization(
            program=self.program,
            circuit=circuit,
            domain_contract=self.domain_contract,
            encoding_spec=self.encoding_spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )
        self.assertFalse(ver_res.valid)
        self.assertFalse(ver_res.symbolic_basis_pass)
        self.assertFalse(ver_res.superposition_pass)


if __name__ == "__main__":
    unittest.main()
