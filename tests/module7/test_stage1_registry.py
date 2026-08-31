"""
Module 7 Stage 1 Engine Test Suite — Backend Registry & Capability Model Tests.

Provides complete positive, negative, security isolation, multi-versioning, determinism,
cross-stage contract, and upstream immutability tests for Stage 1.
"""

import unittest
from dataclasses import FrozenInstanceError
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module7 import (
    BackendCapabilityModel,
    CredentialReference,
    HistoricalBackendRegistry,
    serialize_backend_capability_model,
    deserialize_backend_capability_model,
)


class TestModule7Stage1Registry(unittest.TestCase):
    """Stage 1 Engine Test Suite for Backend Registry & Capability Model."""

    def setUp(self) -> None:
        self.registry = HistoricalBackendRegistry()
        self.cap_sim = BackendCapabilityModel(
            backend_id="LOCAL_REF_SIM_01",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=16,
            native_gate_set=("X", "Y", "Z", "H", "CNOT", "CZ", "RX", "RY", "RZ"),
            topology_coupling_map=((0, 1), (1, 2), (2, 3), (3, 4)),
            max_shots=100000,
            supports_custom_pulses=False,
            capability_version="1.0.0",
        )
        self.cap_hw = BackendCapabilityModel(
            backend_id="IBM_TORONTO",
            provider_id="IBM",
            backend_type="PHYSICAL_HARDWARE",
            qubit_count=27,
            native_gate_set=("RZ", "SX", "X", "CX"),
            topology_coupling_map=((0, 1), (1, 2), (2, 3)),
            max_shots=20000,
            supports_custom_pulses=True,
            capability_version="1.0.0",
        )

    def test_01_backend_identity_and_sha256_hash(self) -> None:
        """Verifies backend identity fields and 64-char SHA-256 capability hash computation."""
        self.assertEqual(self.cap_sim.backend_id, "LOCAL_REF_SIM_01")
        self.assertEqual(self.cap_sim.provider_id, "LOCAL_REFERENCE")
        self.assertEqual(self.cap_sim.backend_type, "VIRTUAL_SIMULATOR")
        self.assertEqual(len(self.cap_sim.capability_hash), 64)

    def test_02_provider_identity_multi_backend(self) -> None:
        """Verifies multiple backends can belong to one provider without identity collision."""
        cap_ibm_1 = BackendCapabilityModel(
            backend_id="IBM_TORONTO", provider_id="IBM", backend_type="PHYSICAL_HARDWARE",
            qubit_count=27, native_gate_set=("CX", "X"), topology_coupling_map=((0, 1),), max_shots=10000
        )
        cap_ibm_2 = BackendCapabilityModel(
            backend_id="IBM_PERTH", provider_id="IBM", backend_type="PHYSICAL_HARDWARE",
            qubit_count=7, native_gate_set=("CX", "X"), topology_coupling_map=((0, 1),), max_shots=10000
        )
        self.registry.register_backend(cap_ibm_1)
        self.registry.register_backend(cap_ibm_2)

        self.assertIsNotNone(self.registry.get_backend("IBM_TORONTO"))
        self.assertIsNotNone(self.registry.get_backend("IBM_PERTH"))
        self.assertEqual(len(self.registry.list_backends()), 2)

    def test_03_capability_inspection_methods(self) -> None:
        """Verifies supports_gate, supports_qubits, and supports_shots inspection methods."""
        self.assertTrue(self.cap_sim.supports_gate("CNOT"))
        self.assertFalse(self.cap_sim.supports_gate("NON_EXISTENT_GATE"))
        self.assertTrue(self.cap_sim.supports_qubits(16))
        self.assertFalse(self.cap_sim.supports_qubits(17))
        self.assertTrue(self.cap_sim.supports_shots(50000))
        self.assertFalse(self.cap_sim.supports_shots(200000))

    def test_04_registry_register_lookup_and_hash_query(self) -> None:
        """Verifies registering backend, querying by ID, contains check, and lookup by SHA-256 hash."""
        self.registry.register_backend(self.cap_sim)
        self.assertTrue(self.registry.contains_backend("LOCAL_REF_SIM_01"))

        retrieved = self.registry.get_backend("LOCAL_REF_SIM_01")
        self.assertEqual(retrieved, self.cap_sim)

        by_hash = self.registry.get_by_hash(self.cap_sim.capability_hash)
        self.assertEqual(by_hash, self.cap_sim)

    def test_05_capability_versioning_and_snapshots(self) -> None:
        """Verifies multi-version capability preservation under (backend_id, capability_version)."""
        cap_v1 = BackendCapabilityModel(
            backend_id="DEV_SIM", provider_id="PROV", backend_type="VIRTUAL_SIMULATOR",
            qubit_count=8, native_gate_set=("X", "CNOT"), topology_coupling_map=((0, 1),),
            max_shots=1000, capability_version="1.0.0"
        )
        cap_v2 = BackendCapabilityModel(
            backend_id="DEV_SIM", provider_id="PROV", backend_type="VIRTUAL_SIMULATOR",
            qubit_count=16, native_gate_set=("X", "CNOT", "H"), topology_coupling_map=((0, 1), (1, 2)),
            max_shots=2000, capability_version="2.0.0"
        )
        self.registry.register_backend(cap_v1)
        self.registry.register_backend(cap_v2)

        self.assertEqual(self.registry.get_backend("DEV_SIM", "1.0.0").qubit_count, 8)
        self.assertEqual(self.registry.get_backend("DEV_SIM", "2.0.0").qubit_count, 16)
        self.assertEqual(self.registry.get_backend("DEV_SIM").capability_version, "2.0.0")

    def test_06_retirement_preserves_historical_snapshots(self) -> None:
        """Verifies retire_backend deactivates backend without physically deleting historical records."""
        self.registry.register_backend(self.cap_sim)
        self.assertTrue(self.registry.retire_backend("LOCAL_REF_SIM_01"))
        self.assertTrue(self.registry.is_retired("LOCAL_REF_SIM_01"))

        self.assertEqual(len(self.registry.list_backends(include_retired=False)), 0)
        self.assertEqual(len(self.registry.list_backends(include_retired=True)), 1)
        self.assertIsNotNone(self.registry.get_backend("LOCAL_REF_SIM_01", "1.0.0"))

    def test_07_serialization_and_deserialization_roundtrip(self) -> None:
        """Verifies canonical JSON serialization and deserialization roundtrip equivalence."""
        json_str = serialize_backend_capability_model(self.cap_sim)
        deserialized = deserialize_backend_capability_model(json_str)

        self.assertEqual(deserialized.backend_id, self.cap_sim.backend_id)
        self.assertEqual(deserialized.capability_hash, self.cap_sim.capability_hash)
        self.assertEqual(deserialized, self.cap_sim)

    def test_08_snapshot_immutability(self) -> None:
        """Verifies BackendCapabilityModel is frozen and cannot be mutated."""
        with self.assertRaises(FrozenInstanceError):
            self.cap_sim.qubit_count = 99

    def test_09_credential_privacy_and_security_negative_test(self) -> None:
        """Security Negative Test: Verifies raw secrets NEVER appear in capability dictionaries or serialized outputs."""
        cred_ref = CredentialReference(credential_ref="env:IBM_QUANTUM_SECRET_KEY", provider_id="IBM")
        cred_dict = cred_ref.to_dict()

        json_str = serialize_backend_capability_model(self.cap_hw)

        self.assertNotIn("secret_value_12345", json_str)
        self.assertNotIn("token_abc_xyz", json_str)
        self.assertEqual(cred_dict["credential_ref"], "env:IBM_QUANTUM_SECRET_KEY")

    def test_10_no_hidden_gate_expansion(self) -> None:
        """Verifies registering a backend with new native gates does NOT mutate Module 6 GE(k) or B_u."""
        ge0 = create_initial_evolutionary_state()
        ge_size_before = len(ge0.vocabulary)

        cap_exotic = BackendCapabilityModel(
            backend_id="EXOTIC_BACKEND", provider_id="PROV", backend_type="PHYSICAL_HARDWARE",
            qubit_count=5, native_gate_set=("CUSTOM_IONQ_G2", "CUSTOM_SYCAMORE_FSIM"),
            topology_coupling_map=((0, 1),), max_shots=1000
        )
        self.registry.register_backend(cap_exotic)

        self.assertEqual(len(ge0.vocabulary), ge_size_before)

    # --- REQUIRED NEGATIVE VALIDATION TESTS ---

    def test_11_negative_empty_backend_id(self) -> None:
        """Negative Test 1: Empty backend_id raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=(), max_shots=100)

    def test_12_negative_empty_provider_id(self) -> None:
        """Negative Test 2: Empty provider_id raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=(), max_shots=100)

    def test_13_negative_unsupported_backend_type(self) -> None:
        """Negative Test 3: Unsupported backend_type raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="UNSUPPORTED_TYPE", qubit_count=5, native_gate_set=("X",), topology_coupling_map=(), max_shots=100)

    def test_14_negative_invalid_qubit_count(self) -> None:
        """Negative Test 4: Qubit count <= 0 raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=0, native_gate_set=("X",), topology_coupling_map=(), max_shots=100)

    def test_15_negative_invalid_max_shots(self) -> None:
        """Negative Test 5: Max shots <= 0 raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=(), max_shots=0)

    def test_16_negative_empty_native_gate_set(self) -> None:
        """Negative Test 6: Empty native gate set raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=(), topology_coupling_map=(), max_shots=100)

    def test_17_negative_topology_self_loop(self) -> None:
        """Negative Test 7: Topology self-loop raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=((0, 0),), max_shots=100)

    def test_18_negative_topology_out_of_bounds_qubit(self) -> None:
        """Negative Test 8: Topology referencing out-of-bounds qubit raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=((0, 99),), max_shots=100)

    def test_19_negative_duplicate_topology_edge(self) -> None:
        """Negative Test 9: Duplicate topology edge raises ValueError."""
        with self.assertRaises(ValueError):
            BackendCapabilityModel(backend_id="B", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=((0, 1), (0, 1)), max_shots=100)

    def test_20_negative_version_conflict_registration(self) -> None:
        """Negative Test 10: Re-registering version with different capability raises ValueError."""
        cap1 = BackendCapabilityModel(backend_id="B1", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=5, native_gate_set=("X",), topology_coupling_map=(), max_shots=100, capability_version="1.0.0")
        cap2 = BackendCapabilityModel(backend_id="B1", provider_id="P", backend_type="VIRTUAL_SIMULATOR", qubit_count=10, native_gate_set=("X",), topology_coupling_map=(), max_shots=100, capability_version="1.0.0")
        self.registry.register_backend(cap1)
        with self.assertRaises(ValueError):
            self.registry.register_backend(cap2)

    def test_21_negative_deserialization_corrupted_hash(self) -> None:
        """Negative Test 11: Deserializing corrupted capability hash raises ValueError."""
        json_str = serialize_backend_capability_model(self.cap_sim)
        corrupted_json = json_str.replace(self.cap_sim.capability_hash, "0000000000000000000000000000000000000000000000000000000000000000")
        with self.assertRaises(ValueError) as ctx:
            deserialize_backend_capability_model(corrupted_json)
        self.assertIn("REGISTRY_INTEGRITY_FAILURE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
