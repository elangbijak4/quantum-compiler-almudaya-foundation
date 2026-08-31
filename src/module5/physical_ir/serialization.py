"""
Module 5 Stage 1 — Deterministic PhysicalCircuitIR Serializer & Deserializer.

Implements byte-for-byte canonical JSON serialization and round-trip deserialization for PhysicalCircuitIR.
"""

from typing import Dict, Any, List, Tuple, Optional
import json
from src.module4.circuit_ir.model import QubitRef
from src.module5.physical_ir.model import (
    PhysicalCircuitIR,
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    ExecutionProvenance,
    SCHEMA_VERSION,
)
from src.module5.physical_ir.validator import validate_physical_circuit_ir


def serialize_physical_circuit_ir(circuit: PhysicalCircuitIR) -> str:
    """
    Serializes a PhysicalCircuitIR to a canonical, deterministic JSON string.
    
    Guarantees:
    1. Deterministic key ordering.
    2. Physical qubits sorted by node_id.
    3. Gates sorted by operation_index.
    4. Mapping sorted by logical QubitRef string key representation.
    5. Topology nodes sorted, edges normalized and sorted.
    6. Exact schema version preservation.
    """
    # Sorted physical qubits
    sorted_qubits = sorted(circuit.physical_qubits, key=lambda q: q.node_id)
    qubits_json = [
        {"node_id": q.node_id, "device_id": q.device_id}
        for q in sorted_qubits
    ]

    # Sorted gates
    sorted_gates = sorted(circuit.gates, key=lambda g: g.operation_index)
    gates_json = [
        {
            "gate_type": g.gate_type,
            "control_nodes": list(g.control_nodes),
            "target_node": g.target_node,
            "operation_index": g.operation_index,
        }
        for g in sorted_gates
    ]

    # Sorted mapping
    sorted_mapping_items = sorted(
        circuit.mapping.mapping.items(),
        key=lambda item: (item[0].register_id, item[0].index),
    )
    mapping_json = {
        f"{q_ref.register_id}[{q_ref.index}]": p_node
        for q_ref, p_node in sorted_mapping_items
    }

    # Sorted topology
    sorted_topo_nodes = sorted(circuit.topology.nodes)
    sorted_topo_edges = sorted(
        [[min(u, v), max(u, v)] for u, v in circuit.topology.edges]
    )
    topology_json = {
        "nodes": sorted_topo_nodes,
        "edges": sorted_topo_edges,
    }

    # Provenance json
    if circuit.provenance:
        prov_json = {
            "source_rutm_program_hash": circuit.provenance.source_rutm_program_hash,
            "source_qtm_machine_id": circuit.provenance.source_qtm_machine_id,
            "logical_circuit_id": circuit.provenance.logical_circuit_id,
            "physical_circuit_id": circuit.provenance.physical_circuit_id or circuit.physical_circuit_id,
            "backend_id": circuit.provenance.backend_id,
            "compiler_version": circuit.provenance.compiler_version,
        }
    else:
        prov_json = None

    # Canonical top-level dict ordering
    data: Dict[str, Any] = {
        "physical_circuit_id": circuit.physical_circuit_id,
        "source_logical_circuit_id": circuit.source_logical_circuit_id,
        "physical_qubits": qubits_json,
        "gates": gates_json,
        "mapping": mapping_json,
        "topology": topology_json,
        "schema_version": circuit.schema_version,
        "provenance": prov_json,
    }

    return json.dumps(data, indent=2)


def deserialize_physical_circuit_ir(json_str: str) -> PhysicalCircuitIR:
    """
    Deserializes a canonical JSON string into a validated PhysicalCircuitIR.
    Rejects malformed JSON, schema version mismatches, or invalid structures.
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

    p_circuit_id = data.get("physical_circuit_id", "")
    s_logical_id = data.get("source_logical_circuit_id", "")

    # Reconstruct physical qubits
    p_qubits: List[PhysicalQubit] = []
    for qd in data.get("physical_qubits", []):
        p_qubits.append(PhysicalQubit(node_id=qd["node_id"], device_id=qd.get("device_id", "reference_device")))

    # Reconstruct gates
    gates: List[PhysicalGateOperation] = []
    for gd in data.get("gates", []):
        gates.append(
            PhysicalGateOperation(
                gate_type=gd["gate_type"],
                target_node=gd["target_node"],
                control_nodes=tuple(gd.get("control_nodes", [])),
                operation_index=gd["operation_index"],
            )
        )

    # Reconstruct mapping
    mapping = QubitMapping()
    for key_str, p_node in data.get("mapping", {}).items():
        # Key format "register_id[index]"
        try:
            reg_id, idx_part = key_str.split("[")
            idx = int(idx_part.rstrip("]"))
            q_ref = QubitRef(register_id=reg_id, index=idx)
            mapping.set_mapping(q_ref, p_node)
        except Exception as e:
            raise ValueError(f"Deserialization failed: Invalid QubitRef mapping key format '{key_str}'. Error: {e}")

    # Reconstruct topology
    topology = DeviceTopology()
    topo_data = data.get("topology", {})
    for n in topo_data.get("nodes", []):
        topology.add_node(n)
    for edge in topo_data.get("edges", []):
        topology.add_edge(edge[0], edge[1])

    # Reconstruct provenance
    prov_data = data.get("provenance")
    if prov_data:
        prov = ExecutionProvenance(
            source_rutm_program_hash=prov_data["source_rutm_program_hash"],
            source_qtm_machine_id=prov_data["source_qtm_machine_id"],
            logical_circuit_id=prov_data["logical_circuit_id"],
            physical_circuit_id=prov_data.get("physical_circuit_id"),
            backend_id=prov_data.get("backend_id", "reference_simulator"),
            compiler_version=prov_data.get("compiler_version", "0.5.0-alpha"),
        )
    else:
        prov = None

    circuit = PhysicalCircuitIR(
        physical_circuit_id=p_circuit_id,
        source_logical_circuit_id=s_logical_id,
        physical_qubits=p_qubits,
        gates=gates,
        mapping=mapping,
        topology=topology,
        provenance=prov,
        schema_version=schema_ver,
    )

    # Validate deserialized circuit
    val_res = validate_physical_circuit_ir(circuit)
    if not val_res.valid:
        raise ValueError(f"Deserialized PhysicalCircuitIR failed validation: {val_res.errors}")

    return circuit
