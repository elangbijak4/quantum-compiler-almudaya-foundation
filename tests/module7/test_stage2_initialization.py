"""
Module 7 Stage 2 Test Suite — Initialization & Lowering Data Contract Verification.
"""

import unittest
from src.module7.stage2 import (
    LoweringStatus,
    LoweringPolicy,
    NativeCircuitArtifact,
    LoweringResultArtifact,
)


class TestModule7Stage2Initialization(unittest.TestCase):
    """Tests verifying Stage 2 foundational type contracts, policy hashing, and immutability."""

    def test_01_lowering_policy_hashing(self) -> None:
        """Verifies LoweringPolicy SHA-256 policy_hash computation determinism."""
        p1 = LoweringPolicy(policy_id="POLICY_DEFAULT")
        p2 = LoweringPolicy(policy_id="POLICY_DEFAULT")
        self.assertEqual(len(p1.policy_hash), 64)
        self.assertEqual(p1.policy_hash, p2.policy_hash)

    def test_02_native_circuit_artifact_hashing(self) -> None:
        """Verifies NativeCircuitArtifact canonical SHA-256 digest computation."""
        native_art = NativeCircuitArtifact(
            native_circuit_id="NAT_CIRC_01",
            backend_id="LOCAL_REF_SIM_01",
            capability_hash="a" * 64,
            native_gate_sequence=({"gate": "H", "qubits": (0,)}, {"gate": "CNOT", "qubits": (0, 1)}),
            qubit_mapping={0: 0, 1: 1},
            native_gate_count=2,
            circuit_depth=2,
            inserted_swap_count=0,
        )
        self.assertEqual(len(native_art.native_circuit_hash), 64)
        self.assertEqual(native_art.native_gate_count, 2)

    def test_03_lowering_result_artifact_integrity(self) -> None:
        """Verifies LoweringResultArtifact fields and status representation."""
        res_art = LoweringResultArtifact(
            lowering_id="LOWER_01",
            logical_circuit_id="LOGIC_CIRC_01",
            logical_circuit_hash="b" * 64,
            backend_id="LOCAL_REF_SIM_01",
            capability_version="1.0.0",
            capability_hash="a" * 64,
            policy_hash="c" * 64,
            status=LoweringStatus.SEMANTICALLY_VERIFIED,
            native_circuit=None,
            qubit_mapping={0: 0, 1: 1},
            semantic_verification_status="VERIFIED",
        )
        self.assertEqual(res_art.status.value, "SEMANTICALLY_VERIFIED")
        self.assertEqual(len(res_art.lowering_hash), 64)


if __name__ == "__main__":
    unittest.main()
