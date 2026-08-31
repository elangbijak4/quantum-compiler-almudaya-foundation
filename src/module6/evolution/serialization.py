"""
Module 6 Stage 5 — Canonical JSON Serialization.

Supports deterministic JSON serialization and deserialization round-trip for:
- CandidateGate
- TargetOperator
- ExpressiveGainMetrics
- Stage5Provenance
- ExtensionReport
- Stage5AnalysisReport
"""

import json
from typing import Any, Dict
from src.module6.evolution.candidate import CandidateGate
from src.module6.evolution.target import TargetOperator
from src.module6.evolution.metrics import ExpressiveGainMetrics
from src.module6.evolution.provenance import Stage5Provenance
from src.module6.evolution.extension import ExtensionReport


def serialize_stage5_object(obj: Any) -> str:
    """
    Serializes Stage 5 object to canonical JSON string.
    Ensures deterministic sorting of keys and consistent float representation.
    """
    if hasattr(obj, "to_dict"):
        d = obj.to_dict()
    elif isinstance(obj, dict):
        d = obj
    else:
        raise ValueError(f"SERIALIZATION_FAILURE: Object of type {type(obj)} is not serializable")

    return json.dumps(d, indent=2, sort_keys=True)


def deserialize_candidate_gate(json_str: str) -> CandidateGate:
    d = json.loads(json_str)
    return CandidateGate.from_dict(d)


def deserialize_target_operator(json_str: str) -> TargetOperator:
    d = json.loads(json_str)
    return TargetOperator.from_dict(d)


def deserialize_extension_report(json_str: str) -> ExtensionReport:
    d = json.loads(json_str)
    return ExtensionReport.from_dict(d)
