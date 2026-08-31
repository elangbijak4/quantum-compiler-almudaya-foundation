"""
Module 5 Stage 1 — PhysicalCircuitIR 3-Level Validator.

Implements Level 1 Structural, Level 2 Semantic, and Level 3 Consistency validation for PhysicalCircuitIR.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional
from src.module5.physical_ir.model import (
    PhysicalCircuitIR,
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    ExecutionProvenance,
    SCHEMA_VERSION,
)


@dataclass
class PhysicalCircuitValidationResult:
    """Diagnostic validation result for PhysicalCircuitIR."""
    valid: bool
    structural_pass: bool = False
    semantic_pass: bool = False
    consistency_pass: bool = False
    errors: List[str] = field(default_factory=list)


def validate_physical_circuit_ir(circuit: PhysicalCircuitIR) -> PhysicalCircuitValidationResult:
    """
    Primary Stage 1 API: Validates a PhysicalCircuitIR across 3 levels.
    Does NOT modify the circuit object. Returns deterministic validation report.
    """
    errors: List[str] = []
    structural_pass = True
    semantic_pass = True
    consistency_pass = True

    # ------------------------------------------------------------------
    # LEVEL 1: STRUCTURAL VALIDATION
    # ------------------------------------------------------------------
    if circuit.schema_version != SCHEMA_VERSION:
        structural_pass = False
        errors.append(f"[Structural Level 1] Invalid schema_version '{circuit.schema_version}', expected '{SCHEMA_VERSION}'.")

    if not circuit.physical_circuit_id or not circuit.physical_circuit_id.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace physical_circuit_id.")

    if not circuit.source_logical_circuit_id or not circuit.source_logical_circuit_id.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace source_logical_circuit_id.")

    # Physical qubit uniqueness
    seen_nodes: Set[int] = set()
    for pq in circuit.physical_qubits:
        if pq.node_id in seen_nodes:
            structural_pass = False
            errors.append(f"[Structural Level 1] Duplicate physical qubit node_id: {pq.node_id}.")
        seen_nodes.add(pq.node_id)

    # Gate operation index uniqueness and sequential ordering
    for idx, gate in enumerate(circuit.gates):
        if gate.operation_index != idx:
            structural_pass = False
            errors.append(f"[Structural Level 1] Non-sequential operation_index at position {idx}: expected {idx}, got {gate.operation_index}.")

        if not gate.gate_type or not gate.gate_type.strip():
            structural_pass = False
            errors.append(f"[Structural Level 1] Empty gate_type at operation_index {gate.operation_index}.")

        # Control/target distinctness and duplicate control nodes
        if gate.target_node in gate.control_nodes:
            structural_pass = False
            errors.append(f"[Structural Level 1] Control-target collision in gate '{gate.gate_type}' at op {gate.operation_index}: target {gate.target_node} in controls {gate.control_nodes}.")

        if len(gate.control_nodes) != len(set(gate.control_nodes)):
            structural_pass = False
            errors.append(f"[Structural Level 1] Duplicate control node in gate '{gate.gate_type}' at op {gate.operation_index}: controls {gate.control_nodes}.")

    if not structural_pass:
        return PhysicalCircuitValidationResult(valid=False, errors=errors)

    # ------------------------------------------------------------------
    # LEVEL 2: SEMANTIC VALIDATION
    # ------------------------------------------------------------------
    valid_node_ids = set(pq.node_id for pq in circuit.physical_qubits)

    # Gate node existence
    for gate in circuit.gates:
        if gate.target_node not in valid_node_ids:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Out-of-bounds target_node {gate.target_node} in gate '{gate.gate_type}' at op {gate.operation_index}.")

        for c_node in gate.control_nodes:
            if c_node not in valid_node_ids:
                semantic_pass = False
                errors.append(f"[Semantic Level 2] Out-of-bounds control_node {c_node} in gate '{gate.gate_type}' at op {gate.operation_index}.")

    # Mapping physical node existence
    for p_node in circuit.mapping.mapping.values():
        if p_node not in valid_node_ids:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Unknown physical node {p_node} in logical-to-physical mapping.")

    # Mapping injectivity
    if not circuit.mapping.is_injective():
        semantic_pass = False
        errors.append("[Semantic Level 2] Non-injective logical-to-physical mapping detected (collision).")

    # Topology node consistency
    for t_node in circuit.topology.nodes:
        if t_node not in valid_node_ids:
            semantic_pass = False
            errors.append(f"[Semantic Level 2] Topology node {t_node} is not defined in physical_qubits set.")

    # Topology edge connectivity check for 2-qubit native operations
    if circuit.topology.edges:
        for gate in circuit.gates:
            if len(gate.control_nodes) == 1:
                c_node = gate.control_nodes[0]
                if not circuit.topology.is_connected(c_node, gate.target_node):
                    semantic_pass = False
                    errors.append(
                        f"[Semantic Level 2] Topology violation: Disconnected physical edge ({c_node}, {gate.target_node}) for gate '{gate.gate_type}' at op {gate.operation_index}."
                    )

    # Provenance presence
    if circuit.provenance is None:
        semantic_pass = False
        errors.append("[Semantic Level 2] Missing ExecutionProvenance metadata.")
    else:
        p = circuit.provenance
        if not p.source_rutm_program_hash or not p.source_qtm_machine_id or not p.logical_circuit_id:
            semantic_pass = False
            errors.append("[Semantic Level 2] Incomplete or empty fields in ExecutionProvenance.")

    if not semantic_pass:
        return PhysicalCircuitValidationResult(
            valid=False,
            structural_pass=structural_pass,
            semantic_pass=False,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # LEVEL 3: MATHEMATICAL / CONSISTENCY VALIDATION
    # ------------------------------------------------------------------
    # Known canonical arity rules
    known_arities = {
        "X": 0,
        "Y": 0,
        "Z": 0,
        "H": 0,
        "SX": 0,
        "S": 0,
        "T": 0,
        "CNOT": 1,
        "CZ": 1,
        "SWAP": 1,
        "TOFFOLI": 2,
    }

    for gate in circuit.gates:
        expected_ctrls = known_arities.get(gate.gate_type.upper())
        if expected_ctrls is not None and len(gate.control_nodes) != expected_ctrls:
            consistency_pass = False
            errors.append(
                f"[Consistency Level 3] Arity mismatch for canonical gate '{gate.gate_type}' at op {gate.operation_index}: expected {expected_ctrls} controls, got {len(gate.control_nodes)}."
            )

    all_valid = structural_pass and semantic_pass and consistency_pass

    return PhysicalCircuitValidationResult(
        valid=all_valid,
        structural_pass=structural_pass,
        semantic_pass=semantic_pass,
        consistency_pass=consistency_pass,
        errors=errors,
    )
