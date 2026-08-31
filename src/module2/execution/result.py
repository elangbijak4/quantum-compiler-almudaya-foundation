"""
Execution and Verification Result Specifications (Module 2 Stage 7).

Defines structured containers for execution outcomes, trace reversal verification,
and differential UTM/RUTM projection verification.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from src.module1.utm.model import UTMConfiguration
from src.module2.rutm.model import RUTMConfiguration


@dataclass(frozen=True)
class RUTMExecutionResult:
    """Container holding the complete outcome of an RUTM-IR execution trace."""

    success: bool
    initial_configuration: RUTMConfiguration
    final_configuration: RUTMConfiguration
    trace: Tuple[RUTMConfiguration, ...]
    steps_executed: int
    halted: bool
    error: Optional[str] = None
    resource_limit_reached: bool = False


@dataclass(frozen=True)
class ReversibilityVerificationResult:
    """Container holding the outcome of a finite-trace reversibility verification."""

    verified: bool
    original_configuration: RUTMConfiguration
    restored_configuration: RUTMConfiguration
    forward_steps: int
    reverse_steps: int
    failure_index: Optional[int] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class DifferentialVerificationResult:
    """Container holding the outcome of a differential UTM/RUTM projection check."""

    matched: bool
    steps_compared: int
    mismatch_step: Optional[int] = None
    utm_configuration: Optional[UTMConfiguration] = None
    projected_rutm_configuration: Optional[UTMConfiguration] = None
    error: Optional[str] = None
