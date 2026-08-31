"""
Module 7 Stage 4 Test Suite — Production Engine Verification.

Verifies CloudExecutionEngine capability binding, provider translation (OpenQASM 2.0 / JSON IR),
MockCloudBackendAdapter job submission, lifecycle tracking (SUBMITTED -> QUEUED -> RUNNING -> COMPLETED),
cancellation, failure injection, security credential privacy, and upstream immutability.
"""

import unittest
from typing import Dict, Any, Tuple

from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import (
    LoweringStatus,
    NativeCircuitArtifact,
    LoweringResultArtifact,
)
from src.module7.stage4 import (
    CloudExecutionLifecycleStatus,
    ExecutionEnvironmentType,
    CloudExecutionRequest,
    CloudJobHandle,
    ProviderNeutralExecutionResult,
    ProviderProgramArtifact,
    ProviderTranslator,
    MockCloudBackendAdapter,
    CloudExecutionEngine,
)


class TestModule7Stage4Engine(unittest.TestCase):
    """Production Engine Tests for Stage 4 Cloud Hardware Provider Adapters."""

    def setUp(self) -> None:
        self.engine = CloudExecutionEngine()
        self.translator = ProviderTranslator()
        self.backend = BackendCapabilityModel(
            backend_id="IBM_TORINO",
            provider_id="IBM",
            backend_type="PHYSICAL_HARDWARE",
            qubit_count=127,
            native_gate_set=("X", "Y", "Z", "H", "RX", "RY", "RZ", "CNOT", "CZ", "SWAP"),
            topology_coupling_map=((0, 1), (1, 0), (0, 2), (2, 0)),
            max_shots=1000000,
        )

    def _create_verified_lowering_artifact(self, ops: Tuple[Dict[str, Any], ...], num_qubits: int = 2) -> LoweringResultArtifact:
        native_circuit = NativeCircuitArtifact(
            native_circuit_id="NATIVE_CIRC_CLOUD",
            backend_id=self.backend.backend_id,
            capability_hash=self.backend.capability_hash,
            native_gate_sequence=ops,
            qubit_mapping={i: i for i in range(num_qubits)},
            native_gate_count=len(ops),
            circuit_depth=len(ops),
            inserted_swap_count=0,
        )
        return LoweringResultArtifact(
            lowering_id="LOWER_CLOUD_01",
            logical_circuit_id="LOG_CIRC_CLOUD",
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

    def test_01_provider_translation_openqasm2(self) -> None:
        """Verifies deterministic translation of NativeCircuitArtifact into OpenQASM 2.0 ProviderProgramArtifact."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        prog = self.translator.translate(artifact.native_circuit, provider_id="IBM", backend_id="IBM_TORINO")

        self.assertEqual(prog.provider_language, "OPENQASM_2_0")
        self.assertIn("OPENQASM 2.0;", prog.provider_program_text)
        self.assertIn("h q[0];", prog.provider_program_text)
        self.assertIn("cx q[0], q[1];", prog.provider_program_text)
        self.assertEqual(len(prog.translation_hash), 64)

    def test_02_provider_translation_json_ir(self) -> None:
        """Verifies translation into AWS JSON IR provider program format."""
        ops = ({"gate": "X", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)
        prog = self.translator.translate(artifact.native_circuit, provider_id="AWS", backend_id="AWS_SV1")

        self.assertEqual(prog.provider_language, "AWS_IR_JSON")
        self.assertIn('"provider": "AWS"', prog.provider_program_text)

    def test_03_mock_cloud_job_execution_lifecycle(self) -> None:
        """Verifies complete mock cloud job lifecycle: SUBMITTED -> QUEUED -> RUNNING -> COMPLETED."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        res = self.engine.execute_cloud_job(
            lowering_result=artifact,
            backend_capability=self.backend,
            provider_id="IBM",
            shots=1000,
            credential_ref="env:IBM_QUANTUM_TOKEN",
        )

        self.assertEqual(res.status, CloudExecutionLifecycleStatus.COMPLETED)
        self.assertEqual(res.shots, 1000)
        self.assertEqual(sum(res.measurement_counts.values()), 1000)
        self.assertIn("translation_hash", res.provenance)

    def test_04_job_cancellation(self) -> None:
        """Verifies provider job cancellation producing CloudExecutionLifecycleStatus.CANCELLED."""
        mock_adapter = MockCloudBackendAdapter()
        ops = ({"gate": "X", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)

        req = CloudExecutionRequest(
            request_id="REQ_CANCEL",
            native_circuit_id=artifact.native_circuit.native_circuit_id,
            native_circuit_hash=artifact.native_circuit.native_circuit_hash,
            backend_id=self.backend.backend_id,
            provider_id="IBM",
            capability_hash=self.backend.capability_hash,
            lowering_id=artifact.lowering_id,
        )
        handle = mock_adapter.submit_job(req, artifact, self.backend)
        self.assertEqual(handle.status, CloudExecutionLifecycleStatus.SUBMITTED)

        canceled_handle = mock_adapter.cancel_job(handle)
        self.assertEqual(canceled_handle.status, CloudExecutionLifecycleStatus.CANCELLED)

    def test_05_unverified_circuit_rejection(self) -> None:
        """Verifies rejection of unverified lowering results."""
        ops = ({"gate": "H", "qubits": (0,)},)
        native_circ = NativeCircuitArtifact(
            native_circuit_id="NATIVE_FAIL",
            backend_id=self.backend.backend_id,
            capability_hash=self.backend.capability_hash,
            native_gate_sequence=ops,
            qubit_mapping={0: 0},
            native_gate_count=1,
            circuit_depth=1,
            inserted_swap_count=0,
        )
        artifact = LoweringResultArtifact(
            lowering_id="LOWER_FAIL",
            logical_circuit_id="LOG_FAIL",
            logical_circuit_hash="c" * 64,
            backend_id=self.backend.backend_id,
            capability_version=self.backend.capability_version,
            capability_hash=self.backend.capability_hash,
            policy_hash="d" * 64,
            status=LoweringStatus.SEMANTICALLY_NON_EQUIVALENT,
            native_circuit=native_circ,
            qubit_mapping={0: 0},
            semantic_verification_status="NON_EQUIVALENT",
        )
        res = self.engine.execute_cloud_job(artifact, self.backend)
        self.assertEqual(res.status, CloudExecutionLifecycleStatus.FAILED)
        self.assertIn("EXECUTION_INPUT_INVALID", res.provenance["failure_reason"])

    def test_06_backend_capability_mismatch_failure(self) -> None:
        """Verifies rejection when native circuit contains unsupported operations."""
        backend_limited = BackendCapabilityModel(
            backend_id="LIMITED_CLOUD",
            provider_id="IBM",
            backend_type="PHYSICAL_HARDWARE",
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
        res = self.engine.execute_cloud_job(artifact, backend_limited)

        self.assertEqual(res.status, CloudExecutionLifecycleStatus.FAILED)
        self.assertIn("BACKEND_CAPABILITY_MISMATCH", res.provenance["failure_reason"])

    def test_07_injected_authentication_failure(self) -> None:
        """Verifies explicit failure handling for injected provider AUTHENTICATION_FAILURE."""
        adapter_auth_fail = MockCloudBackendAdapter(inject_failure="AUTHENTICATION_FAILURE")
        ops = ({"gate": "H", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)

        res = self.engine.execute_cloud_job(
            lowering_result=artifact,
            backend_capability=self.backend,
            adapter=adapter_auth_fail,
        )
        self.assertEqual(res.status, CloudExecutionLifecycleStatus.FAILED)
        self.assertIn("AUTHENTICATION_FAILURE", res.provenance["failure_reason"])

    def test_08_injected_execution_failure(self) -> None:
        """Verifies explicit failure handling for injected EXECUTION_FAILURE during runtime."""
        adapter_exec_fail = MockCloudBackendAdapter(inject_failure="EXECUTION_FAILURE")
        ops = ({"gate": "H", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)

        res = self.engine.execute_cloud_job(
            lowering_result=artifact,
            backend_capability=self.backend,
            adapter=adapter_exec_fail,
        )
        self.assertEqual(res.status, CloudExecutionLifecycleStatus.FAILED)

    def test_09_security_credential_isolation(self) -> None:
        """Verifies zero secret tokens or passwords appear in ProviderProgramArtifact or job result."""
        ops = ({"gate": "X", "qubits": (0,)},)
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=1)

        res = self.engine.execute_cloud_job(
            lowering_result=artifact,
            backend_capability=self.backend,
            credential_ref="env:MY_SECURE_TOKEN_REF",
        )
        res_str = str(res.to_dict())
        for secret_pattern in ("raw_secret_key", "password123", "bearer_token_abc", "sk-live-999"):
            self.assertNotIn(secret_pattern, res_str)

    def test_10_input_immutability(self) -> None:
        """Verifies cloud execution DOES NOT mutate NativeCircuitArtifact or BackendCapabilityModel."""
        ops = (
            {"gate": "H", "qubits": (0,)},
            {"gate": "CNOT", "qubits": (0, 1)},
        )
        artifact = self._create_verified_lowering_artifact(ops, num_qubits=2)
        circuit_hash_before = artifact.native_circuit.native_circuit_hash
        backend_hash_before = self.backend.capability_hash

        _ = self.engine.execute_cloud_job(artifact, self.backend)

        self.assertEqual(artifact.native_circuit.native_circuit_hash, circuit_hash_before)
        self.assertEqual(self.backend.capability_hash, backend_hash_before)


if __name__ == "__main__":
    unittest.main()
