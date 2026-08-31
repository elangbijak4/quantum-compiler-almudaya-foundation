"""
Module 6 Stage 7 Test Suite — Conflict Engine & Precedence Policy.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.policy import ResolutionPolicy
from src.module6.resolution.model import ConfigurationStatus, ConfigurationPrecedence


class TestStage7Conflicts(unittest.TestCase):
    """Tests for conflict detection and classification engine."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_precedence_hierarchy(self) -> None:
        """Req 14: Deterministic precedence order verification."""
        p_order = ResolutionPolicy.get_precedence_order()
        self.assertEqual(p_order[0], ConfigurationPrecedence.EVOLUTIONARY_DEFAULT)
        self.assertEqual(p_order[1], ConfigurationPrecedence.SESSION_BASELINE)
        self.assertEqual(p_order[3], ConfigurationPrecedence.BACKEND_CONSTRAINTS)

    def test_backend_conflict_classification(self) -> None:
        """Req 29: Conflict detection records explicit conflict metadata."""
        backend_c = {"supported_gates": ["CNOT"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, backend_constraints=backend_c
        )
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.CONFIGURATION_CONFLICT)
        self.assertTrue(any(c.conflict_type == "BACKEND_CONFLICT" for c in ctx.conflicts))


if __name__ == "__main__":
    unittest.main()
