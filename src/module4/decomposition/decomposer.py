"""
Module 4 Stage 4 — Reversible Gate Decomposition Engine.

Transforms logical reversible circuits containing multi-controlled operations (k > 2)
into explicit primitive gate operations (X, CNOT, TOFFOLI) using Bennett Uncomputation Protocol.
"""

from typing import List, Dict, Set, Tuple, Optional
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    QubitRef,
    GateOperation,
    AncillaDeclaration,
    CircuitProvenance,
    RegisterType,
    AncillaStatus,
    LogicalGateType,
    SCHEMA_VERSION,
)
from src.module4.circuit_ir.validator import validate_circuit_ir
from src.module4.synthesis.ancilla import AncillaManager, synthesize_multi_controlled_not


def decompose_circuit_ir(circuit: QuantumCircuitIR, circuit_id: Optional[str] = None) -> QuantumCircuitIR:
    """
    Primary Stage 4 API: Decomposes all multi-controlled operations (k > 2) in a QuantumCircuitIR
    into primitive gates (X, CNOT, TOFFOLI) with clean Bennett uncomputation.
    
    Guarantees:
    1. Output contains ONLY X (arity 1), CNOT (arity 2), TOFFOLI (arity 3).
    2. k=0 -> X, k=1 -> CNOT, k=2 -> TOFFOLI require NO workspace ancillas.
    3. k > 2 uses Toffoli AND-tree compute/use/uncompute protocol.
    4. All allocated workspace ancillas return cleanly to |0>.
    5. Rejects unsupported or unknown gate types.
    6. Output passes validate_circuit_ir().
    7. 100% deterministic decomposition.
    """
    target_circuit_id = circuit_id or f"{circuit.circuit_id}_decomposed"

    # Copy data registers
    registers: List[QubitRegister] = []
    ancilla_reg: Optional[QubitRegister] = None

    for r in circuit.registers:
        if r.register_type == RegisterType.ANCILLA:
            ancilla_reg = r
        else:
            registers.append(r)

    # Ensure a workspace ancilla register with sufficient capacity exists
    needed_capacity = max(16, circuit.total_width * 2)
    if ancilla_reg is None:
        ancilla_reg = QubitRegister("reg_ancilla", RegisterType.ANCILLA, needed_capacity)
    elif ancilla_reg.width < needed_capacity:
        ancilla_reg = QubitRegister(ancilla_reg.register_id, RegisterType.ANCILLA, needed_capacity)

    registers.append(ancilla_reg)
    ancilla_mgr = AncillaManager(ancilla_register=ancilla_reg)

    # Re-register pre-existing ancillas if any
    for anc in circuit.ancilla_declarations:
        if anc.qubit_ref not in ancilla_mgr.active_ancillas:
            ancilla_mgr.active_ancillas.append(anc.qubit_ref)
            ancilla_mgr.allocated_count = max(ancilla_mgr.allocated_count, anc.qubit_ref.index + 1)

    decomposed_gates: List[GateOperation] = []
    gate_idx = 0

    allowed_types = {LogicalGateType.X, LogicalGateType.CNOT, LogicalGateType.TOFFOLI}

    for gate in circuit.gates:
        if gate.gate_type not in allowed_types:
            raise ValueError(f"Decomposition rejected: Unsupported or non-primitive gate type '{gate.gate_type}'.")

        n_ctrl = len(gate.control_qubits)

        if n_ctrl == 0:
            # X gate
            decomposed_gates.append(
                GateOperation(
                    gate_type=LogicalGateType.X,
                    target_qubit=gate.target_qubit,
                    operation_index=gate_idx,
                )
            )
            gate_idx += 1
        elif n_ctrl == 1:
            # CNOT gate
            decomposed_gates.append(
                GateOperation(
                    gate_type=LogicalGateType.CNOT,
                    control_qubits=gate.control_qubits,
                    target_qubit=gate.target_qubit,
                    operation_index=gate_idx,
                )
            )
            gate_idx += 1
        elif n_ctrl == 2:
            # Standard Toffoli gate
            decomposed_gates.append(
                GateOperation(
                    gate_type=LogicalGateType.TOFFOLI,
                    control_qubits=gate.control_qubits,
                    target_qubit=gate.target_qubit,
                    operation_index=gate_idx,
                )
            )
            gate_idx += 1
        else:
            # k > 2: Multi-controlled decomposition via Toffoli AND-tree + Bennett Uncomputation
            ctrl_vals = ["1"] * n_ctrl  # Standard multi-controlled NOT
            syn_gates, gate_idx = synthesize_multi_controlled_not(
                controls=list(gate.control_qubits),
                control_values=ctrl_vals,
                target=gate.target_qubit,
                ancilla_mgr=ancilla_mgr,
                current_gate_index=gate_idx,
            )
            decomposed_gates.extend(syn_gates)

    # Build Stage 4 Provenance
    upstream_prov = circuit.provenance
    provenance = CircuitProvenance(
        source_rutm_program_hash=upstream_prov.source_rutm_program_hash if upstream_prov else "unknown",
        source_qtm_machine_id=upstream_prov.source_qtm_machine_id if upstream_prov else "unknown",
        compiler_version="0.4.0-alpha",
        circuit_schema_version=SCHEMA_VERSION,
        synthesis_method="STAGE_4_GATE_DECOMPOSITION",
    )

    out_circuit = QuantumCircuitIR(
        circuit_id=target_circuit_id,
        registers=registers,
        gates=decomposed_gates,
        ancilla_declarations=ancilla_mgr.build_ancilla_declarations(),
        input_register_ids=circuit.input_register_ids,
        output_register_ids=circuit.output_register_ids,
        provenance=provenance,
        schema_version=SCHEMA_VERSION,
    )

    # Validate decomposed circuit IR
    val_res = validate_circuit_ir(out_circuit)
    if not val_res.valid:
        raise ValueError(f"Decomposed QuantumCircuitIR failed validation: {val_res.errors}")

    return out_circuit
