"""
Module 5 Stage 4 — Native Circuit Data Models & Resolution Contracts.

Defines NativeGateDefinition, NativeOperation, NativeCircuitIR, NativeResolutionStatus,
NativeGateResolutionResult, and NativeTranslationResult.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Optional, Any
from src.module5.physical_ir.model import QubitMapping, PhysicalGateOperation, ExecutionProvenance

SCHEMA_VERSION: str = "1.0.0"


class NativeResolutionStatus(str, Enum):
    """Status classification of physical-to-native gate resolution."""
    DIRECT_NATIVE = "DIRECT_NATIVE"
    DECOMPOSED = "DECOMPOSED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class NativeGateDefinition:
    """Canonical definition of a hardware backend native gate."""
    gate_id: str
    gate_name: str
    arity: int
    parameter_count: int = 0
    native_status: bool = True

    def __post_init__(self) -> None:
        if not self.gate_id or not self.gate_id.strip():
            raise ValueError("Native gate_id cannot be empty.")
        if self.arity < 1:
            raise ValueError(f"Invalid native gate arity: {self.arity}. Must be >= 1.")


@dataclass
class NativeOperation:
    """Representation of an executed native hardware gate operation."""
    native_gate: str
    operands: Tuple[int, ...]
    parameters: Tuple[float, ...] = ()
    operation_index: int = 0


@dataclass
class NativeGateResolutionResult:
    """Resolution outcome for translating a physical gate into native operations."""
    status: NativeResolutionStatus
    source_gate: PhysicalGateOperation
    native_operations: List[NativeOperation] = field(default_factory=list)
    decomposition_id: Optional[str] = None
    diagnostics: List[str] = field(default_factory=list)


@dataclass
class NativeCircuitIR:
    """
    Backend-Native Circuit Intermediate Representation (NativeCircuitIR).
    Represents a translated circuit consisting exclusively of backend-native gates.
    """
    circuit_id: str
    backend_id: str
    backend_version: str
    qubits: List[int]
    native_operations: List[NativeOperation]
    input_mapping: QubitMapping
    output_mapping: QubitMapping
    provenance: ExecutionProvenance
    schema_version: str = SCHEMA_VERSION


@dataclass
class NativeTranslationResult:
    """Master translation result payload for PhysicalCircuitIR -> NativeCircuitIR."""
    success: bool
    source_circuit_id: str
    native_circuit_id: str
    backend_id: str
    native_circuit: Optional[NativeCircuitIR] = None
    translated_operations_count: int = 0
    unresolved_operations: List[PhysicalGateOperation] = field(default_factory=list)
    decomposition_records: List[str] = field(default_factory=list)
    semantic_verification: bool = False
    provenance: Optional[ExecutionProvenance] = None
    diagnostics: List[str] = field(default_factory=list)
