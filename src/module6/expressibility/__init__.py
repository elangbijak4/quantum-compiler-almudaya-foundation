"""
Module 6 Subpackage — Expressibility & Target Matching.
"""

from src.module6.expressibility.config import ExpressibilityExperimentConfig
from src.module6.expressibility.matcher import TargetMatcher
from src.module6.expressibility.report import (
    TargetReachabilityStatus,
    InjectivityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
    Stage2FailureCode,
    TargetReachabilityResult,
    ExpressibilityReport,
    serialize_expressibility_report,
    deserialize_expressibility_report,
)

__all__ = [
    "ExpressibilityExperimentConfig",
    "TargetMatcher",
    "TargetReachabilityStatus",
    "InjectivityStatus",
    "SurjectivityStatus",
    "UniversalExpressibilityStatus",
    "Stage2FailureCode",
    "TargetReachabilityResult",
    "ExpressibilityReport",
    "serialize_expressibility_report",
    "deserialize_expressibility_report",
]
