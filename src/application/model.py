"""
Application / Product Layer — Data Models & Contract Types.

Provides immutable dataclasses for ApplicationRequest, ApplicationResponse,
and application execution intent enumerations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class ApplicationIntent(Enum):
    """Supported application request operational intents."""
    COMPILE = "COMPILE"
    INSPECT = "INSPECT"
    SIMULATE = "SIMULATE"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    LINEAGE = "LINEAGE"


class ApplicationStatus(Enum):
    """Application request completion status."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class ApplicationRequest:
    """
    Immutable user/product intent request submitted to ApplicationContractService.
    """
    request_id: str
    intent: ApplicationIntent
    source_code: Optional[str] = None
    logical_circuit_id: Optional[str] = None
    native_circuit_id: Optional[str] = None
    backend_id: str = "LOCAL_REFERENCE"
    provider_id: str = "LOCAL_REFERENCE"
    shots: int = 1000
    seed: Optional[int] = None
    credential_ref: Optional[str] = None
    verification_policy_id: str = "POLICY_DEFAULT_01"
    request_hash: str = ""

    def __post_init__(self) -> None:
        if not self.request_hash:
            object.__setattr__(self, "request_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "request_id": self.request_id,
            "intent": self.intent.value,
            "source_code": self.source_code or "",
            "logical_circuit_id": self.logical_circuit_id or "",
            "native_circuit_id": self.native_circuit_id or "",
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "shots": int(self.shots),
            "seed": int(self.seed) if self.seed is not None else None,
            "credential_ref": self.credential_ref or "",
            "verification_policy_id": self.verification_policy_id,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "intent": self.intent.value,
            "source_code": self.source_code,
            "logical_circuit_id": self.logical_circuit_id,
            "native_circuit_id": self.native_circuit_id,
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "shots": self.shots,
            "seed": self.seed,
            "credential_ref": self.credential_ref,
            "verification_policy_id": self.verification_policy_id,
            "request_hash": self.request_hash,
        }


@dataclass(frozen=True)
class ApplicationResponse:
    """
    Immutable application response returned by ApplicationContractService to products.
    """
    request_id: str
    intent: ApplicationIntent
    status: ApplicationStatus
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    artifact_references: Dict[str, str] = field(default_factory=dict)
    result_payload: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    response_version: str = "1.0.0"
    response_hash: str = ""

    def __post_init__(self) -> None:
        if not self.response_hash:
            object.__setattr__(self, "response_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "request_id": self.request_id,
            "intent": self.intent.value,
            "status": self.status.value,
            "error_code": self.error_code or "",
            "error_message": self.error_message or "",
            "artifact_references": dict(self.artifact_references),
            "response_version": self.response_version,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "intent": self.intent.value,
            "status": self.status.value,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "artifact_references": dict(self.artifact_references),
            "result_payload": dict(self.result_payload),
            "diagnostics": dict(self.diagnostics),
            "response_version": self.response_version,
            "response_hash": self.response_hash,
        }
