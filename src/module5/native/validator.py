"""
Module 5 Stage 4 — NativeCircuitIR 3-Level Validator.

Implements Level 1 Structural, Level 2 Semantic, and Level 3 Mathematical/Closure validation for NativeCircuitIR.
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional
from src.module5.native.model import NativeCircuitIR, SCHEMA_VERSION
from src.module5.native.adapter import BackendAdapter


@dataclass
class NativeCircuitValidationResult:
    """Diagnostic validation result for NativeCircuitIR."""
    valid: bool
    structural_pass: bool = False
    semantic_pass: bool = False
    consistency_pass: bool = False
    vocabulary_closure_pass: bool = False
    errors: List[str] = field(default_factory=list)


def validate_native_circuit_ir(
    circuit: NativeCircuitIR,
    adapter: Optional[BackendAdapter] = None,
) -> NativeCircuitValidationResult:
    """
    Validates NativeCircuitIR across 3 levels.
    Does NOT modify the circuit object. Returns deterministic validation report.
    """
    errors: List[str] = []
    structural_pass = True
    semantic_pass = True
    consistency_pass = True
    vocabulary_closure_pass = True

    # ------------------------------------------------------------------
    # LEVEL 1: STRUCTURAL VALIDATION
    # ------------------------------------------------------------------
    if circuit.schema_version != SCHEMA_VERSION:
        structural_pass = False
        errors.append(f"[Structural Level 1] Invalid schema_version '{circuit.schema_version}', expected '{SCHEMA_VERSION}'.")

    if not circuit.circuit_id or not circuit.circuit_id.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace circuit_id.")

    if not circuit.backend_id or not circuit.backend_id.strip():
        structural_pass = False
        errors.append("[Structural Level 1] Empty or whitespace backend_id.")

    # Unique physical qubits
    if len(circuit.qubits) != len(set(circuit.qubits)):
        structural_pass = False
        errors.append("[Structural Level 1] Duplicate physical qubit IDs in circuit.")

    # Operation index sequential ordering and arity
    for idx, nop in enumerate(circuit.native_operations):
        if nop.operation_index != idx:
            structural_pass = False
            errors.append(f"[Structural Level 1] Non-sequential operation_index at position {idx}: expected {idx}, got {nop.operation_index}.")

        if not nop.native_gate or not nop.native_gate.strip():
            structural_pass = False
            errors.append(f"[Structural Level 1] Empty native_gate at operation_index {nop.operation_index}.")

        if len(nop.operands) != len(set(nop.operands)):
            structural_pass = False
            errors.append(f"[Structural Level 1] Duplicate operand node in native operation '{nop.native_gate}' at op {nop.operation_index}: {nop.operands}.")

    if not structural_pass:
        return NativeCircuitValidationResult(valid=False, errors=errors)

    # ------------------------------------------------------------------
    # LEVEL 2: SEMANTIC VALIDATION & VOCABULARY CLOSURE
    # ------------------------------------------------------------------
    valid_qubits = set(circuit.qubits)

    for nop in circuit.native_operations:
        for p_node in nop.operands:
            if p_node not in valid_qubits:
                semantic_pass = False
                errors.append(f"[Semantic Level 2] Out-of-bounds operand {p_node} in native gate '{nop.native_gate}' at op {nop.operation_index}.")

        if adapter is not None:
            if not adapter.validate_native_operation(nop):
                vocabulary_closure_pass = False
                errors.append(
                    f"[Semantic Level 2] Vocabulary violation: Gate '{nop.native_gate}' at op {nop.operation_index} is not a valid native operation on backend adapter."
                )

    if not semantic_pass or not vocabulary_closure_pass:
        return NativeCircuitValidationResult(
            valid=False,
            structural_pass=structural_pass,
            semantic_pass=semantic_pass,
            vocabulary_closure_pass=vocabulary_closure_pass,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # LEVEL 3: MATHEMATICAL / CONSISTENCY VALIDATION
    # ------------------------------------------------------------------
    # Verify provenance
    if not circuit.provenance or not circuit.provenance.source_rutm_program_hash:
        consistency_pass = False
        errors.append("[Consistency Level 3] Missing or incomplete ExecutionProvenance.")

    all_valid = structural_pass and semantic_pass and consistency_pass and vocabulary_closure_pass

    return NativeCircuitValidationResult(
        valid=all_valid,
        structural_pass=structural_pass,
        semantic_pass=semantic_pass,
        consistency_pass=consistency_pass,
        vocabulary_closure_pass=vocabulary_closure_pass,
        errors=errors,
    )
