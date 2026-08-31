"""
Module 6 Stage 3 — Operator Class Descriptor.

Formally characterizes mathematical properties of compiler operator class OpImg(F).
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from src.module6.mapping.model import BoundClassification


@dataclass(frozen=True)
class OperatorClassDescriptor:
    """
    Immutable mathematical descriptor of compiler operator image class.
    """
    class_name: str
    formal_expression: str
    is_unitary: bool
    is_real_valued: bool
    is_permutation: bool
    is_superposition_generating: bool
    has_discrete_parameters: bool
    is_closed_under_composition: bool
    classification: BoundClassification
    details: str
    provenance: Dict[str, str] = field(default_factory=dict)
