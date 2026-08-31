"""
Module 4 Stage 2 — Quantum Circuit Intermediate Representation (QuantumCircuitIR) Data Model.

Defines backend-independent data structures for logical quantum circuits, registers, qubits, gate operations, ancillas, and provenance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set, Any

SCHEMA_VERSION: str = "1.0.0"


class RegisterType(str, Enum):
    """Semantic classification of logical qubit registers."""
    STATE = "STATE"
    TAPE = "TAPE"
    HEAD = "HEAD"
    HISTORY = "HISTORY"
    STEP = "STEP"
    STATUS = "STATUS"
    ANCILLA = "ANCILLA"


class AncillaStatus(str, Enum):
    """Initialization and termination status of workspace ancilla qubits."""
    CLEAN = "CLEAN"  # |0> state
    DIRTY = "DIRTY"  # Uncomputed / arbitrary state


class LogicalGateType(str, Enum):
    """Canonical logical primitive reversible gate types."""
    X = "X"
    CNOT = "CNOT"
    TOFFOLI = "TOFFOLI"


@dataclass(frozen=True)
class QubitRef:
    """Canonical reference to a specific qubit within a named register."""
    register_id: str
    index: int

    def to_string(self) -> str:
        return f"{self.register_id}[{self.index}]"


@dataclass(frozen=True)
class QubitRegister:
    """Named, typed, and ordered sequence of logical qubits."""
    register_id: str
    register_type: RegisterType
    width: int

    def get_qubit_ref(self, idx: int) -> QubitRef:
        if idx < 0 or idx >= self.width:
            raise IndexError(f"Index {idx} out of range for register '{self.register_id}' of width {self.width}")
        return QubitRef(register_id=self.register_id, index=idx)


@dataclass(frozen=True)
class GateOperation:
    """
    Representation of a single logical primitive gate operation.
    
    Fields:
    - gate_type: X, CNOT, or TOFFOLI
    - target_qubit: Target QubitRef
    - control_qubits: Tuple of control QubitRefs
    - operation_index: Sequential 0-based operation index
    """
    gate_type: LogicalGateType
    target_qubit: QubitRef
    control_qubits: Tuple[QubitRef, ...] = field(default_factory=tuple)
    operation_index: int = 0

    @property
    def arity(self) -> int:
        return 1 + len(self.control_qubits)

    @property
    def all_qubit_refs(self) -> List[QubitRef]:
        return list(self.control_qubits) + [self.target_qubit]


@dataclass(frozen=True)
class AncillaDeclaration:
    """Declaration of a workspace ancilla qubit and its expected clean state."""
    qubit_ref: QubitRef
    initial_status: AncillaStatus = AncillaStatus.CLEAN
    expected_final_status: AncillaStatus = AncillaStatus.CLEAN


@dataclass(frozen=True)
class CircuitProvenance:
    """Compiler provenance tracking from RUTM -> RUTM-IR -> QTM-IR -> Circuit-IR."""
    source_rutm_program_hash: str
    source_qtm_machine_id: str
    compiler_version: str = "0.4.0-alpha"
    circuit_schema_version: str = SCHEMA_VERSION
    synthesis_method: str = "STAGE_2_LOGICAL_REVERSIBLE_SYNTHESIS"


@dataclass
class QuantumCircuitIR:
    """
    Master Backend-Independent Quantum Circuit Intermediate Representation (QuantumCircuitIR).
    
    Sequential composition semantics:
    U_C = U_{G_m} ... U_{G_1} U_{G_0}
    """
    circuit_id: str
    registers: List[QubitRegister]
    gates: List[GateOperation] = field(default_factory=list)
    ancilla_declarations: List[AncillaDeclaration] = field(default_factory=list)
    input_register_ids: List[str] = field(default_factory=list)
    output_register_ids: List[str] = field(default_factory=list)
    provenance: Optional[CircuitProvenance] = None
    schema_version: str = SCHEMA_VERSION

    @property
    def total_width(self) -> int:
        return sum(r.width for r in self.registers)

    @property
    def total_gate_count(self) -> int:
        return len(self.gates)

    def get_register(self, register_id: str) -> Optional[QubitRegister]:
        for r in self.registers:
            if r.register_id == register_id:
                return r
        return None
