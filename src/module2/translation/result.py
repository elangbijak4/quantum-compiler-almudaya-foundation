"""
Translation Result Specification (Module 2 Stage 6).

Defines the structured result object returned by the UTM-IR -> RUTM-IR translator.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any
from src.module1.utm.model import UTMProgram
from src.module2.rutm_ir.model import RUTM_IR


@dataclass(frozen=True)
class TranslationResult:
    """Structured container holding translation outcome, artifacts, and metrics."""

    success: bool
    source_program: Optional[UTMProgram] = None
    target_ir: Optional[RUTM_IR] = None
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    metrics: Dict[str, Any] = field(default_factory=dict)
