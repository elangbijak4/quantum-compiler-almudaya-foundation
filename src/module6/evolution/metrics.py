"""
Module 6 Stage 5 — Expressive Gain Metrics.

Defines ExpressiveGainMetrics data container for image cardinality comparison, target coverage, and expressive expansion.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class ExpressiveGainMetrics:
    """
    Data record for expressibility expansion metrics.
    """
    baseline_image_cardinality: int
    extended_image_cardinality: int
    structural_circuits_count: int
    semantic_operator_classes_count: int
    target_coverage_baseline: float
    target_coverage_extended: float
    expressive_gain_delta: int
    expressive_gain_ratio: float
    new_operator_classes_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpressiveGainMetrics":
        return cls(**data)
