"""
Module 6 Stage 7 Test Suite — User Compilation Constraints.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.model import ConfigurationStatus


class TestStage7Constraints(unittest.TestCase):
    """Tests for user compilation constraints (forbidden_gates, required_gates)."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_forbidden_gate_excluded(self) -> None:
        """Req 13: Forbidden gate is excluded from effective vocabulary."""
        comp_c = {"forbidden_gates": ["TOFFOLI"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, compilation_constraints=comp_c
        )
        self.assertEqual(ctx.effective_vocabulary, ("CNOT", "X"))
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.CONFIGURATION_CONFLICT)

    def test_unavailable_required_gate_fails_validation(self) -> None:
        """Req 13: Requesting required gate unavailable in GE(0) marks configuration INVALID."""
        comp_c = {"required_gates": ["HADAMARD"]}
        ctx = Stage7CompilerResolver.resolve_effective_context(
            self.ge0, compilation_constraints=comp_c
        )
        self.assertEqual(ctx.configuration_status, ConfigurationStatus.INVALID_CONFIGURATION)


if __name__ == "__main__":
    unittest.main()
