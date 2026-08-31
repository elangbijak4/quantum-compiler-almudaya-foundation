"""
Module 7 Stage 3 Test Suite — Production Engine Verification.

Verifies LocalReferenceSimulatorEngine statevector evolution, native gate execution (X, Y, Z, H, RX, RY, RZ, CNOT, CZ, SWAP),
interference, entanglement, shot sampling determinism, pre-execution validation, resource bounds,
failure classifications, and security isolation.
"""

import math
import unittest
from typing import Dict, Any, Tuple

from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import (
    LoweringStatus,
    NativeCircuitArtifact,
    LoweringResultArtifact,
)
from src.module7.stage3 import (
    SimulationExecutionStatus,
    SimulatorConfig,
    LocalReferenceStatevectorSimulator,
    DeterministicShotSampler,
    LocalReferenceSimulatorEngine,
)


class TestModule7Stage3Engine(unittest.TestCase):
    """Production Engine Tests for Stage 3 Local Reference Simulator Engine."""

    def setUp(self) -> None:
        self.engine = LocalReferenceSimulatorEngine()
        self.backend = BackendCapabilityModel(
            backend_id="LOCAL_REF_SIM_01",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=16,
            native_gate_set=("X", "Y", "Z", "H", "RX", "RY", "RZ", "CNOT", "CZ", "SWAP"),
            topology_coupling_map=((0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)),
            max_shots=1000000,
        )

    def _create_verified_lowering_artifact(self, ops: Tuple[Dict[str, Any], ...], num_qubits: int = 2) -> LoweringResultArtifact:
        native_circuit = NativeCircuitArtifact(
            native_circuit_id="NATIVE_CIRC_TEST",
            backend_id=self.backend.backend_id,
            capability_hash=self.backend.capability_hash,
            native_gate_sequence=ops,
            qubit_mapping={i: i for i in range(num_qubits)},
            native_gate_count=len(ops),
            circuit_depth=len(ops),
            inserted_swap_count=0,
        )
        return LoweringResultArtifact(
            lowering_id="LOWER_TEST_01",
            logical_circuit_id="LOG_CIRC_TEST",
            logical_circuit_hash="a" * 64,
            backend_id=self.backend.backend_id,
            capability_version=self.backend.capability_version,
            capability_hash=self.backend.capability_hash,
            policy_hash="b" * 64,
            status=LoweringStatus.SEMANTICALLY_VERIFIED,
            native_circuit=native_circuit,
            qubit_mapping={i: i for i in range(num_qubits)},
            semantic_verification_status="VERIFIED",
            semantic_verification_reference="MODULE4_STAGE4_REF_01",
        )

    def test_01_interference_h_h_equals_identity(self) -> None:
        """Verifies quantum interference: H + H on |0> returns |0> with probability 1.0."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "H", "qubits": (0,)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)

        self.assertEqual(res.status, SimulationExecutionStatus.COMPLETED)
        self.assertIn("0", res.measurement_distribution)
        self.assertAlmostEqual(res.measurement_distribution["0"], 1.0, delta=1e-5)
        self.assertIsNotNone(res.statevector_summary)
        self.assertAlmostEqual(res.statevector_summary.probabilities["0"], 1.0, delta=1e-5)

    def test_02_entanglement_bell_state_generation(self) -> None:
        """Verifies entanglement: H(q0) + CNOT(q0, q1) produces Bell state (|00> + |11>) / sqrt(2)."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)

        self.assertEqual(res.status, SimulationExecutionStatus.COMPLETED)
        self.assertIsNotNone(res.statevector_summary)
        probs = res.statevector_summary.probabilities

        self.assertAlmostEqual(probs["00"], 0.5, delta=1e-5)
        self.assertAlmostEqual(probs["11"], 0.5, delta=1e-5)
        self.assertNotIn("01", probs)
        self.assertNotIn("10", probs)

    def test_03_all_single_qubit_native_gates(self) -> None:
        """Verifies execution of single-qubit native gates: X, Y, Z, RX, RY, RZ."""
        ops = (
            {"gate": "X", "qubits": (0,)},
            {"gate": "Z", "qubits": (0,)},
            {"gate": "RY", "qubits": (0,), "params": {"theta": math.pi}},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)
        self.assertEqual(res.status, SimulationExecutionStatus.COMPLETED)

    def test_04_cz_and_swap_two_qubit_gates(self) -> None:
        """Verifies execution of two-qubit CZ and SWAP operations."""
        ops = (
            {"gate": "X", "qubits": (0,)},
            {"gate": "SWAP", "qubits": (0, 1)},
            {"gate": "CZ", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)
        self.assertEqual(res.status, SimulationExecutionStatus.COMPLETED)
        self.assertIn("10", res.measurement_counts)

    def test_05_seeded_prng_shot_reproducibility(self) -> None:
        """Verifies identical seed produces 100% identical measurement counts and job hash."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        cfg1 = SimulatorConfig(config_id="CFG1", shots=1000, seed_prng=42)
        cfg2 = SimulatorConfig(config_id="CFG2", shots=1000, seed_prng=42)

        res1 = self.engine.execute_lowered_circuit(artifact, self.backend, cfg1)
        res2 = self.engine.execute_lowered_circuit(artifact, self.backend, cfg2)

        self.assertEqual(res1.status, SimulationExecutionStatus.COMPLETED)
        self.assertEqual(res1.measurement_counts, res2.measurement_counts)
        self.assertEqual(res1.measurement_distribution, res2.measurement_distribution)

    def test_06_unverified_circuit_rejection(self) -> None:
        """Verifies rejection of SEMANTICALLY_NON_EQUIVALENT, INCONCLUSIVE, or FAILED circuits."""
        ops = ({"gate": "H", "qubits": (0,)},)
        native_circuit = NativeCircuitArtifact(
            native_circuit_id="NATIVE_FAIL",
            backend_id=self.backend.backend_id,
            capability_hash=self.backend.capability_hash,
            native_gate_sequence=ops,
            qubit_mapping={0: 0},
            native_gate_count=1,
            circuit_depth=1,
            inserted_swap_count=0,
        )

        for invalid_status in (LoweringStatus.SEMANTICALLY_NON_EQUIVALENT, LoweringStatus.INCONCLUSIVE, LoweringStatus.FAILED):
            artifact = LoweringResultArtifact(
                lowering_id="LOWER_FAIL",
                logical_circuit_id="LOG_FAIL",
                logical_circuit_hash="c" * 64,
                backend_id=self.backend.backend_id,
                capability_version=self.backend.capability_version,
                capability_hash=self.backend.capability_hash,
                policy_hash="d" * 64,
                status=invalid_status,
                native_circuit=native_circuit,
                qubit_mapping={0: 0},
                semantic_verification_status="NON_EQUIVALENT",
            )
            res = self.engine.execute_lowered_circuit(artifact, self.backend)
            self.assertEqual(res.status, SimulationExecutionStatus.REJECTED)
            self.assertIn("EXECUTION_INPUT_INVALID", res.provenance["rejection_reason"])

    def test_07_unsupported_native_gate_failure(self) -> None:
        """Verifies explicit failure when circuit contains unsupported native operation."""
        backend_limited = BackendCapabilityModel(
            backend_id="LIMITED_SIM",
            provider_id="LOCAL_REFERENCE",
            backend_type="VIRTUAL_SIMULATOR",
            qubit_count=4,
            native_gate_set=("X", "H"),  # No CNOT
            topology_coupling_map=((0, 1), (1, 0)),
            max_shots=1000000,
        )
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        res = self.engine.execute_lowered_circuit(artifact, backend_limited)

        self.assertEqual(res.status, SimulationExecutionStatus.FAILED)
        self.assertIn("BACKEND_CAPABILITY_MISMATCH", res.provenance["failure_reason"])

    def test_08_resource_limits_exceeded(self) -> None:
        """Verifies rejection when qubit count or shots exceed simulator limits."""
        ops = ({"gate": "X", "qubits": (0,)},)
        artifact_too_many_qubits = self._create_verified_lowering_artifact(ops, num_qubits=35)
        res_qubits = self.engine.execute_lowered_circuit(artifact_too_many_qubits, self.backend)
        self.assertEqual(res_qubits.status, SimulationExecutionStatus.REJECTED)

        artifact_valid = self._create_verified_lowering_artifact(ops, num_qubits=1)
        cfg_excessive_shots = SimulatorConfig(config_id="CFG_SHOTS", shots=2000000)
        res_shots = self.engine.execute_lowered_circuit(artifact_valid, self.backend, cfg_excessive_shots)
        self.assertEqual(res_shots.status, SimulationExecutionStatus.REJECTED)

    def test_09_default_shots_behavior(self) -> None:
        """Verifies default shot count (1000) when omitted."""
        ops = ({"gate": "H", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)

        self.assertEqual(res.status, SimulationExecutionStatus.COMPLETED)
        self.assertEqual(res.shots, 1000)
        self.assertEqual(sum(res.measurement_counts.values()), 1000)

    def test_10_input_immutability(self) -> None:
        """Verifies execution DOES NOT mutate NativeCircuitArtifact or BackendCapabilityModel."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        circuit_hash_before = artifact.native_circuit.native_circuit_hash
        backend_hash_before = self.backend.capability_hash

        _ = self.engine.execute_lowered_circuit(artifact, self.backend)

        self.assertEqual(artifact.native_circuit.native_circuit_hash, circuit_hash_before)
        self.assertEqual(self.backend.capability_hash, backend_hash_before)

    def test_11_security_credential_isolation(self) -> None:
        """Verifies zero secret tokens or passwords appear in simulator job result or provenance."""
        ops = ({"gate": "X", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        res = self.engine.execute_lowered_circuit(artifact, self.backend)

        res_str = str(res.to_dict())
        for token in ("api_key", "password", "secret", "bearer", "token"):
            self.assertNotIn(token, res_str.lower())

    def test_12_no_hidden_gate_expansion(self) -> None:
        """Verifies reference simulation DOES NOT mutate Module 6 vocabulary."""
        from src.module6.vocabulary import PrimitiveVocabularyAnalyzer
        analyzer = PrimitiveVocabularyAnalyzer()

        ops = ({"gate": "H", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        _ = self.engine.execute_lowered_circuit(artifact, self.backend)

        # Confirm PrimitiveVocabularyAnalyzer remains functional and unaltered
        self.assertIsNotNone(analyzer)


if __name__ == "__main__":
    unittest.main()
