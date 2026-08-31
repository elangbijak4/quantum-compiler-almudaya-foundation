"""
Module 4 Stage 1 Unit Test Suite — Finite Realization Foundation.

Tests:
1. Finite domain contract validation & cardinality
2. Forward closure (R_P(D_fin) ⊆ D_fin) & Reverse closure (R_P^{-1}(D_fin) ⊆ D_fin)
3. Configuration encoding injectivity (C1 != C2 => E(C1) != E(C2))
4. Configuration identity & history preservation (H1 != H2 => E(C1) != E(C2))
5. Finite Hilbert dimension relation (|D_fin| <= 2^n)
6. Computational basis orthogonality (<E(C1)|E(C2)> = \delta_{C1, C2})
7. Canonical primitive gate specifications (Toffoli, CNOT, X)
8. 3-level verification policy & numerical tolerance (\epsilon = 10^{-12})
9. Invalid realization classification
"""

import unittest
from typing import Set, Dict
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module4 import (
    FiniteDomainContract,
    compute_register_encoding_spec,
    encode_configuration,
    verify_encoding_injectivity,
    FiniteHilbertEmbedding,
    RestrictedUnitaryContract,
    LogicalPrimitiveGateType,
    LogicalPrimitiveGate,
    NUMERICAL_VERIFICATION_TOLERANCE,
    VerificationLevel,
    VerificationPolicy,
)


class TestStage1Foundation(unittest.TestCase):
    def setUp(self) -> None:
        # Standard reversible increment program
        self.program = UTMProgram(
            states={"q0", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions={
                ("q0", "0"): TransitionAction(next_state="q_halt", write_symbol="1", direction=Direction.RIGHT),
            },
        )
        self.c0 = RUTMConfiguration(current_state="q0", tape={0: "0"}, head_pos=0, history=(), step_count=0, halted=False)
        self.c1 = forward_step_rutm(self.c0, self.program)

        self.state_map = {"q0": 0, "q_halt": 1}
        self.symbol_map = {"_": 0, "0": 1, "1": 2}

    def test_finite_domain_contract_closure(self) -> None:
        """Req 3 & 26: Test finite domain contract validation and forward/reverse closure."""
        domain_contract = FiniteDomainContract(
            domain=[self.c0, self.c1],
            execution_horizon=1,
            initial_configuration=self.c0,
        )
        res = domain_contract.validate(self.program)
        self.assertTrue(res.valid)
        self.assertTrue(res.forward_closed)
        self.assertTrue(res.reverse_closed)
        self.assertTrue(res.contains_initial)
        self.assertEqual(res.cardinality, 2)

    def test_invalid_domain_unclosed(self) -> None:
        """Req 3 & 22: Test rejection of unclosed finite domain."""
        unclosed_contract = FiniteDomainContract(
            domain=[self.c0],  # Missing c1!
            execution_horizon=1,
            initial_configuration=self.c0,
        )
        res = unclosed_contract.validate(self.program)
        self.assertFalse(res.valid)
        self.assertFalse(res.forward_closed)

    def test_encoding_injectivity(self) -> None:
        """Req 5 & 26: Test encoding injectivity C1 != C2 => E(C1) != E(C2)."""
        domain = [self.c0, self.c1]
        spec = compute_register_encoding_spec(domain, self.program.states, self.program.alphabet)

        e0 = encode_configuration(self.c0, spec, self.state_map, self.symbol_map)
        e1 = encode_configuration(self.c1, spec, self.state_map, self.symbol_map)

        self.assertNotEqual(e0, e1)
        self.assertTrue(verify_encoding_injectivity(domain, spec, self.state_map, self.symbol_map))

    def test_history_preservation(self) -> None:
        """Req 6 & 9: Test history identity preservation H1 != H2 => E(C1) != E(C2)."""
        c0_hist1 = RUTMConfiguration(current_state="q0", tape={0: "0"}, head_pos=0, history=((1, "old"),), step_count=0)
        c0_hist2 = RUTMConfiguration(current_state="q0", tape={0: "0"}, head_pos=0, history=((2, "different"),), step_count=0)

        domain = [c0_hist1, c0_hist2]
        spec = compute_register_encoding_spec(domain, self.program.states, self.program.alphabet)

        e_h1 = encode_configuration(c0_hist1, spec, self.state_map, self.symbol_map)
        e_h2 = encode_configuration(c0_hist2, spec, self.state_map, self.symbol_map)

        self.assertNotEqual(e_h1, e_h2)

    def test_finite_hilbert_embedding_and_orthogonality(self) -> None:
        """Req 11 & 26: Test finite Hilbert embedding iota_fin and computational basis orthogonality."""
        domain_contract = FiniteDomainContract(domain=[self.c0, self.c1], execution_horizon=1)
        spec = compute_register_encoding_spec(domain_contract.domain, self.program.states, self.program.alphabet)

        embedding = FiniteHilbertEmbedding(
            domain_contract=domain_contract,
            encoding_spec=spec,
            state_map=self.state_map,
            symbol_map=self.symbol_map,
        )

        b0 = embedding.embed_basis_state(self.c0)
        b1 = embedding.embed_basis_state(self.c1)

        self.assertIsInstance(b0, str)
        self.assertEqual(len(b0), spec.total_qubits)
        self.assertTrue(embedding.verify_orthogonality())

    def test_restricted_unitary_contract(self) -> None:
        """Req 12 & 15: Test restricted unitary contract bijectivity."""
        domain_contract = FiniteDomainContract(domain=[self.c0, self.c1], execution_horizon=1)
        spec = compute_register_encoding_spec(domain_contract.domain, self.program.states, self.program.alphabet)
        embedding = FiniteHilbertEmbedding(domain_contract=domain_contract, encoding_spec=spec, state_map=self.state_map, symbol_map=self.symbol_map)

        contract = RestrictedUnitaryContract(embedding=embedding)
        self.assertTrue(contract.is_unitary())
        self.assertGreaterEqual(contract.target_dimension, domain_contract.cardinality)

    def test_canonical_logical_gates(self) -> None:
        """Req 16: Test canonical logical primitive gates (Toffoli, CNOT, X)."""
        x_gate = LogicalPrimitiveGate(gate_type=LogicalPrimitiveGateType.X, control_qubits=(), target_qubit=0)
        cnot_gate = LogicalPrimitiveGate(gate_type=LogicalPrimitiveGateType.CNOT, control_qubits=(0,), target_qubit=1)
        toffoli_gate = LogicalPrimitiveGate(gate_type=LogicalPrimitiveGateType.TOFFOLI, control_qubits=(0, 1), target_qubit=2)

        self.assertEqual(x_gate.gate_type, LogicalPrimitiveGateType.X)
        self.assertEqual(cnot_gate.gate_type, LogicalPrimitiveGateType.CNOT)
        self.assertEqual(toffoli_gate.gate_type, LogicalPrimitiveGateType.TOFFOLI)

        # Invalid gate specifications
        with self.assertRaises(ValueError):
            LogicalPrimitiveGate(gate_type=LogicalPrimitiveGateType.CNOT, control_qubits=(), target_qubit=1)

    def test_verification_policy_and_tolerance(self) -> None:
        """Req 19: Test 3-level verification policy and numerical tolerance epsilon = 10^-12."""
        policy = VerificationPolicy(primary_level=VerificationLevel.LEVEL_1_SYMBOLIC_BASIS)
        self.assertEqual(policy.tolerance, 1e-12)
        self.assertTrue(policy.is_within_tolerance(1e-15))
        self.assertFalse(policy.is_within_tolerance(1e-10))


if __name__ == "__main__":
    unittest.main()
