"""
Module 4 Foundation — Canonical Logical Primitive Gate Set Specification.

Defines Toffoli, CNOT, and Pauli-X as the frozen logical primitive gate set.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


class LogicalPrimitiveGateType(str, Enum):
    """Canonical logical primitive reversible gate types."""
    X = "X"
    CNOT = "CNOT"
    TOFFOLI = "TOFFOLI"


@dataclass(frozen=True)
class LogicalPrimitiveGate:
    """
    Specification of a logical reversible primitive gate operating on target qubits.
    
    Fields:
    - gate_type: X, CNOT, or TOFFOLI
    - control_qubits: List of control qubit indices
    - target_qubit: Target qubit index
    """
    gate_type: LogicalPrimitiveGateType
    control_qubits: Tuple[int, ...]
    target_qubit: int

    def __post_init__(self):
        if self.gate_type == LogicalPrimitiveGateType.X and len(self.control_qubits) != 0:
            raise ValueError("Pauli-X gate must have 0 control qubits.")
        if self.gate_type == LogicalPrimitiveGateType.CNOT and len(self.control_qubits) != 1:
            raise ValueError("CNOT gate must have exactly 1 control qubit.")
        if self.gate_type == LogicalPrimitiveGateType.TOFFOLI and len(self.control_qubits) != 2:
            raise ValueError("Toffoli gate must have exactly 2 control qubits.")
        if self.target_qubit in self.control_qubits:
            raise ValueError("Target qubit cannot be one of the control qubits.")
