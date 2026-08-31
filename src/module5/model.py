"""
Module 5 Contract Data Models — Physicalization, Measurement & Execution Contracts.

Defines PhysicalCircuitIR, PhysicalQubit, QubitMapping, DeviceTopology, PhysicalGateOperation,
ExecutionRequest, ExecutionResult, and ExecutionProvenance contracts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRef


@dataclass(frozen=True)
class PhysicalQubit:
    """Representation of a physical hardware qubit node."""
    node_id: int
    device_id: str = "reference_device"


@dataclass
class QubitMapping:
    """
    Injective mapping M_t: Q_L -> Q_P from logical QubitRef to physical node_id.
    Tracks mapping evolution dynamic permutations under SWAP routing operations.
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

    def add_edge(self, u: int, v: int) -> None:
        self.nodes.add(u)
        self.nodes.add(v)
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
class PhysicalCircuitIR:
    """
    Physicalized Circuit Intermediate Representation (PhysicalCircuitIR).
    AST for physicalized circuits operating on physical node IDs and native gates.
    """
    physical_circuit_id: str
    source_logical_circuit_id: str
    physical_qubits: List[PhysicalQubit]
    gates: List[PhysicalGateOperation]
    mapping: QubitMapping
    topology: DeviceTopology
    schema_version: str = "1.0.0"


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
class ExecutionRequest:
    """Input payload for circuit execution."""
    request_id: str
    logical_circuit: Optional[QuantumCircuitIR] = None
    physical_circuit: Optional[PhysicalCircuitIR] = None
    shots: int = 1000
    seed: Optional[int] = None
    target_backend_id: str = "reference_simulator"


@dataclass
class ExecutionResult:
    """Output payload from circuit execution."""
    request_id: str
    status: str  # SUCCESS, FAILURE
    state_vector: Optional[Dict[str, complex]] = None
    counts: Optional[Dict[str, int]] = None
    provenance: Optional[ExecutionProvenance] = None
    execution_time_ms: float = 0.0
    diagnostics: List[str] = field(default_factory=list)
