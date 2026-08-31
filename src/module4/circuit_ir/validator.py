"""
Module 4 Stage 2 — Structural, Semantic, and Mathematical Validator for QuantumCircuitIR.

Enforces 3-Level validation rules:
- Level 1: Structural & AST integrity checks
- Level 2: Semantic register, ancilla, ordering, and provenance checks
- Level 3: Mathematical unitariness & qubit aliasing invariants
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    QubitRef,
    GateOperation,
    LogicalGateType,
    AncillaStatus,
    RegisterType,
    SCHEMA_VERSION,
)


@dataclass(frozen=True)
class CircuitValidationResult:
    """Outcome of validating a QuantumCircuitIR instance."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_circuit_ir(circuit: QuantumCircuitIR) -> CircuitValidationResult:
    """
    Validates a QuantumCircuitIR instance across Level 1, Level 2, and Level 3 checks.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # -------------------------------------------------------------
    # LEVEL 1: Structural Validation
    # -------------------------------------------------------------
    if not circuit.circuit_id or not isinstance(circuit.circuit_id, str):
        errors.append("Circuit ID must be a non-empty string.")

    if circuit.schema_version != SCHEMA_VERSION:
        errors.append(f"Invalid schema version '{circuit.schema_version}'. Expected '{SCHEMA_VERSION}'.")

    # Register uniqueness and width validation
    seen_registers: Set[str] = set()
    register_map: Dict[str, QubitRegister] = {}

    for reg in circuit.registers:
        if reg.register_id in seen_registers:
            errors.append(f"Duplicate register ID '{reg.register_id}'.")
        seen_registers.add(reg.register_id)
        register_map[reg.register_id] = reg

        if reg.width <= 0:
            errors.append(f"Register '{reg.register_id}' must have positive width, got {reg.width}.")

    # Gate operation structural checks
    seen_qubit_refs: Set[str] = set()
    for idx, gate in enumerate(circuit.gates):
        # Sequential ordering
        if gate.operation_index != idx:
            errors.append(f"Nondeterministic operation ordering at index {idx}: got index {gate.operation_index}.")

        # Gate type & arity checks
        if gate.gate_type == LogicalGateType.X:
            if len(gate.control_qubits) != 0:
                errors.append(f"Gate {idx} (X): Expected 0 control qubits, got {len(gate.control_qubits)}.")
        elif gate.gate_type == LogicalGateType.CNOT:
            if len(gate.control_qubits) != 1:
                errors.append(f"Gate {idx} (CNOT): Expected 1 control qubit, got {len(gate.control_qubits)}.")
        elif gate.gate_type == LogicalGateType.TOFFOLI:
            if len(gate.control_qubits) != 2:
                errors.append(f"Gate {idx} (TOFFOLI): Expected 2 control qubits, got {len(gate.control_qubits)}.")
        else:
            errors.append(f"Gate {idx}: Unknown gate type '{gate.gate_type}'.")

        # Qubit reference bounds & validity
        all_refs = gate.all_qubit_refs
        gate_ref_set: Set[str] = set()

        for qref in all_refs:
            if qref.register_id not in register_map:
                errors.append(f"Gate {idx}: Referenced register '{qref.register_id}' does not exist.")
            else:
                target_reg = register_map[qref.register_id]
                if qref.index < 0 or qref.index >= target_reg.width:
                    errors.append(
                        f"Gate {idx}: Qubit index {qref.index} out of bounds for register '{qref.register_id}' (width {target_reg.width})."
                    )

            ref_str = qref.to_string()
            if ref_str in gate_ref_set:
                errors.append(f"Gate {idx}: Qubit aliasing / collision for qubit '{ref_str}' within single gate.")
            gate_ref_set.add(ref_str)
            seen_qubit_refs.add(ref_str)

    # -------------------------------------------------------------
    # LEVEL 2: Semantic Validation
    # -------------------------------------------------------------
    # Input / Output register validity
    for in_reg in circuit.input_register_ids:
        if in_reg not in register_map:
            errors.append(f"Input register '{in_reg}' is not declared in registers.")
    for out_reg in circuit.output_register_ids:
        if out_reg not in register_map:
            errors.append(f"Output register '{out_reg}' is not declared in registers.")

    # Ancilla declarations & cleanliness check
    for anc in circuit.ancilla_declarations:
        qref = anc.qubit_ref
        if qref.register_id not in register_map:
            errors.append(f"Ancilla declaration references non-existent register '{qref.register_id}'.")
        else:
            reg = register_map[qref.register_id]
            if reg.register_type != RegisterType.ANCILLA:
                warnings.append(f"Ancilla declared on non-ancilla register '{qref.register_id}'.")

        if anc.initial_status != AncillaStatus.CLEAN:
            errors.append(f"Dirty initial ancilla status '{anc.initial_status}' on qubit '{qref.to_string()}'.")
        if anc.expected_final_status != AncillaStatus.CLEAN:
            errors.append(f"Dirty final ancilla status '{anc.expected_final_status}' on qubit '{qref.to_string()}'.")

    # Provenance validation
    if circuit.provenance is not None:
        if not circuit.provenance.source_rutm_program_hash:
            errors.append("Circuit provenance missing source RUTM program hash.")
        if not circuit.provenance.source_qtm_machine_id:
            errors.append("Circuit provenance missing source QTM machine ID.")

    # -------------------------------------------------------------
    # LEVEL 3: Mathematical Invariant Validation
    # -------------------------------------------------------------
    # Primitive logical gates (X, CNOT, TOFFOLI) are structurally guaranteed unitary.
    # Check that no invalid aliasing or non-unitary structures exist.

    valid = len(errors) == 0
    return CircuitValidationResult(valid=valid, errors=errors, warnings=warnings)
