"""
Module 7 Stage 4 — Cloud Provider Adapter Protocols & Interfaces.

Defines standard protocols for cloud quantum provider adapters (IBM, AWS, Google, Microsoft, Mock).
"""

from typing import Protocol, Dict, Any, Optional
from src.module7.model import BackendCapabilityModel
from src.module7.stage2.model import LoweringResultArtifact
from src.module7.stage4.model import (
    CloudExecutionRequest,
    CloudJobHandle,
    ProviderNeutralExecutionResult,
)


class CloudBackendAdapterProtocol(Protocol):
    """Protocol that all provider-specific cloud hardware adapters must implement."""

    def validate_capability(
        self,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> bool:
        """Validates native circuit compatibility against backend capability."""
        ...

    def submit_job(
        self,
        request: CloudExecutionRequest,
        lowering_result: LoweringResultArtifact,
        backend_capability: BackendCapabilityModel,
    ) -> CloudJobHandle:
        """Submits native circuit execution job to cloud provider."""
        ...

    def get_job_status(self, handle: CloudJobHandle) -> CloudJobHandle:
        """Queries current job lifecycle status from provider."""
        ...

    def retrieve_result(self, handle: CloudJobHandle) -> ProviderNeutralExecutionResult:
        """Retrieves and normalizes execution results from provider."""
        ...

    def cancel_job(self, handle: CloudJobHandle) -> CloudJobHandle:
        """Cancels a pending or running provider job."""
        ...
