"""
Module 7 Test Suite — Initialization & Data Contract Verification.
"""

import unittest
from src.module7.model import (
    ExecutionLifecycleStatus,
    ExecutionFailureCategory,
    CredentialReference,
    BackendCapabilityModel,
    LoweringResult,
    ExecutionJobResult,
)


class TestModule7Initialization(unittest.TestCase):
    """Tests verifying Module 7 foundational types, capability models, and credential privacy."""

    def test_01_backend_capability_model_hashing(self) -> None:
        """Verifies BackendCapabilityModel SHA-256 hash computation determinism."""
        cap1 = BackendCapabilityModel(
            backend_id="LOCAL_SIM_01",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=8,
            native_gate_set=("X", "Y", "Z", "H", "CNOT"),
            topology_coupling_map=((0, 1), (1, 2), (2, 3)),
            max_shots=10000,
        )
        cap2 = BackendCapabilityModel(
            backend_id="LOCAL_SIM_01",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=8,
            native_gate_set=("X", "Y", "Z", "H", "CNOT"),
            topology_coupling_map=((0, 1), (1, 2), (2, 3)),
            max_shots=10000,
        )
        self.assertEqual(len(cap1.capability_hash), 64)
        self.assertEqual(cap1.capability_hash, cap2.capability_hash)

    def test_02_credential_reference_privacy(self) -> None:
        """Verifies CredentialReference stores non-sensitive reference identifiers only."""
        cred = CredentialReference(
            credential_ref="env:IBM_QUANTUM_TOKEN",
            provider_id="IBM",
        )
        cdict = cred.to_dict()
        self.assertEqual(cdict["credential_ref"], "env:IBM_QUANTUM_TOKEN")
        self.assertEqual(cdict["provider_id"], "IBM")
        self.assertNotIn("secret", str(cdict).lower())
        self.assertNotIn("password", str(cdict).lower())

    def test_03_enum_classifications(self) -> None:
        """Verifies ExecutionLifecycleStatus and ExecutionFailureCategory enums."""
        self.assertEqual(ExecutionLifecycleStatus.COMPLETED.value, "COMPLETED")
        self.assertEqual(ExecutionFailureCategory.BACKEND_UNSUPPORTED.value, "BACKEND_UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
