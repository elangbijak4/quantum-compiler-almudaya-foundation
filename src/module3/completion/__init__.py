"""
Module 3 Stage 9 Completion Gate Package.

Provides self-auditing integration gate and completion verification for Module 3.
"""

from src.module3.completion.gate import (
    Module3CompletionStatus,
    StageAuditReport,
    Module3CompletionResult,
    Module3CompletionGate,
    run_module3_completion_gate,
)

__all__ = [
    "Module3CompletionStatus",
    "StageAuditReport",
    "Module3CompletionResult",
    "Module3CompletionGate",
    "run_module3_completion_gate",
]
