"""
Module 6 Stage 8 — Evolutionary Circuit Optimization & Synthesis Cost Data Models.

Defines CircuitCostMetrics, OptimizationStatus, and OptimizationCostReport models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib


class OptimizationStatus(str, Enum):
    """Status classification for circuit optimization analysis."""
    OPTIMIZED = "OPTIMIZED"
    NO_REDUCTION_POSSIBLE = "NO_REDUCTION_POSSIBLE"
    SEMANTIC_PRESERVATION_FAILED = "SEMANTIC_PRESERVATION_FAILED"
    VOCABULARY_VIOLATION = "VOCABULARY_VIOLATION"
    INVALID_INPUT = "INVALID_INPUT"
    INCONCLUSIVE = "INCONCLUSIVE"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CircuitCostMetrics:
    """
    Immutable cost metrics for a quantum circuit IR.
    """
    total_gate_count: int
    gate_counts_by_type: Dict[str, int]
    circuit_depth: int
    t_gate_depth: int
    cnot_depth: int
    qubit_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_gate_count": self.total_gate_count,
            "gate_counts_by_type": dict(self.gate_counts_by_type),
            "circuit_depth": self.circuit_depth,
            "t_gate_depth": self.t_gate_depth,
            "cnot_depth": self.cnot_depth,
            "qubit_count": self.qubit_count,
        }


@dataclass(frozen=True)
class OptimizationCostReport:
    """
    Immutable report detailing optimization results, cost reduction metrics,
    vocabulary containment, and semantic preservation verification.
    """
    algorithm_id: str
    effective_vocabulary: Tuple[str, ...]
    initial_metrics: CircuitCostMetrics
    optimized_metrics: Optional[CircuitCostMetrics]
    gate_count_reduction: int
    depth_reduction: int
    semantic_equivalence_verified: bool
    vocabulary_containment_verified: bool
    status: OptimizationStatus
    provenance: Dict[str, Any] = field(default_factory=dict)
    report_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_id": self.algorithm_id,
            "effective_vocabulary": list(self.effective_vocabulary),
            "initial_metrics": self.initial_metrics.to_dict(),
            "optimized_metrics": self.optimized_metrics.to_dict() if self.optimized_metrics else None,
            "gate_count_reduction": self.gate_count_reduction,
            "depth_reduction": self.depth_reduction,
            "semantic_equivalence_verified": self.semantic_equivalence_verified,
            "vocabulary_containment_verified": self.vocabulary_containment_verified,
            "status": self.status.value,
            "provenance": dict(self.provenance),
            "report_hash": self.report_hash,
        }
