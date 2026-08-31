"""
Module 6 Stage 6 — Feasibility Serialization.

Canonical JSON serialization and deserialization for CompilationFeasibilityReport.
"""

import json
from src.module6.feasibility.model import (
    FeasibilityStatus,
    DiagnosisLevel,
    CompilationFeasibilityReport,
)


def serialize_feasibility_report(report: CompilationFeasibilityReport) -> str:
    """Serializes CompilationFeasibilityReport into a canonical JSON string."""
    raw = report.to_dict()
    return json.dumps(raw, indent=2, sort_keys=True)


def deserialize_feasibility_report(json_str: str) -> CompilationFeasibilityReport:
    """Deserializes canonical JSON string into CompilationFeasibilityReport."""
    data = json.loads(json_str)
    return CompilationFeasibilityReport(
        algorithm_id=data["algorithm_id"],
        effective_vocabulary=tuple(data["effective_vocabulary"]),
        evolutionary_vocabulary=tuple(data["evolutionary_vocabulary"]),
        feasibility_status=FeasibilityStatus(data["feasibility_status"]),
        diagnosis_level=DiagnosisLevel(data["diagnosis_level"]),
        required_capabilities=tuple(data["required_capabilities"]),
        missing_capabilities=tuple(data["missing_capabilities"]),
        fallback_available=data["fallback_available"],
        fallback_baseline=tuple(data["fallback_baseline"]),
        recommended_augmentation=tuple(data["recommended_augmentation"]),
        search_depth_evaluated=data["search_depth_evaluated"],
        provenance=data["provenance"],
        deterministic_report_id=data["deterministic_report_id"],
    )
