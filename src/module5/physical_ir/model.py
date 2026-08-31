"""
Module 5 Stage 1 — Physical Circuit Intermediate Representation (PhysicalCircuitIR) Data Models.

Defines PhysicalCircuitIR, PhysicalQubit, QubitMapping, DeviceTopology, PhysicalGateOperation,
and ExecutionProvenance AST nodes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from src.module4.circuit_ir.model import QubitRef, SCHEMA_VERSION as LOGICAL_SCHEMA_VERSION

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class PhysicalQubit:
    """Representation of a physical hardware qubit execution node."""
    node_id: int
    device_id: str = "reference_device"

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, int) or self.node_id < 0:
            raise ValueError(f"Invalid physical qubit node_id: {self.node_id}. Must be a non-negative integer.")


@dataclass
class QubitMapping:
    """
    Injective mapping M_t: Q_L -> Q_P from logical QubitRef to physical node_id.
    Supports dynamic mapping evolution permutations under SWAP routing operations.
    """
    mapping: Dict[QubitRef, int] = field(default_factory=dict)
    inverse_mapping: Dict[int, QubitRef] = field(default_factory=dict)

    def set_mapping(self, logical_ref: QubitRef, physical_node: int) -> None:
        """Sets or updates mapping for a logical qubit."""
        if physical_node in self.inverse_mapping and self.inverse_mapping[physical_node] != logical_ref:
            raise ValueError(f"Mapping collision: Physical node {physical_node} already allocated to {self.inverse_mapping[physical_node]}.")
        self.mapping[logical_ref] = physical_node
        self.inverse_mapping[physical_node] = logical_ref

    def get_physical(self, logical_ref: QubitRef) -> int:
        if logical_ref not in self.mapping:
            raise KeyError(f"Unmapped logical qubit: {logical_ref}")
        return self.mapping[logical_ref]

    def apply_swap(self, node_a: int, node_b: int) -> None:
        """
        Updates mapping under physical SWAP(node_a, node_b).
        Logical qubits mapped to node_a and node_b exchange physical locations.
        """
        ref_a = self.inverse_mapping.get(node_a)
        ref_b = self.inverse_mapping.get(node_b)

        if ref_a is not None:
            self.mapping[ref_a] = node_b
            self.inverse_mapping[node_b] = ref_a
        else:
            self.inverse_mapping.pop(node_b, None)

        if ref_b is not None:
            self.mapping[ref_b] = node_a
            self.inverse_mapping[node_a] = ref_b
        else:
            self.inverse_mapping.pop(node_a, None)

    def is_injective(self) -> bool:
        return len(self.mapping) == len(set(self.mapping.values()))


@dataclass
class DeviceTopology:
    """
    Abstract graph representation G_P = (V_P, E_P) of physical qubit coupling connectivity.
    """
    nodes: Set[int] = field(default_factory=set)
    edges: Set[Tuple[int, int]] = field(default_factory=set)

    def add_node(self, node_id: int) -> None:
        if node_id < 0:
            raise ValueError(f"Invalid topology node_id: {node_id}")
        self.nodes.add(node_id)

    def add_edge(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError(f"Self-loops forbidden in DeviceTopology: ({u}, {v}).")
        self.add_node(u)
        self.add_node(v)
        self.edges.add((min(u, v), max(u, v)))

    def is_connected(self, u: int, v: int) -> bool:
        if u == v:
            return True
        edge = (min(u, v), max(u, v))
        return edge in self.edges


@dataclass
class PhysicalGateOperation:
    """Operation acting on physical qubit node IDs."""
    gate_type: str
    target_node: int
    control_nodes: Tuple[int, ...] = ()
    operation_index: int = 0


@dataclass
class ExecutionProvenance:
    """Complete metadata chain tracking execution back to source RUTM & QTM-IR."""
    source_rutm_program_hash: str
    source_qtm_machine_id: str
    logical_circuit_id: str
    physical_circuit_id: Optional[str] = None
    backend_id: str = "reference_simulator"
    compiler_version: str = "0.5.0-alpha"


@dataclass
class PhysicalCircuitIR:
    """
    Physicalized Circuit Intermediate Representation (PhysicalCircuitIR).
    AST for physicalized circuits operating on physical node IDs and native/primitive gates.
    """
    physical_circuit_id: str
    source_logical_circuit_id: str
    physical_qubits: List[PhysicalQubit]
    gates: List[PhysicalGateOperation]
    mapping: QubitMapping
    topology: DeviceTopology
    provenance: Optional[ExecutionProvenance] = None
    schema_version: str = SCHEMA_VERSION
