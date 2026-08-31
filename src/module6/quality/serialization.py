"""
Module 6 Stage 9 — Quality Serialization.

Canonical JSON serialization and deserialization for QualityProfile, ComparisonResult,
and QualityAnalysisReport. Enforces deserialize(serialize(X)) == X.
"""

import json
from typing import Dict, Any
from src.module6.quality.model import (
    ResourceProfile,
    QualityProfile,
    ComparisonResult,
    QualityAnalysisReport,
    ResultClassification,
    ParetoStatus,
)


def serialize_quality_profile(profile: QualityProfile) -> str:
    """Serializes QualityProfile into canonical JSON string."""
    return json.dumps(profile.to_dict(), indent=2, sort_keys=True)


def deserialize_quality_profile(json_str: str) -> QualityProfile:
    """Deserializes canonical JSON string into QualityProfile."""
    data = json.loads(json_str)
    r_data = data["resource_profile"]
    res_prof = ResourceProfile(
        total_qubits=r_data["total_qubits"],
        data_qubits=r_data["data_qubits"],
        ancilla_qubits=r_data["ancilla_qubits"],
        total_gate_count=r_data["total_gate_count"],
        circuit_depth=r_data["circuit_depth"],
        t_gate_count=r_data["t_gate_count"],
        t_gate_depth=r_data["t_gate_depth"],
        cnot_gate_count=r_data["cnot_gate_count"],
        cnot_depth=r_data["cnot_depth"],
        gate_distribution=dict(r_data["gate_distribution"]),
    )

    return QualityProfile(
        semantic_equivalence_verified=data["semantic_equivalence_verified"],
        feasibility_status=data["feasibility_status"],
        resource_profile=res_prof,
        optimization_reduction=data["optimization_reduction"],
        vocabulary_compatibility=data["vocabulary_compatibility"],
        provenance_completeness=data["provenance_completeness"],
        classification=ResultClassification(data["classification"]),
        weighted_quality_score=data.get("weighted_quality_score"),
    )


def serialize_comparison_result(result: ComparisonResult) -> str:
    """Serializes ComparisonResult into canonical JSON string."""
    return json.dumps(result.to_dict(), indent=2, sort_keys=True)


def deserialize_comparison_result(json_str: str) -> ComparisonResult:
    """Deserializes canonical JSON string into ComparisonResult."""
    data = json.loads(json_str)
    return ComparisonResult(
        candidate_a_id=data["candidate_a_id"],
        candidate_b_id=data["candidate_b_id"],
        pareto_status=ParetoStatus(data["pareto_status"]),
        trade_off_summary=dict(data["trade_off_summary"]),
        dominant_candidate_id=data["dominant_candidate_id"],
        provenance=dict(data["provenance"]),
        comparison_hash=data["comparison_hash"],
    )


def serialize_quality_analysis_report(report: QualityAnalysisReport) -> str:
    """Serializes QualityAnalysisReport into canonical JSON string."""
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def deserialize_quality_analysis_report(json_str: str) -> QualityAnalysisReport:
    """Deserializes canonical JSON string into QualityAnalysisReport."""
    data = json.loads(json_str)
    q_prof = deserialize_quality_profile(json.dumps(data["quality_profile"]))
    r_data = data["resource_profile"]
    res_prof = ResourceProfile(
        total_qubits=r_data["total_qubits"],
        data_qubits=r_data["data_qubits"],
        ancilla_qubits=r_data["ancilla_qubits"],
        total_gate_count=r_data["total_gate_count"],
        circuit_depth=r_data["circuit_depth"],
        t_gate_count=r_data["t_gate_count"],
        t_gate_depth=r_data["t_gate_depth"],
        cnot_gate_count=r_data["cnot_gate_count"],
        cnot_depth=r_data["cnot_depth"],
        gate_distribution=dict(r_data["gate_distribution"]),
    )

    return QualityAnalysisReport(
        algorithm_id=data["algorithm_id"],
        quality_profile=q_prof,
        resource_profile=res_prof,
        resource_constraint_violations=tuple(data["resource_constraint_violations"]),
        dual_result_analysis=dict(data["dual_result_analysis"]),
        classification=ResultClassification(data["classification"]),
        provenance=dict(data["provenance"]),
        report_hash=data["report_hash"],
    )
