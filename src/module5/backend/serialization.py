"""
Module 5 Stage 2 — Deterministic BackendCapabilityModel Serializer & Deserializer.

Implements byte-for-byte canonical JSON serialization and round-trip deserialization for BackendCapabilityModel.
"""

from typing import Dict, Any, List
import json
from src.module5.backend.model import (
    BackendType,
    BackendIdentity,
    QubitCapacity,
    BackendTopologyCapability,
    GateCapability,
    GateConstraint,
    MeasurementCapability,
    ExecutionCapability,
    NumericalCapability,
    BackendCapabilityProvenance,
    BackendCapabilityModel,
    BACKEND_CAPABILITY_SCHEMA_VERSION,
)
from src.module5.backend.validator import validate_backend_capabilities


def serialize_backend_capabilities(model: BackendCapabilityModel) -> str:
    """
    Serializes a BackendCapabilityModel to a canonical, deterministic JSON string.
    
    Guarantees:
    1. Deterministic key ordering.
    2. Sorted topology nodes and edges.
    3. Sorted gate capabilities and constraints keys.
    4. Exact schema version preservation.
    """
    # Identity
    id_json = {
        "backend_id": model.identity.backend_id,
        "backend_name": model.identity.backend_name,
        "backend_version": model.identity.backend_version,
        "backend_type": model.identity.backend_type.value,
    }

    # Capacity
    cap_json = {
        "max_qubits": model.qubit_capacity.max_qubits,
        "active_qubits": sorted(list(model.qubit_capacity.active_qubits)) if model.qubit_capacity.active_qubits else None,
    }

    # Topology
    topo_json = {
        "nodes": sorted(list(model.topology.nodes)),
        "edges": sorted([[min(u, v), max(u, v)] for u, v in model.topology.edges]),
    }

    # Gate capabilities
    sorted_gate_caps = sorted(model.gate_capabilities.items(), key=lambda x: x[0])
    gate_caps_json = {
        k: {
            "gate_type": v.gate_type,
            "arity": v.arity,
            "supported": v.supported,
            "native": v.native,
        }
        for k, v in sorted_gate_caps
    }

    # Gate constraints
    sorted_gate_cons = sorted(model.gate_constraints.items(), key=lambda x: x[0])
    gate_cons_json = {
        k: {
            "gate_type": v.gate_type,
            "requires_connectivity": v.requires_connectivity,
            "max_controls": v.max_controls,
        }
        for k, v in sorted_gate_cons
    }

    # Measurement
    meas_json = {
        "supports_measurement": model.measurement.supports_measurement,
        "supports_shots": model.measurement.supports_shots,
        "supports_counts": model.measurement.supports_counts,
        "supports_mid_circuit_measurement": model.measurement.supports_mid_circuit_measurement,
        "supports_reset": model.measurement.supports_reset,
    }

    # Execution
    exec_json = {
        "supports_statevector": model.execution.supports_statevector,
        "supports_shots": model.execution.supports_shots,
        "supports_sampling": model.execution.supports_sampling,
        "supports_async_execution": model.execution.supports_async_execution,
        "supports_batch_execution": model.execution.supports_batch_execution,
        "supports_deterministic_seed": model.execution.supports_deterministic_seed,
    }

    # Numerical
    num_json = {
        "supports_complex_amplitudes": model.numerical.supports_complex_amplitudes,
        "numerical_precision": model.numerical.numerical_precision,
        "deterministic_mode": model.numerical.deterministic_mode,
        "epsilon": model.numerical.epsilon,
    }

    # Provenance
    if model.provenance:
        prov_json = {
            "backend_id": model.provenance.backend_id,
            "backend_version": model.provenance.backend_version,
            "capability_schema_version": model.provenance.capability_schema_version,
            "source": model.provenance.source,
            "compiler_version": model.provenance.compiler_version,
        }
    else:
        prov_json = None

    data: Dict[str, Any] = {
        "identity": id_json,
        "qubit_capacity": cap_json,
        "topology": topo_json,
        "gate_capabilities": gate_caps_json,
        "gate_constraints": gate_cons_json,
        "measurement": meas_json,
        "execution": exec_json,
        "numerical": num_json,
        "schema_version": model.schema_version,
        "provenance": prov_json,
    }

    return json.dumps(data, indent=2)


def deserialize_backend_capabilities(json_str: str) -> BackendCapabilityModel:
    """
    Deserializes a canonical JSON string into a validated BackendCapabilityModel.
    Rejects malformed JSON, schema version mismatches, or invalid structures.
    """
    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Deserialization failed: Invalid JSON string. Error: {e}")

    if not isinstance(data, dict):
        raise ValueError("Deserialization failed: JSON root must be an object/dict.")

    schema_ver = data.get("schema_version")
    if schema_ver != BACKEND_CAPABILITY_SCHEMA_VERSION:
        raise ValueError(f"Deserialization failed: Schema version mismatch. Expected '{BACKEND_CAPABILITY_SCHEMA_VERSION}', got '{schema_ver}'.")

    id_data = data["identity"]
    identity = BackendIdentity(
        backend_id=id_data["backend_id"],
        backend_name=id_data["backend_name"],
        backend_version=id_data["backend_version"],
        backend_type=BackendType(id_data.get("backend_type", BackendType.REFERENCE_SIMULATOR.value)),
    )

    cap_data = data["qubit_capacity"]
    active_qs = set(cap_data["active_qubits"]) if cap_data.get("active_qubits") is not None else None
    qubit_capacity = QubitCapacity(max_qubits=cap_data["max_qubits"], active_qubits=active_qs)

    topo_data = data["topology"]
    topology = BackendTopologyCapability()
    for n in topo_data.get("nodes", []):
        topology.add_node(n)
    for edge in topo_data.get("edges", []):
        topology.add_edge(edge[0], edge[1])

    gate_caps: Dict[str, GateCapability] = {}
    for k, v in data.get("gate_capabilities", {}).items():
        gate_caps[k] = GateCapability(
            gate_type=v["gate_type"],
            arity=v["arity"],
            supported=v.get("supported", True),
            native=v.get("native", True),
        )

    gate_cons: Dict[str, GateConstraint] = {}
    for k, v in data.get("gate_constraints", {}).items():
        gate_cons[k] = GateConstraint(
            gate_type=v["gate_type"],
            requires_connectivity=v.get("requires_connectivity", True),
            max_controls=v.get("max_controls"),
        )

    m_data = data.get("measurement", {})
    measurement = MeasurementCapability(
        supports_measurement=m_data.get("supports_measurement", True),
        supports_shots=m_data.get("supports_shots", True),
        supports_counts=m_data.get("supports_counts", True),
        supports_mid_circuit_measurement=m_data.get("supports_mid_circuit_measurement", False),
        supports_reset=m_data.get("supports_reset", False),
    )

    e_data = data.get("execution", {})
    execution = ExecutionCapability(
        supports_statevector=e_data.get("supports_statevector", True),
        supports_shots=e_data.get("supports_shots", True),
        supports_sampling=e_data.get("supports_sampling", True),
        supports_async_execution=e_data.get("supports_async_execution", False),
        supports_batch_execution=e_data.get("supports_batch_execution", False),
        supports_deterministic_seed=e_data.get("supports_deterministic_seed", True),
    )

    n_data = data.get("numerical", {})
    numerical = NumericalCapability(
        supports_complex_amplitudes=n_data.get("supports_complex_amplitudes", True),
        numerical_precision=n_data.get("numerical_precision", "float64"),
        deterministic_mode=n_data.get("deterministic_mode", True),
        epsilon=n_data.get("epsilon", 1e-12),
    )

    p_data = data.get("provenance")
    if p_data:
        provenance = BackendCapabilityProvenance(
            backend_id=p_data["backend_id"],
            backend_version=p_data["backend_version"],
            capability_schema_version=p_data.get("capability_schema_version", BACKEND_CAPABILITY_SCHEMA_VERSION),
            source=p_data.get("source", "system"),
            compiler_version=p_data.get("compiler_version", "0.5.0-alpha"),
        )
    else:
        provenance = None

    model = BackendCapabilityModel(
        identity=identity,
        qubit_capacity=qubit_capacity,
        topology=topology,
        gate_capabilities=gate_caps,
        gate_constraints=gate_cons,
        measurement=measurement,
        execution=execution,
        numerical=numerical,
        provenance=provenance,
        schema_version=schema_ver,
    )

    val_res = validate_backend_capabilities(model)
    if not val_res.valid:
        raise ValueError(f"Deserialized BackendCapabilityModel failed validation: {val_res.errors}")

    return model
