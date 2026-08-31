"""
Module 4 Stage 2 — Deterministic JSON Serialization & Deserialization for QuantumCircuitIR.

Enforces lossless round-trip identity:
deserialize(serialize(C)) == C
"""

import json
from typing import Dict, Any, List
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


def serialize_circuit_ir_to_dict(circuit: QuantumCircuitIR) -> Dict[str, Any]:
    """Converts a QuantumCircuitIR instance to a canonical dictionary representation."""
    registers_data = [
        {
            "register_id": r.register_id,
            "register_type": r.register_type.value,
            "width": r.width,
        }
        for r in circuit.registers
    ]

    gates_data = [
        {
            "operation_index": g.operation_index,
            "gate_type": g.gate_type.value,
            "target_qubit": {"register_id": g.target_qubit.register_id, "index": g.target_qubit.index},
            "control_qubits": [
                {"register_id": cq.register_id, "index": cq.index} for cq in g.control_qubits
            ],
        }
        for g in circuit.gates
    ]

    ancillas_data = [
        {
            "qubit_ref": {"register_id": a.qubit_ref.register_id, "index": a.qubit_ref.index},
            "initial_status": a.initial_status.value,
            "expected_final_status": a.expected_final_status.value,
        }
        for a in circuit.ancilla_declarations
    ]

    provenance_data = None
    if circuit.provenance is not None:
        provenance_data = {
            "source_rutm_program_hash": circuit.provenance.source_rutm_program_hash,
            "source_qtm_machine_id": circuit.provenance.source_qtm_machine_id,
            "compiler_version": circuit.provenance.compiler_version,
            "circuit_schema_version": circuit.provenance.circuit_schema_version,
            "synthesis_method": circuit.provenance.synthesis_method,
        }

    return {
        "schema_version": circuit.schema_version,
        "circuit_id": circuit.circuit_id,
        "registers": registers_data,
        "gates": gates_data,
        "ancilla_declarations": ancillas_data,
        "input_register_ids": circuit.input_register_ids,
        "output_register_ids": circuit.output_register_ids,
        "provenance": provenance_data,
    }


def serialize_circuit_ir_to_json(circuit: QuantumCircuitIR, indent: int = 2) -> str:
    """Serializes a QuantumCircuitIR to a formatted JSON string."""
    data = serialize_circuit_ir_to_dict(circuit)
    return json.dumps(data, indent=indent, sort_keys=True)


def deserialize_circuit_ir_from_dict(data: Dict[str, Any]) -> QuantumCircuitIR:
    """Deserializes a dictionary representation into a QuantumCircuitIR instance."""
    schema_ver = data.get("schema_version", "")
    if schema_ver != SCHEMA_VERSION:
        raise ValueError(f"Deserialization failed: invalid schema_version '{schema_ver}'. Expected '{SCHEMA_VERSION}'.")

    registers = [
        QubitRegister(
            register_id=r["register_id"],
            register_type=RegisterType(r["register_type"]),
            width=r["width"],
        )
        for r in data.get("registers", [])
    ]

    gates = [
        GateOperation(
            gate_type=LogicalGateType(g["gate_type"]),
            target_qubit=QubitRef(register_id=g["target_qubit"]["register_id"], index=g["target_qubit"]["index"]),
            control_qubits=tuple(
                QubitRef(register_id=cq["register_id"], index=cq["index"]) for cq in g.get("control_qubits", [])
            ),
            operation_index=g.get("operation_index", 0),
        )
        for g in data.get("gates", [])
    ]

    ancillas = [
        AncillaDeclaration(
            qubit_ref=QubitRef(register_id=a["qubit_ref"]["register_id"], index=a["qubit_ref"]["index"]),
            initial_status=AncillaStatus(a.get("initial_status", "CLEAN")),
            expected_final_status=AncillaStatus(a.get("expected_final_status", "CLEAN")),
        )
        for a in data.get("ancilla_declarations", [])
    ]

    prov_data = data.get("provenance")
    provenance = None
    if prov_data:
        provenance = CircuitProvenance(
            source_rutm_program_hash=prov_data["source_rutm_program_hash"],
            source_qtm_machine_id=prov_data["source_qtm_machine_id"],
            compiler_version=prov_data.get("compiler_version", "0.4.0-alpha"),
            circuit_schema_version=prov_data.get("circuit_schema_version", SCHEMA_VERSION),
            synthesis_method=prov_data.get("synthesis_method", "STAGE_2_LOGICAL_REVERSIBLE_SYNTHESIS"),
        )

    return QuantumCircuitIR(
        circuit_id=data["circuit_id"],
        registers=registers,
        gates=gates,
        ancilla_declarations=ancillas,
        input_register_ids=data.get("input_register_ids", []),
        output_register_ids=data.get("output_register_ids", []),
        provenance=provenance,
        schema_version=schema_ver,
    )


def deserialize_circuit_ir_from_json(json_str: str) -> QuantumCircuitIR:
    """Deserializes a JSON string into a QuantumCircuitIR instance."""
    data = json.loads(json_str)
    return deserialize_circuit_ir_from_dict(data)
