"""
Module 6 Stage 7 Test Suite — Default Resolution & Mandatory Invariants.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.model import ConfigurationStatus
from src.module6.session.baseline import BaselineMode


class TestStage7ResolutionDefault(unittest.TestCase):
    """Tests for default compilation resolution behavior."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_default_resolution_reproduces_ge0(self) -> None:
        """Req 9: Default resolution preserves GE(0) evolutionary vocabulary."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.assertEqual(ctx.baseline_mode, BaselineMode.DEFAULT_EVOLUTIONARY.value)
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "TOFFOLI", "X"))
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.VALID_CONFIGURATION)

    def test_default_resolution_has_valid_provenance(self) -> None:
        """Req 30: Default resolution generates complete provenance metadata."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.assertEqual(ctx.provenance["evolution_stage"], "GE_0")
        self.assertEqual(ctx.provenance["baseline_mode"], "DEFAULT_EVOLUTIONARY")
        self.assertEqual(ctx.provenance["effective_vocabulary"], ["CNOT", "TOFFOLI", "X"])


if __name__ == "__main__":
    unittest.main()
