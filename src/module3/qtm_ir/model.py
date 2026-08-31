"""
QTM-IR Core Data Model (Module 3 Stage 5).

Provides a structured, canonical Intermediate Representation (IR) for Quantum Turing Machine
states, basis state references, state vectors, transition operators, finite matrices,
and provenance metadata, as established in Stages 1–4.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
import math

QTM_IR_VERSION = "1.0.0"
CANONICAL_SEMANTIC_RELATION = "Canonical QTM Lifting (U_P ∘ ι = ι ∘ R_P)"


@dataclass(frozen=True)
class QTMIRComplexNumber:
    """
    Canonical representation of a complex number α = real + imag*j in QTM-IR.
    """
    real: float
    imag: float

    def to_complex(self) -> complex:
        """Converts to native Python complex number."""
        return complex(self.real, self.imag)

    @classmethod
    def from_complex(cls, c: complex) -> "QTMIRComplexNumber":
        """Factory constructing QTMIRComplexNumber from complex number."""
        return cls(real=float(c.real), imag=float(c.imag))

    def abs_sq(self) -> float:
        """Returns |α|²."""
        return self.real * self.real + self.imag * self.imag

    def abs(self) -> float:
        """Returns |α|."""
        return math.sqrt(self.abs_sq())


@dataclass(frozen=True)
class QTMIRBasisState:
    """
    Structured QTM-IR Basis State Reference representing computational basis vector |C_R⟩.

    Canonicalizes the underlying 7-tuple RUTM configuration identity (q, T, h, H, k, halted, error).
    """
    basis_id: str
    current_state: str
    tape: Dict[int, str]
    head_pos: int
    history: Tuple[Any, ...] = field(default_factory=tuple)
    step_count: int = 0
    halted: bool = False
    error: Optional[str] = None

    def get_tape_symbol(self, pos: int) -> str:
        """Returns tape symbol at pos, defaulting to '_'."""
        return self.tape.get(pos, "_")


@dataclass
class QTMIRStateVector:
    """
    Structured QTM-IR Quantum State Vector representing |ψ⟩ = Σ α_C |C_R⟩.
    """
    amplitudes: Dict[str, QTMIRComplexNumber] = field(default_factory=dict)
    tolerance: float = 1e-12
    is_normalized: bool = True

    def compute_norm(self) -> float:
        """Computes current vector norm ||ψ|| = sqrt(Σ |α_C|²)."""
        sum_sq = sum(amp.abs_sq() for amp in self.amplitudes.values())
        return math.sqrt(sum_sq)


@dataclass
class QTMIRTransitionMapping:
    """
    Structured QTM-IR Permutation Transition Specification R_P : C_R -> C_R.
    """
    forward_mapping: Dict[str, str] = field(default_factory=dict)
    reverse_mapping: Dict[str, str] = field(default_factory=dict)
    is_bijective: bool = True


@dataclass
class QTMIRMatrixRepresentation:
    """
    Structured QTM-IR Finite Matrix Representation [U_P]_{N x N}.
    """
    basis_order: List[str] = field(default_factory=list)
    matrix: List[List[QTMIRComplexNumber]] = field(default_factory=list)
    dimension: int = 0


@dataclass
class QTMIRProvenance:
    """
    Structured QTM-IR Provenance Metadata.
    """
    source_rutm_program_hash: str
    source_module: str = "Module 2 (RUTM-IR)"
    stage: str = "Stage 5 (QTM-IR Model)"
    compiler_version: str = "0.3.0-alpha"
    semantic_relation: str = CANONICAL_SEMANTIC_RELATION


@dataclass
class QTMIRModel:
    """
    Master Canonical QTM-IR Data Model.
    """
    version: str = QTM_IR_VERSION
    machine_id: str = "qtm_instance"
    basis_states: Dict[str, QTMIRBasisState] = field(default_factory=dict)
    initial_state_vector: QTMIRStateVector = field(default_factory=QTMIRStateVector)
    transition_mapping: QTMIRTransitionMapping = field(default_factory=QTMIRTransitionMapping)
    matrix_representation: Optional[QTMIRMatrixRepresentation] = None
    provenance: Optional[QTMIRProvenance] = None
