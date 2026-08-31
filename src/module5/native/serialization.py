"""
Module 5 Stage 4 — Deterministic NativeCircuitIR Serializer & Deserializer.

Implements byte-for-byte canonical JSON serialization and round-trip deserialization for NativeCircuitIR.
"""

from typing import Dict, Any, List
import json
from src.module4.circuit_ir.model import QubitRef
from src.module5.physical_ir.model import QubitMapping, ExecutionProvenance
from src.module5.native.model import NativeCircuitIR, NativeOperation, SCHEMA_VERSION
from src.module5.native.validator import validate_native_circuit_ir


def serialize_native_circuit_ir(circuit: NativeCircuitIR) -> str:
    """
    Serializes a NativeCircuitIR to a canonical, deterministic JSON string.
    """
    sorted_qubits = sorted(circuit.qubits)
    sorted_ops = sorted(circuit.native_operations, key=lambda n: n.operation_index)

    ops_json = [
        {
            "native_gate": op.native_gate,
            "operands": list(op.operands),
            "parameters": list(op.parameters),
            "operation_index": op.operation_index,
        }
        for op in sorted_ops
    ]

    # Mapping helper
    def _map_to_dict(m: QubitMapping) -> Dict[str, int]:
        sorted_items = sorted(m.mapping.items(), key=lambda item: (item[0].register_id, item[0].index))
        return {f"{q_ref.register_id}[{q_ref.index}]": p_node for q_ref, p_node in sorted_items}

    prov_json = {
        "source_rutm_program_hash": circuit.provenance.source_rutm_program_hash,
        "source_qtm_machine_id": circuit.provenance.source_qtm_machine_id,
        "logical_circuit_id": circuit.provenance.logical_circuit_id,
        "physical_circuit_id": circuit.provenance.physical_circuit_id,
        "backend_id": circuit.provenance.backend_id,
        "compiler_version": circuit.provenance.compiler_version,
    }

    data: Dict[str, Any] = {
        "circuit_id": circuit.circuit_id,
        "backend_id": circuit.backend_id,
        "backend_version": circuit.backend_version,
        "qubits": sorted_qubits,
        "native_operations": ops_json,
        "input_mapping": _map_to_dict(circuit.input_mapping),
        "output_mapping": _map_to_dict(circuit.output_mapping),
        "schema_version": circuit.schema_version,
        "provenance": prov_json,
    }

    return json.dumps(data, indent=2)


def deserialize_native_circuit_ir(json_str: str) -> NativeCircuitIR:
    """
    Deserializes a canonical JSON string into a validated NativeCircuitIR.
    """
    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Deserialization failed: Invalid JSON string. Error: {e}")

    if not isinstance(data, dict):
        raise ValueError("Deserialization failed: JSON root must be an object/dict.")

    schema_ver = data.get("schema_version")
    if schema_ver != SCHEMA_VERSION:
        raise ValueError(f"Deserialization failed: Schema version mismatch. Expected '{SCHEMA_VERSION}', got '{schema_ver}'.")

    c_id = data["circuit_id"]
    b_id = data["backend_id"]
    b_ver = data["backend_version"]
    qubits = list(data.get("qubits", []))

    native_ops: List[NativeOperation] = []
    for od in data.get("native_operations", []):
        native_ops.append(
            NativeOperation(
                native_gate=od["native_gate"],
                operands=tuple(od["operands"]),
                parameters=tuple(od.get("parameters", [])),
                operation_index=od["operation_index"],
            )
        )

    def _dict_to_map(d: Dict[str, int]) -> QubitMapping:
        m = QubitMapping()
        for k, p_node in d.items():
            reg_id, idx_part = k.split("[")
            idx = int(idx_part.rstrip("]"))
            m.set_mapping(QubitRef(register_id=reg_id, index=idx), p_node)
        return m

    input_map = _dict_to_map(data.get("input_mapping", {}))
    output_map = _dict_to_map(data.get("output_mapping", {}))

    prov_data = data["provenance"]
    provenance = ExecutionProvenance(
        source_rutm_program_hash=prov_data["source_rutm_program_hash"],
        source_qtm_machine_id=prov_data["source_qtm_machine_id"],
        logical_circuit_id=prov_data["logical_circuit_id"],
        physical_circuit_id=prov_data.get("physical_circuit_id"),
        backend_id=prov_data.get("backend_id", b_id),
        compiler_version=prov_data.get("compiler_version", "0.5.0-alpha"),
    )

    circuit = NativeCircuitIR(
        circuit_id=c_id,
        backend_id=b_id,
        backend_version=b_ver,
        qubits=qubits,
        native_operations=native_ops,
        input_mapping=input_map,
        output_mapping=output_map,
        provenance=provenance,
        schema_version=schema_ver,
    )

    val_res = validate_native_circuit_ir(circuit)
    if not val_res.valid:
        raise ValueError(f"Deserialized NativeCircuitIR failed validation: {val_res.errors}")

    return circuit
