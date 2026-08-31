"""
Module 7 Stage 2 — Lowering Models & Data Contracts.

Provides immutable data contracts for lowering policy, decomposition rules,
logical-to-physical qubit mappings, and detailed lowering results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class LoweringStatus(Enum):
    """Execution domain lowering statuses."""
    UNINITIALIZED = "UNINITIALIZED"
    LOWERED = "LOWERED"
    SEMANTICALLY_VERIFIED = "SEMANTICALLY_VERIFIED"
    SEMANTICALLY_NON_EQUIVALENT = "SEMANTICALLY_NON_EQUIVALENT"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class LoweringPolicy:
    """
    Configuration and policy governing logical-to-native circuit lowering.
    """
    policy_id: str
    decomposition_strategy: str = "EXACT_DECOMPOSITION"
    qubit_mapping_strategy: str = "NAIVE_DIRECT"
    routing_strategy: str = "LOOKAHEAD_SWAP"
    allow_ancilla: bool = False
    max_ancilla_count: int = 0
    optimization_level: int = 0
    policy_hash: str = ""

    def __post_init__(self) -> None:
        if not self.policy_hash:
            object.__setattr__(self, "policy_hash", self.compute_policy_hash())

    def compute_policy_hash(self) -> str:
        raw_dict = {
            "policy_id": self.policy_id,
            "decomposition_strategy": self.decomposition_strategy,
            "qubit_mapping_strategy": self.qubit_mapping_strategy,
            "routing_strategy": self.routing_strategy,
            "allow_ancilla": self.allow_ancilla,
            "max_ancilla_count": self.max_ancilla_count,
            "optimization_level": self.optimization_level,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "decomposition_strategy": self.decomposition_strategy,
            "qubit_mapping_strategy": self.qubit_mapping_strategy,
            "routing_strategy": self.routing_strategy,
            "allow_ancilla": self.allow_ancilla,
            "max_ancilla_count": self.max_ancilla_count,
            "optimization_level": self.optimization_level,
            "policy_hash": self.policy_hash,
        }


@dataclass(frozen=True)
class NativeCircuitArtifact:
    """
    Derived native quantum circuit artifact after lowering and topology mapping.
    """
    native_circuit_id: str
    backend_id: str
    capability_hash: str
    native_gate_sequence: Tuple[Dict[str, Any], ...]
    qubit_mapping: Dict[int, int]
    native_gate_count: int
    circuit_depth: int
    inserted_swap_count: int
    native_circuit_hash: str = ""

    def __post_init__(self) -> None:
        if not self.native_circuit_hash:
            object.__setattr__(self, "native_circuit_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "native_circuit_id": self.native_circuit_id,
            "backend_id": self.backend_id,
            "capability_hash": self.capability_hash,
            "native_gate_sequence": [dict(g) for g in self.native_gate_sequence],
            "qubit_mapping": {str(k): v for k, v in self.qubit_mapping.items()},
            "native_gate_count": self.native_gate_count,
            "circuit_depth": self.circuit_depth,
            "inserted_swap_count": self.inserted_swap_count,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "native_circuit_id": self.native_circuit_id,
            "backend_id": self.backend_id,
            "capability_hash": self.capability_hash,
            "native_gate_sequence": [dict(g) for g in self.native_gate_sequence],
            "qubit_mapping": dict(self.qubit_mapping),
            "native_gate_count": self.native_gate_count,
            "circuit_depth": self.circuit_depth,
            "inserted_swap_count": self.inserted_swap_count,
            "native_circuit_hash": self.native_circuit_hash,
        }


@dataclass(frozen=True)
class LoweringResultArtifact:
    """
    Immutable comprehensive lowering result artifact.
    """
    lowering_id: str
    logical_circuit_id: str
    logical_circuit_hash: str
    backend_id: str
    capability_version: str
    capability_hash: str
    policy_hash: str
    status: LoweringStatus
    native_circuit: Optional[NativeCircuitArtifact]
    qubit_mapping: Dict[int, int]
    semantic_verification_status: str
    semantic_verification_reference: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    lowering_hash: str = ""

    def __post_init__(self) -> None:
        if not self.lowering_hash:
            object.__setattr__(self, "lowering_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "lowering_id": self.lowering_id,
            "logical_circuit_id": self.logical_circuit_id,
            "logical_circuit_hash": self.logical_circuit_hash,
            "backend_id": self.backend_id,
            "capability_version": self.capability_version,
            "capability_hash": self.capability_hash,
            "policy_hash": self.policy_hash,
            "status": self.status.value,
            "qubit_mapping": {str(k): v for k, v in self.qubit_mapping.items()},
            "semantic_verification_status": self.semantic_verification_status,
            "semantic_verification_reference": self.semantic_verification_reference,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lowering_id": self.lowering_id,
            "logical_circuit_id": self.logical_circuit_id,
            "logical_circuit_hash": self.logical_circuit_hash,
            "backend_id": self.backend_id,
            "capability_version": self.capability_version,
            "capability_hash": self.capability_hash,
            "policy_hash": self.policy_hash,
            "status": self.status.value,
            "native_circuit": self.native_circuit.to_dict() if self.native_circuit else None,
            "qubit_mapping": dict(self.qubit_mapping),
            "semantic_verification_status": self.semantic_verification_status,
            "semantic_verification_reference": self.semantic_verification_reference,
            "provenance": dict(self.provenance),
            "lowering_hash": self.lowering_hash,
        }
