"""
Module 5 Stage 2 — Backend Capability Data Models & Abstract Specifications.

Defines BackendType, BackendIdentity, QubitCapacity, BackendTopologyCapability,
GateCapability, GateConstraint, MeasurementCapability, ExecutionCapability,
NumericalCapability, BackendCapabilityProvenance, and BackendCapabilityModel.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any

BACKEND_CAPABILITY_SCHEMA_VERSION = "1.0.0"


class BackendType(str, Enum):
    """Canonical classification of backend execution targets."""
    REFERENCE_SIMULATOR = "REFERENCE_SIMULATOR"
    STATEVECTOR_SIMULATOR = "STATEVECTOR_SIMULATOR"
    SHOT_SIMULATOR = "SHOT_SIMULATOR"
    QUANTUM_HARDWARE = "QUANTUM_HARDWARE"
    CUSTOM = "CUSTOM"


@dataclass(frozen=True)
class BackendIdentity:
    """Identity and metadata for a backend."""
    backend_id: str
    backend_name: str
    backend_version: str
    backend_type: BackendType = BackendType.REFERENCE_SIMULATOR


@dataclass
class QubitCapacity:
    """Qubit capacity bounds and active physical node set."""
    max_qubits: int
    active_qubits: Optional[Set[int]] = None

    def __post_init__(self) -> None:
        if self.max_qubits <= 0:
            raise ValueError(f"Invalid max_qubits: {self.max_qubits}. Must be a positive integer.")
        if self.active_qubits is not None and len(self.active_qubits) > self.max_qubits:
            raise ValueError(f"Active qubits count ({len(self.active_qubits)}) exceeds max_qubits ({self.max_qubits}).")


@dataclass
class BackendTopologyCapability:
    """Graph model G_B = (V_B, E_B) of backend physical coupling connectivity."""
    nodes: Set[int] = field(default_factory=set)
    edges: Set[Tuple[int, int]] = field(default_factory=set)

    def add_node(self, node_id: int) -> None:
        if node_id < 0:
            raise ValueError(f"Invalid node_id: {node_id}. Must be a non-negative integer.")
        self.nodes.add(node_id)

    def add_edge(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError(f"Self-loops forbidden in BackendTopologyCapability: ({u}, {v}).")
        self.add_node(u)
        self.add_node(v)
        self.edges.add((min(u, v), max(u, v)))

    def supports_qubit(self, node_id: int) -> bool:
        return node_id in self.nodes

    def supports_connection(self, u: int, v: int) -> bool:
        if u not in self.nodes or v not in self.nodes:
            return False
        if u == v:
            return True
        edge = (min(u, v), max(u, v))
        return edge in self.edges


@dataclass
class GateCapability:
    """Representation of a supported physical gate type."""
    gate_type: str
    arity: int
    supported: bool = True
    native: bool = True

    def __post_init__(self) -> None:
        if not self.gate_type or not self.gate_type.strip():
            raise ValueError("Gate type cannot be empty.")
        if self.arity < 1:
            raise ValueError(f"Invalid gate arity: {self.arity}. Must be at least 1.")


@dataclass
class GateConstraint:
    """Declarative restrictions on supported operations."""
    gate_type: str
    requires_connectivity: bool = True
    max_controls: Optional[int] = None


@dataclass
class MeasurementCapability:
    """Backend measurement operational support."""
    supports_measurement: bool = True
    supports_shots: bool = True
    supports_counts: bool = True
    supports_mid_circuit_measurement: bool = False
    supports_reset: bool = False


@dataclass
class ExecutionCapability:
    """Backend execution mode support."""
    supports_statevector: bool = True
    supports_shots: bool = True
    supports_sampling: bool = True
    supports_async_execution: bool = False
    supports_batch_execution: bool = False
    supports_deterministic_seed: bool = True


@dataclass
class NumericalCapability:
    """Numerical precision and mathematical tolerances."""
    supports_complex_amplitudes: bool = True
    numerical_precision: str = "float64"
    deterministic_mode: bool = True
    epsilon: float = 1e-12


@dataclass
class BackendCapabilityProvenance:
    """Metadata tracking backend capability definition."""
    backend_id: str
    backend_version: str
    capability_schema_version: str = BACKEND_CAPABILITY_SCHEMA_VERSION
    source: str = "system"
    compiler_version: str = "0.5.0-alpha"


@dataclass
class BackendCapabilityModel:
    """Root Backend Capability Model (BackendCapabilityModel)."""
    identity: BackendIdentity
    qubit_capacity: QubitCapacity
    topology: BackendTopologyCapability
    gate_capabilities: Dict[str, GateCapability]
    gate_constraints: Dict[str, GateConstraint] = field(default_factory=dict)
    measurement: MeasurementCapability = field(default_factory=MeasurementCapability)
    execution: ExecutionCapability = field(default_factory=ExecutionCapability)
    numerical: NumericalCapability = field(default_factory=NumericalCapability)
    provenance: Optional[BackendCapabilityProvenance] = None
    schema_version: str = BACKEND_CAPABILITY_SCHEMA_VERSION

    # Pure query methods
    def supports_gate(self, gate_type: str) -> bool:
        g = self.gate_capabilities.get(gate_type.upper())
        return g is not None and g.supported

    def supports_gate_arity(self, gate_type: str, arity: int) -> bool:
        g = self.gate_capabilities.get(gate_type.upper())
        return g is not None and g.supported and g.arity == arity

    def supports_qubit(self, node_id: int) -> bool:
        return self.topology.supports_qubit(node_id) and node_id < self.qubit_capacity.max_qubits

    def supports_connection(self, u: int, v: int) -> bool:
        return self.supports_qubit(u) and self.supports_qubit(v) and self.topology.supports_connection(u, v)

    def supports_measurement(self) -> bool:
        return self.measurement.supports_measurement

    def supports_shots(self) -> bool:
        return self.execution.supports_shots and self.measurement.supports_shots

    def supports_statevector(self) -> bool:
        return self.execution.supports_statevector

    def supports_sampling(self) -> bool:
        return self.execution.supports_sampling

    def supports_gate_on_nodes(self, gate_type: str, nodes: Tuple[int, ...]) -> bool:
        if not self.supports_gate(gate_type):
            return False

        for n in nodes:
            if not self.supports_qubit(n):
                return False

        # If 2-qubit operation, check topology connectivity constraint if connectivity required
        if len(nodes) == 2:
            constraint = self.gate_constraints.get(gate_type.upper())
            if constraint is None or constraint.requires_connectivity:
                if not self.supports_connection(nodes[0], nodes[1]):
                    return False

        return True
