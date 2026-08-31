"""
Module 7 Stage 4 — Production Cloud Execution Engine Implementation.

Provides CloudExecutionEngine managing capability validation, provider translation,
adapter dispatch, lifecycle tracking, and provider result normalization.
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
from src.module7.stage4.translation import ProviderTranslator, ProviderProgramArtifact
from src.module7.stage4.mock import MockCloudBackendAdapter


class CloudExecutionEngine:
    """
    Module 7 Stage 4 Production Engine.
    
    Coordinates provider translation, capability binding, job submission, and result normalization.
    """

    def __init__(self, default_adapter: Optional[CloudBackendAdapterProtocol] = None) -> None:
        self.default_adapter = default_adapter or MockCloudBackendAdapter()
        self.translator = ProviderTranslator()

    def execute_cloud_job(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
        provider_id: str = "LOCAL_REFERENCE",
        shots: int = 1000,
        credential_ref: Optional[str] = None,
        adapter: Optional[CloudBackendAdapterProtocol] = None,
    ) -> ProviderNeutralExecutionResult:
        """
        Executes native circuit on target cloud quantum backend via provider adapter framework.
        """
        active_adapter = adapter or self.default_adapter
        job_id = f"JOB_CLOUD_{uuid.uuid4().hex[:8].upper()}"

        # 1. Pre-submission Eligibility Validation
        if lowering_result.status != LoweringStatus.SEMANTICALLY_VERIFIED:
            return ProviderNeutralExecutionResult(
                job_id=job_id,
                provider_job_id="",
                native_circuit_hash=lowering_result.native_circuit.native_circuit_hash if lowering_result.native_circuit else "",
                backend_id=backend_capability.backend_id,
                provider_id=provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "failure_reason": "EXECUTION_INPUT_INVALID: Circuit lowering status is not SEMANTICALLY_VERIFIED.",
                    "lowering_status": lowering_result.status.value,
                },
            )

        if not lowering_result.native_circuit:
            return ProviderNeutralExecutionResult(
                job_id=job_id,
                provider_job_id="",
                native_circuit_hash="",
                backend_id=backend_capability.backend_id,
                provider_id=provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "failure_reason": "EXECUTION_INPUT_INVALID: Missing NativeCircuitArtifact in lowering result.",
                },
            )

        native_circ = lowering_result.native_circuit

        # 2. Capability Validation
        if not active_adapter.validate_capability(lowering_result, backend_capability):
            return ProviderNeutralExecutionResult(
                job_id=job_id,
                provider_job_id="",
                native_circuit_hash=native_circ.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                provider_id=provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={
                    "failure_reason": f"BACKEND_CAPABILITY_MISMATCH: Circuit incompatible with backend '{backend_capability.backend_id}'.",
                },
            )

        # 3. Provider Program Translation
        provider_program = self.translator.translate(
            native_circuit=native_circ,
            provider_id=provider_id,
            backend_id=backend_capability.backend_id,
        )

        # 4. Construct Execution Request
        request_id = f"REQ_{uuid.uuid4().hex[:8].upper()}"
        request = CloudExecutionRequest(
            request_id=request_id,
            native_circuit_id=native_circ.native_circuit_id,
            native_circuit_hash=native_circ.native_circuit_hash,
            backend_id=backend_capability.backend_id,
            provider_id=provider_id,
            capability_hash=backend_capability.capability_hash,
            lowering_id=lowering_result.lowering_id,
            shots=shots,
            credential_ref=credential_ref,
        )

        # 5. Submit Job to Provider Adapter
        try:
            handle = active_adapter.submit_job(request, lowering_result, backend_capability)
        except PermissionError as err:
            return ProviderNeutralExecutionResult(
                job_id=job_id,
                provider_job_id="",
                native_circuit_hash=native_circ.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                provider_id=provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={"failure_reason": f"AUTHENTICATION_FAILURE: {str(err)}"},
            )
        except Exception as err:
            return ProviderNeutralExecutionResult(
                job_id=job_id,
                provider_job_id="",
                native_circuit_hash=native_circ.native_circuit_hash,
                backend_id=backend_capability.backend_id,
                provider_id=provider_id,
                environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
                status=CloudExecutionLifecycleStatus.FAILED,
                shots=shots,
                measurement_counts={},
                measurement_distribution={},
                provenance={"failure_reason": f"SUBMISSION_FAILURE: {str(err)}"},
            )

        # 6. Lifecycle Tracking (Transition handle to COMPLETED)
        while handle.status in (
            CloudExecutionLifecycleStatus.SUBMITTED,
            CloudExecutionLifecycleStatus.QUEUED,
            CloudExecutionLifecycleStatus.RUNNING,
        ):
            handle = active_adapter.get_job_status(handle)

        if handle.status == CloudExecutionLifecycleStatus.FAILED:
            return active_adapter.retrieve_result(handle)

        # 7. Retrieve and Return Normalized Result
        result = active_adapter.retrieve_result(handle)
        
        # Attach translation provenance metadata
        prov = dict(result.provenance)
        prov["program_id"] = provider_program.program_id
        prov["translation_hash"] = provider_program.translation_hash
        prov["provider_language"] = provider_program.provider_language

        return ProviderNeutralExecutionResult(
            job_id=result.job_id,
            provider_job_id=result.provider_job_id,
            native_circuit_hash=result.native_circuit_hash,
            backend_id=result.backend_id,
            provider_id=result.provider_id,
            environment_type=result.environment_type,
            status=result.status,
            shots=result.shots,
            measurement_counts=result.measurement_counts,
            measurement_distribution=result.measurement_distribution,
            provenance=prov,
        )
