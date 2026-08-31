"""
Module 5 Stage 2 — PhysicalCircuitIR vs BackendCapabilityModel Compatibility Evaluator.

Determines whether a PhysicalCircuitIR is compatible with a BackendCapabilityModel without mutating
either input or performing SWAP routing.
"""

from dataclasses import dataclass, field
from typing import List
from src.module5.physical_ir.model import PhysicalCircuitIR
from src.module5.backend.model import BackendCapabilityModel
from src.module5.backend.validator import validate_backend_capabilities


@dataclass
class BackendCompatibilityResult:
    """Detailed compatibility diagnostic report."""
    compatible: bool
    structural_pass: bool = False
    semantic_pass: bool = False
    consistency_pass: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_backend_compatibility(
    physical_circuit: PhysicalCircuitIR,
    backend_capabilities: BackendCapabilityModel,
) -> BackendCompatibilityResult:
    """
    Primary Stage 2 API: Validates compatibility between PhysicalCircuitIR and BackendCapabilityModel.
    
    Checks:
    1. Backend capabilities validity.
    2. Physical qubit capacity (len(physical_qubits) <= max_qubits).
    3. Referenced physical node existence in backend topology.
    4. Topology edge connectivity for 2-qubit operations.
    5. Gate capability support.
    6. Gate arity match.
    
    Does NOT perform SWAP routing or gate decomposition.
    """
    errors: List[str] = []
    warnings: List[str] = []
    structural_pass = True
    semantic_pass = True
    consistency_pass = True

    # 1. Validate backend capabilities model itself
    backend_val = validate_backend_capabilities(backend_capabilities)
    if not backend_val.valid:
        structural_pass = False
        errors.append(f"[Compatibility] Invalid BackendCapabilityModel: {backend_val.errors}")

    # 2. Qubit capacity check
    circuit_qubit_count = len(physical_circuit.physical_qubits)
    if circuit_qubit_count > backend_capabilities.qubit_capacity.max_qubits:
        semantic_pass = False
        errors.append(
            f"[Compatibility] Qubit capacity exceeded: PhysicalCircuitIR requires {circuit_qubit_count} qubits, backend max_qubits is {backend_capabilities.qubit_capacity.max_qubits}."
        )

    # 3. Physical node existence in backend
    for pq in physical_circuit.physical_qubits:
        if not backend_capabilities.supports_qubit(pq.node_id):
            semantic_pass = False
            errors.append(f"[Compatibility] Unsupported physical node_id {pq.node_id} on backend '{backend_capabilities.identity.backend_id}'.")

    # 4. Gate capability and topology connectivity checks
    for gate in physical_circuit.gates:
        g_type = gate.gate_type.upper()
        if not backend_capabilities.supports_gate(g_type):
            semantic_pass = False
            errors.append(f"[Compatibility] Unsupported gate '{gate.gate_type}' at op {gate.operation_index} for backend '{backend_capabilities.identity.backend_id}'.")

        all_nodes = gate.control_nodes + (gate.target_node,)
        expected_arity = len(all_nodes)
        if backend_capabilities.supports_gate(g_type):
            g_cap = backend_capabilities.gate_capabilities[g_type]
            if g_cap.arity != expected_arity:
                consistency_pass = False
                errors.append(
                    f"[Compatibility] Arity mismatch for gate '{gate.gate_type}' at op {gate.operation_index}: circuit operation has arity {expected_arity}, backend expects {g_cap.arity}."
                )

        # Topology connectivity check for 2-node gates
        if len(all_nodes) == 2:
            u, v = all_nodes
            if not backend_capabilities.supports_connection(u, v):
                semantic_pass = False
                errors.append(
                    f"[Compatibility] Topology violation: Physical connection ({u}, {v}) required by gate '{gate.gate_type}' at op {gate.operation_index} is unsupported by backend coupling topology."
                )

    all_compatible = structural_pass and semantic_pass and consistency_pass

    return BackendCompatibilityResult(
        compatible=all_compatible,
        structural_pass=structural_pass,
        semantic_pass=semantic_pass,
        consistency_pass=consistency_pass,
        errors=errors,
        warnings=warnings,
    )
