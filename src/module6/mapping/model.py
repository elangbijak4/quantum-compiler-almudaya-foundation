"""
Module 6 Stage 3 — Mapping Data Models.

Defines immutable descriptors for Domain A_C, Codomain C_Q, Compiler Mapping Record,
Semantic Quotient Record, and Mapping Complexity Record.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any


class MappingTotalityStatus(str, Enum):
    """Classification of compiler mapping totality over defined domain A_C."""
    TOTAL_OVER_DEFINED_DOMAIN = "TOTAL_OVER_DEFINED_DOMAIN"
    PARTIAL = "PARTIAL"
    UNDETERMINED = "UNDETERMINED"


class QuotientWellDefinednessStatus(str, Enum):
    """Status of quotient mapping F_bar well-definedness (A1 \equiv_C A2 => F(A1) \equiv_Q F(A2))."""
    WELL_DEFINED_OBSERVED = "WELL_DEFINED_OBSERVED"
    COUNTEREXAMPLE_OBSERVED = "COUNTEREXAMPLE_OBSERVED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class BoundClassification(str, Enum):
    """Mandatory classification for all image and capacity bounds."""
    FORMAL_THEOREM = "FORMAL_THEOREM"
    STRUCTURAL_INVARIANT = "STRUCTURAL_INVARIANT"
    EXECUTABLE_VERIFICATION = "EXECUTABLE_VERIFICATION"
    EMPIRICAL_OBSERVATION = "EMPIRICAL_OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"


@dataclass(frozen=True)
class DomainDescriptor:
    """
    Formal mathematical descriptor of Classical Algorithm Domain A_C = A_semantic.
    """
    domain_name: str
    formal_definition: str
    state_space_type: str
    transition_type: str
    finite_domain_bound: str
    is_totality_verified: bool
    is_determinism_verified: bool
    is_reversibility_verified: bool
    cardinality_type: str
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CodomainDescriptor:
    """
    Formal mathematical descriptor of Logical Quantum Circuit Codomain C_Q^logical.
    """
    codomain_name: str
    formal_definition: str
    circuit_ir_schema: str
    qubit_register_policy: str
    ancilla_uncomputation_policy: str
    cardinality_type: str
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CompilerMappingRecord:
    """
    Immutable record representing the mapping of a single algorithm A -> F(A).
    """
    source_algorithm_id: str
    source_semantic_id: str
    source_domain_id: str
    logical_circuit_id: str
    circuit_structural_hash: str
    operator_hash: str
    compiler_version: str
    mapping_status: str
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticQuotientRecord:
    """
    Record of semantic quotient mapping evaluation F_bar: A_C/\equiv_C -> C_Q/\equiv_Q.
    """
    evaluation_id: str
    classical_equivalence_class_id: str
    quantum_equivalence_class_id: str
    algorithms_in_class: Tuple[str, ...]
    circuits_in_class: Tuple[str, ...]
    well_defined_in_class: bool
    details: str
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MappingComplexityRecord:
    """
    Deterministic mapping statistics for A -> F(A).
    """
    algorithm_id: str
    circuit_id: str
    source_state_count: int
    transition_count: int
    encoded_configuration_count: int
    logical_qubit_count: int
    logical_gate_count: int
    ancilla_qubit_count: int
    provenance: Dict[str, str] = field(default_factory=dict)
