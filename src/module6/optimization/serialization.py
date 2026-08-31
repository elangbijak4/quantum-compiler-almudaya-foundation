"""
Module 6 Stage 8 — Optimization Serialization.

Canonical JSON serialization and deserialization for OptimizationCostReport.
"""

import json
from src.module6.optimization.model import (
    OptimizationCostReport,
    CircuitCostMetrics,
    OptimizationStatus,
)


def serialize_optimization_report(report: OptimizationCostReport) -> str:
    """Serializes OptimizationCostReport into a canonical JSON string."""
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def deserialize_optimization_report(json_str: str) -> OptimizationCostReport:
    """Deserializes canonical JSON string into OptimizationCostReport."""
    data = json.loads(json_str)

    init_m_data = data["initial_metrics"]
    init_m = CircuitCostMetrics(
        total_gate_count=init_m_data["total_gate_count"],
        gate_counts_by_type=init_m_data["gate_counts_by_type"],
        circuit_depth=init_m_data["circuit_depth"],
        t_gate_depth=init_m_data["t_gate_depth"],
        cnot_depth=init_m_data["cnot_depth"],
        qubit_count=init_m_data["qubit_count"],
    )

    opt_m = None
    if data.get("optimized_metrics"):
        opt_m_data = data["optimized_metrics"]
        opt_m = CircuitCostMetrics(
            total_gate_count=opt_m_data["total_gate_count"],
            gate_counts_by_type=opt_m_data["gate_counts_by_type"],
            circuit_depth=opt_m_data["circuit_depth"],
            t_gate_depth=opt_m_data["t_gate_depth"],
            cnot_depth=opt_m_data["cnot_depth"],
            qubit_count=opt_m_data["qubit_count"],
        )

    return OptimizationCostReport(
        algorithm_id=data["algorithm_id"],
        effective_vocabulary=tuple(data["effective_vocabulary"]),
        initial_metrics=init_m,
        optimized_metrics=opt_m,
        gate_count_reduction=data["gate_count_reduction"],
        depth_reduction=data["depth_reduction"],
        semantic_equivalence_verified=data["semantic_equivalence_verified"],
        vocabulary_containment_verified=data.get("vocabulary_containment_verified", True),
        status=OptimizationStatus(data["status"]),
        provenance=data.get("provenance", {}),
        report_hash=data.get("report_hash", ""),
    )
