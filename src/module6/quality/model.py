"""
Module 6 Stage 9 — Compilation Quality, Resource-Aware Analysis & Result Governance Models.

Defines ResourceProfile, QualityProfile, ComparisonResult, ParetoStatus,
ResultClassification, and QualityAnalysisReport models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib


class ResultClassification(str, Enum):
    """Governed classification for compiled and optimized quantum results."""
    SEMANTICALLY_VALID = "SEMANTICALLY_VALID"
    SEMANTICALLY_INVALID = "SEMANTICALLY_INVALID"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    OPTIMIZED = "OPTIMIZED"
    NON_DOMINATED = "NON_DOMINATED"
    DOMINATED = "DOMINATED"
    INCOMPARABLE = "INCOMPARABLE"
    INCONCLUSIVE = "INCONCLUSIVE"
    INVALID = "INVALID"
    RESOURCE_CONSTRAINT_VIOLATION = "RESOURCE_CONSTRAINT_VIOLATION"

    def __str__(self) -> str:
        return self.value


class ParetoStatus(str, Enum):
    """Pareto trade-off classification between compiled candidates."""
    NON_DOMINATED = "NON_DOMINATED"
    DOMINATED = "DOMINATED"
    INCOMPARABLE = "INCOMPARABLE"
    EQUAL = "EQUAL"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ResourceProfile:
    """
    Immutable logical resource usage profile derived solely from QuantumCircuitIR.
    Enforces logical_metric != physical_metric. Zero QPU claims.
    """
    total_qubits: int
    data_qubits: int
    ancilla_qubits: int
    total_gate_count: int
    circuit_depth: int
    t_gate_count: int
    t_gate_depth: int
    cnot_gate_count: int
    cnot_depth: int
    gate_distribution: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_qubits": self.total_qubits,
            "data_qubits": self.data_qubits,
            "ancilla_qubits": self.ancilla_qubits,
            "total_gate_count": self.total_gate_count,
            "circuit_depth": self.circuit_depth,
            "t_gate_count": self.t_gate_count,
            "t_gate_depth": self.t_gate_depth,
            "cnot_gate_count": self.cnot_gate_count,
            "cnot_depth": self.cnot_depth,
            "gate_distribution": dict(self.gate_distribution),
        }


@dataclass(frozen=True)
class QualityProfile:
    """
    Multi-objective quality profile preserving distinct evaluation dimensions.
    Enforces Non-implication rule: Quality score != Semantic equivalence.
    """
    semantic_equivalence_verified: bool
    feasibility_status: str
    resource_profile: ResourceProfile
    optimization_reduction: int
    vocabulary_compatibility: bool
    provenance_completeness: bool
    classification: ResultClassification
    weighted_quality_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "semantic_equivalence_verified": self.semantic_equivalence_verified,
            "feasibility_status": self.feasibility_status,
            "resource_profile": self.resource_profile.to_dict(),
            "optimization_reduction": self.optimization_reduction,
            "vocabulary_compatibility": self.vocabulary_compatibility,
            "provenance_completeness": self.provenance_completeness,
            "classification": self.classification.value,
            "weighted_quality_score": self.weighted_quality_score,
        }


@dataclass(frozen=True)
class ComparisonResult:
    """
    Governed comparative analysis between candidate compilation results.
    """
    candidate_a_id: str
    candidate_b_id: str
    pareto_status: ParetoStatus
    trade_off_summary: Dict[str, Any]
    dominant_candidate_id: Optional[str]
    provenance: Dict[str, Any] = field(default_factory=dict)
    comparison_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_a_id": self.candidate_a_id,
            "candidate_b_id": self.candidate_b_id,
            "pareto_status": self.pareto_status.value,
            "trade_off_summary": dict(self.trade_off_summary),
            "dominant_candidate_id": self.dominant_candidate_id,
            "provenance": dict(self.provenance),
            "comparison_hash": self.comparison_hash,
        }


@dataclass(frozen=True)
class QualityAnalysisReport:
    """
    Master Stage 9 Analytical & Result Governance Report.
    """
    algorithm_id: str
    quality_profile: QualityProfile
    resource_profile: ResourceProfile
    resource_constraint_violations: Tuple[str, ...]
    dual_result_analysis: Dict[str, Any]
    classification: ResultClassification
    provenance: Dict[str, Any] = field(default_factory=dict)
    report_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_id": self.algorithm_id,
            "quality_profile": self.quality_profile.to_dict(),
            "resource_profile": self.resource_profile.to_dict(),
            "resource_constraint_violations": list(self.resource_constraint_violations),
            "dual_result_analysis": dict(self.dual_result_analysis),
            "classification": self.classification.value,
            "provenance": dict(self.provenance),
            "report_hash": self.report_hash,
        }
