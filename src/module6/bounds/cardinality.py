"""
Module 6 Stage 3 — Cardinality Descriptor & Bounds.

Defines formal mathematical cardinality descriptors (FINITE, COUNTABLE, UNCOUNTABLE) for Domain A_C, Codomain C_Q, and Img(F).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Any


class CardinalityType(str, Enum):
    """Mathematical cardinality types for sets in Module 6."""
    FINITE = "FINITE"
    COUNTABLE = "COUNTABLE"
    UNCOUNTABLE = "UNCOUNTABLE"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


@dataclass(frozen=True)
class CardinalityBound:
    """
    Immutable mathematical cardinality bound for a domain or codomain space.
    """
    space_name: str
    cardinality_type: CardinalityType
    upper_bound_formula: str
    exact_sample_size: Optional[int] = None
    is_formally_proven: bool = False
    details: str = ""
    provenance: Dict[str, str] = field(default_factory=dict)
