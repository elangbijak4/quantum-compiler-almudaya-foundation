"""
Module 7 Stage 1 — Serialization Engine.

Canonical JSON serialization and deserialization for BackendCapabilityModel and Stage 1 types.
Enforces deserialize(serialize(X)) == X, canonical key ordering, and credential isolation.
"""

import json
from typing import Dict, Any
from src.module7.model import (
    BackendCapabilityModel,
    CredentialReference,
)


def serialize_backend_capability_model(cap: BackendCapabilityModel) -> str:
    """
    Serializes BackendCapabilityModel into canonical JSON string.
    Keys are sorted deterministically. Raw secrets MUST NOT be included.
    """
    return json.dumps(cap.to_dict(), indent=2, sort_keys=True)


def deserialize_backend_capability_model(json_str: str) -> BackendCapabilityModel:
    """
    Deserializes canonical JSON string into BackendCapabilityModel.
    Verifies capability_hash integrity upon construction.
    """
    data = json.loads(json_str)

    native_gates = tuple(data["native_gate_set"])
    topology = tuple(tuple(pair) for pair in data["topology_coupling_map"])

    cap = BackendCapabilityModel(
        backend_id=data["backend_id"],
        provider_id=data["provider_id"],
        backend_type=data["backend_type"],
        qubit_count=data["qubit_count"],
        native_gate_set=native_gates,
        topology_coupling_map=topology,
        max_shots=data["max_shots"],
        supports_custom_pulses=data.get("supports_custom_pulses", False),
        capability_version=data.get("capability_version", "1.0.0"),
        capability_hash=data.get("capability_hash", ""),
    )

    expected_hash = cap.compute_capability_hash()
    if cap.capability_hash and cap.capability_hash != expected_hash:
        raise ValueError(f"REGISTRY_INTEGRITY_FAILURE: Capability hash mismatch on {cap.backend_id}: got {cap.capability_hash}, expected {expected_hash}")

    return cap
