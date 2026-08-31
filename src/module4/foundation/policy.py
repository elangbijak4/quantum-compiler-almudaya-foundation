"""
Module 4 Foundation — 3-Level Equivalence Verification Policy.

Defines symbolic, state vector norm, and matrix operator norm verification levels with tolerance \epsilon = 10^{-12}.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional

NUMERICAL_VERIFICATION_TOLERANCE: float = 1e-12


class VerificationLevel(str, Enum):
    """3-Level Verification Policy Levels."""
    LEVEL_1_SYMBOLIC_BASIS = "LEVEL_1_SYMBOLIC_BASIS"
    LEVEL_2_STATE_VECTOR_NORM = "LEVEL_2_STATE_VECTOR_NORM"
    LEVEL_3_OPERATOR_NORM = "LEVEL_3_OPERATOR_NORM"


@dataclass
class VerificationPolicy:
    """
    Verification policy specification for Module 4.
    
    Fields:
    - primary_level: Required verification level.
    - tolerance: Numerical float precision threshold (default 1e-12).
    """
    primary_level: VerificationLevel = VerificationLevel.LEVEL_1_SYMBOLIC_BASIS
    tolerance: float = NUMERICAL_VERIFICATION_TOLERANCE

    def is_within_tolerance(self, diff: float) -> bool:
        return abs(diff) < self.tolerance
