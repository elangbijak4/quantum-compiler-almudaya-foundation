"""
Equivalence Verification Result Specification (Module 2 Stage 8).

Defines the structured container holding outcomes, trace lengths, status codes,
mismatch diagnostics, and provenance metadata for the UTM -> RUTM equivalence gate.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from src.module1.utm.model import UTMConfiguration
from src.module2.rutm.model import RUTMConfiguration


@dataclass(frozen=True)
class EquivalenceVerificationResult:
    """Structured result of the UTM -> RUTM Equivalence Verification Gate."""

    status: str  # "PASS", "FAIL", "INCONCLUSIVE"
    equivalent: bool
    steps_compared: int
    source_trace_length: int
    target_trace_length: int
    mismatch_step: Optional[int] = None
    source_configuration: Optional[UTMConfiguration] = None
    target_configuration: Optional[RUTMConfiguration] = None
    projected_target_configuration: Optional[UTMConfiguration] = None
    source_halted: bool = False
    target_halted: bool = False
    resource_limit_reached: bool = False
    error: Optional[str] = None
    provenance: Optional[Dict[str, Any]] = None
