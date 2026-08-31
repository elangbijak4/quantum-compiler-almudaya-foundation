"""
Module 7 — Quantum Backend & Execution Domain Initialization Models.

Provides foundational type declarations, constants, enums, and data contracts
for backend capabilities, execution jobs, lowering results, and verification metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class ExecutionLifecycleStatus(Enum):
    """Execution domain lifecycle statuses."""
    UNINITIALIZED = "UNINITIALIZED"
    BACKEND_SELECTED = "BACKEND_SELECTED"
    CAPABILITY_VALIDATED = "CAPABILITY_VALIDATED"
    LOWERING_STARTED = "LOWERING_STARTED"
    LOWERING_COMPLETED = "LOWERING_COMPLETED"
    SUBMISSION_STARTED = "SUBMISSION_STARTED"
    SUBMITTED = "SUBMITTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    RESULT_RETRIEVED = "RESULT_RETRIEVED"
    RESULT_VERIFIED = "RESULT_VERIFIED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


class ExecutionFailureCategory(Enum):
    """Execution domain failure classification taxonomy."""
    BACKEND_NOT_FOUND = "BACKEND_NOT_FOUND"
    BACKEND_IDENTITY_INVALID = "BACKEND_IDENTITY_INVALID"
    CAPABILITY_INVALID = "CAPABILITY_INVALID"
    CAPABILITY_VERSION_INVALID = "CAPABILITY_VERSION_INVALID"
    REGISTRY_INTEGRITY_FAILURE = "REGISTRY_INTEGRITY_FAILURE"
    BACKEND_UNSUPPORTED = "BACKEND_UNSUPPORTED"
    BACKEND_CAPABILITY_MISMATCH = "BACKEND_CAPABILITY_MISMATCH"
    LOWERING_FAILURE = "LOWERING_FAILURE"
    TOPOLOGY_FAILURE = "TOPOLOGY_FAILURE"
    SUBMISSION_FAILURE = "SUBMISSION_FAILURE"
    QUEUE_FAILURE = "QUEUE_FAILURE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"
    RESULT_RETRIEVAL_FAILURE = "RESULT_RETRIEVAL_FAILURE"
    RESULT_VERIFICATION_FAILURE = "RESULT_VERIFICATION_FAILURE"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    CREDENTIAL_FAILURE = "CREDENTIAL_FAILURE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class CredentialReference:
    """
    Non-sensitive credential reference identifier.
    Raw secrets (API keys, tokens) MUST NEVER be stored in this object or serialized provenance.
    """
    credential_ref: str  # e.g., "env:IBM_QUANTUM_TOKEN" or "secret_manager:aws_braket_key"
    provider_id: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "credential_ref": self.credential_ref,
            "provider_id": self.provider_id,
        }


@dataclass(frozen=True)
class BackendCapabilityModel:
    """
    Provider-neutral backend capability model (C_backend).
    Represents actual physical or virtual execution capabilities of a target device/simulator.
    """
    backend_id: str
    provider_id: str
    backend_type: str  # "VIRTUAL_SIMULATOR" or "PHYSICAL_HARDWARE"
    qubit_count: int
    native_gate_set: Tuple[str, ...]
    topology_coupling_map: Tuple[Tuple[int, int], ...]
    max_shots: int
    supports_custom_pulses: bool = False
    capability_version: str = "1.0.0"
    capability_hash: str = ""

    def __post_init__(self) -> None:
        self.validate()
        if not self.capability_hash:
            object.__setattr__(self, "capability_hash", self.compute_capability_hash())

    def validate(self) -> None:
        """Validates capability model invariants."""
        if not self.backend_id or not isinstance(self.backend_id, str):
            raise ValueError("Invalid Backend Capability: backend_id must be a non-empty string.")
        if not self.provider_id or not isinstance(self.provider_id, str):
            raise ValueError("Invalid Backend Capability: provider_id must be a non-empty string.")
        if self.backend_type not in ("VIRTUAL_SIMULATOR", "PHYSICAL_HARDWARE", "CLOUD_SIMULATOR", "LOCAL_REFERENCE_SIMULATOR"):
            raise ValueError(f"Invalid Backend Capability: backend_type '{self.backend_type}' is unsupported.")
        if self.qubit_count <= 0:
            raise ValueError(f"Invalid Backend Capability: qubit_count must be > 0, got {self.qubit_count}.")
        if self.max_shots <= 0:
            raise ValueError(f"Invalid Backend Capability: max_shots must be > 0, got {self.max_shots}.")
        if not self.native_gate_set:
            raise ValueError("Invalid Backend Capability: native_gate_set cannot be empty.")

        # Topology validation
        seen_edges = set()
        for edge in self.topology_coupling_map:
            if len(edge) != 2:
                raise ValueError(f"Malformed Topology Edge: edge must be a pair of qubit indices, got {edge}.")
            q1, q2 = edge
            if q1 == q2:
                raise ValueError(f"Malformed Topology Edge: self-loop on qubit {q1} is invalid.")
            if q1 < 0 or q1 >= self.qubit_count or q2 < 0 or q2 >= self.qubit_count:
                raise ValueError(f"Malformed Topology Edge: pair ({q1}, {q2}) references out-of-bounds qubit (qubit_count={self.qubit_count}).")
            if (q1, q2) in seen_edges:
                raise ValueError(f"Duplicate Topology Edge: edge ({q1}, {q2}) appears more than once.")
            seen_edges.add((q1, q2))

    def compute_capability_hash(self) -> str:
        """Computes full 64-character SHA-256 digest over canonical JSON representation."""
        raw_dict = {
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "backend_type": self.backend_type,
            "qubit_count": self.qubit_count,
            "native_gate_set": sorted(list(self.native_gate_set)),
            "topology_coupling_map": [list(pair) for pair in sorted(list(self.topology_coupling_map))],
            "max_shots": self.max_shots,
            "supports_custom_pulses": self.supports_custom_pulses,
            "capability_version": self.capability_version,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def supports_gate(self, gate_name: str) -> bool:
        """Inspects whether gate_name is present in native_gate_set."""
        return gate_name in self.native_gate_set

    def supports_qubits(self, required_qubits: int) -> bool:
        """Inspects whether required_qubits fits within qubit_count."""
        return required_qubits <= self.qubit_count

    def supports_shots(self, required_shots: int) -> bool:
        """Inspects whether required_shots fits within max_shots."""
        return required_shots <= self.max_shots

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend_id": self.backend_id,
            "provider_id": self.provider_id,
            "backend_type": self.backend_type,
            "qubit_count": self.qubit_count,
            "native_gate_set": list(self.native_gate_set),
            "topology_coupling_map": [list(pair) for pair in self.topology_coupling_map],
            "max_shots": self.max_shots,
            "supports_custom_pulses": self.supports_custom_pulses,
            "capability_version": self.capability_version,
            "capability_hash": self.capability_hash,
        }


@dataclass(frozen=True)
class LoweringResult:
    """
    Result model for logical-to-native circuit lowering/transpilation.
    """
    lowering_id: str
    logical_circuit_id: str
    backend_id: str
    native_gate_sequence: Tuple[Dict[str, Any], ...]
    qubit_mapping: Dict[int, int]
    is_equivalent_preserved: bool
    lowering_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lowering_id": self.lowering_id,
            "logical_circuit_id": self.logical_circuit_id,
            "backend_id": self.backend_id,
            "native_gate_sequence": list(self.native_gate_sequence),
            "qubit_mapping": dict(self.qubit_mapping),
            "is_equivalent_preserved": self.is_equivalent_preserved,
            "lowering_hash": self.lowering_hash,
        }


@dataclass(frozen=True)
class ExecutionJobResult:
    """
    Provider-neutral execution job result model.
    """
    job_id: str
    backend_id: str
    logical_circuit_id: str
    lowering_id: str
    status: ExecutionLifecycleStatus
    shots: int
    measurement_counts: Dict[str, int]
    measurement_distribution: Dict[str, float]
    provenance: Dict[str, Any] = field(default_factory=dict)
    job_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "backend_id": self.backend_id,
            "logical_circuit_id": self.logical_circuit_id,
            "lowering_id": self.lowering_id,
            "status": self.status.value,
            "shots": self.shots,
            "measurement_counts": dict(self.measurement_counts),
            "measurement_distribution": dict(self.measurement_distribution),
            "provenance": dict(self.provenance),
            "job_hash": self.job_hash,
        }
