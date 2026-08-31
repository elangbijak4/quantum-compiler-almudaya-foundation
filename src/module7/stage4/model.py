"""
Module 7 Stage 4 — Cloud Hardware Provider Adapter Models & Data Contracts.

Provides data contracts for cloud execution requests, provider job handles,
normalized provider-neutral execution results, and credential references.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class CloudExecutionLifecycleStatus(Enum):
    """Lifecycle status for cloud quantum execution jobs."""
    UNINITIALIZED = "UNINITIALIZED"
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    SUBMITTED = "SUBMITTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    INCONCLUSIVE = "INCONCLUSIVE"


class ExecutionEnvironmentType(Enum):
    """Classification of quantum backend execution target environment."""
    IDEAL_SIMULATOR = "IDEAL_SIMULATOR"
    NOISY_SIMULATOR = "NOISY_SIMULATOR"
    PHYSICAL_HARDWARE = "PHYSICAL_HARDWARE"


@dataclass(frozen=True)
class CloudExecutionRequest:
    """
    Provider-neutral request artifact for submitting a native quantum circuit to a cloud backend.
    """
    request_id: str
    native_circuit_id: str
    native_circuit_hash: str
    backend_id: str
    provider_id: str
    capability_hash: str
    lowering_id: str
    shots: int = 1000
    credential_ref: Optional[str] = None  # Non-sensitive reference, e.g., "env:IBM_QUANTUM_TOKEN"
    request_hash: str = ""

    def __post_init__(self) -> None:
        if not self.request_hash:
            object.__setattr__(self, "request_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "request_id": self.request_id,
            "native_circuit_id": self.native_circuit_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "capability_hash": self.capability_hash,
            "lowering_id": self.lowering_id,
            "shots": self.shots,
            "credential_ref": self.credential_ref,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "native_circuit_id": self.native_circuit_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "capability_hash": self.capability_hash,
            "lowering_id": self.lowering_id,
            "shots": self.shots,
            "credential_ref": self.credential_ref,
            "request_hash": self.request_hash,
        }


@dataclass(frozen=True)
class CloudJobHandle:
    """
    Handle representing a submitted cloud quantum job.
    """
    job_id: str
    provider_job_id: str
    request_id: str
    provider_id: str
    backend_id: str
    status: CloudExecutionLifecycleStatus
    handle_hash: str = ""

    def __post_init__(self) -> None:
        if not self.handle_hash:
            object.__setattr__(self, "handle_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "job_id": self.job_id,
            "provider_job_id": self.provider_job_id,
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "backend_id": self.backend_id,
            "status": self.status.value,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "provider_job_id": self.provider_job_id,
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "backend_id": self.backend_id,
            "status": self.status.value,
            "handle_hash": self.handle_hash,
        }


@dataclass(frozen=True)
class ProviderNeutralExecutionResult:
    """
    Normalized execution result artifact retrieved from a quantum provider.
    """
    job_id: str
    provider_job_id: str
    native_circuit_hash: str
    backend_id: str
    provider_id: str
    environment_type: ExecutionEnvironmentType
    status: CloudExecutionLifecycleStatus
    shots: int
    measurement_counts: Dict[str, int]
    measurement_distribution: Dict[str, float]
    provenance: Dict[str, Any] = field(default_factory=dict)
    result_hash: str = ""

    def __post_init__(self) -> None:
        if not self.result_hash:
            object.__setattr__(self, "result_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "job_id": self.job_id,
            "provider_job_id": self.provider_job_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "environment_type": self.environment_type.value,
            "status": self.status.value,
            "shots": self.shots,
            "measurement_counts": {str(k): int(v) for k, v in sorted(self.measurement_counts.items())},
            "measurement_distribution": {str(k): float(v) for k, v in sorted(self.measurement_distribution.items())},
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "provider_job_id": self.provider_job_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "environment_type": self.environment_type.value,
            "status": self.status.value,
            "shots": self.shots,
            "measurement_counts": dict(self.measurement_counts),
            "measurement_distribution": dict(self.measurement_distribution),
            "provenance": dict(self.provenance),
            "result_hash": self.result_hash,
        }
