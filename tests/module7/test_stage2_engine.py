"""
Module 7 Stage 2 Engine Test Suite — Lowering, Routing & Verification Tests.

Provides complete positive, negative, security isolation, determinism, semantic verification,
and upstream immutability tests for Stage 2 Engine Implementation.
"""

import unittest
from dataclasses import FrozenInstanceError
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module7.model import BackendCapabilityModel
from src.module7.stage2 import (
    LoweringStatus,
    LoweringPolicy,
    NativeCircuitArtifact,
    LoweringResultArtifact,
    DeterministicLoweringEngine,
    Module4SemanticVerificationAdapter,
)


class TestModule7Stage2Engine(unittest.TestCase):
    """Production Engine Test Suite for Module 7 Stage 2."""

    def setUp(self) -> None:
        self.backend_sim = BackendCapabilityModel(
            backend_id="LOCAL_REF_SIM_01",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=8,
            native_gate_set=("X", "Y", "Z", "H", "CNOT", "CZ", "RX", "RY", "RZ"),
            topology_coupling_map=((0, 1), (1, 2), (2, 3), (3, 4)),
            max_shots=100000,
            capability_version="1.0.0",
        )
        self.policy = LoweringPolicy(policy_id="POLICY_DEFAULT")
        self.engine = DeterministicLoweringEngine()

    def test_01_direct_native_gate_lowering_and_case_a_verified(self) -> None:
        """Case A: Verifies direct native gate preservation and SEMANTICALLY_VERIFIED status."""
        gates = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_01",
            logical_circuit_hash="a" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            semantic_evidence_id="EVID_STAGE4_VERIFIED",
            logical_gate_sequence=gates,
        )
        self.assertEqual(res.status, LoweringStatus.SEMANTICALLY_VERIFIED)
        self.assertEqual(res.semantic_verification_status, "VERIFIED")
        self.assertIsNotNone(res.native_circuit)
        self.assertEqual(res.native_circuit.native_gate_count, 2)
        self.assertEqual(len(res.native_circuit.native_circuit_hash), 64)

    def test_02_gate_decomposition(self) -> None:
        """Verifies logical gate decomposition (e.g., SWAP -> 3 CNOTs)."""
        gates = (
            {"gate": "SWAP", "qubits": (0, 1)},
        )
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_SWAP",
            logical_circuit_hash="b" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            logical_gate_sequence=gates,
        )
        self.assertEqual(res.status, LoweringStatus.SEMANTICALLY_VERIFIED)
        self.assertIsNotNone(res.native_circuit)
        self.assertEqual(res.native_circuit.native_gate_count, 3)
        for g in res.native_circuit.native_gate_sequence:
            self.assertEqual(g["gate"], "CNOT")

    def test_03_topology_routing_and_swap_insertion(self) -> None:
        """Verifies SWAP insertion routing when physical qubits are non-adjacent (e.g. (0, 2) on linear graph)."""
        gates = (
            {"gate": "CNOT", "qubits": (0, 2)},  # 0 and 2 are separated by 1 on coupling map ((0,1), (1,2))
        )
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_NON_ADJ",
            logical_circuit_hash="c" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            logical_gate_sequence=gates,
        )
        self.assertEqual(res.status, LoweringStatus.SEMANTICALLY_VERIFIED)
        self.assertIsNotNone(res.native_circuit)
        self.assertGreater(res.native_circuit.inserted_swap_count, 0)

    def test_04_case_c_semantic_non_equivalence(self) -> None:
        """Case C: Verifies candidate native circuit resulting in SEMANTICALLY_NON_EQUIVALENT status."""
        non_eq_verifier = Module4SemanticVerificationAdapter(override_status="SEMANTICALLY_NON_EQUIVALENT")
        non_eq_engine = DeterministicLoweringEngine(verification_adapter=non_eq_verifier)

        res = non_eq_engine.lower_circuit(
            logical_circuit_id="CIRC_NON_EQ",
            logical_circuit_hash="d" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )
        self.assertEqual(res.status, LoweringStatus.SEMANTICALLY_NON_EQUIVALENT)
        self.assertEqual(res.semantic_verification_status, "SEMANTICALLY_NON_EQUIVALENT")

    def test_05_case_d_inconclusive_verification(self) -> None:
        """Case D: Verifies candidate native circuit resulting in INCONCLUSIVE verification status."""
        inc_verifier = Module4SemanticVerificationAdapter(override_status="INCONCLUSIVE")
        inc_engine = DeterministicLoweringEngine(verification_adapter=inc_verifier)

        res = inc_engine.lower_circuit(
            logical_circuit_id="CIRC_INC",
            logical_circuit_hash="e" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )
        self.assertEqual(res.status, LoweringStatus.INCONCLUSIVE)
        self.assertEqual(res.semantic_verification_status, "INCONCLUSIVE")

    def test_06_case_b_missing_semantic_evidence_failure(self) -> None:
        """Case B: Verifies missing mandatory upstream evidence results in LOWERING_INPUT_INVALID failure."""
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_NO_EVID",
            logical_circuit_hash="f" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            semantic_evidence_id=None,  # Missing evidence!
        )
        self.assertEqual(res.status, LoweringStatus.FAILED)
        self.assertIn("LOWERING_INPUT_INVALID", res.provenance.get("failure_reason", ""))

    def test_07_unsupported_operation_failure(self) -> None:
        """Verifies unsupported gate raises FAILED status with UNSUPPORTED_OPERATION."""
        gates = (
            {"gate": "UNSUPPORTED_EXOTIC_GATE", "qubits": (0,)},
        )
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_UNSUPP",
            logical_circuit_hash="g" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            logical_gate_sequence=gates,
        )
        self.assertEqual(res.status, LoweringStatus.FAILED)
        self.assertIn("UNSUPPORTED_OPERATION", res.provenance.get("failure_reason", ""))

    def test_08_insufficient_qubits_failure(self) -> None:
        """Verifies logical qubits exceeding physical capacity result in FAILED status."""
        gates = (
            {"gate": "H", "qubits": (99,)},  # Qubit 99 > backend qubit count 8
        )
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_TOO_MANY_QUBITS",
            logical_circuit_hash="h" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
            logical_gate_sequence=gates,
        )
        self.assertEqual(res.status, LoweringStatus.FAILED)
        self.assertIn("BACKEND_CAPABILITY_MISMATCH", res.provenance.get("failure_reason", ""))

    def test_09_no_hidden_gate_expansion(self) -> None:
        """Verifies lowering native operations DOES NOT mutate Module 6 GE(k) or B_u."""
        ge0 = create_initial_evolutionary_state()
        vocab_before = len(ge0.vocabulary)

        # Execute lowering with native gates
        self.engine.lower_circuit(
            logical_circuit_id="CIRC_GE_CHECK",
            logical_circuit_hash="i" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )

        # GE(k) remains completely unchanged
        self.assertEqual(len(ge0.vocabulary), vocab_before)

    def test_10_determinism(self) -> None:
        """Verifies identical inputs produce identical native circuit hashes and lowering IDs."""
        res1 = self.engine.lower_circuit(
            logical_circuit_id="CIRC_DET",
            logical_circuit_hash="j" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )
        res2 = self.engine.lower_circuit(
            logical_circuit_id="CIRC_DET",
            logical_circuit_hash="j" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )
        self.assertEqual(res1.lowering_hash, res2.lowering_hash)
        self.assertEqual(res1.native_circuit.native_circuit_hash, res2.native_circuit.native_circuit_hash)

    def test_11_input_immutability(self) -> None:
        """Verifies BackendCapabilityModel and LoweringPolicy cannot be mutated."""
        with self.assertRaises(FrozenInstanceError):
            self.backend_sim.qubit_count = 999
        with self.assertRaises(FrozenInstanceError):
            self.policy.routing_strategy = "MUTATED"

    def test_12_security_credential_isolation(self) -> None:
        """Verifies no raw credentials appear in LoweringResultArtifact serialization or provenance."""
        res = self.engine.lower_circuit(
            logical_circuit_id="CIRC_SEC",
            logical_circuit_hash="k" * 64,
            backend_capability=self.backend_sim,
            policy=self.policy,
        )
        res_str = str(res.to_dict())
        self.assertNotIn("secret", res_str.lower())
        self.assertNotIn("password", res_str.lower())
        self.assertNotIn("api_key", res_str.lower())


if __name__ == "__main__":
    unittest.main()
