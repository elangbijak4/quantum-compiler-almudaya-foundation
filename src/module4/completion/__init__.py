"""
Module 4 Completion Package — Self-Auditing Integration & Completion Gate.
"""

from src.module4.completion.model import (
    Stage6CompletionStatus,
    Stage6CompletionResult,
)
from src.module4.completion.gate import (
    Module4CompletionGate,
    verify_module4_completion,
)

__all__ = [
    "Stage6CompletionStatus",
    "Stage6CompletionResult",
    "Module4CompletionGate",
    "verify_module4_completion",
]
