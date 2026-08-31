"""
Module 6 Stage 7 — Resolution Policy & Configuration Precedence (Initialization Scaffold).

Defines deterministic resolution policy precedence rules.
"""

from typing import Dict, List, Tuple, Any
from src.module6.resolution.model import ConfigurationPrecedence


class ResolutionPolicy:
    """
    Defines deterministic configuration precedence across layers.
    """

    PRECEDENCE_ORDER = (
        ConfigurationPrecedence.EVOLUTIONARY_DEFAULT,
        ConfigurationPrecedence.SESSION_BASELINE,
        ConfigurationPrecedence.USER_CONSTRAINTS,
        ConfigurationPrecedence.BACKEND_CONSTRAINTS,
        ConfigurationPrecedence.EQUIVALENCE_POLICY,
        ConfigurationPrecedence.FEASIBILITY_POLICY,
    )

    @classmethod
    def get_precedence_order(cls) -> Tuple[ConfigurationPrecedence, ...]:
        """Returns deterministic precedence hierarchy."""
        return cls.PRECEDENCE_ORDER
