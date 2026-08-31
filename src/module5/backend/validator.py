"""
Module 5 Stage 2 — Backend Capability 3-Level Validator.

Implements Level 1 Structural, Level 2 Semantic, and Level 3 Consistency validation for BackendCapabilityModel.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional
from src.module5.backend.model import (
    BackendCapabilityModel,
    BACKEND_CAPABILITY_SCHEMA_VERSION,
)


@dataclass
class CapabilityValidationResult:
    """Diagnostic validation result for BackendCapabilityModel."""
    valid: bool
    structural_pass: bool = False
    semantic_pass: bool = False
    consistency_pass: bool = False
    errors: List[str] = field(default_factory=list)


def validate_backend_capabilities(model: BackendCapabilityModel) -> CapabilityValidationResult:
    """
    Validates a BackendCapabilityModel across 3 levels.
    Does NOT modify the model object. Returns deterministic validation report.
    """
    errors: List[str] = []
    structural_pass = True
    semantic_pass = True
    consistency_pass = True

    # ------------------------------------------------------------------
    # LEVEL 1: STRUCTURAL VALIDATION
    # ------------------------------------------------------------------
    if model.schema_version != BACKEND_CAPABILITY_SCHEMA_VERSION:
        structural_pass = False
        errors.append(f"[Structural Level 1] Invalid schema_version '{model.schema_version}', expected '{BACKEND_CAPABILITY_SCHEMA_VERSION}'.")

    if not model.identity.backend_id or not model.identity.backend_id.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace backend_id.")

    if not model.identity.backend_name or not model.identity.backend_name.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace backend_name.")

    if model.qubit_capacity.max_qubits <= 0:
        structural_pass = False
        errors.append(f"[Structural Level 1] Invalid max_qubits: {model.qubit_capacity.max_qubits}. Must be > 0.")

    # Topology structural checks
    for node in model.topology.nodes:
        if node < 0:
            structural_pass = False
            errors.append(f"[Structural Level 1] Invalid negative topology node_id: {node}.")

    for u, v in model.topology.edges:
        if u == v:
            structural_pass = False
            errors.append(f"[Structural Level 1] Self-loop forbidden in topology: ({u}, {v}).")

    # Gate capability structural checks
    for g_key, g_cap in model.gate_capabilities.items():
        if g_key != g_cap.gate_type.upper():
            structural_pass = False
            errors.append(f"[Structural Level 1] Key mismatch in gate_capabilities dictionary: key '{g_key}' vs gate_type '{g_cap.gate_type}'.")

        if g_cap.arity < 1:
            structural_pass = False
            errors.append(f"[Structural Level 1] Invalid arity {g_cap.arity} for gate '{g_cap.gate_type}'. Must be >= 1.")

    if not structural_pass:
        return CapabilityValidationResult(valid=False, errors=errors)

    # ------------------------------------------------------------------
    # LEVEL 2: SEMANTIC VALIDATION
    # ------------------------------------------------------------------
    # Qubit capacity bound vs topology nodes
    for node in model.topology.nodes:
        if node >= model.qubit_capacity.max_qubits:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Topology node_id {node} exceeds max_qubits capacity {model.qubit_capacity.max_qubits}.")

    if model.qubit_capacity.active_qubits:
        for node in model.qubit_capacity.active_qubits:
            if node >= model.qubit_capacity.max_qubits:
                semantic_pass = False
                errors.append(f"[Semantic Level 2] Active qubit node_id {node} exceeds max_qubits capacity {model.qubit_capacity.max_qubits}.")

    # Gate constraint semantic mapping
    for c_key, c_val in model.gate_constraints.items():
        if c_key not in model.gate_capabilities:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Gate constraint defined for undeclared gate capability: '{c_key}'.")

    # Provenance semantic verification
    if model.provenance is None:
        semantic_pass = False
        errors.append("[Semantic Level 2] Missing BackendCapabilityProvenance metadata.")
    else:
        if model.provenance.backend_id != model.identity.backend_id:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Provenance backend_id mismatch: '{model.provenance.backend_id}' vs '{model.identity.backend_id}'.")

    if not semantic_pass:
        return CapabilityValidationResult(
            valid=False,
            structural_pass=structural_pass,
            semantic_pass=False,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # LEVEL 3: CONSISTENCY VALIDATION
    # ------------------------------------------------------------------
    # Measurement and execution consistency
    if model.measurement.supports_counts and not model.measurement.supports_measurement:
        consistency_pass = False
        errors.append("[Consistency Level 3] Contradiction: supports_counts is True but supports_measurement is False.")

    if model.execution.supports_sampling and not model.measurement.supports_measurement:
        consistency_pass = False
        errors.append("[Consistency Level 3] Contradiction: supports_sampling is True but supports_measurement is False.")

    all_valid = structural_pass and semantic_pass and consistency_pass

    return CapabilityValidationResult(
        valid=all_valid,
        structural_pass=structural_pass,
        semantic_pass=semantic_pass,
        consistency_pass=consistency_pass,
        errors=errors,
    )
