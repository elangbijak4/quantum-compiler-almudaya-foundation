"""
Module 7 Stage 4 — Deterministic Mock Cloud Backend Adapter.

Provides MockCloudBackendAdapter implementing CloudBackendAdapterProtocol for testing
cloud execution flows, job handles, lifecycles, and result normalization without external network calls.
"""

from typing import Dict, Any, Optional
import uuid

from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import LoweringStatus, LoweringResultArtifact
from src.module7.stage4.model import (
    CloudExecutionLifecycleStatus,
    ExecutionEnvironmentType,
    CloudExecutionRequest,
    CloudJobHandle,
    ProviderNeutralExecutionResult,
)
from src.module7.stage4.interfaces import CloudBackendAdapterProtocol
from src.module7.stage3.statevector import LocalReferenceStatevectorSimulator
from src.module7.stage3.sampling import DeterministicShotSampler


class MockCloudBackendAdapter(CloudBackendAdapterProtocol):
    """
    Deterministic Mock Provider Adapter for Stage 4 Testing.
    """

    def __init__(self, inject_failure: Optional[str] = None) -> None:
        self.inject_failure = inject_failure
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def validate_capability(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> bool:
        """Validates native circuit compatibility against backend capability."""
        if lowering_result.status != LoweringStatus.SEMANTICALLY_VERIFIED:
            return False
        if not lowering_result.native_circuit:
            return False

        native_circ = lowering_result.native_circuit
        for op in native_circ.native_gate_sequence:
            if op["gate"] not in backend_capability.native_gate_set:
                return False
        return True

    def submit_job(
        self,
        request: CloudExecutionRequest,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> CloudJobHandle:
        """Submits native circuit execution job to mock cloud provider."""
        if self.inject_failure == "AUTHENTICATION_FAILURE":
            raise PermissionError("AUTHENTICATION_FAILURE: Invalid provider credential reference.")

        if self.inject_failure == "SUBMISSION_FAILURE":
            raise RuntimeError("SUBMISSION_FAILURE: Mock network submission timeout.")

        if not self.validate_capability(lowering_result, backend_capability):
            raise ValueError("BACKEND_CAPABILITY_MISMATCH: Circuit incompatible with backend capability.")

        provider_job_id = f"MOCK_JOB_{uuid.uuid4().hex[:8].upper()}"
        job_id = f"JOB_MOCK_{uuid.uuid4().hex[:8].upper()}"

        handle = CloudJobHandle(
            job_id=job_id,
            provider_job_id=provider_job_id,
            request_id=request.request_id,
            provider_id=request.provider_id,
            backend_id=request.backend_id,
            status=CloudExecutionLifecycleStatus.SUBMITTED,
        )

        self._jobs[job_id] = {
            "handle": handle,
            "request": request,
            "lowering_result": lowering_result,
            "backend_capability": backend_capability,
            "status": CloudExecutionLifecycleStatus.SUBMITTED,
        }

        return handle

    def get_job_status(self, handle: CloudJobHandle) -> CloudJobHandle:
        """Queries current job lifecycle status from mock provider."""
        if handle.job_id not in self._jobs:
            raise KeyError(f"Job {handle.job_id} not found.")

        job_info = self._jobs[handle.job_id]
        curr_status = job_info["status"]

        # Simulate state transitions: SUBMITTED -> QUEUED -> RUNNING -> COMPLETED
        if curr_status == CloudExecutionLifecycleStatus.SUBMITTED:
            next_status = CloudExecutionLifecycleStatus.QUEUED
        elif curr_status == CloudExecutionLifecycleStatus.QUEUED:
            next_status = CloudExecutionLifecycleStatus.RUNNING
        elif curr_status == CloudExecutionLifecycleStatus.RUNNING:
            next_status = CloudExecutionLifecycleStatus.COMPLETED
        else:
            next_status = curr_status

        if self.inject_failure == "EXECUTION_FAILURE" and next_status == CloudExecutionLifecycleStatus.RUNNING:
            next_status = CloudExecutionLifecycleStatus.FAILED

        job_info["status"] = next_status

        return CloudJobHandle(
            job_id=handle.job_id,
            provider_job_id=handle.provider_job_id,
            request_id=handle.request_id,
            provider_id=handle.provider_id,
            backend_id=handle.backend_id,
            status=next_status,
        )

    def retrieve_result(self, handle: CloudJobHandle) -> ProviderNeutralExecutionResult:
        """Retrieves and normalizes execution results from mock provider."""
        if handle.job_id not in self._jobs:
            raise KeyError(f"Job {handle.job_id} not found.")

        job_info = self._jobs[handle.job_id]
        lowering_result = job_info["lowering_result"]
        native_circ = lowering_result.native_circuit

        if job_info["status"] == CloudExecutionLifecycleStatus.FAILED or self.inject_failure == "EXECUTION_FAILURE":
            return ProviderNeutralExecutionResult(
                job_id=handle.job_id,
                provider_job_id=handle.provider_job_id,
                native_circuit_hash=native_circ.native_circuit_hash,
                backend_id=handle.backend_id,
                provider_id=handle.provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=job_info["request"].shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={"failure_reason": "EXECUTION_FAILURE: Mock cloud execution dropped by provider."},
            )

        # Simulate execution via statevector simulator
        num_q = max(native_circ.qubit_mapping.values()) + 1 if native_circ.qubit_mapping else 1
        sim = LocalReferenceStatevectorSimulator(num_qubits=num_q)
        sim.execute_gate_sequence(native_circ.native_gate_sequence)
        exact_probs = sim.get_probabilities()

        sampler = DeterministicShotSampler(seed_prng=42)
        counts, dist = sampler.sample_shots(exact_probs, job_info["request"].shots)

        return ProviderNeutralExecutionResult(
            job_id=handle.job_id,
            provider_job_id=handle.provider_job_id,
            native_circuit_hash=native_circ.native_circuit_hash,
            backend_id=handle.backend_id,
            provider_id=handle.provider_id,
            environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
            status=CloudExecutionLifecycleStatus.COMPLETED,
            shots=job_info["request"].shots,
            measurement_counts=counts,
            measurement_distribution=dist,
            provenance={
                "provider_job_id": handle.provider_job_id,
                "credential_ref": job_info["request"].credential_ref,
                "mock_execution": True,
            },
        )

    def cancel_job(self, handle: CloudJobHandle) -> CloudJobHandle:
        """Cancels a pending or running provider job."""
        if handle.job_id not in self._jobs:
            raise KeyError(f"Job {handle.job_id} not found.")

        job_info = self._jobs[handle.job_id]
        job_info["status"] = CloudExecutionLifecycleStatus.CANCELLED

        return CloudJobHandle(
            job_id=handle.job_id,
            provider_job_id=handle.provider_job_id,
            request_id=handle.request_id,
            provider_id=handle.provider_id,
            backend_id=handle.backend_id,
            status=CloudExecutionLifecycleStatus.CANCELLED,
        )
