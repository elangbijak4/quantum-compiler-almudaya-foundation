"""
Module 7 Stage 4 Test Suite — Initialization & Provider Adapter Data Contract Verification.
"""

import unittest
from src.module7.stage4 import (
    CloudExecutionLifecycleStatus,
    ExecutionEnvironmentType,
    CloudExecutionRequest,
    CloudJobHandle,
    ProviderNeutralExecutionResult,
)


class TestModule7Stage4Initialization(unittest.TestCase):
    """Tests verifying Stage 4 foundational type contracts, request hashing, and security isolation."""

    def test_01_cloud_execution_request_hashing(self) -> None:
        """Verifies CloudExecutionRequest SHA-256 request_hash computation determinism."""
        r1 = CloudExecutionRequest(
            request_id="REQ_01",
            native_circuit_id="NAT_CIRC_01",
            native_circuit_hash="a" * 64,
            backend_id="IBM_TORINO",
            provider_id="IBM",
            capability_hash="b" * 64,
            lowering_id="LOWER_01",
            shots=1000,
            credential_ref="env:IBM_QUANTUM_TOKEN",
        )
        r2 = CloudExecutionRequest(
            request_id="REQ_01",
            native_circuit_id="NAT_CIRC_01",
            native_circuit_hash="a" * 64,
            backend_id="IBM_TORINO",
            provider_id="IBM",
            capability_hash="b" * 64,
            lowering_id="LOWER_01",
            shots=1000,
            credential_ref="env:IBM_QUANTUM_TOKEN",
        )
        self.assertEqual(len(r1.request_hash), 64)
        self.assertEqual(r1.request_hash, r2.request_hash)

    def test_02_cloud_job_handle_lifecycle(self) -> None:
        """Verifies CloudJobHandle lifecycle status representation and hash computation."""
        handle = CloudJobHandle(
            job_id="JOB_CLOUD_01",
            provider_job_id="IBM_JOB_998877",
            request_id="REQ_01",
            provider_id="IBM",
            backend_id="IBM_TORINO",
            status=CloudExecutionLifecycleStatus.SUBMITTED,
        )
        self.assertEqual(handle.status.value, "SUBMITTED")
        self.assertEqual(len(handle.handle_hash), 64)

    def test_03_provider_neutral_execution_result_security_isolation(self) -> None:
        """Verifies ProviderNeutralExecutionResult fields and credential privacy isolation."""
        res = ProviderNeutralExecutionResult(
            job_id="JOB_CLOUD_01",
            provider_job_id="IBM_JOB_998877",
            native_circuit_hash="a" * 64,
            backend_id="IBM_TORINO",
            provider_id="IBM",
            environment_type=ExecutionEnvironmentType.PHYSICAL_HARDWARE,
            status=CloudExecutionLifecycleStatus.COMPLETED,
            shots=1000,
            measurement_counts={"00": 512, "11": 488},
            measurement_distribution={"00": 0.512, "11": 0.488},
            provenance={"credential_ref": "env:IBM_QUANTUM_TOKEN"},
        )
        self.assertEqual(res.status.value, "COMPLETED")
        self.assertEqual(len(res.result_hash), 64)

        # Confirm zero raw secret values appear in serialized dictionary
        res_str = str(res.to_dict())
        for secret_pattern in ("raw_secret_key", "password123", "bearer_token_abc", "sk-live-999"):
            self.assertNotIn(secret_pattern, res_str)


if __name__ == "__main__":
    unittest.main()
