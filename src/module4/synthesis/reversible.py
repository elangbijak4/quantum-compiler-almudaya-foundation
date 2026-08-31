"""
Module 4 Stage 3 — Logical Reversible Synthesis Engine.

Synthesizes QuantumCircuitIR from QTM-IR transition tables using frozen primitive gates (X, CNOT, TOFFOLI).
"""

from typing import Dict, List, Set, Tuple, Optional
from src.module1.utm.model import UTMProgram
from src.module3.qtm_ir.model import QTMIRModel
from src.module4.foundation.domain import FiniteDomainContract
from src.module4.foundation.encoding import RegisterEncodingSpec, encode_configuration
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    QubitRef,
    GateOperation,
    AncillaDeclaration,
    CircuitProvenance,
    RegisterType,
    LogicalGateType,
    SCHEMA_VERSION,
)
from src.module4.circuit_ir.validator import validate_circuit_ir
from src.module4.synthesis.transition import build_transition_table, TransitionTable
from src.module4.synthesis.ancilla import AncillaManager, synthesize_multi_controlled_not


def synthesize_qtm_transition(
    program: UTMProgram,
    qtm_ir: QTMIRModel,
    domain_contract: FiniteDomainContract,
    encoding_spec: RegisterEncodingSpec,
    state_map: Dict[str, int],
    symbol_map: Dict[str, int],
    circuit_id: str = "qtm_transition_circuit",
) -> QuantumCircuitIR:
    """
    Primary Stage 3 API: Synthesizes a backend-independent QuantumCircuitIR realizing U_C |E(C)> = |E(R_P(C))>.
    
    Guarantees:
    1. Uses ONLY frozen primitive gates (X, CNOT, TOFFOLI).
    2. Sequential 0-based operation ordering.
    3. Clean Bennett uncomputation for all workspace ancillas.
    4. Passes validate_circuit_ir().
    5. 100% deterministic synthesis.
    """
    # 1. Construct & validate transition table T: E(C) -> E(R_P(C))
    table = build_transition_table(program, domain_contract, encoding_spec, state_map, symbol_map)

    # 2. Construct QubitRegisters matching encoding_spec
    reg_state = QubitRegister("reg_state", RegisterType.STATE, encoding_spec.n_state)
    reg_tape = QubitRegister("reg_tape", RegisterType.TAPE, encoding_spec.n_tape_total_bits)
    reg_head = QubitRegister("reg_head", RegisterType.HEAD, encoding_spec.n_head_pos)
    reg_hist = QubitRegister("reg_hist", RegisterType.HISTORY, encoding_spec.n_history) if encoding_spec.n_history > 0 else None
    reg_step = QubitRegister("reg_step", RegisterType.STEP, encoding_spec.n_step)
    reg_halt = QubitRegister("reg_halt", RegisterType.STATUS, encoding_spec.n_halted)
    reg_err = QubitRegister("reg_err", RegisterType.STATUS, encoding_spec.n_error)

    registers: List[QubitRegister] = [reg_state, reg_tape, reg_head]
    if reg_hist:
        registers.append(reg_hist)
    registers.extend([reg_step, reg_halt, reg_err])

    # Workspace Ancilla Register (capacity for multi-controlled AND-tree)
    ancilla_capacity = max(16, encoding_spec.total_qubits * 2)
    reg_anc = QubitRegister("reg_ancilla", RegisterType.ANCILLA, ancilla_capacity)
    registers.append(reg_anc)

    ancilla_mgr = AncillaManager(ancilla_register=reg_anc)

    # Map global bit index -> QubitRef
    all_qubit_refs: List[QubitRef] = []
    for r in registers:
        if r.register_type != RegisterType.ANCILLA:
            for idx in range(r.width):
                all_qubit_refs.append(r.get_qubit_ref(idx))

    total_data_bits = len(all_qubit_refs)

    gates: List[GateOperation] = []
    gate_idx = 0

    # 3. Deterministic Minterm Reversible Synthesis over Transition Table T
    # For each pair (x_bits, y_bits) in T:
    for pair in table.pairs:
        x_bits = pair.source_bits
        y_bits = pair.target_bits

        if len(x_bits) != total_data_bits or len(y_bits) != total_data_bits:
            raise ValueError(f"Bitstring length mismatch: expected {total_data_bits}, got x={len(x_bits)}, y={len(y_bits)}.")

        # Find target bits that need to be transformed
        controls = list(all_qubit_refs)
        ctrl_vals = list(x_bits)

        for bit_i in range(total_data_bits):
            if x_bits[bit_i] != y_bits[bit_i]:
                target_q = all_qubit_refs[bit_i]
                # Filter out target qubit from controls
                sub_ctrls = [c for idx_c, c in enumerate(controls) if idx_c != bit_i]
                sub_vals = [v for idx_c, v in enumerate(ctrl_vals) if idx_c != bit_i]

                syn_gates, gate_idx = synthesize_multi_controlled_not(
                    controls=sub_ctrls,
                    control_values=sub_vals,
                    target=target_q,
                    ancilla_mgr=ancilla_mgr,
                    current_gate_index=gate_idx,
                )
                gates.extend(syn_gates)

    # 4. Build Provenance metadata
    provenance = CircuitProvenance(
        source_rutm_program_hash=qtm_ir.provenance.source_rutm_program_hash if qtm_ir.provenance else "unknown_hash",
        source_qtm_machine_id=qtm_ir.machine_id,
        compiler_version="0.4.0-alpha",
        circuit_schema_version=SCHEMA_VERSION,
        synthesis_method="STAGE_3_LOGICAL_REVERSIBLE_SYNTHESIS",
    )

    # 5. Build QuantumCircuitIR
    circuit = QuantumCircuitIR(
        circuit_id=circuit_id,
        registers=registers,
        gates=gates,
        ancilla_declarations=ancilla_mgr.build_ancilla_declarations(),
        input_register_ids=[r.register_id for r in registers if r.register_type != RegisterType.ANCILLA],
        output_register_ids=[r.register_id for r in registers if r.register_type != RegisterType.ANCILLA],
        provenance=provenance,
        schema_version=SCHEMA_VERSION,
    )

    # 6. Validate generated circuit IR
    val_res = validate_circuit_ir(circuit)
    if not val_res.valid:
        raise ValueError(f"Synthesized QuantumCircuitIR failed validation: {val_res.errors}")

    return circuit
