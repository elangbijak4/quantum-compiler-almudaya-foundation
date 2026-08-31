"""
RUTM-IR Execution and Trace Verification Package (Module 2 Stage 7).
"""

from .result import (
    RUTMExecutionResult,
    ReversibilityVerificationResult,
    DifferentialVerificationResult,
)
from .executor import execute_rutm_ir
from .verifier import verify_trace_reversibility, verify_projected_utm_correspondence

__all__ = [
    "RUTMExecutionResult",
    "ReversibilityVerificationResult",
    "DifferentialVerificationResult",
    "execute_rutm_ir",
    "verify_trace_reversibility",
    "verify_projected_utm_correspondence",
]
