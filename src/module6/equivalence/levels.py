"""
Module 6 Stage 4 — Equivalence Levels Definition.

Defines the six-level equivalence hierarchy:
LEVEL 1: SYNTACTIC / REPRESENTATIONAL IDENTITY
LEVEL 2: STRUCTURAL CIRCUIT EQUIVALENCE
LEVEL 3: COMPUTATIONAL-BASIS SEMANTIC EQUIVALENCE
LEVEL 4: STATE-VECTOR EQUIVALENCE
LEVEL 5: OPERATOR EQUIVALENCE
LEVEL 6: FULL SEMANTIC / QUOTIENT EQUIVALENCE
"""

from enum import Enum, auto


class EquivalenceLevel(str, Enum):
    """
    Six-level equivalence hierarchy for classical and quantum representations.
    """
    LEVEL_1_SYNTACTIC = "LEVEL_1_SYNTACTIC"
    LEVEL_2_STRUCTURAL = "LEVEL_2_STRUCTURAL"
    LEVEL_3_BASIS = "LEVEL_3_BASIS"
    LEVEL_4_STATE_VECTOR = "LEVEL_4_STATE_VECTOR"
    LEVEL_5_OPERATOR = "LEVEL_5_OPERATOR"
    LEVEL_6_SEMANTIC = "LEVEL_6_SEMANTIC"

    def __str__(self) -> str:
        return self.value
