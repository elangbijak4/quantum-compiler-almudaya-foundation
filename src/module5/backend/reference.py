"""
Module 5 Stage 2 — Reference Simulator Capability Profile Generator.

Constructs the canonical vendor-neutral BackendCapabilityModel profile for reference_simulator.
"""

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


def create_reference_simulator_capabilities(max_qubits: int = 32) -> BackendCapabilityModel:
    """
    Creates the vendor-neutral reference_simulator BackendCapabilityModel profile.
    This profile describes a fully-connected, 32-qubit state-vector simulator.
    """
    identity = BackendIdentity(
        backend_id="reference_simulator",
        backend_name="Module 5 Reference State-Vector Simulator",
        backend_version="1.0.0",
        backend_type=BackendType.REFERENCE_SIMULATOR,
    )

    capacity = QubitCapacity(max_qubits=max_qubits)

    # Fully connected topology across max_qubits
    topology = BackendTopologyCapability()
    for i in range(max_qubits):
        topology.add_node(i)
    for i in range(max_qubits):
        for j in range(i + 1, max_qubits):
            topology.add_edge(i, j)

    # Supported canonical gates
    gate_caps = {
        "X": GateCapability(gate_type="X", arity=1, supported=True, native=True),
        "Y": GateCapability(gate_type="Y", arity=1, supported=True, native=True),
        "Z": GateCapability(gate_type="Z", arity=1, supported=True, native=True),
        "H": GateCapability(gate_type="H", arity=1, supported=True, native=True),
        "S": GateCapability(gate_type="S", arity=1, supported=True, native=True),
        "T": GateCapability(gate_type="T", arity=1, supported=True, native=True),
        "SX": GateCapability(gate_type="SX", arity=1, supported=True, native=True),
        "CNOT": GateCapability(gate_type="CNOT", arity=2, supported=True, native=True),
        "CZ": GateCapability(gate_type="CZ", arity=2, supported=True, native=True),
        "SWAP": GateCapability(gate_type="SWAP", arity=2, supported=True, native=True),
        "TOFFOLI": GateCapability(gate_type="TOFFOLI", arity=3, supported=True, native=True),
    }

    gate_cons = {
        "CNOT": GateConstraint(gate_type="CNOT", requires_connectivity=True, max_controls=1),
        "CZ": GateConstraint(gate_type="CZ", requires_connectivity=True, max_controls=1),
        "SWAP": GateConstraint(gate_type="SWAP", requires_connectivity=True, max_controls=1),
    }

    measurement = MeasurementCapability(
        supports_measurement=True,
        supports_shots=True,
        supports_counts=True,
        supports_mid_circuit_measurement=False,
        supports_reset=False,
    )

    execution = ExecutionCapability(
        supports_statevector=True,
        supports_shots=True,
        supports_sampling=True,
        supports_async_execution=False,
        supports_batch_execution=False,
        supports_deterministic_seed=True,
    )

    numerical = NumericalCapability(
        supports_complex_amplitudes=True,
        numerical_precision="float64",
        deterministic_mode=True,
        epsilon=1e-12,
    )

    provenance = BackendCapabilityProvenance(
        backend_id="reference_simulator",
        backend_version="1.0.0",
        capability_schema_version=BACKEND_CAPABILITY_SCHEMA_VERSION,
        source="system_reference",
        compiler_version="0.5.0-alpha",
    )

    return BackendCapabilityModel(
        identity=identity,
        qubit_capacity=capacity,
        topology=topology,
        gate_capabilities=gate_caps,
        gate_constraints=gate_cons,
        measurement=measurement,
        execution=execution,
        numerical=numerical,
        provenance=provenance,
        schema_version=BACKEND_CAPABILITY_SCHEMA_VERSION,
    )
